"""
基础解析器模块，定义所有解析器的基类和通用接口
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import os
from importlib import import_module
from ..utils.logger import get_logger

# 获取 logger 实例
logger = get_logger(__name__)

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
        _, ext = os.path.splitext(file_path)
        supported = ext.lower() in self.get_supported_extensions()
        # logger.debug(f"Checking support for '{file_path}'. Extension '{ext.lower()}' supported: {supported} by {self.__class__.__name__}")
        return supported
    
    def extract_title(self, file_path: str) -> str:
        """
        从文件路径中提取标题
        
        Args:
            file_path: 文件路径
            
        Returns:
            str: 文件标题
        """
        _, ext = os.path.splitext(file_path)
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
        logger.info(f"尝试为文件查找解析器: {file_path}")

        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        logger.debug(f"文件扩展名: {ext}")

        parsers_dir = os.path.dirname(os.path.abspath(__file__))
        logger.debug(f"扫描解析器目录: {parsers_dir}")

        for file in os.listdir(parsers_dir):
            if file.endswith('_parser.py') and file != 'base_parser.py':
                module_name = file[:-3]  # 去掉.py
                full_module_name = f'src.core.parsers.{module_name}'
                logger.debug(f"尝试导入模块: {full_module_name}")
                try:
                    module = import_module(full_module_name)
                    # 查找模块中的解析器类
                    for attr_name in dir(module):
                        if attr_name.endswith('Parser') and attr_name != 'BaseParser':
                            parser_class = getattr(module, attr_name)
                            logger.debug(f"在 {full_module_name} 中找到潜在解析器类: {attr_name}")
                            try:
                                # 检查是否是 BaseParser 的子类并且不是 BaseParser 本身
                                if issubclass(parser_class, BaseParser) and parser_class is not BaseParser:
                                    parser = parser_class()
                                    supported_extensions = parser.get_supported_extensions()
                                    logger.debug(f"解析器 {attr_name} 支持的扩展名: {supported_extensions}")
                                    if ext in supported_extensions:
                                        logger.info(f"找到匹配的解析器: {attr_name} for extension {ext}")
                                        return parser
                            except Exception as e_instantiate:
                                logger.warning(f"实例化解析器 {attr_name} 失败: {e_instantiate}", exc_info=False)
                                continue
                except ImportError as e_import:
                    logger.error(f"导入解析器模块 {full_module_name} 失败: {e_import}", exc_info=False)
                    continue
                except Exception as e_general:
                     logger.error(f"在模块 {full_module_name} 中查找解析器时出错: {e_general}", exc_info=True)
                     continue

        logger.warning(f"未能为文件 {file_path} (扩展名: {ext}) 找到合适的解析器")
        return None