# 文件对话框模块

from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import QDir

class FileDialogs:
    """
    文件对话框类，提供文件选择、保存和目录选择功能
    """
    
    def __init__(self):
        """初始化文件对话框类"""
        # 设置默认目录为用户文档目录
        self.default_dir = QDir.homePath()
        
        # 支持的文件类型过滤器
        self.supported_formats = {
            "all": "所有支持的文件 (*.docx *.xlsx *.txt *.pdf *.jpg *.png *.jpeg *.md)",
            "word": "Word文档 (*.docx)",
            "excel": "Excel表格 (*.xlsx)",
            "text": "文本文件 (*.txt)",
            "pdf": "PDF文档 (*.pdf)",
            "image": "图片文件 (*.jpg *.png *.jpeg)",
            "markdown": "Markdown文件 (*.md)"
        }
        
        # 默认过滤器列表（用于打开文件对话框）
        self.default_filters = [
            self.supported_formats["all"],
            self.supported_formats["word"],
            self.supported_formats["excel"],
            self.supported_formats["text"],
            self.supported_formats["pdf"],
            self.supported_formats["image"],
            self.supported_formats["markdown"]
        ]
    
    def get_open_file_name(self, parent=None, caption="打开文件", directory="", filter="", options=None):
        """
        打开单个文件选择对话框
        
        参数:
            parent: 父窗口
            caption: 对话框标题
            directory: 初始目录
            filter: 文件过滤器
            options: 对话框选项
            
        返回:
            选中的文件路径和选中的过滤器
        """
        if not directory:
            directory = self.default_dir
            
        if not filter:
            filter = ";;".join(self.default_filters)
            
        if options is None:
            options = QFileDialog.Options()
            
        return QFileDialog.getOpenFileName(parent, caption, directory, filter, options=options)
    
    def get_open_file_names(self, parent=None, caption="打开文件", directory="", filter="", options=None):
        """
        打开多个文件选择对话框
        
        参数:
            parent: 父窗口
            caption: 对话框标题
            directory: 初始目录
            filter: 文件过滤器
            options: 对话框选项
            
        返回:
            选中的文件路径列表和选中的过滤器
        """
        if not directory:
            directory = self.default_dir
            
        if not filter:
            filter = ";;".join(self.default_filters)
            
        if options is None:
            options = QFileDialog.Options()
            
        return QFileDialog.getOpenFileNames(parent, caption, directory, filter, options=options)
    
    def get_save_file_name(self, parent=None, caption="保存文件", directory="", filter="", options=None):
        """
        打开保存文件对话框
        
        参数:
            parent: 父窗口
            caption: 对话框标题
            directory: 初始目录
            filter: 文件过滤器
            options: 对话框选项
            
        返回:
            选择的保存路径和选中的过滤器
        """
        if not directory:
            directory = self.default_dir
            
        if not filter:
            filter = self.supported_formats["markdown"]
            
        if options is None:
            options = QFileDialog.Options()
            
        return QFileDialog.getSaveFileName(parent, caption, directory, filter, options=options)
    
    def get_existing_directory(self, parent=None, caption="选择目录", directory="", options=None):
        """
        打开目录选择对话框
        
        参数:
            parent: 父窗口
            caption: 对话框标题
            directory: 初始目录
            options: 对话框选项
            
        返回:
            选择的目录路径
        """
        if not directory:
            directory = self.default_dir
            
        if options is None:
            options = QFileDialog.Options() | QFileDialog.ShowDirsOnly
            
        return QFileDialog.getExistingDirectory(parent, caption, directory, options=options)
    
    def set_default_directory(self, directory):
        """
        设置默认目录
        
        参数:
            directory: 新的默认目录
        """
        self.default_dir = directory