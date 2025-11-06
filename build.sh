#!/bin/bash
echo "正在安装必要的依赖..."
pip install pyinstaller pillow

echo ""
echo "正在打包应用程序..."
pyinstaller dns_switcher.spec

echo ""
echo "打包完成！可执行文件位于 dist/DNS切换器"
echo ""