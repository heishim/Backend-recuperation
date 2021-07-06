from django.db import models
from django.conf import settings



# Create your models here.

class Fichier(models.Model):

    title = models.CharField(max_length=250)
    contenu = models.FileField(upload_to = 'media')
    user = models.CharField(max_length=250)
    date = models.DateTimeField(auto_now_add=True)


    class Meta: 
        ordering = ['user']

    def __str__(self):
        return self.user

class Name(models.Model):
    name = models.CharField(max_length=250, default="default")
    class Meta: 
        ordering = ['name']
    def __str__(self):
        return self.name

class Finess(models.Model):
    user = models.CharField(max_length=250)
    finess = models.CharField(max_length=250)
    class Meta: 
        ordering = ['user']
    def __str__(self):
        return self.user






        