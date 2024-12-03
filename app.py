from flask import Flask, render_template, request, redirect, url_for, jsonify
from pymongo import MongoClient
from models import Book
from dotenv import load_dotenv
import requests
from collections import Counter
import json
import os
# Load environment variables from .env file
load_dotenv()
app = Flask(__name__)
# MongoDB configuration using the MONGO_URI from the .env file
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client.library
collection = db.books
# Google Books API configuration using the API_KEY from the .env file
API_KEY = os.getenv('GOOGLE_BOOKS_API_KEY')
@app.route('/')
def index():
    books = list(collection.find())

    # Fetch unique values for each filter
    genres = list(collection.distinct('genre'))
    authors = list(collection.distinct('author'))
    chelsey_statuses = list(collection.distinct('chelsey_status'))
    jenny_statuses = list(collection.distinct('jenny_status'))

    return render_template('index.html', books=books, genres=genres, authors=authors, chelsey_statuses=chelsey_statuses, jenny_statuses=jenny_statuses)
@app.route('/add', methods=['POST'])
def add_book():
    title = request.form['title']
    author = request.form['author']
    genre = request.form['genre']
    chelsey_status = request.form.get('chelsey_status', 'Unread')
    jenny_status = request.form.get('jenny_status', 'Unread')
    # Insert the book into MongoDB
    book = Book(title, author, genre, chelsey_status, jenny_status)
    collection.insert_one(book.to_dict())
    return redirect(url_for('index'))
@app.route('/delete/<string:title>')
def delete_book(title):
    collection.delete_one({"title": title})
    return redirect(url_for('index'))
@app.route('/update/<string:title>', methods=['POST'])
def update_book(title):
    chelsey_status = request.form['chelsey_status']
    jenny_status = request.form['jenny_status']
    collection.update_one(
        {"title": title},
        {"$set": {"chelsey_status": chelsey_status, "jenny_status": jenny_status}}
    )
    return redirect(url_for('index'))
@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    books = []
    
    if query:
        # Call Google Books API to get search results
        result = search_books(query)
        if result:
            books = result.get('items', [])
    
    return render_template('search.html', books=books)
@app.route('/add_from_search', methods=['POST'])
def add_book_from_search():
    title = request.form['title']
    author = request.form['author']
    genre = request.form['genre']
    cover_url = request.form['cover_url']
    description = request.form.get('description', 'No Description')
    published_date = request.form.get('published_date', 'Unknown')
    page_count = request.form.get('page_count', 0)
    average_rating = request.form.get('average_rating', 'N/A')
    rating_count = request.form.get('rating_count', 0)
    maturity_rating = request.form.get('maturity_rating', 'Unknown')
    chelsey_status = request.form.get('chelsey_status', 'Unread')
    jenny_status = request.form.get('jenny_status', 'Unread')
    # Parse ISBN numbers
    isbn_data = request.form.get('isbn_data', '[]')  # Expect a JSON string of ISBN data
    isbn_list = eval(isbn_data) if isbn_data else []
    # Create book dictionary
    book = {
        "title": title,
        "author": author,
        "genre": genre,
        "cover_url": cover_url,
        "description": description,
        "published_date": published_date,
        "page_count": int(page_count),
        "average_rating": average_rating,
        "rating_count": int(rating_count),
        "maturity_rating": maturity_rating,
        "isbn_numbers": isbn_list,
        "chelsey_status": chelsey_status,
        "jenny_status": jenny_status
    }
    # Insert the book into MongoDB
    collection.insert_one(book)
    return redirect(url_for('index'))
@app.route('/data/<string:attribute>')
def data_by_attribute(attribute):
    books = list(collection.find())
    
    if attribute == "genre":
        values = [genre for book in books for genre in book.get('genre', '').split(', ')]
    elif attribute == "author":
        values = [book.get('author', 'Unknown') for book in books]
    elif attribute == "chelsey_status":
        values = [book.get('chelsey_status', 'Unread') for book in books]
    elif attribute == "jenny_status":
        values = [book.get('jenny_status', 'Unread') for book in books]
    else:
        return jsonify({"error": "Invalid attribute"}), 400
    
    from collections import Counter
    aggregated_data = Counter(values)
    return jsonify(aggregated_data)
def search_books(query):
    url = f'https://www.googleapis.com/books/v1/volumes?q={query}&key={API_KEY}'
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else:
        return None
if __name__ == '__main__':
    app.run(debug=True)