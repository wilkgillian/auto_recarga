@echo off
color 2
call C:\Users\%username%\Anaconda3\Scripts\activate.bat
cd "C:\Users\%username%\Documents\Automation\auto_recarga"
pip install termcolor
cls
python charger.py
exit