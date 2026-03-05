import tkinter as tk

root = tk.Tk()
root.title("Build Tool")
root.geometry("400x200")

label = tk.Label(root, text="Firmware Build Tool")
label.pack(pady=20)

def build():
    print("Start Build")

btn = tk.Button(root, text="Build Keil Project", command=build)
btn.pack()

root.mainloop()