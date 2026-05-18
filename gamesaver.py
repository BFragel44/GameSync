import shutil
import json
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox


CONFIG_FILE = Path(__file__).with_name("config.json")
DEFAULT_CONFIG = {
    "local_saves": r"C:\STALKER GAMMA\Anomaly\appdata\savedgames",
    "onedrive_saves": r"C:\Users\Brett\OneDrive\STALKER MAIN PC SAVE\savedgames",
}


def save_config(config):
    with CONFIG_FILE.open("w", encoding="utf-8") as config_file:
        json.dump(config, config_file, indent=2)


def load_config():
    if not CONFIG_FILE.exists():
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()

    with CONFIG_FILE.open("r", encoding="utf-8") as config_file:
        loaded_config = json.load(config_file)

    config = DEFAULT_CONFIG.copy()
    config.update(loaded_config)
    return config


config = load_config()

LOCAL_SAVES = Path(config["local_saves"])
ONEDRIVE_SAVES = Path(config["onedrive_saves"])

LOCAL_BACKUP_ROOT = LOCAL_SAVES / "BACKUP"
ONEDRIVE_BACKUP_ROOT = ONEDRIVE_SAVES.parent / "BACKUP"


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
    local_path_var.set(str(LOCAL_SAVES))
    onedrive_path_var.set(str(ONEDRIVE_SAVES))


def sync_local_to_onedrive():
    try:
        if not LOCAL_SAVES.exists():
            raise FileNotFoundError(f"Local saves folder not found:\n{LOCAL_SAVES}")

        backup_created = None
        if onedrive_backup_var.get():
            backup_created = backup_folder(
                ONEDRIVE_SAVES,
                ONEDRIVE_BACKUP_ROOT,
                "onedrive_savedgames_backup"
            )

        copy_folder_contents(LOCAL_SAVES, ONEDRIVE_SAVES)
        refresh_status()

        backup_message = (
            f"\n\nBackup created:\n{backup_created}"
            if backup_created
            else "\n\nNo destination backup was created."
        )

        messagebox.showinfo(
            "Success",
            f"LOCAL saves copied to OneDrive.{backup_message}"
        )

    except Exception as e:
        messagebox.showerror("Error", str(e))


def sync_onedrive_to_local():
    try:
        if not ONEDRIVE_SAVES.exists():
            raise FileNotFoundError(f"OneDrive saves folder not found:\n{ONEDRIVE_SAVES}")

        backup_created = None
        if local_backup_var.get():
            backup_created = backup_folder(
                LOCAL_SAVES,
                LOCAL_BACKUP_ROOT,
                "local_savedgames_backup"
            )

        copy_folder_contents(ONEDRIVE_SAVES, LOCAL_SAVES)
        refresh_status()

        backup_message = (
            f"\n\nBackup created:\n{backup_created}"
            if backup_created
            else "\n\nNo destination backup was created."
        )

        messagebox.showinfo(
            "Success",
            f"ONEDRIVE saves copied to LOCAL folder.{backup_message}"
        )

    except Exception as e:
        messagebox.showerror("Error", str(e))


# Main window
root = tk.Tk()
root.title("OneDrive Game Sync")
root.geometry("1020x600")
root.resizable(False, False)
root.config(bg="black")

local_backup_var = tk.BooleanVar(value=False)
onedrive_backup_var = tk.BooleanVar(value=False)
local_path_var = tk.StringVar(value=str(LOCAL_SAVES))
onedrive_path_var = tk.StringVar(value=str(ONEDRIVE_SAVES))

# Main layout rows
root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)

# Top title / refresh row
header_frame = tk.Frame(root, bg="black")
header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=(130,10), pady=(10, 20))

header_frame.columnconfigure(0, weight=1)
header_frame.columnconfigure(1, weight=1)
header_frame.columnconfigure(2, weight=1)

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

local_path_entry = tk.Entry(
    local_panel,
    textvariable=local_path_var,
    font=("Segoe UI", 9),
    state="readonly",
    readonlybackground="white",
    fg="black"
)
local_path_entry.pack(fill="x", pady=(0, 8))

local_tree = ttk.Treeview(
    master=local_panel,
    columns=("filename", "modified", "size"),
    show="headings",
    selectmode="browse",
    height=13
)

# Vertical scrollbar
vsb = ttk.Scrollbar(local_panel, orient="vertical", command=local_tree.yview)
vsb.pack(side="right", fill="y")

# Vertical scrollbar config
local_tree.configure(yscrollcommand=vsb.set)
local_tree.pack(expand=True, fill="both")

local_tree.heading("filename", text="Local Files")
local_tree.heading("modified", text="Modified")
local_tree.heading("size", text="Size")

local_tree.column("filename", width=230)
local_tree.column("modified", width=170)
local_tree.column("size", width=80)

local_tree.pack(fill="both", expand=True)

local_backup_check = tk.Checkbutton(
    local_panel,
    text="Create backup when this is destination",
    variable=local_backup_var,
    bg="black",
    fg="white",
    selectcolor="black",
    activebackground="black",
    activeforeground="white",
    anchor="w"
)
local_backup_check.pack(fill="x", pady=(6, 0))


# RIGHT: ONEDRIVE FILES
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

onedrive_path_entry = tk.Entry(
    onedrive_panel,
    textvariable=onedrive_path_var,
    font=("Segoe UI", 9),
    state="readonly",
    readonlybackground="white",
    fg="black"
)
onedrive_path_entry.pack(fill="x", pady=(0, 8))

onedrv_tree = ttk.Treeview(
    master=onedrive_panel,
    columns=("filename", "modified", "size"),
    show="headings",
    selectmode="browse",
    height=13
)

# Vertical scrollbar
vsb = ttk.Scrollbar(onedrive_panel, orient="vertical", command=onedrv_tree.yview)
vsb.pack(side="right", fill="y")

# Vertical scrollbar config
onedrv_tree.configure(yscrollcommand=vsb.set)
onedrv_tree.pack(expand=True, fill="both")

onedrv_tree.heading("filename", text="OneDrive Files")
onedrv_tree.heading("modified", text="Modified")
onedrv_tree.heading("size", text="Size")

onedrv_tree.column("filename", width=230)
onedrv_tree.column("modified", width=170)
onedrv_tree.column("size", width=80)

onedrv_tree.pack(fill="both", expand=True)

onedrive_backup_check = tk.Checkbutton(
    onedrive_panel,
    text="Create backup when this is destination",
    variable=onedrive_backup_var,
    bg="black",
    fg="white",
    selectcolor="black",
    activebackground="black",
    activeforeground="white",
    anchor="w"
)
onedrive_backup_check.pack(fill="x", pady=(6, 0))


refresh_status()

root.mainloop()
