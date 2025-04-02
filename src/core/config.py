"""
配置模块，存储全局配置信息
"""

import os
from typing import Dict, Any

class Config:
    """配置类，管理应用程序的全局配置"""
    
    def __init__(self):
        """初始化配置"""
        # 默认配置
        self.default_config = {
            # 输出设置
            "output": {
                "default_path": os.path.expanduser("~/Documents"),
                "default_filename": "markdown_output",
                "auto_open_after_save": True,
            },
            
            # 转换设置
            "conversion": {
                "preserve_images": True,
                "extract_tables": True,
                "detect_headings": True,
                "detect_lists": True,
                "code_block_style": "fenced",  # fenced 或 indented
            },
            
            # OCR设置
            "ocr": {
                "language": "chi_sim+eng",  # 中文简体+英文
                "page_segmentation_mode": 3,  # 3=全自动页面分割，但没有OSD
                "oem": 3,  # 3=默认，基于LSTM的OCR引擎和传统的Tesseract引擎
            },
            
            # 界面设置
            "ui": {
                "theme": "light",  # light 或 dark
                "font_size": 12,
                "editor_font_family": "Consolas, 'Courier New', monospace",
                "preview_font_family": "Arial, sans-serif",
                "show_line_numbers": True,
                "word_wrap": True,
            },
            
            # 日志设置
            "logging": {
                "level": "INFO",  # DEBUG, INFO, WARNING, ERROR, CRITICAL
                "file_logging": True,
                "console_logging": True,
                "log_file_path": "logs/app.log",
            }
        }
        
        # 当前配置，初始为默认配置
        self.current_config = self.default_config.copy()
    
    def get(self, section: str, key: str = None) -> Any:
        """
        获取配置值
        
        Args:
            section: 配置节名称
            key: 配置项名称，如果为None则返回整个节
            
        Returns:
            配置值
        """
        if section not in self.current_config:
            return None
        
        if key is None:
            return self.current_config[section]
        
        if key not in self.current_config[section]:
            return None
        
        return self.current_config[section][key]
    
    def set(self, section: str, key: str, value: Any) -> bool:
        """
        设置配置值
        
        Args:
            section: 配置节名称
            key: 配置项名称
            value: 配置值
            
        Returns:
            bool: 设置是否成功
        """
        if section not in self.current_config:
            self.current_config[section] = {}
        
        self.current_config[section][key] = value
        return True
    
    def reset_to_default(self) -> None:
        """重置为默认配置"""
        self.current_config = self.default_config.copy()
    
    def load_from_file(self, file_path: str) -> bool:
        """
        从文件加载配置
        
        Args:
            file_path: 配置文件路径
            
        Returns:
            bool: 加载是否成功
        """
        try:
            import json
            with open(file_path, 'r', encoding='utf-8') as f:
                loaded_config = json.load(f)
                
            # 合并配置，保留默认配置中存在但加载配置中不存在的项
            for section, section_config in self.default_config.items():
                if section not in loaded_config:
                    loaded_config[section] = section_config
                else:
                    for key, value in section_config.items():
                        if key not in loaded_config[section]:
                            loaded_config[section][key] = value
            
            self.current_config = loaded_config
            return True
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            return False
    
    def save_to_file(self, file_path: str) -> bool:
        """
        保存配置到文件
        
        Args:
            file_path: 配置文件路径
            
        Returns:
            bool: 保存是否成功
        """
        try:
            import json
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.current_config, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"保存配置文件失败: {e}")
            return False

# 创建全局配置实例
config = Config()