#!/usr/bin/env python3
"""
XMind文件操作工具模块
提供统一的xmind文件读写功能
"""

import json
import zipfile
import shutil
import tempfile
from pathlib import Path
from typing import Dict, Any, Union, Optional, Callable, List


def _validate_xmind_file(xmind_path: Path) -> None:
    """验证xmind文件是否存在且有效"""
    if not xmind_path.exists():
        raise FileNotFoundError(f"文件不存在: {xmind_path}")
    
    if not xmind_path.is_file():
        raise ValueError(f"路径不是文件: {xmind_path}")


def read_content(xmind_path: Union[str, Path]) -> List[Dict[str, Any]]:
    """
    读取xmind文件中的content.json
    
    Args:
        xmind_path: xmind文件路径
        
    Returns:
        content.json解析后的列表（每个元素是一个画布）
        
    Raises:
        FileNotFoundError: 文件不存在
        ValueError: 文件不是有效的xmind文件或缺少content.json
    """
    xmind_path = Path(xmind_path)
    _validate_xmind_file(xmind_path)
    
    try:
        with zipfile.ZipFile(xmind_path, 'r') as zf:
            if 'content.json' not in zf.namelist():
                raise ValueError(f"文件缺少content.json: {xmind_path}")
            
            with zf.open('content.json') as f:
                return json.load(f)
                
    except zipfile.BadZipFile:
        raise ValueError(f"不是有效的xmind文件（zip格式）: {xmind_path}")


def write_content(
    xmind_path: Union[str, Path],
    content: Union[List[Dict[str, Any]], Dict[str, Any]],
    output_path: Optional[Union[str, Path]] = None
) -> Path:
    """
    更新xmind文件中的content.json
    
    Args:
        xmind_path: 原xmind文件路径
        content: 新的content.json内容
        output_path: 输出文件路径，默认覆盖原文件
        
    Returns:
        输出文件的Path对象
    """
    xmind_path = Path(xmind_path)
    _validate_xmind_file(xmind_path)
    
    if output_path is None:
        output_path = xmind_path
    else:
        output_path = Path(output_path)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        temp_xmind = Path(tmpdir) / "temp.xmind"
        
        with zipfile.ZipFile(xmind_path, 'r') as zf_in:
            with zipfile.ZipFile(temp_xmind, 'w', zipfile.ZIP_DEFLATED) as zf_out:
                for item in zf_in.namelist():
                    if item == 'content.json':
                        zf_out.writestr(item, json.dumps(content, ensure_ascii=False, indent=2))
                    else:
                        zf_out.writestr(item, zf_in.read(item))
        
        shutil.move(str(temp_xmind), str(output_path))
    
    return output_path


def modify_content(
    xmind_path: Union[str, Path],
    modifier: Callable[[List[Dict[str, Any]]], List[Dict[str, Any]]],
    output_path: Optional[Union[str, Path]] = None
) -> List[Dict[str, Any]]:
    """
    使用自定义函数修改xmind文件的content.json
    
    Args:
        xmind_path: xmind文件路径
        modifier: 修改函数，接收并返回content.json对象
        output_path: 输出文件路径，默认覆盖原文件
        
    Returns:
        修改后的content.json对象
    """
    content = read_content(xmind_path)
    modified_content = modifier(content)
    write_content(xmind_path, modified_content, output_path)
    return modified_content
