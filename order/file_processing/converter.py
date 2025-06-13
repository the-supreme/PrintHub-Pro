import os
import tempfile
from pathlib import Path
from PIL import Image
from docx2pdf import convert as docx2pdf_convert
import shutil

# def convert_to_pdf(uploaded_file):
#     input_ext = Path(uploaded_file).suffix.lower()
    
#     # save the file temporarily
#     with tempfile.NamedTemporaryFile(delete=False, suffix=input_ext) as temp_input:
#         for chunk in uploaded_file.chunks():
#             temp_input.write(chunk)
#         temp_input_path = temp_input.name
        
#     if input_ext in ['.pdf']:
#         return temp_input_path
    
#     elif input_ext in ['.jpg', '.jpeg', '.png']:
#         return convert_image_to_pdf(temp_input_path)
    
#     elif input_ext in ['.docx']:
#         return convert_docx_to_pdf(temp_input_path)
    
#     else:
#         raise ValueError("Unsupported File Type: " + input_ext)

def convert_to_pdf(file_path):
    input_ext = Path(file_path).suffix.lower()
    
    if input_ext in ['.pdf']:
        return file_path
    
    elif input_ext in ['.jpg', '.jpeg', '.png']:
        return convert_image_to_pdf(file_path)
    
    elif input_ext in ['.docx']:
        return convert_docx_to_pdf(file_path)
    
    else:
        raise ValueError("Unsupported File Type: " + input_ext)

    
def convert_image_to_pdf(image_path):
    image = Image.open(image_path).convert('RGB')
    output_path = str(Path(image_path).with_suffix('.pdf'))
    image.save(output_path, 'PDF')
    return output_path


def convert_docx_to_pdf(input_path):
    output_dir =  tempfile.mkdtemp()
    input_copy = shutil.copy(input_path, os.path.join(output_dir, "input.docx"))
    output_pdf_path = os.path.join(output_dir, "input.pdf")

    docx2pdf_convert(input_copy, output_pdf_path)
    
    if not os.path.exists(output_pdf_path):
        raise Exception("DOCX to PDF conversion failed.")
    
    return output_pdf_path