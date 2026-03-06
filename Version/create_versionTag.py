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
# 自动版本计算
# ------------------------------------------------
def calc_next_version():

    if custom_var.get():
        return

    major = int(entry_major.get())
    minor = int(entry_minor.get())
    patch = int(entry_patch.get())

    mode = version_mode.get()

    if mode == "major":
        major += 1
        minor = 0
        patch = 0

    elif mode == "minor":
        minor += 1
        patch = 0

    elif mode == "patch":
        patch += 1

    set_version(major,minor,patch)


def set_version(a,b,c):

    entry_major.config(state="normal")
    entry_minor.config(state="normal")
    entry_patch.config(state="normal")

    entry_major.delete(0,tk.END)
    entry_minor.delete(0,tk.END)
    entry_patch.delete(0,tk.END)

    entry_major.insert(0,a)
    entry_minor.insert(0,b)
    entry_patch.insert(0,c)

    if not custom_var.get():
        entry_major.config(state="disabled")
        entry_minor.config(state="disabled")
        entry_patch.config(state="disabled")


# ------------------------------------------------
# 自定义开关
# ------------------------------------------------
def toggle_custom():

    if custom_var.get():

        entry_major.config(state="normal",fg="black")
        entry_minor.config(state="normal",fg="black")
        entry_patch.config(state="normal",fg="black")

        rb_major.config(state="disabled")
        rb_minor.config(state="disabled")
        rb_patch.config(state="disabled")

    else:

        entry_major.config(state="disabled",fg="gray")
        entry_minor.config(state="disabled",fg="gray")
        entry_patch.config(state="disabled",fg="gray")

        rb_major.config(state="normal")
        rb_minor.config(state="normal")
        rb_patch.config(state="normal")


# ------------------------------------------------
# 提交
# ------------------------------------------------
def submit():

    major = entry_major.get()
    minor = entry_minor.get()
    patch = entry_patch.get()

    version = f"v{major}.{minor}.{patch}"

    if tag_exists(version):

        messagebox.showwarning(
            "Version Warning",
            f"该版本已有记录: {version}"
        )

    create_tag(version)

    root.destroy()


# ------------------------------------------------
# GUI
# ------------------------------------------------
root = tk.Tk()
root.title("Create Firmware Version Tag")
root.geometry("320x240")

frame = tk.Frame(root)
frame.pack(pady=10)

# 获取当前版本
last_tag = get_last_tag()
major,minor,patch = parse_version(last_tag)

# 自定义开关
custom_var = tk.BooleanVar()

tk.Checkbutton(
    root,
    text="自定义版本号",
    variable=custom_var,
    command=toggle_custom
).pack()


# -----------------------
# 版本输入
# -----------------------
tk.Label(frame,text="主版本号 MAJOR").grid(row=0,column=0,padx=10,pady=5)

entry_major = tk.Entry(frame,width=6,state="disabled",fg="gray")
entry_major.grid(row=0,column=1)

tk.Label(frame,text="次版本号 MINOR").grid(row=1,column=0,padx=10,pady=5)

entry_minor = tk.Entry(frame,width=6,state="disabled",fg="gray")
entry_minor.grid(row=1,column=1)

tk.Label(frame,text="修订号   PATCH").grid(row=2,column=0,padx=10,pady=5)

entry_patch = tk.Entry(frame,width=6,state="disabled",fg="gray")
entry_patch.grid(row=2,column=1)

set_version(major,minor,patch)


# -----------------------
# 自动升级选择
# -----------------------
version_mode = tk.StringVar(value="patch")

# MAJOR
rb_major = tk.Radiobutton(
    frame,
    text="+1",
    variable=version_mode,
    value="major",
    command=calc_next_version
)
rb_major.grid(row=0,column=2,padx=10)

# MINOR
rb_minor = tk.Radiobutton(
    frame,
    text="+1",
    variable=version_mode,
    value="minor",
    command=calc_next_version
)
rb_minor.grid(row=1,column=2,padx=10)

# PATCH
rb_patch = tk.Radiobutton(
    frame,
    text="+1",
    variable=version_mode,
    value="patch",
    command=calc_next_version
)
rb_patch.grid(row=2,column=2,padx=10)

# -----------------------
# 提交
# -----------------------
tk.Button(
    root,
    text="Create Version Tag",
    command=submit
).pack(pady=20)


root.mainloop()