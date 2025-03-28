# 工具栏模块

from PyQt5.QtWidgets import QToolBar, QAction, QComboBox, QLabel
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtCore import Qt, QSize

import os

class ToolBar(QToolBar):
    """
    工具栏类，提供常用操作的快捷访问
    """
    
    def __init__(self, parent=None):
        """初始化工具栏"""
        super().__init__(parent)
        self.setMovable(False)
        self.setIconSize(QSize(24, 24))
        self.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        
        # 获取图标路径
        self.icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                     "resources", "icons")
        
        # 创建工具栏按钮
        self.create_file_actions()
        self.addSeparator()
        self.create_edit_actions()
        self.addSeparator()
        self.create_convert_actions()
    
    def create_file_actions(self):
        """创建文件操作按钮"""
        # 新建按钮
        self.new_action = QAction(self.get_icon("new.png"), "新建", self)
        self.new_action.setShortcut(QKeySequence.New)
        self.new_action.setStatusTip("创建新文件")
        self.addAction(self.new_action)
        
        # 打开按钮
        self.open_action = QAction(self.get_icon("open.png"), "打开", self)
        self.open_action.setShortcut(QKeySequence.Open)
        self.open_action.setStatusTip("打开文件")
        self.addAction(self.open_action)
        
        # 保存按钮
        self.save_action = QAction(self.get_icon("save.png"), "保存", self)
        self.save_action.setShortcut(QKeySequence.Save)
        self.save_action.setStatusTip("保存文件")
        self.addAction(self.save_action)
        
        # 导入按钮
        self.import_action = QAction(self.get_icon("import.png"), "导入", self)
        self.import_action.setStatusTip("导入文件")
        self.addAction(self.import_action)
    
    def create_edit_actions(self):
        """创建编辑操作按钮"""
        # 撤销按钮
        self.undo_action = QAction(self.get_icon("undo.png"), "撤销", self)
        self.undo_action.setShortcut(QKeySequence.Undo)
        self.undo_action.setStatusTip("撤销上一步操作")
        self.addAction(self.undo_action)
        
        # 重做按钮
        self.redo_action = QAction(self.get_icon("redo.png"), "重做", self)
        self.redo_action.setShortcut(QKeySequence.Redo)
        self.redo_action.setStatusTip("重做上一步操作")
        self.addAction(self.redo_action)
    
    def create_convert_actions(self):
        """创建转换操作按钮"""
        # 转换按钮
        self.convert_action = QAction(self.get_icon("convert.png"), "转换", self)
        self.convert_action.setStatusTip("开始转换为Markdown")
        self.addAction(self.convert_action)
        
        # 预览按钮
        self.preview_action = QAction(self.get_icon("preview.png"), "预览", self)
        self.preview_action.setStatusTip("预览Markdown效果")
        self.preview_action.setCheckable(True)
        self.addAction(self.preview_action)
        
        # 分屏按钮
        self.split_action = QAction(self.get_icon("split.png"), "分屏", self)
        self.split_action.setStatusTip("编辑/预览分屏模式")
        self.split_action.setCheckable(True)
        self.addAction(self.split_action)
    
    def get_icon(self, icon_name):
        """
        获取图标
        
        参数:
            icon_name: 图标文件名
            
        返回:
            QIcon对象
        """
        icon_file = os.path.join(self.icon_path, icon_name)
        if os.path.exists(icon_file):
            return QIcon(icon_file)
        else:
            # 如果图标文件不存在，返回空图标
            return QIcon()
    
    def connect_actions(self, main_window):
        """
        连接工具栏按钮到主窗口的槽函数
        
        参数:
            main_window: 主窗口对象
        """
        # 文件操作
        if hasattr(main_window, 'new_file'):
            self.new_action.triggered.connect(main_window.new_file)
        
        if hasattr(main_window, 'open_file'):
            self.open_action.triggered.connect(main_window.open_file)
        
        if hasattr(main_window, 'save_markdown'):
            self.save_action.triggered.connect(main_window.save_markdown)
        
        if hasattr(main_window, 'browse_input_file'):
            self.import_action.triggered.connect(main_window.browse_input_file)
        
        # 编辑操作
        if hasattr(main_window, 'markdown_editor'):
            self.undo_action.triggered.connect(lambda: main_window.markdown_editor.get_current_editor().undo())
            self.redo_action.triggered.connect(lambda: main_window.markdown_editor.get_current_editor().redo())
        
        # 转换操作
        if hasattr(main_window, 'convert_to_markdown'):
            self.convert_action.triggered.connect(main_window.convert_to_markdown)
        
        # 预览和分屏操作
        if hasattr(main_window, 'markdown_editor'):
            self.preview_action.triggered.connect(lambda checked: 
                main_window.markdown_editor.tab_widget.setCurrentIndex(1 if checked else 0))
            
            self.split_action.triggered.connect(lambda checked: 
                main_window.markdown_editor.tab_widget.setCurrentIndex(2 if checked else 0))