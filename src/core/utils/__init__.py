"""
工具模块初始化文件
"""

from .logger import Logger
from .exceptions import (
    FileParsingError,
    MarkdownGenerationError,
    FileWritingError,
    UnsupportedFileTypeError
)

# 创建全局日志实例
logger = Logger()