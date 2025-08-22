#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
博客管理工具 - PyQt版
基于文章发布指南的自动化管理脚本
"""

import sys
import os
import yaml
import re
import json
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QTextEdit, 
                             QPushButton, QComboBox, QDateEdit, QTabWidget,
                             QTableWidget, QTableWidgetItem, QMessageBox,
                             QFileDialog, QGroupBox, QFormLayout, QSplitter,
                             QCheckBox, QSpinBox)
from PyQt5.QtCore import Qt, QDate, QTimer
from PyQt5.QtGui import QFont

CONFIG_DIR = 'config'
CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.json')

class BlogManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.project_root = None
        self.books_file = None
        self.posts_dir = None
        self.setup_success = False
        
        # 加载配置或进行首次设置
        if not self.load_config_or_setup():
            # 如果设置被取消，标记设置失败
            self.setup_success = False
            return
            
        self.setup_success = True
            
        self.init_ui()
        self.load_books_data()
        
    def load_config_or_setup(self):
        """加载配置或提示用户进行设置"""
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    project_root = config.get('project_root')
                    if project_root and self.validate_project_root(project_root):
                        self.set_project_paths(project_root)
                        return True
        except (FileNotFoundError, json.JSONDecodeError):
            pass
            
        return self.prompt_for_project_root(is_initial_setup=True)
        
    def validate_project_root(self, path):
        """验证项目根目录是否有效"""
        return os.path.isdir(os.path.join(path, '_data')) and \
               os.path.isdir(os.path.join(path, '_posts'))
               
    def set_project_paths(self, root_path):
        """设置项目相关路径"""
        self.project_root = root_path
        self.books_file = os.path.join(root_path, '_data', 'books.yml')
        self.posts_dir = os.path.join(root_path, '_posts')
        
    def save_config(self):
        """保存配置到文件"""
        config = {'project_root': self.project_root}
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
            
    def prompt_for_project_root(self, is_initial_setup=False):
        """提示用户选择项目根目录"""
        if is_initial_setup:
            result = QMessageBox.information(self, "首次运行设置", 
                                         "请选择您的Jekyll博客项目根目录\n"
                                         "该目录应包含 _data 和 _posts 文件夹。",
                                         QMessageBox.Ok | QMessageBox.Cancel)
            if result == QMessageBox.Cancel:
                return False
        
        directory = QFileDialog.getExistingDirectory(
            self,
            "选择项目根目录",
            os.path.expanduser("~")
        )
        
        if directory:
            if self.validate_project_root(directory):
                self.set_project_paths(directory)
                self.save_config()
                if not is_initial_setup:
                    QMessageBox.information(self, "成功", f"项目目录已更新为：\n{directory}")
                    self.root_path_label.setText(directory)
                    self.refresh_data()
                return True
            else:
                QMessageBox.warning(self, "错误", 
                                 "所选目录无效！\n请确保目录中包含 _data 和 _posts 文件夹。")
                return self.prompt_for_project_root(is_initial_setup)
        
        if is_initial_setup:
            QMessageBox.critical(self, "错误", "未选择项目目录，程序将退出。")
        return False
        
    def init_ui(self):
        self.setWindowTitle('博客文章管理器')
        self.setGeometry(100, 100, 1200, 800)
        
        # 创建主窗口部件
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # 创建标签页
        self.tabs = QTabWidget()
        self.create_overview_tab()
        self.create_add_article_tab()
        self.create_settings_tab()  # 添加设置标签页
        
        layout = QVBoxLayout()
        layout.addWidget(self.tabs)
        main_widget.setLayout(layout)
        
    def create_settings_tab(self):
        """创建设置标签页"""
        settings_widget = QWidget()
        layout = QVBoxLayout()
        
        # 项目设置组
        group = QGroupBox("项目设置")
        form_layout = QFormLayout()
        
        # 显示当前项目路径
        self.root_path_label = QLineEdit(self.project_root)
        self.root_path_label.setReadOnly(True)
        form_layout.addRow("当前项目根目录:", self.root_path_label)
        
        # 更改目录按钮
        change_dir_btn = QPushButton("更改目录")
        change_dir_btn.clicked.connect(lambda: self.prompt_for_project_root())
        form_layout.addRow(change_dir_btn)
        
        group.setLayout(form_layout)
        layout.addWidget(group)
        layout.addStretch()
        
        settings_widget.setLayout(layout)
        self.tabs.addTab(settings_widget, "设置")
        
    def create_overview_tab(self):
        """创建概览标签页"""
        overview_widget = QWidget()
        layout = QHBoxLayout()
        
        # 左侧书籍列表
        left_group = QGroupBox("书籍列表")
        left_layout = QVBoxLayout()
        
        self.books_table = QTableWidget()
        self.books_table.setColumnCount(3)
        self.books_table.setHorizontalHeaderLabels(['书籍名称', '章节数', '文章总数'])
        self.books_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.books_table.itemClicked.connect(self.show_book_details)
        
        left_layout.addWidget(self.books_table)
        left_group.setLayout(left_layout)
        
        # 右侧详情
        right_group = QGroupBox("详细信息")
        right_layout = QVBoxLayout()
        
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        right_layout.addWidget(self.details_text)
        
        # 刷新按钮
        refresh_btn = QPushButton("刷新数据")
        refresh_btn.clicked.connect(self.refresh_data)
        right_layout.addWidget(refresh_btn)
        
        right_group.setLayout(right_layout)
        
        layout.addWidget(left_group, 1)
        layout.addWidget(right_group, 2)
        overview_widget.setLayout(layout)
        
        self.tabs.addTab(overview_widget, "文章概览")
        
    def create_add_article_tab(self):
        """创建添加文章标签页"""
        add_widget = QWidget()
        layout = QVBoxLayout()
        
        # 快捷填充组
        quick_group = QGroupBox("快捷填充")
        quick_layout = QVBoxLayout()
        
        # 自动编号
        auto_layout = QHBoxLayout()
        self.auto_number = QCheckBox("自动编号")
        self.auto_number.setChecked(True)
        self.auto_number.toggled.connect(self.toggle_auto_number)
        auto_layout.addWidget(self.auto_number)
        
        self.chapter_spin = QSpinBox()
        self.chapter_spin.setRange(1, 20)
        self.chapter_spin.setValue(1)
        self.chapter_spin.setPrefix("第")
        self.chapter_spin.setSuffix("章")
        self.chapter_spin.valueChanged.connect(self.auto_fill_chapter)
        auto_layout.addWidget(QLabel("章节:"))
        auto_layout.addWidget(self.chapter_spin)
        
        self.section_spin = QSpinBox()
        self.section_spin.setRange(1, 10)
        self.section_spin.setValue(1)
        self.section_spin.valueChanged.connect(self.auto_fill_section)
        auto_layout.addWidget(QLabel("小节:"))
        auto_layout.addWidget(self.section_spin)
        quick_layout.addLayout(auto_layout)
        
        # 快捷填充按钮
        fill_buttons = QHBoxLayout()
        fill_chapter_btn = QPushButton("填充章节")
        fill_chapter_btn.clicked.connect(lambda: self.auto_fill_chapter_text())
        fill_buttons.addWidget(fill_chapter_btn)
        
        fill_section_btn = QPushButton("填充小节")
        fill_section_btn.clicked.connect(lambda: self.auto_fill_section_text())
        fill_buttons.addWidget(fill_section_btn)
        
        quick_layout.addLayout(fill_buttons)
        quick_group.setLayout(quick_layout)
        layout.addWidget(quick_group)
        
        # 文章信息表单
        form_group = QGroupBox("文章信息")
        form_layout = QFormLayout()
        
        self.book_combo = QComboBox()
        self.book_combo.setEditable(True)
        self.book_combo.setPlaceholderText("选择或输入书籍名称")
        
        self.chapter_input = QLineEdit()
        self.chapter_input.setPlaceholderText("例如：第1章：XXX")
        
        self.section_input = QLineEdit()
        self.section_input.setPlaceholderText("例如：1.1")
        
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("文章标题")
        self.subtitle_input = QLineEdit()
        self.subtitle_input.setPlaceholderText("副标题（可选）")
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        
        self.tags_input = QLineEdit()
        self.tags_input.setPlaceholderText("标签，用逗号分隔")
        
        self.description_text = QTextEdit()
        self.description_text.setMaximumHeight(80)
        self.description_text.setPlaceholderText("文章描述（可选）")
        
        self.content_text = QTextEdit()
        self.content_text.setPlaceholderText("文章内容（支持Markdown格式）")
        
        form_layout.addRow("书籍：", self.book_combo)
        form_layout.addRow("章节：", self.chapter_input)
        form_layout.addRow("小节：", self.section_input)
        form_layout.addRow("标题：", self.title_input)
        form_layout.addRow("副标题：", self.subtitle_input)
        form_layout.addRow("日期：", self.date_edit)
        form_layout.addRow("标签：", self.tags_input)
        form_layout.addRow("描述：", self.description_text)
        form_layout.addRow("内容：", self.content_text)
        
        form_group.setLayout(form_layout)
        
        # 预览区域
        preview_group = QGroupBox("预览")
        preview_layout = QVBoxLayout()
        self.preview_text = QTextEdit()
        self.preview_text.setMaximumHeight(150)
        preview_layout.addWidget(self.preview_text)
        preview_group.setLayout(preview_layout)
        
        # 操作按钮
        button_layout = QHBoxLayout()
        
        preview_btn = QPushButton("预览")
        preview_btn.clicked.connect(self.preview_article)
        
        save_btn = QPushButton("保存文章")
        save_btn.clicked.connect(self.save_article)
        
        clear_btn = QPushButton("清空")
        clear_btn.clicked.connect(self.clear_form)
        
        button_layout.addWidget(preview_btn)
        button_layout.addWidget(save_btn)
        button_layout.addWidget(clear_btn)
        
        layout.addWidget(form_group)
        layout.addWidget(preview_group)
        layout.addLayout(button_layout)
        add_widget.setLayout(layout)
        
        self.tabs.addTab(add_widget, "添加文章")
        
    def load_books_data(self):
        """加载书籍数据"""
        try:
            with open(self.books_file, 'r', encoding='utf-8') as f:
                self.books_data = yaml.safe_load(f) or {'books': []}
            self.update_books_list()
        except Exception as e:
            QMessageBox.warning(self, "警告", f"加载书籍数据失败: {str(e)}")
            self.books_data = {'books': []}
            
    def update_books_list(self):
        """更新书籍下拉列表"""
        self.book_combo.clear()
        book_names = [book['name'] for book in self.books_data['books']]
        self.book_combo.addItems(book_names)
        
    def refresh_data(self):
        """刷新数据"""
        self.load_books_data()
        self.display_books_overview()
        
    def display_books_overview(self):
        """显示书籍概览"""
        self.books_table.setRowCount(0)
        
        for book in self.books_data['books']:
            row = self.books_table.rowCount()
            self.books_table.insertRow(row)
            
            # 计算章节数和文章数
            chapter_count = len(book.get('chapters', []))
            article_count = sum(len(chapter.get('sections', [])) 
                              for chapter in book.get('chapters', []))
            
            self.books_table.setItem(row, 0, QTableWidgetItem(book['name']))
            self.books_table.setItem(row, 1, QTableWidgetItem(str(chapter_count)))
            self.books_table.setItem(row, 2, QTableWidgetItem(str(article_count)))
            
    def show_book_details(self, item):
        """显示书籍详情"""
        row = item.row()
        book_name = self.books_table.item(row, 0).text()
        
        for book in self.books_data['books']:
            if book['name'] == book_name:
                details = f"书籍名称: {book['name']}\n"
                details += f"章节数量: {len(book.get('chapters', []))}\n"
                details += f"文章总数: {sum(len(chapter.get('sections', [])) for chapter in book.get('chapters', []))}\n\n"
                
                details += "章节详情:\n"
                for i, chapter in enumerate(book.get('chapters', []), 1):
                    details += f"  {chapter['name']} ({len(chapter.get('sections', []))}篇文章)\n"
                    for section in chapter.get('sections', []):
                        details += f"    - {section['name']}\n"
                        
                self.details_text.setPlainText(details)
                break
                
    def preview_article(self):
        """预览文章"""
        article_data = self.get_article_data()
        if not article_data:
            return
            
        preview_text = f"""---
layout: book
title: "{article_data['title']}"
"""
        
        if article_data['subtitle']:
            preview_text += f"subtitle: {article_data['subtitle']}\n"
            
        preview_text += f"""date: {article_data['date'].strftime('%Y-%m-%d %H:%M:%S')}
author: Heureka
book: "{article_data['book']}"
chapter: "{article_data['chapter']}"
section: "{article_data['section']}"
tags: 
    - {article_data['tags']}
---

{article_data['content']}
"""
        
        QMessageBox.information(self, "文章预览", preview_text)
        
    def get_article_data(self):
        """获取文章数据"""
        book = self.book_combo.currentText().strip()
        chapter = self.chapter_input.text().strip()
        section = self.section_input.text().strip()
        title = self.title_input.text().strip()
        
        if not all([book, chapter, section, title]):
            QMessageBox.warning(self, "警告", "请填写所有必填字段")
            return None
            
        return {
            'book': book,
            'chapter': chapter,
            'section': section,
            'title': title,
            'subtitle': self.subtitle_input.text().strip(),
            'date': self.date_edit.date().toPyDate(),
            'tags': self.tags_input.text().strip() or 'General',
            'content': self.content_text.toPlainText().strip()
        }
        
    def save_article(self):
        """保存文章"""
        try:
            book = self.book_combo.currentText().strip()
            chapter = self.chapter_input.text().strip()
            section = self.section_input.text().strip()
            title = self.title_input.text().strip()
            tags = self.tags_input.text().strip()
            description = self.description_text.toPlainText().strip()
            content = self.content_text.toPlainText().strip()

            if not all([book, chapter, section, title]):
                QMessageBox.warning(self, "警告", "请填写完整的书籍、章节、小节和标题信息！")
                return

            # 生成日期字符串
            date_str = datetime.now().strftime("%Y-%m-%d")
            
            # 生成标题slug
            title_slug = re.sub(r'[^\w\s-]', '', title.lower())
            title_slug = re.sub(r'[-\s]+', '-', title_slug).strip('-')
            
            # 生成完整slug
            full_slug = f"{date_str}-{title_slug}"
            
            # 生成文件名
            filename = f"{full_slug}.md"
            
            # 生成URL路径
            url_path = f"/{date_str.replace('-', '/')}/{title_slug}/"
            
            # 生成章节和小节的格式化字符串
            formatted_section = f"{section} {title}"

            article_data = {
                'book': book,
                'chapter': chapter,
                'section': section,
                'title': title,
                'slug': full_slug,
                'url': url_path,
                'tags': tags,
                'description': description,
                'content': content,
                'date': date_str,
                'filename': filename
            }

            # 更新books.yml
            self.update_books_data_exact(article_data)
            
            # 创建文章文件
            filepath = self.create_article_file_exact(article_data)
            
            QMessageBox.information(self, "成功", "文章保存成功！")
            
            # 尝试用VS Code打开文件，如果失败则使用系统默认程序
            try:
                import subprocess
                
                # 首先尝试用VS Code打开
                try:
                    subprocess.Popen(['code', filepath])
                except FileNotFoundError:
                    # VS Code不可用，使用系统默认程序
                    if sys.platform == 'win32':
                        os.startfile(filepath)
                    else:
                        # 在Linux/Mac上使用xdg-open/open
                        opener = 'xdg-open' if sys.platform.startswith('linux') else 'open'
                        subprocess.call([opener, filepath])
            except Exception as e:
                print(f"无法打开文件：{str(e)}")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存失败：{str(e)}")

    def update_books_data_exact(self, article_data):
        """精确更新books.yml文件，使用正确的数据结构"""
        try:
            # 读取现有数据
            with open(self.books_file, 'r', encoding='utf-8') as f:
                books_data = yaml.safe_load(f) or {'books': []}
        except FileNotFoundError:
            books_data = {'books': []}
        except yaml.YAMLError:
            books_data = {'books': []}

        book = article_data['book']
        chapter = article_data['chapter']
        section = article_data['section']
        title = article_data['title']
        
        # 生成章节和小节的格式化字符串
        formatted_section = f"{section} {title}"

        # 查找或创建书籍
        book_found = None
        for b in books_data['books']:
            if b['name'] == book:
                book_found = b
                break
        
        if book_found is None:
            book_found = {
                'name': book,
                'chapters': []
            }
            books_data['books'].append(book_found)

        # 查找或创建章节
        chapter_found = None
        for c in book_found['chapters']:
            if c['name'] == chapter:
                chapter_found = c
                break
        
        if chapter_found is None:
            chapter_found = {
                'name': chapter,
                'sections': []
            }
            book_found['chapters'].append(chapter_found)

        # 查找或更新小节
        section_found = None
        for s in chapter_found['sections']:
            if s['name'] == formatted_section:
                section_found = s
                break
        
        if section_found is None:
            section_found = {
                'name': formatted_section,
                'slug': article_data['slug'],
                'url': article_data['url']
            }
            chapter_found['sections'].append(section_found)
        else:
            # 更新现有小节
            section_found['slug'] = article_data['slug']
            section_found['url'] = article_data['url']

        # 对章节和小节进行排序
        def extract_number(text):
            # 从文本中提取数字，用于排序
            match = re.search(r'第?(\d+)章?|(\d+)\.', text)
            if match:
                return int(match.group(1) or match.group(2))
            return float('inf')
        
        # 对每本书的章节进行排序
        for book in books_data['books']:
            book['chapters'].sort(key=lambda x: extract_number(x['name']))
            # 对每个章节的小节进行排序
            for chapter in book['chapters']:
                chapter['sections'].sort(key=lambda x: extract_number(x['name'].split()[0]))

        # 写入文件
        with open(self.books_file, 'w', encoding='utf-8') as f:
            yaml.dump(books_data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

    def create_article_file_exact(self, article_data):
        """创建文章文件，使用book布局格式"""
        # 生成日期字符串
        date_str = datetime.now().strftime('%Y-%m-%d')
        title_slug = self.generate_slug(article_data['title'])
        
        # 文件名格式：2025-08-17-STM32-GPIO-configuration.md
        filename = f"{date_str}-{title_slug}.md"
        filepath = os.path.join(self.posts_dir, filename)
        
        # slug格式：2025-08-20-pwm（包含完整日期）
        slug = f"{date_str}-{title_slug}"
        
        # URL路径格式：/2025/08/20/标题/（使用slug）
        url_path = f"/{date_str.replace('-', '/')}/{title_slug}/"
        
        # 构建YAML front matter - 使用book布局格式
        content = f"""---
layout: book
title: "{article_data['title']}"
"""
        
        if article_data.get('subtitle'):
            content += f"subtitle: {article_data['subtitle']}"
            
        content += f"""date: {date_str} 10:00:00
author: Heureka
book: "{article_data['book']}"
chapter: "{article_data['chapter']}"
section: "{article_data['section']}"
tags:
"""
        
        # 处理标签
        tags = article_data.get('tags', '').strip()
        if tags:
            tag_list = [tag.strip() for tag in tags.split(',')]
            for tag in tag_list:
                content += f"    - {tag}\n"
        else:
            content += "    - General\n"
            
        content += "---\n\n"
        content += article_data.get('content', '')
        
        # 写入文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return filepath

    def clear_form(self):
        """清空表单"""
        self.title_input.clear()
        self.subtitle_input.clear()
        self.chapter_input.clear()
        self.section_input.clear()
        self.tags_input.clear()
        self.content_text.clear()
        self.date_edit.setDate(QDate.currentDate())
        self.preview_text.clear()
        
    def toggle_auto_number(self, checked):
        """切换自动编号状态"""
        self.chapter_spin.setEnabled(checked)
        self.section_spin.setEnabled(checked)
        
    def auto_fill_chapter(self, value):
        """自动填充章节"""
        if self.auto_number.isChecked():
            self.chapter_input.setText(f"第{value}章")
            
    def auto_fill_section(self, value):
        """自动填充小节"""
        if self.auto_number.isChecked():
            chapter_num = self.chapter_spin.value()
            self.section_input.setText(f"{chapter_num}.{value}")
            
    def auto_fill_chapter_text(self):
        """手动填充章节"""
        chapter_num = self.chapter_spin.value()
        self.chapter_input.setText(f"第{chapter_num}章")
        
    def auto_fill_section_text(self):
        """手动填充小节"""
        chapter_num = self.chapter_spin.value()
        section_num = self.section_spin.value()
        self.section_input.setText(f"{chapter_num}.{section_num}")

    def generate_slug(self, text):
        """生成URL友好的slug"""
        import urllib.parse
        # 转换为小写，移除非字母数字字符，替换空格为连字符
        slug = re.sub(r'[^\w\s-]', '', text.lower())
        slug = re.sub(r'[-\s]+', '-', slug).strip('-')
        # 如果slug为空（纯中文情况），使用原始文本的URL编码
        if not slug:
            slug = urllib.parse.quote(text)
        return slug

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # 设置中文字体
    font = QFont("Microsoft YaHei", 9)
    app.setFont(font)

    # 首次运行判断：检查 config 文件夹是否存在
    if not os.path.isdir(CONFIG_DIR):
        # 提示用户选择项目根目录并保存到 config/config.json，然后提示重启并退出
        QMessageBox.information(None, '首次运行设置', '首次运行：请在下一步选择您的项目根目录（包含 _data 和 _posts 文件夹）。')
        directory = QFileDialog.getExistingDirectory(None, '选择项目根目录', os.path.expanduser('~'))
        if directory:
            if os.path.isdir(os.path.join(directory, '_data')) and os.path.isdir(os.path.join(directory, '_posts')):
                try:
                    os.makedirs(CONFIG_DIR, exist_ok=True)
                    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                        json.dump({'project_root': directory}, f, ensure_ascii=False, indent=4)
                except Exception as e:
                    QMessageBox.critical(None, '错误', f'保存配置失败：{e}')
                    sys.exit(1)

                # 使用非模态提示框并在 1 秒后退出
                msg = QMessageBox()
                msg.setWindowTitle('完成')
                msg.setText('配置已保存。请重启软件以使更改生效。程序将在 1 秒后退出。')
                msg.setStandardButtons(QMessageBox.NoButton)
                msg.show()
                QTimer.singleShot(1000, lambda: (msg.close(), sys.exit(0)))
                app.exec_()
                sys.exit(0)
            else:
                QMessageBox.critical(None, '无效目录', '所选目录不包含 _data 或 _posts，程序将退出。')
                sys.exit(1)
        else:
            QMessageBox.critical(None, '未选择目录', '未选择项目目录，程序将退出。')
            sys.exit(1)

    # config 目录存在，正常启动
    manager = BlogManager()
    if manager.setup_success:
        manager.show()
        sys.exit(app.exec_())
    else:
        # 未完成设置，退出
        sys.exit(0)