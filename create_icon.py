#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建应用程序图标
"""

from PIL import Image, ImageDraw
import os

def create_icon():
    """创建应用程序图标"""
    # 创建一个简单的图标
    size = (256, 256)
    img = Image.new('RGBA', size, color=(0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 绘制一个简单的DNS图标
    # 背景圆形
    draw.ellipse([(20, 20), (236, 236)], fill=(41, 128, 185), outline=(31, 97, 141), width=5)
    
    # DNS文字
    draw.text((70, 100), "DNS", fill=(255, 255, 255))
    
    # 切换箭头
    draw.polygon([(180, 80), (200, 100), (180, 120)], fill=(255, 255, 255))
    
    # 保存为ICO文件
    img.save('icon.ico')
    
    # 保存为PNG文件
    img.save('icon.png')
    
    print("图标文件已创建: icon.ico 和 icon.png")

if __name__ == "__main__":
    create_icon()