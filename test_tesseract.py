import pytesseract
from PIL import Image

# 指定 Tesseract 可执行文件的路径
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# 打印 Tesseract 版本信息
print("Tesseract 版本:", pytesseract.get_tesseract_version())

# 列出可用的语言
print("可用语言:", pytesseract.get_languages())

# 测试实际图片OCR功能
try:
    # 替换为您的测试图片路径
    test_image_path = r"e:\PythonProjects\Markdown\test_image.png"
    image = Image.open(test_image_path)
    
    # 使用中文+英文进行OCR识别
    text = pytesseract.image_to_string(image, lang='chi_sim+eng')
    
    print("\n识别结果:")
    print("-" * 50)
    print(text)
    print("-" * 50)
    
except FileNotFoundError:
    print("\n未找到测试图片文件，请修改图片路径后重试")
except Exception as e:
    print(f"\nOCR处理出错: {str(e)}")

print("\nTesseract 安装验证完成！")