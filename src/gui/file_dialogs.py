from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import QObject, Qt, QDir
import os


class FileDialogs(QObject):
    """文件对话框工具类，处理文件选择、保存等操作"""
    
    def __init__(self, parent=None):
        """初始化文件对话框工具类
        
        Args:
            parent: 父窗口对象
        """
        super(FileDialogs, self).__init__(parent)
        self.parent = parent
    
    def get_open_files(self, caption="选择文件", directory="", file_filter=""):
        """打开文件选择对话框，支持多选
        
        Args:
            caption: 对话框标题
            directory: 初始目录
            file_filter: 文件过滤器字符串
            
        Returns:
            选择的文件路径列表，如果取消则返回空列表
        """
        if not file_filter:
            file_filter = "Word文档 (*.docx);;Excel表格 (*.xlsx);;文本文件 (*.txt);;PDF文档 (*.pdf);;图片文件 (*.jpg *.jpeg *.png *.bmp *.gif);;所有文件 (*.*)"
        
        files, _ = QFileDialog.getOpenFileNames(
            self.parent,
            caption,
            directory,
            file_filter
        )
        
        return files
    
    def get_open_file(self, caption="选择文件", directory="", file_filter=""):
        """打开文件选择对话框，单选
        
        Args:
            caption: 对话框标题
            directory: 初始目录
            file_filter: 文件过滤器字符串
            
        Returns:
            选择的文件路径，如果取消则返回空字符串
        """
        if not file_filter:
            file_filter = "Markdown文件 (*.md);;所有文件 (*.*)"
        
        file, _ = QFileDialog.getOpenFileName(
            self.parent,
            caption,
            directory,
            file_filter
        )
        
        return file
    
    def get_save_file(self, caption="保存文件", directory="", file_filter=""):
        """打开文件保存对话框"""
        if not file_filter:
            file_filter = "Markdown文件 (*.md);;所有文件 (*.*)"
        
        # 确保目录有效
        if not directory or not os.path.isdir(directory):
            directory = os.path.expanduser("~")  # 默认用户主目录
        
        # 添加默认文件名
        directory = os.path.join(directory, "转换结果.md")
        
        file, _ = QFileDialog.getSaveFileName(
            self.parent,
            caption,
            directory,
            file_filter
        )
        return file
    
    def get_existing_directory(self, caption="选择文件夹", directory=""):
        """打开文件夹选择对话框
        
        Args:
            caption: 对话框标题
            directory: 初始目录
            
        Returns:
            选择的文件夹路径，如果取消则返回空字符串
        """
        options = QFileDialog.Options()
        options |= QFileDialog.ShowDirsOnly
        
        directory = QFileDialog.getExistingDirectory(
            self.parent,
            caption,
            directory,
            options=options
        )
        
        return directory

