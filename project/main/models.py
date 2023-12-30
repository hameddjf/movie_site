from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation

import datetime

from comment.models import Comment
from star_ratings.models import Rating

class ReviewManager(models.Manager):
    def get_approved(self):
        return self.get_queryset().filter(approved=True)

class MovieManager(models.Manager):
    def get_by_genre(self, genre_name):
        return self.get_queryset().filter(genre__name=genre_name)



class Genre(models.Model):
    name             = models.CharField(_("نام"), max_length=50, unique=True)

    class Meta:
        verbose_name = _("ژانر")
        verbose_name_plural = _("ژانرها")

    def __str__(self):
        return self.name

class Actor(models.Model):
    name             = models.CharField(_("نام بازیگر"), max_length=500, unique=True)
    poster           = models.ImageField(_("عکس بازیگر"), upload_to='movie_posters/Actor', blank=True, null=True)
    
    
    class Meta:
        verbose_name = _("بازیگر")
        verbose_name_plural = _("بازیگران")
        
    def __str__(self):
        return self.name

class Director(models.Model):
    full_name        = models.CharField(_("نام کارگردان"), max_length=500, unique=True)
    
    class Meta:
        verbose_name = _("کارگردان")
        verbose_name_plural = _("کارگردان ها")
        
    def __str__(self):
        return self.full_name


class IpAddress(models.Model):
    ip_address       = models.GenericIPAddressField(_("آدرس آیپی"), protocol="both", unpack_ipv4=False)


class Movie(models.Model):
    title            = models.CharField(_("عنوان"), max_length=300, unique=True)
    slug             = models.SlugField(max_length=500, unique=True,
                             verbose_name="آدرس فیلم", blank=True, null=True)

    release_date     = models.DateField(_("تاریخ اکران فیلم"), default=datetime.date.today)
    created_at       = models.DateTimeField(_("ایجاد شده در"), auto_now_add=True)
    updated_at       = models.DateTimeField(_("بروزرسانی شده در"), auto_now=True)

    director         = models.ForeignKey(Director, on_delete=models.CASCADE,
                        verbose_name=_("کارگردان") , related_name='movies_directed', null=True, blank=True  )

    actor            = models.ManyToManyField(Actor,verbose_name=_("بازیگران"),
                        related_name='movies_actor', blank=True )

    description      = models.TextField(_("توضیحات"), blank=True)

    imdb_id          = models.CharField(max_length=9, blank=True, null=True, unique=True, verbose_name='IMDb ID')
    imdb_rating      = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True, verbose_name='IMDb Rating')

    genres           = models.ManyToManyField(Genre, verbose_name=_("ژانر"))
    # rating           = models.FloatField(_("امتیاز"), blank=True, null=True)
    duration         = models.PositiveIntegerField(_("مدت زمان"), help_text=_("مدت زمان فیلم به دقیقه") , null=True, blank=True)
    
    # poster           = models.ImageField(_("پوستر"), upload_to='movie_posters/', blank=True, null=True)
    poster           = models.URLField(_("پوستر"), max_length=500, blank=True, null=True)

    views            = models.PositiveIntegerField(default=0)

    
    objects          = MovieManager()
    comments         = GenericRelation(Comment)
    # rating             = models.ManyToManyField(IpAddress , blank=True , related_name='hits' , verbose_name='بازدیدها') # برای ایجاد رابطه چند به چند بین کاربران یا همون ایپی ها با مقالات
    rating           =  GenericRelation(Rating)
    class Meta:
        verbose_name = _("فیلم")
        verbose_name_plural = _("فیلم‌ها")
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super(Movie, self).save(*args, **kwargs)

    def __str__(self):
        return self.title



class Episode(models.Model):
    movie = models.ForeignKey(
        Movie,  # فرض بر این است که کلاس Movie قبلا تعریف شده است
        related_name='episodes',
        on_delete=models.CASCADE,
        verbose_name=_("سریال")
    )
    season = models.PositiveIntegerField(_("فصل"), default=1)
    title = models.CharField(_("عنوان قسمت"), max_length=500)
    quality = models.CharField(_("کیفیت"), max_length=300, default='HD')
    file = models.FileField(_("فایل"), upload_to='movies/', max_length=255)

    class Meta:
        verbose_name = _("قسمت")
        verbose_name_plural = _("قسمت ها")

    def __str__(self):
        return f"فصل {self.season} - {self.movie.title} - {self.title} - {self.quality}"


class Review(models.Model):
    movie            = models.ForeignKey(Movie, on_delete=models.CASCADE, verbose_name=_("فیلم"), related_name="reviews")
    user             = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("کاربر"))
    content          = models.TextField(_("متن"))
    rating           = models.FloatField(_("امتیاز"), choices=[(i, str(i)) for i in range(1, 6)])  # امتیاز از 1 تا 5
    approved_choices = (
        (True, 'تایید شده'),
        (False, 'تایید نشده')
    )
    approved         = models.BooleanField(_("تایید شده"), choices=approved_choices, default=False)
    created_at       = models.DateTimeField(_("ایجاد شده در"), auto_now_add=True)
    updated_at       = models.DateTimeField(_("بروزرسانی شده در"), auto_now=True)
    
    objects          = ReviewManager()

    class Meta:
        verbose_name = _("نقد و بررسی")
        verbose_name_plural = _("نقدها و بررسی‌ها")

    def __str__(self):
        return f"Review by {self.user.username} on {self.movie.title}"