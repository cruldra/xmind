#!/usr/bin/env python3
"""
在XMind文件中插入新主题
使用JSONPath定位父主题，然后在其children.attached中添加子主题
"""

import uuid
import json
import argparse
from pathlib import Path
from typing import Dict, Any, Union, Optional, List

try:
    from jsonpath_ng import parse
    from jsonpath_ng.exceptions import JSONPathError
except ImportError:
    print("错误: 需要安装 jsonpath-ng 库")
    print("运行: uv add jsonpath-ng")
    raise

try:
    from scripts.xmind_utils import read_content, modify_content
except ImportError:
    from xmind_utils import read_content, modify_content


def create_topic(title: str, topic_id: Optional[str] = None) -> Dict[str, Any]:
    """
    创建一个新的主题对象
    
    Args:
        title: 主题标题
        topic_id: 可选的自定义ID，默认自动生成UUID
        
    Returns:
        主题对象字典
    """
    return {
        "id": topic_id or str(uuid.uuid4()),
        "title": title,
        "titleUnedited": True
    }


def find_parent_topic(content: List[Dict], jsonpath_expr: str) -> Optional[Dict]:
    """
    使用JSONPath定位父主题
    
    Args:
        content: content.json内容（sheet列表）
        jsonpath_expr: JSONPath表达式
        
    Returns:
        找到的主题对象，未找到返回None
        
    示例JSONPath表达式:
        - '$[0].rootTopic'  # 第一个画布的中心主题
        - '$[0].rootTopic.children.attached[0]'  # 第一个画布的第一个分支主题
        - '$[0].rootTopic.children.attached[?(@.title=="分支主题 1")]'  # 按标题查找
    """
    try:
        jsonpath = parse(jsonpath_expr)
        matches = jsonpath.find(content)
        
        if not matches:
            return None
        
        if len(matches) > 1:
            print(f"警告: 找到 {len(matches)} 个匹配，使用第一个")
        
        return matches[0].value
        
    except JSONPathError as e:
        raise ValueError(f"无效的JSONPath表达式: {jsonpath_expr}, 错误: {e}")


def insert_topic(
    xmind_path: Union[str, Path],
    parent_jsonpath: str,
    topic_title: str,
    topic_id: Optional[str] = None,
    sheet_index: int = 0,
    output_path: Optional[Union[str, Path]] = None
) -> List[Dict[str, Any]]:
    """
    在指定父主题下插入新主题
    
    Args:
        xmind_path: xmind文件路径
        parent_jsonpath: 父主题的JSONPath表达式
        topic_title: 新主题标题
        topic_id: 可选的新主题ID（默认自动生成）
        sheet_index: 画布索引（当使用简化的JSONPath时需要）
        output_path: 输出文件路径，默认覆盖原文件
        
    Returns:
        修改后的content.json对象
        
    示例:
        # 在中心主题下添加子主题
        insert_topic(
            "demo.xmind",
            "$[0].rootTopic",
            "新的子主题"
        )
        
        # 在第一个分支主题下添加子主题
        insert_topic(
            "demo.xmind",
            "$[0].rootTopic.children.attached[0]",
            "细分主题 1"
        )
    """
    content = read_content(xmind_path)
    
    # 定位父主题
    parent = find_parent_topic(content, parent_jsonpath)
    
    if parent is None:
        raise ValueError(f"无法找到父主题，JSONPath: {parent_jsonpath}")
    
    # 确保父主题有children属性
    if 'children' not in parent:
        parent['children'] = {}
    
    children = parent['children']
    
    # 确保有attached数组
    if 'attached' not in children:
        children['attached'] = []
    
    # 创建新主题并添加
    new_topic = create_topic(topic_title, topic_id)
    children['attached'].append(new_topic)
    
    # 保存修改
    modify_content(xmind_path, lambda c: content, output_path)
    
    return content


def insert_topics_batch(
    xmind_path: Union[str, Path],
    parent_jsonpath: str,
    topics: List[Union[str, Dict[str, Any]]],
    output_path: Optional[Union[str, Path]] = None
) -> List[Dict[str, Any]]:
    """
    批量插入多个主题
    
    Args:
        xmind_path: xmind文件路径
        parent_jsonpath: 父主题的JSONPath表达式
        topics: 主题列表，可以是标题字符串或完整的主题字典
        output_path: 输出文件路径，默认覆盖原文件
        
    Returns:
        修改后的content.json对象
        
    示例:
        insert_topics_batch(
            "demo.xmind",
            "$[0].rootTopic.children.attached[0]",
            ["细分主题 1", "细分主题 2", "细分主题 3"]
        )
    """
    content = read_content(xmind_path)
    
    # 定位父主题
    parent = find_parent_topic(content, parent_jsonpath)
    
    if parent is None:
        raise ValueError(f"无法找到父主题，JSONPath: {parent_jsonpath}")
    
    # 确保父主题有children属性
    if 'children' not in parent:
        parent['children'] = {}
    
    children = parent['children']
    
    # 确保有attached数组
    if 'attached' not in children:
        children['attached'] = []
    
    # 批量创建并添加主题
    for topic_data in topics:
        if isinstance(topic_data, str):
            new_topic = create_topic(topic_data)
        else:
            # 使用提供的字典，但确保有id
            new_topic = topic_data.copy()
            if 'id' not in new_topic:
                new_topic['id'] = str(uuid.uuid4())
        
        children['attached'].append(new_topic)
    
    # 保存修改
    modify_content(xmind_path, lambda c: content, output_path)
    
    return content


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description='在XMind文件中插入新主题',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
JSONPath表达式示例:
  $[0].rootTopic                          # 第一个画布的中心主题
  $[0].rootTopic.children.attached[0]     # 第一个画布的第一个分支主题
  $[0].rootTopic.children.attached[?(@.title=="分支主题 1")]  # 按标题查找

使用示例:
  # 在中心主题下添加子主题
  uv run insert_topic.py demo.xmind --parent '$.[0].rootTopic' --title '新子主题'
  
  # 在第一个分支主题下添加子主题（颜色值记得加引号！）
  uv run insert_topic.py demo.xmind --parent '$.[0].rootTopic.children.attached[0]' --title '细分主题'
  
  # 批量添加多个主题
  uv run insert_topic.py demo.xmind --parent '$.[0].rootTopic' --titles '主题1' '主题2' '主题3'
  
  # 保存到新文件
  uv run insert_topic.py demo.xmind --parent '$.[0].rootTopic' --title '新主题' -o output.xmind
        """
    )
    
    parser.add_argument('xmind_file', help='xmind文件路径')
    parser.add_argument('--parent', '-p',
                        help='父主题的JSONPath表达式（使用--list-topics时可选）')
    parser.add_argument('--title', '-t',
                        help='新主题标题（单个）')
    parser.add_argument('--titles', nargs='+',
                        help='多个主题标题（批量添加）')
    parser.add_argument('--id',
                        help='自定义主题ID（默认自动生成UUID）')
    parser.add_argument('--output', '-o',
                        help='输出文件路径（默认覆盖原文件）')
    parser.add_argument('--list-topics', action='store_true',
                        help='列出所有可用的主题路径（用于参考）')
    
    args = parser.parse_args()
    
    try:
        # 如果请求列出主题路径
        if args.list_topics:
            content = read_content(args.xmind_file)
            print("\n可用的JSONPath路径示例:")
            print("-" * 80)
            print(f"$[0].rootTopic                           # 中心主题")
            
            for idx, sheet in enumerate(content):
                root = sheet.get('rootTopic', {})
                children = root.get('children', {}).get('attached', [])
                for child_idx, child in enumerate(children):
                    title = child.get('title', f'主题 {child_idx}')
                    print(f"$[{idx}].rootTopic.children.attached[{child_idx}]  # {title}")
            print("-" * 80)
            return
        
        # 检查参数
        if not args.title and not args.titles:
            print("错误: 必须提供 --title 或 --titles 参数")
            parser.print_help()
            raise SystemExit(1)
        
        output_file = args.output or args.xmind_file
        
        if args.titles:
            # 批量添加
            content = insert_topics_batch(
                args.xmind_file,
                args.parent,
                args.titles,
                output_path=args.output
            )
            print(f"✓ 已在父主题下批量添加 {len(args.titles)} 个主题")
            print(f"  输出文件: {output_file}")
        else:
            # 单个添加
            content = insert_topic(
                args.xmind_file,
                args.parent,
                args.title,
                topic_id=args.id,
                output_path=args.output
            )
            print(f"✓ 已添加主题: {args.title}")
            print(f"  父主题路径: {args.parent}")
            print(f"  输出文件: {output_file}")
            
    except Exception as e:
        print(f"错误: {e}", file=__import__('sys').stderr)
        raise


if __name__ == "__main__":
    main()
