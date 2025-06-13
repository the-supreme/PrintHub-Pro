import os
import re
import shutil
import fitz
from PyPDF2 import PdfMerger
import tempfile

def add_blank_page(doc): 
    last_page = doc[-1]
    width, height = last_page.rect.width, last_page.rect.height
    doc.new_page(width=width, height=height)
    return doc

def extract_phone_number(filename):
    match = re.search(r'\b(01[0-9]{8,9})\b', filename)
    return match.group(1) if match else None

def rename_file(pdf_path, phone, quantity, paper_size, color_mode, duplex):
    last4 = phone[-4:]
    type_str = 'Duplex' if duplex else 'Simplex'
    new_name = f"{last4}-{str(quantity).zfill(2)}-{paper_size}-{color_mode.capitalize()}-{type_str}.pdf"
    return new_name

def move_and_rename(src_path, new_filename):
    dest_folder = os.path.join("media", "processed")
    os.makedirs(dest_folder, exist_ok=True)
    new_path = os.path.join(dest_folder, new_filename)
    shutil.move(src_path, new_path)
    return new_path

def get_page_count(pdf_path):
    doc = fitz.open(pdf_path)
    count = doc.page_count
    doc.close()
    return count

def calculate_cost(page_count, color_mode, duplex, quantity):
    color_rate = 0.50 if color_mode.lower() == 'color' else 0.20
    duplex_discount = 0.85 if duplex else 1.0  # e.g. duplex prints 15% cheaper
    cost_per_copy = page_count * color_rate * duplex_discount
    total = cost_per_copy * quantity
    return round(total, 2)

def merge_pdf(pdf_paths):
    merger = PdfMerger()
    for path in pdf_paths:
        merger.append(path)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as output:
        merger.write(output.name)
        return output.name

