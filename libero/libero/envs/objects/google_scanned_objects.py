import os
import numpy as np
import re

from robosuite.models.objects import MujocoXMLObject
from robosuite.utils.mjcf_utils import xml_path_completion

import pathlib

absolute_path = pathlib.Path(__file__).parent.parent.parent.absolute()

from libero.libero.envs.base_object import (
    register_visual_change_object,
    register_object,
)


class GoogleScannedObject(MujocoXMLObject):
    def __init__(self, name, obj_name, joints=[dict(type="free", damping="0.0005")], duplicate_collision_geoms=False):
        super().__init__(
            os.path.join(
                str(absolute_path),
                f"assets/stable_scanned_objects/{obj_name}/{obj_name}.xml",
            ),
            name=name,
            joints=joints,
            obj_type="all",
            duplicate_collision_geoms=duplicate_collision_geoms,
        )
        self.category_name = "_".join(
            re.sub(r"([A-Z])", r" \1", self.__class__.__name__).split()
        ).lower()
        self.rotation = (np.pi / 2, np.pi / 2)
        self.rotation_axis = "x"
        self.object_properties = {"vis_site_names": {}}


@register_object
class Rack(GoogleScannedObject):
    def __init__(
        self,
        name="simple_rack",
        obj_name="simple_rack",
        joints=[dict(type="free", damping="0.0005")],
    ):
        super().__init__(name, obj_name, joints=joints)
        self.rotation = (0, 0)
        self.rotation_axis = "x"


@register_object
class WhiteBowl(GoogleScannedObject):
    def __init__(self, name="white_bowl", obj_name="white_bowl"):
        super().__init__(name, obj_name)


@register_object
class AkitaBlackBowl(GoogleScannedObject):
    def __init__(self, name="akita_black_bowl", obj_name="akita_black_bowl"):
        super().__init__(name, obj_name)

@register_object
class Notebook(GoogleScannedObject):
    def __init__(self, name="notebook", obj_name="notebook"):
        super().__init__(name, obj_name)


@register_object
class Vase(GoogleScannedObject):
    def __init__(self, name='vase', obj_name='vase'):
        super().__init__(name, obj_name)


@register_object
class SaladPorcelainPlate(GoogleScannedObject):
    def __init__(self, name='salad_porcelain_plate', obj_name='porcelain_salad_plate'):
        super().__init__(name, obj_name)



@register_object
class ToyCar(GoogleScannedObject):
    def __init__(self, name='toy_car', obj_name='toy_car'):
        super().__init__(name, obj_name)
        self.rotation_axis = 'z'


@register_object
class RotatedToyCar(GoogleScannedObject):
    def __init__(self, name='rotated_toy_car', obj_name='toy_car'):
        super().__init__(name, obj_name)
        self.rotation_axis = None
        self.rotation = {
            'x': (np.pi/2, np.pi/2),
            'y': (0, 0),
            'z': (np.pi/2, np.pi/2),
        }


@register_object
class ToyTurtle(GoogleScannedObject):
    def __init__(self, name='toy_turtle', obj_name='toy_turtle'):
        super().__init__(name, obj_name)
        self.rotation_axis = 'z'
        self.rotation = {
            # 'x': (np.pi / 2, np.pi / 2),
            # 'y': (np.pi / 2, np.pi / 2),
            'z': (0, 0),
        }


@register_object
class ClassicBlueMug(GoogleScannedObject):
    def __init__(self, name='classic_blue_mug', obj_name='classic_blue_mug'):
        super().__init__(name, obj_name)
        self.rotation_axis = 'z'
        self.rotation = {
            # 'x': (np.pi / 2, np.pi / 2),
            # 'y': (np.pi / 2, np.pi / 2),
            'z': (0, 0),
        }

@register_object
class ToyBalls(GoogleScannedObject):
    def __init__(self, name='toy_balls', obj_name='toy_balls'):
        super().__init__(name, obj_name)


@register_object
class ToyMotorbike(GoogleScannedObject):
    def __init__(self, name='toy_motorbike', obj_name='toy_motorbike'):
        super().__init__(name, obj_name)
        self.rotation_axis = 'z'
        self.rotation = {
            'x': (np.pi / 2, np.pi / 2),
            'y': (0, 0),
            'z': (np.pi / 2, np.pi / 2),
        }


@register_object
class RotatedToyMotorbike(GoogleScannedObject):
    def __init__(self, name='rotated_toy_motorbike', obj_name='toy_motorbike'):
        super().__init__(name, obj_name)
        self.rotation_axis = 'z'
        self.rotation = {'x': (0, 0), 'y': (0, 0), 'z': (np.pi / 2, np.pi / 2)}


@register_object
class RotatedToyMotorbikeX(GoogleScannedObject):
    def __init__(
        self, name='rotated_toy_motorbike_x', obj_name='toy_motorbike'
    ):
        super().__init__(name, obj_name)
        self.rotation_axis = 'z'
        self.rotation = {
            'x': (np.pi / 6, np.pi / 6),
            'y': (0, 0),
            'z': (np.pi / 2, np.pi / 2),
        }


@register_object
class ToyTrain(GoogleScannedObject):
    def __init__(self, name='toy_train', obj_name='toy_train'):
        super().__init__(name, obj_name)
        self.rotation_axis = 'z'
        self.rotation = {
            'x': (0, 0),
            'y': (0, 0),
            'z': (np.pi / 2, np.pi / 2),
        }


@register_object
class BottledWater(GoogleScannedObject):
    def __init__(self, name='bottled_water', obj_name='bottled_water'):
        super().__init__(name, obj_name, duplicate_collision_geoms=True)


@register_object
class BilliardBalls(GoogleScannedObject):
    def __init__(self, name='billiard_balls', obj_name='billiard_balls'):
        super().__init__(name, obj_name)
        self.rotation = (0, 0)
        self.rotation_axis = 'x'


@register_object
class Candle(GoogleScannedObject):
    def __init__(self, name='candle', obj_name='candle'):
        super().__init__(name, obj_name, duplicate_collision_geoms=True)
        self.rotation = (np.pi / 2, np.pi / 2)
        self.rotation_axis = 'z'


@register_object
class LeftHand(GoogleScannedObject):
    def __init__(
        self,
        name="left_hand",
        obj_name="left_hand",
        joints=[dict(type="free", damping="0.0005")],
    ):
        super().__init__(name, obj_name, joints=joints)
        self.rotation = {
            "z": (-np.pi / 2, -np.pi / 2),
        }

@register_object
class WoodBowl(GoogleScannedObject):
    def __init__(
        self,
        name="wood_bowl",
        obj_name="wood_bowl",
        joints=[dict(type="free", damping="0.0005")],
    ):
        super().__init__(name, obj_name, joints=joints)


@register_object
class PorcelainBowl(GoogleScannedObject):
    def __init__(
        self,
        name="porcelain_bowl",
        obj_name="porcelain_bowl",
        joints=[dict(type="free", damping="0.0005")],
    ):
        super().__init__(name, obj_name, joints=joints)


@register_object
class ScanedHammer(GoogleScannedObject):
    def __init__(
        self,
        name="scaned_hammer",
        obj_name="scaned_hammer",
        joints=[dict(type="free", damping="0.0005")],
    ):
        super().__init__(name, obj_name, joints=joints)
        self.rotation = (np.pi / 2, np.pi / 2)
        self.rotation_axis = 'z'


@register_object
class Keyboard(GoogleScannedObject):
    def __init__(
        self,
        name="keyboard",
        obj_name="keyboard",
        joints=[dict(type="free", damping="0.0005")],
    ):
        super().__init__(name, obj_name, joints=joints)


@register_object
class Lemon(GoogleScannedObject):
    def __init__(
        self,
        name="lemon",
        obj_name="lemon",
        joints=[dict(type="free", damping="0.0005")],
    ):
        super().__init__(name, obj_name, joints=joints)


@register_object
class DishTowel(GoogleScannedObject):
    def __init__(
        self,
        name="dish_towel",
        obj_name="dish_towel",
        joints=[dict(type="free", damping="0.0005")],
    ):
        super().__init__(name, obj_name, joints=joints)


@register_object
class GameConsole(GoogleScannedObject):
    def __init__(
        self,
        name="game_console",
        obj_name="game_console",
        joints=[dict(type="free", damping="0.0005")],
    ):
        super().__init__(name, obj_name, joints=joints)


@register_object
class Plate(GoogleScannedObject):
    def __init__(self, name="plate", obj_name="plate"):
        super().__init__(name, obj_name)


@register_object
class Basket(GoogleScannedObject):
    def __init__(self, name="basket", obj_name="basket"):
        super().__init__(name, obj_name)


@register_object
class Chefmate8Frypan(GoogleScannedObject):
    def __init__(self, name="chefmate_8_frypan", obj_name="chefmate_8_frypan"):
        super().__init__(name, obj_name)

@register_object
class Frypan(GoogleScannedObject):
    def __init__(self, name="frypan", obj_name="frypan"):
        super().__init__(name, obj_name)


@register_object
class GlazedRimPorcelainRamekin(GoogleScannedObject):
    def __init__(
        self,
        name="glazed_rim_porcelain_ramekin",
        obj_name="glazed_rim_porcelain_ramekin",
    ):
        super().__init__(name, obj_name)
