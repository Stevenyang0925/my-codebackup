# 设置对话框模块

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, 
                            QWidget, QLabel, QLineEdit, QCheckBox, QComboBox,
                            QPushButton, QGroupBox, QFormLayout, QSpinBox,
                            QDialogButtonBox, QFileDialog, QColorDialog)
from PyQt5.QtCore import Qt, QSettings, QSize
from PyQt5.QtGui import QIcon

import os

class SettingsDialog(QDialog):
    """设置对话框类，提供程序设置和转换选项的配置界面"""
    
    def __init__(self, parent=None):
        """初始化设置对话框"""
        super().__init__(parent)
        
        # 设置对话框基本属性
        self.setWindowTitle("设置")
        self.setMinimumSize(600, 450)
        
        # 创建设置对象
        self.settings = QSettings("MarkdownConverter", "Settings")
        
        # 初始化UI
        self.init_ui()
        
        # 加载设置
        self.load_settings()
    
    def init_ui(self):
        """初始化UI组件"""
        # 创建主布局
        main_layout = QVBoxLayout(self)
        
        # 创建选项卡控件
        self.tab_widget = QTabWidget()
        
        # 创建各个选项卡
        self.create_general_tab()
        self.create_conversion_tab()
        self.create_appearance_tab()
        self.create_advanced_tab()
        
        main_layout.addWidget(self.tab_widget)
        
        # 创建按钮区域
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.Apply)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        button_box.button(QDialogButtonBox.Apply).clicked.connect(self.apply_settings)
        
        main_layout.addWidget(button_box)
    
    def create_general_tab(self):
        """创建常规选项卡"""
        general_tab = QWidget()
        layout = QVBoxLayout(general_tab)
        
        # 文件和目录组
        file_group = QGroupBox("文件和目录")
        file_layout = QFormLayout()
        
        # 默认保存目录
        self.default_dir_edit = QLineEdit()
        browse_button = QPushButton("浏览...")
        browse_button.clicked.connect(self.browse_default_dir)
        
        dir_layout = QHBoxLayout()
        dir_layout.addWidget(self.default_dir_edit)
        dir_layout.addWidget(browse_button)
        
        file_layout.addRow("默认保存目录:", dir_layout)
        
        # 自动保存选项
        self.auto_save_check = QCheckBox("自动保存转换结果")
        file_layout.addRow("", self.auto_save_check)
        
        # 文件关联选项
        self.associate_md_check = QCheckBox("将.md文件关联到此应用")
        file_layout.addRow("", self.associate_md_check)
        
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # 启动选项组
        startup_group = QGroupBox("启动选项")
        startup_layout = QFormLayout()
        
        # 启动时检查更新
        self.check_update_check = QCheckBox("启动时检查更新")
        startup_layout.addRow("", self.check_update_check)
        
        # 启动时显示欢迎页面
        self.show_welcome_check = QCheckBox("启动时显示欢迎页面")
        startup_layout.addRow("", self.show_welcome_check)
        
        startup_group.setLayout(startup_layout)
        layout.addWidget(startup_group)
        
        # 添加弹性空间
        layout.addStretch()
        
        self.tab_widget.addTab(general_tab, "常规")
    
    def create_conversion_tab(self):
        """创建转换选项卡"""
        conversion_tab = QWidget()
        layout = QVBoxLayout(conversion_tab)
        
        # Markdown格式选项组
        md_group = QGroupBox("Markdown格式")
        md_layout = QFormLayout()
        
        # 标题样式
        self.heading_style_combo = QComboBox()
        self.heading_style_combo.addItems(["ATX风格 (# 标题)", "Setext风格 (标题\n===)"])
        md_layout.addRow("标题样式:", self.heading_style_combo)
        
        # 列表样式
        self.list_style_combo = QComboBox()
        self.list_style_combo.addItems(["短横线 (-)", "星号 (*)", "加号 (+)"])
        md_layout.addRow("列表样式:", self.list_style_combo)
        
        # 代码块样式
        self.code_style_combo = QComboBox()
        self.code_style_combo.addItems(["围栏式 (```)", "缩进式 (    )"])
        md_layout.addRow("代码块样式:", self.code_style_combo)
        
        # 链接样式
        self.link_style_combo = QComboBox()
        self.link_style_combo.addItems(["内联式 [文本](链接)", "引用式 [文本][id]"])
        md_layout.addRow("链接样式:", self.link_style_combo)
        
        md_group.setLayout(md_layout)
        layout.addWidget(md_group)
        
        # 转换选项组
        convert_group = QGroupBox("转换选项")
        convert_layout = QFormLayout()
        
        # 保留原始格式
        self.preserve_format_check = QCheckBox("尽可能保留原始格式")
        convert_layout.addRow("", self.preserve_format_check)
        
        # 自动检测标题
        self.detect_headings_check = QCheckBox("自动检测标题")
        convert_layout.addRow("", self.detect_headings_check)
        
        # 提取图片
        self.extract_images_check = QCheckBox("提取并引用文档中的图片")
        convert_layout.addRow("", self.extract_images_check)
        
        # 表格处理
        self.table_format_combo = QComboBox()
        self.table_format_combo.addItems(["标准Markdown表格", "GFM表格", "HTML表格"])
        convert_layout.addRow("表格格式:", self.table_format_combo)
        
        convert_group.setLayout(convert_layout)
        layout.addWidget(convert_group)
        
        # 添加弹性空间
        layout.addStretch()
        
        self.tab_widget.addTab(conversion_tab, "转换")
    
    def create_appearance_tab(self):
        """创建外观选项卡"""
        appearance_tab = QWidget()
        layout = QVBoxLayout(appearance_tab)
        
        # 主题选项组
        theme_group = QGroupBox("主题")
        theme_layout = QFormLayout()
        
        # 主题选择
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["浅色", "深色", "跟随系统"])
        theme_layout.addRow("应用主题:", self.theme_combo)
        
        # 编辑器主题
        self.editor_theme_combo = QComboBox()
        self.editor_theme_combo.addItems(["默认", "GitHub", "Solarized Light", "Solarized Dark", "Monokai"])
        theme_layout.addRow("编辑器主题:", self.editor_theme_combo)
        
        theme_group.setLayout(theme_layout)
        layout.addWidget(theme_group)
        
        # 字体选项组
        font_group = QGroupBox("字体")
        font_layout = QFormLayout()
        
        # 界面字体大小
        self.ui_font_size_spin = QSpinBox()
        self.ui_font_size_spin.setRange(8, 24)
        self.ui_font_size_spin.setValue(12)
        font_layout.addRow("界面字体大小:", self.ui_font_size_spin)
        
        # 编辑器字体大小
        self.editor_font_size_spin = QSpinBox()
        self.editor_font_size_spin.setRange(8, 36)
        self.editor_font_size_spin.setValue(14)
        font_layout.addRow("编辑器字体大小:", self.editor_font_size_spin)
        
        font_group.setLayout(font_layout)
        layout.addWidget(font_group)
        
        # 预览选项组
        preview_group = QGroupBox("预览")
        preview_layout = QFormLayout()
        
        # 实时预览
        self.live_preview_check = QCheckBox("启用实时预览")
        preview_layout.addRow("", self.live_preview_check)
        
        # 预览刷新间隔
        self.preview_interval_spin = QSpinBox()
        self.preview_interval_spin.setRange(500, 10000)
        self.preview_interval_spin.setValue(2000)
        self.preview_interval_spin.setSingleStep(500)
        self.preview_interval_spin.setSuffix(" 毫秒")
        preview_layout.addRow("预览刷新间隔:", self.preview_interval_spin)
        
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)
        
        # 添加弹性空间
        layout.addStretch()
        
        self.tab_widget.addTab(appearance_tab, "外观")
    
    def create_advanced_tab(self):
        """创建高级选项卡"""
        advanced_tab = QWidget()
        layout = QVBoxLayout(advanced_tab)
        
        # OCR选项组
        ocr_group = QGroupBox("OCR设置")
        ocr_layout = QFormLayout()
        
        # Tesseract路径
        self.tesseract_path_edit = QLineEdit()
        browse_button = QPushButton("浏览...")
        browse_button.clicked.connect(self.browse_tesseract_path)
        
        path_layout = QHBoxLayout()
        path_layout.addWidget(self.tesseract_path_edit)
        path_layout.addWidget(browse_button)
        
        ocr_layout.addRow("Tesseract路径:", path_layout)
        
        # OCR语言
        self.ocr_lang_combo = QComboBox()
        self.ocr_lang_combo.addItems(["中文简体", "中文繁体", "英文", "日文", "韩文", "自动检测"])
        ocr_layout.addRow("OCR语言:", self.ocr_lang_combo)
        
        ocr_group.setLayout(ocr_layout)
        layout.addWidget(ocr_group)
        
        # 性能选项组
        perf_group = QGroupBox("性能")
        perf_layout = QFormLayout()
        
        # 并行处理
        self.parallel_check = QCheckBox("启用并行处理")
        perf_layout.addRow("", self.parallel_check)
        
        # 线程数
        self.thread_count_spin = QSpinBox()
        self.thread_count_spin.setRange(1, 16)
        self.thread_count_spin.setValue(4)
        perf_layout.addRow("最大线程数:", self.thread_count_spin)
        
        # 内存限制
        self.memory_limit_spin = QSpinBox()
        self.memory_limit_spin.setRange(256, 4096)
        self.memory_limit_spin.setValue(1024)
        self.memory_limit_spin.setSuffix(" MB")
        perf_layout.addRow("内存限制:", self.memory_limit_spin)
        
        perf_group.setLayout(perf_layout)
        layout.addWidget(perf_group)
        
        # 日志选项组
        log_group = QGroupBox("日志")
        log_layout = QFormLayout()
        
        # 日志级别
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["调试", "信息", "警告", "错误", "严重"])
        log_layout.addRow("日志级别:", self.log_level_combo)
        
        # 保留日志天数
        self.log_days_spin = QSpinBox()
        self.log_days_spin.setRange(1, 90)
        self.log_days_spin.setValue(30)
        self.log_days_spin.setSuffix(" 天")
        log_layout.addRow("保留日志天数:", self.log_days_spin)
        
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)
        
        # 添加弹性空间
        layout.addStretch()
        
        self.tab_widget.addTab(advanced_tab, "高级")
    
    def browse_default_dir(self):
        """浏览默认保存目录"""
        directory = QFileDialog.getExistingDirectory(self, "选择默认保存目录", self.default_dir_edit.text())
        if directory:
            self.default_dir_edit.setText(directory)
    
    def browse_tesseract_path(self):
        """浏览Tesseract路径"""
        file_path, _ = QFileDialog.getOpenFileName(self, "选择Tesseract可执行文件", 
                                                 self.tesseract_path_edit.text(),
                                                 "可执行文件 (*.exe)")
        if file_path:
            self.tesseract_path_edit.setText(file_path)
    
    def load_settings(self):
        """从QSettings加载设置"""
        # 常规设置
        self.default_dir_edit.setText(self.settings.value("general/default_dir", os.path.expanduser("~/Documents")))
        self.auto_save_check.setChecked(self.settings.value("general/auto_save", False, type=bool))
        self.associate_md_check.setChecked(self.settings.value("general/associate_md", False, type=bool))
        self.check_update_check.setChecked(self.settings.value("general/check_update", True, type=bool))
        self.show_welcome_check.setChecked(self.settings.value("general/show_welcome", True, type=bool))
        
        # 转换设置
        self.heading_style_combo.setCurrentIndex(self.settings.value("conversion/heading_style", 0, type=int))
        self.list_style_combo.setCurrentIndex(self.settings.value("conversion/list_style", 0, type=int))
        self.code_style_combo.setCurrentIndex(self.settings.value("conversion/code_style", 0, type=int))
        self.link_style_combo.setCurrentIndex(self.settings.value("conversion/link_style", 0, type=int))
        self.preserve_format_check.setChecked(self.settings.value("conversion/preserve_format", True, type=bool))
        self.detect_headings_check.setChecked(self.settings.value("conversion/detect_headings", True, type=bool))
        self.extract_images_check.setChecked(self.settings.value("conversion/extract_images", True, type=bool))
        self.table_format_combo.setCurrentIndex(self.settings.value("conversion/table_format", 1, type=int))
        
        # 外观设置
        self.theme_combo.setCurrentIndex(self.settings.value("appearance/theme", 2, type=int))
        self.editor_theme_combo.setCurrentIndex(self.settings.value("appearance/editor_theme", 0, type=int))
        self.ui_font_size_spin.setValue(self.settings.value("appearance/ui_font_size", 12, type=int))
        self.editor_font_size_spin.setValue(self.settings.value("appearance/editor_font_size", 14, type=int))
        self.live_preview_check.setChecked(self.settings.value("appearance/live_preview", True, type=bool))
        self.preview_interval_spin.setValue(self.settings.value("appearance/preview_interval", 2000, type=int))
        
        # 高级设置
        self.tesseract_path_edit.setText(self.settings.value("advanced/tesseract_path", ""))
        self.ocr_lang_combo.setCurrentIndex(self.settings.value("advanced/ocr_lang", 0, type=int))
        self.parallel_check.setChecked(self.settings.value("advanced/parallel", True, type=bool))
        self.thread_count_spin.setValue(self.settings.value("advanced/thread_count", 4, type=int))
        self.memory_limit_spin.setValue(self.settings.value("advanced/memory_limit", 1024, type=int))
        self.log_level_combo.setCurrentIndex(self.settings.value("advanced/log_level", 1, type=int))
        self.log_days_spin.setValue(self.settings.value("advanced/log_days", 30, type=int))
    
    def save_settings(self):
        """保存设置到QSettings"""
        # 常规设置
        self.settings.setValue("general/default_dir", self.default_dir_edit.text())
        self.settings.setValue("general/auto_save", self.auto_save_check.isChecked())
        self.settings.setValue("general/associate_md", self.associate_md_check.isChecked())
        self.settings.setValue("general/check_update", self.check_update_check.isChecked())
        self.settings.setValue("general/show_welcome", self.show_welcome_check.isChecked())
        
        # 转换设置
        self.settings.setValue("conversion/heading_style", self.heading_style_combo.currentIndex())
        self.settings.setValue("conversion/list_style", self.list_style_combo.currentIndex())
        self.settings.setValue("conversion/code_style", self.code_style_combo.currentIndex())
        self.settings.setValue("conversion/link_style", self.link_style_combo.currentIndex())
        self.settings.setValue("conversion/preserve_format", self.preserve_format_check.isChecked())
        self.settings.setValue("conversion/detect_headings", self.detect_headings_check.isChecked())
        self.settings.setValue("conversion/extract_images", self.extract_images_check.isChecked())
        self.settings.setValue("conversion/table_format", self.table_format_combo.currentIndex())
        
        # 外观设置
        self.settings.setValue("appearance/theme", self.theme_combo.currentIndex())
        self.settings.setValue("appearance/editor_theme", self.editor_theme_combo.currentIndex())
        self.settings.setValue("appearance/ui_font_size", self.ui_font_size_spin.value())
        self.settings.setValue("appearance/editor_font_size", self.editor_font_size_spin.value())
        self.settings.setValue("appearance/live_preview", self.live_preview_check.isChecked())
        self.settings.setValue("appearance/preview_interval", self.preview_interval_spin.value())
        
        # 高级设置
        self.settings.setValue("advanced/tesseract_path", self.tesseract_path_edit.text())
        self.settings.setValue("advanced/ocr_lang", self.ocr_lang_combo.currentIndex())
        self.settings.setValue("advanced/parallel", self.parallel_check.isChecked())
        self.settings.setValue("advanced/thread_count", self.thread_count_spin.value())
        self.settings.setValue("advanced/memory_limit", self.memory_limit_spin.value())
        self.settings.setValue("advanced/log_level", self.log_level_combo.currentIndex())
        self.settings.setValue("advanced/log_days", self.log_days_spin.value())
        
        # 同步设置
        self.settings.sync()
    
    def apply_settings(self):
        """应用设置"""
        self.save_settings()
        
        # 通知父窗口设置已更改
        if self.parent():
            if hasattr(self.parent(), 'apply_settings'):
                self.parent().apply_settings()
    
    def accept(self):
        """确定按钮点击处理"""
        self.save_settings()
        super().accept()