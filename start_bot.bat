@echo off
REM Gamebozor botini Windows kompyuterda ishga tushirish (ikki marta bosing)
cd /d %~dp0
chcp 65001 >nul
python -m pip install -q -r requirements.txt
echo Bot ishga tushmoqda... Toxtatish: Ctrl+C
python -m bot
pause
