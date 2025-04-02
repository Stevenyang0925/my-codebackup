"""
转换器模块，负责协调文件解析、Markdown生成和文件输出
"""

import os
from typing import Dict, List, Any, Optional

from .parsers import get_parser_for_file
from .markdown.markdown_generator import MarkdownGenerator
from .output.file_writer import FileWriter
from .utils.logger import Logger
from .utils.exceptions import (
    FileParsingError,
    MarkdownGenerationError,
    FileWritingError,
    UnsupportedFileTypeError
)

class Converter:
    """
    转换器类，负责将各种格式的文件转换为Markdown
    """
    
    def __init__(self):
        """初始化转换器"""
        self.markdown_generator = MarkdownGenerator()
        self.file_writer = FileWriter()
        self.logger = Logger()
    
    def convert_file(self, file_path: str, output_dir: str, output_filename: Optional[str] = None) -> Optional[str]:
        """
        转换单个文件为Markdown
        
        Args:
            file_path: 输入文件路径
            output_dir: 输出目录路径
            output_filename: 输出文件名，如果为None则自动生成
            
        Returns:
            Optional[str]: 输出文件路径，如果转换失败则返回None
        """
        try:
            self.logger.info(f"开始转换文件: {file_path}")
            
            # 获取合适的解析器
            parser = get_parser_for_file(file_path)
            self.logger.info(f"使用解析器: {parser.__class__.__name__}")
            
            # 解析文件
            parsed_data = parser.parse(file_path)
            self.logger.info(f"文件解析完成: {file_path}")
            
            # 生成Markdown
            markdown_content = self.markdown_generator.generate(parsed_data)
            self.logger.info(f"Markdown生成完成")
            
            # 如果没有提供输出文件名，则使用原文件名
            if output_filename is None:
                base_name = os.path.basename(file_path)
                output_filename = os.path.splitext(base_name)[0] + ".md"
            
            # 写入文件
            output_file = self.file_writer.write(markdown_content, output_dir, output_filename)
            self.logger.info(f"文件保存成功: {output_file}")
            
            return output_file
            
        except UnsupportedFileTypeError as e:
            self.logger.error(f"不支持的文件类型: {file_path}")
            return None
        except FileParsingError as e:
            self.logger.error(f"解析文件失败: {e}")
            return None
        except MarkdownGenerationError as e:
            self.logger.error(f"生成Markdown失败: {e}")
            return None
        except FileWritingError as e:
            self.logger.error(f"保存文件失败: {e}")
            return None
        except Exception as e:
            self.logger.exception(f"转换文件时发生未知错误: {e}")
            return None
    
    def convert_files(self, file_paths: List[str], output_dir: str) -> Dict[str, str]:
        """
        批量转换文件为Markdown
        
        Args:
            file_paths: 输入文件路径列表
            output_dir: 输出目录路径
            
        Returns:
            Dict[str, str]: 输入文件路径到输出文件路径的映射
        """
        results = {}
        
        for file_path in file_paths:
            output_file = self.convert_file(file_path, output_dir)
            if output_file:
                results[file_path] = output_file
        
        return results