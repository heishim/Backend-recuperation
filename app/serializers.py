from rest_framework import serializers
from . models import Fichier
from . models import Name, Finess
from django.contrib.auth.models import User

class FichierSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Fichier
        fields = '__all__'
        #fields = ("title","commentaire")

class NameSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Name
        fields = '__all__'

class FinessSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Finess
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta: 
        model = User
        fields = '__all__'


        

