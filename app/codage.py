import pandas as pd
import numpy as np
import csv
import os
import re #module permettant d'utiliser les expressions régulières
from os import remove, rmdir, listdir, chdir, sep, walk, mkdir, path
from shutil import copytree, copy
from datetime import date, datetime
######## Fonction décomposition ######

#!/usr/local/bin/python
# coding: latin-1

### Les deux lignes au-dessus permettent juste un meilleur encodage des caractères spéciaux (comme é, à) sur Linux ###

## Importation des librairies utilisées

import re #module permettant d'utiliser les expressions régulières

   


#ouverture de la base de données 
def decomposition_rss(nomFichierRss,user,finess,date1):
    ###Cette fonction permet de parcourir un fichier contenant des RSS groupés (document .grp obtenu après application de la fonction de groupage)et de le mettre en forme dans un dataframe.

    #Entrée : 
    #* nomFichierRss : nom + chemin du fichier contenant les RSS groupés. 

    #Sortie :
    #* un dataframe à un format "standard". 1 ligne 1 RUM
   

    #Ouverture des fichiers et tables qui vont nous être utiles pour la suite
    fichierRss = open(nomFichierRss, 'r')
    lignes = fichierRss.readlines()
    nbLignes = len(lignes)

    tableActesClassants = pd.read_csv("media/actes_classants_2020.csv", sep = ';')#changer le chemin
    listeActesClassants = tableActesClassants['code'].tolist()
    

    ##Première étape : récupération de toutes les informations utiles présentes dans le document txt et les mettre dans un data frame 
    
    #Création d'un dataFrame vide que l'on remplit au fur et à mesure
    df = pd.DataFrame(columns = ['finess','CMD','ghm','num_rss','num_admin','num_rum','date_nais','age','sexe','num_um', 'date_entree', 'mode_entree', 'date_sortie','mode_sortie','duree_um',
                                'nb_rum','poids','gesta','ddr','nb_seances','nb_das','nb_actes','dp','dr','igs','confirm','conv_HC','RAAC','contexte','prod_RH',
                                'rescrit','nb_inter_tot','liste_das','liste_actes_classants','liste_actes'])
    
    i = 0


    while i <= nbLignes-1:
        currentLigne = lignes[i]
        dicoTemp = {'finess':'', 'CMD':'','ghm':'', 'num_rss':'', 'num_admin':'', 'num_rum':'','date_nais' : '', 'age':0,'sexe' : '', 'num_um':'','date_entree' : '', 'mode_entree':'','date_sortie':'',
                    'mode_sortie':'', 'duree_um':0,'nb_rum':0, 'poids':0,'gesta':0,'ddr':'','nb_seances':0,'nb_das':0,'nb_actes':0, 'dp':'', 'dr':'', 'igs':0,
                    'confirm':0,'conv_HC':'','RAAC':'','contexte':'','prod_RH':'','rescrit':'','nb_inter_tot':'','liste_das':'','liste_actes_classants':'','liste_actes':''}

            
        if (i == nbLignes):
            break
    

        #On récupère l'ensemble des informations du RUM
        
        dicoTemp['finess'] = currentLigne[15:24]
        dicoTemp['CMD'] = int(currentLigne[2:4])
        dicoTemp['ghm'] = currentLigne[2:8]

        dicoTemp['num_rss'] = currentLigne[27:47]
        dicoTemp['num_admin'] = currentLigne[47:67]
        dicoTemp['num_rum'] = currentLigne[67:77]
        dicoTemp['date_nais'] = currentLigne[77:85]
        dicoTemp['age'] = 2020-int(currentLigne[81:85])
        dicoTemp['sexe'] = int(currentLigne[85:86])

        dicoTemp['num_um'] = currentLigne[86:90]
        dicoTemp['date_entree'] = currentLigne[92:100]
        dicoTemp['mode_entree'] = currentLigne[100:102]
        dicoTemp['date_sortie'] = currentLigne[102:110]
        dicoTemp['mode_sortie'] = currentLigne[110:112]


        dicoTemp['poids'] = currentLigne[117:121]
        dicoTemp['gesta'] = int(currentLigne[121:123])
        dicoTemp['ddr'] = currentLigne[123:131]
        dicoTemp['nb_seances'] = int(currentLigne[131:133])
        dicoTemp['nb_das'] = int(currentLigne[133:135])
        dicoTemp['nb_actes'] = int(currentLigne[137:140])

        dicoTemp['dp'] = currentLigne[140:148]
        dicoTemp['dr'] = currentLigne[148:156]
        dicoTemp['igs'] = currentLigne[156:159]
        dicoTemp['confirm'] = currentLigne[159:160]

        dicoTemp['conv_HC'] = currentLigne[177:178]
        dicoTemp['RAAC'] = currentLigne[178:179]
        dicoTemp['contexte'] = currentLigne[179:180]
        dicoTemp['prod_RH'] = currentLigne[180:181]
        dicoTemp['rescrit'] = currentLigne[181:182]
        dicoTemp['nb_inter_tot'] = currentLigne[182:183]
   

        #Calcul de la durée du RUM
        delta = date(int(currentLigne[106:110]), int(currentLigne[104:106]), int(currentLigne[102:104])) - date(int(currentLigne[96:100]), int(currentLigne[94:96]), int(currentLigne[92:94]))
        dicoTemp['duree_um'] = delta.days


        liste_das = []
        liste_actes_classants = []
        liste_actes = []
        listeDas = []
        ActesClassants = []
        ActesAutres = []

        #DAS
        nbDasRum = int(currentLigne[133:135])

        if nbDasRum != 0:
            for numDas in range(0, nbDasRum):
                positionDas = 192 + numDas*8
                listeDas.append(currentLigne[positionDas:positionDas+8].strip())

        #Actes
        nbActesRum = int(currentLigne[137:140])

        if nbActesRum != 0:
            for numActes in range(0, nbActesRum):
                positionActes = 192 + 8*(nbDasRum + int(currentLigne[135:137]))+29*numActes
                if currentLigne[positionActes+8:positionActes+7+7].strip() in listeActesClassants:
                    ActesClassants.append(currentLigne[positionActes:positionActes+29])

                else : ActesAutres.append(currentLigne[positionActes:positionActes+29])


        dicoTemp['liste_das'] = ' '.join(list(set(listeDas)))
        dicoTemp['liste_actes_classants'] = ' '.join(list(set(ActesClassants)))
        dicoTemp['liste_actes'] = ' '.join(list(set(ActesAutres)))

        df = df.append(dicoTemp, ignore_index=True)
        print(i)
        i +=1

    chemin = r"media/user/"+user+r"/"+finess+r"/"+date1+r"/"+r"rss_decompo.csv"
    df.to_csv(chemin)
    return (df)


#print(decomposition_rss("media/user/"+"Altao"+'/'+'930110051'+'/'+'30_06_2021'+'/ancien_grp.txt','Altao','930110051','30_06_2021'))
######## Fonction import numéros RSS ######

def liste_rss(user,finess,date1) :
    fichier=pd.read_csv(r"media/user/"+user+r"/"+finess+r"/"+date1+r"/"+r"rss_decompo.csv", sep=",")
    num_rss=fichier["num_rss"].tolist()
    return num_rss   

######## Fonction import numéros RSS ######

def liste_actes() :
    fichier=pd.read_csv("media/actes_2021.csv", sep=";")
    actes=fichier["acte"].tolist()
    return actes

def liste_das() :
    list_das = []
    fichier=pd.read_csv("media/CIM10_2021.csv", sep=";")
    das=fichier["diag"].tolist()
    libelle=fichier["libelle"].tolist()
    for i in range (len(das)):
        list_das.append(das[i]+" - "+libelle[i])
    return list_das




######### Fonction qui renvoie les libellés des diags #######

def libelle_diag() :
    diag={}
    with open("media/CIM10_2021.csv") as f :
        reader=csv.reader(f, delimiter=";")
        for row in reader :
              diag[row[0].replace(" ","")]=row[1]
        return diag

######### Fonction qui renvoie les libellés des actes #######

def libelle_actes() :
    actes={}
    with open("media/actes_2021.csv") as f :
        reader=csv.reader(f, delimiter=";")
        for row in reader :
              actes[row[0].replace(" ","")]=row[1]
        return actes




####### Import d'un rss dans un dictionnaire pour infos administratives(recherche) ########

def info_rss(rss,user,finess,date1) :    
    decompo=pd.read_csv(r"media/user/"+user+r"/"+finess+r"/"+date1+r"/"+r"rss_decompo.csv", index_col=0, converters={"num_rss":str}) #index_col permet d'ignorer la colonne 0, converters permet de convertir un entier en chaîne de caractères
    liste_rss={}
    l=0
    for i in decompo['num_rss'] :
        if rss in i :
            for x in decompo :
                liste_rss[x]=decompo.loc[decompo.index[l],x]
        l=l+1
    return liste_rss


####### Import d'un rum dans un dictionnaire pour modifications (recherche) ########
def info_rum(rss,user,finess,date1) :
    diag=libelle_diag()
    actes=libelle_actes()
    decompo=pd.read_csv(r"media/user/"+user+r"/"+finess+r"/"+date1+r"/"+r"rss_decompo.csv", index_col=0, converters={"num_rss":str}) #index_col permet d'ignorer la colonne 0, converters permet de convertir un entier en chaîne de caractères
    dico_rss={}
    l=0
    rum=0
    for num in decompo['num_rss'] :
        if rss in num :
            dico_rum={}
            for x in decompo :
                dico_rum[x]=decompo.loc[decompo.index[l],x] #va chercher les noms de colonnes comme clé et les met dans un dictionnaire

            #ajout du libelle DP
            dico_dp={}
            code_dp=dico_rum["dp"].replace(" ","")
            libelle_dp=diag[code_dp]
            dico_dp[code_dp]=libelle_dp
            dico_rum['dp']=dico_dp

            #découpage des das en liste
            dico_das={}
            liste_das=str(dico_rum['liste_das']).split()
            dico_rum['liste_das']=liste_das
            #ajout des libelle DAS
            for code in liste_das :
                code_das=code
                if code_das in diag :
                    libelle_das=diag[code_das]
                    dico_das[code_das]=libelle_das
                else :
                    pass
            dico_rum['liste_das']=dico_das

            
            #découpage des actes en liste
            dico_acte={}
            liste_acte=str(dico_rum['liste_actes']).split()
            i=0
            while i <=(len(liste_acte )-1):
                if len(liste_acte[i])<10 :
                    del liste_acte[i]
                i=i+1
            while '0' in liste_acte :
                del liste_acte[liste_acte.index('0')]
            #découpage pour ne récupérer que le code acte
            i=0
            while i <=(len(liste_acte)-1) :
                code=liste_acte[i]
                code=code[8:15]
                liste_acte[i]=code
                i=i+1

            #libellé actes
            for code in liste_acte :
                code_acte=code
                if code_acte in actes :
                    libelle_acte=actes[code_acte]
                    dico_acte[code_acte]=libelle_acte
                else :
                    pass
                
            dico_rum['liste_actes']=dico_acte
            

            dico_rss[rum]=dico_rum
            rum=rum+1
        l=l+1
    return dico_rss

#print(info_rum('998541','Altao','930110051','30_06_2021'))


def test(username,finess) :
    now = datetime.now()
    if not path.exists("../media/user/"+username):
        mkdir('../media/user/'+username)
        mkdir("../media/user/"+username+'/'+finess)
        mkdir("../media/user/"+username+'/'+finess+'/'+now.strftime("%d_%m_%Y"))
        for filename in listdir('../media/nouveau') :
            copy('../media/nouveau/'+filename, '../media/user/'+username+'/'+finess+'/'+now.strftime("%d_%m_%Y")+'/'+filename)
    else :
        if not path.exists("../media/user/"+username+'/'+finess):
            mkdir("../media/user/"+username+'/'+finess)
            mkdir("../media/user/"+username+'/'+finess+'/'+now.strftime("%d_%m_%Y"))
            for filename in listdir('../media/nouveau') :
                copy('../media/nouveau/'+filename, '../media/user/'+username+'/'+finess+'/'+now.strftime("%d_%m_%Y")+'/'+filename)
        else :
            mkdir("../media/user/"+username+'/'+finess+'/'+now.strftime("%d_%m_%Y"))
            for filename in listdir('../media/nouveau') :
                copy('../media/nouveau/'+filename, '../media/user/'+username+'/'+finess+'/'+now.strftime("%d_%m_%Y")+'/'+filename)


######## Fonction ajout das ############

def ajout_das(rss,rum,code) :
    diag=libelle_diag()
    rss=info_rum(rss)
    dico_rum=rss[rum]
    dico_das=dico_rum["liste_das"]
    if code in dico_das :
        pass
    else :
        dico_das[code]=diag[code]
    dico_rum["liste_das"]=dico_das
    rss[rum]=dico_rum
    return rss

def liste_etablissement_codage(user):
    finess = []

    for filename in listdir('media/user/'+user):
        finess.append({'finess' : filename})

    return(finess)

def liste_date_codage(user,finess):
    date = []

    for filename in listdir('media/user/'+user+'/'+finess):
        date.append({'date' : filename})

    return(date)

def liste_file_codage(user,finess,date):
    file = []

    for filename in listdir('media/user/'+user+'/'+finess+'/'+date):
        file.append({'file' : filename})

    return(file)



def test_tocsv():
    df = pd.read_csv('media/actes_reanimation.csv',sep = ',')
    df.to_csv('media/TOCSVTEST.csv')

######## Fonction ajout das ############

def ajout_das(rss,rum,code) :
    diag=libelle_diag()
    rss=info_rum(rss)
    dico_rum=rss[rum]
    dico_das=dico_rum["liste_das"]
    if code in dico_das :
        pass
    else :
        dico_das[code]=diag[code]
    dico_rum["liste_das"]=dico_das
    rss[rum]=dico_rum
    return rss