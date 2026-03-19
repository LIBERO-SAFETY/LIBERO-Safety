import os
import torch
import numpy as np
import cv2  # 导入OpenCV库用于图像处理
import argparse
from libero.libero import get_libero_path
from libero.libero.envs import OffScreenRenderEnv
from tqdm import tqdm, trange
from pathlib import Path
import random

def save_per_bddl_states(bddl_file):
    path = Path(bddl_file)
    # 提取问题名（倒数第二级目录）
    problem_folder = f"{path.parent.parent.name}/{path.parent.name}"
    # 提取任务名（文件名不带扩展名）
    task_name = path.stem
    print(f"problem_folder: {problem_folder}")
    print(f"task_name: {task_name}")
    init_root = get_libero_path("init_states")
    save_dir = os.path.join(init_root, problem_folder)
    save_path = os.path.join(save_dir, f"{task_name}.pruned_init")
    if Path(save_path).exists():
        print(f"Init states for {task_name} already exist at {save_path}, skipping...")
        return
    # 2) 创建环境
    # 注意: 我们需要从环境中获取 'agentview_image'，请确保你的环境配置支持这个观测
    env = OffScreenRenderEnv(bddl_file_name=bddl_file, camera_heights=256, camera_widths=256) # 调高分辨率以便看得更清楚
    # seed=random.randint(0, 10000)
    # env.seed(seed)

    # images_save_dir = os.path.join(save_dir, f"{task_name}_initial_images")
    # os.makedirs(images_save_dir, exist_ok=True)
    # 4) 采样初始状态并保存可视化结果
    num_states = 50
    states = []
    for i in range(num_states):
        # env.reset() 会返回一个观测字典 (observation dict)
        obs = env.reset()
        # image_rgb = obs['agentview_image'][::-1]
        # image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
        # image_path = os.path.join(images_save_dir, f"initial_state_{i:03d}_step_000.png") # 例如: initial_state_000.png
        # cv2.imwrite(image_path, image_bgr)
        # print('saved initial state image:', image_path)
        # # 可选：做几步空行动让物理稳定
        for s in range(20):
            # env.step() 同样会返回观测字典
            obs, _, _, _ = env.step([0.0] * 7)
            # image_rgb = obs['agentview_image'][::-1]
            # image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
            # image_path = os.path.join(images_save_dir, f"initial_state_{i:03d}_step_{s:03d}.png") # 例如: initial_state_000.png
            # cv2.imwrite(image_path, image_bgr)

        sim_state = env.get_sim_state()  # 扁平化 mujoco 状态向量
        states.append(sim_state)

    env.close()

    states = np.stack(states, axis=0)
    states = torch.from_numpy(states).float()

    # 5) 保存 .pruned_init 状态文件 (这部分不变)
    
    os.makedirs(save_dir, exist_ok=True)
    
    torch.save(states, save_path)
    print(f"Saved init states: {save_path}, shape={tuple(states.shape)}")
    # print(f"所有 {num_states} 张初始状态的可视化图像已保存完毕。")


def main(args):
    if args.bddl_path == '':
        save_per_bddl_states(args.bddl_file)
    else:
        bddl_path = Path(args.bddl_path)
        for bddl_file in tqdm(bddl_path.glob("*.bddl")):
            save_per_bddl_states(bddl_file)
        


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--bddl_file",
        type=str,
        help="Where to load the bddl file",
    )
    parser.add_argument(
        "--bddl_path",
        type=str,
        default='',
        help="Where to load the bddl file",
    )
    args = parser.parse_args()
    main(args)