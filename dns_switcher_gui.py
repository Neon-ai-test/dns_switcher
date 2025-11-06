#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DNS切换器 - 桌面应用程序
可以在1.1.1.1和自动获取DNS之间切换
"""

import os
import sys
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import platform
import re


class DnsSwitcherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DNS切换器")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        # 设置窗口图标（如果存在）
        try:
            if os.path.exists("icon.ico"):
                self.root.iconbitmap("icon.ico")
        except:
            pass
        
        # 创建主框架
        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(main_frame, text="DNS切换器", font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # 当前DNS状态框架
        status_frame = ttk.LabelFrame(main_frame, text="当前DNS状态", padding="10")
        status_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.status_label = ttk.Label(status_frame, text="正在获取DNS状态...", font=("Arial", 10))
        self.status_label.pack(anchor=tk.W)
        
        # DNS选项框架
        options_frame = ttk.LabelFrame(main_frame, text="DNS选项", padding="10")
        options_frame.pack(fill=tk.X, pady=(0, 20))
        
        # 自动获取DNS选项
        self.dhcp_var = tk.BooleanVar()
        self.dhcp_radio = ttk.Radiobutton(
            options_frame, 
            text="自动获取DNS", 
            variable=self.dhcp_var, 
            value=True,
            command=self.on_option_change
        )
        self.dhcp_radio.pack(anchor=tk.W, pady=5)
        
        # 1.1.1.1选项
        self.cloudflare_var = tk.BooleanVar()
        self.cloudflare_radio = ttk.Radiobutton(
            options_frame, 
            text="使用 1.1.1.1 (Cloudflare DNS)", 
            variable=self.dhcp_var, 
            value=False,
            command=self.on_option_change
        )
        self.cloudflare_radio.pack(anchor=tk.W, pady=5)
        
        # 自定义DNS选项
        custom_frame = ttk.Frame(options_frame)
        custom_frame.pack(fill=tk.X, pady=10)
        
        self.custom_var = tk.BooleanVar()
        self.custom_check = ttk.Checkbutton(
            custom_frame, 
            text="使用自定义DNS:", 
            variable=self.custom_var,
            command=self.on_custom_check
        )
        self.custom_check.pack(side=tk.LEFT)
        
        self.custom_dns_entry = ttk.Entry(custom_frame, width=15)
        self.custom_dns_entry.pack(side=tk.LEFT, padx=(10, 0))
        self.custom_dns_entry.insert(0, "8.8.8.8")
        
        # 操作按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 20))
        
        # 刷新按钮
        self.refresh_button = ttk.Button(
            button_frame, 
            text="刷新状态", 
            command=self.refresh_status
        )
        self.refresh_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # 应用按钮
        self.apply_button = ttk.Button(
            button_frame, 
            text="应用设置", 
            command=self.apply_settings
        )
        self.apply_button.pack(side=tk.LEFT)
        
        # 进度条
        self.progress = ttk.Progressbar(
            main_frame, 
            orient=tk.HORIZONTAL, 
            mode='indeterminate'
        )
        self.progress.pack(fill=tk.X, pady=(0, 10))
        
        # 日志框架
        log_frame = ttk.LabelFrame(main_frame, text="操作日志", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        # 日志文本框
        self.log_text = tk.Text(log_frame, height=6, width=50, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(self.log_text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.log_text.yview)
        
        # 初始化状态
        self.refresh_status()
    
    def log(self, message):
        """添加日志消息"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def is_admin(self):
        """检查是否以管理员权限运行"""
        try:
            return os.getuid() == 0
        except AttributeError:
            # Windows系统
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
    
    def get_current_dns(self):
        """获取当前DNS设置"""
        system = platform.system().lower()
        
        if system == "windows":
            try:
                # 获取所有网络适配器
                result = subprocess.run(
                    ["netsh", "interface", "show", "interface"],
                    capture_output=True,
                    text=True,
                    encoding="utf-8"
                )
                
                # 解析输出获取启用的以太网适配器
                lines = result.stdout.split('\n')
                adapter_name = None
                
                for line in lines:
                    if "已启用" in line or "Enabled" in line:
                        parts = line.split()
                        if len(parts) >= 4:
                            adapter_name = parts[3]
                            break
                
                if not adapter_name:
                    return "无法找到已启用的网络适配器"
                
                # 获取DNS设置
                result = subprocess.run(
                    ["netsh", "interface", "ip", "show", "dns", f"name=\"{adapter_name}\""],
                    capture_output=True,
                    text=True,
                    encoding="utf-8"
                )
                
                dns_output = result.stdout
                if "DHCP" in dns_output or "自动" in dns_output:
                    return "自动获取"
                else:
                    # 提取DNS服务器
                    dns_match = re.search(r"DNS 服务器.*?(\d+\.\d+\.\d+\.\d+)", dns_output)
                    if dns_match:
                        return dns_match.group(1)
                
                return "未知"
            except Exception as e:
                return f"获取DNS设置时出错: {e}"
        
        elif system == "linux":
            try:
                # 尝试从resolv.conf获取DNS
                with open("/etc/resolv.conf", "r") as f:
                    content = f.read()
                    
                # 检查是否是DHCP分配的
                if "# Generated by" in content:
                    return "自动获取"
                    
                # 提取DNS服务器
                dns_match = re.search(r"nameserver\s+(\d+\.\d+\.\d+\.\d+)", content)
                if dns_match:
                    return dns_match.group(1)
                    
                return "未知"
            except Exception as e:
                return f"获取DNS设置时出错: {e}"
        
        else:
            return f"不支持的操作系统: {system}"
    
    def set_dns_static(self, dns_server="1.1.1.1"):
        """设置静态DNS"""
        system = platform.system().lower()
        
        if system == "windows":
            try:
                # 获取所有网络适配器
                result = subprocess.run(
                    ["netsh", "interface", "show", "interface"],
                    capture_output=True,
                    text=True,
                    encoding="utf-8"
                )
                
                # 解析输出获取启用的以太网适配器
                lines = result.stdout.split('\n')
                adapter_name = None
                
                for line in lines:
                    if "已启用" in line or "Enabled" in line:
                        parts = line.split()
                        if len(parts) >= 4:
                            adapter_name = parts[3]
                            break
                
                if not adapter_name:
                    return False, "无法找到已启用的网络适配器"
                
                # 设置静态DNS
                result = subprocess.run(
                    ["netsh", "interface", "ip", "set", "dns", f"name=\"{adapter_name}\"", "static", dns_server, "primary"],
                    capture_output=True,
                    text=True,
                    encoding="utf-8"
                )
                
                if result.returncode == 0:
                    return True, f"已将DNS设置为: {dns_server}"
                else:
                    return False, f"设置DNS失败: {result.stderr}"
                    
            except Exception as e:
                return False, f"设置DNS时出错: {e}"
        
        elif system == "linux":
            try:
                # 备份原始resolv.conf
                if os.path.exists("/etc/resolv.conf"):
                    subprocess.run(["sudo", "cp", "/etc/resolv.conf", "/etc/resolv.conf.backup"], check=False)
                
                # 写入新的DNS设置
                with open("/tmp/resolv.conf", "w") as f:
                    f.write(f"nameserver {dns_server}\n")
                
                # 应用新设置
                result = subprocess.run(
                    ["sudo", "cp", "/tmp/resolv.conf", "/etc/resolv.conf"],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    return True, f"已将DNS设置为: {dns_server}"
                else:
                    return False, f"设置DNS失败: {result.stderr}"
                    
            except Exception as e:
                return False, f"设置DNS时出错: {e}"
        
        else:
            return False, f"不支持的操作系统: {system}"
    
    def set_dns_dhcp(self):
        """设置为自动获取DNS"""
        system = platform.system().lower()
        
        if system == "windows":
            try:
                # 获取所有网络适配器
                result = subprocess.run(
                    ["netsh", "interface", "show", "interface"],
                    capture_output=True,
                    text=True,
                    encoding="utf-8"
                )
                
                # 解析输出获取启用的以太网适配器
                lines = result.stdout.split('\n')
                adapter_name = None
                
                for line in lines:
                    if "已启用" in line or "Enabled" in line:
                        parts = line.split()
                        if len(parts) >= 4:
                            adapter_name = parts[3]
                            break
                
                if not adapter_name:
                    return False, "无法找到已启用的网络适配器"
                
                # 设置为自动获取DNS
                result = subprocess.run(
                    ["netsh", "interface", "ip", "set", "dns", f"name=\"{adapter_name}\"", "dhcp"],
                    capture_output=True,
                    text=True,
                    encoding="utf-8"
                )
                
                if result.returncode == 0:
                    return True, "已将DNS设置为自动获取"
                else:
                    return False, f"设置DNS失败: {result.stderr}"
                    
            except Exception as e:
                return False, f"设置DNS时出错: {e}"
        
        elif system == "linux":
            try:
                # 恢复备份或使用DHCP客户端重新获取
                if os.path.exists("/etc/resolv.conf.backup"):
                    result = subprocess.run(
                        ["sudo", "cp", "/etc/resolv.conf.backup", "/etc/resolv.conf"],
                        capture_output=True,
                        text=True
                    )
                else:
                    # 尝试使用dhclient重新获取DNS
                    result = subprocess.run(
                        ["sudo", "dhclient", "-r"],
                        capture_output=True,
                        text=True
                    )
                    
                    if result.returncode == 0:
                        result = subprocess.run(
                            ["sudo", "dhclient"],
                            capture_output=True,
                            text=True
                        )
                
                if result.returncode == 0:
                    return True, "已将DNS设置为自动获取"
                else:
                    return False, f"设置DNS失败: {result.stderr}"
                    
            except Exception as e:
                return False, f"设置DNS时出错: {e}"
        
        else:
            return False, f"不支持的操作系统: {system}"
    
    def refresh_status(self):
        """刷新DNS状态"""
        self.progress.start()
        self.status_label.config(text="正在获取DNS状态...")
        
        def update_status():
            current_dns = self.get_current_dns()
            self.status_label.config(text=f"当前DNS: {current_dns}")
            
            # 更新选项状态
            if current_dns == "自动获取":
                self.dhcp_var.set(True)
                self.custom_var.set(False)
            elif current_dns == "1.1.1.1":
                self.dhcp_var.set(False)
                self.custom_var.set(False)
            else:
                # 如果是其他DNS，设置为自定义
                self.dhcp_var.set(False)
                self.custom_var.set(True)
                self.custom_dns_entry.delete(0, tk.END)
                self.custom_dns_entry.insert(0, current_dns)
            
            self.progress.stop()
            self.log(f"状态已更新: {current_dns}")
        
        # 在新线程中执行，避免阻塞UI
        threading.Thread(target=update_status, daemon=True).start()
    
    def on_option_change(self):
        """当选项改变时的处理"""
        if self.dhcp_var.get():
            self.custom_var.set(False)
        else:
            # 选择了1.1.1.1
            self.custom_var.set(False)
    
    def on_custom_check(self):
        """当自定义选项改变时的处理"""
        if self.custom_var.get():
            self.dhcp_var.set(False)
    
    def apply_settings(self):
        """应用DNS设置"""
        self.progress.start()
        
        def apply():
            # 检查管理员权限
            if not self.is_admin() and platform.system().lower() == "windows":
                self.progress.stop()
                messagebox.showerror(
                    "权限不足", 
                    "在Windows上修改DNS设置需要管理员权限。\n请以管理员身份运行此程序。"
                )
                return
            
            success = False
            message = ""
            
            if self.custom_var.get():
                # 使用自定义DNS
                custom_dns = self.custom_dns_entry.get().strip()
                if not custom_dns:
                    self.progress.stop()
                    messagebox.showerror("错误", "请输入有效的DNS服务器地址")
                    return
                
                success, message = self.set_dns_static(custom_dns)
            elif self.dhcp_var.get():
                # 使用自动获取
                success, message = self.set_dns_dhcp()
            else:
                # 使用1.1.1.1
                success, message = self.set_dns_static("1.1.1.1")
            
            self.progress.stop()
            
            if success:
                self.log(f"操作成功: {message}")
                messagebox.showinfo("成功", message)
                # 刷新状态
                self.refresh_status()
            else:
                self.log(f"操作失败: {message}")
                messagebox.showerror("失败", message)
        
        # 在新线程中执行，避免阻塞UI
        threading.Thread(target=apply, daemon=True).start()


def main():
    """主函数"""
    # 检查管理员权限
    try:
        is_admin = os.getuid() == 0
    except AttributeError:
        # Windows系统
        import ctypes
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
    
    if not is_admin:
        if platform.system().lower() == "windows":
            # Windows系统提示以管理员身份运行
            messagebox.showerror(
                "权限不足", 
                "此程序需要管理员权限才能运行。\n\n请右键点击程序图标，选择'以管理员身份运行'。"
            )
            sys.exit(1)
        else:
            # Linux/Mac系统提示使用sudo
            messagebox.showerror(
                "权限不足", 
                "此程序需要管理员权限才能运行。\n\n请使用 sudo python dns_switcher_gui.py 命令运行。"
            )
            sys.exit(1)
    
    # 如果有管理员权限，启动应用程序
    root = tk.Tk()
    app = DnsSwitcherApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()