@echo off
chcp 65001 >nul
echo 正在打包 FakeLogNovel...
python -m PyInstaller --onefile --windowed --name "FakeLogNovel" main.py --clean
echo.
echo 打包完成！exe 文件位于 dist\FakeLogNovel.exe
pause