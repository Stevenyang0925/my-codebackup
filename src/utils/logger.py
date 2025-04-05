"""
日志工具模块，提供统一的日志配置和获取接口
"""

import logging
import logging.handlers
import os
import sys

# --- 配置常量 ---
LOG_DIR = "logs"  # 日志文件存放目录 (相对于项目根目录或运行脚本的位置)
LOG_FILENAME = "converter_app.log" # 日志文件名
# 日志格式: 时间 - 日志级别 - Logger名称 - 函数名 - 行号 - 消息
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(name)s - %(funcName)s:%(lineno)d - %(message)s"
# 控制台日志级别 (INFO 及以上)
CONSOLE_LOG_LEVEL = logging.INFO
# 文件日志级别 (DEBUG 及以上，记录更详细的信息到文件)
FILE_LOG_LEVEL = logging.DEBUG
# 日志文件最大大小 (例如 10MB)
LOG_FILE_MAX_BYTES = 10 * 1024 * 1024
# 保留的旧日志文件数量
LOG_FILE_BACKUP_COUNT = 5

# --- 确保日志目录存在 ---
if not os.path.exists(LOG_DIR):
    try:
        os.makedirs(LOG_DIR)
    except OSError as e:
        # 如果创建目录失败，打印错误到 stderr 并继续（日志可能无法写入文件）
        print(f"错误：无法创建日志目录 '{LOG_DIR}': {e}", file=sys.stderr)
        LOG_DIR = "." # 尝试在当前目录记录

# --- 全局标志，防止重复配置 ---
_logging_configured = False

def setup_logging():
    """
    配置全局日志记录器。
    应该在应用程序启动时调用一次。
    """
    global _logging_configured
    if _logging_configured:
        # 如果已经配置过，直接返回，避免重复添加 handlers
        return

    # 获取根 logger
    root_logger = logging.getLogger()
    # 设置根 logger 的级别为最低（DEBUG），让 handlers 控制实际输出级别
    root_logger.setLevel(logging.DEBUG)

    # 创建日志格式器
    formatter = logging.Formatter(LOG_FORMAT)

    # --- 配置控制台输出 (StreamHandler) ---
    console_handler = logging.StreamHandler(sys.stdout) # 输出到标准输出
    console_handler.setLevel(CONSOLE_LOG_LEVEL) # 设置控制台处理器的级别
    console_handler.setFormatter(formatter) # 应用格式器
    root_logger.addHandler(console_handler) # 添加到根 logger

    # --- 配置文件输出 (RotatingFileHandler) ---
    log_file_path = os.path.join(LOG_DIR, LOG_FILENAME)
    try:
        # 使用 RotatingFileHandler 实现日志轮转
        file_handler = logging.handlers.RotatingFileHandler(
            log_file_path,
            maxBytes=LOG_FILE_MAX_BYTES,
            backupCount=LOG_FILE_BACKUP_COUNT,
            encoding='utf-8' # 确保使用 UTF-8 编码
        )
        file_handler.setLevel(FILE_LOG_LEVEL) # 设置文件处理器的级别
        file_handler.setFormatter(formatter) # 应用格式器
        root_logger.addHandler(file_handler) # 添加到根 logger
    except Exception as e:
        # 如果文件处理器设置失败，记录到控制台
        root_logger.error(f"无法设置文件日志处理器到 '{log_file_path}': {e}", exc_info=True)


    # 标记为已配置
    _logging_configured = True
    root_logger.info("日志系统已配置完成。") # 记录一条配置完成的消息

def get_logger(name: str) -> logging.Logger:
    """
    获取一个指定名称的 logger 实例。
    所有通过此函数获取的 logger 都会继承 setup_logging() 设置的配置。

    Args:
        name: logger 的名称，通常使用 __name__ 获取调用模块的名称。

    Returns:
        配置好的 logger 实例。
    """
    # setup_logging() # 不在这里调用，应在主程序入口调用
    return logging.getLogger(name)

# --- 重要提示 ---
# setup_logging() 函数需要在应用程序的主入口点调用一次，
# 例如在 src/gui/main_window.py 的 if __name__ == "__main__": 块中，
# 或者在专门的 main.py 启动脚本中。
# 示例调用:
# if __name__ == "__main__":
#     from src.utils.logger import setup_logging
#     setup_logging() # 在创建 QApplication 之前调用
#     app = QApplication(sys.argv)
#     # ... rest of the app startup ...
