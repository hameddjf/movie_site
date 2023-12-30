import httpx
import asyncio
from datetime import datetime

from asgiref.sync import sync_to_async
from django.utils.text import slugify
from django.conf import settings
from django.utils.dateparse import parse_date

from .models import Movie, Director, Actor, Genre

async def fetch_movie_data(movie_title):
    async with httpx.AsyncClient() as client:
        response = await client.get(f'http://www.omdbapi.com/?t={movie_title}&apikey={settings.OMDB_API_KEY}')
        movie_data = response.json()
        return movie_data


# تابعی برای تبدیل تاریخ از فرمت '31 Mar 1999' به 'YYYY-MM-DD'
def format_date(date_string):
    try:
        date_object = datetime.strptime(date_string, '%d %b %Y')
        return date_object.strftime('%Y-%m-%d')
    except ValueError:
        return None

def truncate_string(value, max_length):
    if value and len(value) > max_length:
        return value[:max_length]
    return value

@sync_to_async
def save_movie_to_db(movie_title, movie_data):
    movie_title = truncate_string(movie_title, 300)
    movie_slug = slugify(movie_title)
    release_date_string = movie_data.get('Released', 'N/A')
    formatted_release_date = format_date(release_date_string) if release_date_string != 'N/A' else None

    # فرض می‌کنیم که 'Director' در movie_data یک نام کامل است.
    director_name = movie_data.get('Director', '').split(',')[0].strip()
    director, _ = Director.objects.get_or_create(full_name=director_name)

    # ایجاد یا دریافت شیء Movie
    movie, created = Movie.objects.get_or_create(
        title=movie_title,
        defaults={
            'slug': movie_slug,
            'release_date': formatted_release_date,
            'description': truncate_string(movie_data.get('Plot', ''), 1000),
            'imdb_id': movie_data.get('imdbID'),
            'imdb_rating': movie_data.get('imdbRating'),
            'duration': movie_data.get('Runtime', '').split(' ')[0],  # Assuming format is "123 min"
            'director': director,
        }
    )

    # تنظیم پوستر پس از ایجاد یا دریافت شی Movie
    poster_url = movie_data.get('Poster', '')
    if poster_url and poster_url != 'N/A':
        movie.poster = poster_url
    else:
        movie.poster = None  # یا مقدار پیش‌فرض

    if created:
        genres = movie_data.get('Genre', '').split(', ')
        for genre_name in genres:
            genre, _ = Genre.objects.get_or_create(name=genre_name)
            movie.genres.add(genre)

        actors = movie_data.get('Actors', '').split(', ')
        for actor_name in actors:
            actor, _ = Actor.objects.get_or_create(name=actor_name)
            movie.actor.add(actor)  # اینجا باید 'actors' باشد نه 'actor'

    movie.save()
    return movie

async def save_movie_details(movie_title):
    movie_data = await fetch_movie_data(movie_title)
    if movie_data.get('Response') == 'True':
        await save_movie_to_db(movie_title, movie_data)
        print(f"Information for movie '{movie_title}' saved successfully.")
    else:
        print(f"Error: {movie_data.get('Error')}")