import xml.etree.ElementTree as ET
import sys
from pathlib import Path
import os 


def add_gravcomp_to_bodies(input_xml, output_xml=None):
    input_xml = Path(input_xml)
    if output_xml is None:
        output_xml = input_xml.with_suffix(".gravcomp.xml")
    else:
        output_xml = Path(output_xml)

    tree = ET.parse(input_xml)
    root = tree.getroot()
    count_added = 0
    count_set = 0

    # 遍历所有 body（包括嵌套）
    for body in root.iter("body"):
        if "gravcomp" in body.attrib and body.attrib["gravcomp"] != 0:
            body.set("gravcomp", "0")
            count_set += 1
        else:
            body.set("gravcomp", "0")
            count_added += 1

    tree.write(output_xml, encoding="utf-8", xml_declaration=True)

    # print(f"处理完成: {input_xml}")
    print(f"新增 gravcomp=1 的 body 数量: {count_added}")
    print(f"原本已有 gravcomp 的 body 数量: {count_set}")
    print(f"输出文件: {output_xml}")
    return count_set


obj_dir = '/data14/rongxu.cui.2510/benchmark/LIBERO-plus/libero/libero/assets/new_objects_with_hand'


for first_dir in sorted(os.listdir(obj_dir)):
    for second_dir in sorted(os.listdir(os.path.join(obj_dir, first_dir))):
        base_dir = os.path.join(obj_dir, first_dir, second_dir)
        obj_path = os.path.join(base_dir, f'usd/MJCF/{second_dir}_with_hand.xml')
        count = add_gravcomp_to_bodies(obj_path, obj_path)
        if count > 0:
            print(f'Processed {obj_path}, added gravcomp to {count} bodies.')
            # import pdb; pdb.set_trace()