#!/usr/local/bin/python
# coding: latin-1

## Importation des librairies utilis�es

import pandas as pd
import re
from datetime import date, datetime
import pickle
import random

#analyse de la base de donn�es 
def traitement_cmd_multi_sejour(nomFichierRss, dossierSortie):
	"""
	Cette fonction permet de parcourir un fichier contenant des RSS group�s (document .grp obtenu apr�s application de la fonction de groupage) et 
	d'estimer un CMD gr�ce � l'utilisation d'un algorithme de machine learning.
	
	Entr�e : 
	* nomFichierRss : nom + chemin du fichier contenant les RSS group�s. 
	* dossierSortie : nom + chemin du dossier de sortie dans lequel on souhaite avoir le fichier .xlsx contenant les s�jours � r��tudier.
	
	Sortie :
	* un document .xlsx dans le dossier de sortie contenant les s�jours dont la CMD est � �tudier de fa�on plus pr�cise car la CMD pr�dite est diff�rente de la CMD donn�e par la fonction de groupage.
	"""
	
	#Ouverture et pr�paration des fichiers et des tables qui vont nous �tre utiles pour la suite
	fichierRss = open(nomFichierRss, 'r')
	lignes = fichierRss.readlines()
	nbLignes = len(lignes)
       
	tableFiness = pd.read_csv("media/knn_v1/table_finess.csv", sep = ',')

	with open('media/knn_v1/liste_tables_multi_sejour.pkl', 'rb') as f:
	#attention de bien mettre les listes dans cet ordre pr�cis puisque c'est dans cet ordre qu'elles ont �t� enregistr�es
		listeActesClassants = pickle.load(f)
		listeActesOperatoires = pickle.load(f)
		listeActesSurveillance = pickle.load(f)
		listeActesRea = pickle.load(f)

    ##Premi�re �tape : r�cup�ration de toutes les informations utiles pr�sentes dans le document txt et les mettre dans un data frame 
    
	df = pd.DataFrame(columns = ['finess', 'departement_etablissement', 'num_rss', 'CMD', 'age', 'sexe', 'mois_sortie', 'mode_entree', 'mode_sortie', 'duree_tot', 'nb_rum', 'nb_das_tot', 'dp_rum', 'das_tot', 'nb_actes_tot', 'actes_classants', 'nb_actes_operatoires', 'nb_actes_imagerie', 'nb_actes_surveillance', 'nb_actes_rea'])
    
	i = 0
	
	finess = lignes[0][15:24]
    
	while i < nbLignes-1:

		currentLigne = lignes[i]
		dicoTemp = {'finess': finess, 'departement_etablissement':'', 'num_rss':'', 'CMD':'', 'age' : 0, 'sexe' : '', 'mois_sortie' : '', 'mode_entree':8, 'mode_sortie':'', 'duree_tot':'', 'nb_rum':0, 'nb_das_tot':0, 'dp_rum':'', 'das_tot':'', 'nb_actes_tot':0, 'actes_classants':'', 'nb_actes_operatoires':'', 'nb_actes_imagerie':'', 'nb_actes_surveillance':0, 'nb_actes_rea':0}
    	
    	#On ne prend que les lignes pour lesquelles le CMD est valide
		if currentLigne[2:4] != "90":
			compteur = 1
			nextLigne = lignes[i+compteur]

			while int(currentLigne[27:47]) == int(nextLigne[27:47]):
				compteur +=1 #compteur du nombre de ligne appartenant au m�me s�jour
				if ((i+compteur) == nbLignes): 
	   				break
				nextLigne = lignes[i+compteur]

			if compteur !=1:
				lastLigne = lignes[i+compteur-1]
				dicoTemp['departement_etablissement'] = currentLigne[15:17]
				dicoTemp['CMD'] = int(currentLigne[2:4])
    			
				dicoTemp['num_rss'] = int(currentLigne[27:47])
				dicoTemp['age'] = 2020-int(currentLigne[81:85])
				dicoTemp['sexe'] = int(currentLigne[85:86])
				dicoTemp['mois_sortie'] = int(lastLigne[104:106])
    			
				if currentLigne[100:101] != 'N':
					dicoTemp['mode_entree'] = currentLigne[100:101]
				dicoTemp['mode_sortie'] = lastLigne[110:111]
    			
				dicoTemp['nb_rum'] = compteur    			
				
    			#Calcul de la dur�e totale de s�jour
				delta = date(int(lastLigne[106:110]), int(lastLigne[104:106]), int(lastLigne[102:104])) - date(int(currentLigne[106:110]), int(currentLigne[104:106]), int(currentLigne[102:104]))
				dicoTemp['duree_tot'] = delta.days
    			
				listeDp = []
				listeDas = []
				ActesClassants = []
				NbActesOperatoires = 0
				NbActesImagerie = 0
				NbActesSurveillance = 0
				NbActesRea = 0
				
				for j in range(0, compteur):
					ligneRum = lignes[i+j]
	   				#DAS
					nbDasRum = int(ligneRum[133:135])
					dicoTemp['nb_das_tot'] += nbDasRum
    				
					if nbDasRum != 0:
						for numDas in range(0, nbDasRum):
							positionDas = 192 + numDas*8
							listeDas.append(ligneRum[positionDas:positionDas+6].strip())
    				#Actes
					nbActesRum = int(ligneRum[137:140])
					dicoTemp['nb_actes_tot'] += nbActesRum
					if nbActesRum != 0:
						for numActes in range(0, nbActesRum):
							positionActes = 192 + 8*(nbDasRum + int(ligneRum[135:137])) + 8
							if ligneRum[positionActes:positionActes+7].strip() in listeActesClassants:
								ActesClassants.append(ligneRum[positionActes:positionActes+7].strip())
								if ligneRum[positionActes:positionActes+7].strip() in listeActesOperatoires:
									NbActesOperatoires += 1
							elif ligneRum[positionActes:positionActes+7].strip() in listeActesSurveillance:
								NbActesSurveillance += 1
							elif ligneRum[positionActes:positionActes+7].strip() in listeActesRea:
								NbActesRea += 1
							if re.match('^..Q', ligneRum[positionActes:positionActes+7].strip()) != None:
								NbActesImagerie += 1
    
    				#DP
					listeDp.append(ligneRum[140:146].strip())
    				
				dicoTemp['das_tot'] = ' '.join(list(set(listeDas)))
				dicoTemp['actes_classants'] = ' '.join(list(set(ActesClassants)))
				dicoTemp['nb_actes_operatoires'] = NbActesOperatoires
				dicoTemp['nb_actes_imagerie'] = NbActesImagerie
				dicoTemp['dp_rum'] = ' '.join(list(set(listeDp)))
				dicoTemp['nb_actes_surveillance'] = NbActesSurveillance
				dicoTemp['nb_actes_rea'] = NbActesRea
				
				df = df.append(dicoTemp, ignore_index=True)
    	
		i = i+compteur

	#id�e de faire une copie de la base de donn�es, comme �a je n'ai plus qu'� extraire les lignes qui seront � �tudier	d�j� de la bonne forme
	df2 = df.copy()
	## Deuxi�me �tape : mise en forme de la base de donn�es pour applique l'algorithme de machine learning

	# Traitement de la base de donn�es contenant les actes class�s selon la CMD dans laquelle l'acte est consid�r� comme classant
	tableActesCMD = pd.read_csv('media/knn_v1/actes_classants_CMD.csv', sep = ',')
	
	actes_classants_cmd01 = [x for x in tableActesCMD.cmd01 if type(x) == str]	
	actes_classants_cmd02 = [x for x in tableActesCMD.cmd02 if type(x) == str]	
	actes_classants_cmd03 = [x for x in tableActesCMD.cmd03 if type(x) == str]	
	actes_classants_cmd04 = [x for x in tableActesCMD.cmd04 if type(x) == str]	
	actes_classants_cmd05 = [x for x in tableActesCMD.cmd05 if type(x) == str]	
	actes_classants_cmd06 = [x for x in tableActesCMD.cmd06 if type(x) == str]	
	actes_classants_cmd07 = [x for x in tableActesCMD.cmd07 if type(x) == str]	
	actes_classants_cmd08 = [x for x in tableActesCMD.cmd08 if type(x) == str]	
	actes_classants_cmd09 = [x for x in tableActesCMD.cmd09 if type(x) == str]	
	actes_classants_cmd10 = [x for x in tableActesCMD.cmd10 if type(x) == str]	
	actes_classants_cmd11 = [x for x in tableActesCMD.cmd11 if type(x) == str]	
	actes_classants_cmd12 = [x for x in tableActesCMD.cmd12 if type(x) == str]	
	actes_classants_cmd13 = [x for x in tableActesCMD.cmd13 if type(x) == str]	
	actes_classants_cmd14 = [x for x in tableActesCMD.cmd14 if type(x) == str]	
	actes_classants_cmd16 = [x for x in tableActesCMD.cmd16 if type(x) == str]	
	actes_classants_cmd17 = [x for x in tableActesCMD.cmd17 if type(x) == str]	
	actes_classants_cmd21 = [x for x in tableActesCMD.cmd21 if type(x) == str]	
	actes_classants_cmd22 = [x for x in tableActesCMD.cmd22 if type(x) == str]	
	actes_classants_cmd23 = [x for x in tableActesCMD.cmd23 if type(x) == str]

	df = df.assign(actes_cmd01 = lambda df: df['actes_classants'].map(lambda actes : len([x for x in actes.split() if x in actes_classants_cmd01])))
	df = df.assign(actes_cmd02 = lambda df: df['actes_classants'].map(lambda actes : len([x for x in actes.split() if x in actes_classants_cmd02])))
	df = df.assign(actes_cmd03 = lambda df: df['actes_classants'].map(lambda actes : len([x for x in actes.split() if x in actes_classants_cmd03])))
	df = df.assign(actes_cmd04 = lambda df: df['actes_classants'].map(lambda actes : len([x for x in actes.split() if x in actes_classants_cmd04])))
	df = df.assign(actes_cmd05 = lambda df: df['actes_classants'].map(lambda actes : len([x for x in actes.split() if x in actes_classants_cmd05])))
	df = df.assign(actes_cmd06 = lambda df: df['actes_classants'].map(lambda actes : len([x for x in actes.split() if x in actes_classants_cmd06])))
	df = df.assign(actes_cmd07 = lambda df: df['actes_classants'].map(lambda actes : len([x for x in actes.split() if x in actes_classants_cmd07])))
	df = df.assign(actes_cmd08 = lambda df: df['actes_classants'].map(lambda actes : len([x for x in actes.split() if x in actes_classants_cmd08])))
	df = df.assign(actes_cmd09 = lambda df: df['actes_classants'].map(lambda actes : len([x for x in actes.split() if x in actes_classants_cmd09])))
	df = df.assign(actes_cmd10 = lambda df: df['actes_classants'].map(lambda actes : len([x for x in actes.split() if x in actes_classants_cmd10])))
	df = df.assign(actes_cmd11 = lambda df: df['actes_classants'].map(lambda actes : len([x for x in actes.split() if x in actes_classants_cmd11])))
	df = df.assign(actes_cmd12 = lambda df: df['actes_classants'].map(lambda actes : len([x for x in actes.split() if x in actes_classants_cmd12])))
	df = df.assign(actes_cmd13 = lambda df: df['actes_classants'].map(lambda actes : len([x for x in actes.split() if x in actes_classants_cmd13])))
	df = df.assign(actes_cmd14 = lambda df: df['actes_classants'].map(lambda actes : len([x for x in actes.split() if x in actes_classants_cmd14])))
	df.insert(len(df.columns), 'actes_cmd15', 0, allow_duplicates = False)
	df = df.assign(actes_cmd16 = lambda df: df['actes_classants'].map(lambda actes : len([x for x in actes.split() if x in actes_classants_cmd16])))
	df = df.assign(actes_cmd17 = lambda df: df['actes_classants'].map(lambda actes : len([x for x in actes.split() if x in actes_classants_cmd17])))
	df.insert(len(df.columns), 'actes_cmd18', 0, allow_duplicates = False)
	df.insert(len(df.columns), 'actes_cmd19', 0, allow_duplicates = False)
	df.insert(len(df.columns), 'actes_cmd20', 0, allow_duplicates = False)
	df = df.assign(actes_cmd21 = lambda df: df['actes_classants'].map(lambda actes : len([x for x in actes.split() if x in actes_classants_cmd21])))
	df = df.assign(actes_cmd22 = lambda df: df['actes_classants'].map(lambda actes : len([x for x in actes.split() if x in actes_classants_cmd22])))
	df = df.assign(actes_cmd23 = lambda df: df['actes_classants'].map(lambda actes : len([x for x in actes.split() if x in actes_classants_cmd23])))


	# Traitement de la base de donn�es contenant les diagnostics class�s selon la CMD d'entr�e 
	tableDiagEntree = pd.read_csv('media/knn_v1/liste_diag_entree.csv', sep = ',')
	
	cmd01 = [x for x in tableDiagEntree.CMD01 if type(x) == str]
	cmd02 = [x for x in tableDiagEntree.CMD02 if type(x) == str]
	cmd03 = [x for x in tableDiagEntree.CMD03 if type(x) == str]
	cmd04 = [x for x in tableDiagEntree.CMD04 if type(x) == str]
	cmd05 = [x for x in tableDiagEntree.CMD05 if type(x) == str]
	cmd06 = [x for x in tableDiagEntree.CMD06 if type(x) == str]
	cmd07 = [x for x in tableDiagEntree.CMD07 if type(x) == str]
	cmd08 = [x for x in tableDiagEntree.CMD08 if type(x) == str]
	cmd09 = [x for x in tableDiagEntree.CMD09 if type(x) == str]
	cmd10 = [x for x in tableDiagEntree.CMD10 if type(x) == str]
	cmd11 = [x for x in tableDiagEntree.CMD11 if type(x) == str]
	cmd12 = [x for x in tableDiagEntree.CMD12 if type(x) == str]
	cmd13 = [x for x in tableDiagEntree.CMD13 if type(x) == str]
	cmd14 = [x for x in tableDiagEntree.CMD14 if type(x) == str]
	cmd15 = [x for x in tableDiagEntree.CMD15 if type(x) == str]
	cmd16 = [x for x in tableDiagEntree.CMD16 if type(x) == str]
	cmd17 = [x for x in tableDiagEntree.CMD17 if type(x) == str]
	cmd18 = [x for x in tableDiagEntree.CMD18 if type(x) == str]
	cmd19 = [x for x in tableDiagEntree.CMD19 if type(x) == str]
	cmd20 = [x for x in tableDiagEntree.CMD20 if type(x) == str]
	cmd21 = [x for x in tableDiagEntree.CMD21 if type(x) == str]
	cmd22 = [x for x in tableDiagEntree.CMD22 if type(x) == str]
	cmd23 = [x for x in tableDiagEntree.CMD23 if type(x) == str]	

	# Comptage des diagnostics
	
	df = df.assign(diag_entree_cmd01 = lambda df: df['dp_rum'].map(lambda diag : len([x for x in diag.split() if x in cmd01])) + df['das_tot'].map(lambda diag : len([x for x in diag.split() if x in cmd01])))
	df = df.assign(diag_entree_cmd02 = lambda df: df['dp_rum'].map(lambda diag : len([x for x in diag.split() if x in cmd02])) + df['das_tot'].map(lambda diag : len([x for x in diag.split() if x in cmd02])))
	df = df.assign(diag_entree_cmd03 = lambda df: df['dp_rum'].map(lambda diag : len([x for x in diag.split() if x in cmd03])) + df['das_tot'].map(lambda diag : len([x for x in diag.split() if x in cmd03])))
	df = df.assign(diag_entree_cmd04 = lambda df: df['dp_rum'].map(lambda diag : len([x for x in diag.split() if x in cmd04])) + df['das_tot'].map(lambda diag : len([x for x in diag.split() if x in cmd04])))
	df = df.assign(diag_entree_cmd05 = lambda df: df['dp_rum'].map(lambda diag : len([x for x in diag.split() if x in cmd05])) + df['das_tot'].map(lambda diag : len([x for x in diag.split() if x in cmd05])))
	df = df.assign(diag_entree_cmd06 = lambda df: df['dp_rum'].map(lambda diag : len([x for x in diag.split() if x in cmd06])) + df['das_tot'].map(lambda diag : len([x for x in diag.split() if x in cmd06])))
	df = df.assign(diag_entree_cmd07 = lambda df: df['dp_rum'].map(lambda diag : len([x for x in diag.split() if x in cmd07])) + df['das_tot'].map(lambda diag : len([x for x in diag.split() if x in cmd07])))
	df = df.assign(diag_entree_cmd08 = lambda df: df['dp_rum'].map(lambda diag : len([x for x in diag.split() if x in cmd08])) + df['das_tot'].map(lambda diag : len([x for x in diag.split() if x in cmd08])))
	df = df.assign(diag_entree_cmd09 = lambda df: df['dp_rum'].map(lambda diag : len([x for x in diag.split() if x in cmd09])) + df['das_tot'].map(lambda diag : len([x for x in diag.split() if x in cmd09])))
	df = df.assign(diag_entree_cmd10 = lambda df: df['dp_rum'].map(lambda diag : len([x for x in diag.split() if x in cmd10])) + df['das_tot'].map(lambda diag : len([x for x in diag.split() if x in cmd10])))
	df = df.assign(diag_entree_cmd11 = lambda df: df['dp_rum'].map(lambda diag : len([x for x in diag.split() if x in cmd11])) + df['das_tot'].map(lambda diag : len([x for x in diag.split() if x in cmd11])))
	df = df.assign(diag_entree_cmd12 = lambda df: df['dp_rum'].map(lambda diag : len([x for x in diag.split() if x in cmd12])) + df['das_tot'].map(lambda diag : len([x for x in diag.split() if x in cmd12])))
	df = df.assign(diag_entree_cmd13 = lambda df: df['dp_rum'].map(lambda diag : len([x for x in diag.split() if x in cmd13])) + df['das_tot'].map(lambda diag : len([x for x in diag.split() if x in cmd13])))
	df = df.assign(diag_entree_cmd14 = lambda df: df['dp_rum'].map(lambda diag : len([x for x in diag.split() if x in cmd14])) + df['das_tot'].map(lambda diag : len([x for x in diag.split() if x in cmd14])))
	df = df.assign(diag_entree_cmd15 = lambda df: df['dp_rum'].map(lambda diag : len([x for x in diag.split() if x in cmd15])) + df['das_tot'].map(lambda diag : len([x for x in diag.split() if x in cmd15])))
	df = df.assign(diag_entree_cmd16 = lambda df: df['dp_rum'].map(lambda diag : len([x for x in diag.split() if x in cmd16])) + df['das_tot'].map(lambda diag : len([x for x in diag.split() if x in cmd16])))
	df = df.assign(diag_entree_cmd17 = lambda df: df['dp_rum'].map(lambda diag : len([x for x in diag.split() if x in cmd17])) + df['das_tot'].map(lambda diag : len([x for x in diag.split() if x in cmd17])))
	df = df.assign(diag_entree_cmd18 = lambda df: df['dp_rum'].map(lambda diag : len([x for x in diag.split() if x in cmd18])) + df['das_tot'].map(lambda diag : len([x for x in diag.split() if x in cmd18])))
	df = df.assign(diag_entree_cmd19 = lambda df: df['dp_rum'].map(lambda diag : len([x for x in diag.split() if x in cmd19])) + df['das_tot'].map(lambda diag : len([x for x in diag.split() if x in cmd19])))
	df = df.assign(diag_entree_cmd20 = lambda df: df['dp_rum'].map(lambda diag : len([x for x in diag.split() if x in cmd20])) + df['das_tot'].map(lambda diag : len([x for x in diag.split() if x in cmd20])))
	df = df.assign(diag_entree_cmd21 = lambda df: df['dp_rum'].map(lambda diag : len([x for x in diag.split() if x in cmd21])) + df['das_tot'].map(lambda diag : len([x for x in diag.split() if x in cmd21])))
	df = df.assign(diag_entree_cmd22 = lambda df: df['dp_rum'].map(lambda diag : len([x for x in diag.split() if x in cmd22])) + df['das_tot'].map(lambda diag : len([x for x in diag.split() if x in cmd22])))
	df = df.assign(diag_entree_cmd23 = lambda df: df['dp_rum'].map(lambda diag : len([x for x in diag.split() if x in cmd23])) + df['das_tot'].map(lambda diag : len([x for x in diag.split() if x in cmd23])))

	## Troisi�me �tape : application de l'algorithme de machine learning
	
	#Conversion des colonnes en integer
	df['departement_etablissement'] = pd.to_numeric(df['departement_etablissement'], errors = 'coerce')
	df['CMD'] = pd.to_numeric(df['CMD'], errors = 'coerce')
	df['age'] = pd.to_numeric(df['age'], errors = 'coerce')
	df['sexe'] = pd.to_numeric(df['sexe'], errors = 'coerce')
	df['mois_sortie'] = pd.to_numeric(df['mois_sortie'], errors = 'coerce')
	df['mode_sortie'] = pd.to_numeric(df['mode_sortie'], errors = 'coerce')
	df['mode_entree'] = pd.to_numeric(df['mode_entree'], errors = 'coerce')
	df['duree_tot'] = pd.to_numeric(df['duree_tot'], errors = 'coerce')
	df['nb_rum'] = pd.to_numeric(df['nb_rum'], errors = 'coerce')
	df['nb_das_tot'] = pd.to_numeric(df['nb_das_tot'], errors = 'coerce')
	df['nb_actes_tot'] = pd.to_numeric(df['nb_actes_tot'], errors = 'coerce')
	
	#Application de l'algorithme
	with open('media/knn_v1/model_knn_V1.pkl', 'rb') as f :
		knn = pickle.load(f)
	
	X = df.drop(['finess', 'CMD', 'num_rss', 'dp_rum', 'das_tot', 'actes_classants'], axis = 1)
	y_knn = knn.predict(X)
	y_knn_proba = knn.predict_proba(X)
	
	## Quatri�me �tape : r�cup�ration des lignes pour lesquelles les CMD pr�dits et group�s sont diff�rents et ajout des donn�es de score 
	
	proba = []
	for i in range(0, df2.shape[0]):
		proba.append(max(list(y_knn_proba)[i]))
	
	df2.insert(5, 'CMD_predit', list(y_knn), allow_duplicates=False)
	df2.insert(6, 'score', proba, allow_duplicates=False)
 
	listeLignes = []
	for i in range(0, df2.shape[0]):
		if (df2.CMD[i] != df2.CMD_predit[i]) and (df2.score[i] > 0.5):
			listeLignes.append(i)
	df2 = df2.iloc[listeLignes]
	
	
	#Enregistrement du tableau final au format xlsx
	
	df2 = df2[['finess', 'num_rss', 'CMD', 'CMD_predit', 'score']]
	
	now = datetime.now()
	excel_writer = dossierSortie + r"/prediction_CMD_" + str(finess) + now.strftime("_%H:%M:%S_%d_%m_%Y_") + str(random.randint(0,1000)) + r".xlsx" 
	df2.to_excel(excel_writer)

			

			
			
			
