# import os
# import re
# import numpy as np

# from robosuite.models.objects import MujocoXMLObject
# from robosuite.utils.mjcf_utils import xml_path_completion

# from libero.libero.envs.base_object import register_object

# import pathlib

# from libero.libero.envs.base_object import (
#     register_visual_change_object,
#     register_object,
# )

import os
from collections import namedtuple

from libero.libero.utils.mu_utils import get_scene_class
from libero.libero.utils.bddl_generation_utils import *
from libero.libero.utils.mu_utils import register_mu, InitialSceneTemplates
from libero.libero.utils.task_generation_utils import register_task_info, get_task_info, generate_bddl_from_task_info

# from libero.libero.custom_benchmark.mu_creation import KitchenDemoSceneWithDynamics

# # class CustomObjects(MujocoXMLObject):
# #     def __init__(self, custom_path, name, obj_name, joints=[dict(type="free", damping="0.0005")], gravcomp=True):
# #         # make sure custom path is an absolute path
# #         if gravcomp:
# #             custom_path = custom_path.replace(".xml", "_gravcomp.xml")
# #         assert(os.path.isabs(custom_path)), "Custom path must be an absolute path"
# #         # make sure the custom path is also an xml file
# #         assert(custom_path.endswith(".xml")), "Custom path must be an xml file"
# #         super().__init__(
# #             custom_path,
# #             name=name,
# #             joints=joints,
# #             obj_type="all",
# #             duplicate_collision_geoms=False,
# #         )
# #         # Ensure the root body named "object" has gravity compensation enabled without modifying source XML.
# #         # We search for both prefixed (e.g., "0_object") and raw ("object") names, and set gravcomp="1" if found.
# #         try:
# #             # Prefer prefixed name if available
# #             target_names = [self.correct_naming("object"), "object"]
# #             # import pdb; pdb.set_trace()
# #             for body in self.worldbody.findall(".//body"):
# #                 name = body.get("name")
# #                 if name in target_names:
# #                     body.set("gravcomp", "1")
# #                     break
                
# #         except Exception as e:
# #             # Fail silently if structure differs; this is a best-effort augmentation
# #             print(e)
# #             pass
        
# #         self.category_name = "_".join(
# #             re.sub(r"([A-Z])", r" \1", self.__class__.__name__).split()
# #         ).lower()
# #         self.object_properties = {"vis_site_names": {}}

# # @register_object
# # class CustomPorcelainMug(CustomObjects):
# #     def __init__(self,
# #                  name="custom_porcelain_mug",
# #                  obj_name="custom_porcelain_mug",
# #                  ):
# #         super().__init__(
# #             custom_path=os.path.abspath(os.path.join(
# #                 "/data14/rongxu.cui.2510/LIBERO", "libero", "libero", "custom_assets", "objects", "porcelain_mug", "porcelain_mug.xml"
# #             )),
# #             name=name,
# #             obj_name=obj_name,
# #         )

# #         self.rotation = {
# #             "x": (-np.pi/2, -np.pi/2),
# #             "y": (-np.pi, -np.pi),
# #             "z": (np.pi, np.pi),
# #         }
# #         self.rotation_axis = None

# # @register_object
# # class CustomRedCoffeeMug(CustomObjects):
# #     def __init__(self,
# #                  name="custom_red_coffee_mug",
# #                  obj_name="custom_red_coffee_mug",
# #                  ):
# #         super().__init__(
# #             custom_path=os.path.abspath(os.path.join(
# #                 "/data14/rongxu.cui.2510/LIBERO", "libero", "libero", "custom_assets", "objects", "red_coffee_mug", "red_coffee_mug.xml"
# #             )),
# #             name=name,
# #             obj_name=obj_name,
# #         )

# #         self.rotation = {
# #             "x": (-np.pi/2, -np.pi/2),
# #             "y": (-np.pi, -np.pi),
# #             "z": (np.pi, np.pi),
# #         }
# #         self.rotation_axis = None
        
# # @register_object
# # class CustomWhiteYellowMug(CustomObjects):
# #     def __init__(self,
# #                  name="custom_white_yellow_mug",
# #                  obj_name="custom_white_yellow_mug",
# #                  ):
# #         super().__init__(
# #             custom_path=os.path.abspath(os.path.join(
# #                 "/data14/rongxu.cui.2510/LIBERO", "libero", "libero", "custom_assets", "objects", "white_yellow_mug", "white_yellow_mug.xml"
# #             )),
# #             name=name,
# #             obj_name=obj_name,
# #         )

# #         self.rotation = {
# #             "x": (-np.pi/2, -np.pi/2),
# #             "y": (-np.pi, -np.pi),
# #             "z": (np.pi, np.pi),
# #         }
# #         self.rotation_axis = None


# # @register_mu(scene_type="kitchen")
# # class KitchenDemoSceneWithDynamics(InitialSceneTemplates):
# #     def __init__(self):

# #         fixture_num_info = {
# #             "kitchen_table": 1,
# #             "flat_stove": 1,
# #         }

# #         object_num_info = {
# #             "custom_porcelain_mug": 1,
# #             "custom_red_coffee_mug": 1,
# #             "custom_white_yellow_mug": 1,
# #             "chefmate_8_frypan": 1,
# #             "moka_pot": 1
# #         }

# #         super().__init__(
# #             workspace_name="kitchen_table",
# #             fixture_num_info=fixture_num_info,
# #             object_num_info=object_num_info,
# #         )

# #     def define_regions(self):
# #         self.regions.update(
# #             self.get_region_dict(
# #                 region_centroid_xy=[-0.20, 0.20],
# #                 region_name="flat_stove_init_region",
# #                 target_name=self.workspace_name,
# #                 region_half_len=0.01,
# #             )
# #         )

# #         self.regions.update(
# #             self.get_region_dict(
# #                 region_centroid_xy=[-0.05, -0.25],
# #                 region_name="frypan_init_region",
# #                 target_name=self.workspace_name,
# #                 region_half_len=0.025,
# #             )
# #         )

# #         self.regions.update(
# #             self.get_region_dict(
# #                 region_centroid_xy=[0.05, 0.0],
# #                 region_name="moka_pot_init_region",
# #                 target_name=self.workspace_name,
# #                 region_half_len=0.025,
# #             )
# #         )

# #         self.regions.update(
# #             self.get_region_dict(
# #                 region_centroid_xy=[0.2, -0.2],
# #                 region_name="custom_porcelain_mug_init_region",
# #                 target_name=self.workspace_name,
# #                 region_half_len=0.005,
# #             )
# #         )

# #         self.regions.update(
# #             self.get_region_dict(
# #                 region_centroid_xy=[0.2, 0.0],
# #                 region_name="custom_red_coffee_mug_init_region",
# #                 target_name=self.workspace_name,
# #                 region_half_len=0.005,
# #             )
# #         )
        
# #         self.regions.update(
# #             self.get_region_dict(
# #                 region_centroid_xy=[0.2, 0.2],
# #                 region_name="custom_white_yellow_mug_init_region",
# #                 target_name=self.workspace_name,
# #                 region_half_len=0.005,
# #             )
# #         )

# #         self.xy_region_kwargs_list = get_xy_region_kwargs_list_from_regions_info(
# #             self.regions
# #         )

# #     @property
# #     def init_states(self):
# #         states = [
# #             ("On", "flat_stove_1", "kitchen_table_flat_stove_init_region"),
# #             ("On", "chefmate_8_frypan_1", "kitchen_table_frypan_init_region"),
# #             ("On", "moka_pot_1", "kitchen_table_moka_pot_init_region"),
# #             ("On", "custom_porcelain_mug_1", "kitchen_table_custom_porcelain_mug_init_region"),
# #             ("On", "custom_red_coffee_mug_1", "kitchen_table_custom_red_coffee_mug_init_region"),
# #             ("On", "custom_white_yellow_mug_1", "kitchen_table_custom_white_yellow_mug_init_region"),
# #         ]
# #         return states

# #     @property
# #     def dynamics_specs(self):
# #         # 三种动态：线性、圆周、静止
# #         return [
# #             {
# #                 "obj": "custom_porcelain_mug_1",
# #                 "type": "kinematic",
# #                 "traj": {"kind": "linear", "p0": [-0.10, 0.00, 0.95], "v": [0.01, 0.00, 0.00], "quat": [0, 0, 0, 1]},
# #             },
# #             {
# #                 "obj": "custom_red_coffee_mug_1",
# #                 "type": "kinematic",
# #                 "traj": {"kind": "circle", "center": [0.00, 0.10, 0.95], "radius": 0.12, "omega": 1.57, "z": 0.95},
# #             },
# #             {
# #                 "obj": "custom_white_yellow_mug_1",
# #                 "type": "kinematic",
# #                 "traj": {"kind": "linear", "p0": [0.10, 0.15, 1.10], "v": [0.00, 0.00, 0.00], "quat": [0, 0, 0, 1]},
# #             },
# #         ]
    


# # scene_name = "kitchen_demo_scene_with_dynamics"
# # language = "libero demo behaviors1"

# # register_task_info(language,
# #                    scene_name=scene_name,
# #                    objects_of_interest=[],
# #                    goal_states=[
# #                     #    ("Open", "wooden_cabinet_1_top_region"),
# #                     #    ("In", "libero_mug_yellow_1", "wooden_cabinet_1_top_region"),
# #                     ("Turnon", "flat_stove_1"),
# #                     ("On", "moka_pot_1", "kitchen_table_moka_pot_init_region"),
# #                     ],
# # )

# # YOUR_BDDL_FILE_PATH = "/data14/rongxu.cui.2510/LIBERO/libero/libero/custom_pddl/libero_custom_10"
# # bddl_file_names, failures = generate_bddl_from_task_info(folder=YOUR_BDDL_FILE_PATH)
# # print(bddl_file_names)

# # print("Encountered some failures: ", failures)

# # with open(bddl_file_names[0], "r") as f:
# #     print(f.read())

from libero.libero.envs import OffScreenRenderEnv
# from IPython.display import display
from PIL import Image

import torch
import torchvision
import imageio



def append_unique(filename, text):
    # 确保行格式一致（避免带换行重复）
    text = text.strip()

    # 如果文件不存在，直接创建并写入
    try:
        with open(filename, "r", encoding="utf-8") as f:
            lines = {line.strip() for line in f}
    except FileNotFoundError:
        lines = set()

    # 判断是否存在
    if text not in lines:
        with open(filename, "a", encoding="utf-8") as f:
            f.write(text + "\n")
        print(f"追加写入成功: {text}")
    else:
        print(f"已存在，跳过: {text}")
        # import pdb; pdb.set_trace()

# # dirs = '/data14/rongxu.cui.2510/benchmark/LIBERO/libero/libero/bddl_files/libero_goal'
# # for item in os.listdir(dirs):
# #     if item.endswith('.bddl'):
# #         bddl_file_name = os.path.join(dirs, item)
# #         env_args = {
# #             "bddl_file_name": bddl_file_name,
# #             "camera_heights": 256,
# #             "camera_widths": 256
# #         }

# #         env = OffScreenRenderEnv(**env_args)
# #         obs = env.reset()
# #         for i in range(10):
# #             obs, _, _, _ = env.step([0.] * 7)
# #         # display(Image.fromarray(obs["agentview_image"][::-1]))
# #         Image.fromarray(obs["agentview_image"][::-1, ::-1]).save(os.path.join(dirs, item.replace('.bddl', '.png')))
start = False
dirss = '/data14/rongxu.cui.2510/benchmark/LIBERO-Safety/libero/libero/bddl_files_new/obstacle_avoidance/L2_ranges2'
for task_name in sorted(os.listdir(dirss)):
    if not task_name.endswith('.bddl'):
        continue
    # if task_name == 'KITCHEN_SCENE3_turn_on_the_stove_and_put_the_moka_pot_on_it_table_1_granulated_sugar_jar_1_with_hand.bddl':
    #     start = True
    # if start:
    bddl_file_name = os.path.join(dirss, task_name)
    env_args = {
        "bddl_file_name": bddl_file_name,
        "camera_heights": 512,
        "camera_widths": 512
    }




    env = OffScreenRenderEnv(**env_args)
    
    obs = env.reset()
    sim = env.sim
    # for i in range(env.sim.model.njnt):
    #     name = env.sim.model.joint_id2name(i)
    #     print(i, name)
    # import pdb; pdb.set_trace()
    # for i in range(10):
    #     # import pdb; pdb.set_trace()
    #     # xzy = map_dof_to_joint_and_qpos(env.sim, 51)
    #     obs, _, _, _ = env.step([0.] * 7)
    #     qacc = env.sim.data.qacc.copy()
    #     THRESH = 1e6
    #     if not np.all(np.isfinite(qacc) | (np.abs(qacc) > THRESH)):
            
    #         bad_idx = np.where(~np.isfinite(qacc) | (np.abs(qacc) > THRESH))[0]
    #         print("Step", i, "found non-finite qacc at indices:", bad_idx)
    #         print("qpos:", env.sim.data.qpos)      # 关节位置
    #         print("qvel:", env.sim.data.qvel)      # 关节速度
    #         print("qacc (excerpt):", qacc[bad_idx])
    #         print("qfrc_applied (forces applied):", env.sim.data.qfrc_applied[:200])  # 观察力矩
    #         print("number of contacts:", env.sim.data.ncon)
    #         # 如果支持，打印接触细节（contact array）
    #         break
    # Image.fromarray(obs["agentview_image"][::-1]).save(bddl_file_name.replace('.bddl', '.png'))\
    replay_imgs = []
    collided = False
    for i in range(20):
        action = [0.] * 7
        obs, _, _, _ = env.step(action)

    for i in range(200):
        obs, _, _, _ = env.step([0.] * 7)
        img = obs["agentview_image"][::-1]
        replay_imgs.append(img)
    
    mp4_path = bddl_file_name.replace('.bddl', '.mp4')
    video_writer = imageio.get_writer(mp4_path, fps=30)
    for img in replay_imgs:
        video_writer.append_data(img)
    video_writer.close()
    print("save mp4 to", mp4_path)
        

    env.close()
    
        
    






