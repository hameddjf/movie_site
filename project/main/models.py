from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation

import datetime
from polymorphic.models import PolymorphicModel

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




class IpAddress(models.Model):
    ip_address       = models.GenericIPAddressField(_("آدرس آیپی"), protocol="both", unpack_ipv4=False)


class Movie(PolymorphicModel):
    # فیلدهای مشترک بین فیلم‌های تک قسمتی و سریال‌های چند قسمتی
    title = models.CharField(_("عنوان"), max_length=300, unique=True)
    slug = models.SlugField(max_length=500, unique=True,
                            verbose_name="آدرس فیلم", blank=True, null=True)
    status = models.BooleanField(_('تاییدیه انتشار'),)
    category = models.ForeignKey('category.category', verbose_name=_("دسته بندی"), blank=False, on_delete=models.CASCADE)
    release_date = models.DateField(_("تاریخ اکران فیلم"), auto_now_add=True)
    created_at = models.DateTimeField(_("ایجاد شده در"), auto_now_add=True)
    updated_at = models.DateTimeField(_("بروزرسانی شده در"), auto_now=True)
    director = models.ManyToManyField("cast.director", verbose_name=_("کارگردان"), blank=True)
    actor = models.ManyToManyField("cast.actor", verbose_name=_("بازیگران"), related_name='movies_actor', blank=True)
    description = models.TextField(_("توضیحات"), blank=True)
    imdb_id = models.CharField(max_length=9, blank=True, null=True, unique=True, verbose_name='IMDb ID')
    imdb_rating = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True, verbose_name='IMDb Rating')
    genres = models.ManyToManyField(Genre, verbose_name=_("ژانر"))
    duration = models.PositiveIntegerField(_("مدت زمان"), help_text=_("مدت زمان فیلم به دقیقه"), null=True, blank=True)
    poster = models.URLField(_("پوستر"), max_length=500, blank=True, null=True)
    views = models.PositiveIntegerField(default=0)
    comments = GenericRelation(Comment)
    rating = GenericRelation(Rating)
    
    objects = MovieManager()  # اطمینان حاصل کنید که MovieManager را تعریف کرده‌اید

    class Meta:
        verbose_name = _("فیلم")
        verbose_name_plural = _("فیلم‌ها")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super(Movie, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

class SingleMovie(Movie):
    release_country = models.CharField(
        _("کشور اکران"),
        max_length=50,
        blank=True,
        null=True
    )
    language = models.CharField(
        _("زبان فیلم"),
        max_length=50,
        blank=True,
        null=True
    )
    class Meta:
        verbose_name = _("فیلم سینمایی")
        verbose_name_plural = _("فیلم سینمایی")
class Series(Movie):
    number_of_seasons = models.PositiveIntegerField(
        _("تعداد فصل‌ها"),
        default=1
    )
    average_episode_duration = models.PositiveIntegerField(
        _("میانگین مدت زمان قسمت‌ها"),
        help_text=_("میانگین مدت زمان هر قسمت به دقیقه"),
        null=True,
        blank=True
    )
    class Meta:
        verbose_name = _("سریال")
        verbose_name_plural = _("سریال‌ها")


class MovieNote(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='notes', verbose_name=_("فیلم"))
    note = models.TextField(_("نکته"), blank=True)
    created_at = models.DateTimeField(_("ایجاد شده در"), auto_now_add=True)
    updated_at = models.DateTimeField(_("بروزرسانی شده در"), auto_now=True)

    class Meta:
        verbose_name = _("نکته فیلم")
        verbose_name_plural = _("نکات فیلم‌ها")

    def __str__(self):
        return f'نکته برای {self.movie.title}: {self.note[:50]}...'

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