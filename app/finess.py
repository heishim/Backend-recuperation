import pandas as pd
import numpy as np
import csv
import os
import shutil
from django.contrib.auth.models import User

#création du dictionnaire contenant nom d'utilisateur et finess associés
liste_utilisateurs={}

#appel du fichier csv contenant les noms d'établissements et les finess avec en 1ère colonne le finess et en 2ème colonne la raison sociale de l'étab
fichier="media/liste_etab_2021.csv"

#sélection des CH par rapport à une région choisie
def selection_CH(region) :
    etab=[]     #initialisation de la liste étab
    with open(fichier,"r") as f :
        reader=csv.reader(f, delimiter=";")
        for row in reader :     #récupération des noms étab par rapport à la région
            if row[5]==region :
                etab.append(row[1])     
    return etab

#fonction qui transforme le rds en txt
def conversion(a,b) : #a=dossier d'entree b=dossier de sortie
    os.chdir(a) #ouvre le dossier entree
    for subdir, dirs, files in os.walk(a):
        for file in files:
            #print os.path.join(subdir, file)
            filepath = subdir + os.sep + file
            if filepath.endswith(".rds"): #cherche les fichiers rds
                with open(file,"r") as rds : #ouvre le fichier en lecture
                    source= rds.read()
    os.chdir(b) #ouvre le dossier sortie pour créer le fichier
    txt= open("rum.txt","a")
    txt.write(source)
    txt.close()

#fonction qui déplace un fichier
def deplacer(a,b): # entrer chemin + nom du fichier pour a et b
    source=a
    dest=b
    shutil.move(a,b) #deplacer le fichier  


#fonction qui lit le fichier log et retourne les erreurs
def lecture_log(a) : #a=dossier d'entree
    os.chdir(a) #ouvre le dossier entree
    for subdir, dirs, files in os.walk(a):
        for file in files:
            filepath = subdir + os.sep + file
            if filepath.endswith(".log"): #cherche les fichiers log
                with open(file,"r") as log : #ouvre le fichier en lecture
                    for line in log :
                        if "Nombre d'enregistrements ayant un format non traité" in line :
                            mots = line.split()
                            nontrait = mots[8]
                            if nontrait=="0" :
                                pass
                            else :
                                return str(line)
                        elif "Nombre de RUM en erreur (CM 90)" in line :
                            mots = line.split()
                            rum = mots[8]
                            if rum=="0" :
                                pass
                            else :
                                return str(line)
                        elif "Nombre de RSS en erreur" in line :
                            mots = line.split()
                            rss = mots[6]
                            if rss=="0" :
                                pass
                            else :
                                return str(line)
                    if nontrait=="0" and rum=="0" and rss=="0" :
                        return "Aucune erreur"


#création de la liste des étabs
def liste_etab(fichier) :
    liste_etab=[]
    with open(fichier,"r") as f :
        reader=pd.read_csv(fichier, sep=";")
        liste_etab = reader["raison_sociale"].tolist()
    return liste_etab

#import du finess et de l'étab associé dans un dictionnaire
def import_ref(fichier) :
    finess_etab={}
    with open(fichier,"r") as f :
        reader=csv.reader(f, delimiter=";")
        for row in reader :
            finess_etab[row[1]]=row[0]
    return finess_etab

#écriture du dictionnaire dans un csv
def write_dict(dico) :
    with open("media/liste_utilisateurs.csv","w") as f :
        writer=csv.writer(f, delimiter=";",lineterminator="\r")
        for k, v in dico.items() :
            v=",".join(v)
            writer.writerow([k,v])

#ajout des utilisateurs associés au finess
def add_user_finess(user, *args) : #*args permet de rentrer plusieurs noms d'établissement
    test=import_ref("media/liste_etab_2021.csv")
    liste_utilisateurs={}
    with open("media/liste_utilisateurs.csv","r") as f :
        reader=csv.reader(f, delimiter=";")
        for row in reader :
            liste=row[1].split(',')
            liste_utilisateurs[row[0]]=liste
    for etab in args :
        finess=test[etab]
        if user in liste_utilisateurs :
            if finess in liste_utilisateurs[user] :
                pass
            else :
                liste_utilisateurs[user].append(test[etab])
        else :
            liste_utilisateurs[user]=[test[etab]]
    write_dict(liste_utilisateurs)
    return liste_utilisateurs

def test_finess (fichier,user): #fichier=fichier rss testé/nom utilisateur
    #lecture du ficher RSS et récupération du finess
    fichier= open(fichier,"r")
    for i in range(1):  #lecture de la première ligne
        ligne=fichier.readline()
        finess=ligne[0:9] #récupération du finess du fichier groupé
        liste_utilisateurs={}
        with open("media/liste_utilisateurs.csv","r") as f :
            reader=csv.reader(f, delimiter=";")
            for row in reader :
                liste=row[1].split(',')
                liste_utilisateurs[row[0]]=liste
    liste_finess= liste_utilisateurs[user]   
    return finess in liste_finess #comparaison du finess avec la liste des finess autorisés

#suppression numéros finess associés à un utilisateur
def sup_user_finess(user, *args) : #*args pemet de rentrer plusieurs noms d'établissement
    test=import_ref("media/liste_etab_2021.csv") #appel de la liste étab associée au finess
    liste_utilisateurs={}
    with open("media/liste_utilisateurs.csv","r") as f :
        reader=csv.reader(f, delimiter=";")
        for row in reader :
            liste=row[1].split(',')
            liste_utilisateurs[row[0]]=liste
    for etab in args :
        finess=test[etab]
        if user in liste_utilisateurs :
            if finess in liste_utilisateurs[user] :
                liste=liste_utilisateurs[user]
                liste.remove(finess)
                liste_utilisateurs[user]=liste
        else :
            pass
    write_dict(liste_utilisateurs)
    return liste_utilisateurs

#suppression totale d'un utilisateur
def sup_user(user) :
    liste_utilisateurs={}
    with open("media/liste_utilisateurs.csv","r") as f :
        reader=csv.reader(f, delimiter=";")
        for row in reader :
            liste=row[1].split(',')
            liste_utilisateurs[row[0]]=liste
    if user in liste_utilisateurs :
        liste_utilisateurs.pop(user)
    else :
        pass
    write_dict(liste_utilisateurs)
    return liste_utilisateurs



def liste_user_finess():
    liste_utilisateurs={}
    with open("media/liste_utilisateurs.csv","r") as f :
        reader=csv.reader(f, delimiter=";")
        for row in reader :
            liste=row[1].split(',')
            liste_utilisateurs[row[0]]=liste
    return liste_utilisateurs



#Tester si le rss d'entrée est groupé ou non
def test_rss_groupe (fichier):
    #lecture du ficher RSS et récupération du finess
    fichier= open(fichier,"r")
    for i in range(1):  #lecture de la première ligne
        ligne=fichier.readline()
        test=ligne[4:5]
    #test si 
    return test in('M','C','O','K','Z')





def conversion(a,b):
	for subdir, dirs, files in os.walk(a):
		for file in files:
			filepath = a + os.sep + file
			
			if filepath.endswith(".grp"): #cherche les fichiers rds
				with open(filepath,"r") as f : #ouvre le fichier en lecture
					source= f.read()
	
	nouveauFichier = b + os.sep + "transfo_rum.txt"
	txt = open(nouveauFichier,"a")
	txt.write(source)
	txt.close()

def conversion2(a,b):
	for subdir, dirs, files in os.walk(a):
		for file in files:
			filepath = a + os.sep + file
			
			if filepath.endswith(".grp"): #cherche les fichiers rds
				with open(filepath,"r") as f : #ouvre le fichier en lecture
					source= f.read()
	
	nouveauFichier = b + os.sep + "ancien_grp.txt"
	txt = open(nouveauFichier,"a")
	txt.write(source)
	txt.close()

######## Fonction import numéros RSS ######

def liste_rss() :
    fichier=pd.read_csv(r"\rum.txt.grp", sep=";")
    num_rss=fichier["num_rss"].tolist()
    return num_rss    					












        
