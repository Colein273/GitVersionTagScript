#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import sys
from pathlib import Path
from datetime import datetime

# ===============================
# UTF-8 输出（防止 GBK 炸）
# ===============================
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

# ===============================
# 路径策略（与 build_lib 完全一致）
# ===============================
REPO_ROOT = Path.cwd()
VERSION_FILE = REPO_ROOT / "Version" / "version_base.txt"

TAG_PREFIX = "v"

# ===============================
# 工具函数
# ===============================
def run(cmd, check=True):
    return subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        check=check
    )

def die(msg):
    print(f"[ERROR] {msg}")
    sys.exit(1)

def info(msg):
    print(f"[INFO] {msg}")

# ===============================
# version_base.txt 解析
# ===============================
def read_version_file(path: Path):
    kv = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            k, v = line.split("=", 1)
            kv[k.strip()] = v.strip()
    return kv

def write_version_file(path: Path, kv: dict):
    content = (
        f"MAJOR={kv['MAJOR']}\n"
        f"MINOR={kv['MINOR']}\n"
        f"PATCH={kv['PATCH']}\n"
        f"BUILD={kv['BUILD']}\n"
        f"BUILD_REALTIME={kv['BUILD_REALTIME']}\n"
        f"BUILD_REALNUM={kv['BUILD_REALNUM']}\n"
    )
    path.write_text(content, encoding="utf-8")

# ===============================
# 主逻辑
# ===============================
def main():

    # ---------- git 检查 ----------
    try:
        run(["git", "--version"])
    except Exception:
        die("git not found")

    if not VERSION_FILE.exists():
        die(f"{VERSION_FILE} not found")

    # ---------- 读取版本 ----------
    kv = read_version_file(VERSION_FILE)
    for k in ("MAJOR", "MINOR", "PATCH", "BUILD"):
        if k not in kv:
            die("version_base.txt format error")

    major = kv["MAJOR"]
    minor = kv["MINOR"]
    patch = kv["PATCH"]
    build = int(kv["BUILD"]) + 1

    base_tag = f"{TAG_PREFIX}{major}.{minor}.{patch}"
    build_tag = f"{base_tag}.{build}"

    kv["BUILD"] = str(build)
    kv["BUILD_REALTIME"] = datetime.now().strftime("%Y%m%d%H%M%S")
    kv["BUILD_REALNUM"] = build_tag

    write_version_file(VERSION_FILE, kv)
    run(["git", "add", str(VERSION_FILE)])

    info(f"version_base.txt updated → BUILD={build}")

    # ---------- 方案一：tag 只创建一次 ----------
    tag_exists = run(
        ["git", "rev-parse", base_tag],
        check=False
    ).returncode == 0

    if tag_exists:
        info(f"tag {base_tag} already exists, skip")
    else:
        run([
            "git", "tag", "-a",
            base_tag,
            "-m", f"Release {build_tag}"
        ])
        info(f"tag created: {base_tag}")

    info("pre-commit hook finished")

# ===============================
if __name__ == "__main__":
    main()
