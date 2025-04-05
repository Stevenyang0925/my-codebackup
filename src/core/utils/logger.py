"""
日志模块，提供日志记录功能
"""

import os
import logging
from datetime import datetime
from typing import Optional
from logging.handlers import RotatingFileHandler

# --- 配置区 ---
LOG_DIR = "logs"  # 日志文件存放目录 (可以考虑从配置读取)
LOG_FILENAME = "app.log"  # 日志文件名
MAX_BYTES = 10 * 1024 * 1024  # 日志文件最大大小 (10MB)
BACKUP_COUNT = 5  # 保留的备份文件数量
CONSOLE_LOG_LEVEL = logging.INFO  # 控制台输出级别
FILE_LOG_LEVEL = logging.DEBUG  # 文件输出级别
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
# --- 配置区结束 ---

# 确保日志目录存在
if not os.path.exists(LOG_DIR):
    try:
        os.makedirs(LOG_DIR)
    except OSError as e:
        print(f"Error creating log directory '{LOG_DIR}': {e}")
        # 如果无法创建日志目录，可以选择退出或回退到无文件日志
        LOG_DIR = None # 禁用文件日志

log_file_path = os.path.join(LOG_DIR, LOG_FILENAME) if LOG_DIR else None

# 创建或获取名为 'app' 的 logger
# 使用 getLogger() 而不是 getLogger(__name__) 可以方便地在全局获取同一个 logger 实例
logger = logging.getLogger("app")
logger.setLevel(logging.DEBUG)  # 设置 logger 能处理的最低级别

# --- 控制台 Handler ---
console_handler = logging.StreamHandler()
console_handler.setLevel(CONSOLE_LOG_LEVEL)
console_formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)

# --- 文件 Handler (如果目录创建成功) ---
if log_file_path:
    # 使用 RotatingFileHandler 实现日志文件轮转
    file_handler = RotatingFileHandler(
        log_file_path,
        maxBytes=MAX_BYTES,
        backupCount=BACKUP_COUNT,
        encoding='utf-8' # 明确指定编码
    )
    file_handler.setLevel(FILE_LOG_LEVEL)
    file_formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
else:
    logger.warning("File logging disabled because log directory could not be created.")


# --- 提供一个简单的获取 logger 的函数 ---
def get_logger(name: str = "app"):
    """
    获取配置好的 logger 实例。

    Args:
        name (str): logger 的名称，建议使用模块名 (__name__)。
                    如果使用默认的 'app'，则获取全局配置的 logger。
                    如果使用其他名称，会继承 'app' logger 的配置。

    Returns:
        logging.Logger: 配置好的 logger 实例。
    """
    # 如果需要为不同模块创建不同的 logger，可以使用 logging.getLogger(name)
    # 这里为了简单，暂时都返回同一个根 logger 'app'
    # 如果需要更细粒度的控制，可以改为 return logging.getLogger(name)
    return logger

# --- 移除旧的 Logger 类 ---
# class Logger:
#     ... (旧代码)

# --- 可以在这里添加一些初始日志，确认配置生效 ---
# logger.debug("Logger initialized (debug level).")
# logger.info("Logger initialized (info level).")
# logger.warning("Logger initialized (warning level).")
# logger.error("Logger initialized (error level).")
# logger.critical("Logger initialized (critical level).")