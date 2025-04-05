# Main window module

import os
import sys
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QLabel, QFileDialog, QStatusBar, 
                            QProgressBar, QApplication, QLineEdit, QListWidget,
                            QListWidgetItem, QSplitter, QFrame, QComboBox,
                            QCheckBox, QGroupBox, QScrollArea, QTabWidget)
from PyQt5.QtCore import Qt, QSize, QMimeData, QSettings, QThread, pyqtSignal
from PyQt5.QtGui import QIcon, QDragEnterEvent, QDropEvent

from ..core.converter import Converter
from ..core.utils.logger import get_logger, setup_logging
from ..core.utils.exceptions import FileParsingError, MarkdownGenerationError, FileWritingError, UnsupportedFileTypeError

from .menu_bar import MenuBar
from .tool_bar import ToolBar
from .status_bar import StatusBar
from .file_dialogs import FileDialogs
from .markdown_editor import MarkdownEditor
from .settings_dialog import SettingsDialog

# +++ 获取 logger 实例 +++
logger = get_logger(__name__) # 通常使用 __name__ 获取模块名作为 logger 名

# +++ (可选) 创建一个工作线程类来执行转换，避免阻塞GUI +++
class ConversionWorker(QThread):
    progress_updated = pyqtSignal(int)
    status_updated = pyqtSignal(str)
    conversion_finished = pyqtSignal(str, str) # input_path, output_path (or None if failed)

    def __init__(self, converter, file_path, output_dir, output_filename, settings):
        super().__init__()
        self.converter = converter
        self.file_path = file_path
        self.output_dir = output_dir
        self.output_filename = output_filename
        self.settings = settings # 传递设置给转换器（如果需要）

    def run(self):
        try:
            # --- 这里可以模拟进度更新，或者如果Converter支持回调则使用回调 ---
            self.status_updated.emit(f"正在转换: {os.path.basename(self.file_path)}...")
            self.progress_updated.emit(10) # 模拟开始

            # --- 实际调用转换器 ---
            # 注意：如果Converter需要设置，需要传递 self.settings
            # output_file = self.converter.convert_file(self.file_path, self.output_dir, self.output_filename, settings=self.settings)
            output_file = self.converter.convert_file(self.file_path, self.output_dir, self.output_filename) # 简化调用

            self.progress_updated.emit(100) # 完成

            if output_file:
                self.status_updated.emit(f"转换成功: {os.path.basename(output_file)}")
                self.conversion_finished.emit(self.file_path, output_file)
            else:
                # 错误已在Converter中记录，这里只更新状态
                self.status_updated.emit(f"转换失败: {os.path.basename(self.file_path)}")
                self.conversion_finished.emit(self.file_path, None)

        except Exception as e: # 捕获线程中未预料的异常
            logger.exception(f"转换线程中发生未预料的错误 for {self.file_path}", exc_info=True)
            self.status_updated.emit(f"转换错误: {os.path.basename(self.file_path)}")
            self.conversion_finished.emit(self.file_path, None)


class DropArea(QFrame):
    """拖放区域类，用于接收拖放的文件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setAcceptDrops(True)
        logger.debug("DropArea initialized.") # +++ 添加日志 +++
        
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
            logger.debug("Drag enter event accepted.") # +++ 添加日志 +++
            event.acceptProposedAction()
    
    def dragLeaveEvent(self, event):
        """拖拽离开事件"""
        logger.debug("Drag leave event.") # +++ 添加日志 +++
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
            urls = event.mimeData().urls()
            logger.info(f"Drop event with {len(urls)} files.") # +++ 添加日志 +++
            for url in urls:
                file_path = url.toLocalFile()
                logger.debug(f"Adding dropped file: {file_path}") # +++ 添加日志 +++
                self.parent.add_file_to_list(file_path)
            event.acceptProposedAction()
            
            # 恢复样式
            self.setStyleSheet("""
                QFrame {
                    background-color: #F5F5F7;
                    border: 2px dashed #D1D1D6;
                    border-radius: 12px;
                }
            """)

class MainWindow(QMainWindow):
    """主窗口类，应用程序的主界面"""
    
    def __init__(self):
        super().__init__()
        logger.info("Initializing MainWindow...") # +++ 添加日志 +++
        
        # 设置窗口基本属性
        self.setWindowTitle("多格式文本转Markdown工具")
        self.setMinimumSize(1000, 700)  # 增加窗口尺寸以适应三栏布局
        
        # 初始化文件对话框
        self.file_dialogs = FileDialogs()
        
        # +++ 初始化核心转换器 +++
        self.converter = Converter()
        self.conversion_threads = {} # 用于跟踪转换线程
        
        # 初始化设置
        self.settings = QSettings("MarkdownConverter", "Settings")
        self.load_settings()
        
        # 初始化UI组件
        self.init_ui()
        
        # 连接信号和槽
        self.connect_signals()
        
        # 显示就绪状态
        self.statusBar.set_status("就绪")
        logger.info("MainWindow initialized successfully.") # +++ 添加日志 +++
    
    def init_ui(self):
        """初始化UI组件"""
        logger.debug("Initializing UI components...") # +++ 添加日志 +++
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
        logger.debug("UI components initialized.") # +++ 添加日志 +++
    
    def connect_signals(self):
        """连接信号和槽"""
        logger.debug("Connecting signals and slots...") # +++ 添加日志 +++
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
        logger.debug("Signals and slots connected.") # +++ 添加日志 +++
    
    def load_settings(self):
        """加载设置"""
        logger.info("Loading settings...") # +++ 添加日志 +++
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
        logger.info("Settings loaded.") # +++ 添加日志 +++
    
    def browse_input_file(self):
        """打开文件选择对话框"""
        logger.debug("Browse input file button clicked.") # +++ 添加日志 +++
        file_paths, _ = self.file_dialogs.get_open_file_names(
            self,
            "选择输入文件",
            self.default_dir,
            "所有支持的文件 (*.docx *.xlsx *.txt *.pdf *.jpg *.png *.jpeg);;Word文档 (*.docx);;Excel表格 (*.xlsx);;文本文件 (*.txt);;PDF文档 (*.pdf);;图片文件 (*.jpg *.png *.jpeg)"
        )
        
        if file_paths:
            logger.info(f"Selected {len(file_paths)} files via dialog.") # +++ 添加日志 +++
            for file_path in file_paths:
                self.add_file_to_list(file_path)
        else:
            logger.debug("No files selected from dialog.") # +++ 添加日志 +++
    
    def add_file_to_list(self, file_path):
        """将文件添加到文件列表"""
        if not file_path:
            logger.warning("Attempted to add an empty file path to the list.") # +++ 添加日志 +++
            return
            
        # 检查文件是否已在列表中
        for i in range(self.file_list.count()):
            if self.file_list.item(i).data(Qt.UserRole) == file_path:
                logger.debug(f"File already in list, skipping: {file_path}") # +++ 添加日志 +++
                return
        
        logger.info(f"Adding file to list: {file_path}") # +++ 添加日志 +++
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
            logger.debug("Setting default output path and filename based on first file.") # +++ 添加日志 +++
            dir_name = os.path.dirname(file_path)
            self.output_path_edit.setText(dir_name)
            
            # 设置默认文件名
            base_name = os.path.basename(file_path)
            file_name, _ = os.path.splitext(base_name)
            self.filename_edit.setText(f"{file_name}.md")
    
    def batch_select_files(self):
        """批量选择文件"""
        logger.debug("Batch select files button clicked.") # +++ 添加日志 +++
        self.browse_input_file()
    
    def browse_output_path(self):
        """打开保存文件对话框"""
        logger.debug("Browse output path button clicked.") # +++ 添加日志 +++
        dir_path = self.file_dialogs.get_existing_directory(
            self,
            "选择保存目录",
            self.output_path_edit.text() if self.output_path_edit.text() else self.default_dir
        )
        
        if dir_path:
            logger.info(f"Output directory set to: {dir_path}") # +++ 添加日志 +++
            self.output_path_edit.setText(dir_path)
        else:
            logger.debug("No output directory selected.") # +++ 添加日志 +++
    
    def convert_to_markdown(self):
        """将选中的文件转换为Markdown格式"""
        logger.info("Convert to Markdown button clicked.") # +++ 添加日志 +++

        if self.file_list.count() == 0:
            logger.warning("Conversion attempt with no files selected.") # +++ 添加日志 +++
            self.statusBar.set_status("请先选择要转换的文件")
            return
        
        output_dir = self.output_path_edit.text()
        output_filename_template = self.filename_edit.text() # 可能包含占位符或用于单个文件

        if not output_dir:
            logger.warning("Conversion attempt with no output directory set.") # +++ 添加日志 +++
            self.statusBar.set_status("请设置输出路径")
            return

        # --- 获取转换设置 (这部分逻辑不变) ---
        settings = {
            'heading_style': self.heading_style_combo.currentIndex(),
            'list_style': self.list_style_combo.currentIndex(),
            'code_style': self.code_style_combo.currentIndex(),
            'extract_images': self.extract_images_check.isChecked(),
            'compress_images': self.compress_images_check.isChecked(),
            'image_quality': self.quality_slider.value()
        }
        logger.debug(f"Conversion settings: {settings}") # +++ 添加日志 +++

        # --- 获取选中的文件 (这部分逻辑不变) ---
        selected_files = []
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            file_path = item.data(Qt.UserRole)
            selected_files.append(file_path)
        logger.info(f"Starting conversion for {len(selected_files)} files.") # +++ 添加日志 +++

        # --- 使用线程进行转换 ---
        self.statusBar.show_progress(True) # 显示总进度条（如果需要）
        self.statusBar.set_progress(0) # 重置总进度
        self._conversion_count = 0
        self._total_files = len(selected_files)

        for file_path in selected_files:
            # 为每个文件确定输出文件名
            base_name = os.path.basename(file_path)
            file_name_only, _ = os.path.splitext(base_name)
            # 如果模板为空或只有一个文件，使用模板；否则基于输入文件名生成
            if len(selected_files) == 1 and output_filename_template:
                 current_output_filename = output_filename_template
            else:
                 current_output_filename = f"{file_name_only}.md"

            logger.info(f"Queueing conversion for: {file_path} -> {os.path.join(output_dir, current_output_filename)}") # +++ 添加日志 +++

            # 创建并启动转换线程
            worker = ConversionWorker(self.converter, file_path, output_dir, current_output_filename, settings)
            worker.status_updated.connect(self.statusBar.set_status)
            # worker.progress_updated.connect(self.update_single_file_progress) # 如果需要单文件进度
            worker.conversion_finished.connect(self.on_conversion_finished)
            self.conversion_threads[file_path] = worker # 存储线程引用
            worker.start()

    # +++ 新增：处理单个文件转换完成的槽函数 +++
    def on_conversion_finished(self, input_path: str, output_path: Optional[str]):
        """当一个文件的转换线程结束时调用"""
        logger.debug(f"Conversion finished signal received for {input_path}. Output: {output_path}")
        self._conversion_count += 1
        progress = int((self._conversion_count / self._total_files) * 100)
        self.statusBar.set_progress(progress)

        if output_path:
            # 转换成功
            logger.info(f"Successfully converted {input_path} to {output_path}")
            # 添加到历史记录
            self.add_to_history(os.path.basename(output_path))
            # (可选) 在编辑器中显示最后一个成功转换的文件
            if self._conversion_count == self._total_files or self._total_files == 1:
                 self.open_markdown_file(output_path) # 显示结果
        else:
            # 转换失败 (错误已在Converter或线程中记录)
            logger.warning(f"Conversion failed for {input_path}")
            # (可选) 更新文件列表项的视觉状态以指示失败

        # 清理完成的线程
        if input_path in self.conversion_threads:
            del self.conversion_threads[input_path]

        # 所有文件处理完毕
        if self._conversion_count == self._total_files:
            logger.info("All conversions finished.")
            final_status = f"批量转换完成 ({self._total_files - len(self.conversion_threads)} 成功, {len(self.conversion_threads)} 失败)"
            self.statusBar.set_status(final_status)
            self.statusBar.show_progress(False) # 隐藏进度条

    def add_to_history(self, filename):
        """添加文件到历史记录"""
        logger.info(f"Adding to history: {filename}") # +++ 添加日志 +++
        self.history_list.addItem(filename)
    
    def on_file_double_clicked(self, item):
        """文件列表项双击事件"""
        file_path = item.data(Qt.UserRole)
        logger.debug(f"File list item double-clicked: {file_path}") # +++ 添加日志 +++
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
        logger.debug(f"History list item double-clicked: {filename}") # +++ 添加日志 +++
        output_dir = self.output_path_edit.text()
        file_path = os.path.join(output_dir, filename)
        self.open_markdown_file(file_path)
    
    def new_file(self):
        """创建新文件"""
        logger.info("New file action triggered.") # +++ 添加日志 +++
        self.markdown_editor.set_text("")
        self.statusBar.set_file_info("", "", False)
        self.statusBar.set_status("新建文件")
    
    def open_file(self):
        """打开文件"""
        logger.info("Open file action triggered.") # +++ 添加日志 +++
        self.open_markdown_file()
    
    def save_markdown(self):
        """保存Markdown文件"""
        logger.info("Save markdown action triggered.") # +++ 添加日志 +++
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
                logger.info(f"Markdown file saved successfully: {file_path}") # +++ 添加日志 +++
                return True
            except Exception as e:
                logger.error(f"Failed to save markdown file: {file_path}", exc_info=True) # +++ 修改日志记录 +++
                self.statusBar.set_status(f"保存文件失败: {str(e)}")
        else:
            logger.debug("Save markdown cancelled by user.") # +++ 添加日志 +++

        return False
    
    def open_markdown_file(self, file_path=None):
        """打开Markdown文件"""
        action_triggered = file_path is None # 判断是用户点击菜单触发还是内部调用
        if action_triggered:
            logger.debug("Open markdown file dialog triggered.") # +++ 添加日志 +++
            file_path, _ = self.file_dialogs.get_open_file_name(
                self,
                "打开Markdown文件",
                self.default_dir,
                "Markdown文件 (*.md)"
            )
        else:
             logger.debug(f"Opening markdown file internally: {file_path}") # +++ 添加日志 +++

        if file_path and os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.markdown_editor.set_text(content)
                self.statusBar.set_status(f"已打开: {file_path}")
                self.statusBar.set_file_info(file_path, "Markdown", False)
                logger.info(f"Markdown file opened successfully: {file_path}") # +++ 添加日志 +++
                return True
            except Exception as e:
                logger.error(f"Failed to open markdown file: {file_path}", exc_info=True) # +++ 修改日志记录 +++
                self.statusBar.set_status(f"打开文件失败: {str(e)}")
        elif action_triggered:
             logger.debug("Open markdown cancelled or file not found.") # +++ 添加日志 +++

        return False

if __name__ == "__main__":
    # +++ 在创建 QApplication 之前配置日志 +++
    setup_logging()

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())