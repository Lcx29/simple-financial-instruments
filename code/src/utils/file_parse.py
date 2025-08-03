#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
@Author  :  lcn29

@Software:  PyCharm

@File    :  file_parse.py

@Time    :  2025-08-02 16:47:16

@Desc    :  文件解析工具
"""
import yaml
from loguru import logger

def parse_yaml_file(file_path: str) -> dict | list| None:
    """ 解析 YAML 文件
    Args:
        file_path (str): YAML 文件的路径
    Returns:
        dict or list: 解析后的数据，如果解析失败则返回 None
    """
    try:
        # 打开并读取 YAML 文件
        with open(file_path, 'r', encoding='utf-8') as file:
            # 解析 YAML 内容为 Python 字典/列表
            data = yaml.safe_load(file)
            return data
    except FileNotFoundError:
        logger.warning(f"错误：文件 '{file_path}' 未找到")
    except yaml.YAMLError as e:
        logger.warning(f"YAML 解析错误：{e}")
    except Exception as e:
        logger.warning(f"发生错误：{e}")
    return None
