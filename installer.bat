@echo off
cls
:menu
cls
color 2
echo Usuario Logado:%username%                            Computador:%computername%
date /t  

echo  __________________________
echo     ESCOLHA UM APLICATIVO     
echo  1. INSTALAR - ANACONDA3           
echo  2. EXECUTAR - AUTO RECARGA
echo  3. SAIR               
echo __________________________ 
               
set /p opcao= Escolha uma opcao:
echo _______________________
if %opcao% equ 1 goto opcao1
if %opcao% equ 2 goto opcao2
if %opcao% equ 3 goto opcao3
if %opcao% GEQ 4 goto opcao4


:opcao1
cls
if exist "C:\Users\%username%\Downloads\Anaconda3-2022.05-Windows-x86_64.exe" (
start C:\Users\%username%\Downloads\Anaconda3-2022.05-Windows-x86_64.exe
pause
goto menu
) else (
bitsadmin /transfer AcessoRemoto /priority normal https://repo.anaconda.com/archive/Anaconda3-2022.10-Windows-x86_64.exe C:\Users\%username%\Downloads\Anaconda3.exe
pause
start C:\Users\%username%\Downloads\Anaconda3.exe
call C:\Users\%username%\Anaconda3\Scripts\activate.bat
cd "C:\Users\%username%\Documents\Automation\auto_recarga"
pip install -r requirements.txt
pause
goto menu
)

:opcao2
cls
start C:\Users\wilk.silva\Documents\Automation\auto_recarga\executor.bat
pause
goto menu


:opcao3
exit

:op4
cls
echo -----------------------------------
echo Opcao invalida! Escolha outra opcao
echo -----------------------------------
pause
goto menu