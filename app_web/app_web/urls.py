"""
URL configuration for app_web project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from blog.views import detail
from django.contrib import admin
from django.urls import path
from blog.views import home, detail,annuler_panier,search,confirmer_commande,afficher_panier,ajouter_au_panier,inscription,connexion,deconnexion,liker_article,ajouter_commentaire,supprimer_commentaire # Assure-toi d'importer la nouvelle vue
from momo.views import mes_achats_view,supprimer_vente,supprimer_achat,app_admin,user_article,AddArticle,UpdateArticle,DeleteArticle,mon_espace_commandes,toggle_publish,statistiques


urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', home, name="home"),
    path('confirmer-commande/',confirmer_commande, name='confirmer_commande'),
    path('annuler-panier/', annuler_panier, name='annuler_panier'),
    path('ajouter-au-panier/<int:id_article>/', ajouter_au_panier, name='ajouter_au_panier'),
    path('mon-panier/', afficher_panier, name='afficher_panier'), # On prépare l'étape suivante
    # J'ai ajouté une virgule à la fin de la ligne ci-dessous
    path('article/<int:id_article>', detail, name="detail"), ## ici ont veut affiche chaque produit et le mot entre guillemet veut dire que le nom de l'article change
    path('article/recherche', search, name="search"),
    path('', inscription , name="inscription"),
    path('conn/', connexion , name="connexion"),
    path('deconnexion/', deconnexion ,name='deconnexion'),
    path('my-admin/', app_admin ,name='app_admin'),
    path('my-article/', user_article,name='my-article'),
    path('article/<int:pk>/toggle-publish/', toggle_publish, name='toggle-publish'),
    path('statistiques/', statistiques, name='statistiques'),
    path('ajout-article/', AddArticle.as_view(),name='ajout-article'),
    path('modifier-article/<int:pk>/', UpdateArticle.as_view(), name='modifier-article'),
    path('supprimer-article/<int:pk>/', DeleteArticle.as_view(), name='supprimer-article'),
    path('mon-espace-commandes/',mon_espace_commandes, name='mes_commandes'),
      ### pk(cles primaire de l'article) permet de dire a django va me chercher les infos de l'article possedant tel cles primaire et biensur int permet de rester dans les entiers
    path('supprimer-achat/<int:pk>/', supprimer_achat, name='supprimer_achat'),
    path('supprimer-vente/<int:pk>/', supprimer_vente, name='supprimer_vente'),
    path('mes-achats/', mes_achats_view, name='mes_achats'),
    path('article/<int:id_article>/like/', liker_article, name='liker_article'),
    path('article/<int:id_article>/commentaire/',ajouter_commentaire, name='ajouter_commentaire'),
    path('commentaire/supprimer/<int:id_commentaire>/', supprimer_commentaire, name='supprimer_commentaire'),


]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)