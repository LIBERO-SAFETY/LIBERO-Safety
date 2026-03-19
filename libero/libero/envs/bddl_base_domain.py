import numpy as np
import os
import robosuite.utils.transform_utils as T

from copy import deepcopy
from robosuite.environments.manipulation.single_arm_env import SingleArmEnv
from robosuite.models.tasks import ManipulationTask
from robosuite.utils.placement_samplers import SequentialCompositeSampler
from robosuite.utils.observables import Observable, sensor
from robosuite.utils.mjcf_utils import CustomMaterial
import robosuite.macros as macros
import random
import mujoco
from robosuite.models.base import MujocoModel
import libero.libero.envs.bddl_utils as BDDLUtils
from libero.libero.envs.robots import *
from libero.libero.envs.utils import *
from libero.libero.envs.object_states import *
from libero.libero.envs.predicates import *
from libero.libero.envs.objects import *
from libero.libero.envs.regions import *
from libero.libero.envs.arenas import *


DIR_PATH = os.path.dirname(os.path.realpath(__file__))

TASK_MAPPING = {}


def register_problem(target_class):
    """We design the mapping to be case-INsensitive."""
    TASK_MAPPING[target_class.__name__.lower()] = target_class
    return target_class


import time


class BDDLBaseDomain(SingleArmEnv):
    """
    A base domain for parsing bddl files.
    """

    def __init__(
        self,
        bddl_file_name,
        robots,
        env_configuration="default",
        controller_configs=None,
        gripper_types="default",
        initialization_noise="default",
        use_latch=False,
        use_camera_obs=True,
        use_object_obs=True,
        reward_scale=1.0,
        reward_shaping=False,
        placement_initializer=None,
        object_property_initializers=None,
        has_renderer=False,
        has_offscreen_renderer=True,
        random_init = False,
        render_camera="frontview",
        render_collision_mesh=False,
        render_visual_mesh=True,
        render_gpu_device_id=-1,
        control_freq=20,
        horizon=1000,
        ignore_done=False,
        hard_reset=True,
        camera_names="agentview",
        camera_heights=256,
        camera_widths=256,
        camera_depths=False,
        camera_segmentations=None,
        renderer="mujoco",
        table_full_size=(1.0, 1.0, 0.05),
        workspace_offset=(0.0, 0.0, 0.0),
        arena_type="table",
        scene_xml="scenes/libero_base_style.xml",
        scene_properties={},
        **kwargs,
    ):
        # settings for table top (hardcoded since it's not an essential part of the environment)
        self.workspace_offset = workspace_offset
        # reward configuration
        self.reward_scale = reward_scale
        self.reward_shaping = reward_shaping

        # whether to use ground-truth object states
        self.use_object_obs = use_object_obs
        self.contact_force_threshold = 100.0
        # object placement initializer
        self.placement_initializer = placement_initializer
        self.conditional_placement_initializer = None
        self.conditional_placement_on_objects_initializer = None

        self.dyn_object_original_quat = {}
        self.dyn_object_original_pos = {}
        # object property initializer

        if object_property_initializers is not None:
            self.object_property_initializers = object_property_initializers
        else:
            self.object_property_initializers = list()

        # Keep track of movable objects in the tasks
        self.objects_dict = {}
        # Kepp track of fixed objects in the tasks
        self.fixtures_dict = {}
        # Keep track of site objects in the tasks. site objects
        # (instances of SiteObject)
        self.object_sites_dict = {}
        # This is a dictionary that stores all the object states
        # interface for all the objects
        self.object_states_dict = {}
        
        # For those that require visual feature changes, update the state every time step to avoid missing state changes. We keep track of this type of objects to make predicate checking more efficient.
        self.tracking_object_states_change = []

        self.object_sites_dict = {}
        self.random_color = False
        self.objects = []
        self.fixtures = []
        # self.custom_material_dict = {}

        self.custom_asset_dir = os.path.abspath(os.path.join(DIR_PATH, "../assets"))

        self.bddl_file_name = bddl_file_name
        self.parsed_problem = BDDLUtils.robosuite_parse_problem(self.bddl_file_name)
        # crx 0120
        self.obj_of_interest = self.parsed_problem["obj_of_interest"]
        self.dynamic_objects = self.parsed_problem.get("dynamic_objects", {})
        self._domain_randomization(random_init, scene_xml, scene_properties)

        self._assert_problem_name()
        if self.robot_init_id != 0:
            robots = [robots[0]+str(self.robot_init_id)]
        self.grasp_obj = []
        self.place_obj = []
        for goal in self.parsed_problem["goal_state"]:
            if len(goal) == 3:
                if goal[0] == 'checkgrippercontactpart' or goal[0] == 'checkpartiallycontain':
                    continue
                for obj_name in self.obj_of_interest:
                    if goal[1] in obj_name or obj_name in goal[1]:
                        self.grasp_obj.append(obj_name)
                for obj_name in self.obj_of_interest:
                    if goal[2] in obj_name or obj_name in goal[2]:
                        self.place_obj.append(obj_name)
            elif len(goal) == 2:
                for obj_name in self.obj_of_interest:
                    if goal[1] in obj_name or obj_name in goal[1]:
                        self.grasp_obj.append(obj_name)
            

        self._arena_type = arena_type
        self._arena_xml = os.path.join(self.custom_asset_dir, self.scene_xml)
        self._arena_properties = self.scene_properties

        super().__init__(
            robots=robots,
            env_configuration=env_configuration,
            controller_configs=controller_configs,
            mount_types="default",
            gripper_types=gripper_types,
            initialization_noise=initialization_noise,
            use_camera_obs=use_camera_obs,
            has_renderer=has_renderer,
            has_offscreen_renderer=has_offscreen_renderer,
            render_camera=render_camera,
            render_collision_mesh=render_collision_mesh,
            render_visual_mesh=render_visual_mesh,
            render_gpu_device_id=render_gpu_device_id,
            control_freq=control_freq,
            horizon=horizon,
            ignore_done=ignore_done,
            hard_reset=hard_reset,
            camera_names=camera_names,
            camera_heights=camera_heights,
            camera_widths=camera_widths,
            camera_depths=camera_depths,
            camera_segmentations=camera_segmentations,
            renderer=renderer,
            **kwargs,
        )

    def seed(self, seed):
        np.random.seed(seed)

    def reward(self, action=None):
        """
        Reward function for the task.

        Sparse un-normalized reward:

            - a discrete reward of 1.0 is provided if the task succeeds.

        Args:
            action (np.array): [NOT USED]

        Returns:
            float: reward value
        """
        reward = 0.0

        # sparse completion reward
        if self._check_success():
            reward = 1.0

        # Scale reward if requested
        if self.reward_scale is not None:
            reward *= self.reward_scale / 1.0

        return reward

    def _assert_problem_name(self):
        """Implement this to make sure the loaded bddl file has the correct problem name specification."""
        assert (
            self.parsed_problem["problem_name"] == self.__class__.__name__.lower()
        ), "Problem name mismatched"

    def _load_fixtures_in_arena(self, mujoco_arena):
        """
        Load fixtures based on the bddl file description. Please override the method in the custom problem file.
        """
        raise NotImplementedError

    def _load_objects_in_arena(self, mujoco_arena):
        """
        Load movable objects based on the bddl file description
        """
        raise NotImplementedError

    def _load_sites_in_arena(self, mujoco_arena):
        """
        Load sites information from each object to keep track of them for predicate checking
        """
        raise NotImplementedError

    
    def _domain_randomization(self, random_init, scene_xml, scene_properties):
        # crx 0117
        if random_init:
            randomizer = SceneRandomizer(self.workspace_name)
            self.scene_xml, self.scene_properties, self.robot_init_id, self.vertical_view, \
            self.horizon_view, self.scale_factor, self.end_point_vertical, self.end_point_rot, \
            self.noise = randomizer.get_random_config()      
            if not self.scene_xml:
                self.scene_xml = scene_xml
            if not self.scene_properties:
                self.scene_properties = scene_properties
        else:
            self.noise = self.parsed_problem.get("noise", {})
            parsed_scene_properties = self.parsed_problem.get("scene_properties", {})
            if len(parsed_scene_properties) != 0:
                self.scene_properties = parsed_scene_properties
            else:
                self.scene_properties = scene_properties
            parsed_scene_xml = self.parsed_problem.get("scene_xml", None)
            if parsed_scene_xml:
                self.scene_xml = parsed_scene_xml
            else:
                self.scene_xml = scene_xml
            self.robot_init_id = self.parsed_problem.get("robot_init_state", 0)
            cam_view = self.parsed_problem.get("cam_view", {})
            self.vertical_view = cam_view.get("vertical", 0)
            self.horizon_view = cam_view.get("horizon", 0)
            self.scale_factor = float(cam_view.get("scale_factor", 1.0))
            self.end_point_vertical = cam_view.get("end_point_vertical", 0)
            self.end_point_rot = cam_view.get("end_point_rot", 0)
            
    
    def _generate_object_state_wrapper(
        self, skip_object_names=["main_table", "floor", "countertop", "coffee_table"]
    ):
        object_states_dict = {}
        tracking_object_states_changes = []
        for object_name in self.objects_dict.keys():
            if object_name in skip_object_names:
                continue
            object_states_dict[object_name] = ObjectState(self, object_name)
            if (
                self.objects_dict[object_name].category_name
                in VISUAL_CHANGE_OBJECTS_DICT
            ):
                tracking_object_states_changes.append(object_states_dict[object_name])

        for object_name in self.fixtures_dict.keys():
            if object_name in skip_object_names:
                continue
            object_states_dict[object_name] = ObjectState(
                self, object_name, is_fixture=True
            )
            if (
                self.fixtures_dict[object_name].category_name
                in VISUAL_CHANGE_OBJECTS_DICT
            ):
                tracking_object_states_changes.append(object_states_dict[object_name])

        for object_name in self.object_sites_dict.keys():
            if object_name in skip_object_names:
                continue
            object_states_dict[object_name] = SiteObjectState(
                self,
                object_name,
                parent_name=self.object_sites_dict[object_name].parent_name,
            )
        self.object_states_dict = object_states_dict
        self.tracking_object_states_change = tracking_object_states_changes

    def _load_distracting_objects(self, mujoco_arena):
        raise NotImplementedError

    def _load_custom_material(self):
        """
        Define all the textures
        """
        # self.custom_material_dict = dict()

        # tex_attrib = {
        #     "type": "cube"
        # }

        # self.custom_material_dict["bread"] = CustomMaterial(
        #     texture="Bread",
        #     tex_name="bread",
        #     mat_name="MatBread",
        #     tex_attrib=tex_attrib,
        #     mat_attrib={"texrepeat": "3 3", "specular": "0.4","shininess": "0.1"}
        # )

    def _setup_camera(self, mujoco_arena):
        # Modify default agentview camera
        mujoco_arena.set_camera(
            camera_name="canonical_agentview",
            pos=[0.5386131746834771, 0.0, 1.4903500240372423],
            quat=[
                0.6380177736282349,
                0.3048497438430786,
                0.30484986305236816,
                0.6380177736282349,
            ],
        )
        mujoco_arena.set_camera(
            camera_name="agentview",
            pos=[0.5886131746834771, 0.0, 1.4903500240372423],
            quat=[
                0.6380177736282349,
                0.3048497438430786,
                0.30484986305236816,
                0.6380177736282349,
            ],
        )

    def _load_model(self):
        """
        Loads an xml model, puts it in self.model
        """
        super()._load_model()
        # Adjust base pose accordingly
        if self._arena_type == "table":
            xpos = self.robots[0].robot_model.base_xpos_offset["table"](
                self.table_full_size[0]
            )
            self.robots[0].robot_model.set_base_xpos(xpos)
            mujoco_arena = TableArena(
                table_full_size=self.table_full_size,
                table_offset=self.workspace_offset,
                table_friction=(0.6, 0.005, 0.0001),
                xml=self._arena_xml,
                **self._arena_properties,
            )
        elif self._arena_type == "kitchen":
            xpos = self.robots[0].robot_model.base_xpos_offset["kitchen_table"](
                self.kitchen_table_full_size[0]
            )
            self.robots[0].robot_model.set_base_xpos(xpos)
            mujoco_arena = KitchenTableArena(
                table_full_size=self.kitchen_table_full_size,
                table_offset=self.workspace_offset,
                xml=self._arena_xml,
                **self._arena_properties,
            )

        elif self._arena_type == "floor":
            xpos = self.robots[0].robot_model.base_xpos_offset["empty"]
            self.robots[0].robot_model.set_base_xpos(xpos)

            mujoco_arena = EmptyArena(
                xml=self._arena_xml,
                **self._arena_properties,
            )
        elif self._arena_type == "coffee_table":
            xpos = self.robots[0].robot_model.base_xpos_offset["coffee_table"](
                self.coffee_table_full_size[0]
            )
            self.robots[0].robot_model.set_base_xpos(xpos)
            mujoco_arena = CoffeeTableArena(
                xml=self._arena_xml,
                **self._arena_properties,
            )

        elif self._arena_type == "living_room":
            xpos = self.robots[0].robot_model.base_xpos_offset["living_room_table"](
                self.living_room_table_full_size[0]
            )
            self.robots[0].robot_model.set_base_xpos(xpos)
            mujoco_arena = LivingRoomTableArena(
                xml=self._arena_xml,
                **self._arena_properties,
            )

        elif self._arena_type == "study":
            xpos = self.robots[0].robot_model.base_xpos_offset["study_table"](
                self.study_table_full_size[0]
            )
            self.robots[0].robot_model.set_base_xpos(xpos)
            mujoco_arena = StudyTableArena(
                xml=self._arena_xml,
                **self._arena_properties,
            )

        # Arena always gets set to zero origin
        mujoco_arena.set_origin([0, 0, 0])

        self._setup_camera(mujoco_arena)

        self._load_custom_material()

        self._load_fixtures_in_arena(mujoco_arena)

        self._load_objects_in_arena(mujoco_arena)

        self._load_sites_in_arena(mujoco_arena)

        self._generate_object_state_wrapper()

        self._setup_placement_initializer(mujoco_arena)

        self.dyn_objects_names = [
            object for object in self.dynamic_objects.keys()
        ]
        xml_processor = make_xml_processor(
            self.dyn_objects_names, self.random_color
        )
        self.set_xml_processor(xml_processor)

        self.objects = list(self.objects_dict.values())
        self.fixtures = list(self.fixtures_dict.values())
        # task includes arena, robot, and objects of interest
        self.model = ManipulationTask(
            mujoco_arena=mujoco_arena,
            mujoco_robots=[robot.robot_model for robot in self.robots],
            mujoco_objects=self.objects + self.fixtures,
        )

        for fixture in self.fixtures:
            self.model.merge_assets(fixture)

    def _setup_placement_initializer(self, mujoco_arena):
        self.placement_initializer = SequentialCompositeSampler(name="ObjectSampler")
        self.conditional_placement_initializer = SiteSequentialCompositeSampler(
            name="ConditionalSiteSampler"
        )
        self.conditional_placement_on_objects_initializer = SequentialCompositeSampler(
            name="ConditionalObjectSampler"
        )
        self._add_placement_initializer()

    def _setup_references(self):
        """
        Sets up references to important components. A reference is typically an
        index or a list of indices that point to the corresponding elements
        in a flatten array, which is how MuJoCo stores physical simulation data.
        """
        super()._setup_references()

        # Additional object references from this env
        self.obj_body_id = dict()

        for (object_name, object_body) in self.objects_dict.items():
            self.obj_body_id[object_name] = self.sim.model.body_name2id(
                object_body.root_body
            )

        for (fixture_name, fixture_body) in self.fixtures_dict.items():
            self.obj_body_id[fixture_name] = self.sim.model.body_name2id(
                fixture_body.root_body
            )

    def _setup_observables(self):
        """
        Sets up observables to be used for this environment. Creates object-based observables if enabled

        Returns:
            OrderedDict: Dictionary mapping observable names to its corresponding Observable object
        """
        observables = super()._setup_observables()

        observables["robot0_joint_pos"]._active = True

        # low-level object information
        if self.use_object_obs:
            # Get robot prefix and define observables modality
            pf = self.robots[0].robot_model.naming_prefix
            sensors = []
            names = [s.__name__ for s in sensors]

            # Also append handle qpos if we're using a locked drawer version with rotatable handle

            # Create observables
            for name, s in zip(names, sensors):
                observables[name] = Observable(
                    name=name,
                    sensor=s,
                    sampling_rate=self.control_freq,
                )

        pf = self.robots[0].robot_model.naming_prefix

        @sensor(modality="object")
        def world_pose_in_gripper(obs_cache):
            return (
                T.pose_inv(
                    T.pose2mat((obs_cache[f"{pf}eef_pos"], obs_cache[f"{pf}eef_quat"]))
                )
                if f"{pf}eef_pos" in obs_cache and f"{pf}eef_quat" in obs_cache
                else np.eye(4)
            )

        sensors.append(world_pose_in_gripper)
        names.append("world_pose_in_gripper")

        for (i, obj) in enumerate(self.objects):
            obj_sensors, obj_sensor_names = self._create_obj_sensors(
                obj_name=obj.name, modality="object"
            )

            sensors += obj_sensors
            names += obj_sensor_names

        for name, s in zip(names, sensors):
            if name == "world_pose_in_gripper":
                observables[name] = Observable(
                    name=name,
                    sensor=s,
                    sampling_rate=self.control_freq,
                    enabled=True,
                    active=False,
                )
            else:
                observables[name] = Observable(
                    name=name, sensor=s, sampling_rate=self.control_freq
                )

        return observables

    def _create_obj_sensors(self, obj_name, modality="object"):
        """
        Helper function to create sensors for a given object. This is abstracted in a separate function call so that we
        don't have local function naming collisions during the _setup_observables() call.

        Args:
            obj_name (str): Name of object to create sensors for
            modality (str): Modality to assign to all sensors

        Returns:
            2-tuple:
                sensors (list): Array of sensors for the given obj
                names (list): array of corresponding observable names
        """
        pf = self.robots[0].robot_model.naming_prefix

        @sensor(modality=modality)
        def obj_pos(obs_cache):
            return np.array(self.sim.data.body_xpos[self.obj_body_id[obj_name]])

        @sensor(modality=modality)
        def obj_quat(obs_cache):
            return T.convert_quat(
                self.sim.data.body_xquat[self.obj_body_id[obj_name]], to="xyzw"
            )

        @sensor(modality=modality)
        def obj_to_eef_pos(obs_cache):
            # Immediately return default value if cache is empty
            if any(
                [
                    name not in obs_cache
                    for name in [
                        f"{obj_name}_pos",
                        f"{obj_name}_quat",
                        "world_pose_in_gripper",
                    ]
                ]
            ):
                return np.zeros(3)
            obj_pose = T.pose2mat(
                (obs_cache[f"{obj_name}_pos"], obs_cache[f"{obj_name}_quat"])
            )
            rel_pose = T.pose_in_A_to_pose_in_B(
                obj_pose, obs_cache["world_pose_in_gripper"]
            )
            rel_pos, rel_quat = T.mat2pose(rel_pose)
            obs_cache[f"{obj_name}_to_{pf}eef_quat"] = rel_quat
            return rel_pos

        @sensor(modality=modality)
        def obj_to_eef_quat(obs_cache):
            return (
                obs_cache[f"{obj_name}_to_{pf}eef_quat"]
                if f"{obj_name}_to_{pf}eef_quat" in obs_cache
                else np.zeros(4)
            )

        sensors = [obj_pos, obj_quat, obj_to_eef_pos, obj_to_eef_quat]
        names = [
            f"{obj_name}_pos",
            f"{obj_name}_quat",
            f"{obj_name}_to_{pf}eef_pos",
            f"{obj_name}_to_{pf}eef_quat",
        ]

        return sensors, names

    def _add_placement_initializer(self):

        mapping_inv = {}
        for k, values in self.parsed_problem["fixtures"].items():
            for v in values:
                mapping_inv[v] = k
        for k, values in self.parsed_problem["objects"].items():
            for v in values:
                mapping_inv[v] = k

        regions = self.parsed_problem["regions"]
        initial_state = self.parsed_problem["initial_state"]
        problem_name = self.parsed_problem["problem_name"]

        conditioned_initial_place_state_on_sites = []
        conditioned_initial_place_state_on_objects = []
        conditioned_initial_place_state_in_objects = []

        for state in initial_state:
            if state[0] == "on" and state[2] in self.objects_dict:
                conditioned_initial_place_state_on_objects.append(state)
                continue

            # (Yifeng) Given that an object needs to have a certain "containing" region in order to hold the relation "In", we assume that users need to specify the containing region of the object already.
            if state[0] == "in" and state[2] in regions:
                conditioned_initial_place_state_in_objects.append(state)
                continue
            # Check if the predicate is in the form of On(object, region)
            if state[0] == "on" and state[2] in regions:
                object_name = state[1]
                region_name = state[2]
                target_name = regions[region_name]["target"]
                x_ranges, y_ranges = rectangle2xyrange(regions[region_name]["ranges"])
                yaw_rotation = regions[region_name]["yaw_rotation"]
                if (
                    target_name in self.objects_dict
                    or target_name in self.fixtures_dict
                ):
                    conditioned_initial_place_state_on_sites.append(state)
                    continue
                if self.is_fixture(object_name):
                    # This is to place environment fixtures.
                    fixture_sampler = MultiRegionRandomSampler(
                        f"{object_name}_sampler",
                        mujoco_objects=self.fixtures_dict[object_name],
                        x_ranges=x_ranges,
                        y_ranges=y_ranges,
                        rotation=yaw_rotation,
                        rotation_axis="z",
                        z_offset=self.z_offset,  # -self.table_full_size[2],
                        ensure_object_boundary_in_range=False,
                        ensure_valid_placement=False,
                        reference_pos=self.workspace_offset,
                    )
                    self.placement_initializer.append_sampler(fixture_sampler)
                else:
                    # This is to place movable objects.
                    region_sampler = get_region_samplers(
                        problem_name, mapping_inv[target_name]
                    )(
                        object_name,
                        self.objects_dict[object_name],
                        x_ranges=x_ranges,
                        y_ranges=y_ranges,
                        rotation=self.objects_dict[object_name].rotation,
                        rotation_axis=self.objects_dict[object_name].rotation_axis,
                        reference_pos=self.workspace_offset,
                    )
                    self.placement_initializer.append_sampler(region_sampler)
            if state[0] in ["open", "close"]:
                # If "open" is implemented, we assume "close" is also implemented
                if state[1] in self.object_states_dict and hasattr(
                    self.object_states_dict[state[1]], "set_joint"
                ):
                    obj = self.get_object(state[1])
                    if state[0] == "open":
                        joint_ranges = obj.object_properties["articulation"][
                            "default_open_ranges"
                        ]
                    else:
                        joint_ranges = obj.object_properties["articulation"][
                            "default_close_ranges"
                        ]

                    property_initializer = OpenCloseSampler(
                        name=obj.name,
                        state_type=state[0],
                        joint_ranges=joint_ranges,
                    )
                    self.object_property_initializers.append(property_initializer)
            elif state[0] in ["turnon", "turnoff"]:
                # If "turnon" is implemented, we assume "turnoff" is also implemented.
                if state[1] in self.object_states_dict and hasattr(
                    self.object_states_dict[state[1]], "set_joint"
                ):
                    obj = self.get_object(state[1])
                    if state[0] == "turnon":
                        joint_ranges = obj.object_properties["articulation"][
                            "default_turnon_ranges"
                        ]
                    else:
                        joint_ranges = obj.object_properties["articulation"][
                            "default_turnoff_ranges"
                        ]

                    property_initializer = TurnOnOffSampler(
                        name=obj.name,
                        state_type=state[0],
                        joint_ranges=joint_ranges,
                    )
                    self.object_property_initializers.append(property_initializer)

        # Place objects that are on sites
        for state in conditioned_initial_place_state_on_sites:
            object_name = state[1]
            region_name = state[2]
            target_name = regions[region_name]["target"]
            site_xy_size = self.object_sites_dict[region_name].size[:2]
            sampler = SiteRegionRandomSampler(
                f"{object_name}_sampler",
                mujoco_objects=self.objects_dict[object_name],
                x_ranges=[[-site_xy_size[0] / 2, site_xy_size[0] / 2]],
                y_ranges=[[-site_xy_size[1] / 2, site_xy_size[1] / 2]],
                ensure_object_boundary_in_range=True,
                ensure_valid_placement=True,
                rotation=self.objects_dict[object_name].rotation,
                rotation_axis=self.objects_dict[object_name].rotation_axis,
            )
            self.conditional_placement_initializer.append_sampler(
                sampler, {"reference": target_name, "site_name": region_name}
            )
        # Place objects that are on other objects
        for state in conditioned_initial_place_state_on_objects:
            object_name = state[1]
            other_object_name = state[2]
            sampler = ObjectBasedSampler(
                f"{object_name}_sampler",
                mujoco_objects=self.objects_dict[object_name],
                x_ranges=[[0.0, 0.0]],
                y_ranges=[[0.0, 0.0]],
                ensure_object_boundary_in_range=False,
                ensure_valid_placement=False,
                rotation=self.objects_dict[object_name].rotation,
                rotation_axis=self.objects_dict[object_name].rotation_axis,
            )
            self.conditional_placement_on_objects_initializer.append_sampler(
                sampler, {"reference": other_object_name}
            )
        # Place objects inside some containing regions
        for state in conditioned_initial_place_state_in_objects:
            object_name = state[1]
            region_name = state[2]
            target_name = regions[region_name]["target"]
            site_xy_size = self.object_sites_dict[region_name].size[:2]
            sampler = InSiteRegionRandomSampler(
                f"{object_name}_sampler",
                mujoco_objects=self.objects_dict[object_name],
                # x_ranges=[[-site_xy_size[0] / 2, site_xy_size[0] / 2]],
                # y_ranges=[[-site_xy_size[1] / 2, site_xy_size[1] / 2]],
                ensure_object_boundary_in_range=True,
                ensure_valid_placement=True,
                rotation=self.objects_dict[object_name].rotation,
                rotation_axis=self.objects_dict[object_name].rotation_axis,
            )
            self.conditional_placement_initializer.append_sampler(
                sampler, {"reference": target_name, "site_name": region_name}
            )

    def _reset_internal(self):
        """
        Resets simulation internal configurations.
        """
        super()._reset_internal()

        # Reset all object positions using initializer sampler if we're not directly loading from an xml
        if not self.deterministic_reset:
            
            # Sample from the placement initializer for all objects
            for object_property_initializer in self.object_property_initializers:
                if isinstance(object_property_initializer, OpenCloseSampler):
                    joint_pos = object_property_initializer.sample()
                    self.object_states_dict[object_property_initializer.name].set_joint(
                        joint_pos
                    )
                elif isinstance(object_property_initializer, TurnOnOffSampler):
                    joint_pos = object_property_initializer.sample()
                    self.object_states_dict[object_property_initializer.name].set_joint(
                        joint_pos
                    )
                else:
                    print("Warning!!! This sampler doesn't seem to be used")
            # robosuite didn't provide api for this stepping. we manually do this stepping to increase the speed of resetting simulation.
            mujoco.mj_step1(self.sim.model._model, self.sim.data._data)

            object_placements = self.placement_initializer.sample()
            object_placements = self.conditional_placement_initializer.sample(
                self.sim, object_placements
            )
            object_placements = (
                self.conditional_placement_on_objects_initializer.sample(
                    object_placements
                )
            )
            for obj_pos, obj_quat, obj in object_placements.values():
                if obj.name not in list(self.fixtures_dict.keys()):
                    # This is for movable object resetting
                    self.sim.data.set_joint_qpos(
                        obj.joints[-1],
                        np.concatenate([np.array(obj_pos), np.array(obj_quat)]),
                    )
                    # crx 0119 offset
                    if obj.name in self.dyn_objects_names:
                        z_offset = self.dynamic_objects[f'{obj.name}'].get('z_offset', None)
                        if z_offset:
                            obj_pos = list(obj_pos)
                            obj_pos[-1] = float(z_offset) + self.workspace_offset[-1]
                            obj_pos = tuple(obj_pos)
                        self.dyn_object_original_quat[obj.name] = obj_quat
                        self.dyn_object_original_pos[obj.name] = obj_pos
                else:
                    # This is for fixture resetting
                    body_id = self.sim.model.body_name2id(obj.root_body)
                    self.sim.model.body_pos[body_id] = obj_pos
                    self.sim.model.body_quat[body_id] = obj_quat
            mocap_joint_names = []
            mocap_motion_generators = {}
            for name, info in self.dynamic_objects.items():
                mocap_joint_names.append(f"{name}_main_mocap")
                pos = self.dyn_object_original_pos[name]
                quat = self.dyn_object_original_quat[name]
                self.sim.data.set_mocap_pos(mocap_joint_names[-1], pos)
                self.sim.data.set_mocap_quat(mocap_joint_names[-1], quat)
                mocap_motion_generator = self._set_mocap_motion_generator(name, info)
                mocap_motion_generators[name] = mocap_motion_generator

            self.mocap_joint_names = mocap_joint_names
            self.mocap_motion_generators = mocap_motion_generators
            

    def _set_mocap_motion(self):
        for (
            object_name,
            mocap_motion_generator,
        ) in self.mocap_motion_generators.items():
            pos, quat = next(mocap_motion_generator)
            self.sim.data.set_mocap_pos(object_name + '_main_mocap', pos)
            self.sim.data.set_mocap_quat(object_name + '_main_mocap', quat)


    def _set_mocap_motion_generator(self, name, info):
        if info['motion_type'] == 'circle':
            # Get object's initial position and quaternion
            start_pos = self.dyn_object_original_pos[name]
            start_quat = self.dyn_object_original_quat[name]
            # Create circular motion generator
            return CircularMotionGenerator(
                start_pos=start_pos,
                center_pos=info.get('motion_center', [0, 0]),
                start_quat=start_quat,
                period=info.get(
                    'motion_period', 1
                ),  # Convert speed to period
            )
        if info['motion_type'] == 'linear':
            # Get object's initial position and quaternion
            start_pos = self.dyn_object_original_pos[name]
            start_quat = self.dyn_object_original_quat[name]
            # Create linear motion generator
            return LinearMotionGenerator(
                start_pos=start_pos,
                start_quat=start_quat,
                direction=info.get('motion_direction', [0, 1, 0]),
                cycle_time=info.get(
                    'motion_period', 1000
                ),  # Default period is 1 second
                travel_dist=info.get(
                    'motion_travel_dist', 1
                ),  # Use speed as travel distance
            )
        if info['motion_type'] == 'waypoint':
            return SmoothWaypointMotionGenerator(
                waypoints=info.get('motion_waypoints', [[0, 0, 1.2]]),
                start_quat=self.dyn_object_original_quat[name],
                dt=info.get('motion_dt', 0.01),
                loop=info.get('motion_loop', True),
            )
        if info['motion_type'] == 'parabolic':
            return ParabolicMotionGenerator(
                start_pos=info.get('motion_start_pos', [0, 0, 1.2]),
                start_quat=info.get('motion_start_quat', [0, 0, 0, 1]),
                initial_speed=info.get('motion_initial_speed', 1),
                direction=info.get('motion_direction', [0, 1, 0]),
                dt=info.get('motion_dt', 0.01),
                gravity=info.get('motion_gravity', np.array([0, 0, -9.81])),
            )
        raise NotImplementedError(
            f"Invalid motion type: {info['motion_type']}"
        )
    
    def _check_constraint(self, done):
        constraints = self.parsed_problem['constraints']
        cost = {}
        if not done:
            for constraint in constraints:
                predicate_cost = int(self._eval_predicate(constraint))
                cost[constraint[0]] = predicate_cost
        return cost
    
    def check_gripper_force(self, object_geoms):
        left_g_geoms = [
            self.robots[0].gripper._important_geoms['left_fingerpad']
            
        ]
        right_g_geoms = [
            self.robots[0].gripper._important_geoms['right_fingerpad']
        ]
        left_force = self.check_force(left_g_geoms, object_geoms)
        right_force = self.check_force(right_g_geoms, object_geoms)
        return max(left_force, right_force)

    def check_force(self, geoms_1, geoms_2=None):
        if type(geoms_1) is str:
            geoms_1 = [geoms_1]
        elif isinstance(geoms_1, MujocoModel):
            geoms_1 = geoms_1.contact_geoms
        if type(geoms_2) is str:
            geoms_2 = [geoms_2]
        elif isinstance(geoms_2, MujocoModel):
            geoms_2 = geoms_2.contact_geoms
        
        normal_force = 0
        for i in range(self.sim.data.ncon):
            contact = self.sim.data.contact[i]
            c1_in_g1 = self.sim.model.geom_id2name(contact.geom1) in geoms_1
            c2_in_g2 = (
                self.sim.model.geom_id2name(contact.geom2) in geoms_2
                if geoms_2 is not None
                else True
            )
            # check contact geom in geoms (flipped)
            c2_in_g1 = self.sim.model.geom_id2name(contact.geom2) in geoms_1
            c1_in_g2 = (
                self.sim.model.geom_id2name(contact.geom1) in geoms_2
                if geoms_2 is not None
                else True
            )
            if (c1_in_g1 and c2_in_g2) or (c1_in_g2 and c2_in_g1):
                # print(
                #     f'contact: {self.sim.model.geom_id2name(contact.geom1)} {self.sim.model.geom_id2name(contact.geom2)}',
                # )
                f6 = np.zeros(6)
                mujoco.mj_contactForce(
                    self.sim.model._model, self.sim.data._data, i, f6
                )
                normal_force += f6[2]
                return normal_force
        return normal_force


    def _check_contact(self, sim, geoms_1, geoms_2=None):
        """
        Finds contact between two geom groups.
        Args:
            sim (MjSim): Current simulation object
            geoms_1 (str or list of str or MujocoModel): an individual geom name or list of geom names or a model. If
                a MujocoModel is specified, the geoms checked will be its contact_geoms
            geoms_2 (str or list of str or MujocoModel or None): another individual geom name or list of geom names.
                If a MujocoModel is specified, the geoms checked will be its contact_geoms. If None, will check
                any collision with @geoms_1 to any other geom in the environment
        Returns:
            bool: True if any geom in @geoms_1 is in contact with any geom in @geoms_2.
        """
        # Check if either geoms_1 or geoms_2 is a string, convert to list if so
        if type(geoms_1) is str:
            geoms_1 = [geoms_1]
        elif isinstance(geoms_1, MujocoModel):
            geoms_1 = geoms_1.contact_geoms
        if type(geoms_2) is str:
            geoms_2 = [geoms_2]
        elif isinstance(geoms_2, MujocoModel):
            geoms_2 = geoms_2.contact_geoms
        for i in range(sim.data.ncon):
            contact = sim.data.contact[i]
            geom_1_name = sim.model.geom_id2name(contact.geom1)
            if geom_1_name and 'pad_collision' in geom_1_name:
                geom_1_name = geom_1_name[9:]
            geom_2_name = sim.model.geom_id2name(contact.geom2)
            if geom_2_name and 'pad_collision' in geom_2_name:
                geom_2_name = geom_2_name[9:]
            # check contact geom in geoms
            c1_in_g1 = geom_1_name in geoms_1
            c2_in_g2 = geom_2_name in geoms_2 if geoms_2 is not None else True
            # check contact geom in geoms (flipped)
            c2_in_g1 = geom_1_name in geoms_2 if geoms_2 is not None else True
            c1_in_g2 = geom_2_name in geoms_1 

            if (c1_in_g1 and c2_in_g2) or (c1_in_g2 and c2_in_g1):
                # print(geom_2_name)
                return True
        return False

    def check_robot_contact(self, object_geoms):
        """
        Checks whether the specified gripper as defined by @gripper is grasping the specified object in the environment.
        If multiple grippers are specified, will return True if at least one gripper is grasping the object.

        By default, this will return True if at least one geom in both the "left_fingerpad" and "right_fingerpad" geom
        groups are in contact with any geom specified by @object_geoms. Custom gripper geom groups can be
        specified with @gripper as well.

        Args:
            gripper (GripperModel or str or list of str or list of list of str or dict): If a MujocoModel, this is specific
                gripper to check for grasping (as defined by "left_fingerpad" and "right_fingerpad" geom groups). Otherwise,
                this sets custom gripper geom groups which together define a grasp. This can be a string
                (one group of single gripper geom), a list of string (multiple groups of single gripper geoms) or a
                list of list of string (multiple groups of multiple gripper geoms), or a dictionary in the case
                where the robot has multiple arms/grippers. At least one geom from each group must be in contact
                with any geom in @object_geoms for this method to return True.
            object_geoms (str or list of str or MujocoModel): If a MujocoModel is inputted, will check for any
                collisions with the model's contact_geoms. Otherwise, this should be specific geom name(s) composing
                the object to check for contact.

        Returns:
            bool: True if the gripper is grasping the given object
        """
        # Convert object, gripper geoms into standardized form
        if isinstance(object_geoms, MujocoModel):
            o_geoms = object_geoms.contact_geoms
        else:
            o_geoms = (
                [object_geoms] if type(object_geoms) is str else object_geoms
            )
        g_group = []
        for geom_i in range(self.sim.model.ngeom):
            g_name = self.sim.model.geom_id2name(geom_i)
            if g_name and "gripper" in g_name and self.sim.model.geom_group[geom_i] == 0:
                g_group.append(geom_i)
            if g_name and "robot" in g_name and self.sim.model.geom_group[geom_i] == 0:
                g_group.append(geom_i)
        if self._check_contact(self.sim, g_group, o_geoms):
            return True
        return False

    def check_gripper_contact(self, object_geoms):
        """
        Checks whether the specified gripper as defined by @gripper is grasping the specified object in the environment.
        If multiple grippers are specified, will return True if at least one gripper is grasping the object.

        By default, this will return True if at least one geom in both the "left_fingerpad" and "right_fingerpad" geom
        groups are in contact with any geom specified by @object_geoms. Custom gripper geom groups can be
        specified with @gripper as well.

        Args:
            gripper (GripperModel or str or list of str or list of list of str or dict): If a MujocoModel, this is specific
                gripper to check for grasping (as defined by "left_fingerpad" and "right_fingerpad" geom groups). Otherwise,
                this sets custom gripper geom groups which together define a grasp. This can be a string
                (one group of single gripper geom), a list of string (multiple groups of single gripper geoms) or a
                list of list of string (multiple groups of multiple gripper geoms), or a dictionary in the case
                where the robot has multiple arms/grippers. At least one geom from each group must be in contact
                with any geom in @object_geoms for this method to return True.
            object_geoms (str or list of str or MujocoModel): If a MujocoModel is inputted, will check for any
                collisions with the model's contact_geoms. Otherwise, this should be specific geom name(s) composing
                the object to check for contact.

        Returns:
            bool: True if the gripper is grasping the given object
        """
        # Convert object, gripper geoms into standardized form
        if isinstance(object_geoms, MujocoModel):
            o_geoms = object_geoms.contact_geoms
        else:
            o_geoms = (
                [object_geoms] if type(object_geoms) is str else object_geoms
            )
        left_g_geoms = [
            self.robots[0].gripper._important_geoms['left_fingerpad']
            
        ]
        right_g_geoms = [
            self.robots[0].gripper._important_geoms['right_fingerpad']
        ]
        # Search for collisions between each gripper geom group and the object geoms group
        left_contact = right_contact = False
        for g_group in left_g_geoms:
            if self._check_contact(self.sim, g_group, o_geoms):
                left_contact = True
                break
        for g_group in right_g_geoms:
            if self._check_contact(self.sim, g_group, o_geoms):
                right_contact = True
                break
        return left_contact and right_contact


    def check_gripper_contact_part(self, object_1, geom_ids_1):
        assert isinstance(
            geom_ids_1, list
        ), 'geom_ids_1 must be a list of geom ids'
        geom_1 = object_1.contact_geoms
        geoms_to_check = []
        for geom_name in geom_1:
            if isinstance(geom_name, str):
                geom_id = str(extract_trailing_int(geom_name))
                if geom_id is not None and geom_id in geom_ids_1:
                    geoms_to_check.append(geom_name)
            else:
                raise NotImplementedError(f'Invalid geom_id_1: {geom_name}')
        return self.check_gripper_contact(geoms_to_check)


    def _eval_predicate(self, state):
        if len(state) == 3:
            predicate_fn_name = state[0]
            # Checking binary logical predicates
            if predicate_fn_name == 'checkgrippercontactpart':
                return eval_predicate_fn(
                    predicate_fn_name,
                    self.object_states_dict[state[1]],
                    state[2],
                )
            if predicate_fn_name == 'checkpartiallycontain':
                object_1_name = state[1]
                return eval_predicate_fn(
                    predicate_fn_name,
                    self.object_states_dict[object_1_name],
                    [self.object_states_dict[object_2_name] for object_2_name in state[2]]
                )
            if predicate_fn_name == 'checkpartpartiallycontain':
                object_1_name = state[1]
                return eval_predicate_fn(
                    predicate_fn_name,
                    self.object_states_dict[object_1_name],
                    [self.object_states_dict[object_2_name] for object_2_name in state[2]]
                )
            object_1_name = state[1]
            object_2_name = state[2]
            return eval_predicate_fn(
                predicate_fn_name,
                self.object_states_dict[object_1_name],
                self.object_states_dict[object_2_name],
            )
        if len(state) == 2:
            # Checking unary logical predicates
            predicate_fn_name = state[0]
            object_name = state[1]
            if predicate_fn_name == 'checkgripperforce':
                force = eval_predicate_fn(
                    predicate_fn_name,
                    self.object_states_dict[state[1]],
                )
                if force > 0:
                    print(f'force: {force}')
                return force > self.contact_force_threshold
            
            return eval_predicate_fn(
                predicate_fn_name, self.object_states_dict[object_name]
            )
        if len(state) == 4:
            # Checking binary logical predicates
            predicate_fn_name = state[0]
            object_1_name = state[1]
            object_2_name = state[2]
            return float(state[3]) < eval_predicate_fn(
                predicate_fn_name,
                self.object_states_dict[object_1_name],
                self.object_states_dict[object_2_name],
            )
        if len(state) == 5:
            # Checking binary logical predicates
            predicate_fn_name = state[0]
            if predicate_fn_name == 'incontactpart':
                object_1_name = state[1]
                object_2_name = state[2]
                geom_name_1 = state[3]
                geom_name_2 = state[4]
                if geom_name_1 == 'all':
                    geom_name_1 = object_1_name
                elif isinstance(geom_name_1, list):
                    geom_name_1 = [
                        object_1_name + '_g' + (geom_name)
                        for geom_name in geom_name_1
                    ]
                else:
                    raise NotImplementedError(
                        f'Invalid geom_name_1: {geom_name_1}'
                    )
                if geom_name_2 == 'all':
                    geom_name_2 = object_2_name
                elif isinstance(geom_name_2, list):
                    geom_name_2 = [
                        object_2_name + '_g' + (geom_name)
                        for geom_name in geom_name_2
                    ]
                else:
                    raise NotImplementedError(
                        f'Invalid geom_name_2: {geom_name_2}'
                    )
                return self._check_contact(geom_name_1, geom_name_2)
            raise NotImplementedError(f'Invalid state length: {len(state)}')
        raise NotImplementedError(f'Invalid state length: {len(state)}')


    def _check_success(self):
        """
        Check if the goal is achieved. Consider conjunction goals at the moment
        """
        goal_state = self.parsed_problem["goal_state"]
        result = True
        for state in goal_state:
            result = self._eval_predicate(state) and result
        return result


    def visualize(self, vis_settings):
        """
        In addition to super call, visualize gripper site proportional to the distance to the drawer handle.

        Args:
            vis_settings (dict): Visualization keywords mapped to T/F, determining whether that specific
                component should be visualized. Should have "grippers" keyword as well as any other relevant
                options specified.
        """
        # Run superclass method first
        super().visualize(vis_settings=vis_settings)

    def step(self, action):
        if self.action_dim == 4 and len(action) > 4:
            # Convert OSC_POSITION action
            action = np.array(action)
            action = np.concatenate((action[:3], action[-1:]), axis=-1)
        self._set_mocap_motion()
        obs, reward, done, info = super().step(action)
        done = self._check_success()
        cost = self._check_constraint(done)
        info['cost'] = cost
        return obs, reward, done, info

    def _pre_action(self, action, policy_step=False):
        super()._pre_action(action, policy_step=policy_step)

    def _post_action(self, action):
        reward, done, info = super()._post_action(action)

        self._post_process()

        return reward, done, info

    def _post_process(self):
        # Update some object states, such as light switching etc.
        for object_state in self.tracking_object_states_change:
            object_state.update_state()


    def get_robot_state_vector(self, obs):
        return np.concatenate(
            [obs["robot0_gripper_qpos"], obs["robot0_eef_pos"], obs["robot0_eef_quat"]]
        )

    def is_fixture(self, object_name):
        """
        Check if an object is defined as a fixture in the task

        Args:
            object_name (str): The name string of the object in query
        """
        return object_name in list(self.fixtures_dict.keys())

    @property
    def language_instruction(self):
        return self.parsed_problem["language"]

    def get_object(self, object_name):
        for query_dict in [
            self.fixtures_dict,
            self.objects_dict,
            self.object_sites_dict,
        ]:
            if object_name in query_dict:
                return query_dict[object_name]
