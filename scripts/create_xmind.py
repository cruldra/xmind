#!/usr/bin/env python3
"""
创建全新的XMind文件
基于模板复制并支持自定义标题
"""

import shutil
from pathlib import Path
from typing import Union, Optional

try:
    from scripts.xmind_utils import read_content, write_content
except ImportError:
    from xmind_utils import read_content, write_content


def create_xmind(
    output_path: Union[str, Path],
    template_path: Union[str, Path] = None,
    sheet_title: Optional[str] = None,
    root_topic_title: Optional[str] = None
) -> Path:
    """
    创建新的XMind文件
    
    Args:
        output_path: 新文件输出路径
        template_path: 模板文件路径，默认使用assets/demo.xmind
        sheet_title: 画布标题（可选）
        root_topic_title: 中心主题标题（可选）
        
    Returns:
        新文件的Path对象
        
    示例:
        # 基本使用 - 直接复制模板
        create_xmind("my_new.xmind")
        
        # 自定义标题
        create_xmind(
            "my_new.xmind",
            sheet_title="我的画布",
            root_topic_title="中心主题"
        )
        
        # 使用自定义模板
        create_xmind(
            "my_new.xmind",
            template_path="path/to/my_template.xmind"
        )
    """
    output_path = Path(output_path)
    
    # 确保输出目录存在
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 确定模板路径
    if template_path is None:
        # 默认使用demo.xmind作为模板
        script_dir = Path(__file__).parent
        template_path = script_dir.parent / "assets" / "demo.xmind"
    else:
        template_path = Path(template_path)
    
    # 检查模板是否存在
    if not template_path.exists():
        raise FileNotFoundError(f"模板文件不存在: {template_path}")
    
    # 如果没有自定义标题，直接复制
    if sheet_title is None and root_topic_title is None:
        shutil.copy2(template_path, output_path)
        return output_path
    
    # 需要修改内容，使用xmind_utils
    content = read_content(template_path)
    
    # 修改画布标题
    if sheet_title and len(content) > 0:
        content[0]['title'] = sheet_title
    
    # 修改中心主题标题
    if root_topic_title and len(content) > 0:
        root_topic = content[0].get('rootTopic', {})
        if root_topic:
            root_topic['title'] = root_topic_title
    
    # 写入新文件
    write_content(template_path, content, output_path)
    
    return output_path


def main():
    """命令行入口"""
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(
        description='创建全新的XMind文件',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 创建空白思维导图
  uv run create_xmind.py my_new.xmind
  
  # 自定义画布标题
  uv run create_xmind.py my_new.xmind --sheet-title "项目规划"
  
  # 自定义中心主题
  uv run create_xmind.py my_new.xmind --root-topic "产品路线图"
  
  # 同时自定义画布和中心主题
  uv run create_xmind.py my_new.xmind --sheet-title "项目规划" --root-topic "Q4目标"
  
  # 使用自定义模板
  uv run create_xmind.py my_new.xmind --template path/to/template.xmind
        """
    )
    
    parser.add_argument('output', help='新xmind文件路径（如：my_new.xmind）')
    parser.add_argument('--sheet-title', '-s',
                        help='画布标题')
    parser.add_argument('--root-topic', '-r',
                        help='中心主题标题')
    parser.add_argument('--template', '-t',
                        help='自定义模板路径（默认使用demo.xmind）')
    
    args = parser.parse_args()
    
    try:
        output_file = create_xmind(
            args.output,
            template_path=args.template,
            sheet_title=args.sheet_title,
            root_topic_title=args.root_topic
        )
        
        print(f"✓ 成功创建XMind文件: {output_file}")
        
        # 显示创建详情
        if args.sheet_title or args.root_topic:
            print("  配置信息:")
            if args.sheet_title:
                print(f"    - 画布标题: {args.sheet_title}")
            if args.root_topic:
                print(f"    - 中心主题: {args.root_topic}")
        
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
