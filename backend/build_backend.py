import PyInstaller

import PyInstaller.__main__
import os
import sys

def build_backend():
    print("开始打包后端...")

    # 确保PyInstaller已安装
    try:
        import PyInstaller
    except ImportError:
        print("正在安装PyInstaller...")
        os.system(f"{sys.executable} -m pip install pyinstaller")

    # 使用spec文件进行打包，确保包含所有必要的__init__.py文件
    spec_file = 'kvs_backend.spec'
    if os.path.exists(spec_file):
        print(f"使用spec文件: {spec_file}")
        args = [spec_file]
    else:
        print("spec文件不存在，使用命令行参数")
        # 定义PyInstaller参数
        args = [
            'app.py',
            '--name=kvs_backend',
            '--onefile',
            '--noconsole',
            '--hidden-import=routes.api',
            '--hidden-import=routes.kv',
            '--hidden-import=models',
            '--hidden-import=utils.logger',
            '--add-data=models/__init__.py;models',
            '--add-data=routes/__init__.py;routes',
            '--add-data=utils/__init__.py;utils',
        ]

        # 添加数据文件（如果有）
        if os.path.exists('templates'):
            args.append('--add-data=templates;templates')
        if os.path.exists('static'):
            args.append('--add-data=static;static')

    # 运行PyInstaller
    PyInstaller.__main__.run(args)

    print("后端打包完成！")
    return os.path.abspath(os.path.join('dist', 'kvs_backend.exe'))

if __name__ == "__main__":
    build_backend()
