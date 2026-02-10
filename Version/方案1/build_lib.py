import os
import sys
import subprocess
from pathlib import Path

# ================================
# 构建策略开关
# 0 = 保留 version.c / version.h
# 1 = 生成 lib 后删除
# ================================
CLEAN_VERSION_SRC = 0

# ================================
# Keil 安装路径
# ================================
KEIL_PATH = Path(r"E:\Keil")

def run(cmd):
    subprocess.check_call(cmd)

def must_exist(path: Path, name: str):
    if not path.exists():
        print(f"[ERROR] {name} not found: {path}")
        sys.exit(1)

# ================================
# 获取程序真实所在目录
# py 运行：__file__
# exe 运行：sys.executable
# ================================
def get_app_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    else:
        return Path(__file__).resolve().parent

def main():
    print("[INFO] Build GD32 FMC + Version static library (ARMCC5)")

    # ================================
    # Version 目录（脚本 / EXE 所在）
    # ================================
    script_dir = get_app_dir()

    # ================================
    # 工程根目录
    # Version/
    # └── ..
    # ================================
    project_root = script_dir.parent

    # ================================
    # 工具链
    # ================================
    armcc = KEIL_PATH / "ARM" / "ARMCC" / "bin" / "armcc.exe"
    armar = KEIL_PATH / "ARM" / "ARMCC" / "bin" / "armar.exe"

    must_exist(armcc, "armcc")
    must_exist(armar, "armar")

    # ================================
    # 输出路径
    # ================================
    obj_dir = project_root / "output"
    lib_path = script_dir / "version.lib"

    obj_dir.mkdir(parents=True, exist_ok=True)

    # 清理旧文件
    if lib_path.exists():
        lib_path.unlink()

    for obj in obj_dir.glob("*.o"):
        obj.unlink()

    # ================================
    # 编译参数（ARMCC5 对齐 Keil）
    # ================================
    cflags = [
        "--c99",
        "--cpu", "Cortex-M4.fp",
        "-O0",
        "--apcs=interwork",
        "--split_sections",
        "-DGD32F450",
        "-I", str(project_root / "gd32Lib" / "Include"),
        "-I", str(script_dir),
        "-c",
    ]

    # ================================
    # 编译 gd32f4xx_fmc.c
    # ================================
    fmc_src = project_root / "gd32Lib" / "Source" / "gd32f4xx_fmc.c"
    must_exist(fmc_src, "gd32f4xx_fmc.c")

    print("[CC] gd32f4xx_fmc.c")
    run([
        str(armcc),
        *cflags,
        str(fmc_src),
        "-o", str(obj_dir / "gd32f4xx_fmc.o"),
    ])

    # ================================
    # 编译 version.c
    # ================================
    version_c = script_dir / "version.c"
    must_exist(version_c, "version.c")

    print("[CC] version.c")
    run([
        str(armcc),
        *cflags,
        str(version_c),
        "-o", str(obj_dir / "version.o"),
    ])

    # ================================
    # 打包静态库
    # ================================
    print("[AR] version.lib")
    run([
        str(armar),
        "--create",
        str(lib_path),
        str(obj_dir / "gd32f4xx_fmc.o"),
        str(obj_dir / "version.o"),
    ])

    # ================================
    # 可选：删除 version 源文件
    # ================================
    if CLEAN_VERSION_SRC == 1:
        print("[INFO] Cleaning version source files")
        (script_dir / "version.c").unlink(missing_ok=True)
        (script_dir / "version.h").unlink(missing_ok=True)

    print("[SUCCESS] Build finished:", lib_path)

if __name__ == "__main__":
    main()
