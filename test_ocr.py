import pytesseract
from PIL import Image

# 如果需要，指定 Tesseract 路径
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# 打开图片
image = Image.open('path_to_your_image.png')

# 进行 OCR 识别（使用中文+英文）
text = pytesseract.image_to_string(image, lang='chi_sim+eng')

# 打印识别结果
print(text)