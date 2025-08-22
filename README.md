# Heureka's Blog

> **基于Jekyll的个人技术博客系统**

## 🏗️ 网站架构

### 核心技术栈

- **静态生成引擎**: Jekyll 4.x + GitHub Pages
- **前端框架**: Bootstrap 3.4.1
- **构建工具**: Grunt + Node.js
- **数学公式**: MathJax 3.x
- **搜索功能**: Simple Jekyll Search
- **管理工具**: PyQt5 桌面应用

### 整体架构

```plaintext
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  本地开发环境   │────>│  GitHub Pages   │────>│   线上博客网站   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        ▲                       ▲                      ▲
        │                       │                      │
        └───────────────────────┴──────────────────────┘
                             │
                     ┌───────────────┐
                     │ BlogManage工具 │
                     └───────────────┘
```

## 📁 文件结构

```plaintext
Heureka-L.github.io/
├── .github/workflows/jekyll.yml  # GitHub Actions自动部署配置
├── .gitignore                    # Git忽略文件
├── 404.html                      # 404页面
├── BlogManage/                   # 博客管理工具
│   ├── blog_manager.py           # 主程序
│   ├── requirements.txt          # 依赖包
│   └── templates/                # 文章模板
├── CNAME                         # 自定义域名配置
├── Gemfile                       # Ruby依赖
├── Gruntfile.js                  # Grunt构建配置
├── LICENSE                       # 许可证
├── README.md                     # 项目说明
├── _config.yml                   # Jekyll配置
├── _data/books.yml               # 书籍章节数据
├── _doc/                         # 文档
├── _includes/                    # 可复用组件
│   ├── about/                    # 关于信息
│   ├── nav.html                  # 导航栏
│   ├── footer.html               # 页脚
│   └── short-about.html          # 侧边栏关于
├── _layouts/                     # 页面模板
│   ├── default.html              # 基础模板
│   ├── post.html                 # 文章模板
│   └── book.html                 # 书籍模板
├── _posts/                       # 文章目录
│   ├── 2025-08-17-STM32外部中断标准库配置流程.md
│   ├── data_rep/                 # 数据表示系列
│   └── hidden/                   # 隐藏文章
├── about.html                    # 关于页面
├── archive.html                  # 归档页面
├── books.html                    # 书籍页面
├── config/config.json            # 博客管理工具配置
├── css/                          # 样式文件
├── fonts/                        # 字体文件
├── img/                          # 图片资源
│   ├── 头像.jpg                  # 用户头像
│   ├── bg-little-universe.jpg    # 头部背景
│   └── bk6.jpg                   # 页面背景
├── index.html                    # 首页
├── js/                           # JavaScript文件
├── less/                         # Less样式
├── offline.html                  # 离线页面
├── package-lock.json             # NPM依赖锁
├── package.json                  # NPM依赖
├── pwa/                          # 渐进式Web应用配置
├── search.json                   # 搜索索引
├── sw.js                         # Service Worker
└── 文章发布指南.md                # 文章发布指南
```

## 🔧 环境配置与部署

### 本地开发环境

1. **安装依赖**

```bash
# 安装Ruby依赖
bundle install

# 安装Node.js依赖
npm install
```

2. **本地预览**

```bash
bundle exec jekyll serve
# 访问 http://localhost:4000
```

### GitHub Pages部署

1. **自动部署**
   - 提交代码到`master`分支
   - GitHub Actions会自动执行`.github/workflows/jekyll.yml`进行部署
   - 部署完成后访问: `https://heureka-l.github.io`

2. **手动部署**

```bash
git add .
git commit -m "提交说明"
git push origin master
```

## 🎨 个性化设置

### 用户信息修改

1. **基本信息**
   修改`_config.yml`文件中的以下字段:

```yaml
title: Heureka's Blog       # 博客标题
SEOTitle: Heureka           # SEO标题
description: "这里是 @Heureka 的个人博客..."  # 博客描述
keyword: "HEureka, Hek, Heureka的博客..."   # 关键词
url: "https://Heureka.github.io"  # 博客URL
github_username: Heureka-L  # GitHub用户名
sidebar-about-description: "励志成为嵌入式工程师 <br> React Team @ Meta"  # 侧边栏描述
```

2. **头像和背景图**

- **头像**: 替换`img/头像.jpg`文件
- **头部背景**: 替换`img/bg-little-universe.jpg`文件
- **页面背景**: 替换`img/bk6.jpg`文件

3. **导航菜单**
   编辑`_includes/nav.html`文件自定义导航链接

## 📝 BlogManage工具使用

### 功能介绍

- 📚 **书籍章节管理**: 可视化管理`_data/books.yml`
- 📝 **文章创建**: 通过表单快速生成符合格式的文章
- 🎨 **模板选择**: 支持通用模板和STM32专用模板
- 🔄 **自动更新**: 自动更新书籍章节信息

### 运行方法

1. **安装依赖**

```bash
cd BlogManage
pip install -r requirements.txt
```

2. **启动程序**

```bash
python blog_manager.py
```

### 打包成EXE程序

使用PyInstaller将工具打包成Windows可执行文件:

1. **安装PyInstaller**

```bash
pip install pyinstaller
```

2. **生成EXE文件**

```bash
cd BlogManage
pyinstaller --onefile --windowed --icon=../img/favicon.ico blog_manager.py
```

3. **获取EXE文件**
   生成的EXE文件位于`dist`目录下

## ✍️ 文章发布流程

1. **使用BlogManage工具**
   - 选择书籍和章节
   - 填写文章信息和内容
   - 点击"保存文章"

2. **手动编辑完善**
   - 工具会自动用VS Code打开生成的文章
   - 进一步编辑和完善内容

3. **提交发布**
   - 保存文章后会自动更新`_data/books.yml`
   - 提交代码到GitHub自动部署

## 📚 文章格式规范

### 元数据格式

```yaml
---
layout: book
book: "STM32开发指南"
chapter: "第2章：定时器应用"
section: "2.1 STM32定时器标准库配置流程"
title: "STM32定时器标准库配置流程"
subtitle: "从寄存器到应用的完整配置指南"
date: 2025-08-18 14:30:00
tags: [定时器, 标准库, 寄存器配置]
---
```

### 内容格式
- 使用Markdown语法
- 支持代码块、表格、列表等
- 数学公式使用`$$`包围

## 🐛 常见问题

1. **文章不显示在书籍目录中?**
   - 检查`_data/books.yml`中的`slug`是否匹配
   - 确认文章使用了`layout: book`
   - 验证`book`字段与书籍名称一致

2. **本地预览样式异常?**
   - 确保已安装所有依赖
   - 尝试清除缓存: `bundle exec jekyll clean`

3. **BlogManage工具无法运行?**
   - 检查Python版本(需Python 3.6+)
   - 确认已安装所有依赖: `pip install -r requirements.txt`

---

**文档版本**: v4.0

**最后更新**: {{ site.time | date: '%Y年%m月%d日' }}

**维护者**: Heureka

**GitHub**: [Heureka-L/Heureka-L.github.io](https://github.com/Heureka-L/Heureka-L.github.io)
