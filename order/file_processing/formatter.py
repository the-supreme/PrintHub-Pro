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

def apply_booklet_layout(doc):
    pages = [doc.load_page(i) for i in range(len(doc))]
    total_pages = len(pages)
    
    while total_pages % 4 != 0:
        doc.new_page()  # Add blank page at end(-1)
        total_pages += 1

    new_doc = fitz.open()
    left = 0
    right = total_pages - 1

    while left < right:
        new_doc.insert_pdf(doc, from_page=right)
        new_doc.insert_pdf(doc, from_page=left)
        left += 1
        right -= 1

    return new_doc


def merge_pages_n_in_1(doc: fitz.Document, n: int) -> fitz.Document:
    if n not in (2, 4):
        raise ValueError("Only 2 or 4 pages per sheet supported")

    new_doc = fitz.Document()

    page_count = doc.page_count

    # Grid layout for n pages:
    if n == 2:
        rows, cols = 1, 2
    else:  # n == 4
        rows, cols = 2, 2

    # Use first page as reference for size
    first_page = doc.load_page(0)
    src_rect = first_page.rect
    src_width, src_height = src_rect.width, src_rect.height

    # Output page dimensions remain same as original page (to avoid confusion)
    # But inside, we will scale pages down to fit in grid cells.
    # So output page size == original page size

    out_width, out_height = src_width, src_height

    # Calculate size of each grid cell on output page:
    cell_width = out_width / cols
    cell_height = out_height / rows

    # Iterate over pages in chunks of n
    for i in range(0, page_count, n):
        new_page = new_doc.new_page(width=out_width, height=out_height)

        for j in range(n):
            page_index = i + j
            if page_index >= page_count:
                # no page to add, optionally leave blank or continue
                continue

            src_page = doc.load_page(page_index)

            # Render source page to pixmap
            # Calculate scaling to fit into cell size
            # Use zoom factors to keep aspect ratio

            zoom_x = cell_width / src_width
            zoom_y = cell_height / src_height
            zoom = min(zoom_x, zoom_y)

            mat = fitz.Matrix(zoom, zoom)
            pix = src_page.get_pixmap(matrix=mat, alpha=False)

            # Calculate position for this page on the new_page
            row = j // cols
            col = j % cols
            x = col * cell_width
            y = row * cell_height

            # Insert pixmap image at (x,y)
            # fitz.Rect expects float coords: left, top, right, bottom
            rect = fitz.Rect(x, y, x + pix.width, y + pix.height)
            new_page.insert_image(rect, pixmap=pix)

    return new_doc
    