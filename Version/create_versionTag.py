import tkinter as tk
from tkinter import messagebox
import subprocess
import re


# ------------------------------------------------
# 执行 git 命令
# ------------------------------------------------
def run_git(cmd):
    try:
        result = subprocess.check_output(cmd, shell=True)
        return result.decode().strip()
    except:
        return ""


# ------------------------------------------------
# 获取当前最新 tag
# ------------------------------------------------
def get_last_tag():

    tag = run_git("git describe --tags --abbrev=0")

    if tag == "":
        return "v1.0.0"

    return tag


# ------------------------------------------------
# 解析版本号
# v1.2.3 -> (1,2,3)
# ------------------------------------------------
def parse_version(tag):

    match = re.match(r"v(\d+)\.(\d+)\.(\d+)", tag)

    if match:
        return match.groups()

    return ("1", "0", "0")


# ------------------------------------------------
# 创建 Git Tag
# ------------------------------------------------
def create_git_tag(version):

    try:
        subprocess.check_call(f"git tag {version}", shell=True)
        return True
    except:
        return False


def run(cmd):
    return subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8"
    )

def tag_exists(tag):
    r = subprocess.run(
        ["git", "rev-parse", tag],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    return r.returncode == 0


def create_tag(tag):
    subprocess.run([
        "git", "tag",
        "-a", tag,
        "-m", f"Release {tag}"
    ])
# ------------------------------------------------
# GUI 提交
# ------------------------------------------------
def submit():

    major = entry_major.get()
    minor = entry_minor.get()
    patch = entry_patch.get()

    version = f"v{major}.{minor}.{patch}"
    if tag_exists(version):
        messagebox.showwarning(
            "Version Warning",
            f"该版本已有记录, 可查看: {version}\n\n"
        )
    create_tag(version)
    root.destroy()

# ------------------------------------------------
# GUI 初始化
# ------------------------------------------------
root = tk.Tk()
root.title("Create Firmware Version Tag")
root.geometry("300x200")

frame = tk.Frame(root)
frame.pack(pady=20)


# 读取最新版本
last_tag = get_last_tag()
major, minor, patch = parse_version(last_tag)


# -------- MAJOR --------
tk.Label(frame, text="主版本号 MAJOR").grid(row=0, column=0, padx=10, pady=5, sticky="e")
entry_major = tk.Entry(frame, width=6)
entry_major.insert(0, major)
entry_major.grid(row=0, column=1)


# -------- MINOR --------
tk.Label(frame, text="次版本号 MINOR").grid(row=1, column=0, padx=10, pady=5, sticky="e")
entry_minor = tk.Entry(frame, width=6)
entry_minor.insert(0, minor)
entry_minor.grid(row=1, column=1)


# -------- PATCH --------
tk.Label(frame, text="修订号 PATCH").grid(row=2, column=0, padx=10, pady=5, sticky="e")
entry_patch = tk.Entry(frame, width=6)
entry_patch.insert(0, patch)
entry_patch.grid(row=2, column=1)


# -------- BUTTON --------
tk.Button(root, text="Create Version Tag", command=submit).pack(pady=20)


root.mainloop()