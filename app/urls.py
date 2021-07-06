from django.urls import path
from . views import FichierView, NameViewSet, FichierViewSet, FinessViewSet,UserViewSet,list_actes, list_das, recherche_rum, list_rss, liste_etablissement_codage, liste_date_codage, liste_file_codage ,recherche_rss, test3, test, test2, delete_donnee_finess, supprimer_user, sup_finess, sup_user, ajout_finess, region, users, dictionnaire, etab, donnee, sortie, delete, patienter, delete_delay, user, attente, resultat, delete_all,delete_one, telecharger_all, clean_zip, user
from rest_framework_simplejwt.views import (TokenObtainPairView, TokenRefreshView)
from rest_framework import routers
from django.contrib.auth.models import User


router = routers.DefaultRouter()
#router.register('fichiers', FichierViewSet)
#router.register('name', NameViewSet)
#router.register('finess', FinessViewSet)
#router.register('add_user', UserViewSet)
#urlpatterns = router.urls

urlpatterns = [
    path('fichiers/', test),
    path('name/', test2),
    path('finess/', test3),
    path('fichier/', FichierView.as_view()),
    path('donnee/', donnee),
    path('user/', user),
    path('sortie/', sortie),
    path('clean/', delete),
    path('api-token/', TokenObtainPairView.as_view()),
    path('api-token-refresh/', TokenRefreshView.as_view()),
    path('empty/', patienter),
    path('deletedelay/', delete_delay),
    path('resultat/', resultat),
    path('delete_one/', delete_one),
    path('delete_all/', delete_all),
    path('telecharger_all/', telecharger_all),
    path('clean_zip/', clean_zip),
    path('users/', users),
    path('etab/', etab),
    path('dictionnaire/', dictionnaire),
    path('region/', region),
    path('ajouter_finess/', ajout_finess),
    path('supprimer_finess/', sup_finess),
    path('supprimer_user_finess/', supprimer_user),
    path('delete_donnee_finess/', delete_donnee_finess),

    path('liste_etablissement_codage/', liste_etablissement_codage),
    path('liste_date_codage/', liste_date_codage),
    path('liste_file_codage/', liste_file_codage),


    #fonction à faire : 
    path('recherche_rss/', recherche_rss),
    path('recherche_rum/', recherche_rum),
    path('liste_rss/',list_rss),
    path('liste_das/',list_das),
    path('liste_actes/',list_actes),
    
    
    #path('donnee_rum/'),
    #path('das_to_dp/'),
    #path('add_das/'),
    #path('add_actes/'),
    #path('add_rum/'),
    #path('replace_igs/'),
    #path('replace_dr/'),
    #path('calcul_gain_ghm/'),

    
]

urlpatterns += router.urls

