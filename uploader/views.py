import json
import os
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.db.models import Q
from django.contrib import messages
from .models import Document, Tag

# OCR and PDF Processing Imports
import pdfplumber
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import google.generativeai as genai

# Configure Tesseract Path (for Windows users if not in PATH)
if hasattr(settings, 'TESSERACT_CMD'):
    pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD

# --- Home Page View ---
def home_view(request):
    document_count = Document.objects.count()
    tag_count = Tag.objects.count()
    context = {
        'document_count': document_count,
        'tag_count': tag_count,
    }
    return render(request, 'uploader/home.html', context)

# --- AI Analysis Helper Function ---
def analyze_text_with_gemini(text):
    """
    Analyzes text with Gemini to extract title, summary, and keywords.
    """
    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.5-pro')
        
        prompt = f"""
        Analyze the following document text and return ONLY a valid JSON object with three keys:
        1. "title": A short, descriptive title for the document.
        2. "summary": A concise one-paragraph summary.
        3. "keywords": A list of 5-7 relevant keywords as a Python list of strings.

        Here is the text:
        ---
        {text[:8000]} 
        ---
        """
        
        response = model.generate_content(prompt)
        cleaned_response = response.text.strip().replace('```json', '').replace('```', '').strip()
        result = json.loads(cleaned_response)
        return result

    except Exception as e:
        print(f"An error occurred during Gemini analysis: {e}")
        return None

# --- View for the Dedicated Upload Page ---
def upload_document(request):
    if request.method == 'POST':
        uploaded_file = request.FILES.get('document')
        if uploaded_file:
            document = Document(uploaded_file=uploaded_file)
            document.save()
            
            file_path = document.uploaded_file.path
            file_extension = os.path.splitext(file_path)[1].lower()
            extracted_text = ""

            try:
                if file_extension == '.pdf':
                    with pdfplumber.open(file_path) as pdf:
                        for page in pdf.pages:
                            if page.extract_text():
                                extracted_text += page.extract_text() + "\n"
                    
                    if len(extracted_text.strip()) < 100:
                        extracted_text = ""
                        images = convert_from_path(file_path)
                        for img in images:
                            extracted_text += pytesseract.image_to_string(img) + "\n"

                elif file_extension in ['.png', '.jpg', '.jpeg', '.tiff']:
                    extracted_text = pytesseract.image_to_string(Image.open(file_path))
                
                document.extracted_text = extracted_text

            except Exception as e:
                print(f"Error extracting text: {e}")
            
            if extracted_text:
                analysis_result = analyze_text_with_gemini(extracted_text)
                if analysis_result:
                    document.title = analysis_result.get('title', 'Untitled')
                    document.summary = analysis_result.get('summary', '')
                    document.tags.clear()
                    keyword_list = analysis_result.get('keywords', [])
                    for keyword_name in keyword_list:
                        tag, created = Tag.objects.get_or_create(name=keyword_name.strip())
                        document.tags.add(tag)
            
            document.save()
            messages.success(request, f"Successfully uploaded and analyzed '{document.title}'.")
            return redirect('upload_document')
    
    return render(request, 'uploader/upload_page.html')

# --- View for the Search Page ---
def search_documents(request):
    query = request.GET.get('q', '')
    results = []

    if query:
        results = Document.objects.filter(
            Q(title__icontains=query) |
            Q(summary__icontains=query) |
            Q(extracted_text__icontains=query) |
            Q(tags__name__icontains=query)
        ).distinct()

    context = {'query': query, 'results': results}
    return render(request, 'uploader/search.html', context)

# --- View for the Document Detail Page ---
def document_detail(request, pk):
    document = get_object_or_404(Document, pk=pk)
    context = {'document': document}
    return render(request, 'uploader/document_detail.html', context)

# --- Views for Categories ---
def category_list(request):
    tags = Tag.objects.all().order_by('name')
    context = {
        'tags': tags
    }
    return render(request, 'uploader/categories_list.html', context)

def category_detail(request, tag_name):
    tag = get_object_or_404(Tag, name=tag_name)
    documents = Document.objects.filter(tags=tag)
    context = {
        'tag': tag,
        'documents': documents,
    }
    return render(request, 'uploader/category_detail.html', context)