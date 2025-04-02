import os
import sys
from src.core.converter import Converter
import traceback

def test_single_file_conversion(file_path, output_dir):
    """测试单个文件转换"""
    print(f"测试转换文件: {file_path}")
    
    try:
        converter = Converter()
        print(f"创建Converter实例成功")
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            print(f"错误: 文件不存在: {file_path}")
            return False
            
        # 检查输出目录
        if not os.path.exists(output_dir):
            print(f"创建输出目录: {output_dir}")
            os.makedirs(output_dir, exist_ok=True)
        
        print(f"开始转换文件...")
        output_file = converter.convert_file(file_path, output_dir)
        
        if output_file:
            print(f"转换成功! 输出文件: {output_file}")
            # 检查输出文件是否真的存在
            if os.path.exists(output_file):
                print(f"输出文件确实存在，大小: {os.path.getsize(output_file)} 字节")
            else:
                print(f"警告: 输出文件路径返回成功，但文件不存在: {output_file}")
            return True
        else:
            print(f"转换失败! 没有返回输出文件路径")
            return False
    except Exception as e:
        print(f"转换过程中发生异常: {e}")
        traceback.print_exc()
        return False

def test_batch_conversion(file_paths, output_dir):
    """测试批量文件转换"""
    print(f"测试批量转换 {len(file_paths)} 个文件")
    
    try:
        converter = Converter()
        print(f"创建Converter实例成功")
        
        # 检查输出目录
        if not os.path.exists(output_dir):
            print(f"创建输出目录: {output_dir}")
            os.makedirs(output_dir, exist_ok=True)
        
        print(f"开始批量转换文件...")
        results = converter.convert_files(file_paths, output_dir)
        
        success_count = len(results)
        print(f"成功转换: {success_count}/{len(file_paths)} 个文件")
        
        for input_file, output_file in results.items():
            print(f"  {os.path.basename(input_file)} -> {os.path.basename(output_file)}")
            # 检查输出文件是否真的存在
            if os.path.exists(output_file):
                print(f"  输出文件确实存在，大小: {os.path.getsize(output_file)} 字节")
            else:
                print(f"  警告: 输出文件路径返回成功，但文件不存在: {output_file}")
        
        return success_count == len(file_paths)
    except Exception as e:
        print(f"批量转换过程中发生异常: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # 设置固定的测试目录和输出目录
    test_dir = r"E:\PythonProjects\Markdown\test file"
    output_dir = r"E:\PythonProjects\Markdown\output"
    
    print(f"测试目录: {test_dir}")
    print(f"输出目录: {output_dir}")
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 测试文件路径
    test_files = []
    
    # 添加调试信息
    print(f"命令行参数数量: {len(sys.argv)}")
    for i, arg in enumerate(sys.argv):
        print(f"参数 {i}: {arg}")
    
    # 检查命令行参数
    if len(sys.argv) > 1:
        # 使用命令行提供的文件
        for arg in sys.argv[1:]:
            print(f"检查文件路径: {arg}")
            if os.path.exists(arg):
                test_files.append(arg)
                print(f"  文件存在，已添加到测试列表")
            else:
                print(f"  文件不存在: {arg}")
    else:
        # 如果没有提供命令行参数，则使用默认测试目录
        print(f"未提供命令行参数，使用默认测试目录: {test_dir}")
        
        if os.path.exists(test_dir) and os.path.isdir(test_dir):
            # 获取目录中的所有文件
            print(f"读取测试目录中的文件...")
            file_count = 0
            
            # 特别检查两个特定文件
            special_files = ["AI戒指三代硬件需求表.docx", "智能腕表2代.docx"]
            for special_file in special_files:
                special_path = os.path.join(test_dir, special_file)
                if os.path.exists(special_path):
                    print(f"找到特定文件: {special_path}")
                    test_files.append(special_path)
                    file_count += 1
                else:
                    print(f"特定文件不存在: {special_path}")
            
            # 如果没有找到特定文件，则获取目录中的所有文件
            if file_count == 0:
                for file_name in os.listdir(test_dir):
                    file_path = os.path.join(test_dir, file_name)
                    if os.path.isfile(file_path):
                        test_files.append(file_path)
                        print(f"添加测试文件: {file_path}")
                        file_count += 1
            
            print(f"共找到 {file_count} 个测试文件")
        else:
            print(f"默认测试目录不存在或不是一个目录: {test_dir}")
    
    if not test_files:
        print("没有找到可测试的文件")
        print("请提供要测试的文件路径作为命令行参数")
        print("例如: python test_core.py path/to/file1.docx path/to/file2.xlsx")
        print("或者确保默认测试目录中包含测试文件")
        sys.exit(1)
    
    print(f"\n准备开始测试，共 {len(test_files)} 个文件")
    for i, file_path in enumerate(test_files):
        print(f"  {i+1}. {os.path.basename(file_path)}")
    
    # 测试单个文件
    if len(test_files) == 1:
        success = test_single_file_conversion(test_files[0], output_dir)
    # 测试批量转换
    else:
        success = test_batch_conversion(test_files, output_dir)
    
    if success:
        print("\n所有测试通过!")
    else:
        print("\n测试失败!")