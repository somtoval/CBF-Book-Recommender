from django.db import models
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    description = models.TextField()
    cover_image = models.ImageField(upload_to='book_covers/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    category = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.title} by {self.author}"

    @classmethod
    def get_recommendations(cls, book_id, num_recommendations=2):
        """
        Get book recommendations using TF-IDF based on title and description.
        """
        # Get all books
        books = cls.objects.all()
        
        if not books:
            return []

        # Combine title and description for TF-IDF
        content = [f"{book.title} {book.description} {book.author}" for book in books]
        
        # Create TF-IDF matrix
        tfidf = TfidfVectorizer(stop_words='english')
        tfidf_matrix = tfidf.fit_transform(content)
        
        # Calculate similarity scores
        cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
        
        # Get index of the target book
        idx = None
        for index, book in enumerate(books):
            if book.id == book_id:
                idx = index
                break
                
        if idx is None:
            return []
        
        # Get similarity scores for the target book
        sim_scores = list(enumerate(cosine_sim[idx]))
        
        # Sort books by similarity score
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        
        # Get top N most similar books (excluding the book itself)
        sim_scores = sim_scores[1:num_recommendations + 1]
        
        # Get book indices
        book_indices = [score[0] for score in sim_scores]
        
        # Return recommended books
        recommended_books = []
        for index in book_indices:
            recommended_books.append({
                'book': books[index],
                'similarity_score': sim_scores[book_indices.index(index)][1]
            })
            
        return recommended_books

    def save(self, *args, **kwargs):
        # Clean the text data before saving
        if self.title:
            self.title = self.title.strip()
        if self.description:
            self.description = self.description.strip()
        super().save(*args, **kwargs)