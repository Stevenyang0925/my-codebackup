import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath('.'))

from src.core.parsers.word_parser import WordParser

def main():
    if len(sys.argv) < 2:
        print("用法: python test_word_parser.py [word文档路径] [可选输出路径]")
        return
    
    file_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        # 初始化WordParser
        parser = WordParser()
        
        # 运行测试转换
        output_file = parser.test_conversion(file_path, output_path)
        
        if output_file:
            print(f"\n测试成功，转换结果已保存至: {output_file}")
        else:
            print("\n测试失败，请检查错误信息")
            
    except Exception as e:
        import traceback
        print(f"测试过程中发生错误: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main() 