#!/usr/bin/env python3

import argparse
import re
import os
import sys
import shutil
import textwrap
import json
import re
import astor
import ast
from libero.libero.envs import OffScreenRenderEnv
from PIL import Image
import numpy as np
from libero.libero.envs.objects import get_object_dict
from libero.libero import get_libero_path
from libero.libero import set_libero_default_path
import random
from typing import List
# set_libero_default_path("/data14/rongxu.cui.2510/benchmark/LIBERO-plus/libero/libero")
from libero.libero.benchmark import libero_task_map 

# ---------------------------
# Predefined dynamics templates (parameterized)
# ---------------------------
DYN_TEMPLATES = {
    "static": """
        ({obj_name}
            (:type kinematic)
            (:traj
                (:kind linear)
                (:p0 {x_min} {x_max} {y_min} {y_max} {z_min} {z_max})
                (:v 0.0 0.0 0.0 0.0 0.0 0.0)
                (:quat {quat_x} {quat_y} {quat_z} {quat_w})
            )
        )
        """,
    "circle": """
        ({obj_name}
            (:type kinematic)
            (:traj
                (:kind circle)
                (:center {x_min} {x_max} {y_min} {y_max} {z_min} {z_max})
                (:radius {radius_min} {radius_max})
                (:omega {omega_min} {omega_max})
                (:quat {quat_x} {quat_y} {quat_z} {quat_w})
            )
        )
        """,

    "linear": """
        ({obj_name}
            (:type kinematic)
            (:traj
                (:kind linear)
                (:p0 {x_min} {x_max} {y_min} {y_max} {z_min} {z_max})
                (:v {v_x_min} {v_x_max} {v_y_min} {v_y_max} {v_z_min} {v_z_max})
                (:quat {quat_x} {quat_y} {quat_z} {quat_w})
            )
        )
        """,

    "brownian": """
        ({obj_name}
            (:type kinematic)
            (:traj
                (:kind brownian)
                (:p0 {x_min} {x_max} {y_min} {y_max} {z_min} {z_max})
                (:quat 0.0 0.0 0.0 1.0)
                (:quat {quat_x} {quat_y} {quat_z} {quat_w})
            )
        )
        """
}

DEFAULT_TEMPLATE_KWARGS = {
    "static": {
        "center_x": 0.0, "center_y": 0.0, "center_z": 1.0
    },
    "circle": {
        "center_x": 0.0, "center_y": 0.0, "center_z": 1.0,
        "radius": 0.12, "omega": -0.2, "z": 0.7,
    },
    "linear": {
        "center_x": 0.0, "center_y": 0.0, "center_z": 0.6,
        "v_x": 0.2, "v_y": 0.0, "v_z": 0.0,
        "quat_w": 0.0, "quat_x": 0.0, "quat_y": 0.0, "quat_z": 1.0,
    },
    "brownian": {
        "center_x": 0.0, "center_y": 0.0, "center_z": 0.6
    }
}

CLASS_TEMPLATE = """@register_object
class {class_name}(CustomObstacle):
    def __init__(self,
                 name={name!r},
                 obj_name={obj_name!r},
                 texture_label={texture_label!r},
                 mesh_label={mesh_label!r},
                 base_xml={base_xml!r},
                 scale=[{scale_list}],
                 joints={joints_raw},
                 gravcomp={gravcomp_flag},
                 ):
        super().__init__(
            name=name,
            obj_name=obj_name,
            texture_label=texture_label,
            mesh_label=mesh_label,
            base_xml=base_xml,
            scale=scale,
            joints=joints,
            gravcomp=gravcomp,
        )
        self.rotation = {rotation}
        self.rotation_axis = None
"""


def _make_context(obj_name, obj_type, index, extra_kwargs):
    ctx = {
        "obj_name": obj_name,
        "obj_type": obj_type,
        "index": index,
    }
    if extra_kwargs:
        for k, v in extra_kwargs.items():
            if isinstance(v, (list, tuple)):
                ctx[k] = " ".join(str(x) for x in v)
            else:
                ctx[k] = v
    return ctx

def render_dyn_template_from_id(template_id, obj_name, obj_type=None, index=1, overrides=None, indent="    "):
    if template_id not in DYN_TEMPLATES:
        raise KeyError(f"Unknown template id: {template_id}")
    defaults = dict(DEFAULT_TEMPLATE_KWARGS.get(template_id, {}))
    if overrides:
        for k, v in overrides.items():
            defaults[k] = v
    ctx = _make_context(obj_name, obj_type, index, defaults)
    raw = DYN_TEMPLATES[template_id].format(**ctx)
    ded = textwrap.dedent(raw).rstrip()
    lines = ded.splitlines()
    indented = "\n".join((indent + ln) if ln.strip() != "" else "" for ln in lines)
    return indented + "\n"

def render_dyn_template_custom(template_str, obj_name, obj_type=None, index=1, overrides=None, indent="    "):
    ctx = _make_context(obj_name, obj_type, index, overrides or {})
    try:
        raw = template_str.format(**ctx)
    except Exception as e:
        raise ValueError(f"Error formatting custom dyn template: {e}")
    ded = textwrap.dedent(raw).rstrip()
    lines = ded.splitlines()
    indented = "\n".join((indent + ln) if ln.strip() != "" else "" for ln in lines)
    return indented + "\n"

# ---------------------------
# Helper functions (same as before)
# ---------------------------
def find_matching_paren(text: str, start_idx: int) -> int:
    if start_idx < 0 or start_idx >= len(text) or text[start_idx] != "(":
        return -1
    depth = 0
    for i in range(start_idx, len(text)):
        ch = text[i]
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                return i
    return -1

def find_first_problem_region(text: str):
    key = "(define (problem"
    idx = text.find(key)
    if idx == -1:
        return None, None
    end_idx = find_matching_paren(text, idx)
    if end_idx == -1:
        return None, None
    return idx, end_idx

def find_subblock(problem_text: str, subkey: str):
    idx = problem_text.find(subkey)
    if idx == -1:
        return None, None
    end_idx = find_matching_paren(problem_text, idx)
    if end_idx == -1:
        return None, None
    return idx, end_idx

def parse_existing_objects(objects_block_text: str):
    inner = objects_block_text.strip()
    m = re.match(r'^\(\:objects\b(.*)\)\s*$', inner, flags=re.S)
    if m:
        content = m.group(1)
    else:
        content = inner
        if content.startswith("(:objects"):
            content = content[len("(:objects"):].rstrip(")")
    lines = [ln.strip() for ln in content.splitlines() if ln.strip() != ""]
    tokens = []
    for ln in lines:
        parts = re.split(r'\s+', ln)
        tokens.extend(parts)
    type_map = {}
    i = 0
    while i < len(tokens):
        if i+2 < len(tokens) and tokens[i+1] == '-':
            name = tokens[i]
            typ = tokens[i+2]
            type_map.setdefault(typ, []).append(name)
            i += 3
        else:
            i += 1
    return content, tokens, type_map

def detect_next_index_for_type(tokens, obj_type):
    pattern = re.compile(r'^(.+?)_(\d+)$')
    max_idx = 0
    i = 0
    while i < len(tokens):
        if i+2 < len(tokens) and tokens[i+1] == '-':
            name = tokens[i]
            typ = tokens[i+2]
            if typ == obj_type:
                m = pattern.match(name)
                if m:
                    idx = int(m.group(2))
                    if idx > max_idx:
                        max_idx = idx
            i += 3
        else:
            i += 1
    return max_idx + 1

def render_line_for_type(names, obj_type, indent):
    return indent + " ".join(names) + " - " + obj_type + "\n"

def parse_names_arg(names_arg):
    if not names_arg:
        return None
    parts = [p.strip() for p in names_arg.split(",") if p.strip() != ""]
    return parts if parts else None

def ensure_dynamics_block(problem_text: str):
    sub_start, sub_end = find_subblock(problem_text, "(:dynamics")
    if sub_start is not None:
        return problem_text, sub_start, sub_end
    insert_pos = len(problem_text) - 1
    line_start = problem_text.rfind("\n", 0, insert_pos)
    if line_start == -1:
        base_indent = ""
    else:
        lc = problem_text[line_start+1:insert_pos]
        base_indent = ""
        for ch in lc:
            if ch in (" ", "\t"):
                base_indent += ch
            else:
                break
    new_block = "\n" + base_indent + "(:dynamics\n" + base_indent + ")\n"
    new_problem_text = problem_text[:insert_pos] + new_block + problem_text[insert_pos:]
    new_sub_start = new_problem_text.find("(:dynamics", 0)
    new_sub_end = find_matching_paren(new_problem_text, new_sub_start)
    return new_problem_text, new_sub_start, new_sub_end


def _split_top_level_blocks(s: str):
    """
    将字符串 s（可能包含多个 Lisp 子树）切分成若干 top-level 块（包含括号），
    返回块的列表（每个块以 '(' 开始、以相应的 ')' 结束，保留原始文本内部换行与空白）。
    非块文本（空白、注释行）会被忽略。
    """
    blocks = []
    buf = []
    depth = 0
    started = False
    i = 0
    while i < len(s):
        ch = s[i]
        if ch == '(':
            depth += 1
            started = True
            buf.append(ch)
        elif ch == ')':
            buf.append(ch)
            depth -= 1
            if depth == 0 and started:
                # complete block
                blocks.append(''.join(buf))
                buf = []
                started = False
            # else still inside block
        else:
            if started:
                buf.append(ch)
            else:
                # outside a block: ignore whitespace/comments between blocks
                pass
        i += 1
    # if buffer leftover (unbalanced), include it as-is (best-effort)
    if buf:
        rem = ''.join(buf).strip()
        if rem:
            blocks.append(rem)
    return blocks

def _extract_block_name(block: str):
    """
    从一个 Lisp 块（字符串，以 '(' 开头）提取第一个符号作为名字。
    例如 "(dynamic_box_1 (:type kinematic) ...)" -> "dynamic_box_1"
    返回 None 如果无法解析。
    """
    # 使用正则在 '(' 后找到第一个非空白、非括号的 token
    m = re.match(r'^\s*\(\s*([^\s()]+)', block)
    if m:
        return m.group(1)
    return None

def append_entries_to_dynamics_block(problem_text: str, dyn_start: int, dyn_end: int, entries_text: str):
    """
    在 problem_text 的 dynamics 块范围 [dyn_start, dyn_end] 中：
    - 解析现有条目为若干 top-level 块
    - 解析 entries_text 为若干 top-level 块
    - 对每个要插入块：若已存在同名块则替换；否则追加
    - 保持其他未修改的现有块顺序
    返回修改后的完整文本
    """
    before = problem_text[:dyn_start]
    block = problem_text[dyn_start:dyn_end+1]
    after = problem_text[dyn_end+1:]

    # split block into lines to isolate the opening "( :dynamics" line and the final closing paren line
    lines = block.splitlines(True)
    if len(lines) < 2:
        # 非常规格式，退化到简单追加行为
        new_block = block[:-1] + ("\n" + entries_text.rstrip() + "\n") + block[-1]
        return before + new_block + after

    start_line = lines[0]          # e.g. "(:dynamics\n" 或 "  (:dynamics\n"
    end_line = lines[-1]           # the closing ")" line for dynamics block
    middle_text = ''.join(lines[1:-1])  # 中间包含若干 top-level dynamics 条目（每个是一个 lisp 子树）

    # 解析现有的 top-level blocks（每个 block 以 '(' 开始）
    existing_blocks = _split_top_level_blocks(middle_text)
    # 构建按原始顺序的 name -> block 列表 & name->index 映射（保留第一个出现的位置）
    existing_name_to_index = {}
    for i, blk in enumerate(existing_blocks):
        name = _extract_block_name(blk)
        if name:
            # 如果 name 重复出现，我们保留最先出现的索引（后续重复视为独立块，不覆盖）
            if name not in existing_name_to_index:
                existing_name_to_index[name] = i

    # 解析要插入的 entries_text 为 blocks
    new_blocks = _split_top_level_blocks(entries_text)

    # 将现有 blocks 转为可修改的列表
    mod_blocks = existing_blocks[:]  # shallow copy

    # 对每个 new block：提取其名字，若存在则替换对应索引，否则 append
    for nb in new_blocks:
        name = _extract_block_name(nb)
        if not name:
            # 如果无法提取名字，直接追加（保守策略）
            mod_blocks.append(nb)
            continue
        if name in existing_name_to_index:
            idx = existing_name_to_index[name]
            mod_blocks[idx] = nb
        else:
            # append new block and register its index (so subsequent new blocks with same name replace this appended one)
            existing_name_to_index[name] = len(mod_blocks)
            mod_blocks.append(nb)

    # 重新组合块，保留 start_line 与 end_line 的原样（缩进/换行）
    # Ensure there's a newline between blocks for readability
    joined_middle = ''
    for blk in mod_blocks:
        # trim trailing/leading blank lines to avoid accidental double newlines
        joined_middle += (blk if blk.endswith('\n') else blk + '\n')

    new_block = start_line + joined_middle + end_line
    return before + new_block + after




# ---------------------------
# Core: insert objects and per-object dynamics (uses per_object_map)
# ---------------------------
def insert_objects_and_dynamics(orig_text: str, obj_type: str, count: int, 
                                dyn_template_id=None, dyn_overrides=None):
    p_start, p_end = find_first_problem_region(orig_text)
    if p_start is None:
        print("No (define (problem ...) block found. Aborting.")
        return orig_text, False

    problem_text = orig_text[p_start:p_end+1]
    before = orig_text[:p_start]
    after = orig_text[p_end+1:]

    # find or create objects block
    sub_start, sub_end = find_subblock(problem_text, "(:objects")
    final_names = []
    # tokens = []
    if sub_start is not None:
        block_text = problem_text[sub_start:sub_end+1]
        # inner_text, tokens, type_map = parse_existing_objects(block_text)
        # next_idx = detect_next_index_for_type(tokens, obj_type)
        for i in range(count):
            final_names.append(f"{obj_type}_{i + 1}")
        
        # 只替换符合 obj_type 的行，保留其他类型的对象
        lines = block_text.splitlines(keepends=True)
        new_lines = []
        
        # 保留第一行 (:objects
        new_lines.append(lines[0])
        
        # 收集所有不匹配目标类型的行
        obj_type_pattern = r'\s+-\s+' + re.escape(obj_type) + r'(\s+|$)'
        for ln in lines[1:-1]:  # 排除第一行和最后一行
            # 检查这行是否包含我们要替换的目标类型
            if not re.search(obj_type_pattern, ln):
                # 不包含目标类型，保留这行
                new_lines.append(ln)
            # 如果包含目标类型，则跳过这行（相当于删除）
        
        # 添加新的对象行
        if lines:
            # 获取缩进信息
            first_line = lines[0]
            base_indent = first_line[:len(first_line) - len(first_line.lstrip())]
            inner_indent = base_indent + "    "
        else:
            base_indent = ""
            inner_indent = "    "
            
        new_lines.append(inner_indent + " ".join(final_names) + " - " + obj_type + "\n")
        
        # 添加最后一行 )
        if len(lines) > 1:
            new_lines.append(lines[-1])
        else:
            new_lines.append(base_indent + ")\n")
            
        new_block = "".join(new_lines)
        problem_text = problem_text[:sub_start] + new_block + problem_text[sub_end+1:]
    else:
        anchors = ["(:fixtures", "(:obj_of_interest", "(:init", "(:goal", "(:dynamics"]
        insert_idx = None
        for a in anchors:
            idx = problem_text.find(a)
            if idx != -1:
                insert_idx = idx
                break
        if insert_idx is None:
            insert_idx = len(problem_text) - 1
        line_start = problem_text.rfind("\n", 0, insert_idx)
        base_indent = ""
        if line_start != -1:
            lc = problem_text[line_start+1:insert_idx]
            for ch in lc:
                if ch in (" ", "\t"):
                    base_indent += ch
                else:
                    break
        inner_indent = base_indent + "    "

        final_names = [f"{obj_type}_{i+1}" for i in range(count)]
        objects_block = "\n" + base_indent + "(:objects\n"
        objects_block += inner_indent + " ".join(final_names) + " - " + obj_type + "\n"
        objects_block += base_indent + ")\n"
        problem_text = problem_text[:insert_idx] + objects_block + problem_text[insert_idx:]

    # final_names now hold the names added
    problem_text, dyn_s, dyn_e = ensure_dynamics_block(problem_text)
    entries = []
    for idx, name in enumerate(final_names, start=1):
        m = re.match(r'.*_([0-9]+)$', name)
        num = int(m.group(1)) if m else idx
        entry = render_dyn_template_from_id(dyn_template_id, name, obj_type=obj_type, index=num, overrides=dyn_overrides, indent="    ")
        entries.append(entry.rstrip())
    entries_text = "\n".join(entries)
    problem_text = append_entries_to_dynamics_block(problem_text, dyn_s, dyn_e, entries_text)

    new_text = before + problem_text + after
    return new_text, True

# ---------------------------
# Parsing of per-object CLI / JSON
# ---------------------------
def parse_per_object_arg(entries):
    """
    entries: list of strings passed via --per-object (may be empty)
    each entry format: "obj_name|template_id|<json_params>" or "obj_name|template|<template_string>"
    returns dict: name -> {"template_id":int,"params":dict} or {"template": str, "params":dict}
    """
    out = {}
    if not entries:
        return out
    for e in entries:
        # split only at first two '|' occurrences
        parts = e.split("|", 2)
        if len(parts) < 2:
            print(f"Invalid --per-object entry (must be obj_name|template_id|params OR obj_name|template|template_str): {e}", file=sys.stderr)
            continue
        name = parts[0].strip()
        kind = parts[1].strip()
        if kind.isdigit():
            # template id form; params optional
            tid = int(kind)
            params = None
            if len(parts) == 3 and parts[2].strip() != "":
                try:
                    params = json.loads(parts[2])
                except Exception as ex:
                    print(f"Error parsing JSON params for {name}: {ex}", file=sys.stderr)
                    params = None
            out[name] = {"template_id": tid, "params": params}
        else:
            # treat kind == 'template' or direct template string (if provided in third part)
            if kind == "template" and len(parts) == 3:
                tpl = parts[2]
                out[name] = {"template": tpl}
            else:
                # if kind is a non-digit and there's a third part, treat third as params or template?
                if len(parts) == 3:
                    # assume second part is template string (maybe user omitted 'template' keyword)
                    tpl = parts[1]  # include full
                    # here we've already grabbed second as kind; if third present, maybe it's params — ambiguous
                    out[name] = {"template": tpl}
                else:
                    # ambiguous fallback
                    print(f"Unrecognized --per-object entry: {e}", file=sys.stderr)
    return out


def validate_scale(scale_str):
    parts = [s.strip() for s in scale_str.split(",") if s.strip() != ""]
    if len(parts) != 3:
        raise ValueError("scale must have three comma-separated numbers, e.g. 0.005,0.005,0.005")
    # Validate they are numbers
    try:
        nums = [float(x) for x in parts]
    except Exception as e:
        raise ValueError("scale contains non-numeric values") from e
    # return Python list literal string like [0.005, 0.005, 0.005]
    return "[" + ", ".join(repr(x) for x in nums) + "]"

def class_exists_in_source(src, class_name):
    """
    Try to parse AST; if fails, fallback to text search.
    """
    try:
        module = ast.parse(src)
    except Exception:
        return ("class " + class_name) in src
    for node in module.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            return True
    return False

def replace_class_in_source(src, class_name, new_class_src):
    """
    Replace the first top-level ClassDef with name `class_name` by the AST nodes in new_class_src.
    Returns (new_src, True) on success, (orig_src, False) if class not found.
    """
    try:
        module = ast.parse(src)
        new_module = ast.parse(new_class_src)
    except Exception as e:
        print("AST parse error during replace:", e, file=sys.stderr)
        return src, False

    replace_idx = None
    for i, node in enumerate(module.body):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            replace_idx = i
            break
    if replace_idx is None:
        return src, False

    new_nodes = new_module.body
    new_body = module.body[:replace_idx] + new_nodes + module.body[replace_idx+1:]
    module.body = new_body
    try:
        new_src = astor.to_source(module)
    except Exception as e:
        print("Error converting AST to source with astor:", e, file=sys.stderr)
        return src, False
    return new_src, True

def interactive_choice_loop():
    prompt = (
        "Class name already exists. Choose action:\n"
        "  [a] Abort (do nothing)\n"
        "  [n] New name (enter a different class name)\n"
        "  [f] Force append (allow duplicate)\n"
        "  [r] Replace existing class with the new one\n"
        "Enter choice (a/n/f/r): "
    )
    while True:
        try:
            c = input(prompt).strip().lower()
        except EOFError:
            return "abort", None
        if c in ("a", "abort"):
            return "abort", None
        if c in ("n", "new"):
            new_name = input("Enter new class name: ").strip()
            if new_name == "":
                print("Class name cannot be empty.")
                continue
            return "new", new_name
        if c in ("f", "force"):
            return "force", None
        if c in ("r", "replace"):
            return "replace", None
        print("Invalid choice. Please enter a/n/f/r.")

def camel_to_snake(name):
    key = "_".join(re.sub(r"([A-Z0-9])", r" \1", name).split()).lower()
    # 转换为小写
    return key


# --- fixtures: add mapping "name - type" as a separate line in (:fixtures ...) ---
def add_object(problem_text: str, obj_type: str, count: int, is_fixed: bool = False):
    """
    Ensure (:fixtures ...) contains a line 'obj_name - obj_type'.
    If fixtures block missing -> create one near top of problem (before :objects or :regions).
    If mapping already present -> do nothing.
    Returns modified text.
    """
    # find or create objects block
    if is_fixed:
        sub_start, sub_end = find_subblock(problem_text, "(:fixtures")
    else:
        sub_start, sub_end = find_subblock(problem_text, "(:objects")
    final_names = []
    # tokens = []
    block_text = problem_text[sub_start:sub_end+1]
    # inner_text, tokens, type_map = parse_existing_objects(block_text)
    # next_idx = detect_next_index_for_type(tokens, obj_type)
    for i in range(count):
        final_names.append(f"{obj_type}_{i + 1}")
    
    # 只替换符合 obj_type 的行，保留其他类型的对象
    lines = block_text.splitlines(keepends=True)
    new_lines = []
    
    # 保留第一行 (:objects
    new_lines.append(lines[0])
    
    # 收集所有不匹配目标类型的行
    obj_type_pattern = r'\s+-\s+' + re.escape(obj_type) + r'(\s+|$)'
    for ln in lines[1:-1]:  # 排除第一行和最后一行
        # 检查这行是否包含我们要替换的目标类型
        if not re.search(obj_type_pattern, ln):
            # 不包含目标类型，保留这行
            new_lines.append(ln)
        # 如果包含目标类型，则跳过这行（相当于删除）
    
    # 添加新的对象行
    if lines:
        # 获取缩进信息
        first_line = lines[0]
        base_indent = first_line[:len(first_line) - len(first_line.lstrip())]
        inner_indent = base_indent + "    "
    else:
        base_indent = ""
        inner_indent = "    "
        
    new_lines.append(inner_indent + " ".join(final_names) + " - " + obj_type + "\n")
    
    # 添加最后一行 )
    if len(lines) > 1:
        new_lines.append(lines[-1])
    else:
        new_lines.append(base_indent + ")\n")
        
    new_block = "".join(new_lines)
    problem_text = problem_text[:sub_start] + new_block + problem_text[sub_end+1:]
    return problem_text, final_names


# --- regions: replace region if exists, otherwise append region inside (:regions ...) ---
def build_region_block(region_name: str, target: str, ranges: list, yaw_rotation=None, indent="    "):
    """
    ranges: list of tuples/lists e.g. [(-0.16, 0.14, -0.14, 0.16)]
    yaw_rotation: list of (min, max) tuples, default [(0.0,0.0)]
    returns a string region block (no surrounding newline)
    """
    yaw_rotation = yaw_rotation if yaw_rotation is not None else [(0.0, 0.0)]
    s = []
    s.append(f"({region_name}\n")
    s.append(f"    (:target {target})\n")
    s.append(f"    (:ranges (\n")

    # format numbers preserving original-ish formatting
    s.append("        (" + " ".join(repr(float(x)) for x in ranges) + ")\n")
    s.append("      )\n")
    s.append("    )\n")
    s.append("    (:yaw_rotation (\n")
    for y in yaw_rotation:
        s.append("        (" + " ".join(repr(float(x)) for x in y) + ")\n")
    s.append("      )\n")
    s.append("    )\n")
    s.append(")\n")
    # indent inner lines by one level when inserted into (:regions) block
    block = "".join(s)
    indented = "".join(indent + line if line.strip() != "" else line for line in block.splitlines(True))
    return indented


def get_first_region_target(problem_text: str):
    """
    返回 (:regions ...) 中第一个 region 的 (:target ...) 的 token。
    如果不存在 regions 或第一个 region 没有 target，则返回 None。
    """
    # 找到 regions 块
    regions_start = problem_text.find("(:regions")
    if regions_start == -1:
        return None

    regions_end = find_matching_paren(problem_text, regions_start)
    if regions_end == -1:
        return None

    regions_block = problem_text[regions_start:regions_end+1]

    # 匹配第一个子 region： (xxxx_init_region 或任意 "(" 开始的 block)
    # 只匹配顶层的 region，不匹配 ranges/yaw_rotation 里的 "("
    # 因此只找第一层的新 region 名称
    m = re.search(r'\(\s*([A-Za-z0-9_]+)\s*\n', regions_block)
    if not m:
        return None

    first_region_name = m.group(1)

    # 查找第一个 region 的 block
    rm = re.search(r'\(\s*' + re.escape(first_region_name) + r'\b', regions_block)
    if not rm:
        return None

    # 找 region 子块边界
    abs_start = regions_start + rm.start()
    abs_end = find_matching_paren(problem_text, abs_start)
    if abs_end == -1:
        return None

    region_block = problem_text[abs_start:abs_end+1]

    # 找 (:target xxx)
    tm = re.search(r'\(\s*:target\s+([^\s()]+)', region_block)
    if tm:
        return tm.group(1).strip()

    return None

def add_or_replace_region(problem_text: str, region_name: str, ranges: list, yaw_rotation=None):
    sub_start, sub_end = find_subblock(problem_text, "(:regions")
    target = get_first_region_target(problem_text)
    region_block = build_region_block(region_name, target, ranges, yaw_rotation)
    # existing regions block -> parse into top-level region subblocks and replace if same name exists
    block = problem_text[sub_start:sub_end+1]
    # find existing region by name using regex
    # region start pattern: e.g. "(region_name" possibly preceded by whitespace/newline + indentation
    pattern = re.compile(r'(\(\s*' + re.escape(region_name) + r'\b)', flags=re.M)
    if pattern.search(block):
        # replace the entire region: find its start index within block, then matching parenthesis
        # locate the exact start offset
        m = pattern.search(block)
        start_off = m.start()
        # compute absolute start in full text
        abs_start = sub_start + start_off
        abs_end = find_matching_paren(problem_text, abs_start)
        if abs_end == -1:
            # malformed; fallback to appending
            pass
        else:
            new_text = problem_text[:abs_start] + "\n" + region_block.rstrip() + problem_text[abs_end+1:]
            return new_text, target
    else:
        # not found -> append new region before closing paren of regions block
        # insert just before last char of block
        new_block = block[:-1] + region_block + block[-1]
        return problem_text[:sub_start] + new_block + problem_text[sub_end+1:], target


# --- init: add (On obj region) if missing; create (:init ...) block if absent ---
def add_init_on(problem_text: str, obj_name: str, region_name: str):
    sub_start, sub_end = find_subblock(problem_text, "(:init")
    new_line = f"    (On {obj_name} {region_name})\n"
    if sub_start is None:
        # create init block before :goal (or before :dynamics)
        anchors = ["(:goal", "(:dynamics", "(:objects"]
        insert_idx = None
        for a in anchors:
            idx = problem_text.find(a)
            if idx != -1:
                insert_idx = idx
                break
        if insert_idx is None:
            insert_idx = len(problem_text) - 1
        line_start = problem_text.rfind("\n", 0, insert_idx)
        base_indent = ""
        if line_start != -1:
            lc = problem_text[line_start+1:insert_idx]
            for ch in lc:
                if ch in (" ", "\t"):
                    base_indent += ch
                else:
                    break
        block = "\n" + base_indent + "(:init\n" + new_line + base_indent + ")\n"
        return problem_text[:insert_idx] + block + problem_text[insert_idx:]

    block = problem_text[sub_start:sub_end+1]
    # check if line already present
    if re.search(r'\(On\s+' + re.escape(obj_name) + r'\s+' + re.escape(region_name) + r'\)', block):
        return problem_text
    # insert before closing paren
    # maintain indentation of other init lines if available
    m = re.search(r'\n([ \t]*)\(', block)
    inner_indent = "    "
    if m:
        inner_indent = m.group(1)
    insertion = inner_indent + "(On " + obj_name + " " + region_name + ")\n"
    new_block = block[:-1] + insertion + block[-1]
    return problem_text[:sub_start] + new_block + problem_text[sub_end+1:]


# ------------------------
# Example of usage
# ------------------------
def add_fixed_object_to_problem_file(src: str,
                                     obj_type: str,
                                     ranges: list,
                                     count: int = 1,
                                     is_fixed: bool = False,
                                     yaw_rotation=None):
    """
      - add fixture mapping obj_name - obj_type
      - add/replace region region_name (target, ranges)
      - add init (On obj_name <target>_<region_name>_init_region) -> but here we pass region_name explicitly
    """

    # 1) add fixture
    src, obj_names = add_object(src, obj_type, count, is_fixed)
    # 2) add/replace region
    region_name = f"obs_init_region"
    src, target_name = add_or_replace_region(src, region_name, ranges, yaw_rotation)
    # 3) add init On
    region = f"{target_name}_{region_name}"
    for obj_name in obj_names:
        src = add_init_on(src, obj_name, region)

    return src, True

def add_or_replace_region2(problem_text: str, region_name: str):
    def build_region_block2(region_name: str, indent="    "):
        """
        ranges: list of tuples/lists e.g. [(-0.16, 0.14, -0.14, 0.16)]
        yaw_rotation: list of (min, max) tuples, default [(0.0,0.0)]
        returns a string region block (no surrounding newline)
        """
        s = []
        s.append("(top_side\n")
        s.append(f"    (:target {region_name}_1)\n")
        s.append(")\n")
        # indent inner lines by one level when inserted into (:regions) block
        block = "".join(s)
        indented = "".join(indent + line if line.strip() != "" else line for line in block.splitlines(True))
        return indented
    sub_start, sub_end = find_subblock(problem_text, "(:regions")
    region_block = build_region_block2(region_name)
    # existing regions block -> parse into top-level region subblocks and replace if same name exists
    block = problem_text[sub_start:sub_end+1]
    # find existing region by name using regex
    # region start pattern: e.g. "(region_name" possibly preceded by whitespace/newline + indentation
    new_block = block[:-1] + region_block + block[-1]
    return problem_text[:sub_start] + new_block + problem_text[sub_end+1:]

def add_place_object_to_problem_file(src: str,
                                     obj_type: str,
                                     count: int = 1,
                                     is_fixed: bool = False,
                                     yaw_rotation=None):
    """
      - add fixture mapping obj_name - obj_type
      - add/replace region region_name (target, ranges)
      - add init (On obj_name <target>_<region_name>_init_region) -> but here we pass region_name explicitly
    """

    # 1) add fixture
    src, obj_names = add_object(src, obj_type, count, is_fixed)
    region_name = "white_place_box"
    src = add_or_replace_region2(src, region_name)
    # 2) add init On
    region = f"white_place_box_1_top_side"
    for obj_name in obj_names:
        src = add_init_on(src, obj_name, region)

    return src, True


def _find_matching_paren(text: str, open_paren_index: int) -> int:
    """
    给定 text 和一个 '(' 的位置，返回与之匹配的 ')' 的索引（同层级闭合）。
    会忽略字符串中的括号（简单处理：遇到 "..." 或 '...' 就跳过）。
    """
    if open_paren_index < 0 or open_paren_index >= len(text) or text[open_paren_index] != "(":
        raise ValueError("open_paren_index 必须指向 '('")

    depth = 0
    i = open_paren_index
    in_single = False
    in_double = False

    while i < len(text):
        ch = text[i]

        # 处理字符串（很常见但 bddl 里一般不多）
        if ch == "'" and not in_double:
            in_single = not in_single
            i += 1
            continue
        if ch == '"' and not in_single:
            in_double = not in_double
            i += 1
            continue

        if in_single or in_double:
            i += 1
            continue

        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                return i
        i += 1

    raise ValueError("没有找到匹配的 ')'，文件括号可能不平衡")

def insert_obstacle_after_goal(
    bddl_text: str,
    obstacles: List[str],
    indent: str = "  ",
) -> str:
    """
    在顶层 (:goal ...) 段后插入 (:obstacle ...)

    obstacles: 障碍物名字列表，例如 ["box1", "box2"]。
               若为 None 或空，则插入空的 (:obstacle\n\n)
    """
    obstacles = obstacles or []

    goal_kw = "(:goal"
    goal_start = bddl_text.find(goal_kw)
    if goal_start == -1:
        raise ValueError("未找到 '(:goal' 段")

    # goal_start 指向 '('，找到这整个 (:goal ...) 的匹配 ')'
    goal_open_paren = goal_start  # 因为 "(:goal" 以 '(' 开头
    goal_end_paren = _find_matching_paren(bddl_text, goal_open_paren)

    # 插入内容（保持风格：插入前后各留一个空行）
    if obstacles:
        obstacle_lines = "\n".join(f"{indent}{name}" for name in obstacles)
        obstacle_block = f"\n\n(:obstacle\n{obstacle_lines}\n)\n"
    else:
        obstacle_block = "\n\n(:obstacle\n\n)\n"

    insert_pos = goal_end_paren + 1  # 在 goal 的 ')' 之后插入
    return bddl_text[:insert_pos] + obstacle_block + bddl_text[insert_pos:]


def insert_obstacle_in_file(
    problem_text: str,
    obstacles: List[str] = None,
) -> str:
    new_text = insert_obstacle_after_goal(problem_text, obstacles=obstacles)
    return new_text


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
        import pdb; pdb.set_trace()


def main():
    # np.random.seed(42)
    # random.seed()
    p = argparse.ArgumentParser(description="Add objects to (:objects ...) and optionally add per-object :dynamics entries (per-object templates supported).")
    p.add_argument("--backup", action="store_true", default=False, help="create backup .bak (default True)")
    p.add_argument("--train", action="store_true", default=True, help="train objects")
    p.add_argument("--libero_task", type=str, default="libero_spatial", help="libero task name")

    args = p.parse_args()
    object_dict = get_object_dict()

    filtered_names = [name 
        for name, cls in object_dict.items()
        if 'with_hand' in name
    ]
    train_names = []
    test_names = []
    table_test_names = []
    table_train_names = []
    test_count = 0
    table_names = [name for name, clas in object_dict.items() 
    if ('libero.libero.envs.objects.custom_objects' in clas.__module__ and 'with_hand' not in clas.__module__ and 'bottle' in name)]
    for name in filtered_names:   
        parts = name.split('_')
        obj_id = int(parts[-3])
        if obj_id > 2:
            test_names.append(name)
        else:
            train_names.append(name)
    for name in table_names:   
        parts = name.split('_')
        if parts[-1].isdigit() and int(parts[-1]) > 2:
            table_test_names.append(name)
        else:
            table_train_names.append(name)
    
    task_names = libero_task_map[args.libero_task]
    count = 0
    for task_name in task_names:
        if "noise" in task_name:
            continue
        print(count)
        if (test_count % 10 == 0) or (test_count % 9 == 0) or (test_count % 8 == 0) or (test_count % 7 == 0):
            train_set = False
        else:
            train_set = True
        test_count += 1

        random_int = random.randint(1, 3)
        if random_int == 1:
            motion_type = "static"
            obj_num = 1
        elif random_int == 2:
            motion_type = "dynamic"
            obj_num = 1
        else:
            motion_type = "table"
            obj_num = 1
        ori_task_name = task_name
        if "_view_" in str(task_name) and "_initstate_" in str(task_name):
            try:
                ori_task_name, angle_view_initstate = task_name.split("_view_")
            except:
                task_name_str = str(task_name)
                ori_task_name, angle_view_initstate = task_name_str.split("_view_")

        in_path = os.path.join(get_libero_path("bddl_files"), args.libero_task, ori_task_name + ".bddl")
        if not in_path or not os.path.isfile(in_path):
            print("File not found or not specified:", in_path, file=sys.stderr)
            import pdb; pdb.set_trace()
        with open(in_path, "r", encoding="utf-8") as f:
            bddl_src = f.read()

        for i in range(obj_num):
            quat_x, quat_y, quat_z, quat_w = random_quaternion_xyzw()
            if train_set:
                selected_name = np.random.choice(train_names)
            else:
                selected_name = np.random.choice(test_names)
            if 'pick_up_the_black_bowl_between_the_plate_and_the_ramekin_and_place_it_on_the_plate' in task_name: # 1
                x_min = -0.09
                x_max = -0.07
                y_min = 0.03
                y_max = 0.05
            elif 'pick_up_the_black_bowl_from_table_center_and_place_it_on_the_plate' in task_name:
                x_min = -0.1
                x_max = -0.08
                y_min = 0.17 
                y_max = 0.19
            elif 'pick_up_the_black_bowl_on_the_ramekin_and_place_it_on_the_plate' in task_name:
                x_min = -0.09
                x_max = -0.07
                y_min = 0.03 
                y_max = 0.05   
            elif 'pick_up_the_black_bowl_on_the_cookie_box_and_place_it_on_the_plate' in task_name:
                x_min = -0.08
                x_max = -0.06
                y_min = -0.06 
                y_max = -0.04 
            elif 'pick_up_the_black_bowl_in_the_top_drawer_of_the_wooden_cabinet_and_place_it_on_the_plate' in task_name:
                x_min = -0.08
                x_max = -0.06
                y_min = 0.08 
                y_max = 0.1  
            elif 'pick_up_the_black_bowl_next_to_the_plate_and_place_it_on_the_plate' in task_name: 
                x_min = -0.06 
                x_max = -0.04
                y_min = 0.04 
                y_max = 0.06  
            elif 'pick_up_the_black_bowl_next_to_the_ramekin_and_place_it_on_the_plate' in task_name:
                x_min = -0.04 
                x_max = -0.02
                y_min = 0.04 
                y_max = 0.06  
            elif 'pick_up_the_black_bowl_on_the_stove_and_place_it_on_the_plate' in task_name:
                x_min = -0.06 
                x_max = -0.04
                y_min = 0.02 
                y_max = 0.04 
            elif "pick_up_the_black_bowl_next_to_the_cookie_box_and_place_it_on_the_plate" in task_name:
                x_min = -0.08 
                x_max = -0.06
                y_min = 0.09
                y_max = 0.11 
            elif "pick_up_the_black_bowl_on_the_wooden_cabinet_and_place_it_on_the_plate" in task_names:
                x_min = 0.05 
                x_max = 0.07
                y_min = 0.03 
                y_max = 0.05
                random_int = random.randint(1, 2)
                if random_int == 1:
                    motion_type = "static"
                    obj_num = 1
                else:
                    motion_type = "dynamic"
                    obj_num = 1

            z_min = 0.38
            z_max = 0.4
            if motion_type == "static":
                # x_true = random.uniform(x_min, x_max)
                # y_true = random.uniform(y_min, y_max)
                # z_true = random.uniform(0.26, 0.3)
                
                # y = random.uniform(-0.2, 0.2)
                # y_min = max(-0.25, y - 0.01)
                # y_max = min(0.25, y + 0.01)
                # x = random.uniform(-0.2, 0.2)
                # if -0.06 < y < 0.06:
                #     x = random.uniform(0.15, 0.2)
                # x_min = max(-0.25, x - 0.01)
                # x_max = min(0.25, x + 0.01)
                if obj_num == 1:
                    dyn_overrides = {"x_min":x_min,"x_max":x_max,"y_min":y_min,"y_max":y_max,"z_min":z_min,"z_max":z_max, "quat_x": quat_x, "quat_y": quat_y, "quat_z": quat_z, "quat_w": quat_w}
                # else:
                #     if i == 0:
                #         dyn_overrides = {"x_min":-0.3,"x_max":0.0,"y_min":-0.3,"y_max":0.0,"z_min":0.23,"z_max":0.3}
                #     else:
                #         dyn_overrides = {"x_min":0.0,"x_max":0.3,"y_min":0.0,"y_max":0.3,"z_min":0.23,"z_max":0.3}
                dyn_template = "static"
                new_text, ok = insert_objects_and_dynamics(bddl_src, selected_name, 1,
                                                    dyn_template_id=dyn_template,
                                                    dyn_overrides=dyn_overrides)
            elif motion_type == "dynamic":
                # random_int = random.randint(1, 2)
                # if random_int == 1:
                
                dyn_template = "linear"
                target_x = (x_max + x_min) * 0.5
                target_y = (y_max + y_min) * 0.5
                y = random.uniform(0.0, 0.25)
                y_min = max(-0.25, y - 0.01)
                y_max = min(0.3, y + 0.01)
                x = random.uniform(0.27, 0.3)
                # if -0.06 < y < 0.06:
                #     x = random.uniform(0.15, 0.2)
                x_min = max(-0.25, x - 0.01)
                x_max = min(0.35, x + 0.01)
                target_dir = np.array([target_x - x, target_y - y])
                target_norm = target_dir / np.linalg.norm(target_dir)
                vel = random.uniform(0.1, 0.15)
                v_x = target_norm[0] * vel
                v_y = target_norm[1] * vel
                v_z = random.uniform(0.0, 0.01)
                dyn_overrides = {"x_min":x_min,"x_max":x_max,"y_min":y_min,"y_max":y_max,"z_min":z_min,"z_max":z_max,"v_x_min":v_x,"v_x_max":v_x,"v_y_min":v_y,"v_y_max":v_y,"v_z_min":v_z,"v_z_max":v_z, "quat_x": quat_x, "quat_y": quat_y, "quat_z": quat_z, "quat_w": quat_w}
                # if obj_num == 1:
                #     if -0.1 < y < 0.1:
                #         dyn_overrides = {"x_min":x_min,"x_max":x_max,"y_min":y_min,"y_max":y_max,"z_min":0.26,"z_max":0.3,"v_x_min":v_x,"v_x_max":v_x,"v_y_min":v_y,"v_y_max":v_y,"v_z_min":v_z,"v_z_max":v_z, "quat_w":0.0, "quat_x":0.0, "quat_y":0.0, "quat_z":1.0}
                #     else:
                        
                # else:
                #     interval = random.choice([(-0.2, -0.1), (0.1, 0.2)])
                #     omega = random.choice([(-0.2, -0.1), (0.1, 0.2)])
                #     y = random.uniform(interval[0], interval[1])
                #     y_min = max(-0.25, y - 0.01)
                #     y_max = min(0.25, y + 0.01)
                #     x = random.uniform(0.2, 0.3)
                #     x_min = max(-0.3, x - 0.01)
                #     x_max = min(0.3, x + 0.01)
                #     dyn_template = "circle"
                #     if obj_num == 1:
                #         dyn_overrides = {"x_min":x_min,"x_max":x_max,"y_min":y_min,"y_max":y_max,"z_min":0.26,"z_max":0.3,"radius_min": 0.15, "radius_max": 0.25, "omega_min": omega[0],"omega_max": omega[1]}
                    
            
                new_text, ok = insert_objects_and_dynamics(bddl_src, selected_name, 1,
                                                    dyn_template_id=dyn_template,
                                                    dyn_overrides=dyn_overrides)
            elif motion_type == "table":
                # if 'open_the_middle_drawer_of_the_cabinet' in task_name:
                #     x_min = 0.12
                #     x_max = 0.14
                #     y_min = 0.2
                #     y_max = 0.22
                # bottle_train_names = [name for name in table_train_names if "bottle" in name]
                # bottle_test_names = [name for name in table_test_names if "bottle" in name]
                if train_set:
                    selected_name = np.random.choice(table_train_names)
                else:
                    selected_name = np.random.choice(table_test_names)
                new_text, ok = add_fixed_object_to_problem_file(bddl_src, 'white_place_box', ranges=[x_min, y_min, x_max, y_max], is_fixed=True)
                new_text, ok = add_place_object_to_problem_file(new_text, selected_name)
            
            new_text = insert_obstacle_in_file(new_text, obstacles=[selected_name])
            bddl_src = new_text


            if not ok:
                print("No changes made.", file=sys.stderr)
                sys.exit(1)

        if args.backup:
            bak = in_path + ".bak"
            shutil.copyfile(in_path, bak)
            print("Backup created:", bak)
        
        suffix = f"{motion_type}"
        out_dir = os.path.dirname(in_path) + '_obs'
        if train_set:
            out_dir = out_dir + '_train'
        out_path = os.path.join(out_dir, task_name + f'_{suffix}.bddl')
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(bddl_src)
        print("Wrote modified file to", out_path)
        append_unique(os.path.join(out_dir, 'tasks_info.txt'), "\"" + task_name + f'_{suffix}.bddl' + "\"" + ",")
        
        count += 1
        # break
    # # test
    # env_args = {
    #     "bddl_file_name": out_path,
    #     "camera_heights": 512,
    #     "camera_widths": 512
    # }

    # env = OffScreenRenderEnv(**env_args)
    # obs = env.reset()
    # for i in range(20):
    #     obs, _, _, _ = env.step([0.] * 7)
    # Image.fromarray(obs["agentview_image"][::-1]).save(out_path.replace('.bddl', '.png'))
    # env.close()


def random_quaternion_xyzw():
    # 随机生成单位旋转轴
    axis = np.random.randn(3)
    axis = axis / np.linalg.norm(axis)

    # 随机角度 [-pi, pi]
    theta = np.random.uniform(-np.pi, np.pi)

    # 计算四元数
    half = theta / 2
    qx = axis[0] * np.sin(half)
    qy = axis[1] * np.sin(half)
    qz = axis[2] * np.sin(half)
    qw = np.cos(half)

    return [qx, qy, qz, qw]

if __name__ == "__main__":
    main()