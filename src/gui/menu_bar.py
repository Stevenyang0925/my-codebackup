# 菜单栏模块

from PyQt5.QtWidgets import (QMenuBar, QMenu, QAction, QMessageBox, 
                            QFileDialog, QDialog, QVBoxLayout, QLabel, 
                            QTextBrowser, QDialogButtonBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QKeySequence

import os
import sys

class AboutDialog(QDialog):
    """关于对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("关于")
        self.setFixedSize(500, 300)
        
        layout = QVBoxLayout()
        
        # 添加标题
        title_label = QLabel("多格式文本转Markdown工具")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # 添加版本信息
        version_label = QLabel("版本: 1.0.0")
        version_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(version_label)
        
        # 添加描述
        description = QTextBrowser()
        description.setOpenExternalLinks(True)
        description.setHtml("""
        <p style='text-align:center;'>一个用于将多种格式文本转换为Markdown的工具</p>
        <p style='text-align:center;'>支持Word、Excel、TXT、PDF和图片格式</p>
        <p style='text-align:center;'>基于PyQt5开发</p>
        <br>
        <p style='text-align:center;'>Copyright © 2023 All Rights Reserved</p>
        """)
        layout.addWidget(description)
        
        # 添加按钮
        buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)
        
        self.setLayout(layout)


class HelpDialog(QDialog):
    """帮助对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("使用帮助")
        self.setFixedSize(600, 400)
        
        layout = QVBoxLayout()
        
        # 添加帮助内容
        help_content = QTextBrowser()
        help_content.setOpenExternalLinks(True)
        help_content.setHtml("""
        <h2 style='text-align:center;'>多格式文本转Markdown工具使用指南</h2>
        
        <h3>基本操作</h3>
        <ol>
            <li><strong>选择文件</strong>: 点击"导入文件"按钮或将文件拖放到左侧区域</li>
            <li><strong>设置选项</strong>: 在中央区域配置转换选项</li>
            <li><strong>开始转换</strong>: 点击右侧的"开始转换"按钮</li>
            <li><strong>保存结果</strong>: 转换完成后，点击"保存"按钮将结果保存为Markdown文件</li>
        </ol>
        
        <h3>支持的文件格式</h3>
        <ul>
            <li><strong>Word文档</strong> (.docx)</li>
            <li><strong>Excel表格</strong> (.xlsx)</li>
            <li><strong>文本文件</strong> (.txt)</li>
            <li><strong>PDF文档</strong> (.pdf)</li>
            <li><strong>图片文件</strong> (.jpg, .png, .jpeg)</li>
            <li><strong>Markdown文件</strong> (.md)</li>
        </ul>
        
        <h3>快捷键</h3>
        <ul>
            <li><strong>Ctrl+O</strong>: 打开文件</li>
            <li><strong>Ctrl+S</strong>: 保存Markdown</li>
            <li><strong>Ctrl+N</strong>: 新建</li>
            <li><strong>F1</strong>: 打开帮助</li>
            <li><strong>Ctrl+Q</strong>: 退出程序</li>
        </ul>
        
        <h3>注意事项</h3>
        <ul>
            <li>图片文字识别功能需要安装Tesseract OCR引擎</li>
            <li>处理大文件可能需要较长时间，请耐心等待</li>
            <li>转换过程中请勿关闭程序</li>
        </ul>
        """)
        layout.addWidget(help_content)
        
        # 添加按钮
        buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)
        
        self.setLayout(layout)


class MenuBar(QMenuBar):
    """菜单栏类，提供应用程序的菜单选项"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        
        # 创建菜单
        self.create_file_menu()
        self.create_edit_menu()
        self.create_view_menu()
        self.create_tools_menu()
        self.create_help_menu()
    
    def create_file_menu(self):
        """创建文件菜单"""
        file_menu = QMenu("文件(&F)", self)
        
        # 新建文件
        self.new_action = QAction("新建(&N)", self)
        self.new_action.setShortcut("Ctrl+N")
        file_menu.addAction(self.new_action)
        
        # 打开文件
        self.open_action = QAction("打开(&O)...", self)
        self.open_action.setShortcut("Ctrl+O")
        file_menu.addAction(self.open_action)
        
        # 保存文件
        self.save_action = QAction("保存(&S)", self)
        self.save_action.setShortcut("Ctrl+S")
        file_menu.addAction(self.save_action)
        
        # 另存为
        self.save_as_action = QAction("另存为(&A)...", self)
        self.save_as_action.setShortcut("Ctrl+Shift+S")
        file_menu.addAction(self.save_as_action)
        
        file_menu.addSeparator()
        
        # 退出
        self.exit_action = QAction("退出(&Q)", self)
        self.exit_action.setShortcut("Alt+F4")
        file_menu.addAction(self.exit_action)
        
        self.addMenu(file_menu)
    
    def create_edit_menu(self):
        """创建编辑菜单"""
        edit_menu = QMenu("编辑(&E)", self)
        
        # 撤销
        self.undo_action = QAction("撤销(&U)", self)
        self.undo_action.setShortcut("Ctrl+Z")
        edit_menu.addAction(self.undo_action)
        
        # 重做
        self.redo_action = QAction("重做(&R)", self)
        self.redo_action.setShortcut("Ctrl+Y")
        edit_menu.addAction(self.redo_action)
        
        edit_menu.addSeparator()
        
        # 剪切
        self.cut_action = QAction("剪切(&T)", self)
        self.cut_action.setShortcut("Ctrl+X")
        edit_menu.addAction(self.cut_action)
        
        # 复制
        self.copy_action = QAction("复制(&C)", self)
        self.copy_action.setShortcut("Ctrl+C")
        edit_menu.addAction(self.copy_action)
        
        # 粘贴
        self.paste_action = QAction("粘贴(&P)", self)
        self.paste_action.setShortcut("Ctrl+V")
        edit_menu.addAction(self.paste_action)
        
        self.addMenu(edit_menu)
    
    def create_view_menu(self):
        """创建视图菜单"""
        view_menu = QMenu("视图(&V)", self)
        
        # 显示/隐藏工具栏
        self.show_toolbar_action = QAction("工具栏", self)
        self.show_toolbar_action.setCheckable(True)
        self.show_toolbar_action.setChecked(True)
        view_menu.addAction(self.show_toolbar_action)
        
        # 显示/隐藏状态栏
        self.show_statusbar_action = QAction("状态栏", self)
        self.show_statusbar_action.setCheckable(True)
        self.show_statusbar_action.setChecked(True)
        view_menu.addAction(self.show_statusbar_action)
        
        self.addMenu(view_menu)
    
    def create_tools_menu(self):
        """创建工具菜单"""
        tools_menu = QMenu("工具(&T)", self)
        
        # 设置
        self.settings_action = QAction("设置(&S)...", self)
        tools_menu.addAction(self.settings_action)
        
        self.addMenu(tools_menu)
    
    def create_help_menu(self):
        """创建帮助菜单"""
        help_menu = QMenu("帮助(&H)", self)
        
        # 关于
        self.about_action = QAction("关于(&A)", self)
        help_menu.addAction(self.about_action)
        
        self.addMenu(help_menu)
    
    def connect_actions(self, window):
        """连接菜单动作到窗口的槽函数"""
        # 文件菜单
        if hasattr(window, 'new_file'):
            self.new_action.triggered.connect(window.new_file)
        
        if hasattr(window, 'open_file'):
            self.open_action.triggered.connect(window.open_file)
        
        if hasattr(window, 'save_markdown'):
            self.save_action.triggered.connect(window.save_markdown)
        
        if hasattr(window, 'save_as'):
            self.save_as_action.triggered.connect(window.save_as)
        else:
            # 如果没有save_as方法，可以临时禁用该菜单项
            self.save_as_action.setEnabled(False)
        
        self.exit_action.triggered.connect(window.close)
        
        # 编辑菜单
        if hasattr(window, 'markdown_editor'):
            if hasattr(window.markdown_editor, 'undo'):
                self.undo_action.triggered.connect(window.markdown_editor.undo)
            else:
                self.undo_action.setEnabled(False)
                
            if hasattr(window.markdown_editor, 'redo'):
                self.redo_action.triggered.connect(window.markdown_editor.redo)
            else:
                self.redo_action.setEnabled(False)
                
            if hasattr(window.markdown_editor, 'cut'):
                self.cut_action.triggered.connect(window.markdown_editor.cut)
            else:
                self.cut_action.setEnabled(False)
                
            if hasattr(window.markdown_editor, 'copy'):
                self.copy_action.triggered.connect(window.markdown_editor.copy)
            else:
                self.copy_action.setEnabled(False)
                
            if hasattr(window.markdown_editor, 'paste'):
                self.paste_action.triggered.connect(window.markdown_editor.paste)
            else:
                self.paste_action.setEnabled(False)
        else:
            # 如果没有markdown_editor，禁用所有编辑菜单项
            self.undo_action.setEnabled(False)
            self.redo_action.setEnabled(False)
            self.cut_action.setEnabled(False)
            self.copy_action.setEnabled(False)
            self.paste_action.setEnabled(False)
        
        # 视图菜单
        if hasattr(window, 'tool_bar'):
            self.show_toolbar_action.triggered.connect(
                lambda checked: window.tool_bar.setVisible(checked)
            )
        
        if hasattr(window, 'statusBar'):
            self.show_statusbar_action.triggered.connect(
                lambda checked: window.statusBar.setVisible(checked)
            )
        
        # 工具菜单
        if hasattr(window, 'show_settings_dialog'):
            self.settings_action.triggered.connect(window.show_settings_dialog)
        else:
            self.settings_action.setEnabled(False)
        
        # 帮助菜单
        if hasattr(window, 'show_about_dialog'):
            self.about_action.triggered.connect(window.show_about_dialog)
        else:
            self.about_action.setEnabled(False)
    
    def on_new(self):
        """新建文件"""
        if self.parent():
            self.parent().new_file()
    
    def on_open(self):
        """打开文件"""
        if self.parent():
            self.parent().open_file()
    
    def on_save(self):
        """保存文件"""
        if self.parent():
            self.parent().save_markdown()
    
    def on_save_as(self):
        """另存为文件"""
        if self.parent():
            self.parent().save_markdown_as()
    
    def on_import(self):
        """导入文件"""
        if self.parent():
            self.parent().browse_input_file()
    
    def on_batch_import(self):
        """批量导入文件"""
        if self.parent():
            self.parent().batch_select_files()
    
    def on_exit(self):
        """退出程序"""
        if self.parent():
            self.parent().close()
    
    def on_undo(self):
        """撤销操作"""
        if self.parent() and hasattr(self.parent(), 'markdown_editor'):
            editor = self.parent().markdown_editor.get_current_editor()
            if editor:
                editor.undo()
    
    def on_redo(self):
        """重做操作"""
        if self.parent() and hasattr(self.parent(), 'markdown_editor'):
            editor = self.parent().markdown_editor.get_current_editor()
            if editor:
                editor.redo()
    
    def on_cut(self):
        """剪切操作"""
        if self.parent() and hasattr(self.parent(), 'markdown_editor'):
            editor = self.parent().markdown_editor.get_current_editor()
            if editor:
                editor.cut()
    
    def on_copy(self):
        """复制操作"""
        if self.parent() and hasattr(self.parent(), 'markdown_editor'):
            editor = self.parent().markdown_editor.get_current_editor()
            if editor:
                editor.copy()
    
    def on_paste(self):
        """粘贴操作"""
        if self.parent() and hasattr(self.parent(), 'markdown_editor'):
            editor = self.parent().markdown_editor.get_current_editor()
            if editor:
                editor.paste()
    
    def on_select_all(self):
        """全选操作"""
        if self.parent() and hasattr(self.parent(), 'markdown_editor'):
            editor = self.parent().markdown_editor.get_current_editor()
            if editor:
                editor.selectAll()
    
    def on_preview(self):
        """预览操作"""
        if self.parent() and hasattr(self.parent(), 'markdown_editor'):
            # 切换到预览标签页
            self.parent().markdown_editor.tab_widget.setCurrentIndex(1)
    
    def on_split_view(self, checked):
        """分屏模式操作"""
        if self.parent() and hasattr(self.parent(), 'markdown_editor'):
            # 切换到分屏标签页
            if checked:
                self.parent().markdown_editor.tab_widget.setCurrentIndex(2)
            else:
                self.parent().markdown_editor.tab_widget.setCurrentIndex(0)
    
    def on_zoom_in(self):
        """放大操作"""
        if self.parent() and hasattr(self.parent(), 'markdown_editor'):
            editor = self.parent().markdown_editor.get_current_editor()
            if editor:
                editor.zoomIn(1)
    
    def on_zoom_out(self):
        """缩小操作"""
        if self.parent() and hasattr(self.parent(), 'markdown_editor'):
            editor = self.parent().markdown_editor.get_current_editor()
            if editor:
                editor.zoomOut(1)
    
    def on_reset_zoom(self):
        """重置缩放操作"""
        if self.parent() and hasattr(self.parent(), 'markdown_editor'):
            editor = self.parent().markdown_editor.get_current_editor()
            if editor:
                # 重置缩放级别
                editor.setFont(self.parent().markdown_editor.editor_font)
    
    def on_convert(self):
        """开始转换操作"""
        if self.parent():
            self.parent().convert_to_markdown()
    
    def on_settings(self):
        """设置操作"""
        from .settings_dialog import SettingsDialog
        settings_dialog = SettingsDialog(self.parent())
        settings_dialog.exec_()
    
    def on_help(self):
        """显示帮助内容"""
        help_dialog = HelpDialog(self.parent())
        help_dialog.exec_()
    
    def on_about(self):
        """显示关于对话框"""
        about_dialog = AboutDialog(self.parent())
        about_dialog.exec_()