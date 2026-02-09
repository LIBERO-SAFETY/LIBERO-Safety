from bddl.parsing import *

import itertools
import numpy as np
import xml.etree.ElementTree as ET
import random

pi = np.pi

def get_regions(t, regions, group):
    group.pop(0)
    while group:
        region = group.pop(0)
        region_name = region[0]
        target_name = None
        region_dict = {
            "target": None,
            "ranges": [],
            "extra": [],
            "yaw_rotation": [0, 0],
            "rgba": [0, 0, 1, 0],
        }
        for attribute in region[1:]:
            if attribute[0] == ":target":
                assert len(attribute) == 2
                region_dict["target"] = attribute[1]
                target_name = attribute[1]
            elif attribute[0] == ":ranges":
                for rect_range in attribute[1]:
                    assert (
                        len(rect_range) == 4
                    ), f"Dimension of rectangular range mismatched!!, supposed to be 4, only found {len(rect_range)}"
                    region_dict["ranges"].append([float(x) for x in rect_range])
            elif attribute[0] == ":yaw_rotation":
                for value in attribute[1]:
                    region_dict["yaw_rotation"] = [eval(x) for x in value]
            elif attribute[0] == ":rgba":
                assert (
                    len(attribute[1]) == 4
                ), f"Missing specification for rgba color, supposed to be 4 dimension, but only got  {attribute[1]}"
                region_dict["rgba"] = [float(x) for x in attribute[1]]
            else:
                raise NotImplementedError
        regions[target_name + "_" + region_name] = region_dict


def get_scenes(t, scene_properties, group):
    group.pop(0)
    while group:
        scene_property = group.pop(0)   
        if scene_property[0] == ":floor":
            assert len(scene_property) == 2
            scene_properties["floor_style"] = scene_property[1]
        elif scene_property[0] == ":wall":
            assert len(scene_property) == 2
            scene_properties["wall_style"] = scene_property[1]
        else:
            raise NotImplementedError


def get_problem_info(problem_filename):
    domain_name = "unknown"
    problem_filename = problem_filename
    tokens = scan_tokens(filename=problem_filename)
    if isinstance(tokens, list) and tokens.pop(0) == "define":
        problem_name = "unknown"
        language_instruction = ""
        while tokens:
            group = tokens.pop()
            t = group[0]
            if t == "problem":
                problem_name = group[-1]
            elif t == ":domain":
                domain_name = "robosuite"
            elif t == ":language":
                group.pop(0)
                language_instruction = group
    return {
        "problem_name": problem_name,
        "domain_name": domain_name,
        "language_instruction": " ".join(language_instruction),
    }


def get_dynamic_objects(t, dynamic_objects, group):
    group.pop(0)
    while group:
        dynamic_object = group.pop(0)
        dynamic_object_dict = {}
        for attribute in dynamic_object[1:]:
            if attribute[0] == ':motion_type':
                dynamic_object_dict['motion_type'] = attribute[1]
            elif attribute[0] == ':motion_speed':
                dynamic_object_dict['motion_speed'] = attribute[1]
            elif attribute[0] == ':motion_radius':
                dynamic_object_dict['motion_radius'] = attribute[1]
            elif attribute[0] == ':motion_center':
                dynamic_object_dict['motion_center'] = attribute[1]
            elif attribute[0] == ':motion_quat':
                dynamic_object_dict['motion_quat'] = attribute[1]
            elif attribute[0] == ':motion_pos':
                dynamic_object_dict['motion_pos'] = attribute[1]
            elif attribute[0] == ':motion_direction':
                dynamic_object_dict['motion_direction'] = attribute[1]
            elif attribute[0] == ':motion_angle':
                dynamic_object_dict['motion_angle'] = attribute[1]
            elif attribute[0] == ':motion_period':
                dynamic_object_dict['motion_period'] = attribute[1]
            elif attribute[0] == ':motion_travel_dist':
                dynamic_object_dict['motion_travel_dist'] = attribute[1]
            elif attribute[0] == ':motion_waypoints':
                dynamic_object_dict['motion_waypoints'] = attribute[1]
            elif attribute[0] == ':motion_dt':
                dynamic_object_dict['motion_dt'] = attribute[1]
            elif attribute[0] == ':z_offset':
                dynamic_object_dict['z_offset'] = attribute[1]
            elif attribute[0] == ':motion_loop':
                dynamic_object_dict['motion_loop'] = attribute[1]
            elif attribute[0] == ':motion_initial_speed':
                dynamic_object_dict['motion_initial_speed'] = attribute[1]
            elif attribute[0] == ':motion_direction':
                dynamic_object_dict['motion_direction'] = attribute[1]
            elif attribute[0] == ':motion_start_pos':
                dynamic_object_dict['motion_start_pos'] = attribute[1]
            elif attribute[0] == ':motion_start_quat':
                dynamic_object_dict['motion_start_quat'] = attribute[1]
            elif attribute[0] == ':motion_center':
                dynamic_object_dict['motion_center'] = attribute[1]
            elif attribute[0] == ':motion_radius':
                dynamic_object_dict['motion_radius'] = attribute[1]
            elif attribute[0] == ':motion_gravity':
                dynamic_object_dict['motion_gravity'] = attribute[1]
            else:
                raise NotImplementedError(
                    f'Invalid motion attribute: {attribute[0]}'
                )
        dynamic_objects[f'{dynamic_object[0]}'] = dynamic_object_dict
        # dynamic_objects.append(dynamic_object_dict)


def get_cam_view(t, cam_view, group):
    group.pop(0)
    while group:
        cam_info = group.pop(0)
        if cam_info[0] == ':vertical':
            cam_view['vertical'] = cam_info[1]
        elif cam_info[0] == ':horizon':
            cam_view['horizon'] = cam_info[1]
        elif cam_info[0] == ':scale_factor':
            cam_view['scale_factor'] = cam_info[1]
        elif cam_info[0] == ':end_point_vertical':
            cam_view['end_point_vertical'] = cam_info[1]
        elif cam_info[0] == ':end_point_rot':
            cam_view['end_point_rot'] = cam_info[1] 


def get_noise(t, noise, group):
    group.pop(0)
    while group:
        noise_info = group.pop(0)
        if noise_info[0] == ':gaussian':
            noise['gaussian'] = noise_info[1]
        elif noise_info[0] == ':zoom':
            noise['zoom'] = noise_info[1]
        elif noise_info[0] == ':fog':
            noise['fog'] = noise_info[1]
        elif noise_info[0] == ':glass':
            noise['glass'] = noise_info[1]
        elif noise_info[0] == ':motion':
            noise['motion'] = noise_info[1] 
        elif noise_info[0] == ':pepper':
            noise['pepper'] = noise_info[1] 
        elif noise_info[0] == ':salt':
            noise['salt'] = noise_info[1] 
            

def robosuite_parse_problem(problem_filename):
    domain_name = "robosuite"
    problem_filename = problem_filename
    # random
    tokens = scan_tokens(filename=problem_filename)
    if isinstance(tokens, list) and tokens.pop(0) == "define":
        problem_name = "unknown"
        objects = {}
        obj_of_interest = []
        initial_state = []
        goal_state = []
        constraint = []
        dynamic_objects = {}
        cam_view = {}
        fixtures = {}
        regions = {}
        obstacle = []
        scene_properties = {}
        noise = {}
        scene_xml = None
        robot_init_state = 0
        language_instruction = ""
        while tokens:
            group = tokens.pop()
            t = group[0]
            if t == "problem":
                problem_name = group[-1]
            elif t == ":domain":
                if domain_name != group[-1]:
                    raise Exception("Different domain specified in problem file")
            elif t == ":requirements":
                pass
            elif t == ":objects":
                group.pop(0)
                object_list = []
                while group:
                    if group[0] == "-":
                        group.pop(0)
                        objects[group.pop(0)] = object_list
                        object_list = []
                    else:
                        object_list.append(group.pop(0))
                if object_list:
                    if not "object" in objects:
                        objects["object"] = []
                    objects["object"] += object_list
            elif t == ":obj_of_interest":
                group.pop(0)
                while group:
                    obj_of_interest.append(group.pop(0))
            elif t == ":fixtures":
                group.pop(0)
                fixture_list = []
                while group:
                    if group[0] == "-":
                        group.pop(0)
                        fixtures[group.pop(0)] = fixture_list
                        fixture_list = []
                    else:
                        fixture_list.append(group.pop(0))
                if fixture_list:
                    if not "fixture" in fixtures:
                        fixtures["fixture"] = []
                    fixtures["fixture"] += fixture_list
            elif t == ":regions":
                get_regions(t, regions, group)
            elif t == ":language":
                group.pop(0)
                language_instruction = group
            elif t == ":init":
                group.pop(0)
                initial_state = group
            elif t == ":goal":
                package_predicates(group[1], goal_state, "", "goals")
            elif t == ':robot_init_state':
                group.pop(0)
                robot_init_state = int(group[0])
            elif t == ":obstacle":
                group.pop(0)
                while group:
                    obstacle.append(group.pop(0))
            elif t == ":dynamics":
                get_dynamic_objects(t, dynamic_objects, group)
            elif t == ":noise":
                get_noise(t, noise, group)
            elif t == ":cam_view":
                get_cam_view(t, cam_view, group)
            elif t == ":scene_properties":
                get_scenes(t, scene_properties, group)
            elif t == ":scene_xml":
                group.pop(0)
                scene_xml = group[0]
            elif t == ":constraint":
                package_predicates(group[1], constraint, '', 'constraints')
            else:
                print("%s is not recognized in problem" % t)
        return {
            "problem_name": problem_name,
            "fixtures": fixtures,
            "regions": regions,
            "objects": objects,
            "scene_properties": scene_properties,
            "scene_xml": scene_xml,
            "initial_state": initial_state,
            "goal_state": goal_state,
            "language_instruction": language_instruction,
            "obj_of_interest": obj_of_interest,
            "dynamic_objects": dynamic_objects,
            "obstacle": obstacle,
            "noise": noise,
            "cam_view": cam_view,
            "robot_init_state": robot_init_state,
            "constraint": constraint,
        }
    else:
        raise Exception(
            f"Problem {behavior_activity} {activity_definition} does not match problem pattern"
        )


def make_xml_processor(body_names, random_color):
    """
    Create an XML processor function that modifies MuJoCo XML strings.

    The returned function processes XML strings to:
    1. Add mocap bodies and weld constraints for each body_name_main (if they don't exist)
    2. Add rgba attributes to all elements with material attributes (if random_color is True)

    Args:
        body_names: list of strings, e.g., ["milk_1", "lemon_1"]
        random_color: bool, whether to add random rgba colors to material elements

    Returns:
        function: xml_processor(xml_string) that takes an XML string and returns a modified XML string
    """

    def xml_processor(xml_string):
        root = ET.fromstring(xml_string)

        # Find worldbody and equality nodes
        worldbody = root.find('worldbody')
        equality = root.find('equality')
        if equality is None:
            equality = ET.SubElement(root, 'equality')

        # Iterate through body_names
        for name in body_names:
            full_body_name = f'{name}_main'  # Automatically append _main
            mocap_body_name = f'{full_body_name}_mocap'  # Mocap body name

            # Check if mocap body already exists
            existing_mocap = worldbody.find(
                f".//body[@name='{mocap_body_name}']"
            )
            if existing_mocap is None:
                # If not exists, append mocap body
                mocap_body = ET.Element(
                    'body',
                    {'mocap': 'true', 'name': mocap_body_name, 'pos': '0 0 0'},
                )
                worldbody.append(mocap_body)
                weld = ET.Element(
                    'weld',
                    {
                        'body1': full_body_name,
                        'body2': mocap_body_name,
                        'solimp': '0.9 0.95 0.001',
                        'solref': '0.02 1',
                    },
                )
                equality.append(weld)
            else:
                # If exists, skip
                continue

        # Process all elements with material attributes and add rgba attributes
        # Recursively traverse all elements
        def process_elements(element):
            # Check if current element has material attribute
            if 'material' in element.attrib:
                material_value = element.attrib['material']
                # If material doesn't contain "robot0" and doesn't have rgba attribute, add it
                if (
                    'robot0' not in material_value
                    and 'rgba' not in element.attrib
                ):
                    # Add default rgba value (random color with full opacity)
                    color = np.append(
                        np.random.uniform(low=0.2, high=0.8, size=3), 1
                    )
                    color_string = ' '.join(map(str, color))
                    element.set('rgba', color_string)

            # Process child elements
            for child in element:
                process_elements(child)

        if random_color:
            process_elements(root)

        return ET.tostring(root, encoding='unicode')

    return xml_processor