#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
临时脚本：从custom_objects.py中提取所有obj_name并保存到JSON文件
"""
import re
import json
import os
from pathlib import Path

def extract_obj_names(file_path):
    """
    从custom_objects.py文件中提取所有obj_name
    
    Args:
        file_path: custom_objects.py文件的路径
        
    Returns:
        list: 包含所有obj_name的列表
    """
    obj_names = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 匹配模式：@register_object装饰器后跟类定义，然后找到obj_name="xxx"
    # 使用正则表达式匹配 @register_object 后面的类，然后找到 obj_name="xxx" 或 obj_name='xxx'
    pattern = r'@register_object\s+class\s+\w+.*?obj_name=["\']([^"\']+)["\']'
    
    # 使用re.DOTALL使.匹配换行符
    matches = re.findall(pattern, content, re.DOTALL)
    
    if matches:
        obj_names = matches
    else:
        # 如果上面的模式没匹配到，尝试更精确的模式
        # 匹配 @register_object 到下一个 @register_object 之间的内容
        class_blocks = re.split(r'@register_object', content)
        
        for block in class_blocks[1:]:  # 跳过第一个（@register_object之前的内容）
            # 在每个类块中查找 obj_name="xxx" 或 obj_name='xxx'
            obj_name_match = re.search(r'obj_name\s*=\s*["\']([^"\']+)["\']', block)
            if obj_name_match:
                obj_names.append(obj_name_match.group(1))
    
    # 去重并排序
    obj_names = sorted(list(set(obj_names)))
    
    return obj_names

def main():
    # 获取脚本所在目录
    script_dir = Path(__file__).parent
    custom_objects_file = script_dir / 'custom_objects.py'
    
    if not custom_objects_file.exists():
        print(f"错误：找不到文件 {custom_objects_file}")
        return
    
    print(f"正在从 {custom_objects_file} 提取obj_name...")
    
    # 提取obj_name
    obj_names = extract_obj_names(str(custom_objects_file))
    
    print(f"找到 {len(obj_names)} 个obj_name")
    
    # 保存到JSON文件
    output_file = script_dir / 'custom_objects.json'
    output_data = {
        "obj_names": obj_names,
        "count": len(obj_names)
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"已保存到 {output_file}")
    print(f"前10个obj_name: {obj_names[:10]}")

if __name__ == '__main__':
    main()
