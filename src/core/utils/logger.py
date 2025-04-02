"""
日志模块，提供日志记录功能
"""

import os
import logging
from datetime import datetime
from typing import Optional

class Logger:
    """
    日志记录器，提供文件和控制台日志记录功能
    """
    
    def __init__(self, log_level: str = "INFO", log_file: Optional[str] = None, console_logging: bool = True):
        """
        初始化日志记录器
        
        Args:
            log_level: 日志级别，可选值为DEBUG, INFO, WARNING, ERROR, CRITICAL
            log_file: 日志文件路径，如果为None则使用默认路径
            console_logging: 是否输出到控制台
        """
        # 设置日志级别
        self.log_level = getattr(logging, log_level.upper())
        
        # 创建日志记录器
        self.logger = logging.getLogger("markdown_converter")
        self.logger.setLevel(self.log_level)
        
        # 清除已有的处理器
        if self.logger.handlers:
            self.logger.handlers.clear()
        
        # 设置日志格式
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        
        # 添加控制台处理器
        if console_logging:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(self.log_level)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
        
        # 添加文件处理器
        if log_file is None:
            # 默认日志文件路径
            log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "logs")
            os.makedirs(log_dir, exist_ok=True)
            log_file = os.path.join(log_dir, f"app_{datetime.now().strftime('%Y%m%d')}.log")
        
        # 确保日志目录存在
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(self.log_level)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
    
    def debug(self, message: str):
        """记录调试信息"""
        self.logger.debug(message)
    
    def info(self, message: str):
        """记录一般信息"""
        self.logger.info(message)
    
    def warning(self, message: str):
        """记录警告信息"""
        self.logger.warning(message)
    
    def error(self, message: str):
        """记录错误信息"""
        self.logger.error(message)
    
    def critical(self, message: str):
        """记录严重错误信息"""
        self.logger.critical(message)
    
    def exception(self, message: str):
        """记录异常信息，包含堆栈跟踪"""
        self.logger.exception(message)
    
    def set_level(self, level: str):
        """
        设置日志级别
        
        Args:
            level: 日志级别，可选值为DEBUG, INFO, WARNING, ERROR, CRITICAL
        """
        new_level = getattr(logging, level.upper())
        self.logger.setLevel(new_level)
        for handler in self.logger.handlers:
            handler.setLevel(new_level)