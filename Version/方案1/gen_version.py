import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime

# ========================
# 工具函数
# ========================

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

def get_app_dir() -> Path:
    """
    py运行：__file__
    exe运行：sys.executable
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent

# ========================
# 主程序
# ========================

def main():
    # ---------- 定位自身目录 ----------
    script_dir = get_app_dir()

    # ---------- 工程固有信息 ----------
    project_name = "GD32-Communication-Module"
    build_type   = "CommModuleForGD32.uvprojx"
    product_name = "CommModuleForGD32"
    mcu_type     = "GD32F450"
    platform     = "Keil5"

    # ---------- Git 信息 ----------
    git_tag = run_git("tag", "--list", "v*", "--sort=-v:refname")
    if not git_tag:
        git_tag = "v0.0.0"
    else:
        git_tag = git_tag.splitlines()[0]

    git_hash = run_git("rev-parse", "--short", "HEAD") or "nogit"
    dirty = bool(run_git("status", "--porcelain", "--untracked-files=no"))

    # ---------- 解析 vX.Y.Z ----------
    tag_clean = git_tag.lstrip("v")
    parts = tag_clean.split(".")
    major = int(parts[0]) if len(parts) > 0 and parts[0].isdigit() else 0
    minor = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
    patch = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 0

    git_tag_hex = (major << 24) | (minor << 16) | (patch << 8)

    # ---------- version_base.txt ----------
    base_file = script_dir / "version_base.txt"
    base_kv = read_key_value_file(base_file)

    build_realtime = base_kv.get("BUILD_REALTIME", "UNKNOWN")
    build_realnum  = base_kv.get("BUILD_REALNUM", "0")

    # ---------- 构建时间 / 主机 ----------
    build_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    build_host = os.environ.get("COMPUTERNAME", "UNKNOWN")
    build_user = os.environ.get("USERNAME", "UNKNOWN")

    # ---------- 设备白名单 ----------
    allow_hosts = {
        "LAPTOP-Q2N29D5I",
        "BuildServer",
        "YCY-Laptop",
    }
    allow_print = build_host in allow_hosts

    # ========================
    # 输出 version.h
    # ========================
    version_h = script_dir / "version.h"
    with version_h.open("w", encoding="utf-8") as fh:
        fh.write(
            "#ifndef __VERSION_H__\n"
            "#define __VERSION_H__\n\n"
            "extern void Write_Version_Info(void);\n\n"
            "#endif\n"
        )

    # ========================
    # 输出 version.c
    # ========================
    version_c = script_dir / "version.c"
    with version_c.open("w", encoding="utf-8") as fc:
        fc.write('#include "version.h"\n')
        fc.write('#include "gd32f4xx_fmc.h"\n\n')

        fc.write(f'#define FW_GIT_HASH      "{git_hash}"\n')
        fc.write(f'#define FW_GIT_TAG       "{git_tag}"\n')
        fc.write(f'#define FW_GIT_TAG_HEX   0x{git_tag_hex:08X}\n')
        fc.write("// 代码是否修改标志位:0为代码无修改,1为代码有修改\n")
        fc.write(f'#define FW_DIRTY_FLAG    {bool_to_int(dirty)}\n')
        fc.write("// 设备是否可用标志位:0为设备不可用,1为设备可用\n")
        fc.write(f'#define FW_ALLOW_FLAG    {bool_to_int(allow_print)}\n\n')

        fc.write("// 有效构建时间(上次提交时间码)\n")
        fc.write(f'#define FW_BD_REALTIME  "{build_realtime}"\n')
        fc.write("// 有效构建版本(上次提交版本号)\n")
        fc.write(f'#define FW_BD_REALNUM   "{build_realnum}"\n')
        fc.write(f'#define FW_BUILD_TIME  "{build_time}"\n')
        fc.write(f'#define FW_BUILD_HOST  "{build_host}"\n')
        fc.write(f'#define FW_BUILD_USER  "{build_user}"\n\n')

        fc.write(f'#define MAJOR_VERSION   {major}\n')
        fc.write(f'#define MINOR_VERSION   {minor}\n')
        fc.write(f'#define PATCH_VERSION   {patch}\n')
        fc.write(f'#define VERSION_NUM     (({major}<<24)|({minor}<<16)|({patch}<<8))\n\n')

        fc.write(f'#define FW_PROJECT_NAME "{project_name}"\n')
        fc.write(f'#define FW_BUILD_TYPE   "{build_type}"\n')
        fc.write(f'#define FW_PRODUCT_NAME "{product_name}"\n')
        fc.write(f'#define FW_MCU_TYPE     "{mcu_type}"\n')
        fc.write(f'#define FW_PLATFORM     "{platform}"\n\n')

        fc.write("#define VERSION_FLASH_BASE ((uint32_t)0x08020000)\n\n")

        fc.write("void Write_Version_Info(void)\n{\n")
        fc.write("    fmc_unlock();\n")
        fc.write("    fmc_sector_erase(CTL_SECTOR_NUMBER_5);\n")
        fc.write("    fmc_byte_program(VERSION_FLASH_BASE + 0x00, FW_ALLOW_FLAG);\n")
        fc.write("    fmc_byte_program(VERSION_FLASH_BASE + 0x01, FW_DIRTY_FLAG);\n")
        fc.write("    fmc_word_program(VERSION_FLASH_BASE + 0x04, FW_GIT_TAG_HEX);\n")
        fc.write("    fmc_lock();\n")
        fc.write("}\n")

    print("[SUCCESS] version.c / version.h generated")

if __name__ == "__main__":
    main()
