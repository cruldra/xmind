#!/usr/bin/env python3
"""
修改XMind文件的背景颜色
"""

import sys
import uuid
import argparse
from pathlib import Path
from typing import Dict, Any, Union, Optional, List
try:
    from scripts.xmind_utils import read_content, modify_content
except ImportError:
    from xmind_utils import read_content, modify_content


def _apply_background_style(sheet: Dict[str, Any], color: str) -> None:
    """为画布应用背景样式"""
    if 'style' not in sheet:
        sheet['style'] = {}
    
    style = sheet['style']
    
    if 'id' not in style:
        style['id'] = str(uuid.uuid4())
    
    if 'properties' not in style:
        style['properties'] = {}
    
    style['properties']['svg:fill'] = color


def set_sheet_background(
    xmind_path: Union[str, Path],
    color: str = "#000000FF",
    sheet_index: int = 0,
    output_path: Optional[Union[str, Path]] = None
) -> List[Dict[str, Any]]:
    """
    修改XMind文件指定画布的背景颜色
    
    Args:
        xmind_path: xmind文件路径
        color: 背景颜色（十六进制，如 #000000FF 表示黑色不透明）
        sheet_index: 画布索引，默认为0（第一个画布）
        output_path: 输出文件路径，默认为None（覆盖原文件）
        
    Returns:
        修改后的content.json对象
        
    Raises:
        FileNotFoundError: 文件不存在
        ValueError: 文件不是有效的xmind文件或缺少content.json
        IndexError: sheet_index超出范围
    """
    content = read_content(xmind_path)
    
    # 检查sheet_index是否有效
    if sheet_index < 0 or sheet_index >= len(content):
        raise IndexError(f"sheet_index {sheet_index} 超出范围，文件共有 {len(content)} 个画布")
    
    # 修改指定画布
    _apply_background_style(content[sheet_index], color)
    
    # 写回文件
    modify_content(xmind_path, lambda c: content, output_path)
    
    return content


def set_all_sheets_background(
    xmind_path: Union[str, Path],
    color: str = "#000000FF",
    output_path: Optional[Union[str, Path]] = None
) -> List[Dict[str, Any]]:
    """
    修改XMind文件所有画布的背景颜色
    
    Args:
        xmind_path: xmind文件路径
        color: 背景颜色（十六进制）
        output_path: 输出文件路径，默认为None（覆盖原文件）
        
    Returns:
        修改后的content.json对象
    """
    def modifier(content):
        for sheet in content:
            _apply_background_style(sheet, color)
        return content
    
    return modify_content(xmind_path, modifier, output_path)


def list_sheets(xmind_path: Union[str, Path]) -> List[Dict[str, Any]]:
    """
    列出XMind文件中的所有画布信息
    
    Args:
        xmind_path: xmind文件路径
        
    Returns:
        画布信息列表
    """
    content = read_content(xmind_path)
    
    sheets_info = []
    for idx, sheet in enumerate(content):
        info = {
            'index': idx,
            'id': sheet.get('id', 'N/A'),
            'title': sheet.get('title', f'画布 {idx + 1}'),
            'has_style': 'style' in sheet,
            'background_color': sheet.get('style', {}).get('properties', {}).get('svg:fill', '未设置')
        }
        sheets_info.append(info)
    
    return sheets_info


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description='修改XMind文件的背景颜色',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 修改第一个画布的背景为黑色
  python set_background.py demo.xmind --color #000000FF
  
  # 修改第二个画布的背景为红色
  python set_background.py demo.xmind --color #FF0000FF --sheet 1
  
  # 修改所有画布的背景为蓝色
  python set_background.py demo.xmind --color #0000FFFF --all
  
  # 保存到新文件
  python set_background.py demo.xmind --color #000000FF -o demo_black.xmind
  
  # 列出所有画布
  python set_background.py demo.xmind --list
        """
    )
    
    parser.add_argument('xmind_file', help='xmind文件路径')
    parser.add_argument('--color', '-c', default='#000000FF', 
                        help='背景颜色（十六进制，默认：#000000FF）')
    parser.add_argument('--sheet', '-s', type=int, default=0,
                        help='画布索引（从0开始，默认：0）')
    parser.add_argument('--all', '-a', action='store_true',
                        help='修改所有画布的背景颜色')
    parser.add_argument('--output', '-o',
                        help='输出文件路径（默认覆盖原文件）')
    parser.add_argument('--list', '-l', action='store_true',
                        help='列出所有画布信息')
    
    args = parser.parse_args()
    
    try:
        if args.list:
            # 列出所有画布
            sheets = list_sheets(args.xmind_file)
            print(f"\n文件 '{args.xmind_file}' 中的画布：")
            print("-" * 80)
            for sheet in sheets:
                print(f"索引: {sheet['index']}")
                print(f"  标题: {sheet['title']}")
                print(f"  ID: {sheet['id']}")
                print(f"  背景颜色: {sheet['background_color']}")
                print()
        elif args.all:
            # 修改所有画布
            content = set_all_sheets_background(
                args.xmind_file,
                color=args.color,
                output_path=args.output
            )
            output_file = args.output or args.xmind_file
            print(f"✓ 已将所有 {len(content)} 个画布的背景颜色修改为 {args.color}")
            print(f"  输出文件: {output_file}")
        else:
            # 修改单个画布
            content = set_sheet_background(
                args.xmind_file,
                color=args.color,
                sheet_index=args.sheet,
                output_path=args.output
            )
            output_file = args.output or args.xmind_file
            sheet_title = content[args.sheet].get('title', f'画布 {args.sheet}')
            print(f"✓ 已将 '{sheet_title}' 的背景颜色修改为 {args.color}")
            print(f"  输出文件: {output_file}")
            
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        raise


if __name__ == "__main__":
    main()
