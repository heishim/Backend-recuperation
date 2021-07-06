
#from subprocess import Popen
from os import popen
from os import remove, rmdir, listdir, chdir, sep, walk
import os

from shutil import unpack_archive
import zipfile 


#%% Version fonction 

def execution_fg(nomRSS):
    """
    Fonction permettant d'éxécuter la fonction de groupage
    
    Entrée : nom complet du fichier RSS (c'est-à-dire chemin inclus), avec un petit r' ' encadrant le chemin
                                         
    Sortie : pas de sortie
    """
    execut = "wine 'groupeur V2020'/BIN/fg1920.exe " + nomRSS +" 'groupeur V2020'/TABLES/" " 1" " 'groupeur V2020'/um.txt" " media/nouveau" 
    #execut = r'"C:\Users\Heishim\tuto_django_vuejs_axios\Django rest framework\groupeur V2020\BIN\fg1920.exe" ' + nomRSS + r' "C:\Users\Heishim\tuto_django_vuejs_axios\Django rest framework\groupeur V2020\TABLES/" 1 "C:\Users\Heishim\tuto_django_vuejs_axios\Django rest framework\groupeur V2020\um.txt" "C:\Users\Heishim\tuto_django_vuejs_axios\Django rest framework\media\nouveau" '
    
    #popen([r"cmd"])
    popen(execut)

#execution_fg("../media/media/test.txt")

def clean(dossier):
    for filename in listdir(dossier) :
        remove(dossier + "/" + filename)
        
def clean_action():
    clean("media/nouveau")
    clean("media/media")
    #clean(r'C:\Users\Heishim\tuto_django_vuejs_axios\Django rest framework\media\nouveau')
    #clean(r'C:\Users\Heishim\tuto_django_vuejs_axios\Django rest framework\media\media')


def dossier_zip(dossier):
    my_zip = zipfile.ZipFile("media/media/RSS_GROUPE.zip",'w', compression=zipfile.ZIP_DEFLATED)
    for filename in listdir(dossier) :
        my_zip.write(dossier+"/"+filename)
    my_zip.close()
#dossier_zip("../media/nouveau")

def conversion(a,b) : #a=dossier d'entree b=dossier de sortie
    chdir(a) #ouvre le dossier entree
    for subdir, dirs, files in walk(a):
        for file in files:
            filepath = subdir + sep + file
            if filepath.endswith(".rds"): #cherche les fichiers rds
                with open(file,"r") as rds : #ouvre le fichier en lecture
                    source= rds.read()
    chdir(b) #ouvre le dossier sortie pour créer le fichier
    txt= open("transfo_rum.txt","a")
    txt.write(source)
    txt.close()
    
    
#conversion("../media", "../media")

def dossier_zip2(dossier,sortie):
    my_zip = zipfile.ZipFile(sortie,'w', compression=zipfile.ZIP_DEFLATED)
    for filename in listdir(dossier) :
        my_zip.write(dossier+"/"+filename)
    my_zip.close()

def is_list_empty(list):
    if len(list) == 0:
        return True
    return False


def conversion(a,b) : #a=dossier d'entree b=dossier de sortie
    #os.chdir(a) #ouvre le dossier entree
    resultat = []
    for filename in os.listdir(a) :
        resultat.append(filename)
    for subdir, dirs, files in os.walk(a):
        for file in files:
            #print os.path.join(subdir, file)
            filepath = subdir + os.sep + file
            if filepath.endswith(".grp"): #cherche les fichiers rds
                with open(file,"r") as grp : #ouvre le fichier en lecture
                    source= grp.read()
                    txt= open("transfo_rum.txt","a")
                    txt.write(source)
                    txt.close()
    #os.chdir(b) #ouvre le dossier sortie pour créer le fichier
    return resultat

#print('rr')
#print(conversion("media/nouveau", "media/nouveau"))






