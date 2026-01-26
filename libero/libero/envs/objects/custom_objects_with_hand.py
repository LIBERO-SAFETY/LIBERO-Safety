import os
import re
import numpy as np
import copy
from robosuite.models.objects import MujocoXMLObject
from robosuite.utils.mjcf_utils import array_to_string
 
import pathlib
 
# 使用pathlib计算项目根目录的绝对路径
absolute_path = pathlib.Path(__file__).parent.parent.parent.absolute()
 
from libero.libero.envs.base_object import register_object
 
def hack_robosuite():
    """
    Hack 'robosuite.models.objects.objects.MujocoXMLObject._get_object_subtree' function for custom objects supports.
    """
    from robosuite.models.objects.objects import (
        MujocoXMLObject, GEOMTYPE2GROUP, array_to_string, OBJECT_COLLISION_COLOR,
        ET, new_joint
    )

    def _get_object_subtree(self):
        # Parse object

        # # ===== Original Code =====================================
        # obj = copy.deepcopy(self.worldbody.find("./body/body[@name='object']"))
        # # =========================================================

        # ===== Modified Code =====================================
        obj = self.worldbody.find("./body/body[@name='object']")
        if obj is None:
            obj = self.worldbody.find("./body[@name='object']")
        if obj is None:
            raise ValueError(
                "Could not find object body with name='object' at either "
                "./body[@name='object'] or ./body/body[@name='object']. "
                "Please check your XML structure."
            )
        obj = copy.deepcopy(obj)
        # =========================================================

        # Rename this top level object body (will have self.naming_prefix added later)
        obj.attrib["name"] = "main"
        # Get all geom_pairs in this tree
        geom_pairs = self._get_geoms(obj)

        # Define a temp function so we don't duplicate so much code
        obj_type = self.obj_type

        def _should_keep(el):
            return int(el.get("group")) in GEOMTYPE2GROUP[obj_type]

        # Loop through each of these pairs and modify them according to @elements arg
        for i, (parent, element) in enumerate(geom_pairs):
            # Delete non-relevant geoms and rename remaining ones
            if not _should_keep(element):
                parent.remove(element)
            else:
                g_name = element.get("name")
                g_name = g_name if g_name is not None else f"g{i}"
                element.set("name", g_name)
                # Also optionally duplicate collision geoms if requested (and this is a collision geom)
                if self.duplicate_collision_geoms and element.get("group") in {None, "0"}:
                    parent.append(self._duplicate_visual_from_collision(element))
                    # Also manually set the visual appearances to the original collision model
                    element.set("rgba", array_to_string(OBJECT_COLLISION_COLOR))
                    if element.get("material") is not None:
                        del element.attrib["material"]
        # add joint(s)
        for joint_spec in self.joint_specs:
            obj.append(new_joint(**joint_spec))
        # Lastly, add a site for this object
        template = self.get_site_attrib_template()
        template["rgba"] = "1 0 0 0"
        template["name"] = "default_site"
        obj.append(ET.Element("site", attrib=template))

        return obj

    MujocoXMLObject._get_object_subtree = _get_object_subtree


hack_robosuite()
 
class CustomObjects(MujocoXMLObject):
    def __init__(self, custom_path, name, obj_name, joints=[dict(type="free", damping="0.0005")]):
        # 确保custom_path是一个绝对路径
        assert (os.path.isabs(custom_path)), "Custom path must be an absolute path"
        # 确保custom_path指向一个xml文件
        assert (custom_path.endswith("_with_hand.xml")), "Custom path must be an xml file"
        super().__init__(
            custom_path,
            name=name,
            joints=joints,
            obj_type="all",
            duplicate_collision_geoms=False,
        )
        
        self.category_name = "_".join(
            re.sub(r"([A-Z])", r" \1", self.__class__.__name__).split()
        ).lower()
        self.object_properties = {"vis_site_names": {}}


# --- appended class Banana1WithHand ---
@register_object
class Banana1WithHand(CustomObjects):
    def __init__(self,
                 name='banana_1_with_hand',
                 obj_name='banana_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/banana/wmglhc/usd/MJCF/wmglhc_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Banana2WithHand ---
@register_object
class Banana2WithHand(CustomObjects):
    def __init__(self,
                 name='banana_2_with_hand',
                 obj_name='banana_2_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/banana/znakxm/usd/MJCF/znakxm_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Banana4WithHand ---
@register_object
class Banana4WithHand(CustomObjects):
    def __init__(self,
                 name='banana_4_with_hand',
                 obj_name='banana_4_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/banana/verqwv/usd/MJCF/verqwv_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Cork1WithHand ---
@register_object
class Cork1WithHand(CustomObjects):
    def __init__(self,
                 name='cork_1_with_hand',
                 obj_name='cork_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/cork/lseuwf/usd/MJCF/lseuwf_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Cork2WithHand ---
@register_object
class Cork2WithHand(CustomObjects):
    def __init__(self,
                 name='cork_2_with_hand',
                 obj_name='cork_2_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/cork/ncxgpe/usd/MJCF/ncxgpe_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Cork3WithHand ---
@register_object
class Cork3WithHand(CustomObjects):
    def __init__(self,
                 name='cork_3_with_hand',
                 obj_name='cork_3_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/cork/uyceta/usd/MJCF/uyceta_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BrusselsSprouts1WithHand ---
@register_object
class BrusselsSprouts1WithHand(CustomObjects):
    def __init__(self,
                 name='brussels_sprouts_1_with_hand',
                 obj_name='brussels_sprouts_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/brussels_sprouts/vdamtq/usd/MJCF/vdamtq_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BrusselsSprouts2WithHand ---
@register_object
class BrusselsSprouts2WithHand(CustomObjects):
    def __init__(self,
                 name='brussels_sprouts_2_with_hand',
                 obj_name='brussels_sprouts_2_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/brussels_sprouts/hkwyzk/usd/MJCF/hkwyzk_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BrusselsSprouts3WithHand ---
@register_object
class BrusselsSprouts3WithHand(CustomObjects):
    def __init__(self,
                 name='brussels_sprouts_3_with_hand',
                 obj_name='brussels_sprouts_3_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/brussels_sprouts/siodbb/usd/MJCF/siodbb_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BrusselsSprouts4WithHand ---
@register_object
class BrusselsSprouts4WithHand(CustomObjects):
    def __init__(self,
                 name='brussels_sprouts_4_with_hand',
                 obj_name='brussels_sprouts_4_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/brussels_sprouts/mbkrxe/usd/MJCF/mbkrxe_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BouillonCube1WithHand ---
@register_object
class BouillonCube1WithHand(CustomObjects):
    def __init__(self,
                 name='bouillon_cube_1_with_hand',
                 obj_name='bouillon_cube_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bouillon_cube/ctzwzz/usd/MJCF/ctzwzz_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfSoySauce1WithHand ---
@register_object
class BottleOfSoySauce1WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_soy_sauce_1_with_hand',
                 obj_name='bottle_of_soy_sauce_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_soy_sauce/afxisg/usd/MJCF/afxisg_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Avocado1WithHand ---
@register_object
class Avocado1WithHand(CustomObjects):
    def __init__(self,
                 name='avocado_1_with_hand',
                 obj_name='avocado_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/avocado/arswzs/usd/MJCF/arswzs_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Beet1WithHand ---
@register_object
class Beet1WithHand(CustomObjects):
    def __init__(self,
                 name='beet_1_with_hand',
                 obj_name='beet_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/beet/wantjv/usd/MJCF/wantjv_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BlackboardEraser1WithHand ---
@register_object
class BlackboardEraser1WithHand(CustomObjects):
    def __init__(self,
                 name='blackboard_eraser_1_with_hand',
                 obj_name='blackboard_eraser_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/blackboard_eraser/oynrtw/usd/MJCF/oynrtw_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Croissant1WithHand ---
@register_object
class Croissant1WithHand(CustomObjects):
    def __init__(self,
                 name='croissant_1_with_hand',
                 obj_name='croissant_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/croissant/xxsanu/usd/MJCF/xxsanu_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Croissant2WithHand ---
# @register_object
# class Croissant2WithHand(CustomObjects):
#     def __init__(self,
#                  name='croissant_2_with_hand',
#                  obj_name='croissant_2_with_hand',
#                  ):
#         custom_path = os.path.join(
#                 str(absolute_path), f"assets/new_objects_with_hand/croissant/hnbnap/usd/MJCF/hnbnap_with_hand.xml"
#             )
#         super().__init__(
#             custom_path=custom_path,
#             name=name,
#             obj_name=obj_name,
#         )
#         self.rotation = {
#             "x": (-np.pi / 2, -np.pi / 2),
#             "y": (-np.pi, -np.pi),
#             "z": (np.pi, np.pi),
#         }
#         self.rotation_axis = None


# --- appended class CoffeeGrinder1WithHand ---
# @register_object
# class CoffeeGrinder1WithHand(CustomObjects):
#     def __init__(self,
#                  name='coffee_grinder_1_with_hand',
#                  obj_name='coffee_grinder_1_with_hand',
#                  ):
#         custom_path = os.path.join(
#                 str(absolute_path), f"assets/new_objects_with_hand/coffee_grinder/bubzvn/usd/MJCF/bubzvn_with_hand.xml"
#             )
#         super().__init__(
#             custom_path=custom_path,
#             name=name,
#             obj_name=obj_name,
#         )
#         self.rotation = {
#             "x": (-np.pi / 2, -np.pi / 2),
#             "y": (-np.pi, -np.pi),
#             "z": (np.pi, np.pi),
#         }
#         self.rotation_axis = None


# --- appended class BottleOfPesto1WithHand ---
@register_object
class BottleOfPesto1WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_pesto_1_with_hand',
                 obj_name='bottle_of_pesto_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_pesto/hyeetr/usd/MJCF/hyeetr_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfOrangeJuice2WithHand ---
@register_object
class BottleOfOrangeJuice2WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_orange_juice_2_with_hand',
                 obj_name='bottle_of_orange_juice_2_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_orange_juice/edltwh/usd/MJCF/edltwh_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfOrangeJuice3WithHand ---
@register_object
class BottleOfOrangeJuice3WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_orange_juice_3_with_hand',
                 obj_name='bottle_of_orange_juice_3_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_orange_juice/jcvqmb/usd/MJCF/jcvqmb_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfTea1WithHand ---
@register_object
class BottleOfTea1WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_tea_1_with_hand',
                 obj_name='bottle_of_tea_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_tea/iladfg/usd/MJCF/iladfg_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfTea2WithHand ---
@register_object
class BottleOfTea2WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_tea_2_with_hand',
                 obj_name='bottle_of_tea_2_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_tea/yatmrs/usd/MJCF/yatmrs_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Carton1WithHand ---
# @register_object
# class Carton1WithHand(CustomObjects):
#     def __init__(self,
#                  name='carton_1_with_hand',
#                  obj_name='carton_1_with_hand',
#                  ):
#         custom_path = os.path.join(
#                 str(absolute_path), f"assets/new_objects_with_hand/carton/causya/usd/MJCF/causya_with_hand.xml"
#             )
#         super().__init__(
#             custom_path=custom_path,
#             name=name,
#             obj_name=obj_name,
#         )
#         self.rotation = {
#             "x": (-np.pi / 2, -np.pi / 2),
#             "y": (-np.pi, -np.pi),
#             "z": (np.pi, np.pi),
#         }
#         self.rotation_axis = None


# --- appended class Carton2WithHand ---
# @register_object
# class Carton2WithHand(CustomObjects):
#     def __init__(self,
#                  name='carton_2_with_hand',
#                  obj_name='carton_2_with_hand',
#                  ):
#         custom_path = os.path.join(
#                 str(absolute_path), f"assets/new_objects_with_hand/carton/ylrxhe/usd/MJCF/ylrxhe_with_hand.xml"
#             )
#         super().__init__(
#             custom_path=custom_path,
#             name=name,
#             obj_name=obj_name,
#         )
#         self.rotation = {
#             "x": (-np.pi / 2, -np.pi / 2),
#             "y": (-np.pi, -np.pi),
#             "z": (np.pi, np.pi),
#         }
#         self.rotation_axis = None


# --- appended class Carton3WithHand ---
# @register_object
# class Carton3WithHand(CustomObjects):
#     def __init__(self,
#                  name='carton_3_with_hand',
#                  obj_name='carton_3_with_hand',
#                  ):
#         custom_path = os.path.join(
#                 str(absolute_path), f"assets/new_objects_with_hand/carton/msfzpz/usd/MJCF/msfzpz_with_hand.xml"
#             )
#         super().__init__(
#             custom_path=custom_path,
#             name=name,
#             obj_name=obj_name,
#         )
#         self.rotation = {
#             "x": (-np.pi / 2, -np.pi / 2),
#             "y": (-np.pi, -np.pi),
#             "z": (np.pi, np.pi),
#         }
#         self.rotation_axis = None


# --- appended class Carton4WithHand ---
# @register_object
# class Carton4WithHand(CustomObjects):
#     def __init__(self,
#                  name='carton_4_with_hand',
#                  obj_name='carton_4_with_hand',
#                  ):
#         custom_path = os.path.join(
#                 str(absolute_path), f"assets/new_objects_with_hand/carton/cdmmwy/usd/MJCF/cdmmwy_with_hand.xml"
#             )
#         super().__init__(
#             custom_path=custom_path,
#             name=name,
#             obj_name=obj_name,
#         )
#         self.rotation = {
#             "x": (-np.pi / 2, -np.pi / 2),
#             "y": (-np.pi, -np.pi),
#             "z": (np.pi, np.pi),
#         }
#         self.rotation_axis = None


# --- appended class Carton5WithHand ---
# @register_object
# class Carton5WithHand(CustomObjects):
#     def __init__(self,
#                  name='carton_5_with_hand',
#                  obj_name='carton_5_with_hand',
#                  ):
#         custom_path = os.path.join(
#                 str(absolute_path), f"assets/new_objects_with_hand/carton/sxlklf/usd/MJCF/sxlklf_with_hand.xml"
#             )
#         super().__init__(
#             custom_path=custom_path,
#             name=name,
#             obj_name=obj_name,
#         )
#         self.rotation = {
#             "x": (-np.pi / 2, -np.pi / 2),
#             "y": (-np.pi, -np.pi),
#             "z": (np.pi, np.pi),
#         }
#         self.rotation_axis = None


# --- appended class Carton6WithHand ---
# @register_object
# class Carton6WithHand(CustomObjects):
#     def __init__(self,
#                  name='carton_6_with_hand',
#                  obj_name='carton_6_with_hand',
#                  ):
#         custom_path = os.path.join(
#                 str(absolute_path), f"assets/new_objects_with_hand/carton/hhlmbi/usd/MJCF/hhlmbi_with_hand.xml"
#             )
#         super().__init__(
#             custom_path=custom_path,
#             name=name,
#             obj_name=obj_name,
#         )
#         self.rotation = {
#             "x": (-np.pi / 2, -np.pi / 2),
#             "y": (-np.pi, -np.pi),
#             "z": (np.pi, np.pi),
#         }
#         self.rotation_axis = None


# --- appended class Carton7WithHand ---
# @register_object
# class Carton7WithHand(CustomObjects):
#     def __init__(self,
#                  name='carton_7_with_hand',
#                  obj_name='carton_7_with_hand',
#                  ):
#         custom_path = os.path.join(
#                 str(absolute_path), f"assets/new_objects_with_hand/carton/libote/usd/MJCF/libote_with_hand.xml"
#             )
#         super().__init__(
#             custom_path=custom_path,
#             name=name,
#             obj_name=obj_name,
#         )
#         self.rotation = {
#             "x": (-np.pi / 2, -np.pi / 2),
#             "y": (-np.pi, -np.pi),
#             "z": (np.pi, np.pi),
#         }
#         self.rotation_axis = None


# --- appended class BottleOfSolvent1WithHand ---
@register_object
class BottleOfSolvent1WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_solvent_1_with_hand',
                 obj_name='bottle_of_solvent_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_solvent/gsafbo/usd/MJCF/gsafbo_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class HalfGingerRoot1WithHand ---
@register_object
class HalfGingerRoot1WithHand(CustomObjects):
    def __init__(self,
                 name='half_ginger_root_1_with_hand',
                 obj_name='half_ginger_root_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/half_ginger_root/lqubed/usd/MJCF/lqubed_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class HalfGingerRoot2WithHand ---
# @register_object
# class HalfGingerRoot2WithHand(CustomObjects):
#     def __init__(self,
#                  name='half_ginger_root_2_with_hand',
#                  obj_name='half_ginger_root_2_with_hand',
#                  ):
#         custom_path = os.path.join(
#                 str(absolute_path), f"assets/new_objects_with_hand/half_ginger_root/owzxwo/usd/MJCF/owzxwo_with_hand.xml"
#             )
#         super().__init__(
#             custom_path=custom_path,
#             name=name,
#             obj_name=obj_name,
#         )
#         self.rotation = {
#             "x": (-np.pi / 2, -np.pi / 2),
#             "y": (-np.pi, -np.pi),
#             "z": (np.pi, np.pi),
#         }
#         self.rotation_axis = None


# --- appended class HalfSushi1WithHand ---
@register_object
class HalfSushi1WithHand(CustomObjects):
    def __init__(self,
                 name='half_sushi_1_with_hand',
                 obj_name='half_sushi_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/half_sushi/kbvcub/usd/MJCF/kbvcub_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class HalfSushi2WithHand ---
@register_object
class HalfSushi2WithHand(CustomObjects):
    def __init__(self,
                 name='half_sushi_2_with_hand',
                 obj_name='half_sushi_2_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/half_sushi/yeczqn/usd/MJCF/yeczqn_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfCologne1WithHand ---
@register_object
class BottleOfCologne1WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_cologne_1_with_hand',
                 obj_name='bottle_of_cologne_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_cologne/lyipur/usd/MJCF/lyipur_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfMolasses1WithHand ---
@register_object
class BottleOfMolasses1WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_molasses_1_with_hand',
                 obj_name='bottle_of_molasses_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_molasses/jvsjop/usd/MJCF/jvsjop_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfConditioner1WithHand ---
@register_object
class BottleOfConditioner1WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_conditioner_1_with_hand',
                 obj_name='bottle_of_conditioner_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_conditioner/teafxb/usd/MJCF/teafxb_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Eyeglasses1WithHand ---
@register_object
class Eyeglasses1WithHand(CustomObjects):
    def __init__(self,
                 name='eyeglasses_1_with_hand',
                 obj_name='eyeglasses_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/eyeglasses/gphhuu/usd/MJCF/gphhuu_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


@register_object
class PlateWithHand(CustomObjects):
    def __init__(self,
                 name='plate_with_hand',
                 obj_name='plate_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/plate/plate_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            # "x": (-np.pi / 2, -np.pi / 2),
            "x": (0, 0),
            "y": (0, 0),
            "z": (0, 0),
            # "y": (-np.pi, -np.pi),
            # "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


@register_object
class AkitaBlackBowlWithHand(CustomObjects):
    def __init__(self,
                 name='akita_black_bowl_with_hand',
                 obj_name='akita_black_bowl_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/akita_black_bowl/akita_black_bowl_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            # "x": (-np.pi / 2, -np.pi / 2),
            # "y": (-np.pi, -np.pi),
            # "z": (np.pi, np.pi),
            "x": (0, 0),
            "y": (0, 0),
            "z": (0, 0),
        }
        self.rotation_axis = None


# --- appended class Eyeglasses2WithHand ---
@register_object
class Eyeglasses2WithHand(CustomObjects):
    def __init__(self,
                 name='eyeglasses_2_with_hand',
                 obj_name='eyeglasses_2_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/eyeglasses/ujauoy/usd/MJCF/ujauoy_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfGingerBeer1WithHand ---
@register_object
class BottleOfGingerBeer1WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_ginger_beer_1_with_hand',
                 obj_name='bottle_of_ginger_beer_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_ginger_beer/zkocwb/usd/MJCF/zkocwb_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfShampoo1WithHand ---
@register_object
class BottleOfShampoo1WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_shampoo_1_with_hand',
                 obj_name='bottle_of_shampoo_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_shampoo/stjjjm/usd/MJCF/stjjjm_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfShampoo3WithHand ---
@register_object
class BottleOfShampoo3WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_shampoo_3_with_hand',
                 obj_name='bottle_of_shampoo_3_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_shampoo/dvrzmy/usd/MJCF/dvrzmy_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfShampoo4WithHand ---
@register_object
class BottleOfShampoo4WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_shampoo_4_with_hand',
                 obj_name='bottle_of_shampoo_4_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_shampoo/hlkpwd/usd/MJCF/hlkpwd_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfMustardSeeds1WithHand ---
@register_object
class BottleOfMustardSeeds1WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_mustard_seeds_1_with_hand',
                 obj_name='bottle_of_mustard_seeds_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_mustard_seeds/grryaf/usd/MJCF/grryaf_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None
        

# --- appended class HalfHeadCabbage2WithHand ---
@register_object
class HalfHeadCabbage2WithHand(CustomObjects):
    def __init__(self,
                 name='half_head_cabbage_2_with_hand',
                 obj_name='half_head_cabbage_2_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/half_head_cabbage/wpebpb/usd/MJCF/wpebpb_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Folder3WithHand ---
# @register_object
# class Folder3WithHand(CustomObjects):
#     def __init__(self,
#                  name='folder_3_with_hand',
#                  obj_name='folder_3_with_hand',
#                  ):
#         custom_path = os.path.join(
#                 str(absolute_path), f"assets/new_objects_with_hand/folder/lufqkq/usd/MJCF/lufqkq_with_hand.xml"
#             )
#         super().__init__(
#             custom_path=custom_path,
#             name=name,
#             obj_name=obj_name,
#         )
#         self.rotation = {
#             "x": (-np.pi / 2, -np.pi / 2),
#             "y": (-np.pi, -np.pi),
#             "z": (np.pi, np.pi),
#         }
#         self.rotation_axis = None


# --- appended class Folder4WithHand ---
# @register_object
# class Folder4WithHand(CustomObjects):
#     def __init__(self,
#                  name='folder_4_with_hand',
#                  obj_name='folder_4_with_hand',
#                  ):
#         custom_path = os.path.join(
#                 str(absolute_path), f"assets/new_objects_with_hand/folder/lktggf/usd/MJCF/lktggf_with_hand.xml"
#             )
#         super().__init__(
#             custom_path=custom_path,
#             name=name,
#             obj_name=obj_name,
#         )
#         self.rotation = {
#             "x": (-np.pi / 2, -np.pi / 2),
#             "y": (-np.pi, -np.pi),
#             "z": (np.pi, np.pi),
#         }
#         self.rotation_axis = None


# --- appended class Folder5WithHand ---
# @register_object
# class Folder5WithHand(CustomObjects):
#     def __init__(self,
#                  name='folder_5_with_hand',
#                  obj_name='folder_5_with_hand',
#                  ):
#         custom_path = os.path.join(
#                 str(absolute_path), f"assets/new_objects_with_hand/folder/guhatz/usd/MJCF/guhatz_with_hand.xml"
#             )
#         super().__init__(
#             custom_path=custom_path,
#             name=name,
#             obj_name=obj_name,
#         )
#         self.rotation = {
#             "x": (-np.pi / 2, -np.pi / 2),
#             "y": (-np.pi, -np.pi),
#             "z": (np.pi, np.pi),
#         }
#         self.rotation_axis = None


# --- appended class Folder6WithHand ---
# @register_object
# class Folder6WithHand(CustomObjects):
#     def __init__(self,
#                  name='folder_6_with_hand',
#                  obj_name='folder_6_with_hand',
#                  ):
#         custom_path = os.path.join(
#                 str(absolute_path), f"assets/new_objects_with_hand/folder/wauyns/usd/MJCF/wauyns_with_hand.xml"
#             )
#         super().__init__(
#             custom_path=custom_path,
#             name=name,
#             obj_name=obj_name,
#         )
#         self.rotation = {
#             "x": (-np.pi / 2, -np.pi / 2),
#             "y": (-np.pi, -np.pi),
#             "z": (np.pi, np.pi),
#         }
#         self.rotation_axis = None


# --- appended class Folder7WithHand ---
# @register_object
# class Folder7WithHand(CustomObjects):
#     def __init__(self,
#                  name='folder_7_with_hand',
#                  obj_name='folder_7_with_hand',
#                  ):
#         custom_path = os.path.join(
#                 str(absolute_path), f"assets/new_objects_with_hand/folder/inkwmw/usd/MJCF/inkwmw_with_hand.xml"
#             )
#         super().__init__(
#             custom_path=custom_path,
#             name=name,
#             obj_name=obj_name,
#         )
#         self.rotation = {
#             "x": (-np.pi / 2, -np.pi / 2),
#             "y": (-np.pi, -np.pi),
#             "z": (np.pi, np.pi),
#         }
#         self.rotation_axis = None


# --- appended class BoxOfCoconutMilk1WithHand ---
@register_object
class BoxOfCoconutMilk1WithHand(CustomObjects):
    def __init__(self,
                 name='box_of_coconut_milk_1_with_hand',
                 obj_name='box_of_coconut_milk_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/box_of_coconut_milk/dagbyl/usd/MJCF/dagbyl_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BellPepper1WithHand ---
@register_object
class BellPepper1WithHand(CustomObjects):
    def __init__(self,
                 name='bell_pepper_1_with_hand',
                 obj_name='bell_pepper_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bell_pepper/uqcenz/usd/MJCF/uqcenz_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BellPepper2WithHand ---
@register_object
class BellPepper2WithHand(CustomObjects):
    def __init__(self,
                 name='bell_pepper_2_with_hand',
                 obj_name='bell_pepper_2_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bell_pepper/wszvwc/usd/MJCF/wszvwc_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BellPepper3WithHand ---
@register_object
class BellPepper3WithHand(CustomObjects):
    def __init__(self,
                 name='bell_pepper_3_with_hand',
                 obj_name='bell_pepper_3_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bell_pepper/ggurxn/usd/MJCF/ggurxn_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BellPepper4WithHand ---
@register_object
class BellPepper4WithHand(CustomObjects):
    def __init__(self,
                 name='bell_pepper_4_with_hand',
                 obj_name='bell_pepper_4_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bell_pepper/ihctxa/usd/MJCF/ihctxa_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BellPepper5WithHand ---
@register_object
class BellPepper5WithHand(CustomObjects):
    def __init__(self,
                 name='bell_pepper_5_with_hand',
                 obj_name='bell_pepper_5_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bell_pepper/ukkycp/usd/MJCF/ukkycp_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Apricot1WithHand ---
@register_object
class Apricot1WithHand(CustomObjects):
    def __init__(self,
                 name='apricot_1_with_hand',
                 obj_name='apricot_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/apricot/qmwmwm/usd/MJCF/qmwmwm_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class HalfVidaliaOnion1WithHand ---
# @register_object
# class HalfVidaliaOnion1WithHand(CustomObjects):
#     def __init__(self,
#                  name='half_vidalia_onion_1_with_hand',
#                  obj_name='half_vidalia_onion_1_with_hand',
#                  ):
#         custom_path = os.path.join(
#                 str(absolute_path), f"assets/new_objects_with_hand/half_vidalia_onion/yxwjgn/usd/MJCF/yxwjgn_with_hand.xml"
#             )
#         super().__init__(
#             custom_path=custom_path,
#             name=name,
#             obj_name=obj_name,
#         )
#         self.rotation = {
#             "x": (-np.pi / 2, -np.pi / 2),
#             "y": (-np.pi, -np.pi),
#             "z": (np.pi, np.pi),
#         }
#         self.rotation_axis = None


# --- appended class HalfVidaliaOnion2WithHand ---
# @register_object
# class HalfVidaliaOnion2WithHand(CustomObjects):
#     def __init__(self,
#                  name='half_vidalia_onion_2_with_hand',
#                  obj_name='half_vidalia_onion_2_with_hand',
#                  ):
#         custom_path = os.path.join(
#                 str(absolute_path), f"assets/new_objects_with_hand/half_vidalia_onion/tnmqrt/usd/MJCF/tnmqrt_with_hand.xml"
#             )
#         super().__init__(
#             custom_path=custom_path,
#             name=name,
#             obj_name=obj_name,
#         )
#         self.rotation = {
#             "x": (-np.pi / 2, -np.pi / 2),
#             "y": (-np.pi, -np.pi),
#             "z": (np.pi, np.pi),
#         }
#         self.rotation_axis = None


# --- appended class HalfRadish1WithHand ---
@register_object
class HalfRadish1WithHand(CustomObjects):
    def __init__(self,
                 name='half_radish_1_with_hand',
                 obj_name='half_radish_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/half_radish/kyujnh/usd/MJCF/kyujnh_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class DentalFloss1WithHand ---
@register_object
class DentalFloss1WithHand(CustomObjects):
    def __init__(self,
                 name='dental_floss_1_with_hand',
                 obj_name='dental_floss_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/dental_floss/aokqke/usd/MJCF/aokqke_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class HalfCheddar1WithHand ---
@register_object
class HalfCheddar1WithHand(CustomObjects):
    def __init__(self,
                 name='half_cheddar_1_with_hand',
                 obj_name='half_cheddar_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/half_cheddar/zkwspo/usd/MJCF/zkwspo_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class HalfCheddar2WithHand ---
@register_object
class HalfCheddar2WithHand(CustomObjects):
    def __init__(self,
                 name='half_cheddar_2_with_hand',
                 obj_name='half_cheddar_2_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/half_cheddar/cortmw/usd/MJCF/cortmw_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfMustard1WithHand ---
@register_object
class BottleOfMustard1WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_mustard_1_with_hand',
                 obj_name='bottle_of_mustard_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_mustard/qbbqat/usd/MJCF/qbbqat_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfMustard2WithHand ---
@register_object
class BottleOfMustard2WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_mustard_2_with_hand',
                 obj_name='bottle_of_mustard_2_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_mustard/sjasxe/usd/MJCF/sjasxe_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BoxOfTissues1WithHand ---
@register_object
class BoxOfTissues1WithHand(CustomObjects):
    def __init__(self,
                 name='box_of_tissues_1_with_hand',
                 obj_name='box_of_tissues_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/box_of_tissues/ntbrtz/usd/MJCF/ntbrtz_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BoxOfTissues3WithHand ---
@register_object
class BoxOfTissues3WithHand(CustomObjects):
    def __init__(self,
                 name='box_of_tissues_3_with_hand',
                 obj_name='box_of_tissues_3_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/box_of_tissues/uglbjc/usd/MJCF/uglbjc_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BoxOfTissues4WithHand ---
@register_object
class BoxOfTissues4WithHand(CustomObjects):
    def __init__(self,
                 name='box_of_tissues_4_with_hand',
                 obj_name='box_of_tissues_4_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/box_of_tissues/zutrxn/usd/MJCF/zutrxn_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BobbyPin1WithHand ---
# @register_object
# class BobbyPin1WithHand(CustomObjects):
#     def __init__(self,
#                  name='bobby_pin_1_with_hand',
#                  obj_name='bobby_pin_1_with_hand',
#                  ):
#         custom_path = os.path.join(
#                 str(absolute_path), f"assets/new_objects_with_hand/bobby_pin/zphpcz/usd/MJCF/zphpcz_with_hand.xml"
#             )
#         super().__init__(
#             custom_path=custom_path,
#             name=name,
#             obj_name=obj_name,
#         )
#         self.rotation = {
#             "x": (-np.pi / 2, -np.pi / 2),
#             "y": (-np.pi, -np.pi),
#             "z": (np.pi, np.pi),
#         }
#         self.rotation_axis = None


# --- appended class GingerRoot1WithHand ---
@register_object
class GingerRoot1WithHand(CustomObjects):
    def __init__(self,
                 name='ginger_root_1_with_hand',
                 obj_name='ginger_root_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/ginger_root/izvukv/usd/MJCF/izvukv_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class GingerRoot2WithHand ---
@register_object
class GingerRoot2WithHand(CustomObjects):
    def __init__(self,
                 name='ginger_root_2_with_hand',
                 obj_name='ginger_root_2_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/ginger_root/wqcasl/usd/MJCF/wqcasl_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BoxOfBarley1WithHand ---
@register_object
class BoxOfBarley1WithHand(CustomObjects):
    def __init__(self,
                 name='box_of_barley_1_with_hand',
                 obj_name='box_of_barley_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/box_of_barley/lxpwnw/usd/MJCF/lxpwnw_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfBugRepellent1WithHand ---
@register_object
class BottleOfBugRepellent1WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_bug_repellent_1_with_hand',
                 obj_name='bottle_of_bug_repellent_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_bug_repellent/qqztry/usd/MJCF/qqztry_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Broccoli1WithHand ---
@register_object
class Broccoli1WithHand(CustomObjects):
    def __init__(self,
                 name='broccoli_1_with_hand',
                 obj_name='broccoli_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/broccoli/wsxavx/usd/MJCF/wsxavx_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class HalfBananaBread1WithHand ---
# @register_object
# class HalfBananaBread1WithHand(CustomObjects):
#     def __init__(self,
#                  name='half_banana_bread_1_with_hand',
#                  obj_name='half_banana_bread_1_with_hand',
#                  ):
#         custom_path = os.path.join(
#                 str(absolute_path), f"assets/new_objects_with_hand/half_banana_bread/sooaaz/usd/MJCF/sooaaz_with_hand.xml"
#             )
#         super().__init__(
#             custom_path=custom_path,
#             name=name,
#             obj_name=obj_name,
#         )
#         self.rotation = {
#             "x": (-np.pi / 2, -np.pi / 2),
#             "y": (-np.pi, -np.pi),
#             "z": (np.pi, np.pi),
#         }
#         self.rotation_axis = None


# --- appended class HalfBananaBread2WithHand ---
@register_object
class HalfBananaBread2WithHand(CustomObjects):
    def __init__(self,
                 name='half_banana_bread_2_with_hand',
                 obj_name='half_banana_bread_2_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/half_banana_bread/myxyfa/usd/MJCF/myxyfa_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfPizzaSauce1WithHand ---
@register_object
class BottleOfPizzaSauce1WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_pizza_sauce_1_with_hand',
                 obj_name='bottle_of_pizza_sauce_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_pizza_sauce/clttao/usd/MJCF/clttao_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class GreenOnion1WithHand ---
@register_object
class GreenOnion1WithHand(CustomObjects):
    def __init__(self,
                 name='green_onion_1_with_hand',
                 obj_name='green_onion_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/green_onion/ljynzg/usd/MJCF/ljynzg_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Broccolini1WithHand ---
@register_object
class Broccolini1WithHand(CustomObjects):
    def __init__(self,
                 name='broccolini_1_with_hand',
                 obj_name='broccolini_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/broccolini/rlsytp/usd/MJCF/rlsytp_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class AlarmClock1WithHand ---
@register_object
class AlarmClock1WithHand(CustomObjects):
    def __init__(self,
                 name='alarm_clock_1_with_hand',
                 obj_name='alarm_clock_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/alarm_clock/trwyaq/usd/MJCF/trwyaq_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class AlarmClock3WithHand ---
@register_object
class AlarmClock3WithHand(CustomObjects):
    def __init__(self,
                 name='alarm_clock_3_with_hand',
                 obj_name='alarm_clock_3_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/alarm_clock/vqwovi/usd/MJCF/vqwovi_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfHotSauce1WithHand ---
@register_object
class BottleOfHotSauce1WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_hot_sauce_1_with_hand',
                 obj_name='bottle_of_hot_sauce_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_hot_sauce/zqhkzh/usd/MJCF/zqhkzh_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Corkscrew1WithHand ---
# @register_object
# class Corkscrew1WithHand(CustomObjects):
#     def __init__(self,
#                  name='corkscrew_1_with_hand',
#                  obj_name='corkscrew_1_with_hand',
#                  ):
#         custom_path = os.path.join(
#                 str(absolute_path), f"assets/new_objects_with_hand/corkscrew/gqocna/usd/MJCF/gqocna_with_hand.xml"
#             )
#         super().__init__(
#             custom_path=custom_path,
#             name=name,
#             obj_name=obj_name,
#         )
#         self.rotation = {
#             "x": (-np.pi / 2, -np.pi / 2),
#             "y": (-np.pi, -np.pi),
#             "z": (np.pi, np.pi),
#         }
#         self.rotation_axis = None


# --- appended class CanOfBeans1WithHand ---
@register_object
class CanOfBeans1WithHand(CustomObjects):
    def __init__(self,
                 name='can_of_beans_1_with_hand',
                 obj_name='can_of_beans_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/can_of_beans/ojqgjz/usd/MJCF/ojqgjz_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class CanOfBeans2WithHand ---
@register_object
class CanOfBeans2WithHand(CustomObjects):
    def __init__(self,
                 name='can_of_beans_2_with_hand',
                 obj_name='can_of_beans_2_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/can_of_beans/kclbuu/usd/MJCF/kclbuu_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Apple1WithHand ---
@register_object
class Apple1WithHand(CustomObjects):
    def __init__(self,
                 name='apple_1_with_hand',
                 obj_name='apple_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/apple/netbsb/usd/MJCF/netbsb_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Apple2WithHand ---
@register_object
class Apple2WithHand(CustomObjects):
    def __init__(self,
                 name='apple_2_with_hand',
                 obj_name='apple_2_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/apple/zutnsf/usd/MJCF/zutnsf_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Apple3WithHand ---
@register_object
class Apple3WithHand(CustomObjects):
    def __init__(self,
                 name='apple_3_with_hand',
                 obj_name='apple_3_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/apple/dfgurb/usd/MJCF/dfgurb_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Apple4WithHand ---
@register_object
class Apple4WithHand(CustomObjects):
    def __init__(self,
                 name='apple_4_with_hand',
                 obj_name='apple_4_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/apple/rizrsp/usd/MJCF/rizrsp_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Apple5WithHand ---
@register_object
class Apple5WithHand(CustomObjects):
    def __init__(self,
                 name='apple_5_with_hand',
                 obj_name='apple_5_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/apple/zlxfxt/usd/MJCF/zlxfxt_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Apple6WithHand ---
@register_object
class Apple6WithHand(CustomObjects):
    def __init__(self,
                 name='apple_6_with_hand',
                 obj_name='apple_6_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/apple/qrqzvs/usd/MJCF/qrqzvs_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Apple7WithHand ---
@register_object
class Apple7WithHand(CustomObjects):
    def __init__(self,
                 name='apple_7_with_hand',
                 obj_name='apple_7_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/apple/agveuv/usd/MJCF/agveuv_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Apple8WithHand ---
@register_object
class Apple8WithHand(CustomObjects):
    def __init__(self,
                 name='apple_8_with_hand',
                 obj_name='apple_8_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/apple/bwteqh/usd/MJCF/bwteqh_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Apple9WithHand ---
@register_object
class Apple9WithHand(CustomObjects):
    def __init__(self,
                 name='apple_9_with_hand',
                 obj_name='apple_9_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/apple/ymhxqk/usd/MJCF/ymhxqk_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Apple10WithHand ---
@register_object
class Apple10WithHand(CustomObjects):
    def __init__(self,
                 name='apple_10_with_hand',
                 obj_name='apple_10_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/apple/obixxh/usd/MJCF/obixxh_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Apple11WithHand ---
@register_object
class Apple11WithHand(CustomObjects):
    def __init__(self,
                 name='apple_11_with_hand',
                 obj_name='apple_11_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/apple/yyuiva/usd/MJCF/yyuiva_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Apple12WithHand ---
@register_object
class Apple12WithHand(CustomObjects):
    def __init__(self,
                 name='apple_12_with_hand',
                 obj_name='apple_12_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/apple/omzprq/usd/MJCF/omzprq_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Apple13WithHand ---
@register_object
class Apple13WithHand(CustomObjects):
    def __init__(self,
                 name='apple_13_with_hand',
                 obj_name='apple_13_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/apple/hwrflj/usd/MJCF/hwrflj_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BeefsteakTomato1WithHand ---
@register_object
class BeefsteakTomato1WithHand(CustomObjects):
    def __init__(self,
                 name='beefsteak_tomato_1_with_hand',
                 obj_name='beefsteak_tomato_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/beefsteak_tomato/pnrdxh/usd/MJCF/pnrdxh_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BeefsteakTomato2WithHand ---
@register_object
class BeefsteakTomato2WithHand(CustomObjects):
    def __init__(self,
                 name='beefsteak_tomato_2_with_hand',
                 obj_name='beefsteak_tomato_2_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/beefsteak_tomato/eevvzv/usd/MJCF/eevvzv_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BeefsteakTomato3WithHand ---
@register_object
class BeefsteakTomato3WithHand(CustomObjects):
    def __init__(self,
                 name='beefsteak_tomato_3_with_hand',
                 obj_name='beefsteak_tomato_3_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/beefsteak_tomato/ogpans/usd/MJCF/ogpans_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BeefsteakTomato4WithHand ---
@register_object
class BeefsteakTomato4WithHand(CustomObjects):
    def __init__(self,
                 name='beefsteak_tomato_4_with_hand',
                 obj_name='beefsteak_tomato_4_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/beefsteak_tomato/altlfz/usd/MJCF/altlfz_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfFennel1WithHand ---
@register_object
class BottleOfFennel1WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_fennel_1_with_hand',
                 obj_name='bottle_of_fennel_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_fennel/ihlkfu/usd/MJCF/ihlkfu_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BarSoap2WithHand ---
@register_object
class BarSoap2WithHand(CustomObjects):
    def __init__(self,
                 name='bar_soap_2_with_hand',
                 obj_name='bar_soap_2_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bar_soap/utgixp/usd/MJCF/utgixp_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BarSoap3WithHand ---
@register_object
class BarSoap3WithHand(CustomObjects):
    def __init__(self,
                 name='bar_soap_3_with_hand',
                 obj_name='bar_soap_3_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bar_soap/ozifwa/usd/MJCF/ozifwa_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BarSoap4WithHand ---
@register_object
class BarSoap4WithHand(CustomObjects):
    def __init__(self,
                 name='bar_soap_4_with_hand',
                 obj_name='bar_soap_4_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bar_soap/feqemg/usd/MJCF/feqemg_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BarSoap5WithHand ---
@register_object
class BarSoap5WithHand(CustomObjects):
    def __init__(self,
                 name='bar_soap_5_with_hand',
                 obj_name='bar_soap_5_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bar_soap/lyigsj/usd/MJCF/lyigsj_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfCarrotJuice1WithHand ---
@register_object
class BottleOfCarrotJuice1WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_carrot_juice_1_with_hand',
                 obj_name='bottle_of_carrot_juice_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_carrot_juice/jkuhio/usd/MJCF/jkuhio_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Hairbrush1WithHand ---
@register_object
class Hairbrush1WithHand(CustomObjects):
    def __init__(self,
                 name='hairbrush_1_with_hand',
                 obj_name='hairbrush_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/hairbrush/bdylnb/usd/MJCF/bdylnb_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfPumpkinPieSpice1WithHand ---
@register_object
class BottleOfPumpkinPieSpice1WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_pumpkin_pie_spice_1_with_hand',
                 obj_name='bottle_of_pumpkin_pie_spice_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_pumpkin_pie_spice/oindrv/usd/MJCF/oindrv_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class HalfHotdogBun1WithHand ---
@register_object
class HalfHotdogBun1WithHand(CustomObjects):
    def __init__(self,
                 name='half_hotdog_bun_1_with_hand',
                 obj_name='half_hotdog_bun_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/half_hotdog_bun/znjcve/usd/MJCF/znjcve_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class HalfZucchini3WithHand ---
@register_object
class HalfZucchini3WithHand(CustomObjects):
    def __init__(self,
                 name='half_zucchini_3_with_hand',
                 obj_name='half_zucchini_3_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/half_zucchini/uzezze/usd/MJCF/uzezze_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Carrot1WithHand ---
@register_object
class Carrot1WithHand(CustomObjects):
    def __init__(self,
                 name='carrot_1_with_hand',
                 obj_name='carrot_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/carrot/nktmff/usd/MJCF/nktmff_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Carrot2WithHand ---
@register_object
class Carrot2WithHand(CustomObjects):
    def __init__(self,
                 name='carrot_2_with_hand',
                 obj_name='carrot_2_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/carrot/qhmmmx/usd/MJCF/qhmmmx_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Carrot3WithHand ---
@register_object
class Carrot3WithHand(CustomObjects):
    def __init__(self,
                 name='carrot_3_with_hand',
                 obj_name='carrot_3_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/carrot/aucrah/usd/MJCF/aucrah_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BagOfBreadcrumbs1WithHand ---
@register_object
class BagOfBreadcrumbs1WithHand(CustomObjects):
    def __init__(self,
                 name='bag_of_breadcrumbs_1_with_hand',
                 obj_name='bag_of_breadcrumbs_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bag_of_breadcrumbs/nvhvxe/usd/MJCF/nvhvxe_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class CopperPot1WithHand ---
# @register_object
# class CopperPot1WithHand(CustomObjects):
#     def __init__(self,
#                  name='copper_pot_1_with_hand',
#                  obj_name='copper_pot_1_with_hand',
#                  ):
#         custom_path = os.path.join(
#                 str(absolute_path), f"assets/new_objects_with_hand/copper_pot/gqemcq/usd/MJCF/gqemcq_with_hand.xml"
#             )
#         super().__init__(
#             custom_path=custom_path,
#             name=name,
#             obj_name=obj_name,
#         )
#         self.rotation = {
#             "x": (-np.pi / 2, -np.pi / 2),
#             "y": (-np.pi, -np.pi),
#             "z": (np.pi, np.pi),
#         }
#         self.rotation_axis = None


# --- appended class CanOfBayLeaves1WithHand ---
# @register_object
# class CanOfBayLeaves1WithHand(CustomObjects):
#     def __init__(self,
#                  name='can_of_bay_leaves_1_with_hand',
#                  obj_name='can_of_bay_leaves_1_with_hand',
#                  ):
#         custom_path = os.path.join(
#                 str(absolute_path), f"assets/new_objects_with_hand/can_of_bay_leaves/ppwvjf/usd/MJCF/ppwvjf_with_hand.xml"
#             )
#         super().__init__(
#             custom_path=custom_path,
#             name=name,
#             obj_name=obj_name,
#         )
#         self.rotation = {
#             "x": (-np.pi / 2, -np.pi / 2),
#             "y": (-np.pi, -np.pi),
#             "z": (np.pi, np.pi),
#         }
#         self.rotation_axis = None


# --- appended class BottleOfSage1WithHand ---
@register_object
class BottleOfSage1WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_sage_1_with_hand',
                 obj_name='bottle_of_sage_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_sage/bterim/usd/MJCF/bterim_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfSriracha1WithHand ---
@register_object
class BottleOfSriracha1WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_sriracha_1_with_hand',
                 obj_name='bottle_of_sriracha_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_sriracha/gnklax/usd/MJCF/gnklax_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfFruitPunch2WithHand ---
@register_object
class BottleOfFruitPunch2WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_fruit_punch_2_with_hand',
                 obj_name='bottle_of_fruit_punch_2_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_fruit_punch/azcigi/usd/MJCF/azcigi_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Crayon1WithHand ---
@register_object
class Crayon1WithHand(CustomObjects):
    def __init__(self,
                 name='crayon_1_with_hand',
                 obj_name='crayon_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/crayon/vdkdur/usd/MJCF/vdkdur_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Crayon2WithHand ---
@register_object
class Crayon2WithHand(CustomObjects):
    def __init__(self,
                 name='crayon_2_with_hand',
                 obj_name='crayon_2_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/crayon/gfgsev/usd/MJCF/gfgsev_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Crayon3WithHand ---
@register_object
class Crayon3WithHand(CustomObjects):
    def __init__(self,
                 name='crayon_3_with_hand',
                 obj_name='crayon_3_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/crayon/jfqetz/usd/MJCF/jfqetz_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Crayon4WithHand ---
# @register_object
# class Crayon4WithHand(CustomObjects):
#     def __init__(self,
#                  name='crayon_4_with_hand',
#                  obj_name='crayon_4_with_hand',
#                  ):
#         custom_path = os.path.join(
#                 str(absolute_path), f"assets/new_objects_with_hand/crayon/uwmrwr/usd/MJCF/uwmrwr_with_hand.xml"
#             )
#         super().__init__(
#             custom_path=custom_path,
#             name=name,
#             obj_name=obj_name,
#         )
#         self.rotation = {
#             "x": (-np.pi / 2, -np.pi / 2),
#             "y": (-np.pi, -np.pi),
#             "z": (np.pi, np.pi),
#         }
#         self.rotation_axis = None


# --- appended class Crayon5WithHand ---
# @register_object
# class Crayon5WithHand(CustomObjects):
#     def __init__(self,
#                  name='crayon_5_with_hand',
#                  obj_name='crayon_5_with_hand',
#                  ):
#         custom_path = os.path.join(
#                 str(absolute_path), f"assets/new_objects_with_hand/crayon/uqlfwf/usd/MJCF/uqlfwf_with_hand.xml"
#             )
#         super().__init__(
#             custom_path=custom_path,
#             name=name,
#             obj_name=obj_name,
#         )
#         self.rotation = {
#             "x": (-np.pi / 2, -np.pi / 2),
#             "y": (-np.pi, -np.pi),
#             "z": (np.pi, np.pi),
#         }
#         self.rotation_axis = None


# --- appended class Crayon6WithHand ---
@register_object
class Crayon6WithHand(CustomObjects):
    def __init__(self,
                 name='crayon_6_with_hand',
                 obj_name='crayon_6_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/crayon/jqodxx/usd/MJCF/jqodxx_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Crayon7WithHand ---
@register_object
class Crayon7WithHand(CustomObjects):
    def __init__(self,
                 name='crayon_7_with_hand',
                 obj_name='crayon_7_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/crayon/coapeh/usd/MJCF/coapeh_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Crayon8WithHand ---
@register_object
class Crayon8WithHand(CustomObjects):
    def __init__(self,
                 name='crayon_8_with_hand',
                 obj_name='crayon_8_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/crayon/diiinz/usd/MJCF/diiinz_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Crayon9WithHand ---
@register_object
class Crayon9WithHand(CustomObjects):
    def __init__(self,
                 name='crayon_9_with_hand',
                 obj_name='crayon_9_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/crayon/csglmn/usd/MJCF/csglmn_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Crayon10WithHand ---
@register_object
class Crayon10WithHand(CustomObjects):
    def __init__(self,
                 name='crayon_10_with_hand',
                 obj_name='crayon_10_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/crayon/cvebde/usd/MJCF/cvebde_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Crayon11WithHand ---
@register_object
class Crayon11WithHand(CustomObjects):
    def __init__(self,
                 name='crayon_11_with_hand',
                 obj_name='crayon_11_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/crayon/xmysum/usd/MJCF/xmysum_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfPeanutButter1WithHand ---
@register_object
class BottleOfPeanutButter1WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_peanut_butter_1_with_hand',
                 obj_name='bottle_of_peanut_butter_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_peanut_butter/edcvwr/usd/MJCF/edcvwr_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfCoconutOil1WithHand ---
@register_object
class BottleOfCoconutOil1WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_coconut_oil_1_with_hand',
                 obj_name='bottle_of_coconut_oil_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_coconut_oil/rrwzkq/usd/MJCF/rrwzkq_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class ChocolateBiscuit1WithHand ---
@register_object
class ChocolateBiscuit1WithHand(CustomObjects):
    def __init__(self,
                 name='chocolate_biscuit_1_with_hand',
                 obj_name='chocolate_biscuit_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/chocolate_biscuit/xhmpht/usd/MJCF/xhmpht_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class ChocolateBiscuit2WithHand ---
@register_object
class ChocolateBiscuit2WithHand(CustomObjects):
    def __init__(self,
                 name='chocolate_biscuit_2_with_hand',
                 obj_name='chocolate_biscuit_2_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/chocolate_biscuit/fwnyas/usd/MJCF/fwnyas_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Dowel1WithHand ---
# @register_object
# class Dowel1WithHand(CustomObjects):
#     def __init__(self,
#                  name='dowel_1_with_hand',
#                  obj_name='dowel_1_with_hand',
#                  ):
#         custom_path = os.path.join(
#                 str(absolute_path), f"assets/new_objects_with_hand/dowel/ghnjry/usd/MJCF/ghnjry_with_hand.xml"
#             )
#         super().__init__(
#             custom_path=custom_path,
#             name=name,
#             obj_name=obj_name,
#         )
#         self.rotation = {
#             "x": (-np.pi / 2, -np.pi / 2),
#             "y": (-np.pi, -np.pi),
#             "z": (np.pi, np.pi),
#         }
#         self.rotation_axis = None


# --- appended class BottleOfOliveOil1WithHand ---
@register_object
class BottleOfOliveOil1WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_olive_oil_1_with_hand',
                 obj_name='bottle_of_olive_oil_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_olive_oil/wztvie/usd/MJCF/wztvie_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfOliveOil2WithHand ---
@register_object
class BottleOfOliveOil2WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_olive_oil_2_with_hand',
                 obj_name='bottle_of_olive_oil_2_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_olive_oil/ksxqkk/usd/MJCF/ksxqkk_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfOliveOil5WithHand ---
@register_object
class BottleOfOliveOil5WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_olive_oil_5_with_hand',
                 obj_name='bottle_of_olive_oil_5_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_olive_oil/cqycjk/usd/MJCF/cqycjk_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfOliveOil6WithHand ---
@register_object
class BottleOfOliveOil6WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_olive_oil_6_with_hand',
                 obj_name='bottle_of_olive_oil_6_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_olive_oil/luikop/usd/MJCF/luikop_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfOliveOil7WithHand ---
@register_object
class BottleOfOliveOil7WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_olive_oil_7_with_hand',
                 obj_name='bottle_of_olive_oil_7_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_olive_oil/jocrsz/usd/MJCF/jocrsz_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfAspirin1WithHand ---
@register_object
class BottleOfAspirin1WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_aspirin_1_with_hand',
                 obj_name='bottle_of_aspirin_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_aspirin/psvktc/usd/MJCF/psvktc_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Chives1WithHand ---
@register_object
class Chives1WithHand(CustomObjects):
    def __init__(self,
                 name='chives_1_with_hand',
                 obj_name='chives_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/chives/gboofh/usd/MJCF/gboofh_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Chives2WithHand ---
@register_object
class Chives2WithHand(CustomObjects):
    def __init__(self,
                 name='chives_2_with_hand',
                 obj_name='chives_2_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/chives/yifjct/usd/MJCF/yifjct_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class CupOfYogurt1WithHand ---
@register_object
class CupOfYogurt1WithHand(CustomObjects):
    def __init__(self,
                 name='cup_of_yogurt_1_with_hand',
                 obj_name='cup_of_yogurt_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/cup_of_yogurt/kihdsj/usd/MJCF/kihdsj_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class GlueStick1WithHand ---
@register_object
class GlueStick1WithHand(CustomObjects):
    def __init__(self,
                 name='glue_stick_1_with_hand',
                 obj_name='glue_stick_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/glue_stick/sqzyci/usd/MJCF/sqzyci_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class HalfSugarCookie1WithHand ---
# @register_object
# class HalfSugarCookie1WithHand(CustomObjects):
#     def __init__(self,
#                  name='half_sugar_cookie_1_with_hand',
#                  obj_name='half_sugar_cookie_1_with_hand',
#                  ):
#         custom_path = os.path.join(
#                 str(absolute_path), f"assets/new_objects_with_hand/half_sugar_cookie/hvqdow/usd/MJCF/hvqdow_with_hand.xml"
#             )
#         super().__init__(
#             custom_path=custom_path,
#             name=name,
#             obj_name=obj_name,
#         )
#         self.rotation = {
#             "x": (-np.pi / 2, -np.pi / 2),
#             "y": (-np.pi, -np.pi),
#             "z": (np.pi, np.pi),
#         }
#         self.rotation_axis = None


# --- appended class HalfSugarCookie2WithHand ---
@register_object
class HalfSugarCookie2WithHand(CustomObjects):
    def __init__(self,
                 name='half_sugar_cookie_2_with_hand',
                 obj_name='half_sugar_cookie_2_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/half_sugar_cookie/jkrbjp/usd/MJCF/jkrbjp_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfTomatoJuice1WithHand ---
@register_object
class BottleOfTomatoJuice1WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_tomato_juice_1_with_hand',
                 obj_name='bottle_of_tomato_juice_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_tomato_juice/csumos/usd/MJCF/csumos_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class HalfLime1WithHand ---
@register_object
class HalfLime1WithHand(CustomObjects):
    def __init__(self,
                 name='half_lime_1_with_hand',
                 obj_name='half_lime_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/half_lime/mxmmcp/usd/MJCF/mxmmcp_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfAlfredoSauce1WithHand ---
@register_object
class BottleOfAlfredoSauce1WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_alfredo_sauce_1_with_hand',
                 obj_name='bottle_of_alfredo_sauce_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_alfredo_sauce/xwzqjr/usd/MJCF/xwzqjr_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Bell1WithHand ---
@register_object
class Bell1WithHand(CustomObjects):
    def __init__(self,
                 name='bell_1_with_hand',
                 obj_name='bell_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bell/oshurh/usd/MJCF/oshurh_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Chestnut1WithHand ---
@register_object
class Chestnut1WithHand(CustomObjects):
    def __init__(self,
                 name='chestnut_1_with_hand',
                 obj_name='chestnut_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/chestnut/tulvpb/usd/MJCF/tulvpb_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Chestnut2WithHand ---
@register_object
class Chestnut2WithHand(CustomObjects):
    def __init__(self,
                 name='chestnut_2_with_hand',
                 obj_name='chestnut_2_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/chestnut/gjbnba/usd/MJCF/gjbnba_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Bratwurst1WithHand ---
@register_object
class Bratwurst1WithHand(CustomObjects):
    def __init__(self,
                 name='bratwurst_1_with_hand',
                 obj_name='bratwurst_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bratwurst/pqfrrn/usd/MJCF/pqfrrn_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Bratwurst2WithHand ---
@register_object
class Bratwurst2WithHand(CustomObjects):
    def __init__(self,
                 name='bratwurst_2_with_hand',
                 obj_name='bratwurst_2_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bratwurst/wuyflp/usd/MJCF/wuyflp_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Frame1WithHand ---
# @register_object
# class Frame1WithHand(CustomObjects):
#     def __init__(self,
#                  name='frame_1_with_hand',
#                  obj_name='frame_1_with_hand',
#                  ):
#         custom_path = os.path.join(
#                 str(absolute_path), f"assets/new_objects_with_hand/frame/trhhqo/usd/MJCF/trhhqo_with_hand.xml"
#             )
#         super().__init__(
#             custom_path=custom_path,
#             name=name,
#             obj_name=obj_name,
#         )
#         self.rotation = {
#             "x": (-np.pi / 2, -np.pi / 2),
#             "y": (-np.pi, -np.pi),
#             "z": (np.pi, np.pi),
#         }
#         self.rotation_axis = None


# --- appended class Frame2WithHand ---
# @register_object
# class Frame2WithHand(CustomObjects):
#     def __init__(self,
#                  name='frame_2_with_hand',
#                  obj_name='frame_2_with_hand',
#                  ):
#         custom_path = os.path.join(
#                 str(absolute_path), f"assets/new_objects_with_hand/frame/argijo/usd/MJCF/argijo_with_hand.xml"
#             )
#         super().__init__(
#             custom_path=custom_path,
#             name=name,
#             obj_name=obj_name,
#         )
#         self.rotation = {
#             "x": (-np.pi / 2, -np.pi / 2),
#             "y": (-np.pi, -np.pi),
#             "z": (np.pi, np.pi),
#         }
#         self.rotation_axis = None


# # --- appended class BasilJar1WithHand ---
# @register_object
# class BasilJar1WithHand(CustomObjects):
#     def __init__(self,
#                  name='basil_jar_1_with_hand',
#                  obj_name='basil_jar_1_with_hand',
#                  ):
#         custom_path = os.path.join(
#                 str(absolute_path), f"assets/new_objects_with_hand/basil_jar/swytaw/usd/MJCF/swytaw_with_hand.xml"
#             )
#         super().__init__(
#             custom_path=custom_path,
#             name=name,
#             obj_name=obj_name,
#         )
#         self.rotation = {
#             "x": (-np.pi / 2, -np.pi / 2),
#             "y": (-np.pi, -np.pi),
#             "z": (np.pi, np.pi),
#         }
#         self.rotation_axis = None


# --- appended class BottleOfBlackPepper1WithHand ---
@register_object
class BottleOfBlackPepper1WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_black_pepper_1_with_hand',
                 obj_name='bottle_of_black_pepper_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_black_pepper/ydzzrv/usd/MJCF/ydzzrv_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfBlackPepper2WithHand ---
@register_object
class BottleOfBlackPepper2WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_black_pepper_2_with_hand',
                 obj_name='bottle_of_black_pepper_2_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_black_pepper/honise/usd/MJCF/honise_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfBlackPepper3WithHand ---
@register_object
class BottleOfBlackPepper3WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_black_pepper_3_with_hand',
                 obj_name='bottle_of_black_pepper_3_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_black_pepper/ejtiig/usd/MJCF/ejtiig_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfBlackPepper4WithHand ---
@register_object
class BottleOfBlackPepper4WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_black_pepper_4_with_hand',
                 obj_name='bottle_of_black_pepper_4_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_black_pepper/zybfok/usd/MJCF/zybfok_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Asparagus1WithHand ---
@register_object
class Asparagus1WithHand(CustomObjects):
    def __init__(self,
                 name='asparagus_1_with_hand',
                 obj_name='asparagus_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/asparagus/eodozo/usd/MJCF/eodozo_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Asparagus2WithHand ---
@register_object
class Asparagus2WithHand(CustomObjects):
    def __init__(self,
                 name='asparagus_2_with_hand',
                 obj_name='asparagus_2_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/asparagus/xguktb/usd/MJCF/xguktb_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Asparagus3WithHand ---
@register_object
class Asparagus3WithHand(CustomObjects):
    def __init__(self,
                 name='asparagus_3_with_hand',
                 obj_name='asparagus_3_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/asparagus/npggjn/usd/MJCF/npggjn_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfTeaLeaves1WithHand ---
@register_object
class BottleOfTeaLeaves1WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_tea_leaves_1_with_hand',
                 obj_name='bottle_of_tea_leaves_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_tea_leaves/pfbtus/usd/MJCF/pfbtus_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfLemonSauce1WithHand ---
@register_object
class BottleOfLemonSauce1WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_lemon_sauce_1_with_hand',
                 obj_name='bottle_of_lemon_sauce_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_lemon_sauce/iyijeb/usd/MJCF/iyijeb_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class CanOfSoda1WithHand ---
@register_object
class CanOfSoda1WithHand(CustomObjects):
    def __init__(self,
                 name='can_of_soda_1_with_hand',
                 obj_name='can_of_soda_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/can_of_soda/iloapr/usd/MJCF/iloapr_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class CanOfSoda2WithHand ---
@register_object
class CanOfSoda2WithHand(CustomObjects):
    def __init__(self,
                 name='can_of_soda_2_with_hand',
                 obj_name='can_of_soda_2_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/can_of_soda/uzbpnw/usd/MJCF/uzbpnw_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class CanOfSoda3WithHand ---
@register_object
class CanOfSoda3WithHand(CustomObjects):
    def __init__(self,
                 name='can_of_soda_3_with_hand',
                 obj_name='can_of_soda_3_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/can_of_soda/itolcg/usd/MJCF/itolcg_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class CanOfSoda4WithHand ---
@register_object
class CanOfSoda4WithHand(CustomObjects):
    def __init__(self,
                 name='can_of_soda_4_with_hand',
                 obj_name='can_of_soda_4_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/can_of_soda/chwjfu/usd/MJCF/chwjfu_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class CanOfSoda5WithHand ---
@register_object
class CanOfSoda5WithHand(CustomObjects):
    def __init__(self,
                 name='can_of_soda_5_with_hand',
                 obj_name='can_of_soda_5_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/can_of_soda/frewxk/usd/MJCF/frewxk_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class CanOfSoda6WithHand ---
# @register_object
# class CanOfSoda6WithHand(CustomObjects):
#     def __init__(self,
#                  name='can_of_soda_6_with_hand',
#                  obj_name='can_of_soda_6_with_hand',
#                  ):
#         custom_path = os.path.join(
#                 str(absolute_path), f"assets/new_objects_with_hand/can_of_soda/ixrfxv/usd/MJCF/ixrfxv_with_hand.xml"
#             )
#         super().__init__(
#             custom_path=custom_path,
#             name=name,
#             obj_name=obj_name,
#         )
#         self.rotation = {
#             "x": (-np.pi / 2, -np.pi / 2),
#             "y": (-np.pi, -np.pi),
#             "z": (np.pi, np.pi),
#         }
#         self.rotation_axis = None


# --- appended class CanOfSoda7WithHand ---
@register_object
class CanOfSoda7WithHand(CustomObjects):
    def __init__(self,
                 name='can_of_soda_7_with_hand',
                 obj_name='can_of_soda_7_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/can_of_soda/xlyult/usd/MJCF/xlyult_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class CanOfSoda8WithHand ---
@register_object
class CanOfSoda8WithHand(CustomObjects):
    def __init__(self,
                 name='can_of_soda_8_with_hand',
                 obj_name='can_of_soda_8_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/can_of_soda/xmjfcg/usd/MJCF/xmjfcg_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class CanOfSoda9WithHand ---
@register_object
class CanOfSoda9WithHand(CustomObjects):
    def __init__(self,
                 name='can_of_soda_9_with_hand',
                 obj_name='can_of_soda_9_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/can_of_soda/mrrozu/usd/MJCF/mrrozu_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class CanOfSoda10WithHand ---
@register_object
class CanOfSoda10WithHand(CustomObjects):
    def __init__(self,
                 name='can_of_soda_10_with_hand',
                 obj_name='can_of_soda_10_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/can_of_soda/opivig/usd/MJCF/opivig_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class CanOfSoda11WithHand ---
@register_object
class CanOfSoda11WithHand(CustomObjects):
    def __init__(self,
                 name='can_of_soda_11_with_hand',
                 obj_name='can_of_soda_11_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/can_of_soda/ttxyui/usd/MJCF/ttxyui_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class CanOfSoda12WithHand ---
@register_object
class CanOfSoda12WithHand(CustomObjects):
    def __init__(self,
                 name='can_of_soda_12_with_hand',
                 obj_name='can_of_soda_12_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/can_of_soda/bfrzvk/usd/MJCF/bfrzvk_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class CanOfSoda13WithHand ---
@register_object
class CanOfSoda13WithHand(CustomObjects):
    def __init__(self,
                 name='can_of_soda_13_with_hand',
                 obj_name='can_of_soda_13_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/can_of_soda/lugwcz/usd/MJCF/lugwcz_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class CanOfSoda14WithHand ---
@register_object
class CanOfSoda14WithHand(CustomObjects):
    def __init__(self,
                 name='can_of_soda_14_with_hand',
                 obj_name='can_of_soda_14_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/can_of_soda/vszbvb/usd/MJCF/vszbvb_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfAppleJuice1WithHand ---
@register_object
class BottleOfAppleJuice1WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_apple_juice_1_with_hand',
                 obj_name='bottle_of_apple_juice_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_apple_juice/xvrbdy/usd/MJCF/xvrbdy_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfBarbecueSauce1WithHand ---
@register_object
class BottleOfBarbecueSauce1WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_barbecue_sauce_1_with_hand',
                 obj_name='bottle_of_barbecue_sauce_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_barbecue_sauce/ikbsox/usd/MJCF/ikbsox_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfBarbecueSauce2WithHand ---
@register_object
class BottleOfBarbecueSauce2WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_barbecue_sauce_2_with_hand',
                 obj_name='bottle_of_barbecue_sauce_2_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_barbecue_sauce/rzevkb/usd/MJCF/rzevkb_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfBarbecueSauce3WithHand ---
# @register_object
# class BottleOfBarbecueSauce3WithHand(CustomObjects):
#     def __init__(self,
#                  name='bottle_of_barbecue_sauce_3_with_hand',
#                  obj_name='bottle_of_barbecue_sauce_3_with_hand',
#                  ):
#         custom_path = os.path.join(
#                 str(absolute_path), f"assets/new_objects_with_hand/bottle_of_barbecue_sauce/nkqvex/usd/MJCF/nkqvex_with_hand.xml"
#             )
#         super().__init__(
#             custom_path=custom_path,
#             name=name,
#             obj_name=obj_name,
#         )
#         self.rotation = {
#             "x": (-np.pi / 2, -np.pi / 2),
#             "y": (-np.pi, -np.pi),
#             "z": (np.pi, np.pi),
#         }
#         self.rotation_axis = None


# --- appended class BottleOfVinegar1WithHand ---
@register_object
class BottleOfVinegar1WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_vinegar_1_with_hand',
                 obj_name='bottle_of_vinegar_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_vinegar/snzyfk/usd/MJCF/snzyfk_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BulldogClip1WithHand ---
@register_object
class BulldogClip1WithHand(CustomObjects):
    def __init__(self,
                 name='bulldog_clip_1_with_hand',
                 obj_name='bulldog_clip_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bulldog_clip/cqxnkn/usd/MJCF/cqxnkn_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class HalfBanana1WithHand ---
@register_object
class HalfBanana1WithHand(CustomObjects):
    def __init__(self,
                 name='half_banana_1_with_hand',
                 obj_name='half_banana_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/half_banana/matxor/usd/MJCF/matxor_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class HalfBanana2WithHand ---
@register_object
class HalfBanana2WithHand(CustomObjects):
    def __init__(self,
                 name='half_banana_2_with_hand',
                 obj_name='half_banana_2_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/half_banana/xytkre/usd/MJCF/xytkre_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None



# --- appended class Garlic1WithHand ---
@register_object
class Garlic1WithHand(CustomObjects):
    def __init__(self,
                 name='garlic_1_with_hand',
                 obj_name='garlic_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/garlic/nlclql/usd/MJCF/nlclql_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Garlic2WithHand ---
@register_object
class Garlic2WithHand(CustomObjects):
    def __init__(self,
                 name='garlic_2_with_hand',
                 obj_name='garlic_2_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/garlic/thigpl/usd/MJCF/thigpl_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfTomatoPaste1WithHand ---
@register_object
class BottleOfTomatoPaste1WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_tomato_paste_1_with_hand',
                 obj_name='bottle_of_tomato_paste_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_tomato_paste/kkqtjv/usd/MJCF/kkqtjv_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfTomatoPaste2WithHand ---
@register_object
class BottleOfTomatoPaste2WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_tomato_paste_2_with_hand',
                 obj_name='bottle_of_tomato_paste_2_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_tomato_paste/pnshkj/usd/MJCF/pnshkj_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfTomatoPaste3WithHand ---
@register_object
class BottleOfTomatoPaste3WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_tomato_paste_3_with_hand',
                 obj_name='bottle_of_tomato_paste_3_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_tomato_paste/toeelk/usd/MJCF/toeelk_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Grater1WithHand ---
# @register_object
# class Grater1WithHand(CustomObjects):
#     def __init__(self,
#                  name='grater_1_with_hand',
#                  obj_name='grater_1_with_hand',
#                  ):
#         custom_path = os.path.join(
#                 str(absolute_path), f"assets/new_objects_with_hand/grater/jlkowf/usd/MJCF/jlkowf_with_hand.xml"
#             )
#         super().__init__(
#             custom_path=custom_path,
#             name=name,
#             obj_name=obj_name,
#         )
#         self.rotation = {
#             "x": (-np.pi / 2, -np.pi / 2),
#             "y": (-np.pi, -np.pi),
#             "z": (np.pi, np.pi),
#         }
#         self.rotation_axis = None


# --- appended class HalfColdCuts1WithHand ---
@register_object
class HalfColdCuts1WithHand(CustomObjects):
    def __init__(self,
                 name='half_cold_cuts_1_with_hand',
                 obj_name='half_cold_cuts_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/half_cold_cuts/khcjog/usd/MJCF/khcjog_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class HalfColdCuts2WithHand ---
@register_object
class HalfColdCuts2WithHand(CustomObjects):
    def __init__(self,
                 name='half_cold_cuts_2_with_hand',
                 obj_name='half_cold_cuts_2_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/half_cold_cuts/qhmncb/usd/MJCF/qhmncb_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfLiquidSoap1WithHand ---
@register_object
class BottleOfLiquidSoap1WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_liquid_soap_1_with_hand',
                 obj_name='bottle_of_liquid_soap_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_liquid_soap/bhquvg/usd/MJCF/bhquvg_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Baguette1WithHand ---
@register_object
class Baguette1WithHand(CustomObjects):
    def __init__(self,
                 name='baguette_1_with_hand',
                 obj_name='baguette_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/baguette/xhqnuc/usd/MJCF/xhqnuc_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Baguette2WithHand ---
@register_object
class Baguette2WithHand(CustomObjects):
    def __init__(self,
                 name='baguette_2_with_hand',
                 obj_name='baguette_2_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/baguette/pjzkeh/usd/MJCF/pjzkeh_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Baguette3WithHand ---
@register_object
class Baguette3WithHand(CustomObjects):
    def __init__(self,
                 name='baguette_3_with_hand',
                 obj_name='baguette_3_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/baguette/ypbyek/usd/MJCF/ypbyek_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Baguette4WithHand ---
@register_object
class Baguette4WithHand(CustomObjects):
    def __init__(self,
                 name='baguette_4_with_hand',
                 obj_name='baguette_4_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/baguette/xydhpd/usd/MJCF/xydhpd_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BoxOfBakingMix4WithHand ---
@register_object
class BoxOfBakingMix4WithHand(CustomObjects):
    def __init__(self,
                 name='box_of_baking_mix_4_with_hand',
                 obj_name='box_of_baking_mix_4_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/box_of_baking_mix/fmewsz/usd/MJCF/fmewsz_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BoxOfBakingMix5WithHand ---
@register_object
class BoxOfBakingMix5WithHand(CustomObjects):
    def __init__(self,
                 name='box_of_baking_mix_5_with_hand',
                 obj_name='box_of_baking_mix_5_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/box_of_baking_mix/qkvqkm/usd/MJCF/qkvqkm_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class HalfBellPepper1WithHand ---
@register_object
class HalfBellPepper1WithHand(CustomObjects):
    def __init__(self,
                 name='half_bell_pepper_1_with_hand',
                 obj_name='half_bell_pepper_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/half_bell_pepper/uycgmx/usd/MJCF/uycgmx_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class HalfBellPepper2WithHand ---
@register_object
class HalfBellPepper2WithHand(CustomObjects):
    def __init__(self,
                 name='half_bell_pepper_2_with_hand',
                 obj_name='half_bell_pepper_2_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/half_bell_pepper/waeejs/usd/MJCF/waeejs_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfTonic1WithHand ---
@register_object
class BottleOfTonic1WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_tonic_1_with_hand',
                 obj_name='bottle_of_tonic_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_tonic/hpddkk/usd/MJCF/hpddkk_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Comb2WithHand ---
@register_object
class Comb2WithHand(CustomObjects):
    def __init__(self,
                 name='comb_2_with_hand',
                 obj_name='comb_2_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/comb/nybyjz/usd/MJCF/nybyjz_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Comb3WithHand ---
@register_object
class Comb3WithHand(CustomObjects):
    def __init__(self,
                 name='comb_3_with_hand',
                 obj_name='comb_3_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/comb/yopqrq/usd/MJCF/yopqrq_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class CartonOfMilk3WithHand ---
@register_object
class CartonOfMilk3WithHand(CustomObjects):
    def __init__(self,
                 name='carton_of_milk_3_with_hand',
                 obj_name='carton_of_milk_3_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/carton_of_milk/kklgxk/usd/MJCF/kklgxk_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class CartonOfMilk6WithHand ---
@register_object
class CartonOfMilk6WithHand(CustomObjects):
    def __init__(self,
                 name='carton_of_milk_6_with_hand',
                 obj_name='carton_of_milk_6_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/carton_of_milk/atyqub/usd/MJCF/atyqub_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class CartonOfMilk7WithHand ---
@register_object
class CartonOfMilk7WithHand(CustomObjects):
    def __init__(self,
                 name='carton_of_milk_7_with_hand',
                 obj_name='carton_of_milk_7_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/carton_of_milk/znqqft/usd/MJCF/znqqft_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfSupplements1WithHand ---
@register_object
class BottleOfSupplements1WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_supplements_1_with_hand',
                 obj_name='bottle_of_supplements_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_supplements/oqakev/usd/MJCF/oqakev_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfSupplements2WithHand ---
@register_object
class BottleOfSupplements2WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_supplements_2_with_hand',
                 obj_name='bottle_of_supplements_2_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_supplements/kgreql/usd/MJCF/kgreql_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfGroundMace1WithHand ---
@register_object
class BottleOfGroundMace1WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_ground_mace_1_with_hand',
                 obj_name='bottle_of_ground_mace_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_ground_mace/lgpxro/usd/MJCF/lgpxro_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfSkinCream1WithHand ---
@register_object
class BottleOfSkinCream1WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_skin_cream_1_with_hand',
                 obj_name='bottle_of_skin_cream_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_skin_cream/ynwxtx/usd/MJCF/ynwxtx_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BokChoy1WithHand ---
@register_object
class BokChoy1WithHand(CustomObjects):
    def __init__(self,
                 name='bok_choy_1_with_hand',
                 obj_name='bok_choy_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bok_choy/bbvcji/usd/MJCF/bbvcji_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BokChoy2WithHand ---
@register_object
class BokChoy2WithHand(CustomObjects):
    def __init__(self,
                 name='bok_choy_2_with_hand',
                 obj_name='bok_choy_2_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bok_choy/jpkewd/usd/MJCF/jpkewd_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Goggles1WithHand ---
# @register_object
# class Goggles1WithHand(CustomObjects):
#     def __init__(self,
#                  name='goggles_1_with_hand',
#                  obj_name='goggles_1_with_hand',
#                  ):
#         custom_path = os.path.join(
#                 str(absolute_path), f"assets/new_objects_with_hand/goggles/wszdxi/usd/MJCF/wszdxi_with_hand.xml"
#             )
#         super().__init__(
#             custom_path=custom_path,
#             name=name,
#             obj_name=obj_name,
#         )
#         self.rotation = {
#             "x": (-np.pi / 2, -np.pi / 2),
#             "y": (-np.pi, -np.pi),
#             "z": (np.pi, np.pi),
#         }
#         self.rotation_axis = None


# --- appended class BottleOfMedicine1WithHand ---
@register_object
class BottleOfMedicine1WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_medicine_1_with_hand',
                 obj_name='bottle_of_medicine_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_medicine/syfpak/usd/MJCF/syfpak_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfMedicine2WithHand ---
@register_object
class BottleOfMedicine2WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_medicine_2_with_hand',
                 obj_name='bottle_of_medicine_2_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_medicine/kqkwoq/usd/MJCF/kqkwoq_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfMedicine3WithHand ---
@register_object
class BottleOfMedicine3WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_medicine_3_with_hand',
                 obj_name='bottle_of_medicine_3_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_medicine/fmfwng/usd/MJCF/fmfwng_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfMedicine4WithHand ---
@register_object
class BottleOfMedicine4WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_medicine_4_with_hand',
                 obj_name='bottle_of_medicine_4_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_medicine/egondf/usd/MJCF/egondf_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfMedicine5WithHand ---
@register_object
class BottleOfMedicine5WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_medicine_5_with_hand',
                 obj_name='bottle_of_medicine_5_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_medicine/kasbsy/usd/MJCF/kasbsy_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfMedicine6WithHand ---
@register_object
class BottleOfMedicine6WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_medicine_6_with_hand',
                 obj_name='bottle_of_medicine_6_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_medicine/zfbnjh/usd/MJCF/zfbnjh_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfMedicine7WithHand ---
@register_object
class BottleOfMedicine7WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_medicine_7_with_hand',
                 obj_name='bottle_of_medicine_7_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_medicine/qqsukh/usd/MJCF/qqsukh_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfMedicine8WithHand ---
@register_object
class BottleOfMedicine8WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_medicine_8_with_hand',
                 obj_name='bottle_of_medicine_8_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_medicine/hvocpc/usd/MJCF/hvocpc_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfPapayaJuice1WithHand ---
@register_object
class BottleOfPapayaJuice1WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_papaya_juice_1_with_hand',
                 obj_name='bottle_of_papaya_juice_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_papaya_juice/nmfmxy/usd/MJCF/nmfmxy_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfPapayaJuice2WithHand ---
@register_object
class BottleOfPapayaJuice2WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_papaya_juice_2_with_hand',
                 obj_name='bottle_of_papaya_juice_2_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_papaya_juice/tcauim/usd/MJCF/tcauim_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfAntihistamines1WithHand ---
@register_object
class BottleOfAntihistamines1WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_antihistamines_1_with_hand',
                 obj_name='bottle_of_antihistamines_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_antihistamines/agavwx/usd/MJCF/agavwx_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Bandage1WithHand ---
@register_object
class Bandage1WithHand(CustomObjects):
    def __init__(self,
                 name='bandage_1_with_hand',
                 obj_name='bandage_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bandage/riftxh/usd/MJCF/riftxh_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class CanOfCorn1WithHand ---
@register_object
class CanOfCorn1WithHand(CustomObjects):
    def __init__(self,
                 name='can_of_corn_1_with_hand',
                 obj_name='can_of_corn_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/can_of_corn/pddtfk/usd/MJCF/pddtfk_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class DeodorantStick1WithHand ---
@register_object
class DeodorantStick1WithHand(CustomObjects):
    def __init__(self,
                 name='deodorant_stick_1_with_hand',
                 obj_name='deodorant_stick_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/deodorant_stick/albeyc/usd/MJCF/albeyc_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class HalfMango1WithHand ---
@register_object
class HalfMango1WithHand(CustomObjects):
    def __init__(self,
                 name='half_mango_1_with_hand',
                 obj_name='half_mango_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/half_mango/jywliv/usd/MJCF/jywliv_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class HalfMango2WithHand ---
# @register_object
# class HalfMango2WithHand(CustomObjects):
#     def __init__(self,
#                  name='half_mango_2_with_hand',
#                  obj_name='half_mango_2_with_hand',
#                  ):
#         custom_path = os.path.join(
#                 str(absolute_path), f"assets/new_objects_with_hand/half_mango/qzgjym/usd/MJCF/qzgjym_with_hand.xml"
#             )
#         super().__init__(
#             custom_path=custom_path,
#             name=name,
#             obj_name=obj_name,
#         )
#         self.rotation = {
#             "x": (-np.pi / 2, -np.pi / 2),
#             "y": (-np.pi, -np.pi),
#             "z": (np.pi, np.pi),
#         }
#         self.rotation_axis = None


# --- appended class BottleOfProteinPowder1WithHand ---
# @register_object
# class BottleOfProteinPowder1WithHand(CustomObjects):
#     def __init__(self,
#                  name='bottle_of_protein_powder_1_with_hand',
#                  obj_name='bottle_of_protein_powder_1_with_hand',
#                  ):
#         custom_path = os.path.join(
#                 str(absolute_path), f"assets/new_objects_with_hand/bottle_of_protein_powder/ysgesq/usd/MJCF/ysgesq_with_hand.xml"
#             )
#         super().__init__(
#             custom_path=custom_path,
#             name=name,
#             obj_name=obj_name,
#         )
#         self.rotation = {
#             "x": (-np.pi / 2, -np.pi / 2),
#             "y": (-np.pi, -np.pi),
#             "z": (np.pi, np.pi),
#         }
#         self.rotation_axis = None


# --- appended class BottleOfProteinPowder2WithHand ---
# @register_object
# class BottleOfProteinPowder2WithHand(CustomObjects):
#     def __init__(self,
#                  name='bottle_of_protein_powder_2_with_hand',
#                  obj_name='bottle_of_protein_powder_2_with_hand',
#                  ):
#         custom_path = os.path.join(
#                 str(absolute_path), f"assets/new_objects_with_hand/bottle_of_protein_powder/rbvrrp/usd/MJCF/rbvrrp_with_hand.xml"
#             )
#         super().__init__(
#             custom_path=custom_path,
#             name=name,
#             obj_name=obj_name,
#         )
#         self.rotation = {
#             "x": (-np.pi / 2, -np.pi / 2),
#             "y": (-np.pi, -np.pi),
#             "z": (np.pi, np.pi),
#         }
#         self.rotation_axis = None


# --- appended class HalfBaguette1WithHand ---
@register_object
class HalfBaguette1WithHand(CustomObjects):
    def __init__(self,
                 name='half_baguette_1_with_hand',
                 obj_name='half_baguette_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/half_baguette/mnhwnp/usd/MJCF/mnhwnp_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class HalfBaguette2WithHand ---
# @register_object
# class HalfBaguette2WithHand(CustomObjects):
#     def __init__(self,
#                  name='half_baguette_2_with_hand',
#                  obj_name='half_baguette_2_with_hand',
#                  ):
#         custom_path = os.path.join(
#                 str(absolute_path), f"assets/new_objects_with_hand/half_baguette/mdaqot/usd/MJCF/mdaqot_with_hand.xml"
#             )
#         super().__init__(
#             custom_path=custom_path,
#             name=name,
#             obj_name=obj_name,
#         )
#         self.rotation = {
#             "x": (-np.pi / 2, -np.pi / 2),
#             "y": (-np.pi, -np.pi),
#             "z": (np.pi, np.pi),
#         }
#         self.rotation_axis = None


# --- appended class BeefBrothCarton1WithHand ---
# @register_object
# class BeefBrothCarton1WithHand(CustomObjects):
#     def __init__(self,
#                  name='beef_broth_carton_1_with_hand',
#                  obj_name='beef_broth_carton_1_with_hand',
#                  ):
#         custom_path = os.path.join(
#                 str(absolute_path), f"assets/new_objects_with_hand/beef_broth_carton/ecqxgd/usd/MJCF/ecqxgd_with_hand.xml"
#             )
#         super().__init__(
#             custom_path=custom_path,
#             name=name,
#             obj_name=obj_name,
#         )
#         self.rotation = {
#             "x": (-np.pi / 2, -np.pi / 2),
#             "y": (-np.pi, -np.pi),
#             "z": (np.pi, np.pi),
#         }
#         self.rotation_axis = None


# --- appended class HalfPepperoni1WithHand ---
@register_object
class HalfPepperoni1WithHand(CustomObjects):
    def __init__(self,
                 name='half_pepperoni_1_with_hand',
                 obj_name='half_pepperoni_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/half_pepperoni/nworyk/usd/MJCF/nworyk_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Charger1WithHand ---
@register_object
class Charger1WithHand(CustomObjects):
    def __init__(self,
                 name='charger_1_with_hand',
                 obj_name='charger_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/charger/bapkyh/usd/MJCF/bapkyh_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class CanOfTomatoPaste1WithHand ---
@register_object
class CanOfTomatoPaste1WithHand(CustomObjects):
    def __init__(self,
                 name='can_of_tomato_paste_1_with_hand',
                 obj_name='can_of_tomato_paste_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/can_of_tomato_paste/sqqdzb/usd/MJCF/sqqdzb_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class HalfPickle1WithHand ---
@register_object
class HalfPickle1WithHand(CustomObjects):
    def __init__(self,
                 name='half_pickle_1_with_hand',
                 obj_name='half_pickle_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/half_pickle/rmvuqm/usd/MJCF/rmvuqm_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class HalfPickle2WithHand ---
@register_object
class HalfPickle2WithHand(CustomObjects):
    def __init__(self,
                 name='half_pickle_2_with_hand',
                 obj_name='half_pickle_2_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/half_pickle/enuftv/usd/MJCF/enuftv_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class HalfButterCookie2WithHand ---
@register_object
class HalfButterCookie2WithHand(CustomObjects):
    def __init__(self,
                 name='half_butter_cookie_2_with_hand',
                 obj_name='half_butter_cookie_2_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/half_butter_cookie/wqgfsj/usd/MJCF/wqgfsj_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Gooseberry1WithHand ---
# @register_object
# class Gooseberry1WithHand(CustomObjects):
#     def __init__(self
#                  name='gooseberry_1_with_hand',
#                  obj_name='gooseberry_1_with_hand',
#                  ):
#         custom_path = os.path.join(
#                 str(absolute_path), f"assets/new_objects_with_hand/gooseberry/cltzwx/usd/MJCF/cltzwx_with_hand.xml"
#             )
#         super().__init__(
#             custom_path=custom_path,
#             name=name,
#             obj_name=obj_name,
#         )
#         self.rotation = {
#             "x": (-np.pi / 2, -np.pi / 2),
#             "y": (-np.pi, -np.pi),
#             "z": (np.pi, np.pi),
#         }
#         self.rotation_axis = None


# --- appended class HalfMacaroon1WithHand ---
# @register_object
# class HalfMacaroon1WithHand(CustomObjects):
#     def __init__(self,
#                  name='half_macaroon_1_with_hand',
#                  obj_name='half_macaroon_1_with_hand',
#                  ):
#         custom_path = os.path.join(
#                 str(absolute_path), f"assets/new_objects_with_hand/half_macaroon/znmffr/usd/MJCF/znmffr_with_hand.xml"
#             )
#         super().__init__(
#             custom_path=custom_path,
#             name=name,
#             obj_name=obj_name,
#         )
#         self.rotation = {
#             "x": (-np.pi / 2, -np.pi / 2),
#             "y": (-np.pi, -np.pi),
#             "z": (np.pi, np.pi),
#         }
#         self.rotation_axis = None


# --- appended class HalfMacaroon2WithHand ---
# @register_object
# class HalfMacaroon2WithHand(CustomObjects):
#     def __init__(self,
#                  name='half_macaroon_2_with_hand',
#                  obj_name='half_macaroon_2_with_hand',
#                  ):
#         custom_path = os.path.join(
#                 str(absolute_path), f"assets/new_objects_with_hand/half_macaroon/gafeof/usd/MJCF/gafeof_with_hand.xml"
#             )
#         super().__init__(
#             custom_path=custom_path,
#             name=name,
#             obj_name=obj_name,
#         )
#         self.rotation = {
#             "x": (-np.pi / 2, -np.pi / 2),
#             "y": (-np.pi, -np.pi),
#             "z": (np.pi, np.pi),
#         }
#         self.rotation_axis = None


# --- appended class CelluloseTapeDispenser1WithHand ---
@register_object
class CelluloseTapeDispenser1WithHand(CustomObjects):
    def __init__(self,
                 name='cellulose_tape_dispenser_1_with_hand',
                 obj_name='cellulose_tape_dispenser_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/cellulose_tape_dispenser/fetnry/usd/MJCF/fetnry_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class CelluloseTapeDispenser2WithHand ---
@register_object
class CelluloseTapeDispenser2WithHand(CustomObjects):
    def __init__(self,
                 name='cellulose_tape_dispenser_2_with_hand',
                 obj_name='cellulose_tape_dispenser_2_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/cellulose_tape_dispenser/yyekns/usd/MJCF/yyekns_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BoxOfChocolates1WithHand ---
@register_object
class BoxOfChocolates1WithHand(CustomObjects):
    def __init__(self,
                 name='box_of_chocolates_1_with_hand',
                 obj_name='box_of_chocolates_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/box_of_chocolates/bdvkbh/usd/MJCF/bdvkbh_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BoxOfCaneSugar4WithHand ---
@register_object
class BoxOfCaneSugar4WithHand(CustomObjects):
    def __init__(self,
                 name='box_of_cane_sugar_4_with_hand',
                 obj_name='box_of_cane_sugar_4_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/box_of_cane_sugar/pozpqi/usd/MJCF/pozpqi_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BoxOfCaneSugar5WithHand ---
@register_object
class BoxOfCaneSugar5WithHand(CustomObjects):
    def __init__(self,
                 name='box_of_cane_sugar_5_with_hand',
                 obj_name='box_of_cane_sugar_5_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/box_of_cane_sugar/rvsivw/usd/MJCF/rvsivw_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfGinger1WithHand ---
@register_object
class BottleOfGinger1WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_ginger_1_with_hand',
                 obj_name='bottle_of_ginger_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_ginger/drqhzo/usd/MJCF/drqhzo_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfLemonade1WithHand ---
@register_object
class BottleOfLemonade1WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_lemonade_1_with_hand',
                 obj_name='bottle_of_lemonade_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_lemonade/hqobwj/usd/MJCF/hqobwj_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Chip1WithHand ---
@register_object
class Chip1WithHand(CustomObjects):
    def __init__(self,
                 name='chip_1_with_hand',
                 obj_name='chip_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/chip/obgeiz/usd/MJCF/obgeiz_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfDishSoap1WithHand ---
@register_object
class BottleOfDishSoap1WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_dish_soap_1_with_hand',
                 obj_name='bottle_of_dish_soap_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_dish_soap/bnmixt/usd/MJCF/bnmixt_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfSesameSeeds1WithHand ---
@register_object
class BottleOfSesameSeeds1WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_sesame_seeds_1_with_hand',
                 obj_name='bottle_of_sesame_seeds_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_sesame_seeds/lzndie/usd/MJCF/lzndie_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfCoconutWater1WithHand ---
@register_object
class BottleOfCoconutWater1WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_coconut_water_1_with_hand',
                 obj_name='bottle_of_coconut_water_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_coconut_water/lsixio/usd/MJCF/lsixio_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class HalfNectarine1WithHand ---
# @register_object
# class HalfNectarine1WithHand(CustomObjects):
#     def __init__(self,
#                  name='half_nectarine_1_with_hand',
#                  obj_name='half_nectarine_1_with_hand',
#                  ):
#         custom_path = os.path.join(
#                 str(absolute_path), f"assets/new_objects_with_hand/half_nectarine/uoechx/usd/MJCF/uoechx_with_hand.xml"
#             )
#         super().__init__(
#             custom_path=custom_path,
#             name=name,
#             obj_name=obj_name,
#         )
#         self.rotation = {
#             "x": (-np.pi / 2, -np.pi / 2),
#             "y": (-np.pi, -np.pi),
#             "z": (np.pi, np.pi),
#         }
#         self.rotation_axis = None


# --- appended class HalfNectarine2WithHand ---
# @register_object
# class HalfNectarine2WithHand(CustomObjects):
#     def __init__(self,
#                  name='half_nectarine_2_with_hand',
#                  obj_name='half_nectarine_2_with_hand',
#                  ):
#         custom_path = os.path.join(
#                 str(absolute_path), f"assets/new_objects_with_hand/half_nectarine/glfyoh/usd/MJCF/glfyoh_with_hand.xml"
#             )
#         super().__init__(
#             custom_path=custom_path,
#             name=name,
#             obj_name=obj_name,
#         )
#         self.rotation = {
#             "x": (-np.pi / 2, -np.pi / 2),
#             "y": (-np.pi, -np.pi),
#             "z": (np.pi, np.pi),
#         }
#         self.rotation_axis = None


# --- appended class BottleOfGroundCloves1WithHand ---
@register_object
class BottleOfGroundCloves1WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_ground_cloves_1_with_hand',
                 obj_name='bottle_of_ground_cloves_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_ground_cloves/vzamzb/usd/MJCF/vzamzb_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfDisinfectant1WithHand ---
@register_object
class BottleOfDisinfectant1WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_disinfectant_1_with_hand',
                 obj_name='bottle_of_disinfectant_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_disinfectant/ucqzck/usd/MJCF/ucqzck_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BeanCurd1WithHand ---
@register_object
class BeanCurd1WithHand(CustomObjects):
    def __init__(self,
                 name='bean_curd_1_with_hand',
                 obj_name='bean_curd_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bean_curd/hekigc/usd/MJCF/hekigc_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class CanOfBakingMix1WithHand ---
@register_object
class CanOfBakingMix1WithHand(CustomObjects):
    def __init__(self,
                 name='can_of_baking_mix_1_with_hand',
                 obj_name='can_of_baking_mix_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/can_of_baking_mix/blrqqz/usd/MJCF/blrqqz_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class CanOfBakingMix2WithHand ---
@register_object
class CanOfBakingMix2WithHand(CustomObjects):
    def __init__(self,
                 name='can_of_baking_mix_2_with_hand',
                 obj_name='can_of_baking_mix_2_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/can_of_baking_mix/rxorlp/usd/MJCF/rxorlp_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class CanOfBakingMix3WithHand ---
# @register_object
# class CanOfBakingMix3WithHand(CustomObjects):
#     def __init__(self,
#                  name='can_of_baking_mix_3_with_hand',
#                  obj_name='can_of_baking_mix_3_with_hand',
#                  ):
#         custom_path = os.path.join(
#                 str(absolute_path), f"assets/new_objects_with_hand/can_of_baking_mix/xefopo/usd/MJCF/xefopo_with_hand.xml"
#             )
#         super().__init__(
#             custom_path=custom_path,
#             name=name,
#             obj_name=obj_name,
#         )
#         self.rotation = {
#             "x": (-np.pi / 2, -np.pi / 2),
#             "y": (-np.pi, -np.pi),
#             "z": (np.pi, np.pi),
#         }
#         self.rotation_axis = None


# --- appended class CanOfBakingMix4WithHand ---
@register_object
class CanOfBakingMix4WithHand(CustomObjects):
    def __init__(self,
                 name='can_of_baking_mix_4_with_hand',
                 obj_name='can_of_baking_mix_4_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/can_of_baking_mix/fpbxfp/usd/MJCF/fpbxfp_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class CanOfBakingMix5WithHand ---
# @register_object
# class CanOfBakingMix5WithHand(CustomObjects):
#     def __init__(self,
#                  name='can_of_baking_mix_5_with_hand',
#                  obj_name='can_of_baking_mix_5_with_hand',
#                  ):
#         custom_path = os.path.join(
#                 str(absolute_path), f"assets/new_objects_with_hand/can_of_baking_mix/ohtiap/usd/MJCF/ohtiap_with_hand.xml"
#             )
#         super().__init__(
#             custom_path=custom_path,
#             name=name,
#             obj_name=obj_name,
#         )
#         self.rotation = {
#             "x": (-np.pi / 2, -np.pi / 2),
#             "y": (-np.pi, -np.pi),
#             "z": (np.pi, np.pi),
#         }
#         self.rotation_axis = None


# --- appended class CanOfBakingMix6WithHand ---
@register_object
class CanOfBakingMix6WithHand(CustomObjects):
    def __init__(self,
                 name='can_of_baking_mix_6_with_hand',
                 obj_name='can_of_baking_mix_6_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/can_of_baking_mix/orwvfx/usd/MJCF/orwvfx_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class ButterCookie1WithHand ---
@register_object
class ButterCookie1WithHand(CustomObjects):
    def __init__(self,
                 name='butter_cookie_1_with_hand',
                 obj_name='butter_cookie_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/butter_cookie/kukrla/usd/MJCF/kukrla_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfGroundNutmeg1WithHand ---
@register_object
class BottleOfGroundNutmeg1WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_ground_nutmeg_1_with_hand',
                 obj_name='bottle_of_ground_nutmeg_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_ground_nutmeg/qebruq/usd/MJCF/qebruq_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class CaseOfEyeshadow1WithHand ---
# @register_object
# class CaseOfEyeshadow1WithHand(CustomObjects):
#     def __init__(self,
#                  name='case_of_eyeshadow_1_with_hand',
#                  obj_name='case_of_eyeshadow_1_with_hand',
#                  ):
#         custom_path = os.path.join(
#                 str(absolute_path), f"assets/new_objects_with_hand/case_of_eyeshadow/zgervc/usd/MJCF/zgervc_with_hand.xml"
#             )
#         super().__init__(
#             custom_path=custom_path,
#             name=name,
#             obj_name=obj_name,
#         )
#         self.rotation = {
#             "x": (-np.pi / 2, -np.pi / 2),
#             "y": (-np.pi, -np.pi),
#             "z": (np.pi, np.pi),
#         }
#         self.rotation_axis = None


# --- appended class BoxOfFlour1WithHand ---
# @register_object
# class BoxOfFlour1WithHand(CustomObjects):
#     def __init__(self,
#                  name='box_of_flour_1_with_hand',
#                  obj_name='box_of_flour_1_with_hand',
#                  ):
#         custom_path = os.path.join(
#                 str(absolute_path), f"assets/new_objects_with_hand/box_of_flour/ylezpk/usd/MJCF/ylezpk_with_hand.xml"
#             )
#         super().__init__(
#             custom_path=custom_path,
#             name=name,
#             obj_name=obj_name,
#         )
#         self.rotation = {
#             "x": (-np.pi / 2, -np.pi / 2),
#             "y": (-np.pi, -np.pi),
#             "z": (np.pi, np.pi),
#         }
#         self.rotation_axis = None


# --- appended class ChickenSoupCarton1WithHand ---
# @register_object
# class ChickenSoupCarton1WithHand(CustomObjects):
#     def __init__(self,
#                  name='chicken_soup_carton_1_with_hand',
#                  obj_name='chicken_soup_carton_1_with_hand',
#                  ):
#         custom_path = os.path.join(
#                 str(absolute_path), f"assets/new_objects_with_hand/chicken_soup_carton/ooyqcr/usd/MJCF/ooyqcr_with_hand.xml"
#             )
#         super().__init__(
#             custom_path=custom_path,
#             name=name,
#             obj_name=obj_name,
#         )
#         self.rotation = {
#             "x": (-np.pi / 2, -np.pi / 2),
#             "y": (-np.pi, -np.pi),
#             "z": (np.pi, np.pi),
#         }
#         self.rotation_axis = None


# --- appended class BoxOfBakingSoda1WithHand ---
@register_object
class BoxOfBakingSoda1WithHand(CustomObjects):
    def __init__(self,
                 name='box_of_baking_soda_1_with_hand',
                 obj_name='box_of_baking_soda_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/box_of_baking_soda/pskrgy/usd/MJCF/pskrgy_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class HalfApple3WithHand ---
@register_object
class HalfApple3WithHand(CustomObjects):
    def __init__(self,
                 name='half_apple_3_with_hand',
                 obj_name='half_apple_3_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/half_apple/jjaskz/usd/MJCF/jjaskz_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class CartonOfPineappleJuice1WithHand ---
@register_object
class CartonOfPineappleJuice1WithHand(CustomObjects):
    def __init__(self,
                 name='carton_of_pineapple_juice_1_with_hand',
                 obj_name='carton_of_pineapple_juice_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/carton_of_pineapple_juice/vzueyg/usd/MJCF/vzueyg_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfFaceCream1WithHand ---
@register_object
class BottleOfFaceCream1WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_face_cream_1_with_hand',
                 obj_name='bottle_of_face_cream_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_face_cream/dztaed/usd/MJCF/dztaed_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class CanOfCoffee1WithHand ---
@register_object
class CanOfCoffee1WithHand(CustomObjects):
    def __init__(self,
                 name='can_of_coffee_1_with_hand',
                 obj_name='can_of_coffee_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/can_of_coffee/poteji/usd/MJCF/poteji_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class CanOfCoffee2WithHand ---
@register_object
class CanOfCoffee2WithHand(CustomObjects):
    def __init__(self,
                 name='can_of_coffee_2_with_hand',
                 obj_name='can_of_coffee_2_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/can_of_coffee/zubwua/usd/MJCF/zubwua_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class CanOfIcetea1WithHand ---
@register_object
class CanOfIcetea1WithHand(CustomObjects):
    def __init__(self,
                 name='can_of_icetea_1_with_hand',
                 obj_name='can_of_icetea_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/can_of_icetea/ifrjsc/usd/MJCF/ifrjsc_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class HalfSourdough1WithHand ---
@register_object
class HalfSourdough1WithHand(CustomObjects):
    def __init__(self,
                 name='half_sourdough_1_with_hand',
                 obj_name='half_sourdough_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/half_sourdough/flwdle/usd/MJCF/flwdle_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfOnionPowder1WithHand ---
@register_object
class BottleOfOnionPowder1WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_onion_powder_1_with_hand',
                 obj_name='bottle_of_onion_powder_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_onion_powder/xruqod/usd/MJCF/xruqod_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfBeer1WithHand ---
@register_object
class BottleOfBeer1WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_beer_1_with_hand',
                 obj_name='bottle_of_beer_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_beer/vhscym/usd/MJCF/vhscym_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfBeer2WithHand ---
@register_object
class BottleOfBeer2WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_beer_2_with_hand',
                 obj_name='bottle_of_beer_2_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_beer/rjwdae/usd/MJCF/rjwdae_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfBeer3WithHand ---
@register_object
class BottleOfBeer3WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_beer_3_with_hand',
                 obj_name='bottle_of_beer_3_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_beer/ukbhdj/usd/MJCF/ukbhdj_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfBeer4WithHand ---
@register_object
class BottleOfBeer4WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_beer_4_with_hand',
                 obj_name='bottle_of_beer_4_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_beer/mhzpkh/usd/MJCF/mhzpkh_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfBeer5WithHand ---
@register_object
class BottleOfBeer5WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_beer_5_with_hand',
                 obj_name='bottle_of_beer_5_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_beer/jssuog/usd/MJCF/jssuog_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfBeer6WithHand ---
@register_object
class BottleOfBeer6WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_beer_6_with_hand',
                 obj_name='bottle_of_beer_6_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_beer/dcwvkg/usd/MJCF/dcwvkg_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfBeer7WithHand ---
@register_object
class BottleOfBeer7WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_beer_7_with_hand',
                 obj_name='bottle_of_beer_7_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_beer/crfcwo/usd/MJCF/crfcwo_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfBeer8WithHand ---
@register_object
class BottleOfBeer8WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_beer_8_with_hand',
                 obj_name='bottle_of_beer_8_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_beer/gxxbhh/usd/MJCF/gxxbhh_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfBeer9WithHand ---
@register_object
class BottleOfBeer9WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_beer_9_with_hand',
                 obj_name='bottle_of_beer_9_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_beer/noxtlc/usd/MJCF/noxtlc_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfBeer10WithHand ---
@register_object
class BottleOfBeer10WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_beer_10_with_hand',
                 obj_name='bottle_of_beer_10_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_beer/ikgezm/usd/MJCF/ikgezm_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfBeer11WithHand ---
@register_object
class BottleOfBeer11WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_beer_11_with_hand',
                 obj_name='bottle_of_beer_11_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_beer/phdimo/usd/MJCF/phdimo_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfBeer12WithHand ---
@register_object
class BottleOfBeer12WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_beer_12_with_hand',
                 obj_name='bottle_of_beer_12_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_beer/meqliv/usd/MJCF/meqliv_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfBeer13WithHand ---
@register_object
class BottleOfBeer13WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_beer_13_with_hand',
                 obj_name='bottle_of_beer_13_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_beer/qepxvl/usd/MJCF/qepxvl_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfBeer14WithHand ---
@register_object
class BottleOfBeer14WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_beer_14_with_hand',
                 obj_name='bottle_of_beer_14_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_beer/miiijl/usd/MJCF/miiijl_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfBeer15WithHand ---
@register_object
class BottleOfBeer15WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_beer_15_with_hand',
                 obj_name='bottle_of_beer_15_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_beer/nfzzqc/usd/MJCF/nfzzqc_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfBeer16WithHand ---
@register_object
class BottleOfBeer16WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_beer_16_with_hand',
                 obj_name='bottle_of_beer_16_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_beer/dqfsgv/usd/MJCF/dqfsgv_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfBeer17WithHand ---
@register_object
class BottleOfBeer17WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_beer_17_with_hand',
                 obj_name='bottle_of_beer_17_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_beer/xpqnfz/usd/MJCF/xpqnfz_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfBeer18WithHand ---
@register_object
class BottleOfBeer18WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_beer_18_with_hand',
                 obj_name='bottle_of_beer_18_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_beer/jxhtdl/usd/MJCF/jxhtdl_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfBeer19WithHand ---
@register_object
class BottleOfBeer19WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_beer_19_with_hand',
                 obj_name='bottle_of_beer_19_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_beer/kqskmv/usd/MJCF/kqskmv_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfBeer20WithHand ---
@register_object
class BottleOfBeer20WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_beer_20_with_hand',
                 obj_name='bottle_of_beer_20_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_beer/zlmwyn/usd/MJCF/zlmwyn_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfBeer21WithHand ---
@register_object
class BottleOfBeer21WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_beer_21_with_hand',
                 obj_name='bottle_of_beer_21_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_beer/fgzjnb/usd/MJCF/fgzjnb_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfBeer22WithHand ---
@register_object
class BottleOfBeer22WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_beer_22_with_hand',
                 obj_name='bottle_of_beer_22_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_beer/rdnopv/usd/MJCF/rdnopv_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfBeer23WithHand ---
@register_object
class BottleOfBeer23WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_beer_23_with_hand',
                 obj_name='bottle_of_beer_23_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_beer/zbsxro/usd/MJCF/zbsxro_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None



# --- appended class BottleOfBeer25WithHand ---
@register_object
class BottleOfBeer25WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_beer_25_with_hand',
                 obj_name='bottle_of_beer_25_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_beer/hauvsg/usd/MJCF/hauvsg_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfBeer26WithHand ---
@register_object
class BottleOfBeer26WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_beer_26_with_hand',
                 obj_name='bottle_of_beer_26_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_beer/eicnxj/usd/MJCF/eicnxj_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfBeer27WithHand ---
@register_object
class BottleOfBeer27WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_beer_27_with_hand',
                 obj_name='bottle_of_beer_27_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_beer/jtgyoo/usd/MJCF/jtgyoo_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfBeer28WithHand ---
@register_object
class BottleOfBeer28WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_beer_28_with_hand',
                 obj_name='bottle_of_beer_28_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_beer/fcnrqt/usd/MJCF/fcnrqt_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfBeer29WithHand ---
@register_object
class BottleOfBeer29WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_beer_29_with_hand',
                 obj_name='bottle_of_beer_29_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_beer/mljzrl/usd/MJCF/mljzrl_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfBeer30WithHand ---
@register_object
class BottleOfBeer30WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_beer_30_with_hand',
                 obj_name='bottle_of_beer_30_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_beer/rbpakt/usd/MJCF/rbpakt_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfBeer31WithHand ---
@register_object
class BottleOfBeer31WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_beer_31_with_hand',
                 obj_name='bottle_of_beer_31_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_beer/saslsh/usd/MJCF/saslsh_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfEssentialOil1WithHand ---
@register_object
class BottleOfEssentialOil1WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_essential_oil_1_with_hand',
                 obj_name='bottle_of_essential_oil_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_essential_oil/eyyhld/usd/MJCF/eyyhld_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfEssentialOil2WithHand ---
# @register_object
# class BottleOfEssentialOil2WithHand(CustomObjects):
#     def __init__(self,
#                  name='bottle_of_essential_oil_2_with_hand',
#                  obj_name='bottle_of_essential_oil_2_with_hand',
#                  ):
#         custom_path = os.path.join(
#                 str(absolute_path), f"assets/new_objects_with_hand/bottle_of_essential_oil/xhoipk/usd/MJCF/xhoipk_with_hand.xml"
#             )
#         super().__init__(
#             custom_path=custom_path,
#             name=name,
#             obj_name=obj_name,
#         )
#         self.rotation = {
#             "x": (-np.pi / 2, -np.pi / 2),
#             "y": (-np.pi, -np.pi),
#             "z": (np.pi, np.pi),
#         }
#         self.rotation_axis = None


# --- appended class BottleOfEssentialOil3WithHand ---
@register_object
class BottleOfEssentialOil3WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_essential_oil_3_with_hand',
                 obj_name='bottle_of_essential_oil_3_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_essential_oil/wansva/usd/MJCF/wansva_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfEssentialOil4WithHand ---
@register_object
class BottleOfEssentialOil4WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_essential_oil_4_with_hand',
                 obj_name='bottle_of_essential_oil_4_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_essential_oil/xvqshn/usd/MJCF/xvqshn_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfEssentialOil5WithHand ---
@register_object
class BottleOfEssentialOil5WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_essential_oil_5_with_hand',
                 obj_name='bottle_of_essential_oil_5_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_essential_oil/yjxvpg/usd/MJCF/yjxvpg_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfSake1WithHand ---
@register_object
class BottleOfSake1WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_sake_1_with_hand',
                 obj_name='bottle_of_sake_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_sake/luadgb/usd/MJCF/luadgb_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfSake3WithHand ---
@register_object
class BottleOfSake3WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_sake_3_with_hand',
                 obj_name='bottle_of_sake_3_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_sake/swlykk/usd/MJCF/swlykk_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfSake4WithHand ---
@register_object
class BottleOfSake4WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_sake_4_with_hand',
                 obj_name='bottle_of_sake_4_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_sake/vfxfuj/usd/MJCF/vfxfuj_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfSake7WithHand ---
@register_object
class BottleOfSake7WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_sake_7_with_hand',
                 obj_name='bottle_of_sake_7_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_sake/rctijo/usd/MJCF/rctijo_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BeeswaxCandle1WithHand ---
@register_object
class BeeswaxCandle1WithHand(CustomObjects):
    def __init__(self,
                 name='beeswax_candle_1_with_hand',
                 obj_name='beeswax_candle_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/beeswax_candle/rptogj/usd/MJCF/rptogj_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BeeswaxCandle2WithHand ---
@register_object
class BeeswaxCandle2WithHand(CustomObjects):
    def __init__(self,
                 name='beeswax_candle_2_with_hand',
                 obj_name='beeswax_candle_2_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/beeswax_candle/nxewyk/usd/MJCF/nxewyk_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BeeswaxCandle3WithHand ---
@register_object
class BeeswaxCandle3WithHand(CustomObjects):
    def __init__(self,
                 name='beeswax_candle_3_with_hand',
                 obj_name='beeswax_candle_3_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/beeswax_candle/pfewit/usd/MJCF/pfewit_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BeeswaxCandle4WithHand ---
@register_object
class BeeswaxCandle4WithHand(CustomObjects):
    def __init__(self,
                 name='beeswax_candle_4_with_hand',
                 obj_name='beeswax_candle_4_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/beeswax_candle/oimgmh/usd/MJCF/oimgmh_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BeeswaxCandle5WithHand ---
@register_object
class BeeswaxCandle5WithHand(CustomObjects):
    def __init__(self,
                 name='beeswax_candle_5_with_hand',
                 obj_name='beeswax_candle_5_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/beeswax_candle/ouzkdj/usd/MJCF/ouzkdj_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BeeswaxCandle6WithHand ---
@register_object
class BeeswaxCandle6WithHand(CustomObjects):
    def __init__(self,
                 name='beeswax_candle_6_with_hand',
                 obj_name='beeswax_candle_6_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/beeswax_candle/aiuhyv/usd/MJCF/aiuhyv_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BeeswaxCandle7WithHand ---
@register_object
class BeeswaxCandle7WithHand(CustomObjects):
    def __init__(self,
                 name='beeswax_candle_7_with_hand',
                 obj_name='beeswax_candle_7_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/beeswax_candle/kxange/usd/MJCF/kxange_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BeeswaxCandle8WithHand ---
@register_object
class BeeswaxCandle8WithHand(CustomObjects):
    def __init__(self,
                 name='beeswax_candle_8_with_hand',
                 obj_name='beeswax_candle_8_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/beeswax_candle/nhdnje/usd/MJCF/nhdnje_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BoxedRouter1WithHand ---
# @register_object
# class BoxedRouter1WithHand(CustomObjects):
#     def __init__(self,
#                  name='boxed_router_1_with_hand',
#                  obj_name='boxed_router_1_with_hand',
#                  ):
#         custom_path = os.path.join(
#                 str(absolute_path), f"assets/new_objects_with_hand/boxed_router/dsgtpk/usd/MJCF/dsgtpk_with_hand.xml"
#             )
#         super().__init__(
#             custom_path=custom_path,
#             name=name,
#             obj_name=obj_name,
#         )
#         self.rotation = {
#             "x": (-np.pi / 2, -np.pi / 2),
#             "y": (-np.pi, -np.pi),
#             "z": (np.pi, np.pi),
#         }
#         self.rotation_axis = None


# --- appended class BottleOfFrosting1WithHand ---
@register_object
class BottleOfFrosting1WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_frosting_1_with_hand',
                 obj_name='bottle_of_frosting_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_frosting/eqdsmn/usd/MJCF/eqdsmn_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfLotion1WithHand ---
@register_object
class BottleOfLotion1WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_lotion_1_with_hand',
                 obj_name='bottle_of_lotion_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_lotion/tkryrh/usd/MJCF/tkryrh_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Cap1WithHand ---
@register_object
class Cap1WithHand(CustomObjects):
    def __init__(self,
                 name='cap_1_with_hand',
                 obj_name='cap_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/cap/hkvuxj/usd/MJCF/hkvuxj_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Cap4WithHand ---
@register_object
class Cap4WithHand(CustomObjects):
    def __init__(self,
                 name='cap_4_with_hand',
                 obj_name='cap_4_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/cap/amryfj/usd/MJCF/amryfj_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Cap5WithHand ---
@register_object
class Cap5WithHand(CustomObjects):
    def __init__(self,
                 name='cap_5_with_hand',
                 obj_name='cap_5_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/cap/xeswtq/usd/MJCF/xeswtq_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Cap7WithHand ---
@register_object
class Cap7WithHand(CustomObjects):
    def __init__(self,
                 name='cap_7_with_hand',
                 obj_name='cap_7_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/cap/zknitk/usd/MJCF/zknitk_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Cap11WithHand ---
@register_object
class Cap11WithHand(CustomObjects):
    def __init__(self,
                 name='cap_11_with_hand',
                 obj_name='cap_11_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/cap/nkjxbc/usd/MJCF/nkjxbc_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Cap16WithHand ---
@register_object
class Cap16WithHand(CustomObjects):
    def __init__(self,
                 name='cap_16_with_hand',
                 obj_name='cap_16_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/cap/vsvwig/usd/MJCF/vsvwig_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Cap17WithHand ---
@register_object
class Cap17WithHand(CustomObjects):
    def __init__(self,
                 name='cap_17_with_hand',
                 obj_name='cap_17_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/cap/sjsles/usd/MJCF/sjsles_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Cap18WithHand ---
@register_object
class Cap18WithHand(CustomObjects):
    def __init__(self,
                 name='cap_18_with_hand',
                 obj_name='cap_18_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/cap/pwsngg/usd/MJCF/pwsngg_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Cap19WithHand ---
@register_object
class Cap19WithHand(CustomObjects):
    def __init__(self,
                 name='cap_19_with_hand',
                 obj_name='cap_19_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/cap/tkwpyr/usd/MJCF/tkwpyr_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Cap20WithHand ---
@register_object
class Cap20WithHand(CustomObjects):
    def __init__(self,
                 name='cap_20_with_hand',
                 obj_name='cap_20_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/cap/vnpjfn/usd/MJCF/vnpjfn_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Cap22WithHand ---
@register_object
class Cap22WithHand(CustomObjects):
    def __init__(self,
                 name='cap_22_with_hand',
                 obj_name='cap_22_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/cap/dduopd/usd/MJCF/dduopd_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Cap23WithHand ---
@register_object
class Cap23WithHand(CustomObjects):
    def __init__(self,
                 name='cap_23_with_hand',
                 obj_name='cap_23_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/cap/dmzavi/usd/MJCF/dmzavi_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Cap24WithHand ---
@register_object
class Cap24WithHand(CustomObjects):
    def __init__(self,
                 name='cap_24_with_hand',
                 obj_name='cap_24_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/cap/ghwjwe/usd/MJCF/ghwjwe_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Cap25WithHand ---
@register_object
class Cap25WithHand(CustomObjects):
    def __init__(self,
                 name='cap_25_with_hand',
                 obj_name='cap_25_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/cap/ngionj/usd/MJCF/ngionj_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Cap29WithHand ---
@register_object
class Cap29WithHand(CustomObjects):
    def __init__(self,
                 name='cap_29_with_hand',
                 obj_name='cap_29_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/cap/fomiem/usd/MJCF/fomiem_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Cap31WithHand ---
@register_object
class Cap31WithHand(CustomObjects):
    def __init__(self,
                 name='cap_31_with_hand',
                 obj_name='cap_31_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/cap/arskxc/usd/MJCF/arskxc_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Cap33WithHand ---
@register_object
class Cap33WithHand(CustomObjects):
    def __init__(self,
                 name='cap_33_with_hand',
                 obj_name='cap_33_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/cap/qwrndi/usd/MJCF/qwrndi_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Cap35WithHand ---
@register_object
class Cap35WithHand(CustomObjects):
    def __init__(self,
                 name='cap_35_with_hand',
                 obj_name='cap_35_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/cap/gmdwwe/usd/MJCF/gmdwwe_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Cap36WithHand ---
@register_object
class Cap36WithHand(CustomObjects):
    def __init__(self,
                 name='cap_36_with_hand',
                 obj_name='cap_36_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/cap/qscujv/usd/MJCF/qscujv_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Cap37WithHand ---
@register_object
class Cap37WithHand(CustomObjects):
    def __init__(self,
                 name='cap_37_with_hand',
                 obj_name='cap_37_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/cap/tpknvf/usd/MJCF/tpknvf_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Cap38WithHand ---
@register_object
class Cap38WithHand(CustomObjects):
    def __init__(self,
                 name='cap_38_with_hand',
                 obj_name='cap_38_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/cap/ceizxn/usd/MJCF/ceizxn_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Cap39WithHand ---
@register_object
class Cap39WithHand(CustomObjects):
    def __init__(self,
                 name='cap_39_with_hand',
                 obj_name='cap_39_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/cap/rgtedj/usd/MJCF/rgtedj_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Cap40WithHand ---
@register_object
class Cap40WithHand(CustomObjects):
    def __init__(self,
                 name='cap_40_with_hand',
                 obj_name='cap_40_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/cap/hbafeb/usd/MJCF/hbafeb_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Cap41WithHand ---
@register_object
class Cap41WithHand(CustomObjects):
    def __init__(self,
                 name='cap_41_with_hand',
                 obj_name='cap_41_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/cap/yqvild/usd/MJCF/yqvild_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Cap44WithHand ---
@register_object
class Cap44WithHand(CustomObjects):
    def __init__(self,
                 name='cap_44_with_hand',
                 obj_name='cap_44_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/cap/gxkbcd/usd/MJCF/gxkbcd_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfSalsa2WithHand ---
@register_object
class BottleOfSalsa2WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_salsa_2_with_hand',
                 obj_name='bottle_of_salsa_2_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_salsa/mavope/usd/MJCF/mavope_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfSalsa3WithHand ---
@register_object
class BottleOfSalsa3WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_salsa_3_with_hand',
                 obj_name='bottle_of_salsa_3_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_salsa/nafwlf/usd/MJCF/nafwlf_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfMilk3WithHand ---
@register_object
class BottleOfMilk3WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_milk_3_with_hand',
                 obj_name='bottle_of_milk_3_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_milk/czblzn/usd/MJCF/czblzn_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfMilk4WithHand ---
@register_object
class BottleOfMilk4WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_milk_4_with_hand',
                 obj_name='bottle_of_milk_4_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_milk/utfsmp/usd/MJCF/utfsmp_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfMilk7WithHand ---
@register_object
class BottleOfMilk7WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_milk_7_with_hand',
                 obj_name='bottle_of_milk_7_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_milk/mrejrs/usd/MJCF/mrejrs_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfMilk8WithHand ---
@register_object
class BottleOfMilk8WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_milk_8_with_hand',
                 obj_name='bottle_of_milk_8_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_milk/ddvsgl/usd/MJCF/ddvsgl_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class GraduatedCylinder1WithHand ---
# @register_object
# class GraduatedCylinder1WithHand(CustomObjects):
#     def __init__(self,
#                  name='graduated_cylinder_1_with_hand',
#                  obj_name='graduated_cylinder_1_with_hand',
#                  ):
#         custom_path = os.path.join(
#                 str(absolute_path), f"assets/new_objects_with_hand/graduated_cylinder/egpkea/usd/MJCF/egpkea_with_hand.xml"
#             )
#         super().__init__(
#             custom_path=custom_path,
#             name=name,
#             obj_name=obj_name,
#         )
#         self.rotation = {
#             "x": (-np.pi / 2, -np.pi / 2),
#             "y": (-np.pi, -np.pi),
#             "z": (np.pi, np.pi),
#         }
#         self.rotation_axis = None


# # --- appended class CreamCheeseBox1WithHand ---
# @register_object
# class CreamCheeseBox1WithHand(CustomObjects):
#     def __init__(self,
#                  name='cream_cheese_box_1_with_hand',
#                  obj_name='cream_cheese_box_1_with_hand',
#                  ):
#         custom_path = os.path.join(
#                 str(absolute_path), f"assets/new_objects_with_hand/cream_cheese_box/hfclfn/usd/MJCF/hfclfn_with_hand.xml"
#             )
#         super().__init__(
#             custom_path=custom_path,
#             name=name,
#             obj_name=obj_name,
#         )
#         self.rotation = {
#             "x": (-np.pi / 2, -np.pi / 2),
#             "y": (-np.pi, -np.pi),
#             "z": (np.pi, np.pi),
#         }
#         self.rotation_axis = None


# --- appended class CelluloseTape1WithHand ---
@register_object
class CelluloseTape1WithHand(CustomObjects):
    def __init__(self,
                 name='cellulose_tape_1_with_hand',
                 obj_name='cellulose_tape_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/cellulose_tape/kavsnx/usd/MJCF/kavsnx_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class CelluloseTape2WithHand ---
@register_object
class CelluloseTape2WithHand(CustomObjects):
    def __init__(self,
                 name='cellulose_tape_2_with_hand',
                 obj_name='cellulose_tape_2_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/cellulose_tape/sklkyc/usd/MJCF/sklkyc_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class CelluloseTape3WithHand ---
@register_object
class CelluloseTape3WithHand(CustomObjects):
    def __init__(self,
                 name='cellulose_tape_3_with_hand',
                 obj_name='cellulose_tape_3_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/cellulose_tape/gchdhk/usd/MJCF/gchdhk_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfPaint1WithHand ---
@register_object
class BottleOfPaint1WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_paint_1_with_hand',
                 obj_name='bottle_of_paint_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_paint/volzrj/usd/MJCF/volzrj_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfChiliPepper1WithHand ---
@register_object
class BottleOfChiliPepper1WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_chili_pepper_1_with_hand',
                 obj_name='bottle_of_chili_pepper_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_chili_pepper/hjalqq/usd/MJCF/hjalqq_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class CannedFood1WithHand ---
@register_object
class CannedFood1WithHand(CustomObjects):
    def __init__(self,
                 name='canned_food_1_with_hand',
                 obj_name='canned_food_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/canned_food/byakrm/usd/MJCF/byakrm_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class CannedFood5WithHand ---
@register_object
class CannedFood5WithHand(CustomObjects):
    def __init__(self,
                 name='canned_food_5_with_hand',
                 obj_name='canned_food_5_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/canned_food/pkopdw/usd/MJCF/pkopdw_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class CannedFood6WithHand ---
@register_object
class CannedFood6WithHand(CustomObjects):
    def __init__(self,
                 name='canned_food_6_with_hand',
                 obj_name='canned_food_6_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/canned_food/acgdtc/usd/MJCF/acgdtc_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class CannedFood7WithHand ---
@register_object
class CannedFood7WithHand(CustomObjects):
    def __init__(self,
                 name='canned_food_7_with_hand',
                 obj_name='canned_food_7_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/canned_food/ycbspm/usd/MJCF/ycbspm_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class CannedFood8WithHand ---
@register_object
class CannedFood8WithHand(CustomObjects):
    def __init__(self,
                 name='canned_food_8_with_hand',
                 obj_name='canned_food_8_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/canned_food/qhgdys/usd/MJCF/qhgdys_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class CannedFood9WithHand ---
@register_object
class CannedFood9WithHand(CustomObjects):
    def __init__(self,
                 name='canned_food_9_with_hand',
                 obj_name='canned_food_9_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/canned_food/ycodks/usd/MJCF/ycodks_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Cupcake1WithHand ---
@register_object
class Cupcake1WithHand(CustomObjects):
    def __init__(self,
                 name='cupcake_1_with_hand',
                 obj_name='cupcake_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/cupcake/fabdnw/usd/MJCF/fabdnw_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Cupcake2WithHand ---
@register_object
class Cupcake2WithHand(CustomObjects):
    def __init__(self,
                 name='cupcake_2_with_hand',
                 obj_name='cupcake_2_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/cupcake/pfwrlq/usd/MJCF/pfwrlq_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Cupcake3WithHand ---
@register_object
class Cupcake3WithHand(CustomObjects):
    def __init__(self,
                 name='cupcake_3_with_hand',
                 obj_name='cupcake_3_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/cupcake/wdiezm/usd/MJCF/wdiezm_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Cupcake4WithHand ---
# @register_object
# class Cupcake4WithHand(CustomObjects):
#     def __init__(self,
#                  name='cupcake_4_with_hand',
#                  obj_name='cupcake_4_with_hand',
#                  ):
#         custom_path = os.path.join(
#                 str(absolute_path), f"assets/new_objects_with_hand/cupcake/rpadye/usd/MJCF/rpadye_with_hand.xml"
#             )
#         super().__init__(
#             custom_path=custom_path,
#             name=name,
#             obj_name=obj_name,
#         )
#         self.rotation = {
#             "x": (-np.pi / 2, -np.pi / 2),
#             "y": (-np.pi, -np.pi),
#             "z": (np.pi, np.pi),
#         }
#         self.rotation_axis = None


# --- appended class Cupcake5WithHand ---
# @register_object
# class Cupcake5WithHand(CustomObjects):
#     def __init__(self,
#                  name='cupcake_5_with_hand',
#                  obj_name='cupcake_5_with_hand',
#                  ):
#         custom_path = os.path.join(
#                 str(absolute_path), f"assets/new_objects_with_hand/cupcake/mbhweg/usd/MJCF/mbhweg_with_hand.xml"
#             )
#         super().__init__(
#             custom_path=custom_path,
#             name=name,
#             obj_name=obj_name,
#         )
#         self.rotation = {
#             "x": (-np.pi / 2, -np.pi / 2),
#             "y": (-np.pi, -np.pi),
#             "z": (np.pi, np.pi),
#         }
#         self.rotation_axis = None


# --- appended class Cupcake6WithHand ---
@register_object
class Cupcake6WithHand(CustomObjects):
    def __init__(self,
                 name='cupcake_6_with_hand',
                 obj_name='cupcake_6_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/cupcake/sutaow/usd/MJCF/sutaow_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Cupcake7WithHand ---
# @register_object
# class Cupcake7WithHand(CustomObjects):
#     def __init__(self,
#                  name='cupcake_7_with_hand',
#                  obj_name='cupcake_7_with_hand',
#                  ):
#         custom_path = os.path.join(
#                 str(absolute_path), f"assets/new_objects_with_hand/cupcake/outske/usd/MJCF/outske_with_hand.xml"
#             )
#         super().__init__(
#             custom_path=custom_path,
#             name=name,
#             obj_name=obj_name,
#         )
#         self.rotation = {
#             "x": (-np.pi / 2, -np.pi / 2),
#             "y": (-np.pi, -np.pi),
#             "z": (np.pi, np.pi),
#         }
#         self.rotation_axis = None


# --- appended class Cupcake8WithHand ---
@register_object
class Cupcake8WithHand(CustomObjects):
    def __init__(self,
                 name='cupcake_8_with_hand',
                 obj_name='cupcake_8_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/cupcake/hvyxpw/usd/MJCF/hvyxpw_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class GarlicBread1WithHand ---
@register_object
class GarlicBread1WithHand(CustomObjects):
    def __init__(self,
                 name='garlic_bread_1_with_hand',
                 obj_name='garlic_bread_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/garlic_bread/kjhxsq/usd/MJCF/kjhxsq_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class HalfButternutSquash1WithHand ---
# @register_object
# class HalfButternutSquash1WithHand(CustomObjects):
#     def __init__(self,
#                  name='half_butternut_squash_1_with_hand',
#                  obj_name='half_butternut_squash_1_with_hand',
#                  ):
#         custom_path = os.path.join(
#                 str(absolute_path), f"assets/new_objects_with_hand/half_butternut_squash/ttries/usd/MJCF/ttries_with_hand.xml"
#             )
#         super().__init__(
#             custom_path=custom_path,
#             name=name,
#             obj_name=obj_name,
#         )
#         self.rotation = {
#             "x": (-np.pi / 2, -np.pi / 2),
#             "y": (-np.pi, -np.pi),
#             "z": (np.pi, np.pi),
#         }
#         self.rotation_axis = None


# --- appended class HalfButternutSquash2WithHand ---
@register_object
class HalfButternutSquash2WithHand(CustomObjects):
    def __init__(self,
                 name='half_butternut_squash_2_with_hand',
                 obj_name='half_butternut_squash_2_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/half_butternut_squash/mfhfrq/usd/MJCF/mfhfrq_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfChocolateSauce1WithHand ---
@register_object
class BottleOfChocolateSauce1WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_chocolate_sauce_1_with_hand',
                 obj_name='bottle_of_chocolate_sauce_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_chocolate_sauce/tsyldw/usd/MJCF/tsyldw_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class HalfWhiteTurnip1WithHand ---
# @register_object
# class HalfWhiteTurnip1WithHand(CustomObjects):
#     def __init__(self,
#                  name='half_white_turnip_1_with_hand',
#                  obj_name='half_white_turnip_1_with_hand',
#                  ):
#         custom_path = os.path.join(
#                 str(absolute_path), f"assets/new_objects_with_hand/half_white_turnip/cqztci/usd/MJCF/cqztci_with_hand.xml"
#             )
#         super().__init__(
#             custom_path=custom_path,
#             name=name,
#             obj_name=obj_name,
#         )
#         self.rotation = {
#             "x": (-np.pi / 2, -np.pi / 2),
#             "y": (-np.pi, -np.pi),
#             "z": (np.pi, np.pi),
#         }
#         self.rotation_axis = None


# --- appended class HalfWhiteTurnip2WithHand ---
# @register_object
# class HalfWhiteTurnip2WithHand(CustomObjects):
#     def __init__(self,
#                  name='half_white_turnip_2_with_hand',
#                  obj_name='half_white_turnip_2_with_hand',
#                  ):
#         custom_path = os.path.join(
#                 str(absolute_path), f"assets/new_objects_with_hand/half_white_turnip/guvvjb/usd/MJCF/guvvjb_with_hand.xml"
#             )
#         super().__init__(
#             custom_path=custom_path,
#             name=name,
#             obj_name=obj_name,
#         )
#         self.rotation = {
#             "x": (-np.pi / 2, -np.pi / 2),
#             "y": (-np.pi, -np.pi),
#             "z": (np.pi, np.pi),
#         }
#         self.rotation_axis = None


# --- appended class Battery1WithHand ---
@register_object
class Battery1WithHand(CustomObjects):
    def __init__(self,
                 name='battery_1_with_hand',
                 obj_name='battery_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/battery/dcjyzg/usd/MJCF/dcjyzg_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class DriedApricot1WithHand ---
@register_object
class DriedApricot1WithHand(CustomObjects):
    def __init__(self,
                 name='dried_apricot_1_with_hand',
                 obj_name='dried_apricot_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/dried_apricot/fasedf/usd/MJCF/fasedf_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class HalfSwissCheese1WithHand ---
# @register_object
# class HalfSwissCheese1WithHand(CustomObjects):
#     def __init__(self,
#                  name='half_swiss_cheese_1_with_hand',
#                  obj_name='half_swiss_cheese_1_with_hand',
#                  ):
#         custom_path = os.path.join(
#                 str(absolute_path), f"assets/new_objects_with_hand/half_swiss_cheese/ppnaxx/usd/MJCF/ppnaxx_with_hand.xml"
#             )
#         super().__init__(
#             custom_path=custom_path,
#             name=name,
#             obj_name=obj_name,
#         )
#         self.rotation = {
#             "x": (-np.pi / 2, -np.pi / 2),
#             "y": (-np.pi, -np.pi),
#             "z": (np.pi, np.pi),
#         }
#         self.rotation_axis = None


# --- appended class HalfSwissCheese2WithHand ---
# @register_object
# class HalfSwissCheese2WithHand(CustomObjects):
#     def __init__(self,
#                  name='half_swiss_cheese_2_with_hand',
#                  obj_name='half_swiss_cheese_2_with_hand',
#                  ):
#         custom_path = os.path.join(
#                 str(absolute_path), f"assets/new_objects_with_hand/half_swiss_cheese/siurhp/usd/MJCF/siurhp_with_hand.xml"
#             )
#         super().__init__(
#             custom_path=custom_path,
#             name=name,
#             obj_name=obj_name,
#         )
#         self.rotation = {
#             "x": (-np.pi / 2, -np.pi / 2),
#             "y": (-np.pi, -np.pi),
#             "z": (np.pi, np.pi),
#         }
#         self.rotation_axis = None


# --- appended class GreenOnionStalk1WithHand ---
@register_object
class GreenOnionStalk1WithHand(CustomObjects):
    def __init__(self,
                 name='green_onion_stalk_1_with_hand',
                 obj_name='green_onion_stalk_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/green_onion_stalk/lgsfgs/usd/MJCF/lgsfgs_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class GreenOnionStalk2WithHand ---
@register_object
class GreenOnionStalk2WithHand(CustomObjects):
    def __init__(self,
                 name='green_onion_stalk_2_with_hand',
                 obj_name='green_onion_stalk_2_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/green_onion_stalk/ldaffa/usd/MJCF/ldaffa_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class GreenOnionStalk3WithHand ---
@register_object
class GreenOnionStalk3WithHand(CustomObjects):
    def __init__(self,
                 name='green_onion_stalk_3_with_hand',
                 obj_name='green_onion_stalk_3_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/green_onion_stalk/kfaasd/usd/MJCF/kfaasd_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfPoppySeeds1WithHand ---
@register_object
class BottleOfPoppySeeds1WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_poppy_seeds_1_with_hand',
                 obj_name='bottle_of_poppy_seeds_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_poppy_seeds/xdtrgi/usd/MJCF/xdtrgi_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class GranulatedSugarSack1WithHand ---
# @register_object
# class GranulatedSugarSack1WithHand(CustomObjects):
#     def __init__(self,
#                  name='granulated_sugar_sack_1_with_hand',
#                  obj_name='granulated_sugar_sack_1_with_hand',
#                  ):
#         custom_path = os.path.join(
#                 str(absolute_path), f"assets/new_objects_with_hand/granulated_sugar_sack/oywwzz/usd/MJCF/oywwzz_with_hand.xml"
#             )
#         super().__init__(
#             custom_path=custom_path,
#             name=name,
#             obj_name=obj_name,
#         )
#         self.rotation = {
#             "x": (-np.pi / 2, -np.pi / 2),
#             "y": (-np.pi, -np.pi),
#             "z": (np.pi, np.pi),
#         }
#         self.rotation_axis = None


# --- appended class CocoaPowderJar1WithHand ---
# @register_object
# class CocoaPowderJar1WithHand(CustomObjects):
#     def __init__(self,
#                  name='cocoa_powder_jar_1_with_hand',
#                  obj_name='cocoa_powder_jar_1_with_hand',
#                  ):
#         custom_path = os.path.join(
#                 str(absolute_path), f"assets/new_objects_with_hand/cocoa_powder_jar/cjmtvq/usd/MJCF/cjmtvq_with_hand.xml"
#             )
#         super().__init__(
#             custom_path=custom_path,
#             name=name,
#             obj_name=obj_name,
#         )
#         self.rotation = {
#             "x": (-np.pi / 2, -np.pi / 2),
#             "y": (-np.pi, -np.pi),
#             "z": (np.pi, np.pi),
#         }
#         self.rotation_axis = None


# --- appended class ColoredPencil1WithHand ---
@register_object
class ColoredPencil1WithHand(CustomObjects):
    def __init__(self,
                 name='colored_pencil_1_with_hand',
                 obj_name='colored_pencil_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/colored_pencil/acumgp/usd/MJCF/acumgp_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class ColoredPencil2WithHand ---
@register_object
class ColoredPencil2WithHand(CustomObjects):
    def __init__(self,
                 name='colored_pencil_2_with_hand',
                 obj_name='colored_pencil_2_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/colored_pencil/wifbfs/usd/MJCF/wifbfs_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class ColoredPencil3WithHand ---
@register_object
class ColoredPencil3WithHand(CustomObjects):
    def __init__(self,
                 name='colored_pencil_3_with_hand',
                 obj_name='colored_pencil_3_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/colored_pencil/egvqng/usd/MJCF/egvqng_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class ColoredPencil4WithHand ---
@register_object
class ColoredPencil4WithHand(CustomObjects):
    def __init__(self,
                 name='colored_pencil_4_with_hand',
                 obj_name='colored_pencil_4_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/colored_pencil/vdpmhz/usd/MJCF/vdpmhz_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class ColoredPencil5WithHand ---
@register_object
class ColoredPencil5WithHand(CustomObjects):
    def __init__(self,
                 name='colored_pencil_5_with_hand',
                 obj_name='colored_pencil_5_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/colored_pencil/qxeydw/usd/MJCF/qxeydw_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class ColoredPencil6WithHand ---
@register_object
class ColoredPencil6WithHand(CustomObjects):
    def __init__(self,
                 name='colored_pencil_6_with_hand',
                 obj_name='colored_pencil_6_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/colored_pencil/bkdqwb/usd/MJCF/bkdqwb_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class ColoredPencil7WithHand ---
@register_object
class ColoredPencil7WithHand(CustomObjects):
    def __init__(self,
                 name='colored_pencil_7_with_hand',
                 obj_name='colored_pencil_7_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/colored_pencil/zisrpq/usd/MJCF/zisrpq_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class ColoredPencil8WithHand ---
# @register_object
# class ColoredPencil8WithHand(CustomObjects):
#     def __init__(self,
#                  name='colored_pencil_8_with_hand',
#                  obj_name='colored_pencil_8_with_hand',
#                  ):
#         custom_path = os.path.join(
#                 str(absolute_path), f"assets/new_objects_with_hand/colored_pencil/tzadtj/usd/MJCF/tzadtj_with_hand.xml"
#             )
#         super().__init__(
#             custom_path=custom_path,
#             name=name,
#             obj_name=obj_name,
#         )
#         self.rotation = {
#             "x": (-np.pi / 2, -np.pi / 2),
#             "y": (-np.pi, -np.pi),
#             "z": (np.pi, np.pi),
#         }
#         self.rotation_axis = None


# --- appended class ColoredPencil9WithHand ---
@register_object
class ColoredPencil9WithHand(CustomObjects):
    def __init__(self,
                 name='colored_pencil_9_with_hand',
                 obj_name='colored_pencil_9_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/colored_pencil/bnsqcn/usd/MJCF/bnsqcn_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class ColoredPencil10WithHand ---
@register_object
class ColoredPencil10WithHand(CustomObjects):
    def __init__(self,
                 name='colored_pencil_10_with_hand',
                 obj_name='colored_pencil_10_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/colored_pencil/qwficr/usd/MJCF/qwficr_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class ColoredPencil11WithHand ---
# @register_object
# class ColoredPencil11WithHand(CustomObjects):
#     def __init__(self,
#                  name='colored_pencil_11_with_hand',
#                  obj_name='colored_pencil_11_with_hand',
#                  ):
#         custom_path = os.path.join(
#                 str(absolute_path), f"assets/new_objects_with_hand/colored_pencil/kjwoqm/usd/MJCF/kjwoqm_with_hand.xml"
#             )
#         super().__init__(
#             custom_path=custom_path,
#             name=name,
#             obj_name=obj_name,
#         )
#         self.rotation = {
#             "x": (-np.pi / 2, -np.pi / 2),
#             "y": (-np.pi, -np.pi),
#             "z": (np.pi, np.pi),
#         }
#         self.rotation_axis = None


# --- appended class ColoredPencil12WithHand ---
# @register_object
# class ColoredPencil12WithHand(CustomObjects):
#     def __init__(self,
#                  name='colored_pencil_12_with_hand',
#                  obj_name='colored_pencil_12_with_hand',
#                  ):
#         custom_path = os.path.join(
#                 str(absolute_path), f"assets/new_objects_with_hand/colored_pencil/wmjjvo/usd/MJCF/wmjjvo_with_hand.xml"
#             )
#         super().__init__(
#             custom_path=custom_path,
#             name=name,
#             obj_name=obj_name,
#         )
#         self.rotation = {
#             "x": (-np.pi / 2, -np.pi / 2),
#             "y": (-np.pi, -np.pi),
#             "z": (np.pi, np.pi),
#         }
#         self.rotation_axis = None


# --- appended class ColoredPencil13WithHand ---
@register_object
class ColoredPencil13WithHand(CustomObjects):
    def __init__(self,
                 name='colored_pencil_13_with_hand',
                 obj_name='colored_pencil_13_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/colored_pencil/kadvlg/usd/MJCF/kadvlg_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class ColoredPencil14WithHand ---
@register_object
class ColoredPencil14WithHand(CustomObjects):
    def __init__(self,
                 name='colored_pencil_14_with_hand',
                 obj_name='colored_pencil_14_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/colored_pencil/jdqvdl/usd/MJCF/jdqvdl_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class ColoredPencil15WithHand ---
@register_object
class ColoredPencil15WithHand(CustomObjects):
    def __init__(self,
                 name='colored_pencil_15_with_hand',
                 obj_name='colored_pencil_15_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/colored_pencil/jnccuz/usd/MJCF/jnccuz_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class ColoredPencil16WithHand ---
@register_object
class ColoredPencil16WithHand(CustomObjects):
    def __init__(self,
                 name='colored_pencil_16_with_hand',
                 obj_name='colored_pencil_16_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/colored_pencil/vtbwvo/usd/MJCF/vtbwvo_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class ColoredPencil17WithHand ---
@register_object
class ColoredPencil17WithHand(CustomObjects):
    def __init__(self,
                 name='colored_pencil_17_with_hand',
                 obj_name='colored_pencil_17_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/colored_pencil/kgmapz/usd/MJCF/kgmapz_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class ColoredPencil18WithHand ---
@register_object
class ColoredPencil18WithHand(CustomObjects):
    def __init__(self,
                 name='colored_pencil_18_with_hand',
                 obj_name='colored_pencil_18_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/colored_pencil/nssris/usd/MJCF/nssris_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class ColoredPencil19WithHand ---
@register_object
class ColoredPencil19WithHand(CustomObjects):
    def __init__(self,
                 name='colored_pencil_19_with_hand',
                 obj_name='colored_pencil_19_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/colored_pencil/deuvcx/usd/MJCF/deuvcx_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class ColoredPencil20WithHand ---
@register_object
class ColoredPencil20WithHand(CustomObjects):
    def __init__(self,
                 name='colored_pencil_20_with_hand',
                 obj_name='colored_pencil_20_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/colored_pencil/qrxemk/usd/MJCF/qrxemk_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfSunscreen1WithHand ---
@register_object
class BottleOfSunscreen1WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_sunscreen_1_with_hand',
                 obj_name='bottle_of_sunscreen_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_sunscreen/prlrwi/usd/MJCF/prlrwi_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BoxOfSanitaryNapkins1WithHand ---
@register_object
class BoxOfSanitaryNapkins1WithHand(CustomObjects):
    def __init__(self,
                 name='box_of_sanitary_napkins_1_with_hand',
                 obj_name='box_of_sanitary_napkins_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/box_of_sanitary_napkins/cmnpuv/usd/MJCF/cmnpuv_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BoxOfSanitaryNapkins2WithHand ---
# @register_object
# class BoxOfSanitaryNapkins2WithHand(CustomObjects):
#     def __init__(self,
#                  name='box_of_sanitary_napkins_2_with_hand',
#                  obj_name='box_of_sanitary_napkins_2_with_hand',
#                  ):
#         custom_path = os.path.join(
#                 str(absolute_path), f"assets/new_objects_with_hand/box_of_sanitary_napkins/acaivd/usd/MJCF/acaivd_with_hand.xml"
#             )
#         super().__init__(
#             custom_path=custom_path,
#             name=name,
#             obj_name=obj_name,
#         )
#         self.rotation = {
#             "x": (-np.pi / 2, -np.pi / 2),
#             "y": (-np.pi, -np.pi),
#             "z": (np.pi, np.pi),
#         }
#         self.rotation_axis = None


# --- appended class BoxOfSanitaryNapkins3WithHand ---
@register_object
class BoxOfSanitaryNapkins3WithHand(CustomObjects):
    def __init__(self,
                 name='box_of_sanitary_napkins_3_with_hand',
                 obj_name='box_of_sanitary_napkins_3_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/box_of_sanitary_napkins/mxdefq/usd/MJCF/mxdefq_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BoxOfSanitaryNapkins4WithHand ---
@register_object
class BoxOfSanitaryNapkins4WithHand(CustomObjects):
    def __init__(self,
                 name='box_of_sanitary_napkins_4_with_hand',
                 obj_name='box_of_sanitary_napkins_4_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/box_of_sanitary_napkins/skltgp/usd/MJCF/skltgp_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BoxOfSanitaryNapkins5WithHand ---
@register_object
class BoxOfSanitaryNapkins5WithHand(CustomObjects):
    def __init__(self,
                 name='box_of_sanitary_napkins_5_with_hand',
                 obj_name='box_of_sanitary_napkins_5_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/box_of_sanitary_napkins/arqcyu/usd/MJCF/arqcyu_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BoxOfSanitaryNapkins6WithHand ---
@register_object
class BoxOfSanitaryNapkins6WithHand(CustomObjects):
    def __init__(self,
                 name='box_of_sanitary_napkins_6_with_hand',
                 obj_name='box_of_sanitary_napkins_6_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/box_of_sanitary_napkins/humkqw/usd/MJCF/humkqw_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BoxOfSanitaryNapkins7WithHand ---
@register_object
class BoxOfSanitaryNapkins7WithHand(CustomObjects):
    def __init__(self,
                 name='box_of_sanitary_napkins_7_with_hand',
                 obj_name='box_of_sanitary_napkins_7_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/box_of_sanitary_napkins/tkrzkb/usd/MJCF/tkrzkb_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfCookingOil1WithHand ---
@register_object
class BottleOfCookingOil1WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_cooking_oil_1_with_hand',
                 obj_name='bottle_of_cooking_oil_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_cooking_oil/ywrkyg/usd/MJCF/ywrkyg_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class CookieCutter1WithHand ---
@register_object
class CookieCutter1WithHand(CustomObjects):
    def __init__(self,
                 name='cookie_cutter_1_with_hand',
                 obj_name='cookie_cutter_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/cookie_cutter/fvxiun/usd/MJCF/fvxiun_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class CookieCutter2WithHand ---
@register_object
class CookieCutter2WithHand(CustomObjects):
    def __init__(self,
                 name='cookie_cutter_2_with_hand',
                 obj_name='cookie_cutter_2_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/cookie_cutter/lqrfzo/usd/MJCF/lqrfzo_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class CookieCutter3WithHand ---
@register_object
class CookieCutter3WithHand(CustomObjects):
    def __init__(self,
                 name='cookie_cutter_3_with_hand',
                 obj_name='cookie_cutter_3_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/cookie_cutter/jpscvj/usd/MJCF/jpscvj_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class HalfLemon1WithHand ---
# @register_object
# class HalfLemon1WithHand(CustomObjects):
#     def __init__(self,
#                  name='half_lemon_1_with_hand',
#                  obj_name='half_lemon_1_with_hand',
#                  ):
#         custom_path = os.path.join(
#                 str(absolute_path), f"assets/new_objects_with_hand/half_lemon/wouoym/usd/MJCF/wouoym_with_hand.xml"
#             )
#         super().__init__(
#             custom_path=custom_path,
#             name=name,
#             obj_name=obj_name,
#         )
#         self.rotation = {
#             "x": (-np.pi / 2, -np.pi / 2),
#             "y": (-np.pi, -np.pi),
#             "z": (np.pi, np.pi),
#         }
#         self.rotation_axis = None


# --- appended class BottleOfColdCream1WithHand ---
@register_object
class BottleOfColdCream1WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_cold_cream_1_with_hand',
                 obj_name='bottle_of_cold_cream_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_cold_cream/lyzvuk/usd/MJCF/lyzvuk_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Drill1WithHand ---
@register_object
class Drill1WithHand(CustomObjects):
    def __init__(self,
                 name='drill_1_with_hand',
                 obj_name='drill_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/drill/nzgmza/usd/MJCF/nzgmza_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfBabyOil1WithHand ---
@register_object
class BottleOfBabyOil1WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_baby_oil_1_with_hand',
                 obj_name='bottle_of_baby_oil_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_baby_oil/xpdlrr/usd/MJCF/xpdlrr_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Chili2WithHand ---
@register_object
class Chili2WithHand(CustomObjects):
    def __init__(self,
                 name='chili_2_with_hand',
                 obj_name='chili_2_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/chili/agecro/usd/MJCF/agecro_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Chili3WithHand ---
@register_object
class Chili3WithHand(CustomObjects):
    def __init__(self,
                 name='chili_3_with_hand',
                 obj_name='chili_3_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/chili/rafkbt/usd/MJCF/rafkbt_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Chili4WithHand ---
@register_object
class Chili4WithHand(CustomObjects):
    def __init__(self,
                 name='chili_4_with_hand',
                 obj_name='chili_4_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/chili/pbbkpz/usd/MJCF/pbbkpz_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class AllenWrench1WithHand ---
@register_object
class AllenWrench1WithHand(CustomObjects):
    def __init__(self,
                 name='allen_wrench_1_with_hand',
                 obj_name='allen_wrench_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/allen_wrench/neqlcn/usd/MJCF/neqlcn_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BagOfYeast1WithHand ---
@register_object
class BagOfYeast1WithHand(CustomObjects):
    def __init__(self,
                 name='bag_of_yeast_1_with_hand',
                 obj_name='bag_of_yeast_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bag_of_yeast/ibvtik/usd/MJCF/ibvtik_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfLimeJuice1WithHand ---
@register_object
class BottleOfLimeJuice1WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_lime_juice_1_with_hand',
                 obj_name='bottle_of_lime_juice_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_lime_juice/ouuhaa/usd/MJCF/ouuhaa_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfPaprika1WithHand ---
@register_object
class BottleOfPaprika1WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_paprika_1_with_hand',
                 obj_name='bottle_of_paprika_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_paprika/nrdgrp/usd/MJCF/nrdgrp_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class CinnamonStick1WithHand ---
@register_object
class CinnamonStick1WithHand(CustomObjects):
    def __init__(self,
                 name='cinnamon_stick_1_with_hand',
                 obj_name='cinnamon_stick_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/cinnamon_stick/qsqvgk/usd/MJCF/qsqvgk_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class CinnamonStick2WithHand ---
# @register_object
# class CinnamonStick2WithHand(CustomObjects):
#     def __init__(self,
#                  name='cinnamon_stick_2_with_hand',
#                  obj_name='cinnamon_stick_2_with_hand',
#                  ):
#         custom_path = os.path.join(
#                 str(absolute_path), f"assets/new_objects_with_hand/cinnamon_stick/cdkjfo/usd/MJCF/cdkjfo_with_hand.xml"
#             )
#         super().__init__(
#             custom_path=custom_path,
#             name=name,
#             obj_name=obj_name,
#         )
#         self.rotation = {
#             "x": (-np.pi / 2, -np.pi / 2),
#             "y": (-np.pi, -np.pi),
#             "z": (np.pi, np.pi),
#         }
#         self.rotation_axis = None


# --- appended class CinnamonStick3WithHand ---
@register_object
class CinnamonStick3WithHand(CustomObjects):
    def __init__(self,
                 name='cinnamon_stick_3_with_hand',
                 obj_name='cinnamon_stick_3_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/cinnamon_stick/smfuqz/usd/MJCF/smfuqz_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class CinnamonStick4WithHand ---
@register_object
class CinnamonStick4WithHand(CustomObjects):
    def __init__(self,
                 name='cinnamon_stick_4_with_hand',
                 obj_name='cinnamon_stick_4_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/cinnamon_stick/qxpzdm/usd/MJCF/qxpzdm_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class CinnamonStick5WithHand ---
@register_object
class CinnamonStick5WithHand(CustomObjects):
    def __init__(self,
                 name='cinnamon_stick_5_with_hand',
                 obj_name='cinnamon_stick_5_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/cinnamon_stick/hjhcpm/usd/MJCF/hjhcpm_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class CinnamonStick6WithHand ---
# @register_object
# class CinnamonStick6WithHand(CustomObjects):
#     def __init__(self,
#                  name='cinnamon_stick_6_with_hand',
#                  obj_name='cinnamon_stick_6_with_hand',
#                  ):
#         custom_path = os.path.join(
#                 str(absolute_path), f"assets/new_objects_with_hand/cinnamon_stick/kdaxdy/usd/MJCF/kdaxdy_with_hand.xml"
#             )
#         super().__init__(
#             custom_path=custom_path,
#             name=name,
#             obj_name=obj_name,
#         )
#         self.rotation = {
#             "x": (-np.pi / 2, -np.pi / 2),
#             "y": (-np.pi, -np.pi),
#             "z": (np.pi, np.pi),
#         }
#         self.rotation_axis = None


# --- appended class CinnamonStick7WithHand ---
@register_object
class CinnamonStick7WithHand(CustomObjects):
    def __init__(self,
                 name='cinnamon_stick_7_with_hand',
                 obj_name='cinnamon_stick_7_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/cinnamon_stick/qmlyim/usd/MJCF/qmlyim_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class CinnamonStick8WithHand ---
@register_object
class CinnamonStick8WithHand(CustomObjects):
    def __init__(self,
                 name='cinnamon_stick_8_with_hand',
                 obj_name='cinnamon_stick_8_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/cinnamon_stick/bmbjdf/usd/MJCF/bmbjdf_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class DetergentBottle1WithHand ---
# @register_object
# class DetergentBottle1WithHand(CustomObjects):
#     def __init__(self,
#                  name='detergent_bottle_1_with_hand',
#                  obj_name='detergent_bottle_1_with_hand',
#                  ):
#         custom_path = os.path.join(
#                 str(absolute_path), f"assets/new_objects_with_hand/detergent_bottle/yufawg/usd/MJCF/yufawg_with_hand.xml"
#             )
#         super().__init__(
#             custom_path=custom_path,
#             name=name,
#             obj_name=obj_name,
#         )
#         self.rotation = {
#             "x": (-np.pi / 2, -np.pi / 2),
#             "y": (-np.pi, -np.pi),
#             "z": (np.pi, np.pi),
#         }
#         self.rotation_axis = None


# --- appended class HalfShiitake1WithHand ---
@register_object
class HalfShiitake1WithHand(CustomObjects):
    def __init__(self,
                 name='half_shiitake_1_with_hand',
                 obj_name='half_shiitake_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/half_shiitake/zuskah/usd/MJCF/zuskah_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class HalfShiitake2WithHand ---
@register_object
class HalfShiitake2WithHand(CustomObjects):
    def __init__(self,
                 name='half_shiitake_2_with_hand',
                 obj_name='half_shiitake_2_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/half_shiitake/wkcotv/usd/MJCF/wkcotv_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class CookieStick1WithHand ---
@register_object
class CookieStick1WithHand(CustomObjects):
    def __init__(self,
                 name='cookie_stick_1_with_hand',
                 obj_name='cookie_stick_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/cookie_stick/zlhayf/usd/MJCF/zlhayf_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class CandleHolder1WithHand ---
@register_object
class CandleHolder1WithHand(CustomObjects):
    def __init__(self,
                 name='candle_holder_1_with_hand',
                 obj_name='candle_holder_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/candle_holder/wiufnv/usd/MJCF/wiufnv_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Biscuit1WithHand ---
@register_object
class Biscuit1WithHand(CustomObjects):
    def __init__(self,
                 name='biscuit_1_with_hand',
                 obj_name='biscuit_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/biscuit/ukcwqw/usd/MJCF/ukcwqw_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BoxOfCereal11WithHand ---
@register_object
class BoxOfCereal11WithHand(CustomObjects):
    def __init__(self,
                 name='box_of_cereal_11_with_hand',
                 obj_name='box_of_cereal_11_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/box_of_cereal/yorray/usd/MJCF/yorray_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BoxOfCookies11WithHand ---
@register_object
class BoxOfCookies11WithHand(CustomObjects):
    def __init__(self,
                 name='box_of_cookies_11_with_hand',
                 obj_name='box_of_cookies_11_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/box_of_cookies/qkzrdd/usd/MJCF/qkzrdd_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfLemonJuice1WithHand ---
@register_object
class BottleOfLemonJuice1WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_lemon_juice_1_with_hand',
                 obj_name='bottle_of_lemon_juice_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_lemon_juice/vsjter/usd/MJCF/vsjter_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfWater2WithHand ---
@register_object
class BottleOfWater2WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_water_2_with_hand',
                 obj_name='bottle_of_water_2_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_water/emquat/usd/MJCF/emquat_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfWater5WithHand ---
@register_object
class BottleOfWater5WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_water_5_with_hand',
                 obj_name='bottle_of_water_5_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_water/cytqio/usd/MJCF/cytqio_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfWater8WithHand ---
@register_object
class BottleOfWater8WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_water_8_with_hand',
                 obj_name='bottle_of_water_8_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_water/rrkhva/usd/MJCF/rrkhva_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfWater10WithHand ---
@register_object
class BottleOfWater10WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_water_10_with_hand',
                 obj_name='bottle_of_water_10_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_water/atvnqy/usd/MJCF/atvnqy_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfWater11WithHand ---
@register_object
class BottleOfWater11WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_water_11_with_hand',
                 obj_name='bottle_of_water_11_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_water/suytyi/usd/MJCF/suytyi_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfWater12WithHand ---
@register_object
class BottleOfWater12WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_water_12_with_hand',
                 obj_name='bottle_of_water_12_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_water/qaceen/usd/MJCF/qaceen_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfWater15WithHand ---
@register_object
class BottleOfWater15WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_water_15_with_hand',
                 obj_name='bottle_of_water_15_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_water/rmtdxh/usd/MJCF/rmtdxh_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfPop1WithHand ---
@register_object
class BottleOfPop1WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_pop_1_with_hand',
                 obj_name='bottle_of_pop_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_pop/mhzttm/usd/MJCF/mhzttm_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfPop2WithHand ---
@register_object
class BottleOfPop2WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_pop_2_with_hand',
                 obj_name='bottle_of_pop_2_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_pop/ribekf/usd/MJCF/ribekf_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfPop3WithHand ---
@register_object
class BottleOfPop3WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_pop_3_with_hand',
                 obj_name='bottle_of_pop_3_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_pop/uwmchl/usd/MJCF/uwmchl_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfPop4WithHand ---
@register_object
class BottleOfPop4WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_pop_4_with_hand',
                 obj_name='bottle_of_pop_4_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_pop/xvxcvv/usd/MJCF/xvxcvv_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfPop5WithHand ---
@register_object
class BottleOfPop5WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_pop_5_with_hand',
                 obj_name='bottle_of_pop_5_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_pop/bqretx/usd/MJCF/bqretx_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfPop6WithHand ---
@register_object
class BottleOfPop6WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_pop_6_with_hand',
                 obj_name='bottle_of_pop_6_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_pop/jnoksl/usd/MJCF/jnoksl_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfPop7WithHand ---
@register_object
class BottleOfPop7WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_pop_7_with_hand',
                 obj_name='bottle_of_pop_7_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_pop/zxambx/usd/MJCF/zxambx_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfPop8WithHand ---
@register_object
class BottleOfPop8WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_pop_8_with_hand',
                 obj_name='bottle_of_pop_8_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_pop/tfvmik/usd/MJCF/tfvmik_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfPop9WithHand ---
@register_object
class BottleOfPop9WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_pop_9_with_hand',
                 obj_name='bottle_of_pop_9_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_pop/vfjhav/usd/MJCF/vfjhav_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfPop10WithHand ---
@register_object
class BottleOfPop10WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_pop_10_with_hand',
                 obj_name='bottle_of_pop_10_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_pop/sevoto/usd/MJCF/sevoto_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfPop11WithHand ---
@register_object
class BottleOfPop11WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_pop_11_with_hand',
                 obj_name='bottle_of_pop_11_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_pop/ubazru/usd/MJCF/ubazru_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfPop12WithHand ---
@register_object
class BottleOfPop12WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_pop_12_with_hand',
                 obj_name='bottle_of_pop_12_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_pop/nyupqh/usd/MJCF/nyupqh_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfPop13WithHand ---
@register_object
class BottleOfPop13WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_pop_13_with_hand',
                 obj_name='bottle_of_pop_13_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_pop/rhclfg/usd/MJCF/rhclfg_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfPop15WithHand ---
@register_object
class BottleOfPop15WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_pop_15_with_hand',
                 obj_name='bottle_of_pop_15_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_pop/nepfjl/usd/MJCF/nepfjl_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfPop16WithHand ---
@register_object
class BottleOfPop16WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_pop_16_with_hand',
                 obj_name='bottle_of_pop_16_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_pop/drqbiy/usd/MJCF/drqbiy_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfPop17WithHand ---
@register_object
class BottleOfPop17WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_pop_17_with_hand',
                 obj_name='bottle_of_pop_17_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_pop/gkwdyt/usd/MJCF/gkwdyt_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfPop18WithHand ---
@register_object
class BottleOfPop18WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_pop_18_with_hand',
                 obj_name='bottle_of_pop_18_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_pop/xoldze/usd/MJCF/xoldze_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfPop19WithHand ---
@register_object
class BottleOfPop19WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_pop_19_with_hand',
                 obj_name='bottle_of_pop_19_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_pop/oghrnk/usd/MJCF/oghrnk_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfPop20WithHand ---
@register_object
class BottleOfPop20WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_pop_20_with_hand',
                 obj_name='bottle_of_pop_20_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_pop/msmlud/usd/MJCF/msmlud_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfPop21WithHand ---
@register_object
class BottleOfPop21WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_pop_21_with_hand',
                 obj_name='bottle_of_pop_21_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_pop/haoywb/usd/MJCF/haoywb_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfPop22WithHand ---
@register_object
class BottleOfPop22WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_pop_22_with_hand',
                 obj_name='bottle_of_pop_22_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_pop/eyazzi/usd/MJCF/eyazzi_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfPop24WithHand ---
@register_object
class BottleOfPop24WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_pop_24_with_hand',
                 obj_name='bottle_of_pop_24_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_pop/pvabxf/usd/MJCF/pvabxf_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfPop26WithHand ---
@register_object
class BottleOfPop26WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_pop_26_with_hand',
                 obj_name='bottle_of_pop_26_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_pop/zsisxf/usd/MJCF/zsisxf_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfPop27WithHand ---
@register_object
class BottleOfPop27WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_pop_27_with_hand',
                 obj_name='bottle_of_pop_27_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_pop/wuuoes/usd/MJCF/wuuoes_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfPop28WithHand ---
@register_object
class BottleOfPop28WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_pop_28_with_hand',
                 obj_name='bottle_of_pop_28_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_pop/mdznsn/usd/MJCF/mdznsn_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfPop29WithHand ---
@register_object
class BottleOfPop29WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_pop_29_with_hand',
                 obj_name='bottle_of_pop_29_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_pop/hjrwqb/usd/MJCF/hjrwqb_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfPop30WithHand ---
@register_object
class BottleOfPop30WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_pop_30_with_hand',
                 obj_name='bottle_of_pop_30_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_pop/iynssk/usd/MJCF/iynssk_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfPop32WithHand ---
@register_object
class BottleOfPop32WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_pop_32_with_hand',
                 obj_name='bottle_of_pop_32_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_pop/wmqhul/usd/MJCF/wmqhul_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfPop33WithHand ---
@register_object
class BottleOfPop33WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_pop_33_with_hand',
                 obj_name='bottle_of_pop_33_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_pop/pfjzkn/usd/MJCF/pfjzkn_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfPop34WithHand ---
@register_object
class BottleOfPop34WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_pop_34_with_hand',
                 obj_name='bottle_of_pop_34_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_pop/pyrics/usd/MJCF/pyrics_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfPop35WithHand ---
@register_object
class BottleOfPop35WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_pop_35_with_hand',
                 obj_name='bottle_of_pop_35_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_pop/cmqubs/usd/MJCF/cmqubs_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfPop36WithHand ---
@register_object
class BottleOfPop36WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_pop_36_with_hand',
                 obj_name='bottle_of_pop_36_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_pop/wrgmdt/usd/MJCF/wrgmdt_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfPop37WithHand ---
@register_object
class BottleOfPop37WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_pop_37_with_hand',
                 obj_name='bottle_of_pop_37_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_pop/oeipjl/usd/MJCF/oeipjl_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfPop38WithHand ---
@register_object
class BottleOfPop38WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_pop_38_with_hand',
                 obj_name='bottle_of_pop_38_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_pop/twtsry/usd/MJCF/twtsry_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfPop39WithHand ---
@register_object
class BottleOfPop39WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_pop_39_with_hand',
                 obj_name='bottle_of_pop_39_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_pop/uwdeok/usd/MJCF/uwdeok_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfPop40WithHand ---
@register_object
class BottleOfPop40WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_pop_40_with_hand',
                 obj_name='bottle_of_pop_40_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_pop/ghxeqz/usd/MJCF/ghxeqz_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfMushroomSauce1WithHand ---
@register_object
class BottleOfMushroomSauce1WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_mushroom_sauce_1_with_hand',
                 obj_name='bottle_of_mushroom_sauce_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_mushroom_sauce/xamfxi/usd/MJCF/xamfxi_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class HalfScone1WithHand ---
@register_object
class HalfScone1WithHand(CustomObjects):
    def __init__(self,
                 name='half_scone_1_with_hand',
                 obj_name='half_scone_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/half_scone/nruwwp/usd/MJCF/nruwwp_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class HalfScone2WithHand ---
# @register_object
# class HalfScone2WithHand(CustomObjects):
#     def __init__(self,
#                  name='half_scone_2_with_hand',
#                  obj_name='half_scone_2_with_hand',
#                  ):
#         custom_path = os.path.join(
#                 str(absolute_path), f"assets/new_objects_with_hand/half_scone/vykthm/usd/MJCF/vykthm_with_hand.xml"
#             )
#         super().__init__(
#             custom_path=custom_path,
#             name=name,
#             obj_name=obj_name,
#         )
#         self.rotation = {
#             "x": (-np.pi / 2, -np.pi / 2),
#             "y": (-np.pi, -np.pi),
#             "z": (np.pi, np.pi),
#         }
#         self.rotation_axis = None


# --- appended class BoxOfShampoo1WithHand ---
@register_object
class BoxOfShampoo1WithHand(CustomObjects):
    def __init__(self,
                 name='box_of_shampoo_1_with_hand',
                 obj_name='box_of_shampoo_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/box_of_shampoo/tzghev/usd/MJCF/tzghev_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BoxOfShampoo2WithHand ---
@register_object
class BoxOfShampoo2WithHand(CustomObjects):
    def __init__(self,
                 name='box_of_shampoo_2_with_hand',
                 obj_name='box_of_shampoo_2_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/box_of_shampoo/nijidu/usd/MJCF/nijidu_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BoxOfShampoo3WithHand ---
@register_object
class BoxOfShampoo3WithHand(CustomObjects):
    def __init__(self,
                 name='box_of_shampoo_3_with_hand',
                 obj_name='box_of_shampoo_3_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/box_of_shampoo/bclpiq/usd/MJCF/bclpiq_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfGarlicSauce1WithHand ---
@register_object
class BottleOfGarlicSauce1WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_garlic_sauce_1_with_hand',
                 obj_name='bottle_of_garlic_sauce_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_garlic_sauce/ucnmax/usd/MJCF/ucnmax_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfAlcohol1WithHand ---
@register_object
class BottleOfAlcohol1WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_alcohol_1_with_hand',
                 obj_name='bottle_of_alcohol_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_alcohol/qvhrjh/usd/MJCF/qvhrjh_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Clamp1WithHand ---
@register_object
class Clamp1WithHand(CustomObjects):
    def __init__(self,
                 name='clamp_1_with_hand',
                 obj_name='clamp_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/clamp/feswhy/usd/MJCF/feswhy_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class HamburgerBun1WithHand ---
# @register_object
# class HamburgerBun1WithHand(CustomObjects):
#     def __init__(self,
#                  name='hamburger_bun_1_with_hand',
#                  obj_name='hamburger_bun_1_with_hand',
#                  ):
#         custom_path = os.path.join(
#                 str(absolute_path), f"assets/new_objects_with_hand/hamburger_bun/fqxumh/usd/MJCF/fqxumh_with_hand.xml"
#             )
#         super().__init__(
#             custom_path=custom_path,
#             name=name,
#             obj_name=obj_name,
#         )
#         self.rotation = {
#             "x": (-np.pi / 2, -np.pi / 2),
#             "y": (-np.pi, -np.pi),
#             "z": (np.pi, np.pi),
#         }
#         self.rotation_axis = None


# --- appended class HamburgerBun2WithHand ---
# @register_object
# class HamburgerBun2WithHand(CustomObjects):
#     def __init__(self,
#                  name='hamburger_bun_2_with_hand',
#                  obj_name='hamburger_bun_2_with_hand',
#                  ):
#         custom_path = os.path.join(
#                 str(absolute_path), f"assets/new_objects_with_hand/hamburger_bun/jeygaq/usd/MJCF/jeygaq_with_hand.xml"
#             )
#         super().__init__(
#             custom_path=custom_path,
#             name=name,
#             obj_name=obj_name,
#         )
#         self.rotation = {
#             "x": (-np.pi / 2, -np.pi / 2),
#             "y": (-np.pi, -np.pi),
#             "z": (np.pi, np.pi),
#         }
#         self.rotation_axis = None


# --- appended class BroccoliRabe1WithHand ---
@register_object
class BroccoliRabe1WithHand(CustomObjects):
    def __init__(self,
                 name='broccoli_rabe_1_with_hand',
                 obj_name='broccoli_rabe_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/broccoli_rabe/ushqbz/usd/MJCF/ushqbz_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfMilkshake1WithHand ---
@register_object
class BottleOfMilkshake1WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_milkshake_1_with_hand',
                 obj_name='bottle_of_milkshake_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_milkshake/naxqya/usd/MJCF/naxqya_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class HalfSweetCorn2WithHand ---
@register_object
class HalfSweetCorn2WithHand(CustomObjects):
    def __init__(self,
                 name='half_sweet_corn_2_with_hand',
                 obj_name='half_sweet_corn_2_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/half_sweet_corn/tlrvtd/usd/MJCF/tlrvtd_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfCatsup1WithHand ---
@register_object
class BottleOfCatsup1WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_catsup_1_with_hand',
                 obj_name='bottle_of_catsup_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_catsup/ialodu/usd/MJCF/ialodu_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfCatsup2WithHand ---
@register_object
class BottleOfCatsup2WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_catsup_2_with_hand',
                 obj_name='bottle_of_catsup_2_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_catsup/bcqfxb/usd/MJCF/bcqfxb_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfCatsup3WithHand ---
@register_object
class BottleOfCatsup3WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_catsup_3_with_hand',
                 obj_name='bottle_of_catsup_3_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_catsup/hvxkso/usd/MJCF/hvxkso_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfCatsup4WithHand ---
@register_object
class BottleOfCatsup4WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_catsup_4_with_hand',
                 obj_name='bottle_of_catsup_4_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_catsup/ahoiqe/usd/MJCF/ahoiqe_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfCatsup5WithHand ---
@register_object
class BottleOfCatsup5WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_catsup_5_with_hand',
                 obj_name='bottle_of_catsup_5_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_catsup/dmyfdf/usd/MJCF/dmyfdf_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class HalfPear1WithHand ---
@register_object
class HalfPear1WithHand(CustomObjects):
    def __init__(self,
                 name='half_pear_1_with_hand',
                 obj_name='half_pear_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/half_pear/mqvgcg/usd/MJCF/mqvgcg_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Clipper1WithHand ---
@register_object
class Clipper1WithHand(CustomObjects):
    def __init__(self,
                 name='clipper_1_with_hand',
                 obj_name='clipper_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/clipper/befwbq/usd/MJCF/befwbq_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class Cucumber1WithHand ---
@register_object
class Cucumber1WithHand(CustomObjects):
    def __init__(self,
                 name='cucumber_1_with_hand',
                 obj_name='cucumber_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/cucumber/wcvwye/usd/MJCF/wcvwye_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfSoda1WithHand ---
@register_object
class BottleOfSoda1WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_soda_1_with_hand',
                 obj_name='bottle_of_soda_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_soda/eqyqlx/usd/MJCF/eqyqlx_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None


# --- appended class BottleOfLavenderOil1WithHand ---
@register_object
class BottleOfLavenderOil1WithHand(CustomObjects):
    def __init__(self,
                 name='bottle_of_lavender_oil_1_with_hand',
                 obj_name='bottle_of_lavender_oil_1_with_hand',
                 ):
        custom_path = os.path.join(
                str(absolute_path), f"assets/new_objects_with_hand/bottle_of_lavender_oil/csalbx/usd/MJCF/csalbx_with_hand.xml"
            )
        super().__init__(
            custom_path=custom_path,
            name=name,
            obj_name=obj_name,
        )
        self.rotation = {
            "x": (-np.pi / 2, -np.pi / 2),
            "y": (-np.pi, -np.pi),
            "z": (np.pi, np.pi),
        }
        self.rotation_axis = None
