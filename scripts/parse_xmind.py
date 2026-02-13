#!/usr/bin/env python3
"""
解析XMind文件，提取content.json内容
"""

import json
import zipfile
from pathlib import Path
from typing import Dict, Any, Union


def parse_xmind_content(xmind_path: Union[str, Path]) -> Dict[str, Any]:
    """
    解析.xmind文件，返回content.json的字典对象
    
    Args:
        xmind_path: xmind文件路径
        
    Returns:
        content.json解析后的字典对象
        
    Raises:
        FileNotFoundError: 文件不存在
        ValueError: 文件不是有效的xmind文件或缺少content.json
        json.JSONDecodeError: content.json解析失败
    """
    xmind_path = Path(xmind_path)
    
    # 检查文件是否存在
    if not xmind_path.exists():
        raise FileNotFoundError(f"文件不存在: {xmind_path}")
    
    if not xmind_path.is_file():
        raise ValueError(f"路径不是文件: {xmind_path}")
    
    # 读取xmind文件（zip格式）
    try:
        with zipfile.ZipFile(xmind_path, 'r') as zf:
            # 检查content.json是否存在
            if 'content.json' not in zf.namelist():
                raise ValueError(f"文件缺少content.json: {xmind_path}")
            
            # 读取并解析content.json
            with zf.open('content.json') as f:
                content = json.load(f)
                return content
                
    except zipfile.BadZipFile:
        raise ValueError(f"不是有效的xmind文件（zip格式）: {xmind_path}")


def main():
    """命令行入口"""
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python parse_xmind.py <xmind文件路径>")
        print("示例: python parse_xmind.py demo.xmind")
        sys.exit(1)
    
    xmind_path = sys.argv[1]
    
    try:
        content = parse_xmind_content(xmind_path)
        print(json.dumps(content, ensure_ascii=False, indent=2))
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
