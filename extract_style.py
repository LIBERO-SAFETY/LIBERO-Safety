import ast
import json
import re
import os
from collections import defaultdict


# def extract_robust(file_path):
#     # 1. 读取所有代码行
#     with open(file_path, "r", encoding="utf-8") as f:
#         lines = f.readlines()
#         full_content = "".join(lines)

#     # 2. 解析文件结构
#     try:
#         tree = ast.parse(full_content)
#     except SyntaxError as e:
#         print(f"文件语法错误，无法定位类: {e}")
#         return {}

#     # ==========================================
#     # 修改点 1: 使用 dict 代替 set
#     # Python 3.7+ 字典是保留插入顺序的
#     # ==========================================
#     data_store = {
#         "scene_xml": {}, 
#         "floor_style": {},
#         "wall_style": {}
#     }

#     # 3. 收集所有类节点并按行号排序 (确保严格按文件顺序)
#     class_nodes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
#     class_nodes.sort(key=lambda x: x.lineno) # 按行号从小到大排序

#     print(f"找到 {len(class_nodes)} 个类，正在按文件顺序提取...")

#     # 4. 遍历
#     for node in class_nodes:
#         # 获取该类在文件中的起始行和结束行
#         start_line = node.lineno - 1
#         end_line = getattr(node, 'end_lineno', None)
        
#         if end_line:
#             class_source_code = "".join(lines[start_line:end_line])
#         else:
#             class_source_code = "".join(lines[start_line:start_line+50])

#         # 5. 正则提取 (利用字典键去重且保持顺序)
        
#         # --- 提取 scene_xml ---
#         xml_match = re.search(r'["\']scene_xml["\']\s*:\s*["\']([^"\']+)["\']', class_source_code)
#         if xml_match:
#             val = xml_match.group(1)
#             # 只有当 key 不存在时才插入 (实际上重复插入也不会改变顺序，但这样逻辑更清晰)
#             data_store["scene_xml"][val] = None 

#         # --- 提取 floor_style ---
#         floor_match = re.search(r'["\']floor_style["\']\s*:\s*["\']([^"\']+)["\']', class_source_code)
#         if floor_match:
#             val = floor_match.group(1)
#             data_store["floor_style"][val] = None

#         # --- 提取 wall_style ---
#         wall_match = re.search(r'["\']wall_style["\']\s*:\s*["\']([^"\']+)["\']', class_source_code)
#         if wall_match:
#             val = wall_match.group(1)
#             data_store["wall_style"][val] = None

#     # ==========================================
#     # 修改点 2: 直接取 keys 转 list，不要 sorted()
#     # ==========================================
#     final_output = {
#         "scene_xml": list(data_store["scene_xml"].keys()),
#         "floor_style": list(data_store["floor_style"].keys()),
#         "wall_style": list(data_store["wall_style"].keys())
#     }
    
#     return final_output


# # ==========================================
# # 执行部分
# # ==========================================
# TARGET_FILE = "/data14/rongxu.cui.2510/benchmark/LIBERO-plus/libero/libero/envs/problems/libero_tabletop_manipulation.py"

# if __name__ == "__main__":
#     if os.path.exists(TARGET_FILE):
#         print("正在使用 [AST定位 + 正则提取] (保持文件顺序模式)...")
#         result = extract_robust(TARGET_FILE)

#         output_file = TARGET_FILE.replace('.py', '.json')
#         with open(output_file, "w", encoding="utf-8") as f:
#             json.dump(result, f, indent=4, ensure_ascii=False)
            
#         print(f"\n结果已保存至: {output_file}")
#         print(f"XML数量: {len(result['scene_xml'])}")
#         print(f"Floor数量: {len(result['floor_style'])}")
#         print(f"Wall数量: {len(result['wall_style'])}")


import ast
import json
import re
import os

def extract_configs_ordered(file_path):
    # 1. 读取文件
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        full_content = "".join(lines)

    # 2. 解析 AST
    try:
        tree = ast.parse(full_content)
    except SyntaxError as e:
        print(f"文件语法错误: {e}")
        return []

    # 3. 收集类节点并按行号排序 (确保物理顺序)
    class_nodes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
    class_nodes.sort(key=lambda x: x.lineno)

    print(f"找到 {len(class_nodes)} 个类，正在提取配置组合...")

    # 用于存储最终结果的列表
    ordered_configs = []
    # 用于去重的集合 (存储元组 hash)
    seen_configs = set()

    # 4. 遍历提取
    for node in class_nodes:
        # 获取源码片段
        start_line = node.lineno - 1
        end_line = getattr(node, 'end_lineno', None)
        
        if end_line:
            class_source_code = "".join(lines[start_line:end_line])
        else:
            class_source_code = "".join(lines[start_line:start_line+50])

        # --- 正则提取 ---
        
        # 提取 XML
        xml_match = re.search(r'["\']scene_xml["\']\s*:\s*["\']([^"\']+)["\']', class_source_code)
        xml_val = xml_match.group(1) if xml_match else None

        # 提取 Floor
        floor_match = re.search(r'["\']floor_style["\']\s*:\s*["\']([^"\']+)["\']', class_source_code)
        floor_val = floor_match.group(1) if floor_match else None

        # 提取 Wall
        wall_match = re.search(r'["\']wall_style["\']\s*:\s*["\']([^"\']+)["\']', class_source_code)
        wall_val = wall_match.group(1) if wall_match else None

        # 5. 构建字典对象
        # 只有当至少提取到一个属性时才保存，避免保存全 None 的空对象
        if xml_val or floor_val or wall_val:
            config_entry = {
                "scene_xml": xml_val,
                "floor_style": floor_val,
                "wall_style": wall_val
            }

            # 6. 去重逻辑 (Unique Check)
            # 我们用一个元组来代表这个配置的“指纹”，放入 set 中比对
            # 如果你想要保留所有重复的类配置，请注释掉下面 3 行 if 逻辑
            config_signature = (xml_val, floor_val, wall_val)
            
            if config_signature not in seen_configs:
                seen_configs.add(config_signature)
                ordered_configs.append(config_entry)

    return ordered_configs


# ==========================================
# 执行部分
# ==========================================
TARGET_FILE = "/data14/rongxu.cui.2510/benchmark/LIBERO-plus/libero/libero/envs/problems/libero_floor_manipulation.py"

if __name__ == "__main__":
    if os.path.exists(TARGET_FILE):
        print("正在提取并构建字典列表...")
        result_list = extract_configs_ordered(TARGET_FILE)

        output_file = TARGET_FILE.replace('.py', '.json')
        
        # 保存为 JSON
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result_list, f, indent=4, ensure_ascii=False)
            
        print(f"\n提取完成！")
        print(f"共提取到 {len(result_list)} 个唯一的配置组合。")
        print(f"结果已保存至: {output_file}")