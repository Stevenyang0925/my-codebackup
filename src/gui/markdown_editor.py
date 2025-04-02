# Markdown编辑器模块

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, 
                            QTextEdit, QSplitter, QPushButton, QToolBar, 
                            QAction, QLabel, QComboBox)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon, QTextCursor, QTextCharFormat, QColor

import markdown
import os

class MarkdownEditor(QWidget):
    """Markdown编辑器组件，提供编辑和预览功能"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 设置字体
        self.editor_font = QFont("Consolas", 11)
        self.preview_font = QFont("Microsoft YaHei", 11)
        
        # 初始化UI
        self.init_ui()
    
    def init_ui(self):
        """初始化UI组件"""
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建工具栏
        self.create_toolbar()
        main_layout.addWidget(self.toolbar)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        
        # 创建编辑器页面
        self.editor_widget = QWidget()
        editor_layout = QVBoxLayout(self.editor_widget)
        editor_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建编辑器
        self.editor = QTextEdit()
        self.editor.setFont(self.editor_font)
        self.editor.setAcceptRichText(False)  # 只接受纯文本
        self.editor.setLineWrapMode(QTextEdit.WidgetWidth)
        self.editor.textChanged.connect(self.update_preview)
        
        # 设置编辑器样式
        self.editor.setStyleSheet("""
            QTextEdit {
                background-color: #FFFFFF;
                color: #333333;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        
        editor_layout.addWidget(self.editor)
        
        # 创建预览页面
        self.preview_widget = QWidget()
        preview_layout = QVBoxLayout(self.preview_widget)
        preview_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建预览区域
        self.preview = QTextEdit()
        self.preview.setFont(self.preview_font)
        self.preview.setReadOnly(True)
        
        # 设置预览区域样式
        self.preview.setStyleSheet("""
            QTextEdit {
                background-color: #FFFFFF;
                color: #333333;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        
        preview_layout.addWidget(self.preview)
        
        # 创建分屏页面
        self.split_widget = QWidget()
        split_layout = QVBoxLayout(self.split_widget)
        split_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建分割器
        splitter = QSplitter(Qt.Horizontal)
        
        # 创建分屏编辑器
        self.split_editor = QTextEdit()
        self.split_editor.setFont(self.editor_font)
        self.split_editor.setAcceptRichText(False)
        self.split_editor.setLineWrapMode(QTextEdit.WidgetWidth)
        self.split_editor.textChanged.connect(self.update_split_preview)
        
        # 设置分屏编辑器样式
        self.split_editor.setStyleSheet("""
            QTextEdit {
                background-color: #FFFFFF;
                color: #333333;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        
        # 创建分屏预览区域
        self.split_preview = QTextEdit()
        self.split_preview.setFont(self.preview_font)
        self.split_preview.setReadOnly(True)
        
        # 设置分屏预览区域样式
        self.split_preview.setStyleSheet("""
            QTextEdit {
                background-color: #FFFFFF;
                color: #333333;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        
        # 添加到分割器
        splitter.addWidget(self.split_editor)
        splitter.addWidget(self.split_preview)
        splitter.setSizes([int(self.width() / 2), int(self.width() / 2)])
        
        split_layout.addWidget(splitter)
        
        # 添加标签页
        self.tab_widget.addTab(self.editor_widget, "编辑")
        self.tab_widget.addTab(self.preview_widget, "预览")
        self.tab_widget.addTab(self.split_widget, "分屏")
        
        # 连接标签页切换信号
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        
        # 添加到主布局
        main_layout.addWidget(self.tab_widget)
    
    def create_toolbar(self):
        """创建工具栏"""
        self.toolbar = QToolBar()
        self.toolbar.setIconSize(QSize(16, 16))
        self.toolbar.setMovable(False)
        
        # 添加标题下拉框
        heading_label = QLabel("标题: ")
        self.toolbar.addWidget(heading_label)
        
        self.heading_combo = QComboBox()
        self.heading_combo.addItem("正文")
        self.heading_combo.addItem("标题 1")
        self.heading_combo.addItem("标题 2")
        self.heading_combo.addItem("标题 3")
        self.heading_combo.addItem("标题 4")
        self.heading_combo.addItem("标题 5")
        self.heading_combo.addItem("标题 6")
        self.heading_combo.currentIndexChanged.connect(self.apply_heading)
        self.toolbar.addWidget(self.heading_combo)
        
        self.toolbar.addSeparator()
        
        # 添加格式化按钮
        bold_action = QAction("B", self)
        bold_action.setToolTip("粗体")
        bold_action.triggered.connect(lambda: self.apply_format("**"))
        self.toolbar.addAction(bold_action)
        
        italic_action = QAction("I", self)
        italic_action.setToolTip("斜体")
        italic_action.triggered.connect(lambda: self.apply_format("*"))
        self.toolbar.addAction(italic_action)
        
        self.toolbar.addSeparator()
        
        # 添加列表按钮
        bullet_list_action = QAction("• 列表", self)
        bullet_list_action.setToolTip("无序列表")
        bullet_list_action.triggered.connect(self.apply_bullet_list)
        self.toolbar.addAction(bullet_list_action)
        
        numbered_list_action = QAction("1. 列表", self)
        numbered_list_action.setToolTip("有序列表")
        numbered_list_action.triggered.connect(self.apply_numbered_list)
        self.toolbar.addAction(numbered_list_action)
        
        self.toolbar.addSeparator()
        
        # 添加链接和图片按钮
        link_action = QAction("链接", self)
        link_action.setToolTip("插入链接")
        link_action.triggered.connect(self.insert_link)
        self.toolbar.addAction(link_action)
        
        image_action = QAction("图片", self)
        image_action.setToolTip("插入图片")
        image_action.triggered.connect(self.insert_image)
        self.toolbar.addAction(image_action)
        
        self.toolbar.addSeparator()
        
        # 添加代码按钮
        code_action = QAction("代码", self)
        code_action.setToolTip("插入代码块")
        code_action.triggered.connect(self.insert_code_block)
        self.toolbar.addAction(code_action)
        
        quote_action = QAction("引用", self)
        quote_action.setToolTip("插入引用")
        quote_action.triggered.connect(self.insert_quote)
        self.toolbar.addAction(quote_action)
    
    def on_tab_changed(self, index):
        """标签页切换事件处理"""
        if index == 0:  # 编辑标签页
            # 如果从分屏切换到编辑，同步内容
            if self.tab_widget.currentWidget() == self.editor_widget and self.split_editor.toPlainText():
                self.editor.setPlainText(self.split_editor.toPlainText())
        elif index == 1:  # 预览标签页
            # 更新预览内容
            self.update_preview()
        elif index == 2:  # 分屏标签页
            # 如果从编辑切换到分屏，同步内容
            if self.tab_widget.currentWidget() == self.split_widget and self.editor.toPlainText():
                self.split_editor.setPlainText(self.editor.toPlainText())
                self.update_split_preview()
    
    def update_preview(self):
        """更新预览内容"""
        md_text = self.editor.toPlainText()
        html = self.markdown_to_html(md_text)
        self.preview.setHtml(html)
    
    def update_split_preview(self):
        """更新分屏预览内容"""
        md_text = self.split_editor.toPlainText()
        html = self.markdown_to_html(md_text)
        self.split_preview.setHtml(html)
    
    def markdown_to_html(self, md_text):
        """将Markdown文本转换为HTML"""
        try:
            # 使用Python-Markdown库进行转换
            html = markdown.markdown(
                md_text,
                extensions=[
                    'markdown.extensions.tables',
                    'markdown.extensions.fenced_code',
                    'markdown.extensions.codehilite',
                    'markdown.extensions.toc'
                ]
            )
            
            # 添加基本样式
            styled_html = f"""
            <html>
            <head>
                <style>
                    body {{
                        font-family: 'Microsoft YaHei', sans-serif;
                        line-height: 1.6;
                        color: #333333;
                        padding: 10px;
                    }}
                    h1, h2, h3, h4, h5, h6 {{
                        margin-top: 24px;
                        margin-bottom: 16px;
                        font-weight: 600;
                        line-height: 1.25;
                    }}
                    h1 {{ font-size: 2em; border-bottom: 1px solid #eaecef; padding-bottom: .3em; }}
                    h2 {{ font-size: 1.5em; border-bottom: 1px solid #eaecef; padding-bottom: .3em; }}
                    h3 {{ font-size: 1.25em; }}
                    h4 {{ font-size: 1em; }}
                    h5 {{ font-size: .875em; }}
                    h6 {{ font-size: .85em; color: #6a737d; }}
                    p {{ margin-top: 0; margin-bottom: 16px; }}
                    a {{ color: #0366d6; text-decoration: none; }}
                    a:hover {{ text-decoration: underline; }}
                    code {{
                        font-family: Consolas, monospace;
                        padding: 0.2em 0.4em;
                        margin: 0;
                        font-size: 85%;
                        background-color: rgba(27,31,35,0.05);
                        border-radius: 3px;
                    }}
                    pre {{
                        font-family: Consolas, monospace;
                        padding: 16px;
                        overflow: auto;
                        font-size: 85%;
                        line-height: 1.45;
                        background-color: #f6f8fa;
                        border-radius: 3px;
                    }}
                    blockquote {{
                        padding: 0 1em;
                        color: #6a737d;
                        border-left: 0.25em solid #dfe2e5;
                        margin: 0 0 16px 0;
                    }}
                    ul, ol {{
                        padding-left: 2em;
                        margin-top: 0;
                        margin-bottom: 16px;
                    }}
                    table {{
                        border-collapse: collapse;
                        width: 100%;
                        margin-bottom: 16px;
                    }}
                    table th, table td {{
                        padding: 6px 13px;
                        border: 1px solid #dfe2e5;
                    }}
                    table tr {{
                        background-color: #fff;
                        border-top: 1px solid #c6cbd1;
                    }}
                    table tr:nth-child(2n) {{
                        background-color: #f6f8fa;
                    }}
                    img {{
                        max-width: 100%;
                        box-sizing: content-box;
                    }}
                </style>
            </head>
            <body>
                {html}
            </body>
            </html>
            """
            return styled_html
        except Exception as e:
            return f"<p>Markdown渲染错误: {str(e)}</p>"
    
    def apply_heading(self, index):
        """应用标题格式"""
        if index == 0:  # 正文
            self.insert_text_at_cursor("")
            return
            
        # 获取当前编辑器
        editor = self.get_current_editor()
        if not editor:
            return
            
        # 获取当前光标位置
        cursor = editor.textCursor()
        
        # 获取当前行文本
        cursor.select(QTextCursor.LineUnderCursor)
        line_text = cursor.selectedText()
        
        # 移动到行首
        cursor.movePosition(QTextCursor.StartOfLine)
        cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
        
        # 删除当前行
        cursor.removeSelectedText()
        
        # 插入标题
        heading_prefix = "#" * index
        cursor.insertText(f"{heading_prefix} {line_text.lstrip('#').lstrip()}")
        
        # 重置下拉框
        self.heading_combo.setCurrentIndex(0)
    
    def apply_format(self, marker):
        """应用格式（粗体、斜体等）"""
        editor = self.get_current_editor()
        if not editor:
            return
            
        cursor = editor.textCursor()
        
        # 检查是否有选中的文本
        if cursor.hasSelection():
            start = cursor.selectionStart()
            end = cursor.selectionEnd()
            selected_text = cursor.selectedText()
            
            # 删除选中的文本
            cursor.removeSelectedText()
            
            # 插入带格式的文本
            cursor.insertText(f"{marker}{selected_text}{marker}")
        else:
            # 如果没有选中文本，则插入格式标记并将光标放在中间
            cursor.insertText(f"{marker}{marker}")
            cursor.movePosition(QTextCursor.Left, QTextCursor.MoveAnchor, len(marker))
            editor.setTextCursor(cursor)
    
    def apply_bullet_list(self):
        """应用无序列表格式"""
        editor = self.get_current_editor()
        if not editor:
            return
            
        cursor = editor.textCursor()
        
        # 获取当前行文本
        cursor.select(QTextCursor.LineUnderCursor)
        line_text = cursor.selectedText()
        
        # 移动到行首
        cursor.movePosition(QTextCursor.StartOfLine)
        cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
        
        # 删除当前行
        cursor.removeSelectedText()
        
        # 插入无序列表项
        cursor.insertText(f"- {line_text.lstrip('-').lstrip()}")
    
    def apply_numbered_list(self):
        """应用有序列表格式"""
        editor = self.get_current_editor()
        if not editor:
            return
            
        cursor = editor.textCursor()
        
        # 获取当前行文本
        cursor.select(QTextCursor.LineUnderCursor)
        line_text = cursor.selectedText()
        
        # 移动到行首
        cursor.movePosition(QTextCursor.StartOfLine)
        cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
        
        # 删除当前行
        cursor.removeSelectedText()
        
        # 插入有序列表项
        cursor.insertText(f"1. {line_text.lstrip('1234567890.').lstrip()}")
    
    def insert_link(self):
        """插入链接"""
        editor = self.get_current_editor()
        if not editor:
            return
            
        cursor = editor.textCursor()
        
        # 检查是否有选中的文本
        if cursor.hasSelection():
            selected_text = cursor.selectedText()
            cursor.removeSelectedText()
            cursor.insertText(f"[{selected_text}](链接URL)")
        else:
            cursor.insertText("[链接文本](链接URL)")
    
    def insert_image(self):
        """插入图片"""
        editor = self.get_current_editor()
        if not editor:
            return
            
        cursor = editor.textCursor()
        cursor.insertText("![图片描述](图片URL)")
    
    def insert_code_block(self):
        """插入代码块"""
        editor = self.get_current_editor()
        if not editor:
            return
            
        cursor = editor.textCursor()
        
        # 检查是否有选中的文本
        if cursor.hasSelection():
            selected_text = cursor.selectedText()
            cursor.removeSelectedText()
            cursor.insertText(f"```\n{selected_text}\n```")
        else:
            cursor.insertText("```\n代码块\n```")
    
    def insert_quote(self):
        """插入引用"""
        editor = self.get_current_editor()
        if not editor:
            return
            
        cursor = editor.textCursor()
        
        # 获取当前行文本
        cursor.select(QTextCursor.LineUnderCursor)
        line_text = cursor.selectedText()
        
        # 移动到行首
        cursor.movePosition(QTextCursor.StartOfLine)
        cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
        
        # 删除当前行
        cursor.removeSelectedText()
        
        # 插入引用
        cursor.insertText(f"> {line_text.lstrip('>').lstrip()}")
    
    def get_current_editor(self):
        """获取当前活动的编辑器"""
        current_tab = self.tab_widget.currentIndex()
        if current_tab == 0:
            return self.editor
        elif current_tab == 2:
            return self.split_editor
        return None
    
    def set_text(self, text):
        """设置编辑器文本内容"""
        self.editor.setPlainText(text)
        self.split_editor.setPlainText(text)
        self.update_preview()
        self.update_split_preview()
    
    def get_text(self):
        """获取编辑器文本内容"""
        current_tab = self.tab_widget.currentIndex()
        if current_tab == 0:
            return self.editor.toPlainText()
        elif current_tab == 2:
            return self.split_editor.toPlainText()
        return self.editor.toPlainText()  # 默认返回编辑标签页的内容
    
    def insert_text_at_cursor(self, text):
        """在光标位置插入文本"""
        editor = self.get_current_editor()
        if editor:
            editor.textCursor().insertText(text)


if __name__ == "__main__":
    # 测试代码
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    editor = MarkdownEditor()
    editor.set_text("# Markdown编辑器测试\n\n这是一个**Markdown编辑器**的测试。\n\n## 功能列表\n\n- 编辑Markdown文本\n- 实时预览\n- 分屏模式\n\n> 这是一个引用\n\n```python\nprint('Hello, World!')\n```")
    editor.show()
    sys.exit(app.exec_())