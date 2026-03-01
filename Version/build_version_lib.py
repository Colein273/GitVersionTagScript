import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime

# 全局配置 
PROJECT_NAME = "GD32-Communication-Module"
BUILD_TYPE   = "CommModuleForGD32.uvprojx"
PRODUCT_NAME = "CommModuleForGD32"
MCU_TYPE     = "GD32F450"
PLATFORM     = "Keil5"
FLASH_BASE   = "0x08020000"

# 0 = 保留 version.c / version.h ||| 1 = 生成 lib 后删除
CLEAN_VERSION_SRC = 0
# Keil软件地址
KEIL_PATH = Path(r"E:\Keil")
# 设备白名单
ALLOW_HOSTS = {
    "LAPTOP-Q2N29D5I",
    "BuildServer",
    "YCY-Laptop",
}

# 基础配置
def get_app_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent

def run(cmd):
    subprocess.check_call(cmd)

def run_git(*args) -> str:
    try:
        out = subprocess.check_output(
            ["git", *args],
            stderr=subprocess.DEVNULL,
            universal_newlines=True
        )
        return out.strip()
    except Exception:
        return ""

def must_exist(path: Path, name: str):
    if not path.exists():
        print(f"[ERROR] {name} not found: {path}")
        sys.exit(1)

def read_key_value_file(path: Path) -> dict:
    result = {}
    if not path.exists():
        return result

    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            k, v = line.split("=", 1)
            result[k] = v
    return result

def bool_to_int(b: bool) -> int:
    return 1 if b else 0

# 生成 version.c / version.h 
def generate_version_files(script_dir: Path):
    git_hash = run_git("rev-parse", "--short", "HEAD") or "nogit"
    dirty = bool(run_git("status", "--porcelain", "--untracked-files=no"))
    base_kv = read_key_value_file(script_dir / "version_base.txt")
    major = base_kv.get("MAJOR", "0")
    minor = base_kv.get("MINOR", "0")    
    patch = base_kv.get("PATCH", "0")
    build = base_kv.get("BUILD", "0")
    git_tag_hex = (int(major) << 24) | (int(minor) << 16) | (int(patch) << 8)
    build_realtime = base_kv.get("BUILD_REALTIME", "UNKNOWN")
    build_realnum  = base_kv.get("BUILD_REALNUM", "0")

    build_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    build_host = os.environ.get("COMPUTERNAME", "UNKNOWN")
    build_user = os.environ.get("USERNAME", "UNKNOWN")
    allow_print = build_host in ALLOW_HOSTS

    # ---------- version.h ----------
    (script_dir / "version.h").write_text(
        "#ifndef __VERSION_H__\n" 
        "#define __VERSION_H__\n\n" 
        "extern void Write_Version_Info(void);\n\n" 
        "#endif\n",
        encoding="utf-8"
    )

    # ---------- version.c ----------
    with (script_dir / "version.c").open("w", encoding="utf-8") as fc:
        fc.write('#include "version.h"\n')
        fc.write('#include "gd32f4xx_fmc.h"\n\n')

        fc.write(f'const char FW_GIT_HASH[] = "{git_hash}";\n')
        fc.write(f'const uint32_t FW_GIT_TAG_HEX = 0x{git_tag_hex:08X};\n')
        fc.write(f'const uint8_t FW_DIRTY_FLAG = {bool_to_int(dirty)};\n')
        fc.write(f'const uint8_t FW_ALLOW_FLAG = {bool_to_int(allow_print)};\n\n')

        fc.write(f'const char FW_BD_REALTIME[] = "{build_realtime}";\n')
        fc.write(f'const char FW_BD_REALNUM[] = "{build_realnum}";\n')
        fc.write(f'const char FW_BUILD_TIME[] = "{build_time}";\n')
        fc.write(f'const char FW_BUILD_HOST[] = "{build_host}";\n')
        fc.write(f'const char FW_BUILD_USER[] = "{build_user}";\n\n')

        fc.write(f'const uint8_t MAJOR_VERSION = {major};\n')
        fc.write(f'const uint8_t MINOR_VERSION = {minor};\n')
        fc.write(f'const uint8_t PATCH_VERSION = {patch};\n')
        fc.write(f'const uint8_t BUILD_VERSION = {build};\n')
        fc.write(f'const uint32_t VERSION_NUM = (({major}<<24)|({minor}<<16)|({patch}<<8));\n\n')

        fc.write(f'const char FW_PROJECT_NAME[] = "{PROJECT_NAME}";\n')
        fc.write(f'const char FW_BUILD_TYPE[] = "{BUILD_TYPE}";\n')
        fc.write(f'const char FW_PRODUCT_NAME[] = "{PRODUCT_NAME}";\n')
        fc.write(f'const char FW_MCU_TYPE[] = "{MCU_TYPE}";\n')
        fc.write(f'const char FW_PLATFORM[] = "{PLATFORM}";\n\n')

        fc.write(f"#define VERSION_FLASH_BASE ((uint32_t){FLASH_BASE})\n\n")
        fc.write(
            "void Write_Version_Info(void)\n"
            "{\n"
            "    fmc_unlock();\n"
            "    fmc_sector_erase(CTL_SECTOR_NUMBER_5);\n"
            "    fmc_byte_program(VERSION_FLASH_BASE + 0x00, FW_ALLOW_FLAG);\n"
            "    fmc_byte_program(VERSION_FLASH_BASE + 0x01, FW_DIRTY_FLAG);\n"
            "    fmc_word_program(VERSION_FLASH_BASE + 0x04, FW_GIT_TAG_HEX);\n"
            "    fmc_lock();\n"
            "}\n"
        )

    print("[OK] version.c / version.h generated")

# 编译并打包静态库 
def build_static_lib(script_dir: Path):
    project_root = script_dir.parent

    armcc = KEIL_PATH / "ARM" / "ARMCC" / "bin" / "armcc.exe"
    armar = KEIL_PATH / "ARM" / "ARMCC" / "bin" / "armar.exe"

    must_exist(armcc, "armcc")
    must_exist(armar, "armar")

    obj_dir = script_dir / "output"
    obj_dir.mkdir(parents=True, exist_ok=True)

    lib_path = script_dir / "version.lib"
    lib_path.unlink(missing_ok=True)

    for obj in obj_dir.glob("*.o"):
        obj.unlink()

    cflags = [
        "--c99",
        "--cpu", "Cortex-M4.fp",
        "-O0",
        "--apcs=interwork",
        "--split_sections",
        "-DGD32F450",
        "-I", str(script_dir / "gd32Lib" / "Include"),
        "-I", str(script_dir),
        "-c",
    ]

    fmc_src = script_dir / "gd32Lib" / "Source" / "gd32f4xx_fmc.c"
    must_exist(fmc_src, "gd32f4xx_fmc.c")

    run([str(armcc), *cflags, str(fmc_src), "-o", str(obj_dir / "gd32f4xx_fmc.o")])
    run([str(armcc), *cflags, str(script_dir / "version.c"), "-o", str(obj_dir / "version.o")])

    run([
        str(armar),
        "--create",
        str(lib_path),
        str(obj_dir / "gd32f4xx_fmc.o"),
        str(obj_dir / "version.o"),
    ])

    if CLEAN_VERSION_SRC:
        (script_dir / "version.c").unlink(missing_ok=True)
        (script_dir / "version.h").unlink(missing_ok=True)

    print("[SUCCESS] Static library built:", lib_path)

# 主函数
def main():
    script_dir = get_app_dir()
    generate_version_files(script_dir)
    build_static_lib(script_dir)

if __name__ == "__main__":
    main()
