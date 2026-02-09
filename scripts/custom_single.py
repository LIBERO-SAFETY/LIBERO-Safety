"""
BDDL 场景视频生成脚本。

支持两种模式（在下方配置区二选一）：
1. 单个 BDDL 文件：指定 BDDL_FILE_PATH，生成该文件的视频
2. BDDL 文件夹：指定 BDDL_FOLDER_PATH，生成该文件夹内所有 .bddl 文件的视频
"""

import os
import imageio
import mujoco
from tqdm import tqdm
from libero.libero.envs import OffScreenRenderEnv
from PIL import Image
# ============== 配置区：在此填写路径，二选一 ==============
# BDDL_FILE_PATH = None
BDDL_FILE_PATH = "/data14/rongxu.cui.2510/benchmark/LIBERO-plus/libero/libero/bddl_files_new/reasoning_safety/L2/put_the_scissors_on_the_notebook.bddl"

# BDDL 文件夹路径（生成该文件夹内所有 .bddl 文件的视频）
# 若使用文件夹模式，将上面 BDDL_FILE_PATH 设为 None，并填写下面的路径
BDDL_FOLDER_PATH = None
# 示例: BDDL_FOLDER_PATH = "/data14/rongxu.cui.2510/benchmark/LIBERO-plus/libero/libero/bddl_files_new/obstacle_avoidance/L1_ranges2"

# 视频参数
CAMERA_HEIGHT = 1024
CAMERA_WIDTH = 1024
VIDEO_FPS = 30
WARMUP_STEPS = 20   # 预热步数
RECORD_STEPS = 200  # 录制步数
# ========================================================


def _collect_bddl_paths():
    """根据配置返回待处理的 BDDL 文件路径列表。"""
    if BDDL_FILE_PATH is not None and BDDL_FILE_PATH.strip():
        path = BDDL_FILE_PATH.strip()
        if os.path.isfile(path) and path.endswith(".bddl"):
            return [path]
        raise FileNotFoundError(f"BDDL 文件不存在或不是 .bddl 文件: {path}")

    if BDDL_FOLDER_PATH is not None and BDDL_FOLDER_PATH.strip():
        folder = BDDL_FOLDER_PATH.strip()
        if not os.path.isdir(folder):
            raise NotADirectoryError(f"BDDL 文件夹不存在: {folder}")
        paths = [
            os.path.join(folder, name)
            for name in sorted(os.listdir(folder))
            if name.endswith(".bddl")
        ]
        if not paths:
            raise FileNotFoundError(f"文件夹内没有 .bddl 文件: {folder}")
        return paths

    raise ValueError("请在配置区设置 BDDL_FILE_PATH 或 BDDL_FOLDER_PATH（二选一）")


def generate_video_for_bddl(bddl_file_name, camera_heights=256, camera_widths=256):
    """
    为单个 BDDL 文件生成视频。

    Args:
        bddl_file_name: BDDL 文件绝对路径
        camera_heights: 画面高度
        camera_widths: 画面宽度

    Returns:
        生成的 mp4 文件路径，失败返回 None
    """
    env_args = {
        "bddl_file_name": bddl_file_name,
        "camera_heights": camera_heights,
        "camera_widths": camera_widths,
    }
    env = OffScreenRenderEnv(**env_args)
    obs = env.reset()
    replay_imgs = []

    # 预热
    for _ in range(WARMUP_STEPS):
        obs, _, _, _ = env.step([0.0] * 7)

    # 录制
    for _ in range(1):
        obs, _, _, _ = env.step([0.0] * 7)
        img = obs["agentview_image"][::-1]
    Image.fromarray(obs["agentview_image"][::-1]).save(bddl_file_name.replace('.bddl', '.png'))
        # replay_imgs.append(img)

    env.close()

    # 写视频
    mp4_path = bddl_file_name.replace(".bddl", ".mp4")
    video_writer = imageio.get_writer(mp4_path, fps=VIDEO_FPS)
    for img in replay_imgs:
        video_writer.append_data(img)
    video_writer.close()

    return mp4_path


def main():
    """根据配置生成单个或多个 BDDL 的视频。"""
    bddl_paths = _collect_bddl_paths()
    total = len(bddl_paths)
    success_count = 0


    for bddl_path in tqdm(bddl_paths, desc="生成视频", unit="file"):
        try:
            mp4_path = generate_video_for_bddl(
                bddl_path,
                camera_heights=CAMERA_HEIGHT,
                camera_widths=CAMERA_WIDTH,
            )
            success_count += 1
            tqdm.write(f"已保存: {mp4_path}")
        except Exception as e:
            tqdm.write(f"失败 {bddl_path}: {e}")

    print(f"完成: 成功 {success_count}/{total}")


if __name__ == "__main__":
    main()
