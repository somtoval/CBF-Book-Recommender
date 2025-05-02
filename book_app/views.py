# views.py
from django.shortcuts import render
from django.http import JsonResponse
from django.core.paginator import Paginator
from .models import Book

def book_list(request):
    book_list = Book.objects.all().order_by('-created_at')
    # Show 9 books per page
    paginator = Paginator(book_list, 6)
    
    page = request.GET.get('page', 1)
    try:
        books = paginator.page(page)
    except:
        books = paginator.page(1)
    
    return render(request, 'index.html', {'books': books})

def get_recommendations(request, book_id):
    recommendations = Book.get_recommendations(book_id)
    data = [{
        'id': rec['book'].id,
        'title': rec['book'].title,
        'author': rec['book'].author,
        'description': rec['book'].description,
        'cover_image': rec['book'].cover_image.url if rec['book'].cover_image else None,
        'similarity': f"{rec['similarity_score']:.2f}"
    } for rec in recommendations]
    return JsonResponse({'recommendations': data})