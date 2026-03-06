import tkinter as tk
from tkinter import messagebox
import subprocess
import re


# ------------------------------------------------
# git 命令
# ------------------------------------------------
def run_git(cmd):
    try:
        result = subprocess.check_output(cmd, shell=True)
        return result.decode().strip()
    except:
        return ""


def get_last_tag():
    tag = run_git("git describe --tags --abbrev=0")

    if tag == "":
        return "v1.0.0"

    return tag


def parse_version(tag):
    m = re.match(r"v(\d+)\.(\d+)\.(\d+)", tag)

    if m:
        return [int(x) for x in m.groups()]

    return [1,0,0]


def tag_exists(tag):
    r = subprocess.run(
        ["git","rev-parse",tag],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    return r.returncode == 0


def create_tag(tag):

    subprocess.run([
        "git","tag",
        "-a",tag,
        "-m",f"Release {tag}"
    ])


# ------------------------------------------------
# UI状态控制
# ------------------------------------------------
def mode_changed():

    mode = version_mode.get()

    if mode == "custom":
        entry_major.config(state="normal",fg="black")
        entry_minor.config(state="normal",fg="black")
        entry_patch.config(state="normal",fg="black")
    else:
        entry_major.config(state="disabled",fg="gray")
        entry_minor.config(state="disabled",fg="gray")
        entry_patch.config(state="disabled",fg="gray")

# ------------------------------------------------
# 提交
# ------------------------------------------------
def submit():

    mode = version_mode.get()

    major = int(entry_major.get())
    minor = int(entry_minor.get())
    patch = int(entry_patch.get())

    # 只在这里计算一次
    if mode == "major":
        major += 1
        minor = 0
        patch = 0

    elif mode == "minor":
        minor += 1
        patch = 0

    elif mode == "patch":
        patch += 1

    elif mode == "none":
        pass

    elif mode == "custom":
        pass

    version = f"v{major}.{minor}.{patch}"

    if tag_exists(version):
        messagebox.showwarning(
            "Version Warning",
            f"该版本已有记录: {version}"
        )

    create_tag(version)
    messagebox.showinfo(
        "Version info",
        f"该版本新建: {version}"
    )
    root.destroy()

# ------------------------------------------------
# GUI
# ------------------------------------------------
root = tk.Tk()
root.title("Create Firmware Version Tag")
root.geometry("320x360")

frame = tk.Frame(root)
frame.pack(pady=10)


# 获取当前版本
last_tag = get_last_tag()
major,minor,patch = parse_version(last_tag)


# -----------------------
# 版本输入
# -----------------------
tk.Label(frame,text="主版本号 MAJOR").grid(row=0,column=0,padx=10,pady=5)

entry_major = tk.Entry(frame,width=6)
entry_major.grid(row=0,column=1)

tk.Label(frame,text="次版本号 MINOR").grid(row=1,column=0,padx=10,pady=5)

entry_minor = tk.Entry(frame,width=6)
entry_minor.grid(row=1,column=1)

tk.Label(frame,text="修订号  PATCH").grid(row=2,column=0,padx=10,pady=5)

entry_patch = tk.Entry(frame,width=6)
entry_patch.grid(row=2,column=1)


entry_major.insert(0,major)
entry_minor.insert(0,minor)
entry_patch.insert(0,patch)


# -----------------------
# 五选一模式
# -----------------------
version_mode = tk.StringVar(value="none")

rb_none = tk.Radiobutton(
    root,
    text="无修改 (使用当前版本)",
    variable=version_mode,
    value="none",
    command=mode_changed
)

rb_patch = tk.Radiobutton(
    root,
    text="修订号：+1",
    variable=version_mode,
    value="patch",
    command=mode_changed
)

rb_minor = tk.Radiobutton(
    root,
    text="次版本号：+1",
    variable=version_mode,
    value="minor",
    command=mode_changed
)

rb_major = tk.Radiobutton(
    root,
    text="主版本号：+1",
    variable=version_mode,
    value="major",
    command=mode_changed
)

rb_custom = tk.Radiobutton(
    root,
    text="自定义版本号",
    variable=version_mode,
    value="custom",
    command=mode_changed
)

rb_none.pack(anchor="w",padx=30)
rb_major.pack(anchor="w",padx=30)
rb_minor.pack(anchor="w",padx=30)
rb_patch.pack(anchor="w",padx=30)
rb_custom.pack(anchor="w",padx=30)

mode_changed()


# -----------------------
# 提交
# -----------------------
tk.Button(
    root,
    text="Create Version Tag",
    command=submit
).pack(pady=20)


root.mainloop()