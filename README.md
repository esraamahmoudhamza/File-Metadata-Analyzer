# 🕵️ File Metadata Analyzer (Python GUI Tool)

A lightweight Python GUI application that extracts hidden metadata from your files using various Python libraries.  
Built with **CustomTkinter** for a modern and responsive interface.

## 📽️ See It in Action

If you want to see this tool working live, check out the full YouTube demo here:  
👉 [Watch on YouTube](https://www.youtube.com/@EsraaCodes-e7j/videos)


---

## 📦 Supported File Types

- 📄 PDF (`.pdf`)
- 📃 Word Documents (`.docx`)
- 📝 Plain Text (`.txt`)
- 🖼️ Images (`.jpg`, `.jpeg`, `.png`) — including GPS metadata if available

---

## ✨ Features

- Simple drag-and-analyze interface  
- Extracts metadata such as:
  - Author / Creator
  - Creation and modification timestamps
  - Image EXIF data (camera model, GPS, etc.)
  - Document properties and revision history
- Error handling for unsupported or corrupted files

---

## ⚙️ Requirements

- Python 3.9+
- [Pillow](https://pypi.org/project/Pillow/)
- [PyPDF2](https://pypi.org/project/PyPDF2/)
- [python-docx](https://pypi.org/project/python-docx/)
- [customtkinter](https://pypi.org/project/customtkinter/)

Install all dependencies:

```bash
pip install -r requirements.txt
