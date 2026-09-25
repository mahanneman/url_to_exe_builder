# 🌐 URL to EXE Builder

[🇬🇧 English](README.md) | [🇮🇷 فارسی](README.FA.md)

**Turn any website URL into a standalone Windows EXE**  
Developed by **Mahan Neman (MA.AD.GH)** – Tehran  
GitHub: [github.com/mahanneman](https://github.com/mahanneman)

Works both as a **Python script** and as a **compiled EXE**.

---

## 📌 Table of Contents
- [Features](#-features)
- [Screenshots](#-screenshots)
- [Requirements](#-requirements)
- [Installation & Running](#-installation--running)
- [How to Use](#-how-to-use)
- [Advanced Options](#-advanced-options)
- [Troubleshooting](#-troubleshooting)
- [License](#-license)

---

## ✨ Features

| Feature                                      | Status |
|----------------------------------------------|--------|
| Convert any URL to a standalone EXE          | ✅     |
| One-file or folder mode                      | ✅     |
| Windowed (no console) mode                   | ✅     |
| Custom icon support (auto-converts PNG/JPG/BMP → ICO) | ✅ |
| 45 advanced PyInstaller options              | ✅     |
| Live build log                               | ✅     |
| Paste & Test URL buttons                     | ✅     |
| Open output folder                           | ✅     |
| Right-click context menu (Copy/Paste/Cut)    | ✅     |
| Works from source **and** as frozen EXE      | ✅     |
| Auto-detects Python + PyInstaller            | ✅     |
| Automatic Pillow installation for icon conversion | ✅ |

---

## 📸 Screenshots

<img width="1599" height="849" alt="image" src="https://github.com/user-attachments/assets/133a983a-8e5c-4aa4-9ca0-7d4bcbde5dac" />

- Main interface with URL field and advanced options  
- Build log during compilation  

---

## 📋 Requirements

- **Windows**
- **Python 3.8+** (if running from source)
- **PyInstaller** (`pip install pyinstaller`)
- Optional: **Pillow** (auto-installed if needed for icon conversion)

---

## 🚀 Installation & Running

### Option 1 – Run from source

```bash
git clone https://github.com/mahanneman/url-to-exe-builder.git
cd url-to-exe-builder
pip install pyinstaller pillow
python url_to_exe_builder.py
