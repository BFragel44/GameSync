#  Save Sync

A lightweight Python utility for syncing and backing up save game files between a local directory and OneDrive.

This was built to make it easier to move between multiple PCs without losing progress or accidentally overwriting newer saves for games that are not on Steam etc.

---

## Features

- Sync saves from Local ➜ OneDrive
- Sync saves from OneDrive ➜ Local
- Timestamp comparison to prevent accidental overwrites
- Automatic backup folder support
- Simple desktop GUI using Tkinter

---

## Current Goals

- Improve UI layout and readability
- Add overwrite safeguards and warnings
- Improve sync validation logic
- Allow for file paths to be saved in config as local & OneDrive path pairs.

---

## Tech Stack

- Python
- Tkinter
- shutil
- pathlib
- os

---

## Project Status

Active personal utility project.

Created to solve real-world laziness when playing S.T.A.L.K.E.R. Anomaly between main PC and laptop installs.

---

## Example Use Case

Desktop PC session ends → Sync latest saves to OneDrive → Open laptop later and pull latest saves locally without manually digging through folders.

---

## Disclaimer

This tool modifies save files and directories. Always keep independent backups of important saves.
