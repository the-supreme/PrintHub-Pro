from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .file_processing import converter, formatter, utils
import os
import tempfile
from .models import PrintOrder
import json


@csrf_exempt
@require_POST
def process_file(request):
    try:
        uploaded_files = request.FILES.getlist('files')
        config = {
            'layout': request.POST.get('layout'),
            'orientation': request.POST.get('orientation'),
            'color_mode': request.POST.get('color_mode'),
            'paper_size': request.POST.get('paper_size'),
            'simplex': request.POST.get('duplex'),
            'pages': request.POST.get('pages'),
            'quantity': int(request.POST.get('qty')),
            'phone': request.POST.get('phone_number'),
        }
        
        converted_pdf_paths = []

        
        # Save file in temp
        # Convert to pdf
        for uploaded_file in uploaded_files:
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as temp_file:
                for chunk in uploaded_file.chunks():
                    temp_file.write(chunk)
                temp_input_path = temp_file.name

            pdf_path = converter.convert_to_pdf(temp_input_path)  # You already handle image/doc to PDF
            converted_pdf_paths.append(pdf_path)
        
                
        # Merge PDFs if more than one
        
        if len(converted_pdf_paths) == 1:
            merged_pdf_path = converted_pdf_paths[0]
        else:
            merged_pdf_path = utils.merge_pdf(converted_pdf_paths)

        # Format the pdf
        formatted_path = formatter.format_pdf(merged_pdf_path, config)
        
        # Rename the file
        renamed_filename = utils.rename_file(
            formatted_path, 
            phone=config['phone'],
            quantity=config['quantity'],
            paper_size=config['paper_size'],
            color_mode=config['color_mode'],
            duplex=config['simplex']
        )
        
        final_output_path = utils.move_and_rename(formatted_path, renamed_filename)
        page_count = utils.get_page_count(final_output_path)
        # Cost Calc
        cost = utils.calculate_cost(page_count, config['color_mode'], config['simplex'], config['quantity'])

        return JsonResponse({
            'success': True,
            'preview_url': f"/media/processed/{final_output_path}",
            'page_count': page_count,
            'renamed_filename': renamed_filename,
            'cost': str(cost)
        })
        
        print("POST data:", request.POST)

    except Exception as ex:
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(ex)}, status=500)
            
            
@csrf_exempt
@require_POST
def submit_order(request):
    data = json.loads(request.body)

    name = data.get('name')
    email = data.get('email')
    phone = data.get('phone')
    total_cost = data.get('total_cost')

    PrintOrder.objects.create(
        name=name,
        email=email,
        phone_number=phone,
        total_cost=total_cost
    )
    
    return JsonResponse({'success': True, 'message': 'Order Submitted!'})

def upload_form_view(request):
    return render(request, "app.html")