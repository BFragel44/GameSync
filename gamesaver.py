import shutil
import os
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from tkinter import Listbox


LOCAL_SAVES = Path(r"C:\STALKER GAMMA\Anomaly\appdata\savedgames")

ONEDRIVE_ROOT = Path(r"C:\Users\Brett\OneDrive\STALKER MAIN PC SAVE")
ONEDRIVE_SAVES = ONEDRIVE_ROOT / "savedgames"

LOCAL_BACKUP_ROOT = LOCAL_SAVES / "BACKUP"
ONEDRIVE_BACKUP_ROOT = ONEDRIVE_ROOT / "BACKUP"


def timestamp():
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def copy_folder_contents(source, dest):
    dest.mkdir(parents=True, exist_ok=True)

    for item in source.iterdir():
        # Do not copy BACKUP folders into save folders
        if item.name.upper() == "BACKUP":
            continue

        target = dest / item.name

        if item.is_dir():
            shutil.copytree(item, target, dirs_exist_ok=True)
        else:
            shutil.copy2(item, target)


def backup_folder(folder_to_backup, backup_root, backup_name):
    if folder_to_backup.exists() and any(folder_to_backup.iterdir()):
        backup_root.mkdir(parents=True, exist_ok=True)
        backup_dest = backup_root / f"{backup_name}_{timestamp()}"

        shutil.copytree(
            folder_to_backup,
            backup_dest,
            ignore=shutil.ignore_patterns("BACKUP")
        )

        return backup_dest

    return None


def get_newest_file(folder):
    if not folder.exists():
        return None

    files = [
        item for item in folder.rglob("*")
        if item.is_file() and "BACKUP" not in item.parts
    ]

    if not files:
        return None

    newest = max(files, key=lambda file: file.stat().st_mtime)
    newest_time = datetime.fromtimestamp(newest.stat().st_mtime)

    return newest.name, newest_time


def update_label(label, folder_name, newest_data):
    if newest_data is None:
        label.config(text=f"{folder_name}: No files found")
        return

    filename, file_time = newest_data
    formatted_time = file_time.strftime("%Y-%m-%d %I:%M:%S %p")

    label.config(
        text=f"{folder_name}: {filename}\nLast Modified: {formatted_time}"
    )


def populate_tree(tree, folder):
    # Clear existing rows
    for row in tree.get_children():
        tree.delete(row)

    if not folder.exists():
        tree.insert("", "end", values=("Folder not found", "", ""))
        return

    files = [
        item for item in folder.iterdir()
        if item.is_file()
    ]

    if not files:
        tree.insert("", "end", values=("No files found", "", ""))
        return

    files.sort(key=lambda item: item.stat().st_mtime, reverse=True)

    for file in files:
        modified_time = datetime.fromtimestamp(file.stat().st_mtime)
        formatted_time = modified_time.strftime("%Y-%m-%d %I:%M:%S %p")
        size_kb = round(file.stat().st_size / 1024, 1)

        tree.insert(
            "",
            "end",
            values=(file.name, formatted_time, f"{size_kb} KB")
        )


def disable_button(btn):
    btn.config(state=tk.DISABLED)


def enable_button(btn):
    btn.config(state=tk.NORMAL)


def refresh_status():
    local_newest = get_newest_file(LOCAL_SAVES)
    onedrive_newest = get_newest_file(ONEDRIVE_SAVES)

    update_label(local_label, "Local", local_newest)
    update_label(onedrive_label, "OneDrive", onedrive_newest)

    local_label.config(fg="black")
    onedrive_label.config(fg="black")

    # Default safe state
    disable_button(button_one)
    disable_button(button_two)

    if local_newest and onedrive_newest:
        if local_newest[1] > onedrive_newest[1]:
            local_label.config(fg="green")
            onedrive_label.config(fg="red")

            enable_button(button_one)
            disable_button(button_two)

        elif onedrive_newest[1] > local_newest[1]:
            onedrive_label.config(fg="green")
            local_label.config(fg="red")

            disable_button(button_one)
            enable_button(button_two)

        else:
            local_label.config(fg="green")
            onedrive_label.config(fg="green")

            disable_button(button_one)
            disable_button(button_two)

    populate_tree(local_tree, LOCAL_SAVES)
    populate_tree(onedrv_tree, ONEDRIVE_SAVES)


def sync_local_to_onedrive():
    try:
        if not LOCAL_SAVES.exists():
            raise FileNotFoundError(f"Local saves folder not found:\n{LOCAL_SAVES}")

        backup_folder(
            ONEDRIVE_SAVES,
            ONEDRIVE_BACKUP_ROOT,
            "onedrive_savedgames_backup"
        )

        copy_folder_contents(LOCAL_SAVES, ONEDRIVE_SAVES)
        refresh_status()

        messagebox.showinfo(
            "Success",
            "LOCAL saves copied to OneDrive.\n\nExisting OneDrive saves were backed up first."
        )

    except Exception as e:
        messagebox.showerror("Error", str(e))


def sync_onedrive_to_local():
    try:
        if not ONEDRIVE_SAVES.exists():
            raise FileNotFoundError(f"OneDrive saves folder not found:\n{ONEDRIVE_SAVES}")

        backup_folder(
            LOCAL_SAVES,
            LOCAL_BACKUP_ROOT,
            "local_savedgames_backup"
        )

        copy_folder_contents(ONEDRIVE_SAVES, LOCAL_SAVES)
        refresh_status()

        messagebox.showinfo(
            "Success",
            "ONEDRIVE saves copied to LOCAL folder.\n\nExisting local saves were backed up first."
        )

    except Exception as e:
        messagebox.showerror("Error", str(e))


def show():
    label.config(text=f"Selected: {listbox.get(ACTIVE)}")


# Main window
root = tk.Tk()
root.title("OneDrive Game Sync")
root.geometry("1020x560")
root.resizable(False, False)
root.config(bg="black")

# Main layout rows
root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)

# Top title / refresh row
header_frame = tk.Frame(root, bg="black")
header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=(130,10), pady=(10, 20))

header_frame.columnconfigure(0, weight=1)
header_frame.columnconfigure(1, weight=1)
header_frame.columnconfigure(2, weight=1)

# Listbox  
listbox = Listbox(root)
for item in [rf"{ONEDRIVE_ROOT}"]:
    listbox.insert(0, item)
listbox.grid()

# Button & Label  
# Button(root, text="Show Selection", command=show).pack()
# label = Label(root, text=" ")
# label.pack()

title = tk.Label(
    header_frame,
    text="OneDrive Game Sync",
    font=("Segoe UI", 16, "bold"),
    bg="white",
    fg="black",
    padx=4,
    pady=8
)
title.grid(row=0, column=1,)

refresh_button = tk.Button(
    header_frame,
    text="Refresh Save Status",
    font=("Segoe UI", 9),
    command=refresh_status
)
refresh_button.grid(row=0, column=2, sticky="e", padx=(0, 10))


# Two-column content area
content_frame = tk.Frame(root, bg="black")
content_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10)

content_frame.columnconfigure(0, weight=1, uniform="sync_columns")
content_frame.columnconfigure(1, weight=1, uniform="sync_columns")


# LEFT: LOCAL FILES
local_panel = tk.Frame(content_frame, bg="black")
local_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

local_label = tk.Label(
    local_panel,
    text="Local: Checking...",
    font=("Segoe UI", 9),
    justify="center",
    bg="white"
)
local_label.pack(fill="x", pady=(0, 6))

button_one = tk.Button(
    local_panel,
    text="Local → OneDrive",
    font=("Segoe UI", 10, "bold"),
    height=2,
    command=sync_local_to_onedrive
)
button_one.pack(fill="x", pady=(0, 8))

local_tree = ttk.Treeview(
    master=local_panel,
    columns=("filename", "modified", "size"),
    show="headings",
    selectmode="browse",
    height=13
)

local_tree.heading("filename", text="Local Files")
local_tree.heading("modified", text="Modified")
local_tree.heading("size", text="Size")

local_tree.column("filename", width=230)
local_tree.column("modified", width=170)
local_tree.column("size", width=80)

local_tree.pack(fill="both", expand=True)


# RIGHT: OneDrive
onedrive_panel = tk.Frame(content_frame, bg="black")
onedrive_panel.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

onedrive_label = tk.Label(
    onedrive_panel,
    text="OneDrive: Checking...",
    font=("Segoe UI", 9),
    justify="center",
    bg="white"
)
onedrive_label.pack(fill="x", pady=(0, 6))

button_two = tk.Button(
    onedrive_panel,
    text="OneDrive → Local",
    font=("Segoe UI", 10, "bold"),
    height=2,
    command=sync_onedrive_to_local
)
button_two.pack(fill="x", pady=(0, 8))

onedrv_tree = ttk.Treeview(
    master=onedrive_panel,
    columns=("filename", "modified", "size"),
    show="headings",
    selectmode="browse",
    height=13
)

onedrv_tree.heading("filename", text="OneDrive Files")
onedrv_tree.heading("modified", text="Modified")
onedrv_tree.heading("size", text="Size")

onedrv_tree.column("filename", width=230)
onedrv_tree.column("modified", width=170)
onedrv_tree.column("size", width=80)

onedrv_tree.pack(fill="both", expand=True)


refresh_status()

root.mainloop()