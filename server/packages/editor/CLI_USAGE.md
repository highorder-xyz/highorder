# HighOrder Editor CLI Usage

## CLI 文件结构简化

将 `cli/` 目录合并为单个 `cli.py` 文件。

### 之前：
```
highorder_editor/
├── cli/
│   ├── __init__.py
│   └── __main__.py
```

### 现在：
```
highorder_editor/
└── cli.py
```

## 使用方法

### 方式 1: 作为模块运行
```bash
python -m highorder_editor.cli init-db
python -m highorder_editor.cli create-user email@example.com password123
python -m highorder_editor.cli help
```

### 方式 2: 安装后使用命令行工具
```bash
# 安装后可以直接使用
pip install -e .

# 使用命令
highorder-editor-cli init-db
highorder-editor-cli create-user email@example.com password123
highorder-editor-cli help
```

## 可用命令

### init-db
初始化数据库架构（创建所有表）

```bash
python -m highorder_editor.cli init-db
```

### create-user
创建新用户

```bash
python -m highorder_editor.cli create-user <email> <password>

# 示例
python -m highorder_editor.cli create-user admin@example.com mypassword123
```

### help
显示帮助信息

```bash
python -m highorder_editor.cli help
```

## 完整工作流程

```bash
# 1. 初始化数据库
python -m highorder_editor.cli init-db

# 2. 创建管理员用户
python -m highorder_editor.cli create-user admin@example.com admin123

# 3. 创建普通用户
python -m highorder_editor.cli create-user user@example.com user123

# 4. 启动编辑器
python -m highorder_editor /path/to/apps 9000
```

## 数据库位置

SQLite 数据库文件：`./editor.db`

可以通过修改 `model.py` 改变位置。
