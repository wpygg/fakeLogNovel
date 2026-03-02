# FakeLogNovel

假日志生成器 - 将小说文本伪装成日志文件，摸鱼神器。

## 功能

- 将源文本按模板格式拆分成多份日志文件
- 每份输出文件混合「模板行」与「真实内容行」
- 支持自定义日志行模板
- 可视化界面操作

## 运行方式

### 方式一：直接运行 exe（推荐）

下载 `dist/FakeLogNovel.exe` 双击运行，无需 Python 环境。

### 方式二：Python 运行

```bash
python main.py
```

## 打包 exe

```bash
build.bat
```

或手动执行：

```bash
pip install pyinstaller
python -m PyInstaller --onefile --windowed --name "FakeLogNovel" main.py
```

打包后的 exe 文件位于 `dist/` 目录。

## 使用说明

1. **Name**: 输出目录名称
2. **行宽(lineLength)**: 每行最大字符数
3. **单文件最大行(lineMax)**: 单个输出文件的最大行数
4. **输出目录**: 选择生成的日志文件存放位置
5. **源文本文件**: 选择要处理的小说文本文件
6. **模板行文件**: 选择日志模板文件
7. **日志行模板**: 可自定义多段固定文字，源内容会被切分插入各段之间

点击「开始」按钮即可生成假日志文件。

## 项目结构

```
fakeLogNovel/
├── main.py        # 程序入口
├── gui.py         # GUI界面
├── fakelog.py     # 核心逻辑
├── build.bat      # 打包脚本
├── pyproject.toml # 项目配置
└── requirements.txt
```