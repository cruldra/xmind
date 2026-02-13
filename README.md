# XMind Processor

[![Agent Skill](https://img.shields.io/badge/Agent%20Skill-Ready-blue)](https://skills.sh)

> 一个用于程序化创建、读取和修改 XMind 思维导图文件（.xmind）的 Agent Skill。

## 安装

使用 `npx skills` 命令安装到任何支持的 Agent：

```bash
# 安装到项目
npx skills add <your-username>/xmind

# 安装到全局
npx skills add <your-username>/xmind -g

# 安装到特定 Agent
npx skills add <your-username>/xmind -a claude-code -a opencode

# 查看可用技能
npx skills add <your-username>/xmind --list
```

### 支持的 Agent

- ✅ OpenCode
- ✅ Claude Code
- ✅ Cursor
- ✅ Codex
- ✅ Gemini CLI
- ✅ Cline
- ✅ GitHub Copilot
- ✅ Roo Code
- ✅ 以及 [更多 Agent](https://github.com/vercel-labs/skills#supported-agents)

## 功能

- 📖 **解析** - 读取并解析 .xmind 文件内容
- ✨ **创建** - 基于模板创建思维导图，支持自定义标题
- 📝 **插入** - 使用 JSONPath 定位父主题，批量或单个插入子主题
- 🎨 **样式** - 修改画布背景颜色等样式属性
- 🔄 **批量** - 支持批量处理多个思维导图文件

## 快速开始

安装后，Agent 会自动加载此 skill，你可以直接让 Agent 帮你处理 XMind 文件：

```
帮我创建一个名为 "项目规划.xmind" 的思维导图，画布标题是 "Q4规划"，中心主题是 "产品路线图"
```

```
读取 "meeting_notes.xmind" 文件，告诉我里面有哪些主题
```

```
在 "project.xmind" 的中心主题下添加三个子主题：设计、开发、测试
```

## 手动使用

如果你想直接使用 Python 脚本：

```bash
# 克隆仓库
git clone <repository-url>
cd xmind

# 安装依赖
uv add jsonpath-ng

# 或使用 pip
pip install jsonpath-ng
```

### 命令行工具

```bash
# 创建新的思维导图
uv run scripts/create_xmind.py my_new.xmind --sheet-title "项目规划" --root-topic "Q4目标"

# 查看结构
uv run scripts/insert_topic.py templates/demo.xmind --list-topics

# 插入主题
uv run scripts/insert_topic.py my_new.xmind \
    --parent '$[0].rootTopic' \
    --title "新的子主题"

# 设置背景颜色
uv run scripts/set_background.py my_new.xmind --color "#000000FF"
```

### Python API

```python
from scripts.create_xmind import create_xmind
from scripts.insert_topic import insert_topic, insert_topics_batch
from scripts.set_background import set_all_sheets_background

# 创建
 create_xmind("new.xmind", sheet_title="画布", root_topic_title="主题")

# 插入
insert_topics_batch(
    "new.xmind",
    "$[0].rootTopic",
    ["产品", "设计", "开发"]
)

# 设置样式
set_all_sheets_background("new.xmind", color="#000000FF")
```

## 项目结构

```
xmind/
├── SKILL.md                    # Agent Skill 定义（必需）
├── README.md                   # 本文档
├── scripts/                    # Python 脚本
│   ├── xmind_utils.py         # 核心工具（读取/写入）
│   ├── create_xmind.py        # 创建新文件
│   ├── insert_topic.py        # 插入主题
│   └── set_background.py      # 设置背景颜色
├── templates/                 # 模板文件
│   └── demo.xmind            # 空白思维导图模板
└── assets/                    # 其他资源
```

## XMIND 文件格式

XMIND 文件是 ZIP 压缩包，包含：

```
content.xmind (ZIP)
├── content.json      # 主要内容（思维导图结构）
├── metadata.json     # 文件元数据
├── manifest.json     # 包清单
└── Thumbnails/
    └── thumbnail.png # 缩略图
```

### content.json 结构示例

```json
[
  {
    "id": "sheet-id",
    "title": "画布 1",
    "rootTopic": {
      "id": "topic-id",
      "title": "中心主题",
      "children": {
        "attached": [
          {
            "id": "child-id",
            "title": "分支主题 1",
            "children": {
              "attached": []
            }
          }
        ]
      }
    }
  }
]
```

## JSONPath 表达式

用于定位思维导图中的主题：

| 表达式 | 说明 |
|--------|------|
| `$[0].rootTopic` | 第一个画布的中心主题 |
| `$[0].rootTopic.children.attached[0]` | 第一个分支主题 |
| `$[0].rootTopic.children.attached[?(@.title=="标题")]` | 按标题查找 |

## 完整示例

### 示例 1：创建项目规划思维导图

```python
from scripts.create_xmind import create_xmind
from scripts.insert_topic import insert_topics_batch

# 创建
create_xmind("project.xmind", sheet_title="Q1规划", root_topic_title="项目目标")

# 添加主要分支
insert_topics_batch("project.xmind", "$[0].rootTopic", ["产品", "设计", "开发", "测试"])

# 在产品下添加子主题
insert_topics_batch(
    "project.xmind",
    "$[0].rootTopic.children.attached[0]",
    ["需求分析", "用户调研", "竞品分析"]
)
```

### 示例 2：批量处理

```python
from pathlib import Path
from scripts.set_background import set_all_sheets_background

# 批量设置背景
for xmind_file in Path("mindmaps/").glob("*.xmind"):
    set_all_sheets_background(xmind_file, color="#000000FF")
```

### 示例 3：生成周报

```python
from scripts.create_xmind import create_xmind
from scripts.insert_topic import insert_topic

create_xmind("report.xmind", sheet_title="周报", root_topic_title="本周工作")

work_items = [
    "完成了用户登录功能",
    "修复了 5 个 Bug", 
    "编写了技术文档",
    "参加了团队会议"
]

for item in work_items:
    insert_topic("report.xmind", "$[0].rootTopic", item)
```

## 注意事项

1. **颜色值需要引号**：命令行中使用 `"#000000FF"` 而非 `#000000FF`
2. **主题 ID 自动生成**：无需手动指定，脚本会自动生成 UUID
3. **备份原文件**：建议开发时使用 `output` 参数指定输出文件
4. **依赖安装**：首次使用前请确保已安装 `jsonpath-ng`

## 错误处理

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| `FileNotFoundError` | 文件路径不存在 | 检查路径是否正确 |
| `ValueError: 不是有效的xmind文件` | 文件损坏或非 ZIP 格式 | 确保文件有效 |
| `IndexError` | 画布索引超出范围 | 使用 `--list` 查看可用画布 |
| `ModuleNotFoundError` | 未安装依赖 | 运行 `uv add jsonpath-ng` |

## 贡献

欢迎提交 Issue 和 Pull Request！

## License

MIT License

---

<p align="center">
  <a href="https://skills.sh">Discover more skills at skills.sh</a>
</p>
