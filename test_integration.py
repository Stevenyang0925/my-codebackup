import sys
import os
from PyQt5.QtWidgets import QApplication
from src.gui.main_window import MainWindow
from src.core.converter import Converter

class IntegrationTest:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.window = MainWindow()
        self.converter = Converter()
    
    def setup(self):
        """设置测试环境"""
        # 连接核心功能到GUI
        self.window.converter = self.converter
        
        # 添加转换功能到开始转换按钮
        self.window.convert_button.clicked.disconnect()  # 断开原有连接
        self.window.convert_button.clicked.connect(self.convert_files)
    
    def convert_files(self):
        """转换文件的集成测试"""
        # 获取GUI中的文件列表
        files = self.window.selected_files
        
        if not files:
            self.window.status_label.setText("请先选择文件")
            return
        
        # 获取输出路径 - 修复错误
        # 根据MainWindow实际实现选择正确的属性
        # 方案1: 如果MainWindow中有定义输出路径的LineEdit
        try:
            # 尝试不同可能的属性名
            if hasattr(self.window, 'output_path_edit'):
                output_path = self.window.output_path_edit.text()
            elif hasattr(self.window, 'output_dir'):
                output_path = self.window.output_dir.text()
            else:
                # 如果没有找到相关属性，使用默认输出路径
                output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
                os.makedirs(output_path, exist_ok=True)
        except:
            # 出错时使用默认路径
            output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
            os.makedirs(output_path, exist_ok=True)
        
        # 开始转换
        self.window.status_label.setText("转换中...")
        self.window.progress_bar.setValue(0)
        
        # 批量转换文件
        total = len(files)
        results = {}
        
        for i, file_path in enumerate(files):
            # 更新进度
            progress = int((i / total) * 100)
            self.window.progress_bar.setValue(progress)
            
            # 转换文件
            output_file = self.converter.convert_file(file_path, output_path)
            if output_file:
                results[file_path] = output_file
                
                # 添加到历史记录
                self.window.history_list.addItem(f"{os.path.basename(file_path)} -> {os.path.basename(output_file)}")
        
        # 完成转换
        self.window.progress_bar.setValue(100)
        self.window.status_label.setText(f"转换完成，成功: {len(results)}/{total}")

if __name__ == "__main__":
    test = IntegrationTest()
    test.setup()
    test.window.show()
    sys.exit(test.app.exec_())