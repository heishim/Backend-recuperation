#from django.shortcuts import render
#from django.views.generic import TemplateView
#from django.core.files.storage import FileSystemStorage

from django.views.decorators import csrf
from rest_framework import response
from rest_framework.response import Response
from rest_framework import generics
from django.views.decorators.csrf import csrf_exempt
from . models import Fichier
from . serializers import FichierSerializer
from . models import Name
from . serializers import NameSerializer
from . models import Finess
from . serializers import FinessSerializer, UserSerializer
from django.http import JsonResponse
from . ouverture_fg import execution_fg, clean, clean_action, dossier_zip, dossier_zip2, is_list_empty
import time
from rest_framework.permissions import IsAuthenticated
from os import remove, rmdir, listdir, chdir, sep, walk, mkdir, path
from shutil import copytree, copy
import random
from django.contrib.auth.models import User
from . codage import *
from . finess import liste_etab, liste_utilisateurs, conversion2, selection_CH, liste_user_finess, add_user_finess, sup_user_finess, sup_user, test_finess, conversion,test_rss_groupe
import pandas as pd
from . pred_cmd_multi_opti import traitement_cmd_multi_sejour
from datetime import date, datetime




from rest_framework.viewsets import ModelViewSet
from django.http import JsonResponse



class FichierView(generics.ListAPIView):
    queryset = Fichier.objects.all()
    serializer_class = FichierSerializer
    #permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = FichierSerializer(queryset, many=True)
        return Response(serializer.data)

#Affichage des données sous forme d'interface graphique

class FichierViewSet(ModelViewSet):

    queryset = Fichier.objects.all()
    serializer_class = FichierSerializer

class UserViewSet(ModelViewSet):
    #permission_classes = (IsAuthenticated,)
    queryset = User.objects.all()
    serializer_class = UserSerializer

class NameViewSet(ModelViewSet):

    queryset = Name.objects.all()
    serializer_class = NameSerializer

class FinessViewSet(ModelViewSet):
    #permission_classes = (IsAuthenticated,)
    queryset = Finess.objects.all()
    serializer_class = FinessSerializer


#Insere les données dans Fichier
@csrf_exempt
def test(request):
    if request.method == 'POST':
        title1 = request.POST['title']
        #contenu1 = Fichier(request.POST.get('contenu'),request.FILES)
        user1 = request.POST['user']
        Fichier.objects.create(
            title=title1,
            #contenu=request.POST.get('contenu'),
            #contenu = contenu1,
            contenu = request.FILES['contenu'],
            user=user1
    )
    return JsonResponse({"status": 'Success'}) 

#Insere les données dans Name
@csrf_exempt
def test2(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        Name.objects.create(
            name=name
    )
    return JsonResponse({"status": 'Success'})

#Insere les données dans Finess
@csrf_exempt
def test3(request):
    if request.method == 'POST':
        user = request.POST['user']
        #contenu1 = request.POST['contenu']
        finess = request.POST['finess']
        Finess.objects.create(
            user=user,
            finess=finess
    )
    return JsonResponse({"status": 'Success'}) 

def copie_user(username,finess) :
    now = datetime.now()
    if not path.exists("media/user/"+username):
        mkdir('media/user/'+username)
        mkdir("media/user/"+username+'/'+finess)
        mkdir("media/user/"+username+'/'+finess+'/'+now.strftime("%d_%m_%Y"))
        #for filename in listdir('media/nouveau') :
            #copy('media/nouveau/'+filename, 'media/user/'+username+'/'+finess+'/'+now.strftime("%d_%m_%Y")+'/'+filename)
        conversion2("media/nouveau","media/user/"+username+'/'+finess+'/'+now.strftime("%d_%m_%Y"))
    else :
        if not path.exists("media/user/"+username+'/'+finess):
            mkdir("media/user/"+username+'/'+finess)
            mkdir("media/user/"+username+'/'+finess+'/'+now.strftime("%d_%m_%Y"))
            #for filename in listdir('media/nouveau') :
                #copy('media/nouveau/'+filename, 'media/user/'+username+'/'+finess+'/'+now.strftime("%d_%m_%Y")+'/'+filename)
            conversion2("media/nouveau","media/user/"+username+'/'+finess+'/'+now.strftime("%d_%m_%Y"))
        else :
            if not path.exists("media/user/"+username+'/'+finess+'/'+now.strftime("%d_%m_%Y")):
                mkdir("media/user/"+username+'/'+finess+'/'+now.strftime("%d_%m_%Y"))
                #for filename in listdir('media/nouveau') :
                    #copy('media/nouveau/'+filename, 'media/user/'+username+'/'+finess+'/'+now.strftime("%d_%m_%Y")+'/'+filename)
                conversion2("media/nouveau","media/user/"+username+'/'+finess+'/'+now.strftime("%d_%m_%Y"))
            else :
                conversion2("media/nouveau","media/user/"+username+'/'+finess+'/'+now.strftime("%d_%m_%Y"))


@csrf_exempt
def liste_etablissement_codage(request):
    if request.method == 'POST':
        finess = []
        user = request.POST.get('user')
        for filename in listdir('media/user/'+user):
            finess.append(filename)
    return JsonResponse(finess, safe=False)

@csrf_exempt
def liste_date_codage(request):
    date = []
    if request.method == 'POST':
        user = request.POST.get('user')
        finess = request.POST.get('finess')
        for filename in listdir('media/user/'+user+'/'+finess):
            date.append(filename)

    return JsonResponse(date, safe=False)

@csrf_exempt
def liste_file_codage(request):
    file = []
    if request.method == 'POST':
        user = request.POST.get('user')
        finess = request.POST.get('finess')
        date = request.POST.get('date')
        for filename in listdir('media/user/'+user+'/'+finess+'/'+date):
            file.append(filename)

    return JsonResponse(file, safe=False)

@csrf_exempt
#Execution des fichiers, FG, algorithme, suppression.. = coeur de fonctionnalités
def donnee(request):

    now = datetime.now()

    fichiers = []

    if (len(listdir('media/media')) != 0):
        for fichier in Fichier.objects.all():
            for utilisateur in User.objects.all():
                if utilisateur.username == fichier.user :
                    email = utilisateur.email
            fichiers.append({
                'title' : fichier.title,
                'contenu': 'media/'+ str(fichier.contenu),
                'date' : str(fichier.date),
                'user' : fichier.user,
                'email': email,
            })
            name = fichier.title
            user = fichier.user
        chemin_execution = "media/" + str(fichier.contenu)
        if(test_finess(chemin_execution,user)==True): 


            if(test_rss_groupe==True):
                traitement_cmd_multi_sejour(chemin_execution,"media/nouveau")
                time.sleep(120)
            else : 
                execution_fg(chemin_execution)
                time.sleep(15)
                conversion("media/nouveau","media/nouveau")
                time.sleep(10)
                traitement_cmd_multi_sejour("media/nouveau/transfo_rum.txt","media/nouveau")
                time.sleep(120)

            myFile = open("media/nouveau/email-"+user+".txt", "w+")
            myFile.write(email)
            myFile.close()
            time.sleep(0.5)
            dossier_zip("media/nouveau")
            time.sleep(5)
            chemin_execution= open(chemin_execution,"r")
            for i in range(1):  #lecture de la première ligne
                ligne=chemin_execution.readline()
                finess=ligne[0:9] #récupération du finess du fichier groupé
            copy('media/media/RSS_GROUPE.zip', 'media/resultat/'+ user + '_' + finess + '_' + str(random.randint(0,100000)) + '.zip')
            copie_user(user,finess)
            #conversion2("media/user/"+user+'/'+finess+'/'+now.strftime("%d_%m_%Y"),"media/user/"+user+'/'+finess+'/'+now.strftime("%d_%m_%Y"))
            decomposition_rss("media/user/"+user+'/'+finess+'/'+now.strftime("%d_%m_%Y")+'/ancien_grp.txt',user,finess,now.strftime("%d_%m_%Y"))

        else : 
            fichiers.append({
            'title' : "erreur.txt"
        })

    else :
        fichiers.append({
            'title' : "erreur.txt"
        })

    return JsonResponse(fichiers, safe=False)


#renvoi l'user du fichier
def user(request):
    fichiers = []
    for fichier in Fichier.objects.all():
        fichiers.append({
            'user' : fichier.user,
        })
    return JsonResponse(fichiers, safe=False)


#zip de dossier media
def sortie(request):
    fichiers = []
    chemin = "/media/nouveau/"
    for fichier in Fichier.objects.all():
        fichiers.append({
            'id' : fichier.id,
            'contenu': 'media/'+ str(fichier.contenu),
            'chemin' : chemin,
        })
    dossier_zip("media/nouveau")


    return JsonResponse(fichiers[0], safe=False)

#Suppression des donnnees
def delete(request):

    clean_action()
    Fichier.objects.all().delete()
    time.sleep(1)
    fichiers = []
    for fichier in Fichier.objects.all():
        fichiers.append({
            'resultat' : "le fichier id :" + str(fichier.id) + "a bien été supprimé",
        })
    return JsonResponse(fichiers, safe=False)


#supprime les données en 4 minutes
def delete_delay(request) : 
    fichiers = []
    for fichier in Fichier.objects.all():
        fichiers.append({
            'resultat' : "le fichier id :" + str(fichier.id) + "a bien été supprimé",
        })
    time.sleep(240)
    Fichier.objects.all().delete()
    clean_action()
    return JsonResponse(fichiers, safe=False)



#envoi tous les noms de fichiers preésent dans resultat
def resultat(request):
    resultat = []
    for filename in listdir("media/nouveau") :
        resultat.append(filename)
    return JsonResponse(resultat, safe=False)

#supprime le fichier dans resultat
def delete_one(request):
    fichiers = []
    for fichier in Name.objects.all():
        fichiers.append({
            'name' : fichier.name
        })
        name = fichier.name
    Name.objects.all().delete()
    remove("media/resultat/"+ name)
    time.sleep(0.2)
    Name.objects.all().delete()
    return JsonResponse(fichiers, safe=False)

#supprime tous les fichiers present dans resultat
def delete_all(request):
    fichiers = []
    for fichier in Name.objects.all():
        fichiers.append({
            'resultat' : "le fichier id :" + str(fichier.id) + "a bien été supprimé",
        })
    Name.objects.all().delete()
    for filename in listdir('media/resultat') :
        remove('media/resultat' + "/" + filename)
    return JsonResponse(fichiers, safe=False)

#telecharger tous les documents de resultat
def telecharger_all(request):
    dossier_zip2("media/resultat","media/zip/Resultat"+ str(random.randint(0,10000000))+".zip")
    time.sleep(10)
    resultat = []
    for filename in listdir("media/zip") :
        resultat.append(filename)
    return JsonResponse(resultat, safe=False)


#supprime le zip dans le dossier zip
def clean_zip(request):
    time.sleep(5)
    resultat = []
    for filename in listdir('media/zip') :
        remove('media/zip' + "/" + filename)
        resultat.append(filename)
    return JsonResponse(resultat, safe=False)


#retourne le nom de l'user present dans user
def users(request):
    users = []
    for user in User.objects.all():
        users.append({
            'user' : user.username,
        })

    return JsonResponse(users, safe=False)

#renvoi le nom de toutes les régions
def region(request):
    liste_region = ['La Reunion', 'Alsace Champagne Ardenne Lorraine', 'Pays de la Loire', 'Saint Pierre et Miquelon', 'Aquitaine Limousin Poitou Charentes', 'Guadeloupe', 'Ile de France', 'Corse', 'Centre Val de Loire', "Provence Alpes Cote d'Azur", 'Languedoc Roussillon Midi Pyrenees', 'Bourgogne Franche Comte', 'Mayotte', 'Auvergne Rhone Alpes', 'Guyane', 'Nord Pas de Calais Picardie', 'Martinique', 'Normandie', 'Bretagne']
    region = []
    for e in liste_region:
        region.append({
            'region' : e,
        })
    return JsonResponse(region, safe=False)


#renvoi la liste des etablissements en fonction de la region
def etab(request):
    time.sleep(1)
    etab = []
    fichiers = []
    for fichier in Name.objects.all():
        fichiers.append({
            'name' : fichier.name
        })
        name = fichier.name
    

    for e in selection_CH(name):
        etab.append({
            'etab' : e,
        })
    Name.objects.all().delete()
    return JsonResponse(etab, safe=False)


#verifie si la liste est vide ou non et renvoi vrai si vide et faux si non vide
def patienter(request) :
    fichiers = []
    resultat = []
    for fichier in Fichier.objects.all():
        fichiers.append({
            'title' : fichier.title,
            'contenu': 'media/'+ str(fichier.contenu),
            'date' : str(fichier.date),
        })
        time.sleep(0.1)
    if(is_list_empty(fichiers)):
        resultat.append({"vide" : "true"})
        return JsonResponse(resultat, safe=False)
    else :
        resultat.append({"vide" : "false"})
        return JsonResponse(resultat, safe=False)

def attente(request) : 
    time.sleep(0.5)



#envoi la liste des users et finess associées
def dictionnaire(request):
    docs = []

    liste_utilisateurs2 = liste_user_finess()
    for user in liste_utilisateurs2.keys():
            docs.append({
                'user' : user,
                'finess' : liste_utilisateurs2[user]
            })

    return JsonResponse(docs, safe=False)


#ajout finess au document xml
def ajout_finess(request):

    docs = []
    finess2 = []
    for ajout in Finess.objects.all():
        finess2.append({
            'user' : ajout.user,
            'finess' : ajout.finess,
        })
        user = ajout.user
        finess = ajout.finess
        add_user_finess(user,finess)

    docs.append({
        'message' : "ajout effectué"
    })
    Finess.objects.all().delete()

    return JsonResponse(docs, safe=False)



#supprime finess du xml
def sup_finess(request):

    docs = []
    finess2 = []
    for ajout in Finess.objects.all():
        finess2.append({
            'user' : ajout.user,
            'finess' : ajout.finess,
        })
        user = ajout.user
        finess = ajout.finess
        sup_user_finess(user,finess)

    docs.append({
        'message' : "suppression effectuée"
    })
    Finess.objects.all().delete()

    return JsonResponse(docs, safe=False)

#supprime l'utilisateur et ses finess du xml
def supprimer_user(request):

    docs = []
    finess2 = []
    for ajout in Finess.objects.all():
        finess2.append({
            'user' : ajout.user,
            'finess' : ajout.finess,
        })
        user = ajout.user
        sup_user(user)
    docs.append({
        'message' : "user finess delete"
    })
    Finess.objects.all().delete()

    return JsonResponse(docs, safe=False)

#supprime les données dans Finess
def delete_donnee_finess(request):
    docs = []
    docs.append({
        'message' : "user finess delete"
    })
    Finess.objects.all().delete()

    return JsonResponse(docs, safe=False)

@csrf_exempt
def recherche_rss(request):
    reponse = []
    if request.method == 'POST':
        rss = request.POST.get('rss')
        user = request.POST.get('user')
        finess = request.POST.get('finess')
        date = request.POST.get('date')
        liste = info_rss(rss,user,finess,date)
        reponse.append({
            'num_rss': str(liste['num_rss']),
            'age': str(liste['age']),
            'num_admin': str(liste['num_admin']),
            'date_entree': str(liste['date_entree']),
            'date_sortie': str(liste['date_sortie']),
            'sexe': str(liste['sexe']),
            'date_nais': str(liste['date_nais']),
            'num_um': str(liste['num_um']),
            'CMD': str(liste['CMD']),
            'ghm': str(liste['ghm']),         
        })
    return JsonResponse(reponse, safe=False)

@csrf_exempt
def recherche_rum(request):
    reponse = []
    info_carte = []
    das = []
    dp = []
    acte = []
    if request.method == 'POST':
        rss = request.POST.get('rss')
        user = request.POST.get('user')
        finess = request.POST.get('finess')
        date = request.POST.get('date')
        liste = info_rum(rss,user,finess,date)
        #print(liste)
        for key, value in liste.items():
            info_carte.append({
                'num_rum': str(key),
                'date_entree': str(value['date_entree']),
                'date_sortie': str(value['date_sortie']),
                'num_um': str(value['num_um']),
                'CMD': str(value['CMD']),
                'igs': str(value['igs']),
                'dr': str(value['dr']),   
            })
            dp_bis = []
            dp_bis.append({
                'dp': [key for key in value['dp'].keys()][0],
                'libelle': [key for key in value['dp'].values()][0],
            })
            dp.append({
                'dp':dp_bis
            })
            dp_bis = []
            das_bis = []
            for i in range(len(value['liste_das'])):
                das_bis.append({
                    'id':i,
                    'das': [key for key in value['liste_das'].keys()][i],
                    'libelle': [key for key in value['liste_das'].values()][i],
                })
            das.append({
                'das' : das_bis
            })
            das_bis = []
            #print(das[0]['das'][2])
            acte_bis = []
            for i in range(len(value['liste_actes'])):
                acte_bis.append({
                    'id':i,
                    'acte': [key for key in value['liste_actes'].keys()][i],
                    'libelle': [key for key in value['liste_actes'].values()][i],
                })
            acte.append({
                'acte' : acte_bis
            })
            acte_bis = []

            """for num_acte in value['liste_actes']:
                acte.append({
                    'acte':num_acte
                })"""

            reponse.append({
                'info_carte' : info_carte[key],
                'dp' : dp[key],
                'das':das[key],
                'acte':acte[key]
            })
    print(reponse)
    return JsonResponse(reponse, safe=False)


@csrf_exempt
def list_rss(request):
    reponse = liste_rss(request.POST.get('user'),request.POST.get('finess'),request.POST.get('date'))
    return JsonResponse(reponse, safe=False)

@csrf_exempt
def list_das(request):
    reponse = liste_das()

    return JsonResponse(reponse, safe=False)

@csrf_exempt
def list_actes(request):
    reponse = liste_actes()
    return JsonResponse(reponse, safe=False)




    










    


    










