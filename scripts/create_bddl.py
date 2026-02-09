import argparse
import json
from typing import List, Dict, Any

from libero.libero.utils.mu_utils import register_mu, InitialSceneTemplates
from libero.libero.utils.bddl_generation_utils import (
    get_xy_region_kwargs_list_from_regions_info,
)
from libero.libero.utils.task_generation_utils import (
    register_task_info,
    generate_bddl_from_task_info,
)


def create_and_register_scene(
    class_name: str,
    scene_type: str,
    workspace_name: str,
    fixture_num_info: Dict[str, int],
    object_num_info: Dict[str, int],
    regions: List[Dict[str, Any]],
    init_states: List[List[Any]],
):
    """动态定义并注册 InitialSceneTemplates 子类。"""

    regions_local = regions or []
    init_states_local = init_states or []

    # 动态类定义，define_regions 使用闭包中的 regions_local
    class DynamicScene(InitialSceneTemplates):
        def __init__(self):
            super().__init__(
                workspace_name=workspace_name,
                fixture_num_info=fixture_num_info,
                object_num_info=object_num_info,
            )

        def define_regions(self):
            self.regions = {}
            for r in regions_local:
                # r 应包含 keys: region_centroid_xy, region_name, target_name(optional), region_half_len(optional), yaw_rotation(optional)
                self.regions.update(
                    self.get_region_dict(
                        region_centroid_xy=r.get("region_centroid_xy"),
                        region_name=r.get("region_name"),
                        target_name=r.get("target_name", self.workspace_name),
                        region_half_len=r.get("region_half_len", 0.02),
                        yaw_rotation=tuple(r.get("yaw_rotation", (0.0, 0.0))),
                    )
                )
            self.xy_region_kwargs_list = get_xy_region_kwargs_list_from_regions_info(
                self.regions
            )

        @property
        def init_states(self):
            return init_states_local

    DynamicScene.__name__ = class_name
    # 注册
    register_mu(scene_type=scene_type)(DynamicScene)
    return DynamicScene


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--config", type=str, help="JSON config file path。")
    p.add_argument("--class-name", type=str, default="CustomScene")
    p.add_argument("--scene-type", type=str, default="general")
    p.add_argument("--workspace-name", type=str, default="main_table")
    p.add_argument("--fixture-num-info", type=str, help='JSON string e.g. \'{"kitchen_table":1}\'')
    p.add_argument("--object-num-info", type=str, help='JSON string e.g. \'{"plate":1}\'')
    p.add_argument("--regions", type=str, help='JSON array of region dicts')
    p.add_argument("--init-states", type=str, help='JSON array of initial state tuples')
    p.add_argument("--scene-name", type=str, required=True, help="任务中使用的 scene_name")
    p.add_argument("--language", type=str, default="en", help="注册任务使用的 language key")
    p.add_argument("--objects-of-interest", type=str, required=True, help='JSON array of object names')
    p.add_argument("--goal-states", type=str, required=True, help='JSON array of goal-state tuples')
    p.add_argument("--out-folder", type=str, default="./bddl_out", help="生成 bddl 的输出目录")
    args = p.parse_args()

    if args.config:
        conf = json.load(open(args.config))
        class_name = conf.get("class_name", args.class_name)
        scene_type = conf.get("scene_type", args.scene_type)
        workspace_name = conf.get("workspace_name", args.workspace_name)
        fixture_num_info = conf.get("fixture_num_info", {})
        object_num_info = conf.get("object_num_info", {})
        regions = conf.get("regions", [])
        init_states = conf.get("init_states", [])
        scene_name = conf.get("scene_name", args.scene_name)
        language = conf.get("language", args.language)
        objects_of_interest = conf.get("objects_of_interest")
        goal_states = conf.get("goal_states")
        out_folder = conf.get("out_folder", args.out_folder)
    else:
        class_name = args.class_name
        scene_type = args.scene_type
        workspace_name = args.workspace_name
        fixture_num_info = json.loads(args.fixture_num_info) if args.fixture_num_info else {}
        object_num_info = json.loads(args.object_num_info) if args.object_num_info else {}
        regions = json.loads(args.regions) if args.regions else []
        init_states = json.loads(args.init_states) if args.init_states else []
        scene_name = args.scene_name
        language = args.language
        objects_of_interest = json.loads(args.objects_of_interest)
        goal_states = json.loads(args.goal_states)
        out_folder = args.out_folder

    # 创建并注册场景模板
    create_and_register_scene(
        class_name=class_name,
        scene_type=scene_type,
        workspace_name=workspace_name,
        fixture_num_info=fixture_num_info,
        object_num_info=object_num_info,
        regions=regions,
        init_states=init_states,
    )

    # 注册任务信息
    register_task_info(
        language,
        scene_name=scene_name,
        objects_of_interest=objects_of_interest,
        goal_states=goal_states,
    )

    # 生成 BDDL 文件
    bddl_files, failures = generate_bddl_from_task_info(folder=out_folder)
    print("bddl_files:", bddl_files)
    if failures:
        print("failures:", failures)


if __name__ == "__main__":
    main()