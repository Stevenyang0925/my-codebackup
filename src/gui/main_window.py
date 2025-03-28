# Main window module

import os
import sys
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QLabel, QFileDialog, QStatusBar, 
                            QProgressBar, QApplication, QLineEdit, QListWidget,
                            QListWidgetItem, QSplitter, QFrame, QComboBox,
                            QCheckBox, QGroupBox, QScrollArea, QTabWidget)
from PyQt5.QtCore import Qt, QSize, QMimeData, QSettings
from PyQt5.QtGui import QIcon, QDragEnterEvent, QDropEvent

from .menu_bar import MenuBar
from .tool_bar import ToolBar
from .status_bar import StatusBar
from .file_dialogs import FileDialogs
from .markdown_editor import MarkdownEditor
from .settings_dialog import SettingsDialog

class DropArea(QFrame):
    """拖放区域类，用于接收拖放的文件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setAcceptDrops(True)
        
        # 设置布局
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        # 添加图标和文字
        icon_label = QLabel("📁")
        icon_label.setStyleSheet("font-size: 36px;")
        
        text_label = QLabel("拖拽文件到此处")
        text_label.setAlignment(Qt.AlignCenter)
        
        or_label = QLabel("或")
        or_label.setAlignment(Qt.AlignCenter)
        
        select_button = QPushButton("选择文件")
        select_button.setFixedWidth(100)
        select_button.clicked.connect(self.parent.browse_input_file)
        
        layout.addWidget(icon_label, 0, Qt.AlignCenter)
        layout.addWidget(text_label)
        layout.addWidget(or_label)
        layout.addWidget(select_button, 0, Qt.AlignCenter)
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """拖动进入事件"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event: QDropEvent):
        """放置事件"""
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                self.parent.add_file_to_list(file_path)
            event.acceptProposedAction()

class MainWindow(QMainWindow):
    """主窗口类，应用程序的主界面"""
    
    def __init__(self):
        super().__init__()
        
        # 设置窗口基本属性
        self.setWindowTitle("多格式文本转Markdown工具")
        self.setMinimumSize(1000, 700)  # 增加窗口尺寸以适应三栏布局
        
        # 初始化文件对话框
        self.file_dialogs = FileDialogs()
        
        # 初始化设置
        self.settings = QSettings("MarkdownConverter", "Settings")
        self.load_settings()
        
        # 初始化UI组件
        self.init_ui()
        
        # 连接信号和槽
        self.connect_signals()
        
        # 显示就绪状态
        self.statusBar.set_status("就绪")
    
    def init_ui(self):
        """初始化UI组件"""
        # 创建菜单栏
        self.menu_bar = MenuBar(self)
        self.setMenuBar(self.menu_bar)
        
        # 创建工具栏
        self.tool_bar = ToolBar(self)
        self.addToolBar(self.tool_bar)
        
        # 创建状态栏
        self.statusBar = StatusBar(self)
        self.setStatusBar(self.statusBar)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建分割器，实现三栏布局
        splitter = QSplitter(Qt.Horizontal)
        
        # 左侧边栏 - 文件选择区
        left_sidebar = QWidget()
        left_layout = QVBoxLayout(left_sidebar)
        left_layout.setContentsMargins(10, 10, 10, 10)
        
        # 添加"选择文件"标题
        file_title = QLabel("选择文件")
        file_title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        left_layout.addWidget(file_title)
        
        # 添加拖放区域
        self.drop_area = DropArea(self)
        self.drop_area.setMinimumHeight(150)
        self.drop_area.setStyleSheet("""
            QFrame {
                background-color: #F5F5F7;
                border: 2px dashed #D1D1D6;
                border-radius: 12px;
            }
            QFrame:hover {
                border-color: #007AFF;
            }
        """)
        left_layout.addWidget(self.drop_area)
        
        # 添加文件列表
        self.file_list = QListWidget()
        self.file_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #E8E8ED;
                border-radius: 6px;
                padding: 5px;
            }
            QListWidget::item {
                border-bottom: 1px solid #E8E8ED;
                padding: 8px;
            }
            QListWidget::item:hover {
                background-color: #F2F2F7;
            }
        """)
        left_layout.addWidget(self.file_list, 1)  # 列表占据剩余空间
        
        # 添加导入和批量选择按钮
        import_button = QPushButton("导入文件")
        import_button.clicked.connect(self.browse_input_file)
        batch_button = QPushButton("批量选择")
        batch_button.clicked.connect(self.batch_select_files)
        
        button_layout = QHBoxLayout()
        button_layout.addWidget(import_button)
        button_layout.addWidget(batch_button)
        left_layout.addLayout(button_layout)
        
        # 中央区域 - 转换设置区
        center_area = QScrollArea()
        center_area.setWidgetResizable(True)
        center_widget = QWidget()
        center_layout = QVBoxLayout(center_widget)
        center_layout.setContentsMargins(15, 15, 15, 15)
        
        # 添加"转换设置"标题
        settings_title = QLabel("转换设置")
        settings_title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 15px;")
        center_layout.addWidget(settings_title)
        
        # 添加输出格式选择
        format_group = QGroupBox("输出格式")
        format_layout = QVBoxLayout(format_group)
        self.format_combo = QComboBox()
        self.format_combo.addItem("Markdown")
        format_layout.addWidget(self.format_combo)
        center_layout.addWidget(format_group)
        
        # 添加输出路径设置
        output_group = QGroupBox("输出设置")
        output_layout = QVBoxLayout(output_group)
        
        # 输出路径
        path_label = QLabel("输出路径:")
        self.output_path_edit = QLineEdit()
        browse_button = QPushButton("浏览...")
        browse_button.clicked.connect(self.browse_output_path)
        
        path_layout = QHBoxLayout()
        path_layout.addWidget(self.output_path_edit)
        path_layout.addWidget(browse_button)
        
        # 文件名
        filename_label = QLabel("文件名:")
        self.filename_edit = QLineEdit()
        self.filename_edit.setPlaceholderText("output.md")
        
        output_layout.addWidget(path_label)
        output_layout.addLayout(path_layout)
        output_layout.addWidget(filename_label)
        output_layout.addWidget(self.filename_edit)
        
        center_layout.addWidget(output_group)
        
        # 添加图片处理选项
        image_group = QGroupBox("图片处理选项")
        image_layout = QVBoxLayout(image_group)
        
        # 图片压缩质量
        quality_label = QLabel("图片压缩质量")
        self.quality_slider = QProgressBar()
        self.quality_slider.setRange(0, 100)
        self.quality_slider.setValue(80)
        self.quality_slider.setTextVisible(True)
        self.quality_slider.setFormat("%v%")
        
        # 图片处理选项
        self.extract_images_check = QCheckBox("提取并引用文档中的图片")
        self.extract_images_check.setChecked(True)
        
        self.compress_images_check = QCheckBox("压缩图片")
        self.compress_images_check.setChecked(True)
        
        image_layout.addWidget(quality_label)
        image_layout.addWidget(self.quality_slider)
        image_layout.addWidget(self.extract_images_check)
        image_layout.addWidget(self.compress_images_check)
        
        center_layout.addWidget(image_group)
        
        # 添加Markdown格式选项
        md_group = QGroupBox("Markdown格式")
        md_layout = QVBoxLayout(md_group)
        
        # 标题样式
        heading_label = QLabel("标题样式:")
        self.heading_style_combo = QComboBox()
        self.heading_style_combo.addItems(["ATX风格 (# 标题)", "Setext风格 (标题\n===)"])
        
        # 列表样式
        list_label = QLabel("列表样式:")
        self.list_style_combo = QComboBox()
        self.list_style_combo.addItems(["短横线 (-)", "星号 (*)", "加号 (+)"])
        
        # 代码块样式
        code_label = QLabel("代码块样式:")
        self.code_style_combo = QComboBox()
        self.code_style_combo.addItems(["围栏式 (```)", "缩进式 (    )"])
        
        md_layout.addWidget(heading_label)
        md_layout.addWidget(self.heading_style_combo)
        md_layout.addWidget(list_label)
        md_layout.addWidget(self.list_style_combo)
        md_layout.addWidget(code_label)
        md_layout.addWidget(self.code_style_combo)
        
        center_layout.addWidget(md_group)
        
        # 添加转换按钮
        convert_button = QPushButton("开始转换")
        convert_button.setStyleSheet("""
            QPushButton {
                background-color: #007AFF;
                color: white;
                border-radius: 6px;
                padding: 10px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0062CC;
            }
            QPushButton:pressed {
                background-color: #004999;
            }
        """)
        convert_button.clicked.connect(self.convert_to_markdown)
        
        center_layout.addWidget(convert_button)
        
        # 添加弹性空间
        center_layout.addStretch()
        
        center_area.setWidget(center_widget)
        
        # 右侧区域 - Markdown编辑器和预览
        self.markdown_editor = MarkdownEditor()
        
        # 添加各区域到分割器
        splitter.addWidget(left_sidebar)
        splitter.addWidget(center_area)
        splitter.addWidget(self.markdown_editor)
        
        # 设置分割器初始大小
        splitter.setSizes([200, 300, 500])
        
        # 添加分割器到主布局
        main_layout.addWidget(splitter)
        
        # 添加历史记录区域
        self.history_list = QListWidget()
        self.history_list.setVisible(False)  # 初始隐藏
    
    def connect_signals(self):
        """连接信号和槽"""
        # 连接工具栏按钮
        if hasattr(self.tool_bar, 'connect_actions'):
            self.tool_bar.connect_actions(self)
        
        # 连接菜单栏动作
        if hasattr(self.menu_bar, 'connect_actions'):
            self.menu_bar.connect_actions(self)
        
        # 连接文件列表双击事件
        self.file_list.itemDoubleClicked.connect(self.on_file_double_clicked)
        
        # 连接历史记录双击事件
        self.history_list.itemDoubleClicked.connect(self.on_history_double_clicked)
    
    def load_settings(self):
        """加载设置"""
        # 加载常规设置
        self.default_dir = self.settings.value("general/default_dir", os.path.expanduser("~/Documents"))
        
        # 加载转换设置
        self.heading_style = self.settings.value("conversion/heading_style", 0, type=int)
        self.list_style = self.settings.value("conversion/list_style", 0, type=int)
        self.code_style = self.settings.value("conversion/code_style", 0, type=int)
        self.extract_images = self.settings.value("conversion/extract_images", True, type=bool)
        
        # 加载外观设置
        self.theme = self.settings.value("appearance/theme", 2, type=int)
        self.editor_font_size = self.settings.value("appearance/editor_font_size", 14, type=int)
        self.live_preview = self.settings.value("appearance/live_preview", True, type=bool)
        self.preview_interval = self.settings.value("appearance/preview_interval", 2000, type=int)
    
    def browse_input_file(self):
        """打开文件选择对话框"""
        file_paths, _ = self.file_dialogs.get_open_file_names(
            self,
            "选择输入文件",
            self.default_dir,
            "所有支持的文件 (*.docx *.xlsx *.txt *.pdf *.jpg *.png *.jpeg);;Word文档 (*.docx);;Excel表格 (*.xlsx);;文本文件 (*.txt);;PDF文档 (*.pdf);;图片文件 (*.jpg *.png *.jpeg)"
        )
        
        if file_paths:
            for file_path in file_paths:
                self.add_file_to_list(file_path)
    
    def add_file_to_list(self, file_path):
        """将文件添加到文件列表"""
        if not file_path:
            return
            
        # 检查文件是否已在列表中
        for i in range(self.file_list.count()):
            if self.file_list.item(i).data(Qt.UserRole) == file_path:
                return
        
        # 创建列表项
        item = QListWidgetItem()
        
        # 获取文件名和扩展名
        file_name = os.path.basename(file_path)
        _, ext = os.path.splitext(file_name)
        
        # 设置图标（这里简化处理，实际应根据文件类型设置不同图标）
        icon_text = ext[1:].upper()[0] if ext else "?"
        
        # 设置显示文本
        item.setText(file_name)
        
        # 存储完整路径
        item.setData(Qt.UserRole, file_path)
        
        # 添加到列表
        self.file_list.addItem(item)
        
        # 自动设置输出路径（使用第一个文件所在目录）
        if self.file_list.count() == 1:
            dir_name = os.path.dirname(file_path)
            self.output_path_edit.setText(dir_name)
            
            # 设置默认文件名
            base_name = os.path.basename(file_path)
            file_name, _ = os.path.splitext(base_name)
            self.filename_edit.setText(f"{file_name}.md")
    
    def batch_select_files(self):
        """批量选择文件"""
        self.browse_input_file()
    
    def browse_output_path(self):
        """打开保存文件对话框"""
        dir_path = self.file_dialogs.get_existing_directory(
            self,
            "选择保存目录",
            self.output_path_edit.text() if self.output_path_edit.text() else self.default_dir
        )
        
        if dir_path:
            self.output_path_edit.setText(dir_path)
    
    def convert_to_markdown(self):
        """将选中的文件转换为Markdown格式"""
        if self.file_list.count() == 0:
            self.statusBar.set_status("请先选择要转换的文件")
            return
        
        output_dir = self.output_path_edit.text()
        output_filename = self.filename_edit.text()
        
        if not output_dir or not output_filename:
            self.statusBar.set_status("请设置输出路径和文件名")
            return
        
        # 构建完整输出路径
        output_path = os.path.join(output_dir, output_filename)
        
        # 获取转换设置
        settings = {
            'heading_style': self.heading_style_combo.currentIndex(),
            'list_style': self.list_style_combo.currentIndex(),
            'code_style': self.code_style_combo.currentIndex(),
            'extract_images': self.extract_images_check.isChecked(),
            'compress_images': self.compress_images_check.isChecked(),
            'image_quality': self.quality_slider.value()
        }
        
        # 获取选中的文件
        selected_files = []
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            file_path = item.data(Qt.UserRole)
            selected_files.append(file_path)
        
        # 这里应该调用核心功能模块进行转换
        self.statusBar.set_status("正在转换...")
        self.statusBar.show_progress(True)
        self.statusBar.set_progress(0)
        
        # TODO: 实际的转换逻辑将在核心功能模块开发完成后集成
        # 这里仅作为示例，模拟转换过程
        import time
        for i in range(101):
            time.sleep(0.05)  # 模拟处理时间
            self.statusBar.set_progress(i)
            QApplication.processEvents()  # 保持UI响应
        
        self.statusBar.set_status(f"转换完成，已保存到 {output_path}")
        self.statusBar.show_progress(False)
        
        # 模拟显示转换结果
        self.markdown_editor.set_text("# 转换结果\n\n这是从文件转换得到的Markdown内容示例。\n\n实际内容将在核心功能模块开发完成后显示。")
        
        # 添加到历史记录
        self.add_to_history(output_filename)
    
    def add_to_history(self, filename):
        """添加文件到历史记录"""
        self.history_list.addItem(filename)
    
    def on_file_double_clicked(self, item):
        """文件列表项双击事件"""
        file_path = item.data(Qt.UserRole)
        # 根据文件类型执行不同操作
        _, ext = os.path.splitext(file_path)
        if ext.lower() in ['.md', '.markdown']:
            self.open_markdown_file(file_path)
        else:
            # 对于其他类型文件，可以尝试用系统默认程序打开
            import subprocess
            try:
                os.startfile(file_path)
            except:
                self.statusBar.set_status(f"无法打开文件: {file_path}")
    
    def on_history_double_clicked(self, item):
        """历史记录项双击事件"""
        filename = item.text()
        output_dir = self.output_path_edit.text()
        file_path = os.path.join(output_dir, filename)
        self.open_markdown_file(file_path)
    
    def new_file(self):
        """创建新文件"""
        self.markdown_editor.set_text("")
        self.statusBar.set_file_info("", "", False)
        self.statusBar.set_status("新建文件")
    
    def open_file(self):
        """打开文件"""
        self.open_markdown_file()
    
    def save_markdown(self):
        """保存Markdown文件"""
        output_dir = self.output_path_edit.text()
        output_filename = self.filename_edit.text()
        
        if not output_dir or not output_filename:
            file_path, _ = self.file_dialogs.get_save_file_name(
                self,
                "保存Markdown文件",
                self.default_dir,
                "Markdown文件 (*.md)"
            )
        else:
            file_path = os.path.join(output_dir, output_filename)
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.markdown_editor.get_text())
                self.statusBar.set_status(f"文件已保存: {file_path}")
                self.statusBar.set_file_info(file_path, "Markdown", False)
                return True
            except Exception as e:
                self.statusBar.set_status(f"保存文件失败: {str(e)}")
        
        return False
    
    def open_markdown_file(self, file_path=None):
        """打开Markdown文件"""
        if not file_path:
            file_path, _ = self.file_dialogs.get_open_file_name(
                self,
                "打开Markdown文件",
                self.default_dir,
                "Markdown文件 (*.md)"
            )
        
        if file_path and os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.markdown_editor.set_text(content)
                self.statusBar.set_status(f"已打开: {file_path}")
                self.statusBar.set_file_info(file_path, "Markdown", False)
                return True
            except Exception as e:
                self.statusBar.set_status(f"打开文件失败: {str(e)}")
        
        return False


class DropArea(QFrame):
    """文件拖放区域"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setAcceptDrops(True)
        
        # 设置布局
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        # 添加图标和文字
        icon_label = QLabel("📁")
        icon_label.setStyleSheet("font-size: 36px;")
        
        text_label = QLabel("拖拽文件到此处")
        text_label.setAlignment(Qt.AlignCenter)
        
        or_label = QLabel("或")
        or_label.setAlignment(Qt.AlignCenter)
        
        select_button = QPushButton("选择文件")
        select_button.setFixedWidth(100)
        select_button.clicked.connect(self.parent.browse_input_file)
        
        layout.addWidget(icon_label, 0, Qt.AlignCenter)
        layout.addWidget(text_label)
        layout.addWidget(or_label)
        layout.addWidget(select_button, 0, Qt.AlignCenter)
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """拖拽进入事件"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet("""
                QFrame {
                    background-color: #F5F5F7;
                    border: 2px dashed #007AFF;
                    border-radius: 12px;
                }
            """)
    
    def dragLeaveEvent(self, event):
        """拖拽离开事件"""
        self.setStyleSheet("""
            QFrame {
                background-color: #F5F5F7;
                border: 2px dashed #D1D1D6;
                border-radius: 12px;
            }
        """)
    
    def dropEvent(self, event: QDropEvent):
        """放置事件"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            
            # 恢复样式
            self.setStyleSheet("""
                QFrame {
                    background-color: #F5F5F7;
                    border: 2px dashed #D1D1D6;
                    border-radius: 12px;
                }
            """)
            
            # 处理文件
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if os.path.isfile(file_path):
                    self.parent.add_file_to_list(file_path)


# 添加apply_settings方法
def apply_settings(self):
    """应用设置"""
    # 从QSettings加载设置
    settings = QSettings("MarkdownConverter", "Settings")
    
    # 应用常规设置
    default_dir = settings.value("general/default_dir", os.path.expanduser("~/Documents"))
    self.file_dialogs.set_default_directory(default_dir)
    
    # 应用外观设置
    editor_font_size = settings.value("appearance/editor_font_size", 14, type=int)
    if hasattr(self, 'markdown_editor'):
        self.markdown_editor.set_font_size(editor_font_size)
    
    # 应用实时预览设置
    live_preview = settings.value("appearance/live_preview", True, type=bool)
    preview_interval = settings.value("appearance/preview_interval", 2000, type=int)
    if hasattr(self, 'markdown_editor'):
        self.markdown_editor.set_live_preview(live_preview, preview_interval)
    
    # 更新状态栏
    self.statusBar().showMessage("设置已应用", 3000)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())