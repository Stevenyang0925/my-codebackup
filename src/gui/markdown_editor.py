from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                              QTextEdit, QToolBar, QLabel, QPushButton,
                              QSplitter, QFrame)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QTextCursor

class MarkdownEditor(QWidget):
    """Markdown编辑器组件，提供编辑和预览Markdown内容的功能"""
    
    # 定义信号
    contentChanged = pyqtSignal(str)  # 内容变更信号
    
    def __init__(self, parent=None):
        """初始化Markdown编辑器
        
        Args:
            parent: 父窗口对象
        """
        super(MarkdownEditor, self).__init__(parent)
        
        # 初始化成员变量
        self.is_preview_mode = False
        self.current_file = None
        self.is_modified = False
        
        # 创建UI
        self._create_ui()
        
        # 连接信号与槽
        self._connect_signals()
    
    def _create_ui(self):
        """创建编辑器UI"""
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 标题
        self.title_label = QLabel("Markdown编辑器")
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 8px;")
        main_layout.addWidget(self.title_label)
        
        # 创建工具栏
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setSpacing(4)
        
        # 创建格式化按钮
        self.h1_button = QPushButton("标题1")
        self.h1_button.setToolTip("将选中文本设置为一级标题")
        self.h1_button.clicked.connect(lambda: self._format_text("h1"))
        toolbar_layout.addWidget(self.h1_button)
        
        self.h2_button = QPushButton("标题2")
        self.h2_button.setToolTip("将选中文本设置为二级标题")
        self.h2_button.clicked.connect(lambda: self._format_text("h2"))
        toolbar_layout.addWidget(self.h2_button)
        
        self.h3_button = QPushButton("标题3")
        self.h3_button.setToolTip("将选中文本设置为三级标题")
        self.h3_button.clicked.connect(lambda: self._format_text("h3"))
        toolbar_layout.addWidget(self.h3_button)
        
        # 添加分隔线
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.VLine)
        separator1.setFrameShadow(QFrame.Sunken)
        toolbar_layout.addWidget(separator1)
        
        self.bold_button = QPushButton("粗体")
        self.bold_button.setToolTip("将选中文本设置为粗体")
        self.bold_button.clicked.connect(lambda: self._format_text("bold"))
        toolbar_layout.addWidget(self.bold_button)
        
        self.italic_button = QPushButton("斜体")
        self.italic_button.setToolTip("将选中文本设置为斜体")
        self.italic_button.clicked.connect(lambda: self._format_text("italic"))
        toolbar_layout.addWidget(self.italic_button)
        
        # 添加分隔线
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.VLine)
        separator2.setFrameShadow(QFrame.Sunken)
        toolbar_layout.addWidget(separator2)
        
        self.ul_button = QPushButton("无序列表")
        self.ul_button.setToolTip("将选中文本转换为无序列表")
        self.ul_button.clicked.connect(lambda: self._format_text("ul"))
        toolbar_layout.addWidget(self.ul_button)
        
        self.ol_button = QPushButton("有序列表")
        self.ol_button.setToolTip("将选中文本转换为有序列表")
        self.ol_button.clicked.connect(lambda: self._format_text("ol"))
        toolbar_layout.addWidget(self.ol_button)
        
        # 添加分隔线
        separator3 = QFrame()
        separator3.setFrameShape(QFrame.VLine)
        separator3.setFrameShadow(QFrame.Sunken)
        toolbar_layout.addWidget(separator3)
        
        self.link_button = QPushButton("链接")
        self.link_button.setToolTip("将选中文本转换为链接")
        self.link_button.clicked.connect(lambda: self._format_text("link"))
        toolbar_layout.addWidget(self.link_button)
        
        self.image_button = QPushButton("图片")
        self.image_button.setToolTip("将选中文本转换为图片引用")
        self.image_button.clicked.connect(lambda: self._format_text("image"))
        toolbar_layout.addWidget(self.image_button)
        
        # 添加分隔线
        separator4 = QFrame()
        separator4.setFrameShape(QFrame.VLine)
        separator4.setFrameShadow(QFrame.Sunken)
        toolbar_layout.addWidget(separator4)
        
        self.code_button = QPushButton("代码块")
        self.code_button.setToolTip("将选中文本转换为代码块")
        self.code_button.clicked.connect(lambda: self._format_text("code"))
        toolbar_layout.addWidget(self.code_button)
        
        self.quote_button = QPushButton("引用")
        self.quote_button.setToolTip("将选中文本转换为引用文本")
        self.quote_button.clicked.connect(lambda: self._format_text("quote"))
        toolbar_layout.addWidget(self.quote_button)
        
        self.table_button = QPushButton("表格")
        self.table_button.setToolTip("插入简单表格")
        self.table_button.clicked.connect(lambda: self._format_text("table"))
        toolbar_layout.addWidget(self.table_button)
        
        main_layout.addLayout(toolbar_layout)
        
        # 创建分割器，支持调整编辑区和预览区比例
        self.splitter = QSplitter(Qt.Vertical)
        
        # 编辑器
        self.editor = QTextEdit()
        self.editor.setPlaceholderText("在这里输入Markdown内容...")
        self.editor.setFont(QFont("Consolas", 11))
        self.editor.setStyleSheet("""
            QTextEdit {
                font-family: 'Consolas', 'Courier New', monospace;
                line-height: 1.5;
                padding: 8px;
                border: 1px solid #D1D1D6;
                border-radius: 6px;
            }
        """)
        self.splitter.addWidget(self.editor)
        
        # 预览区
        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        self.preview.setStyleSheet("""
            QTextEdit {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
                line-height: 1.6;
                padding: 16px;
                border: 1px solid #D1D1D6;
                border-radius: 6px;
                background-color: #FCFCFC;
            }
        """)
        self.splitter.addWidget(self.preview)
        self.preview.hide()  # 初始隐藏预览区域
        
        main_layout.addWidget(self.splitter)
    
    def _connect_signals(self):
        """连接信号与槽"""
        # 编辑器内容变更信号
        self.editor.textChanged.connect(self._on_text_changed)
    
    def _on_text_changed(self):
        """编辑器内容变更处理"""
        self.is_modified = True
        self.contentChanged.emit(self.editor.toPlainText())
        
        # 如果是预览模式，更新预览内容
        if self.is_preview_mode:
            self._update_preview()
    
    def _format_text(self, format_type):
        """格式化所选文本
        
        Args:
            format_type: 格式类型
        """
        cursor = self.editor.textCursor()
        selected_text = cursor.selectedText()
        
        # 根据格式类型应用不同的Markdown语法
        formatted_text = ""
        
        if format_type == "h1":
            formatted_text = f"# {selected_text}"
        elif format_type == "h2":
            formatted_text = f"## {selected_text}"
        elif format_type == "h3":
            formatted_text = f"### {selected_text}"
        elif format_type == "bold":
            formatted_text = f"**{selected_text}**"
        elif format_type == "italic":
            formatted_text = f"*{selected_text}*"
        elif format_type == "ul":
            lines = selected_text.split("\n")
            formatted_text = "\n".join([f"- {line}" for line in lines if line.strip()])
        elif format_type == "ol":
            lines = selected_text.split("\n")
            formatted_text = "\n".join([f"{i+1}. {line}" for i, line in enumerate(lines) if line.strip()])
        elif format_type == "link":
            formatted_text = f"[{selected_text}](链接URL)"
        elif format_type == "image":
            formatted_text = f"![{selected_text}](图片URL)"
        elif format_type == "code":
            formatted_text = f"```\n{selected_text}\n```"
        elif format_type == "quote":
            lines = selected_text.split("\n")
            formatted_text = "\n".join([f"> {line}" for line in lines if line.strip()])
        elif format_type == "table":
            formatted_text = "| 列1 | 列2 | 列3 |\n|-----|-----|-----|\n| 内容 | 内容 | 内容 |"
        
        # 替换所选文本
        if formatted_text:
            cursor.insertText(formatted_text)
    
    def _update_preview(self):
        """更新预览内容"""
        markdown_text = self.editor.toPlainText()
        try:
            import markdown
            html = markdown.markdown(markdown_text, extensions=['tables', 'fenced_code'])
            self.preview.setHtml(html)
        except ImportError:
            self.preview.setPlainText("Markdown库未安装，无法预览")
    
    def _simple_markdown_to_html(self, markdown_text):
        """简单的Markdown到HTML转换，仅用于预览
        
        Args:
            markdown_text: Markdown文本
            
        Returns:
            转换后的HTML文本
        """
        # 简单实现，实际应用中应使用专业的Markdown解析库
        import re
        
        # 基础HTML模板
        html = markdown_text
        
        # 替换标题
        html = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        
        # 替换粗体和斜体
        html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
        html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)
        
        # 替换链接和图片
        html = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', html)
        html = re.sub(r'!\[(.*?)\]\((.*?)\)', r'<img src="\2" alt="\1">', html)
        
        # 替换无序列表
        html = re.sub(r'^- (.*?)$', r'<li>\1</li>', html, flags=re.MULTILINE)
        
        # 替换有序列表
        html = re.sub(r'^\d+\. (.*?)$', r'<li>\1</li>', html, flags=re.MULTILINE)
        
        # 替换代码块
        html = re.sub(r'```(.*?)```', r'<pre><code>\1</code></pre>', html, flags=re.DOTALL)
        
        # 替换引用
        html = re.sub(r'^> (.*?)$', r'<blockquote>\1</blockquote>', html, flags=re.MULTILINE)
        
        # 替换换行符
        html = html.replace('\n\n', '<br><br>')
        
        # 添加基本样式
        return f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    margin: 0;
                    padding: 16px;
                }}
                h1, h2, h3 {{
                    margin-top: 24px;
                    margin-bottom: 16px;
                    font-weight: 600;
                    line-height: 1.25;
                }}
                h1 {{ font-size: 2em; }}
                h2 {{ font-size: 1.5em; }}
                h3 {{ font-size: 1.25em; }}
                strong {{ font-weight: 600; }}
                pre {{
                    background-color: #f6f8fa;
                    border-radius: 3px;
                    padding: 16px;
                    overflow: auto;
                }}
                code {{
                    font-family: Consolas, 'Courier New', monospace;
                    background-color: rgba(27, 31, 35, 0.05);
                    border-radius: 3px;
                    padding: 0.2em 0.4em;
                }}
                blockquote {{
                    padding: 0 1em;
                    color: #6a737d;
                    border-left: 0.25em solid #dfe2e5;
                    margin: 0;
                }}
                img {{
                    max-width: 100%;
                }}
            </style>
        </head>
        <body>
            {html}
        </body>
        </html>
        """
    
    def set_preview_mode(self):
        """切换到预览模式"""
        self.is_preview_mode = True
        self.title_label.setText("Markdown预览")
        self.editor.hide()
        self.preview.show()
        self._update_preview()
    
    def set_edit_mode(self):
        """切换到编辑模式"""
        self.is_preview_mode = False
        self.title_label.setText("Markdown编辑器")
        self.editor.show()
        self.preview.hide()
    
    def set_content(self, text):
        """设置编辑器内容
        
        Args:
            text: 要设置的文本内容
        """
        self.editor.setPlainText(text)
        self.is_modified = False
    
    def get_content(self):
        """获取编辑器内容
        
        Returns:
            编辑器中的文本内容
        """
        return self.editor.toPlainText()
    
    def is_content_modified(self):
        """检查内容是否已修改
        
        Returns:
            如果内容已修改则返回True，否则返回False
        """
        return self.is_modified
    
    def set_current_file(self, file_path):
        """设置当前文件路径
        
        Args:
            file_path: 文件路径
        """
        self.current_file = file_path
        
    def toggle_preview(self):
        """切换预览状态"""
        if self.is_preview_mode:
            self.set_edit_mode()
        else:
            self.set_preview_mode()
            
    def clear_content(self):
        """清空编辑器内容"""
        self.editor.clear()
        self.is_modified = False
        
    def save_to_file(self, file_path):
        """保存内容到文件"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(self.get_content())
            self.is_modified = False
            self.current_file = file_path
            return True
        except Exception as e:
            print(f"保存文件失败: {str(e)}")
            return False