from django.contrib import admin
from django.utils.html import format_html

from .models import Genre, Actor,Director, Movie, Review ,Episode , IpAddress

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', )
    search_fields = ('name', )

@admin.register(Actor)
class ActorAdmin(admin.ModelAdmin):
    list_display = ('name', )
    search_fields = ('name', )

@admin.register(Director)
class DirectorAdmin(admin.ModelAdmin):
    list_display = ('full_name', )
    search_fields = ('full_name', )

class ReviewInline(admin.TabularInline):
    model = Review
    extra = 0
    fields = ('user', 'content', 'rating', 'approved')
    raw_id_fields = ('user', )  # اگر تعداد کاربران زیاد است، استفاده از raw_id_fields می‌تواند مفید باشد

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('thumbnail', 'title', 'director', 'release_date' )
    list_filter = ('genres', 'release_date' )
    
    search_fields = ('title', 'director__name')
    inlines = (ReviewInline, )
    fieldsets = (
        (None, {
            'fields': ('title', 'slug' , 'director', 'actor', 'description', 'genres', 'poster' , 'imdb_id')
        }),
        ('', {
            # 'classes': ('collapse', ),
            'fields': ('release_date' , 'duration'),
        }),
    )
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('actor', 'genres')  # اضافه کردن 'genres' به 'filter_horizontal'

    actions = []  # اضافه کردن اکشن مورد نظر

    group_fieldsets = True

    def thumbnail(self, obj):
        if obj.poster:
            return format_html('<img src="{}" style="max-width: 100px; max-height: 100px;" />', obj.poster)
        return '-'
    thumbnail.short_description = 'Thumbnail'

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('movie', 'user', 'rating', 'approved', 'created_at')
    list_filter = ('approved', 'rating', 'created_at')
    search_fields = ('movie__title', 'user__username', 'content')
    raw_id_fields = ('user', 'movie')  # استفاده برای بهبود عملکرد با انتخاب‌های زیاد

@admin.register(Episode)
class EpisodeAdmin(admin.ModelAdmin):
    list_display = ('title', 'movie', 'file')
    list_filter = ('movie',)
    search_fields = ('title', 'movie__title')
    ordering = ('movie', 'title')

admin.site.register(IpAddress)