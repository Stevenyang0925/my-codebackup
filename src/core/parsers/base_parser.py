"""
基础解析器模块，定义所有解析器的基类和通用接口
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

class BaseParser(ABC):
    """
    解析器基类，定义所有解析器的通用接口
    """
    
    @abstractmethod
    def parse(self, file_path: str) -> Dict[str, Any]:
        """
        解析文件内容
        
        Args:
            file_path: 文件路径
            
        Returns:
            Dict[str, Any]: 解析结果，包含以下字段：
                - title: 文档标题
                - content: 内容列表，每个元素是一个字典，包含以下字段：
                    - type: 内容类型，如heading, text, list, table, image, code, link等
                    - content: 内容文本
                    - level: 仅用于heading类型，表示标题级别
                    - additional_info: 额外信息，如表格数据、图片路径等
        """
        pass
    
    @abstractmethod
    def get_supported_extensions(self) -> List[str]:
        """
        获取支持的文件扩展名列表
        
        Returns:
            List[str]: 支持的文件扩展名列表，如['.docx', '.doc']
        """
        pass
    
    def is_supported(self, file_path: str) -> bool:
        """
        检查文件是否被支持
        
        Args:
            file_path: 文件路径
            
        Returns:
            bool: 是否支持该文件
        """
        import os
        _, ext = os.path.splitext(file_path)
        return ext.lower() in self.get_supported_extensions()
    
    def extract_title(self, file_path: str) -> str:
        """
        从文件路径中提取标题
        
        Args:
            file_path: 文件路径
            
        Returns:
            str: 文件标题
        """
        import os
        base_name = os.path.basename(file_path)
        title, _ = os.path.splitext(base_name)
        return title

    @staticmethod
    def get_parser_for_file(file_path: str) -> Optional['BaseParser']:
        """
        根据文件路径获取合适的解析器
        
        Args:
            file_path: 文件路径
            
        Returns:
            Optional[BaseParser]: 合适的解析器实例，如果没有找到则返回None
        """
        import os
        from importlib import import_module
        
        # 获取文件扩展名
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        # 动态导入所有解析器
        parsers_dir = os.path.dirname(os.path.abspath(__file__))
        for file in os.listdir(parsers_dir):
            if file.endswith('_parser.py') and file != 'base_parser.py':
                module_name = file[:-3]  # 去掉.py
                try:
                    module = import_module(f'src.core.parsers.{module_name}')
                    # 查找模块中的解析器类
                    for attr_name in dir(module):
                        if attr_name.endswith('Parser') and attr_name != 'BaseParser':
                            parser_class = getattr(module, attr_name)
                            try:
                                parser = parser_class()
                                if ext in parser.get_supported_extensions():
                                    return parser
                            except:
                                continue
                except:
                    continue
        
        return None