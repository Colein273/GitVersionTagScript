0、
需要配置Keil的地址，设备的白名单
需要安装Python
py构建exe
pyinstaller -F build_lib.py
pyinstaller -F gen_version.py
再从dist中取出即可使用
1、
将该Version文件夹移至工程根目录下，一定需要包含“gd32Lib”
2、
Keil5 “option for target” -- user -- build before 前勾选加入
Version/gen_version.exe
Version/build_lib.exe

pyinstaller -F build_lib.py
pyinstaller -F gen_version.py
pyinstaller -F create_versionTag.py

"D:\Program Files\Git\bin\bash.exe" Version/bump_version.sh








