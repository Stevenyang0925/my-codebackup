# 多格式文本转Markdown工具

一个基于Python开发的桌面应用程序，可以将多种格式的文件（Word、Excel、TXT、PDF和图片）转换为Markdown格式。

## 功能特点

- 支持多种格式文件转换：
  - Word文档（.docx）
  - Excel表格（.xlsx）
  - 文本文件（.txt）
  - PDF文档（.pdf）
  - 图片文件（.jpg, .png等）
- 简洁直观的用户界面
- 自定义输出路径
- 打开、编辑和保存Markdown文件

## 系统要求

- 操作系统：Windows 10/11
- Python 3.8及以上版本（如果从源码运行）
- 对于OCR功能，需要安装Tesseract-OCR

## 安装方法

### 方法一：直接下载安装包（推荐）

1. 从[发布页面](https://github.com/yourusername/markdown-converter/releases)下载最新的安装包（.msi文件）
2. 双击安装包，按照向导完成安装
3. 从开始菜单或桌面快捷方式启动应用

### 方法二：从源码运行

1. 克隆本仓库
```bash
git clone https://github.com/yourusername/markdown-converter.git
cd markdown-converter
```

2. 创建并激活虚拟环境
```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 安装Tesseract-OCR（用于图片文字识别）
   - 从[官方网站](https://github.com/UB-Mannheim/tesseract/wiki)下载并安装
   - 将Tesseract安装路径添加到系统环境变量

5. 运行程序
```bash
python main.py
```

## 使用方法

1. 启动程序
2. 点击"选择文件"按钮，选择要转换的文件
3. 选择输出路径
4. 点击"转换"按钮开始转换
5. 转换完成后，可以在指定路径找到生成的Markdown文件

## 开发者信息

- 开发语言：Python
- GUI框架：PyQt5
- 文件解析：python-docx, pandas, PyPDF2, pytesseract等

## 许可证

本项目采用MIT许可证。详见[LICENSE](LICENSE)文件。 

创建的文件夹和文件结构总结：
核心源代码目录：
src/ - 源代码主目录
src/gui/ - GUI模块目录
src/parsers/ - 解析器模块目录
src/markdown_generator/ - Markdown生成器目录
src/file_output/ - 文件输出模块目录
src/utils/ - 工具和日志模块目录
测试目录：
tests/ - 测试代码目录
tests/test_data/ - 测试数据目录
资源目录：
resources/ - 资源文件主目录
resources/icons/ - 图标资源目录
resources/styles/ - 样式表目录
主要Python文件：
main.py - 程序入口点
setup.py - 安装脚本
package.py - 打包脚本
markdown_converter.spec - PyInstaller规范文件
文档文件：
README.md - 项目说明文档
LICENSE - 许可证文件
开发步骤说明.md - 开发流程文档
.gitignore - Git忽略文件
每个模块的具体文件：
GUI模块: main_window.py
解析器模块: 每种文件格式的解析器和基类
Markdown生成器: generator.py
文件输出: file_saver.py
工具类: 日志和异常处理程序