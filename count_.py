import os
from pathlib import Path

def count_files(directory, recursive=False, use_pathlib=False):
    """
    统计指定文件夹中的文件数量
    
    参数:
    directory (str): 要统计的文件夹路径
    recursive (bool): 是否递归统计子文件夹中的文件，默认为False
    use_pathlib (bool): 是否使用pathlib模块，默认为False（使用os模块）
    
    返回:
    int: 文件数量
    """
    # 检查目录是否存在
    if not os.path.exists(directory):
        raise FileNotFoundError(f"目录 '{directory}' 不存在")
    
    if use_pathlib:
        # 使用pathlib模块实现[2,6](@ref)
        path = Path(directory)
        if recursive:
            # 递归统计所有子文件夹中的文件[6](@ref)
            return len([file for file in path.rglob('*') if file.is_file()])
        else:
            # 仅统计当前文件夹中的文件[2](@ref)
            return len([item for item in path.iterdir() if item.is_file()])
    else:
        # 使用os模块实现[1,6](@ref)
        if recursive:
            # 使用os.walk递归统计[1](@ref)
            total_files = 0
            for root, dirs, files in os.walk(directory):
                total_files += len(files)
            return total_files
        else:
            # 使用os.listdir统计当前目录[1](@ref)
            return len([name for name in os.listdir(directory) 
                       if os.path.isfile(os.path.join(directory, name))])

# 使用示例
if __name__ == "__main__":
    target_directory = '/data14/rongxu.cui.2510/benchmark/openvla-oft/rollouts/2025_12_21'
    
    # 基本统计（不包含子文件夹）
    try:
        simple_count = count_files(target_directory, recursive=False)
        print(f"当前文件夹中的文件数量（不包含子文件夹）: {simple_count}")
        
        # 递归统计（包含所有子文件夹）
        recursive_count = count_files(target_directory, recursive=True)
        print(f"总文件数量（包含所有子文件夹）: {recursive_count}")
        
        # 使用pathlib进行统计
        pathlib_count = count_files(target_directory, use_pathlib=True)
        print(f"使用pathlib统计的文件数量: {pathlib_count}")
        
    except FileNotFoundError as e:
        print(f"错误: {e}")
    except PermissionError as e:
        print(f"权限错误: {e}")
    except Exception as e:
        print(f"发生错误: {e}")