# -*- coding: utf-8 -*-
"""
假日志生成器：将源文本按模板格式拆分成多份日志文件。
- 从源文件读取文本，按行宽切分
- 每份输出文件混合「模板行」与「真实内容行」
- 单文件行数有上限，超出则切到下一文件；文件名含章节/节信息
"""

import os
import shutil
from pathlib import Path

OUTPUT_PREFIX = "00_"
OUTPUT_SUFFIX = ".txt"

# 默认日志行模板（与 Java 一致），仅在没有传入 fake_parts 时使用
DEFAULT_FAKE_PARTS = [
    "10:50:01.465 [identity-thread-pool-2-8] INFO FIGHT - [加tag-1042] owner_",
    "_thread_1002002_怪物_月媚_551105296909467649 计数:1 name:死亡流程",
]


def get_temp(s: str) -> str:
    """规范化标题/临时名：去掉干扰字符，中文数字转阿拉伯数字，便于作为文件名片段。"""
    if s is None:
        return ""
    t = s
    for a, b in [
        ("?", ""), ("（", ""), ("）", ""), ("/", ""),
        ("一", "1"), ("二", "2"), ("三", "3"), ("四", "4"), ("五", "5"),
        ("六", "6"), ("七", "7"), ("八", "8"), ("九", "9"),
        ("十", ""), ("零", "0"), ("百", ""), ("千", ""), ("第", "root"),
    ]:
        t = t.replace(a, b)
    return t


def handle_contents(lines: list, line_length: int) -> list:
    """将源文本行按指定行宽切分，过长行按 line_length 截成多行。"""
    contents = []
    for line in lines:
        trim = (line or "").strip()
        if not trim:
            continue
        n = len(trim)
        for i in range(0, n, line_length):
            contents.append(trim[i : i + line_length])
    return contents


def build_log_line(content_line: str, fake_parts: list) -> str:
    """将一条内容按「假模板」分段，与固定前缀拼接成一条完整日志行。fake_parts 为多段固定字符串，内容会被切分插入各段之间。"""
    if not fake_parts:
        return content_line
    fake_count = len(fake_parts)
    length = len(content_line)
    ave_len = length // (fake_count - 1) if fake_count > 1 else length
    real_parts = {}
    last = 0
    for idx in range(1, fake_count):
        end = length if idx == fake_count - 1 else min(last + ave_len, length)
        real_parts[idx] = content_line[last:end]
        last = end
    if fake_count == 1:
        real_parts[1] = content_line
    result = []
    for idx in range(1, fake_count + 1):
        result.append(fake_parts[idx - 1])
        result.append(real_parts.get(idx, ""))
    return "".join(result)


def make_log(
    name: int,
    line_length: int,
    line_max: int,
    output_path: str,
    source_file_path: str,
    code_file_path: str,
    fake_parts: list = None,
) -> tuple:
    """
    执行假日志生成。
    output_path: 输出父目录，实际输出到 output_path/name/
    fake_parts: 日志行模板多段（每段为固定字符串），内容行会被切分插入各段之间；默认使用 DEFAULT_FAKE_PARTS。
    返回 (total_line, valid_line)。
    """
    if fake_parts is None:
        fake_parts = DEFAULT_FAKE_PARTS
    path = (output_path or ".").rstrip(os.sep) + os.sep
    out_dir = path + str(name) + os.sep

    if os.path.isdir(out_dir):
        shutil.rmtree(out_dir)
    os.makedirs(out_dir, exist_ok=True)

    with open(source_file_path, "r", encoding="utf-8") as f:
        strings = f.readlines()
    with open(code_file_path, "r", encoding="utf-8") as f:
        code_list = [line.rstrip("\n\r") for line in f.readlines()]

    contents = handle_contents(strings, line_length)
    line = 0
    part = 0
    total_line = 0
    valid_line = 0
    temp = ""

    while line < len(contents):
        i = 0
        if temp and "(" in temp:
            temp = ""
        part += 1
        temp = get_temp(temp)

        out_file = Path(out_dir) / f"{OUTPUT_PREFIX}{part}_{temp}{OUTPUT_SUFFIX}"
        with open(out_file, "w", encoding="utf-8", newline="\n") as out:
            while True:
                for code_line in code_list:
                    if line < len(contents):
                        s1 = contents[line]
                        if line + 1 < len(contents):
                            s2 = contents[line + 1]
                            if s2 is not None and len(s2) <= 3:
                                s1 = s1 + s2
                                line += 1

                        line_str = build_log_line(s1, fake_parts)
                        out.write(line_str + "\n")
                        i += 1
                        line += 1

                    if "第" in s1 and ("节" in s1 or "章" in s1):
                        if "节" in s1:
                            temp = s1[: s1.index("节")]
                        elif "章" in s1:
                            temp = s1[: s1.index("章")]
                        else:
                            temp = s1

                        if "," in s1 and "=" in s1:
                            temp = s1
                        valid_line += 1
                        total_line += 1
                        out.write(code_line + "\n")
                        total_line += 1

                if i >= line_max or line >= len(contents):
                    break

    return total_line, valid_line