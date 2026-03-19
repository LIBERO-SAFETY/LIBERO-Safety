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
import re
import json
import shutil
import traceback
from datetime import datetime
from typing import Tuple, Optional

from libero.libero.envs import OffScreenRenderEnv
import imageio
import numpy as np



def load_replacement_classes(json_path: str) -> list:
    """
    从JSON文件中加载可替换的类名列表
    
    Args:
        json_path: JSON文件路径
        
    Returns:
        类名列表（JSON文件中的obj_names就是类名）
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    # JSON文件中的obj_names就是类名列表
    class_names = data.get('obj_names', [])
    return sorted(list(set(class_names)))  # 去重并排序


def extract_instance_and_class(line: str, target_str: str) -> Optional[Tuple[str, str]]:
    """
    从包含目标字符串的行中提取实例名和类名
    
    Args:
        line: 包含目标字符串的行
        target_str: 目标字符串，如 "white_place_box_1_top_side"
        
    Returns:
        (实例名, 类名) 元组，如果未找到则返回None
    """
    # 找到目标字符串的位置
    idx = line.find(target_str)
    if idx == -1:
        return None
    
    # 提取目标字符串前面的部分
    before_str = line[:idx].strip()
    
    # 使用正则表达式提取最后一个单词（实例名）
    # 匹配格式如: (On milk_1 white_place_box_1_top_side)
    match = re.search(r'(\w+)\s+' + re.escape(target_str), line)
    if not match:
        return None
    
    instance_name = match.group(1)
    
    # 从实例名提取类名（去掉最后的_1）
    # 例如: milk_1 -> milk, bottle_of_beer__2_1 -> bottle_of_beer__2
    class_match = re.match(r'^(.+?)_1$', instance_name)
    if class_match:
        class_name = class_match.group(1)
    else:
        # 如果没有_1后缀，尝试其他模式
        class_name = re.sub(r'_\d+$', '', instance_name)
    
    return instance_name, class_name


def replace_in_section(content: str, section_start: str, section_end: str, 
                      old_instance: str, new_instance: str, old_class: str, new_class: str) -> str:
    """
    在指定章节中替换实例名和类名
    
    Args:
        content: 文件内容
        section_start: 章节开始标记，如 "(:objects"
        section_end: 章节结束标记，如 ")"
        old_instance: 旧实例名
        new_instance: 新实例名
        old_class: 旧类名
        new_class: 新类名
        
    Returns:
        替换后的内容
    """
    # 找到章节的开始和结束位置
    start_idx = content.find(section_start)
    if start_idx == -1:
        return content
    
    # 找到对应的结束括号
    end_idx = start_idx + len(section_start)
    paren_count = 0
    found_start = False
    
    for i in range(start_idx, len(content)):
        if content[i] == '(':
            paren_count += 1
            found_start = True
        elif content[i] == ')':
            paren_count -= 1
            if found_start and paren_count == 0:
                end_idx = i + 1
                break
    
    if end_idx == start_idx + len(section_start):
        return content
    
    # 提取章节内容
    section_content = content[start_idx:end_idx]
    
    # 替换实例名和类名
    # 替换实例定义: old_instance - old_class -> new_instance - new_class
    pattern1 = rf'\b{re.escape(old_instance)}\s+-\s+{re.escape(old_class)}\b'
    replacement1 = f'{new_instance} - {new_class}'
    section_content = re.sub(pattern1, replacement1, section_content)
    
    # 替换实例使用: old_instance -> new_instance
    # 使用单词边界确保完整匹配
    pattern2 = rf'\b{re.escape(old_instance)}\b'
    section_content = re.sub(pattern2, new_instance, section_content)
    
    # 组合结果
    result = content[:start_idx] + section_content + content[end_idx:]
    return result


def replace_bddl_obstacle(bddl_file_path: str, 
                          json_file_path: str = "/data14/rongxu.cui.2510/benchmark/LIBERO-Safety/libero/libero/envs/objects/custom_objects.json",
                          target_str: str = "white_place_box_1_top_side",
                          backup: bool = True,
                          class_index: int = 0) -> Tuple[bool, Optional[str]]:
    """
    替换BDDL文件中的障碍物对象
    
    Args:
        bddl_file_path: BDDL文件路径
        json_file_path: 包含可替换类名的JSON文件路径
        target_str: 目标字符串，默认为 "white_place_box_1_top_side"
        backup: 是否创建备份文件
        class_index: 要使用的类名索引（有序选择，而非随机）
        
    Returns:
        (是否成功替换, 替换后的类名) 元组
    """
    # 检查文件是否存在
    if not os.path.exists(bddl_file_path):
        print(f"错误: BDDL文件不存在: {bddl_file_path}")
        return False, None
    
    if not os.path.exists(json_file_path):
        print(f"错误: JSON文件不存在: {json_file_path}")
        return False, None
    
    # 创建备份
    if backup:
        backup_path = bddl_file_path + '.bak'
        shutil.copy2(bddl_file_path, backup_path)
        print(f"已创建备份文件: {backup_path}")
    
    # 读取BDDL文件
    with open(bddl_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找包含目标字符串的行
    lines = content.split('\n')
    found_line = None
    line_idx = -1
    
    for i, line in enumerate(lines):
        if target_str in line:
            found_line = line
            line_idx = i
            break
    
    if found_line is None:
        print(f"警告: 未找到包含 '{target_str}' 的行")
        return False, None
    
    # 提取实例名和类名
    result = extract_instance_and_class(found_line, target_str)
    if result is None:
        print(f"错误: 无法从行中提取实例名和类名: {found_line}")
        return False, None
    
    old_instance, old_class = result
    print(f"找到实例: {old_instance}, 类名: {old_class}")
    
    # 加载可替换的类名列表
    replacement_classes = load_replacement_classes(json_file_path)
    if not replacement_classes:
        print("错误: JSON文件中没有可用的类名")
        return False, None
    
    # 有序选择一个新类名（排除当前类名）
    available_classes = [c for c in replacement_classes if c != old_class]
    if not available_classes:
        print("警告: 没有其他可用的类名，使用所有类名")
        available_classes = replacement_classes
    
    # 使用索引有序选择类名
    if class_index >= len(available_classes):
        print(f"警告: 索引 {class_index} 超出范围，使用索引 {class_index % len(available_classes)}")
        class_index = class_index % len(available_classes)
    
    new_class = available_classes[class_index]
    new_instance = f"{new_class}_1"
    
    print(f"替换为: 实例={new_instance}, 类名={new_class} (索引: {class_index})")
    
    # 在(:objects)章节中替换
    content = replace_in_section(content, "(:objects", ")", 
                                 old_instance, new_instance, old_class, new_class)
    
    # 在(:init)章节中替换
    content = replace_in_section(content, "(:init", ")", 
                                 old_instance, new_instance, old_class, new_class)
    
    # 写回文件
    with open(bddl_file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"成功替换BDDL文件: {bddl_file_path}")
    return True, new_class


def detect_self_penetration(sim):
    model = sim.model
    data = sim.data

    penetrations = []

    for i in range(data.ncon):
        contact = data.contact[i]

        g1 = contact.geom1
        g2 = contact.geom2

        # 只关心穿透
        if contact.dist >= 0:
            continue

        # # geom -> body
        # b1 = model.geom_bodyid[g1]
        # b2 = model.geom_bodyid[g2]

        # # 找 root body
        # def root_body(b):
        #     while model.body_parentid[b] != 0:
        #         b = model.body_parentid[b]
        #     return b

        # rb1 = root_body(b1)
        # rb2 = root_body(b2)

        # # 如果属于同一物体
        # if rb1 == rb2:
        penetrations.append({
            "geom1": model.geom_id2name(g1),
            "geom2": model.geom_id2name(g2),
            "depth": -contact.dist
        })

    return penetrations
bddl_file_name = '/data14/rongxu.cui.2510/benchmark/LIBERO-Safety/libero/libero/bddl_files_new/obstacle_avoidance/xiaobei_batch_cat_scence.bddl'
json_file_path = "/data14/rongxu.cui.2510/benchmark/LIBERO-Safety/libero/libero/envs/objects/custom_objects.json"
target_str = "white_place_box_1_top_side"

# 加载可替换的类名列表
replacement_classes = load_replacement_classes(json_file_path)
# 读取原始BDDL文件，找到当前类名
with open(bddl_file_name, 'r', encoding='utf-8') as f:
    content = f.read()
lines = content.split('\n')
found_line = None
for line in lines:
    if target_str in line:
        found_line = line
        break

if found_line:
    result = extract_instance_and_class(found_line, target_str)
    if result:
        old_instance, old_class = result
        # 排除当前类名
        available_classes = [c for c in replacement_classes if c != old_class]
    else:
        available_classes = replacement_classes
else:
    available_classes = replacement_classes

# 创建错误日志文件
error_log_path = os.path.join(os.path.dirname(bddl_file_name), "error_log.txt")
error_count = 0
success_count = 0

# 有序遍历所有可替换的类名
for class_index, new_class_name in enumerate(available_classes):
    print(f"\n处理第 {class_index + 1}/{len(available_classes)} 个类名: {new_class_name}")
    
    try:
        # 恢复原始BDDL文件（从备份）
        backup_path = bddl_file_name + '.bak'
        if os.path.exists(backup_path):
            shutil.copy2(backup_path, bddl_file_name)
        else:
            # 如果没有备份，先创建备份
            shutil.copy2(bddl_file_name, backup_path)
            print(f"已创建备份文件: {backup_path}")
        
        # 替换BDDL文件
        success, replaced_class = replace_bddl_obstacle(
            bddl_file_name, 
            json_file_path=json_file_path,
            target_str=target_str,
            backup=False,  # 只在第一次创建备份
            class_index=class_index
        )
        
        if not success:
            error_msg = f"跳过类名 {new_class_name}，替换失败"
            print(error_msg)
            with open(error_log_path, 'a', encoding='utf-8') as log_file:
                log_file.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {error_msg}\n")
            error_count += 1
            continue
        
        # 创建环境并生成视频
        env_args = {
            "bddl_file_name": bddl_file_name,
            "camera_heights": 256,
            "camera_widths": 256
        }
        
        env = OffScreenRenderEnv(**env_args)
        model = env.sim.model
        
        obs = env.reset()
        replay_imgs = []
        sim = env.sim
        
        # 初始等待
        for i in range(10):
            action = [0.] * 7
            obs, _, _, _ = env.step(action)
            img = obs["agentview_image"][::-1]
        
        # 录制动作
        for i in range(30):
            action = [0.] * 7
            action[:3] = [0.001, 0.001, -0.001]
            obs, _, _, _ = env.step(action)
            img = obs["agentview_image"][::-1]
            replay_imgs.append(img)
        
        # 生成mp4文件名，只使用替换后的类名
        mp4_filename = f"{replaced_class}.mp4"
        mp4_path = os.path.join(os.path.dirname(bddl_file_name), mp4_filename)
        
        # 保存视频
        video_writer = imageio.get_writer(mp4_path, fps=30)
        for img in replay_imgs:
            video_writer.append_data(img)
        video_writer.close()
        print(f"保存 mp4 到: {mp4_path}")
        
        env.close()
        success_count += 1
        
    except KeyError as e:
        # 捕获KeyError（如 'apple__10' 不存在）
        error_msg = f"KeyError: 类名 '{new_class_name}' (替换后: '{replaced_class if 'replaced_class' in locals() else 'N/A'}') 不存在于对象字典中"
        error_detail = f"错误详情: {str(e)}\n{traceback.format_exc()}"
        print(f"错误: {error_msg}")
        print(error_detail)
        
        # 记录到错误日志文件
        with open(error_log_path, 'a', encoding='utf-8') as log_file:
            log_file.write(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {error_msg}\n")
            log_file.write(f"{error_detail}\n")
            log_file.write("-" * 80 + "\n")
        
        error_count += 1
        # 确保环境被关闭（如果已创建）
        if 'env' in locals():
            try:
                env.close()
            except:
                pass
        continue
        
    except Exception as e:
        # 捕获其他所有异常
        error_msg = f"处理类名 '{new_class_name}' 时发生未知错误"
        error_detail = f"错误类型: {type(e).__name__}\n错误信息: {str(e)}\n{traceback.format_exc()}"
        print(f"错误: {error_msg}")
        print(error_detail)
        
        # 记录到错误日志文件
        with open(error_log_path, 'a', encoding='utf-8') as log_file:
            log_file.write(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {error_msg}\n")
            log_file.write(f"{error_detail}\n")
            log_file.write("-" * 80 + "\n")
        
        error_count += 1
        # 确保环境被关闭（如果已创建）
        if 'env' in locals():
            try:
                env.close()
            except:
                pass
        continue

print(f"\n完成！共处理 {len(available_classes)} 个类名")
print(f"成功: {success_count} 个，失败: {error_count} 个")
if error_count > 0:
    print(f"错误日志已保存到: {error_log_path}")


