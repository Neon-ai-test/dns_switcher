# DNS切换器 - 桌面应用程序

这是一个简单的桌面应用程序，用于在Windows和Linux系统上快速切换DNS设置，可以在1.1.1.1和自动获取DNS之间切换。

## 功能特点

- 图形化用户界面，操作简单直观
- 支持自动获取DNS和手动设置DNS
- 预设1.1.1.1 (Cloudflare DNS)选项
- 支持自定义DNS服务器地址
- 实时显示当前DNS状态
- 操作日志记录

## 文件说明

- `dns_switcher_gui.py` - GUI应用程序主文件
- `dns_switcher.py` - 命令行版本的DNS切换脚本
- `dns_switcher.spec` - PyInstaller打包配置文件
- `build.bat` - Windows打包脚本
- `build.sh` - Linux/Mac打包脚本
- `create_icon.py` - 应用程序图标生成脚本
- `icon.ico` - 应用程序图标文件

## 使用方法

### 运行源代码

1. 确保已安装Python 3.6或更高版本
2. 安装依赖：`pip install pillow`
3. 运行GUI应用程序：`python dns_switcher_gui.py`

### 打包成可执行文件

#### Windows系统

1. 双击运行 `build.bat` 脚本
2. 等待打包完成
3. 在 `dist` 目录中找到 `DNS切换器.exe` 文件

#### Linux/Mac系统

1. 在终端中运行：`chmod +x build.sh && ./build.sh`
2. 等待打包完成
3. 在 `dist` 目录中找到可执行文件

## 注意事项

- 在Windows系统上修改DNS设置需要管理员权限
- 应用程序会自动检测当前网络适配器
- 修改DNS设置可能会暂时中断网络连接

## 技术实现

- 使用Python的tkinter库创建GUI界面
- 使用subprocess模块执行系统命令
- 使用PyInstaller打包成独立可执行文件
- 使用Pillow库创建应用程序图标