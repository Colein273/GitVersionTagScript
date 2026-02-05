@echo off
setlocal enabledelayedexpansion

echo [INFO] Build GD32 FMC + Version static library (ARMCC5)

REM =====================================================
REM 是否在生成 lib 后删除 version.c / version.h
REM 0 = 保留
REM 1 = 删除
REM =====================================================
set CLEAN_VERSION_SRC=1

REM =====================================================
REM bat 所在目录（Version\）
REM =====================================================
set SCRIPT_DIR=%~dp0
set SCRIPT_DIR=%SCRIPT_DIR:~0,-1%

REM =====================================================
REM 工程根目录
REM =====================================================
for %%i in ("%SCRIPT_DIR%\..") do set PROJECT_ROOT=%%~fi

REM =====================================================
REM Keil MDK 安装路径
REM =====================================================
set KEIL_PATH=E:\Keil

REM =====================================================
REM 输出库（放在 Version 目录）
REM =====================================================
set LIB_NAME=version.lib
set LIB_PATH=%SCRIPT_DIR%\%LIB_NAME%

REM =====================================================
REM ARMCC5 工具链
REM =====================================================
set CC=%KEIL_PATH%\ARM\ARMCC\bin\armcc.exe
set AR=%KEIL_PATH%\ARM\ARMCC\bin\armar.exe

REM =====================================================
REM CPU
REM =====================================================
set CPU=Cortex-M4.fp

REM =====================================================
REM obj 输出目录
REM =====================================================
set OBJ_DIR=%PROJECT_ROOT%\output

REM =====================================================
REM 工具检查
REM =====================================================
if not exist "%CC%" (
    echo [ERROR] armcc not found
    goto :eof
)

if not exist "%AR%" (
    echo [ERROR] armar not found
    goto :eof
)

REM =====================================================
REM 创建 output 目录
REM =====================================================
if not exist "%OBJ_DIR%" mkdir "%OBJ_DIR%"

REM =====================================================
REM 清理旧文件
REM =====================================================
if exist "%OBJ_DIR%\*.o" del "%OBJ_DIR%\*.o"
if exist "%LIB_PATH%" del "%LIB_PATH%"

REM =====================================================
REM 编译参数（严格对齐 Keil ARMCC5）
REM =====================================================
set CFLAGS=--c99 ^
 --cpu %CPU% ^
 -O0 ^
 --apcs=interwork ^
 --split_sections ^
 -DGD32F450 ^
 -I "%PROJECT_ROOT%\gd32Lib\Include" ^
 -I "%SCRIPT_DIR%" ^
 -c

REM =====================================================
REM 编译 gd32f4xx_fmc.c
REM =====================================================
echo [CC] gd32Lib\Source\gd32f4xx_fmc.c
"%CC%" %CFLAGS% "%PROJECT_ROOT%\gd32Lib\Source\gd32f4xx_fmc.c" ^
 -o "%OBJ_DIR%\gd32f4xx_fmc.o"
if errorlevel 1 goto :error

REM =====================================================
REM 编译 version.c
REM =====================================================
echo [CC] Version\version.c
"%CC%" %CFLAGS% "%SCRIPT_DIR%\version.c" ^
 -o "%OBJ_DIR%\version.o"
if errorlevel 1 goto :error

REM =====================================================
REM 打包静态库
REM =====================================================
echo [AR] %LIB_PATH%
"%AR%" --create "%LIB_PATH%" ^
 "%OBJ_DIR%\gd32f4xx_fmc.o" ^
 "%OBJ_DIR%\version.o"
if errorlevel 1 goto :error

REM =====================================================
REM 可选：删除 version 源文件
REM =====================================================
if "%CLEAN_VERSION_SRC%"=="1" (
    echo [INFO] Cleaning version source files...
    if exist "%SCRIPT_DIR%\version.c" del "%SCRIPT_DIR%\version.c"
    if exist "%SCRIPT_DIR%\version.h" del "%SCRIPT_DIR%\version.h"
)

echo.
echo [SUCCESS] Build finished: %LIB_PATH%
goto :eof

:error
echo.
echo [ERROR] Build failed
exit /b 1
