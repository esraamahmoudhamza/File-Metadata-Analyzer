import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ExifTags
import PyPDF2
import docx
import os
from datetime import datetime
import openpyxl
from pymediainfo import MediaInfo

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("MetaReveal V2 - Advanced Metadata Analyzer")
app.geometry("850x700")

current_img = None  

def convert_gps(coord, ref):
    d = coord[0][0] / coord[0][1]
    m = coord[1][0] / coord[1][1]
    s = coord[2][0] / coord[2][1]
    decimal = d + (m / 60.0) + (s / 3600.0)
    if ref in ['S', 'W']:
        decimal = -decimal
    return decimal

def gps_to_link(lat, lon):
    return f"https://www.google.com/maps?q={lat},{lon}"

def extract_image_metadata(path):
    metadata = ""
    global current_img
    try:
        image = Image.open(path)
        image.thumbnail((250, 250))
        current_img = ImageTk.PhotoImage(image)
        
        exif_data = image._getexif()
        if exif_data:
            gps_info = None
            for tag_id, value in exif_data.items():
                tag = ExifTags.TAGS.get(tag_id, tag_id)
                if tag == "GPSInfo":
                    gps_info = value
                else:
                    metadata += f"{tag}: {value}\n"
            if gps_info:
                gps_tags = {}
                for key in gps_info.keys():
                    name = ExifTags.GPSTAGS.get(key, key)
                    gps_tags[name] = gps_info[key]
                if ('GPSLatitude' in gps_tags and 'GPSLongitude' in gps_tags
                    and 'GPSLatitudeRef' in gps_tags and 'GPSLongitudeRef' in gps_tags):
                    lat = convert_gps(gps_tags['GPSLatitude'], gps_tags['GPSLatitudeRef'])
                    lon = convert_gps(gps_tags['GPSLongitude'], gps_tags['GPSLongitudeRef'])
                    metadata += f"GPS Latitude: {lat}\n"
                    metadata += f"GPS Longitude: {lon}\n"
                    metadata += f"Google Maps Link: {gps_to_link(lat, lon)}\n"
            else:
                metadata += "No GPS metadata found.\n"
        else:
            metadata = "No EXIF metadata found in image."
    except Exception as e:
        metadata = f"Error reading image metadata: {e}"
        current_img = None
    return metadata

def extract_pdf_metadata(path):
    metadata = ""
    try:
        with open(path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            doc_info = reader.metadata
            if doc_info:
                for key, value in doc_info.items():
                    metadata += f"{key[1:]}: {value}\n"
            else:
                metadata = "No metadata found in PDF."
    except Exception as e:
        metadata = f"Error reading PDF metadata: {e}"
    return metadata

def extract_docx_metadata(path):
    metadata = ""
    try:
        doc = docx.Document(path)
        props = doc.core_properties
        for attr in dir(props):
            if not attr.startswith("_") and not callable(getattr(props, attr)):
                value = getattr(props, attr)
                if value:
                    metadata += f"{attr}: {value}\n"
        if not metadata:
            metadata = "No metadata found in Word document."
    except Exception as e:
        metadata = f"Error reading Word metadata: {e}"
    return metadata

def extract_xlsx_metadata(path):
    metadata = ""
    try:
        wb = openpyxl.load_workbook(path, read_only=True)
        props = wb.properties
        metadata += f"Title: {props.title}\n"
        metadata += f"Subject: {props.subject}\n"
        metadata += f"Creator: {props.creator}\n"
        metadata += f"Created: {props.created}\n"
        metadata += f"Modified: {props.modified}\n"
        metadata += f"Category: {props.category}\n"
        metadata += f"Keywords: {props.keywords}\n"
    except Exception as e:
        metadata = f"Error reading Excel metadata: {e}"
    return metadata

def extract_text_metadata(path):
    metadata = ""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            lines = []
            for _ in range(10):
                line = f.readline()
                if not line:
                    break
                lines.append(line.strip())
            metadata = "First 10 lines of text file:\n" + "\n".join(lines)
    except Exception as e:
        metadata = f"Error reading text file: {e}"
    return metadata

def extract_video_metadata(path):
    metadata = ""
    try:
        media_info = MediaInfo.parse(path)
        for track in media_info.tracks:
            if track.track_type == "General":
                metadata += f"Format: {track.format}\n"
                if track.duration:
                    metadata += f"Duration: {track.duration / 1000:.2f} seconds\n"
                if track.file_size:
                    metadata += f"File size: {track.file_size} bytes\n"
                if track.overall_bit_rate:
                    metadata += f"Overall bit rate: {track.overall_bit_rate} bps\n"
                if track.encoded_date:
                    metadata += f"Encoded date: {track.encoded_date}\n"
                if track.tagged_date:
                    metadata += f"Tagged date: {track.tagged_date}\n"
                break
    except Exception as e:
        metadata = f"Error reading video metadata: {e}"
    return metadata

def get_file_system_dates(path):
    try:
        stat = os.stat(path)
        created = datetime.fromtimestamp(stat.st_ctime)
        modified = datetime.fromtimestamp(stat.st_mtime)
        diff = modified - created
        return created, modified, diff
    except Exception as e:
        return None, None, None

def choose_file():
    file_path = filedialog.askopenfilename(
        filetypes=[
            ("Supported Files", "*.jpg *.jpeg *.png *.pdf *.docx *.xlsx *.txt *.mp4 *.avi")
        ])
    if file_path:
        entry_file_path.configure(state="normal")
        entry_file_path.delete(0, "end")
        entry_file_path.insert(0, file_path)
        entry_file_path.configure(state="readonly")
        textbox_result.configure(state="normal")
        textbox_result.delete("1.0", "end")
        textbox_result.configure(state="disabled")
        label_image.configure(image=None)

def save_report():
    content = textbox_result.get("1.0", "end").strip()
    if not content:
        messagebox.showinfo("Info", "No metadata to save.")
        return
    file = filedialog.asksaveasfilename(defaultextension=".txt",
                                        filetypes=[("Text files", "*.txt")])
    if file:
        try:
            with open(file, "w", encoding="utf-8") as f:
                f.write(content)
            messagebox.showinfo("Success", f"Report saved to {file}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save file: {e}")

def analyze_metadata():
    file_path = entry_file_path.get()
    if not os.path.exists(file_path):
        messagebox.showerror("Error", "Please select a valid file.")
        return

    extension = os.path.splitext(file_path)[1].lower()
    result = ""

    global current_img

    if extension in [".jpg", ".jpeg", ".png"]:
        result = extract_image_metadata(file_path)
        if current_img:
            label_image.configure(image=current_img)
        else:
            label_image.configure(image=None)
    elif extension == ".pdf":
        result = extract_pdf_metadata(file_path)
        label_image.configure(image=None)
    elif extension == ".docx":
        result = extract_docx_metadata(file_path)
        label_image.configure(image=None)
    elif extension == ".xlsx":
        result = extract_xlsx_metadata(file_path)
        label_image.configure(image=None)
    elif extension == ".txt":
        result = extract_text_metadata(file_path)
        label_image.configure(image=None)
    elif extension in [".mp4", ".avi"]:
        result = extract_video_metadata(file_path)
        label_image.configure(image=None)
    else:
        result = "Unsupported file type."
        label_image.configure(image=None)

    created, modified, diff = get_file_system_dates(file_path)
    if created and modified:
        result += "\n--- File System Dates ---\n"
        result += f"Created: {created}\n"
        result += f"Modified: {modified}\n"
        result += f"Time between creation and modification: {diff}\n"

    if "No metadata found" in result or "No EXIF metadata" in result:
        result += "\n Warning: This file has no detectable metadata. It may have been stripped or generated online."

    textbox_result.configure(state="normal")
    textbox_result.delete("1.0", "end")
    textbox_result.insert("1.0", result)
    textbox_result.configure(state="disabled")


frame = ctk.CTkFrame(app)
frame.pack(pady=15, padx=15, fill="both", expand=True)

label_title = ctk.CTkLabel(frame, text="MetaReveal V2 - Advanced Metadata Analyzer", font=("Arial", 20, "bold"))
label_title.pack(pady=10)

btn_browse = ctk.CTkButton(frame, text="Choose File", command=choose_file)
btn_browse.pack(pady=10)

entry_file_path = ctk.CTkEntry(frame, placeholder_text="Selected file path will appear here", width=600)
entry_file_path.configure(state="readonly")
entry_file_path.pack(pady=5)

btn_analyze = ctk.CTkButton(frame, text="Analyze Metadata", command=analyze_metadata)
btn_analyze.pack(pady=10)

btn_save = ctk.CTkButton(frame, text="Save Report", command=save_report)
btn_save.pack(pady=5)

label_image = ctk.CTkLabel(frame)
label_image.pack(pady=10)

textbox_result = ctk.CTkTextbox(frame, width=800, height=300)
textbox_result.configure(state="disabled")
textbox_result.pack(pady=10)

app.mainloop()
