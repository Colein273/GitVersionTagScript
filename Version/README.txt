Version实际应用文件夹结构应如下
Version/
├─ gd32Lib/
│  ├─ Include/
│  └─ Source/
│     └─ gd32f4xx_fmc.c
├─ output/
│  └─ （中间 .o 文件）
├─ build_version_lib.exe
├─ create_versionTag.exe
├─ README.txt（本文件）
├─ version.lib （核心需要产物）
└─ version_base.txt （用于修改版本标签）


部署中会出现的过度文件
├─ build/
├─ dist/
│  └─ build_version_lib.exe	（最终需要复制到Verison文件夹下）
├─ build_version_lib.py
├─ version.c   （生成，生成lib后可删去）
├─ version.h   （生成，生成lib后可删去）

--------------管理员--------------
I、
需要安装Python（需要拥有pyinstaller库）
需要在build_version_lib.py中设置设备白名单和当前设备可用keil的根目录，也可以选择是否在version.lib生成后自动删除version.c和version.h
使用py构建exe：pyinstaller -F build_version_lib.py，加载完成生成两个文件夹（build和dist）后从dist中取出即可使用
--------------用  户--------------
II、
安装tortoiseGit，打开后在设置--Hook脚本，添加钩子create_versionTag.exe
配置为：启用；Hook类型“Pre-Commit Hook”；将所有勾选项目勾选，执行命令行为Version/create_versionTag.exe
III、
在keil中
Keil5 “option for target” -- user -- build before 前勾选加入
Version/build_version_lib.exe
运行前先可以试双击运行build_version_lib.exe，观察到有Verison.lib生成后，创建一个Group用于存放Verison.lib
当使用Keil编译后可以从0x08020000，flash中读取到设备可用信息（0未该设备不可用，1为该设备可用），代码是否更改（0为上次提交后无修改，1为上次提交后已修改），和版本号
IV、
具体操作：
使用前先在version_base.txt中确定当前的版本号（提交的标签为前三位，如v1.0.7），修改完内容后，右键Git提交至master，填写完提交内容后允许执行Hook脚本
（1）若主版本号、次版本号、修订号均无修改，则不会提交新的版本标签
（2）若主版本号、次版本号、修订号均有修改，则在提交后可在版本分支图中查询到版本标签已经修改

每次提交内容后将会运行hook，此时打开version_base.txt可以观察到BUILD补丁号递增+1


