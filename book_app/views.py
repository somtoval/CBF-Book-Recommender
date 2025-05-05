# # views.py
# from django.shortcuts import render
# from django.http import JsonResponse
# from django.core.paginator import Paginator
# from .models import Book

# def book_list(request):
#     book_list = Book.objects.all().order_by('-created_at')
#     # Show 9 books per page
#     paginator = Paginator(book_list, 6)
    
#     page = request.GET.get('page', 1)
#     try:
#         book_list = paginator.page(page)
#     except:
#         book_list = paginator.page(1)
    
#     return render(request, 'index_old.html', {'book_list': book_list})

# def get_recommendations(request, book_id):
#     recommendations = Book.get_recommendations(book_id)
#     data = [{
#         'id': rec['book'].id,
#         'title': rec['book'].title,
#         'author': rec['book'].author,
#         'description': rec['book'].description,
#         'cover_image': rec['book'].cover_image.url if rec['book'].cover_image else None,
#         'similarity': f"{rec['similarity_score']:.2f}"
#     } for rec in recommendations]
#     return JsonResponse({'recommendations': data})


from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Book

def book_list(request):
    # Get search query if it exists
    search_query = request.GET.get('search', '')
    category = request.GET.get('category', '')
    
    # Start with all books
    queryset = Book.objects.all().order_by('-created_at')
    
    # Apply search filter if provided
    if search_query:
        queryset = queryset.filter(
            Q(title__icontains=search_query) | 
            Q(author__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    # Apply category filter if provided
    if category:
        queryset = queryset.filter(category=category)
    
    # Get all unique categories for the category filter UI
    categories = Book.objects.values_list('category', flat=True).distinct()
    categories = [cat for cat in categories if cat]  # Filter out None/empty values
    
    # Set up pagination - 6 books per page
    paginator = Paginator(queryset, 6)
    page = request.GET.get('page', 1)
    
    try:
        books = paginator.page(page)
    except:
        books = paginator.page(1)
    
    context = {
        'books': books,
        'categories': categories,
    }
    
    return render(request, 'index_old.html', context)

def get_recommendations(request, book_id):
    """
    API endpoint to get book recommendations
    """
    try:
        # Get recommendations from the Book model method
        recommendations = Book.get_recommendations(book_id, num_recommendations=3)
        
        # Format the recommendations for JSON response
        data = [{
            'id': rec['book'].id,
            'title': rec['book'].title,
            'author': rec['book'].author,
            'description': rec['book'].description,
            'cover_image': rec['book'].cover_image.url if rec['book'].cover_image else None,
            'category': rec['book'].category if hasattr(rec['book'], 'category') else None,
            'similarity': rec['similarity_score']
        } for rec in recommendations]
        
        return JsonResponse({'recommendations': data})
    
    except Exception as e:
        # Return error message if something goes wrong
        return JsonResponse({'error': str(e)}, status=400)

def add_book(request):
    """
    View for adding a new book (form handling)
    """
    if request.method == 'POST':
        # Process form data
        title = request.POST.get('title')
        author = request.POST.get('author')
        description = request.POST.get('description')
        category = request.POST.get('category')
        cover_image = request.FILES.get('cover_image')
        
        if title and author and description:
            # Create new book
            book = Book(
                title=title,
                author=author,
                description=description,
                category=category,
                cover_image=cover_image
            )
            book.save()
            
            # Redirect to book list
            return redirect('book_list')
    
    # Get all categories for the dropdown
    categories = Book.objects.values_list('category', flat=True).distinct()
    categories = [cat for cat in categories if cat]
    
    return render(request, 'add_book.html', {'categories': categories})