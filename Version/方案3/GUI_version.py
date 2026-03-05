import tkinter as tk
from pathlib import Path
from datetime import datetime

VERSION_FILE = Path.cwd() / "version_base.txt"

def read_version():
    kv = {}
    for line in VERSION_FILE.read_text().splitlines():
        if "=" in line:
            k,v = line.split("=")
            kv[k] = v
    return kv

def write_version(major,minor,patch,build,build_realtime,build_realnum):
    content = f"""MAJOR={major}
MINOR={minor}
PATCH={patch}
BUILD={build}
BUILD_REALTIME={build_realtime}
BUILD_REALNUM={build_realnum}
"""
    VERSION_FILE.write_text(content)

def submit():
    major = e1.get()
    minor = e2.get()
    patch = e3.get()
    build = e4.get()
    build_realtime = datetime.now().strftime("%Y%m%d%H%M%S")
    build_realnum = f"v{major}.{minor}.{patch}.{build}"
    write_version(major,minor,patch,build,build_realtime,build_realnum)
    root.destroy()

kv = read_version()

root = tk.Tk()
root.title("Version Editor")
root.geometry("300x300")

tk.Label(root,text="MAJOR").pack()
e1 = tk.Entry(root)
e1.insert(0,kv.get("MAJOR","0"))
e1.pack()

tk.Label(root,text="MINOR").pack()
e2 = tk.Entry(root)
e2.insert(0,kv.get("MINOR","0"))
e2.pack()

tk.Label(root,text="PATCH").pack()
e3 = tk.Entry(root)
e3.insert(0,kv.get("PATCH","0"))
e3.pack()

tk.Label(root,text="BUILD").pack()
e4 = tk.Entry(root)
e4.insert(0,kv.get("BUILD","0"))
e4.pack()

tk.Button(root,text="Git Version Tag",command=submit).pack(pady=10)

root.mainloop()