# HighOrder AppView

HighOrder项目的React UI组件库应用，基于Vue到React的完整迁移。

## 项目概述

AppView是HighOrder项目的React版本UI组件库，包含了42个完整的React组件，实现了与原Vue版本1:1的功能对等。

## 技术栈

- **前端框架**: React 18
- **状态管理**: Zustand
- **样式系统**: TailwindCSS + daisyUI
- **构建工具**: Vite
- **包管理器**: npm

## 目录结构

```
appview/
├── src/
│   ├── components/ui/          # 42个UI组件
│   │   ├── index.js           # 统一导出
│   │   ├── Button.jsx         # 按钮组件
│   │   ├── Input.jsx          # 输入框组件
│   │   ├── DataTable.jsx      # 数据表格组件
│   │   └── ...                # 其他组件
│   ├── store/
│   │   └── appStore.js        # Zustand全局状态
│   ├── i18n/
│   │   └── locales.js         # 国际化配置
│   ├── utils/
│   │   └── index.js           # 工具函数
│   ├── App.jsx                # 主应用组件
│   ├── main.jsx               # 应用入口
│   └── index.css              # 全局样式
├── package.json               # 项目配置
├── vite.config.mjs           # Vite配置
├── tailwind.config.cjs       # TailwindCSS配置
├── postcss.config.cjs        # PostCSS配置
├── index.html                # HTML模板
├── EXAMPLES.md               # 使用示例
└── README.md                 # 项目说明
```

## 组件库

AppView包含42个完整的React组件：

### 基础组件 (5个)
- Button - 按钮组件
- Icon - 图标组件
- IconText - 图标+文本组合
- IconTitle - 图标+标题组合
- Link - 链接组件

### 文本组件 (2个)
- Title - 标题组件
- Paragraph - 段落组件

### 布局组件 (3个)
- Row - 横向布局容器
- Column - 纵向布局容器
- Divider - 分隔线组件

### 导航组件 (2个)
- NavBar - 导航栏组件
- Breadcrumb - 面包屑导航

### 反馈组件 (3个)
- Alert - 警告提示组件
- Modal - 模态框组件
- ProgressBar - 进度条组件

### 卡片组件 (1个)
- Card - 卡片容器组件

### 表单组件 (6个)
- Input - 输入框组件
- TextArea - 文本域组件
- Select - 选择框组件
- Checkbox - 复选框组件
- Radio - 单选框组件
- Switch - 开关组件

### 高级组件 (20个)
- Badge - 徽章组件
- Dropdown - 下拉菜单组件
- Tooltip - 工具提示组件
- Tag - 标签组件
- Avatar - 头像组件
- Tabs - 标签页组件
- List - 列表组件
- DataTable - 数据表格组件
- Pagination - 分页组件
- Accordion - 手风琴组件
- Slider - 滑块组件
- Rating - 评分组件
- Upload - 上传组件
- Calendar - 日历组件
- Menu - 菜单组件
- Carousel - 轮播组件
- Timeline - 时间线组件
- Stepper - 步骤条组件
- ColorPicker - 颜色选择器
- Tree - 树形组件

## 开发

### 安装依赖
```bash
npm install
```

### 启动开发服务器
```bash
npm run dev
```

### 构建生产版本
```bash
npm run build
```

### 预览生产版本
```bash
npm run preview
```

## 特性

- ✅ **完整迁移**: 42个组件100%完成迁移
- ✅ **架构对齐**: Zustand状态管理镜像Vue架构
- ✅ **现代化**: React 18 + TailwindCSS + daisyUI
- ✅ **响应式**: 完美适配移动端和桌面端
- ✅ **主题支持**: 完整的主题切换系统
- ✅ **国际化**: 中英文支持
- ✅ **类型安全**: JSDoc类型提示
- ✅ **高性能**: 优化的渲染和状态管理

## 文档

- [EXAMPLES.md](./EXAMPLES.md) - 详细使用示例
- 组件文档请参考各个组件文件的JSDoc注释

## 许可证

本项目遵循与HighOrder主项目相同的许可证。

---

**项目状态**: ✅ 生产就绪  
**迁移完成**: 2025-12-10  
**技术栈**: React 18 + Zustand + TailwindCSS + daisyUI
