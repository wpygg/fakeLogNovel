# -*- coding: utf-8 -*-
"""
FakeLog 可视化界面：可配置 name、行宽、单文件行数、输出目录、源文件、模板文件，点击开始执行生成。
"""

import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from fakelog import make_log, DEFAULT_FAKE_PARTS

# 默认参数（与 Java 一致）
DEFAULT_NAME = 22
DEFAULT_LINE_LENGTH = 10
DEFAULT_LINE_MAX = 3800


def _select_dir(entry: tk.Entry) -> None:
    path = filedialog.askdirectory(title="选择输出目录")
    if path:
        entry.delete(0, tk.END)
        entry.insert(0, path + os.sep)


def _select_file(entry: tk.Entry, title: str) -> None:
    path = filedialog.askopenfilename(title=title)
    if path:
        entry.delete(0, tk.END)
        entry.insert(0, path)


class FakeLogApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FakeLog 假日志生成器")
        self.geometry("620x420")
        self.resizable(True, False)

        main = ttk.Frame(self, padding=16)
        main.pack(fill=tk.BOTH, expand=True)

        # 参数行
        row0 = ttk.Frame(main)
        row0.pack(fill=tk.X, pady=(0, 8))
        ttk.Label(row0, text="Name:").pack(side=tk.LEFT, padx=(0, 4))
        self.name_var = tk.StringVar(value=str(DEFAULT_NAME))
        ttk.Entry(row0, textvariable=self.name_var, width=8).pack(side=tk.LEFT, padx=(0, 16))
        
        ttk.Label(row0, text="行宽(lineLength):").pack(side=tk.LEFT, padx=(0, 4))
        self.line_length_var = tk.StringVar(value=str(DEFAULT_LINE_LENGTH))
        ttk.Entry(row0, textvariable=self.line_length_var, width=8).pack(side=tk.LEFT, padx=(0, 16))
        
        ttk.Label(row0, text="单文件最大行(lineMax):").pack(side=tk.LEFT, padx=(0, 4))
        self.line_max_var = tk.StringVar(value=str(DEFAULT_LINE_MAX))
        ttk.Entry(row0, textvariable=self.line_max_var, width=10).pack(side=tk.LEFT)

        def row(label: str, entry_var: tk.StringVar, choose_dir: bool, tip: str = ""):
            f = ttk.Frame(main)
            f.pack(fill=tk.X, pady=4)
            ttk.Label(f, text=label, width=12).pack(side=tk.LEFT, padx=(0, 8))
            e = ttk.Entry(f, textvariable=entry_var, width=52)
            e.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
            if tip:
                e.bind("<Enter>", lambda ev: _show_tip(ev, tip))
            btn = ttk.Button(f, text="选择目录" if choose_dir else "选择文件", width=10)
            if choose_dir:
                btn.configure(command=lambda: _select_dir(e))
            else:
                btn.configure(command=lambda: _select_file(e, label))
            btn.pack(side=tk.LEFT)

        def _show_tip(ev, tip):
            pass  # 可选：Tooltip

        self.output_var = tk.StringVar(value="")
        row("输出目录:", self.output_var, True)
        
        self.source_var = tk.StringVar(value="")
        row("源文本文件:", self.source_var, False, "如 22.txt")
        
        self.template_var = tk.StringVar(value="")
        row("模板行文件:", self.template_var, False, "如 log.txt")

        # 日志行模板 PARTS：多个框，框之间为 realText1, realText2... 可增删
        # PART 含义：每个框是一段固定文字，每框一段固定文字，框之间插入 realText1, realText2...（源内容会切分填入）
        part_frame = ttk.LabelFrame(main, text="日志行模板：每框一段固定文字，框之间插入 realText1, realText2...（源内容会切分填入）")
        part_frame.pack(fill=tk.BOTH, expand=True, pady=(8, 0))
        
        self.parts_container = ttk.Frame(part_frame)
        self.parts_container.pack(fill=tk.X, padx=4, pady=4)
        
        self.part_vars = [tk.StringVar(value=DEFAULT_FAKE_PARTS[0]), tk.StringVar(value=DEFAULT_FAKE_PARTS[1])]
        self._rebuild_parts_ui()

        part_btn_f = ttk.Frame(part_frame)
        part_btn_f.pack(fill=tk.X, padx=4, pady=(0, 4))
        ttk.Button(part_btn_f, text="添加一段", command=self._add_part).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(part_btn_f, text="删除一段", command=self._remove_part).pack(side=tk.LEFT)

        # 开始按钮与状态
        btn_row = ttk.Frame(main)
        btn_row.pack(pady=16)
        
        self.start_btn = ttk.Button(btn_row, text="开始", command=self._on_start)
        self.start_btn.pack()
        
        self.status_var = tk.StringVar(value=" ")
        ttk.Label(main, textvariable=self.status_var, foreground="gray").pack()

    def _rebuild_parts_ui(self):
        for w in self.parts_container.winfo_children():
            w.destroy()
        for i, var in enumerate(self.part_vars):
            row_f = ttk.Frame(self.parts_container)
            row_f.pack(fill=tk.X, pady=2)
            ttk.Label(row_f, text=f"Part{i + 1}:", width=6).pack(side=tk.LEFT, padx=(0, 4))
            e = ttk.Entry(row_f, textvariable=var, width=72)
            e.pack(side=tk.LEFT, fill=tk.X, expand=True)
            if i < len(self.part_vars) - 1:
                ttk.Label(self.parts_container, text=f" ← realText{i + 1} ", foreground="gray").pack(anchor=tk.W)

    def _add_part(self):
        self.part_vars.append(tk.StringVar(value=""))
        self._rebuild_parts_ui()

    def _remove_part(self):
        if len(self.part_vars) <= 2:
            messagebox.showinfo("提示", "至少需要保留两段（Part1 与 Part2）。")
            return
        self.part_vars.pop()
        self._rebuild_parts_ui()

    def _on_start(self):
        try:
            name = int(self.name_var.get().strip())
        except ValueError:
            self.status_var.set("Name 请输入整数")
            messagebox.showwarning("参数错误", "Name 请输入有效整数。")
            return

        try:
            line_length = int(self.line_length_var.get().strip())
            if line_length <= 0:
                raise ValueError()
        except ValueError:
            self.status_var.set("行宽请输入正整数")
            messagebox.showwarning("参数错误", "行宽(lineLength)请输入有效正整数。")
            return

        try:
            line_max = int(self.line_max_var.get().strip())
            if line_max <= 0:
                raise ValueError()
        except ValueError:
            self.status_var.set("单文件最大行请输入正整数")
            messagebox.showwarning("参数错误", "单文件最大行(lineMax)请输入有效正整数。")
            return

        output_path = self.output_var.get().strip()
        if not output_path:
            self.status_var.set("请选择输出目录")
            messagebox.showwarning("参数错误", "请选择输出目录。")
            return
        output_path = output_path.rstrip(os.sep) + os.sep

        source_path = self.source_var.get().strip()
        if not source_path:
            self.status_var.set("请选择源文本文件")
            messagebox.showwarning("参数错误", "请选择源文本文件。")
            return
        if not os.path.isfile(source_path):
            self.status_var.set("源文本文件不存在")
            messagebox.showerror("文件错误", f"源文本文件不存在：{source_path}")
            return

        template_path = self.template_var.get().strip()
        if not template_path:
            self.status_var.set("请选择模板行文件")
            messagebox.showwarning("参数错误", "请选择模板行文件。")
            return
        if not os.path.isfile(template_path):
            self.status_var.set("模板行文件不存在")
            messagebox.showerror("文件错误", f"模板行文件不存在：{template_path}")
            return

        fake_parts = [v.get().strip() for v in self.part_vars]
        if not any(fake_parts):
            self.status_var.set("请至少输入一段日志行模板(PART)")
            messagebox.showwarning("参数错误", "请至少输入一段日志行模板(PART)，每行一段。")
            return

        self.status_var.set("正在生成...")
        self.start_btn.configure(state=tk.DISABLED)

        def run():
            try:
                out_dir = output_path + str(name) + os.sep
                total, valid = make_log(
                    name, line_length, line_max,
                    output_path, source_path, template_path,
                    fake_parts=fake_parts,
                )
                self.after(0, lambda: self._done(True, out_dir, None))
            except Exception as e:
                self.after(0, lambda: self._done(False, None, e))

        threading.Thread(target=run, daemon=True).start()

    def _done(self, ok: bool, out_dir: str, err: Exception):
        self.start_btn.configure(state=tk.NORMAL)
        if ok:
            self.status_var.set("生成完成")
            messagebox.showinfo("完成", f"假日志已生成到：{out_dir}")
        else:
            self.status_var.set("生成失败")
            msg = str(err) if err else "未知错误"
            if isinstance(err, (OSError, IOError)):
                msg = "读写文件出错：" + msg
            messagebox.showerror("错误", msg)


def main():
    app = FakeLogApp()
    app.mainloop()


if __name__ == "__main__":
    main()