from PyPDF2 import PdfReader, PdfWriter
import fitz
import os
from .utils import add_blank_page, get_page_count

def format_pdf(input_pdf_path, config):
    layout = config.get("layout", "normat")
    orientation = config.get("orientation", "portrait")
    color_mode = config.get("color_mode", "color").lower()
    paper_size = config.get("paper_size", "A4")
    duplex = config.get("duplex", False)
    insert_blank = config.get("insert_blank_pages", False)
    page_range = config.get("page_range", "all")
    
    doc = fitz.open(input_pdf_path)
    
    #if the page range provided, then we extract it
    
    if page_range != "all":
        doc = extract_page_range(doc, page_range)
    
    #if the color_mode is blackwhite...
    if color_mode in ("bw", "blackwhite", "black-white", "grayscale"):
        doc = convert_to_grayscale(doc)

    # if orientation landscape
    if orientation == "landscape":
        doc = rotate_pages(doc, 90)
        
    # Adjust the layout
    if layout == "booklet":
        doc = apply_booklet_layout(doc)
        
    elif layout == "2-in-1":
        doc = merge_pages_n_in_1(doc, 2)
    elif layout == "4-in-1":
        doc = merge_pages_n_in_1(doc, 4)
        
    # add blank page
    if insert_blank or duplex:
        doc = add_blank_page(doc)
        
    base, ext = os.path.splitext(input_pdf_path)
    output_path = f"{base}_formatted.pdf"
    doc.save(output_path)
    doc.close()
    
    return output_path

def extract_page_range(doc, page_range):
    new_doc = fitz.open()
    pages = []
    
    for part in page_range.replace(' ', '').split(','):
        if '-' in part:
            start, end = map(int, part.split('-'))
            pages.extend(range(start - 1, end))
        else:
            pages.append(int(part) - 1)
            
    for page_num in pages:
        if 0 <= page_num < len(doc):
            new_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)
    
    return new_doc
    

def convert_to_grayscale(doc):
    new_doc = fitz.open()

    for page in doc:
        pix = page.get_pixmap(colorspace=fitz.csGRAY)
        rect = fitz.Rect(0, 0, pix.width, pix.height)
        new_page = new_doc.new_page(width=pix.width, height=pix.height)
        new_page.insert_image(rect, pixmap=pix)

    return new_doc

def rotate_pages(doc, angle):
        for page in doc:
            page.set_rotation(angle)    
        return doc

def apply_booklet_layout(doc: fitz.Document) -> fitz.Document:
    # Step 1: Pad to multiple of 4
    total_pages = doc.page_count
    padded_doc = fitz.open()
    padded_doc.insert_pdf(doc)

    while padded_doc.page_count % 4 != 0:
        padded_doc.new_page()

    n = padded_doc.page_count
    new_doc = fitz.open()

    # Step 2: Generate booklet spreads (outer to inner)
    for i in range(n // 2):
        if i % 2 == 0:
            left = n - 1 - i
            right = i
        else:
            left = i
            right = n - 1 - i

        spread = fitz.open()
        spread.insert_pdf(padded_doc, from_page=left, to_page=left)
        spread.insert_pdf(padded_doc, from_page=right, to_page=right)

        # Step 3: Merge side by side into a landscape page
        merged = merge_pages_n_in_1(spread, 2)
        new_doc.insert_pdf(merged)

    return new_doc

def merge_pages_n_in_1(doc: fitz.Document, n: int) -> fitz.Document:
    if n not in (2, 4):
        raise ValueError("Only 2 or 4 pages per sheet supported")

    new_doc = fitz.Document()
    page_count = doc.page_count

    # Grid layout
    rows, cols = (1, 2) if n == 2 else (2, 2)

    # Use first page for size reference
    first_page = doc.load_page(0)
    src_rect = first_page.rect
    src_width, src_height = src_rect.width, src_rect.height

    # Dynamically set output page size based on layout
    out_width = src_width * cols
    out_height = src_height * rows

    cell_width = out_width / cols
    cell_height = out_height / rows

    # DPI scaling factor
    zoom = 2  # ~144 DPI for crispness
    mat = fitz.Matrix(zoom, zoom)

    for i in range(0, page_count, n):
        new_page = new_doc.new_page(width=out_width, height=out_height)

        for j in range(n):
            page_index = i + j
            if page_index >= page_count:
                continue

            src_page = doc.load_page(page_index)
            pix = src_page.get_pixmap(matrix=mat, alpha=False)

            row = j // cols
            col = j % cols
            x = col * cell_width
            y = row * cell_height

            target_rect = fitz.Rect(x, y, x + cell_width, y + cell_height)
            new_page.insert_image(target_rect, pixmap=pix, keep_proportion=True)

    return new_doc
    