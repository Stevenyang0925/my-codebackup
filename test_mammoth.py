import mammoth
import sys

def main():
    if len(sys.argv) < 2:
        print("用法: python test_mammoth.py [word文档路径]")
        return
    
    file_path = sys.argv[1]
    
    try:
        with open(file_path, "rb") as docx_file:
            result = mammoth.convert_to_markdown(docx_file)
            markdown = result.value
            
            # 打印转换结果的前300个字符
            print("转换结果预览:")
            print("-" * 50)
            print(markdown[:300] + "..." if len(markdown) > 300 else markdown)
            print("-" * 50)
            
            # 打印警告信息
            if result.messages:
                print("\n警告信息:")
                for message in result.messages:
                    print(f"- {message.message} ({message.type})")
    except Exception as e:
        print(f"转换失败: {e}")

if __name__ == "__main__":
    main()
