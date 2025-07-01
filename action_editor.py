import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import time
import threading
from pynput import mouse, keyboard
from pynput.keyboard import Key, Listener as KeyboardListener
import pyautogui
import os
from tkinter import simpledialog
import glob
import webbrowser


class EnhancedActionEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("高级动作编辑器 v1.0")
        self.set_window_center(1400, 900)
        self.root.configure(bg='#f0f0f0')
        self.running = True  # 控制线程运行的标志

        # 自定义样式
        self.setup_styles()

        # 状态变量
        self.recording = False
        self.playing = False
        self.commands = []
        self.current_file = None
        self.start_time = 0
        self.recording_threads = {}
        self.playback_threads = {}
        self.file_playback_sequence = []
        self.playback_loop_count = 1
        self.selected_files = []
        self.active_hotkey_files = {}
        self.setting_hotkey = False

        # 初始化UI变量
        self.x_entry = None
        self.y_entry = None
        self.button_var = tk.StringVar()
        self.key_entry = None

        # 热键设置
        self.hotkeys = {
            'start_recording': 'F5',
            'stop_recording': 'F6',
            'stop_playback': 'esc'
        }

        # 文件热键映射
        self.file_hotkeys = {}
        self.hotkey_listeners = {}

        # 创建界面
        self.create_ui()
        self.setup_hotkeys()
        self.scan_json_files()
        self.bind_hover_effects()

        # 设置窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # 显示公告弹窗
        self.show_announcement()

        # 最后启动鼠标跟踪
        self.start_mouse_tracker()

    def set_window_center(self, width, height):
        """设置窗口居中显示"""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')

        # 主色调
        style.configure('.', background='#f5f5f5')
        style.configure('TFrame', background='#f5f5f5')
        style.configure('TLabel', background='#f5f5f5', font=('微软雅黑', 10))
        style.configure('TButton', font=('微软雅黑', 10), padding=6)
        style.configure('Header.TFrame', background='#3a7ebf')
        style.configure('Treeview', font=('Consolas', 10), rowheight=25, background='white')
        style.map('Treeview', background=[('selected', '#3a7ebf')])

        # 按钮样式
        style.configure('Record.TButton', foreground='white', background='#d9534f')
        style.configure('Play.TButton', foreground='white', background='#5cb85c')
        style.configure('File.TButton', foreground='white', background='#5bc0de')
        style.configure('Edit.TButton', foreground='white', background='#f0ad4e')
        style.configure('Hotkey.TButton', foreground='white', background='#6c757d')

        # 按钮悬停效果
        style.map('Record.TButton', background=[('active', '#c9302c')])
        style.map('Play.TButton', background=[('active', '#449d44')])
        style.map('File.TButton', background=[('active', '#31b0d5')])
        style.map('Edit.TButton', background=[('active', '#ec971f')])
        style.map('Hotkey.TButton', background=[('active', '#5a6268')])

    def bind_hover_effects(self):
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Button):
                widget.bind("<Enter>", lambda e: self.root.config(cursor="hand2"))
                widget.bind("<Leave>", lambda e: self.root.config(cursor=""))

    def start_mouse_tracker(self):
        def track_mouse():
            while getattr(self, 'running', True):
                try:
                    x, y = pyautogui.position()
                    if hasattr(self, 'coord_label'):
                        self.root.after(0,
                                        lambda: self.coord_label.config(text=f"鼠标坐标: ({x}, {y})") if hasattr(self,
                                                                                                                 'coord_label') else None)
                    time.sleep(0.1)
                except Exception as e:
                    if str(e) != "main thread is not in main loop":
                        print(f"鼠标跟踪错误: {e}")
                    break

        self.mouse_tracker_thread = threading.Thread(target=track_mouse, daemon=True)
        self.mouse_tracker_thread.start()

    def show_announcement(self):
        """显示居中公告弹窗"""
        announcement = tk.Toplevel(self.root)
        announcement.title("使用说明与反馈")
        announcement_width = 600
        announcement_height = 800

        # 计算居中位置
        screen_width = announcement.winfo_screenwidth()
        screen_height = announcement.winfo_screenheight()
        x = (screen_width - announcement_width) // 2
        y = (screen_height - announcement_height) // 2
        announcement.geometry(f"{announcement_width}x{announcement_height}+{x}+{y}")

        announcement.resizable(False, False)
        announcement.configure(bg='#f5f5f5')

        # 主容器
        main_frame = ttk.Frame(announcement, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 标题
        title_label = ttk.Label(main_frame, text="高级动作编辑器使用说明",
                                font=('微软雅黑', 14, 'bold'))
        title_label.pack(pady=(0, 15))

        # 内容文本
        content_text = """
        欢迎使用高级动作编辑器 v1.0！

        本项目开源且完全免费！
        
        项目链接：
        
        主要功能：
        1. 录制鼠标点击和键盘操作
        2. 保存和加载动作序列
        3. 设置热键快速触发常用动作
        4. 编辑和调整已录制的动作

        使用方法：
        1. 点击"开始录制"按钮或按F5键开始录制
        2. 点击"停止录制"按钮或按F6键停止录制
        3. 可以使用热键快速触发保存的动作

        其它功能：
        - 回放速度可以通过速度控制调整
        - 支持多文件选择和循环播放
        
        反馈：3314982394@qq.com
        
        """

        text_frame = ttk.Frame(main_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)

        text_widget = tk.Text(text_frame, wrap=tk.WORD, font=('微软雅黑', 11),
                              padx=15, pady=15, bg='white', relief=tk.FLAT)
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        text_widget.insert(tk.END, content_text)
        text_widget.config(state=tk.DISABLED)

        # 按钮区域
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=(15, 0))

        # 反馈按钮
        feedback_btn = ttk.Button(btn_frame, text="反馈问题", style='Edit.TButton',
                                  command=lambda: webbrowser.open("https://blog.math-enthusiast.top/1745580912940"))
        feedback_btn.pack(side=tk.LEFT, padx=20, ipadx=10)

        # 确定按钮
        ok_btn = ttk.Button(btn_frame, text="确定", style='File.TButton',
                            command=announcement.destroy)
        ok_btn.pack(side=tk.LEFT, padx=20, ipadx=10)

        # 使弹窗保持在最前
        announcement.transient(self.root)
        announcement.grab_set()

    def on_close(self):
        """窗口关闭时清理资源"""
        self.running = False  # 停止鼠标跟踪线程

        # 停止所有录制和播放线程
        self.stop_recording()
        self.stop_playback()

        # 停止热键监听
        if hasattr(self, 'keyboard_listener'):
            self.keyboard_listener.stop()

        for listener in self.hotkey_listeners.values():
            listener.stop()

        self.root.destroy()

    # 以下是之前的所有其他方法，保持不变
    # setup_hotkeys, disable_hotkeys, enable_hotkeys, scan_json_files, update_file_list
    # toggle_file_selection, set_hotkey_for_file, register_hotkey, create_ui
    # on_treeview_press, on_treeview_drag, update_param_fields
    # start_recording, stop_recording, start_playback, play_commands, stop_playback
    # load_file, save_file, update_treeview, on_select, add_action, delete_action, update_action

    def setup_hotkeys(self):
        # 停止所有之前的监听器
        if hasattr(self, 'keyboard_listener'):
            self.keyboard_listener.stop()

        # 创建新的全局热键监听器
        self.keyboard_listener = keyboard.GlobalHotKeys({
            '<' + self.hotkeys['start_recording'] + '>': self.start_recording,
            '<' + self.hotkeys['stop_recording'] + '>': self.stop_recording,
            '<' + self.hotkeys['stop_playback'] + '>': self.stop_playback
        })
        self.keyboard_listener.start()

    def disable_hotkeys(self):
        """禁用所有热键"""
        if hasattr(self, 'keyboard_listener'):
            self.keyboard_listener.stop()

        for listener in self.hotkey_listeners.values():
            listener.stop()

    def enable_hotkeys(self):
        """启用所有热键"""
        self.setup_hotkeys()
        for filename, hotkey in self.file_hotkeys.items():
            self.register_hotkey(filename, hotkey)

    def scan_json_files(self):
        """扫描当前目录下的JSON文件"""
        self.json_files = glob.glob("*.json")
        self.update_file_list()

    def update_file_list(self):
        """更新文件列表显示"""
        for child in self.file_list_frame.winfo_children():
            child.destroy()

        # 表头
        header_frame = ttk.Frame(self.file_list_frame)
        header_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(header_frame, text="文件名", font=('微软雅黑', 10, 'bold'), width=25).pack(side=tk.LEFT, padx=5)
        ttk.Label(header_frame, text="热键", font=('微软雅黑', 10, 'bold'), width=15).pack(side=tk.LEFT, padx=5)
        ttk.Label(header_frame, text="播放次数", font=('微软雅黑', 10, 'bold')).pack(side=tk.LEFT, padx=5)

        for i, filename in enumerate(self.json_files, 1):
            file_frame = ttk.Frame(self.file_list_frame)
            file_frame.pack(fill=tk.X, pady=2)

            # 文件名
            var = tk.BooleanVar()
            chk = ttk.Checkbutton(file_frame, variable=var,
                                  command=lambda f=filename, v=var: self.toggle_file_selection(f, v))
            chk.pack(side=tk.LEFT, padx=5)
            file_label = ttk.Label(file_frame, text=os.path.basename(filename), width=25, anchor='w')
            file_label.pack(side=tk.LEFT, padx=5)

            # 绑定双击事件
            file_label.bind("<Double-Button-1>", lambda e, f=filename: self.load_file(f))
            chk.bind("<Double-Button-1>", lambda e, f=filename: self.load_file(f))

            # 热键显示和设置按钮
            hotkey_frame = ttk.Frame(file_frame)
            hotkey_frame.pack(side=tk.LEFT, padx=5)

            hotkey = self.file_hotkeys.get(filename, "无")
            ttk.Label(hotkey_frame, text=hotkey, width=10).pack(side=tk.TOP)

            hotkey_btn = ttk.Button(hotkey_frame, text="设置热键", style='Hotkey.TButton', width=8,
                                    command=lambda f=filename: self.set_hotkey_for_file(f))
            hotkey_btn.pack(side=tk.TOP, pady=(5, 0))

            # 播放次数
            repeat_var = tk.StringVar(value="1")
            repeat_entry = ttk.Entry(file_frame, textvariable=repeat_var, width=5)
            repeat_entry.pack(side=tk.LEFT, padx=10)

        # 底部播放控制面板
        playback_control_frame = ttk.Frame(self.file_list_frame)
        playback_control_frame.pack(fill=tk.X, pady=(10, 0), ipady=5)

        self.loop_var = tk.BooleanVar(value=False)
        loop_chk = ttk.Checkbutton(playback_control_frame, text="循环播放", variable=self.loop_var)
        loop_chk.pack(side=tk.LEFT, padx=5)

        ttk.Label(playback_control_frame, text="循环次数:").pack(side=tk.LEFT, padx=5)
        self.loop_count_entry = ttk.Entry(playback_control_frame, width=5)
        self.loop_count_entry.pack(side=tk.LEFT)
        self.loop_count_entry.insert(0, "1")

    def toggle_file_selection(self, filename, var):
        """切换文件选择状态"""
        if var.get():
            if filename not in self.selected_files:
                self.selected_files.append(filename)
        else:
            if filename in self.selected_files:
                self.selected_files.remove(filename)

    def set_hotkey_for_file(self, filename):
        """为文件设置热键"""
        if self.setting_hotkey:
            return

        self.setting_hotkey = True
        self.disable_hotkeys()  # 禁用其他热键

        dialog = tk.Toplevel(self.root)
        dialog.title("设置热键")
        dialog_width = 350
        dialog_height = 250
        screen_width = dialog.winfo_screenwidth()
        screen_height = dialog.winfo_screenheight()
        x = (screen_width - dialog_width) // 2
        y = (screen_height - dialog_height) // 2
        dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        dialog.resizable(False, False)
        dialog.attributes("-topmost", True)

        # 设置对话框样式
        dialog.configure(bg='#f5f5f5')
        ttk.Label(dialog, text=f"为文件设置热键",
                  font=('微软雅黑', 12, 'bold'), background='#f5f5f5').pack(pady=(15, 10))

        ttk.Label(dialog, text=os.path.basename(filename),
                  font=('微软雅黑', 10), background='#f5f5f5').pack()

        key_var = tk.StringVar(value="请按下键盘按键...")
        key_label = ttk.Label(dialog, textvariable=key_var, font=('微软雅黑', 12, 'bold'),
                              background='#f5f5f5', foreground='#007bff')
        key_label.pack(pady=(20, 10))

        status_var = tk.StringVar()
        status_label = ttk.Label(dialog, textvariable=status_var, font=('微软雅黑', 10),
                                 background='#f5f5f5', foreground='#6c757d')
        status_label.pack(pady=5)

        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=(15, 10))

        def on_press(key):
            try:
                key_str = key.char
            except AttributeError:
                key_str = str(key).replace("Key.", "")

            key_var.set(f"已选择热键: {key_str}")
            status_var.set("点击确定保存，或按其他键更改")

            # 停止监听
            return False

        def on_confirm():
            key_str = key_var.get().replace("已选择热键: ", "")
            if key_str != "请按下键盘按键...":
                self.file_hotkeys[filename] = key_str
                self.register_hotkey(filename, key_str)
                self.update_file_list()
                status_var.set("热键设置成功!")
                dialog.after(1000, on_close)
            else:
                status_var.set("请先选择热键!")

        def on_close():
            listener.stop()
            self.setting_hotkey = False
            self.enable_hotkeys()  # 重新启用热键
            dialog.destroy()

        # 添加确定和取消按钮
        ttk.Button(btn_frame, text="确定", style='File.TButton', command=on_confirm).pack(side=tk.LEFT, padx=15)
        ttk.Button(btn_frame, text="取消", style='Record.TButton', command=on_close).pack(side=tk.LEFT, padx=15)

        # 开始监听按键
        listener = KeyboardListener(on_press=on_press)
        listener.start()

        # 对话框关闭时停止监听
        dialog.protocol("WM_DELETE_WINDOW", on_close)

    def register_hotkey(self, filename, hotkey):
        """注册文件热键"""
        # 先取消之前的监听
        if filename in self.hotkey_listeners:
            self.hotkey_listeners[filename].stop()

        # 创建新的监听
        def callback():
            if self.setting_hotkey:  # 正在设置热键时忽略
                return

            if filename in self.active_hotkey_files and self.active_hotkey_files[filename]:
                # 如果正在播放，则停止
                self.stop_playback()
                self.active_hotkey_files[filename] = False
            else:
                # 如果未播放，则开始播放
                self.load_file(filename)
                self.start_playback()
                self.active_hotkey_files[filename] = True

        try:
            listener = keyboard.GlobalHotKeys({
                f'<{hotkey}>': callback
            })
            listener.start()
            self.hotkey_listeners[filename] = listener
            return True
        except Exception as e:
            messagebox.showerror("错误", f"设置热键失败: {e}")
            return False

    def create_ui(self):
        # 顶部控制区
        header = ttk.Frame(self.root, style='Header.TFrame', padding=10)
        header.pack(fill=tk.X, ipady=5)

        # 当前文件显示
        self.current_file_label = ttk.Label(header, text="当前文件: 无", font=('微软雅黑', 10, 'bold'),
                                            background='#3a7ebf', foreground='white')
        self.current_file_label.pack(side=tk.LEFT, padx=10)

        # 控制按钮区域
        control_frame = ttk.Frame(header)
        control_frame.pack(side=tk.RIGHT)

        # 录制控制区
        record_frame = ttk.LabelFrame(control_frame, text=" 录制控制 ", padding=5)
        record_frame.pack(side=tk.LEFT, padx=5)

        ttk.Button(record_frame, text="▶ 开始录制", style='Record.TButton',
                   command=self.start_recording).pack(side=tk.LEFT, padx=3)
        ttk.Button(record_frame, text="■ 停止录制", style='Record.TButton',
                   command=self.stop_recording).pack(side=tk.LEFT, padx=3)

        # 文件控制区
        file_frame = ttk.LabelFrame(control_frame, text=" 文件操作 ", padding=5)
        file_frame.pack(side=tk.LEFT, padx=5)

        ttk.Button(file_frame, text="📂 加载", style='File.TButton',
                   command=self.load_file).pack(side=tk.LEFT, padx=3)
        ttk.Button(file_frame, text="💾 保存", style='File.TButton',
                   command=self.save_file).pack(side=tk.LEFT, padx=3)
        ttk.Button(file_frame, text="🔄 刷新", style='File.TButton',
                   command=self.scan_json_files).pack(side=tk.LEFT, padx=3)

        # 回放控制区
        play_frame = ttk.LabelFrame(control_frame, text=" 回放控制 ", padding=5)
        play_frame.pack(side=tk.LEFT, padx=5)

        ttk.Button(play_frame, text="▶ 开始", style='Play.TButton',
                   command=self.start_playback).pack(side=tk.LEFT, padx=3)
        ttk.Button(play_frame, text="■ 停止", style='Play.TButton',
                   command=self.stop_playback).pack(side=tk.LEFT, padx=3)

        # 速度控制
        speed_frame = ttk.LabelFrame(control_frame, text=" 速度 ", padding=5)
        speed_frame.pack(side=tk.LEFT, padx=5)

        self.speed_var = tk.DoubleVar(value=1.0)
        ttk.Entry(speed_frame, textvariable=self.speed_var, width=3,
                  font=('微软雅黑', 10)).pack(side=tk.LEFT)
        ttk.Label(speed_frame, text="x").pack(side=tk.LEFT)

        # 主内容区
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 左侧文件列表 - 增加宽度
        file_list_frame = ttk.LabelFrame(main_frame, text=" 文件列表 ", padding=10, width=350)
        file_list_frame.pack(side=tk.LEFT, fill=tk.BOTH, ipadx=5)

        # 文件列表滚动区域
        canvas = tk.Canvas(file_list_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(file_list_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.file_list_frame = scrollable_frame

        # 中间动作列表
        list_frame = ttk.LabelFrame(main_frame, text=" 动作序列 ", padding=10)
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 添加总时间显示
        self.total_time_label = ttk.Label(list_frame, text="总时间: 0.000秒",
                                          font=('微软雅黑', 10, 'bold'))
        self.total_time_label.pack(fill=tk.X, pady=5)

        self.tree = ttk.Treeview(list_frame, columns=("type", "params", "interval"),
                                 show="headings", selectmode='extended')
        self.tree.heading("type", text="动作类型", anchor='center')
        self.tree.heading("params", text="参数", anchor='center')
        self.tree.heading("interval", text="间隔时间(秒)", anchor='center')

        self.tree.column("type", width=120, anchor='center')
        self.tree.column("params", width=250, anchor='center')
        self.tree.column("interval", width=150, anchor='center')

        scroll_y = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll_y.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        # 绑定鼠标拖动选择
        self.tree.bind('<ButtonPress-1>', self.on_treeview_press)
        self.tree.bind('<B1-Motion>', self.on_treeview_drag)

        # 右侧编辑区
        edit_frame = ttk.LabelFrame(main_frame, text=" 动作编辑 ", padding=15, width=300)
        edit_frame.pack(side=tk.RIGHT, fill=tk.Y)

        # 动作类型
        type_frame = ttk.Frame(edit_frame)
        type_frame.pack(fill=tk.X, pady=5)
        ttk.Label(type_frame, text="动作类型:").pack(side=tk.LEFT)
        self.action_type = ttk.Combobox(type_frame, values=["click", "press", "release"],
                                        state="readonly", width=15, font=('微软雅黑', 10))
        self.action_type.pack(side=tk.RIGHT)
        self.action_type.bind("<<ComboboxSelected>>", self.update_param_fields)

        # 参数输入区 (动态变化)
        self.param_frame = ttk.Frame(edit_frame)
        self.param_frame.pack(fill=tk.X, pady=5)
        self.update_param_fields()  # 初始化参数字段

        # 间隔时间控制
        interval_frame = ttk.LabelFrame(edit_frame, text=" 间隔时间 ", padding=10)
        interval_frame.pack(fill=tk.X, pady=10)

        ttk.Label(interval_frame, text="间隔时间(秒):").pack()
        self.interval_entry = ttk.Entry(interval_frame, font=('微软雅黑', 10))
        self.interval_entry.pack(fill=tk.X, pady=5)

        # 操作按钮
        btn_frame = ttk.Frame(edit_frame)
        btn_frame.pack(fill=tk.X, pady=10)

        ttk.Button(btn_frame, text="➕ 添加动作", style='Edit.TButton',
                   command=self.add_action).pack(side=tk.TOP, fill=tk.X, pady=5)
        ttk.Button(btn_frame, text="✏️ 更新动作", style='Edit.TButton',
                   command=self.update_action).pack(side=tk.TOP, fill=tk.X, pady=5)
        ttk.Button(btn_frame, text="🗑️ 删除选中", style='Edit.TButton',
                   command=self.delete_action).pack(side=tk.TOP, fill=tk.X, pady=5)

        # 坐标显示器
        self.coord_label = ttk.Label(self.root, text="鼠标坐标: (0, 0)",
                                     relief=tk.SUNKEN, padding=10,
                                     font=('微软雅黑', 10, 'bold'))
        self.coord_label.pack(fill=tk.X, padx=10, pady=5)

        # 绑定事件
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    def on_treeview_press(self, event):
        """处理树形视图鼠标按下事件"""
        self.drag_start = self.tree.identify_row(event.y)
        if self.drag_start:
            self.tree.selection_set(self.drag_start)

    def on_treeview_drag(self, event):
        """处理树形视图鼠标拖动选择"""
        item = self.tree.identify_row(event.y)
        if item and hasattr(self, 'drag_start'):
            start_idx = self.tree.index(self.drag_start)
            end_idx = self.tree.index(item)

            # 清除当前选择
            self.tree.selection_remove(self.tree.selection())

            # 选择范围内的所有项目
            if start_idx <= end_idx:
                for i in range(start_idx, end_idx + 1):
                    self.tree.selection_add(self.tree.get_children()[i])
            else:
                for i in range(end_idx, start_idx + 1):
                    self.tree.selection_add(self.tree.get_children()[i])

    def update_param_fields(self, event=None):
        """根据动作类型更新参数输入字段"""
        for widget in self.param_frame.winfo_children():
            widget.destroy()

        action = self.action_type.get()

        if action == "click":
            # 鼠标点击参数
            ttk.Label(self.param_frame, text="X坐标:").grid(row=0, column=0, sticky='e', padx=5)
            self.x_entry = ttk.Entry(self.param_frame, width=10, font=('微软雅黑', 10))
            self.x_entry.grid(row=0, column=1, padx=5, pady=5)

            ttk.Label(self.param_frame, text="Y坐标:").grid(row=1, column=0, sticky='e', padx=5)
            self.y_entry = ttk.Entry(self.param_frame, width=10, font=('微软雅黑', 10))
            self.y_entry.grid(row=1, column=1, padx=5, pady=5)

            ttk.Label(self.param_frame, text="按钮:").grid(row=2, column=0, sticky='e', padx=5)
            self.button_var = tk.StringVar(value="left")
            btn_frame = ttk.Frame(self.param_frame)
            btn_frame.grid(row=2, column=1, columnspan=2, sticky='w')
            ttk.Radiobutton(btn_frame, text="左键", variable=self.button_var,
                            value="left").pack(side=tk.LEFT)
            ttk.Radiobutton(btn_frame, text="右键", variable=self.button_var,
                            value="right").pack(side=tk.LEFT)
        else:
            # 键盘按键参数
            ttk.Label(self.param_frame, text="按键:").grid(row=0, column=0, sticky='e', padx=5)
            self.key_entry = ttk.Entry(self.param_frame, font=('微软雅黑', 10))
            self.key_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

    def start_recording(self):
        if self.playing:
            messagebox.showwarning("警告", "请先停止回放")
            return

        # 询问保存文件名
        filename = simpledialog.askstring("保存录制", "请输入保存文件名(不带扩展名):",
                                          parent=self.root)
        if filename is None:  # 用户取消
            return

        self.current_file = filename + ".json" if filename else "commands.json"
        self.current_file_label.config(text=f"当前文件: {self.current_file}")

        # 最小化窗口
        self.root.iconify()

        self.recording = True
        self.commands = []
        self.start_time = time.time()
        self.last_record_time = self.start_time

        # 使用线程ID作为键
        thread_id = threading.get_ident()

        def on_click(x, y, button, pressed):
            if pressed and self.recording and thread_id in self.recording_threads:
                current_time = time.time()
                interval = current_time - self.last_record_time
                self.last_record_time = current_time

                self.commands.append((
                    "click",
                    [x, y, str(button)],
                    interval  # 只记录间隔时间
                ))
                self.update_treeview()

        def on_press(key):
            if not self.recording or thread_id not in self.recording_threads:
                return False

            try:
                key_str = key.char
            except:
                key_str = str(key).replace("Key.", "")

            current_time = time.time()
            interval = current_time - self.last_record_time
            self.last_record_time = current_time

            self.commands.append((
                "press",
                [key_str],
                interval  # 只记录间隔时间
            ))
            self.update_treeview()

            if key == keyboard.Key.esc:
                self.stop_recording()
                return False

        def on_release(key):
            if not self.recording or thread_id not in self.recording_threads:
                return False

            try:
                key_str = key.char
            except:
                key_str = str(key).replace("Key.", "")

            current_time = time.time()
            interval = current_time - self.last_record_time
            self.last_record_time = current_time

            self.commands.append((
                "release",
                [key_str],
                interval  # 只记录间隔时间
            ))
            self.update_treeview()

        # 创建监听器
        mouse_listener = mouse.Listener(on_click=on_click)
        keyboard_listener = keyboard.Listener(on_press=on_press, on_release=on_release)

        # 启动监听器
        mouse_listener.start()
        keyboard_listener.start()

        # 保存监听器引用
        self.recording_threads[thread_id] = {
            'mouse': mouse_listener,
            'keyboard': keyboard_listener
        }

        # 显示非模态提示
        self.show_tooltip("录制已开始", "按ESC键结束录制")

    def show_tooltip(self, title, message):
        """显示自动消失的提示"""
        top = tk.Toplevel(self.root)
        top.title(title)
        top.geometry("300x80")
        top.attributes("-topmost", True)

        label = ttk.Label(top, text=message)
        label.pack(pady=20)

        # 3秒后自动关闭
        top.after(3000, top.destroy)

    def stop_recording(self):
        self.recording = False
        thread_id = threading.get_ident()

        if thread_id in self.recording_threads:
            listeners = self.recording_threads[thread_id]
            listeners['mouse'].stop()
            listeners['keyboard'].stop()
            del self.recording_threads[thread_id]

        # 恢复窗口
        self.root.deiconify()

        self.show_tooltip("录制完成", f"共记录{len(self.commands)}个动作")
        self.scan_json_files()  # 刷新文件列表

    def start_playback(self):
        if not self.commands and not self.selected_files:
            messagebox.showwarning("警告", "没有可回放的动作或未选择文件")
            return

        if self.recording:
            messagebox.showwarning("警告", "请先停止录制")
            return

        self.playing = True
        speed = self.speed_var.get()

        try:
            self.playback_loop_count = int(self.loop_count_entry.get())
            if self.playback_loop_count <= 0:
                self.playback_loop_count = 1
        except:
            self.playback_loop_count = 1

        # 使用线程ID作为键
        thread_id = threading.get_ident()

        def playback():
            count = 0
            while (
                    count < self.playback_loop_count or self.loop_var.get()) and self.playing and thread_id in self.playback_threads:
                if self.selected_files:
                    # 播放选中的文件序列
                    for filename in self.selected_files:
                        if not self.playing or thread_id not in self.playback_threads:
                            break

                        try:
                            with open(filename, 'r') as f:
                                data = json.load(f)
                                commands = data.get('commands', [])

                                # 获取播放次数
                                repeat = 1  # 默认播放1次
                                # 这里可以添加从UI获取播放次数的逻辑

                                for _ in range(repeat):
                                    if not self.playing or thread_id not in self.playback_threads:
                                        break

                                    self.play_commands(commands, speed, thread_id)
                        except Exception as e:
                            print(f"加载文件 {filename} 失败: {e}")
                else:
                    # 播放当前命令
                    self.play_commands(self.commands, speed, thread_id)

                count += 1

            if thread_id in self.playback_threads:
                del self.playback_threads[thread_id]
                self.playing = False if not self.playback_threads else True
                # 重置热键文件状态
                for filename in self.active_hotkey_files:
                    self.active_hotkey_files[filename] = False
                self.root.after(0, lambda: self.show_tooltip("回放完成", f"共回放{count}次"))

        # 保存线程引用
        self.playback_threads[thread_id] = True
        threading.Thread(target=playback, daemon=True).start()

    def play_commands(self, commands, speed, thread_id):
        """播放命令序列"""
        mouse_ctrl = mouse.Controller()
        keyboard_ctrl = keyboard.Controller()

        for command in commands:
            if not self.playing or thread_id not in self.playback_threads:
                break

            action, params, interval = command

            # 等待间隔时间
            time.sleep(interval / speed)

            try:
                if action == "click":
                    x, y, button = params
                    mouse_ctrl.position = (x, y)
                    time.sleep(0.05)
                    if "left" in button.lower():
                        mouse_ctrl.click(mouse.Button.left)
                    else:
                        mouse_ctrl.click(mouse.Button.right)

                elif action == "press":
                    key = params[0]
                    if hasattr(keyboard.Key, key):
                        keyboard_ctrl.press(getattr(keyboard.Key, key))
                    else:
                        keyboard_ctrl.press(key)

                elif action == "release":
                    key = params[0]
                    if hasattr(keyboard.Key, key):
                        keyboard_ctrl.release(getattr(keyboard.Key, key))
                    else:
                        keyboard_ctrl.release(key)

            except Exception as e:
                print(f"回放错误: {e}")

    def stop_playback(self):
        """停止所有回放"""
        # 停止所有播放线程
        for thread_id in list(self.playback_threads.keys()):
            del self.playback_threads[thread_id]

        self.playing = False

        # 重置热键文件状态
        for filename in self.active_hotkey_files:
            self.active_hotkey_files[filename] = False

        self.show_tooltip("回放停止", "已停止所有回放")

    def load_file(self, filename=None):
        if not filename:
            filename = filedialog.askopenfilename(filetypes=[("JSON文件", "*.json")])

        if filename:
            try:
                with open(filename, 'r') as f:
                    data = json.load(f)
                    self.commands = data.get('commands', [])
                    self.current_file = filename
                    self.current_file_label.config(text=f"当前文件: {os.path.basename(filename)}")
                    self.update_treeview()
            except Exception as e:
                messagebox.showerror("错误", f"加载文件失败: {e}")

    def save_file(self):
        if not self.commands:
            messagebox.showwarning("警告", "没有可保存的动作")
            return

        if not self.current_file:
            self.current_file = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON文件", "*.json")],
                initialfile="commands.json"
            )

        if self.current_file:
            try:
                with open(self.current_file, 'w') as f:
                    json.dump({
                        "metadata": {
                            "screen_resolution": pyautogui.size(),
                            "record_time": time.strftime("%Y-%m-%d %H:%M:%S")
                        },
                        "commands": self.commands
                    }, f, indent=2)
                messagebox.showinfo("提示", f"保存成功到 {self.current_file}")
                self.current_file_label.config(text=f"当前文件: {os.path.basename(self.current_file)}")
                self.scan_json_files()  # 刷新文件列表
            except Exception as e:
                messagebox.showerror("错误", f"保存失败: {e}")

    def update_treeview(self):
        self.tree.delete(*self.tree.get_children())
        total_time = 0.0

        for cmd in self.commands:
            action, params, interval = cmd
            total_time += interval
            self.tree.insert("", "end", values=(
                action,
                str(params),
                f"{interval:.3f}"
            ))

        # 更新总时间显示
        self.total_time_label.config(text=f"总时间: {total_time:.3f}秒")

    def on_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return

        item = self.tree.item(selected[0])
        values = item['values']
        self.action_type.set(values[0])
        self.update_param_fields()

        # 更新参数字段
        if values[0] == "click":
            if self.x_entry and self.y_entry:
                try:
                    params = eval(values[1])
                    self.x_entry.delete(0, tk.END)
                    self.x_entry.insert(0, params[0])
                    self.y_entry.delete(0, tk.END)
                    self.y_entry.insert(0, params[1])
                    self.button_var.set("left" if "left" in str(params[2]).lower() else "right")
                except:
                    pass
        else:
            if self.key_entry:
                try:
                    params = eval(values[1])
                    self.key_entry.delete(0, tk.END)
                    self.key_entry.insert(0, params[0])
                except:
                    pass

        # 更新间隔时间
        if self.interval_entry:
            self.interval_entry.delete(0, tk.END)
            self.interval_entry.insert(0, values[2])

    def add_action(self):
        try:
            action = self.action_type.get()

            if action == "click":
                x = int(self.x_entry.get())
                y = int(self.y_entry.get())
                button = f"Button.{self.button_var.get()}"
                params = [x, y, button]
            else:
                key = self.key_entry.get()
                params = [key]

            interval = float(self.interval_entry.get())

            self.commands.append((action, params, interval))
            self.update_treeview()
        except Exception as e:
            messagebox.showerror("错误", f"添加动作失败: {e}")

    def delete_action(self):
        selected = self.tree.selection()
        if selected:
            indices = [self.tree.index(item) for item in selected]
            # 从大到小删除避免索引变化
            for i in sorted(indices, reverse=True):
                del self.commands[i]
            self.update_treeview()

    def update_action(self):
        selected = self.tree.selection()
        if selected:
            try:
                index = self.tree.index(selected[0])
                action = self.action_type.get()

                if action == "click":
                    x = int(self.x_entry.get())
                    y = int(self.y_entry.get())
                    button = f"Button.{self.button_var.get()}"
                    params = [x, y, button]
                else:
                    key = self.key_entry.get()
                    params = [key]

                interval = float(self.interval_entry.get())

                self.commands[index] = (action, params, interval)
                self.update_treeview()
            except Exception as e:
                messagebox.showerror("错误", f"更新动作失败: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = EnhancedActionEditor(root)
    root.mainloop()