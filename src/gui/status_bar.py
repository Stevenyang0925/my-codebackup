# 状态栏模块

from PyQt5.QtWidgets import QStatusBar, QLabel, QProgressBar, QWidget, QHBoxLayout
from PyQt5.QtCore import Qt

class StatusBar(QStatusBar):
    """
    状态栏类，显示程序状态、文件信息和转换进度
    """
    
    def __init__(self, parent=None):
        """初始化状态栏"""
        super().__init__(parent)
        
        # 创建快捷键提示区域
        self.shortcut_hints = QWidget()
        shortcut_layout = QHBoxLayout(self.shortcut_hints)
        shortcut_layout.setContentsMargins(0, 0, 0, 0)
        shortcut_layout.setSpacing(10)
        
        # 添加快捷键提示
        self.add_shortcut_hint(shortcut_layout, "Win+O", "打开文件")
        self.add_shortcut_hint(shortcut_layout, "Win+S", "快速保存")
        
        self.addPermanentWidget(self.shortcut_hints)
        
        # 创建状态文本标签
        self.status_label = QLabel("就绪")
        self.status_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.addPermanentWidget(self.status_label)
        
        # 创建文件信息标签
        self.file_info_label = QLabel("")
        self.addWidget(self.file_info_label, 1)
        
        # 创建进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFixedWidth(150)
        self.progress_bar.setVisible(False)  # 初始隐藏
        self.addWidget(self.progress_bar)
    
    def add_shortcut_hint(self, layout, keys, description):
        """
        添加快捷键提示
        
        参数:
            layout: 布局对象
            keys: 快捷键文本
            description: 描述文本
        """
        hint_label = QLabel()
        hint_label.setText(f"<span style='font-family: monospace; background-color: #F5F5F7; padding: 2px 4px; border-radius: 3px;'>{keys}</span> {description}")
        layout.addWidget(hint_label)
    
    def set_status(self, message):
        """
        设置状态信息
        
        参数:
            message: 状态信息
        """
        self.status_label.setText(message)
    
    def set_file_info(self, file_path="", file_type="", is_modified=False):
        """
        设置文件信息
        
        参数:
            file_path: 文件路径
            file_type: 文件类型
            is_modified: 是否已修改
        """
        if not file_path:
            self.file_info_label.setText("")
            return
        
        # 提取文件名
        import os
        file_name = os.path.basename(file_path)
        
        # 构建显示文本
        info_text = f"{file_name}"
        if file_type:
            info_text += f" | {file_type}"
        if is_modified:
            info_text += " *"
            
        self.file_info_label.setText(info_text)
    
    def show_progress(self, visible=True):
        """
        显示或隐藏进度条
        
        参数:
            visible: 是否可见
        """
        self.progress_bar.setVisible(visible)
        if not visible:
            self.progress_bar.setValue(0)
    
    def set_progress(self, value):
        """
        设置进度值
        
        参数:
            value: 进度值(0-100)
        """
        self.progress_bar.setValue(value)
    
    def start_busy_indicator(self):
        """开始显示忙碌指示器"""
        self.progress_bar.setRange(0, 0)  # 设置为不确定模式
        self.show_progress(True)
    
    def stop_busy_indicator(self):
        """停止显示忙碌指示器"""
        self.progress_bar.setRange(0, 100)  # 恢复为确定模式
        self.show_progress(False)