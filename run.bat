@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo === キャッシュを掃除しています ===
for /d /r %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"
echo === アプリを起動します（ブラウザが開きます） ===
streamlit run app.py
pause