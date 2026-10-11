from django.shortcuts import render,redirect
from django.shortcuts import render, get_object_or_404
from blog.models import Article,Commande,CommandeArticle,Category,Commentaire
from django.views.generic.edit import UpdateView,CreateView,DeleteView
from blog.forms import ArticleForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy # Importe ceci en haut de ton fichier
from django.db.models import Sum, Count, F
from django.contrib.auth.models import User
import json


# Create your views here.
def app_admin(request):
    return render(request,'base.html')



def user_article(request):
    # On filtre par 'user' (le nom exact dans ton modèle Article)
    articles_liste = Article.objects.filter(user=request.user).select_related('category').order_by('-id')

    # Petites stats pour l'en-tête de la page Mes articles
    nb_total = articles_liste.count()
    nb_publies = articles_liste.filter(is_published=True).count()
    nb_depublies = nb_total - nb_publies

    # DEBUG : Affiche dans le terminal pour voir si Django trouve quelque chose
    print(f"Utilisateur connecté : {request.user}")
    print(f"Nombre d'articles trouvés pour lui : {nb_total}")

    return render(request, 'my_article.html', {
        'list': articles_liste,
        'nb_total': nb_total,
        'nb_publies': nb_publies,
        'nb_depublies': nb_depublies,
    })
    
    #### cette permet de filtrer la liste des articles de l'utilisateur qui est connecte
   
class AddArticle(CreateView):
    model = Article ## le modele utiliser 
    form_class = ArticleForm  ## le formulaire utiliser
    template_name = "add-article.html"  ## le templet utiliser
   
    success_url = "/my-article/"  ### le chemin a rediriger lorsqu'elle est enregistrer

    #####   cette fonction permet de dire d'enregistrer dans la base de donnee avec le nom de l'utilisateur courant
    def form_valid(self,form):
        form.instance.user=self.request.user
        response = super().form_valid(form)
        messages.success(self.request, f"L'article « {self.object.titre} » a été créé avec succès.")
        return response


########### vue pour modiier un article #################
class UpdateArticle(UpdateView):
    model = Article
    form_class = ArticleForm
    template_name = "modifier-article.html" # Utilise ton nouveau template ici
    success_url = reverse_lazy('my-article')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"L'article « {self.object.titre} » a été modifié avec succès.")
        return response

# Vue pour supprimer
class DeleteArticle(DeleteView):
    model = Article
    template_name = "confirm-delete.html" # Un petit template de confirmation
    success_url = reverse_lazy('my-article')

    def delete(self, request, *args, **kwargs):
        titre = self.get_object().titre
        response = super().delete(request, *args, **kwargs)
        messages.success(request, f"L'article « {titre} » a été supprimé.")
        return response


########## pour l'afficher des commandes(vente et achat) ##########
# NOTE: première version simple de mon_espace_commandes conservée en commentaire,
# la version complète avec statistiques est définie plus bas et la remplace.


########### pour supprimer les achats et ventes #######
def supprimer_achat(request, pk):
    # Un client annule sa propre commande
    commande = get_object_or_404(Commande, id=pk, client=request.user)
    commande.delete()
    messages.success(request, "Commande annulée.")
    return redirect('mes_commandes')

def supprimer_vente(request, pk):
    # Un annonceur supprime une notification de vente de sa liste
    vente = get_object_or_404(CommandeArticle, id=pk, article__user=request.user)
    vente.delete()
    messages.success(request, "Vente retirée de votre historique.")
    return redirect('mes_commandes')

######### pour les cadrants  des ventes #########

def mon_espace_commandes(request):
    # --- DONNÉES ACHATS (Ce que j'ai commandé) ---
    mes_achats = Commande.objects.filter(client=request.user).order_by('-date_commande')
    
    # Statistiques Achats
    nb_commandes_achats = mes_achats.count()
    total_depense = sum(c.total_final for c in mes_achats)
    # Somme de toutes les quantités de tous les articles dans mes achats
    nb_produits_achetés = sum(sum(item.quantite for item in c.items.all()) for c in mes_achats)

    # --- DONNÉES VENTES (Ce qu'on m'a acheté) ---
    mes_ventes = CommandeArticle.objects.filter(article__user=request.user).order_by('-date_ajoute')
    
    # Statistiques Ventes
    nb_commandes_ventes = mes_ventes.values('commande').distinct().count()
    total_revenu = sum(v.get_total for v in mes_ventes)
    nb_produits_vendus = sum(v.quantite for v in mes_ventes)

    return render(request, 'commandes.html', {
        'mes_achats': mes_achats,
        'nb_commandes_achats': nb_commandes_achats,
        'total_depense': total_depense,
        'nb_produits_achetés': nb_produits_achetés,
        
        'mes_ventes': mes_ventes,
        'nb_commandes_ventes': nb_commandes_ventes,
        'total_revenu': total_revenu,
        'nb_produits_vendus': nb_produits_vendus,
    })

######### pour les cadrants  des achats #########

def mes_achats_view(request):
    # On récupère toutes les commandes passées par l'utilisateur connecté
    mes_achats = Commande.objects.filter(client=request.user).order_by('-date_commande')
    
    # --- LES 3 STATISTIQUES POUR LES CADRANS ---
    # 1. Nombre total de commandes passées
    nb_commandes = mes_achats.count()
    
    # 2. Somme totale dépensée (Somme des total_final)
    total_depense = sum(c.total_final for c in mes_achats)
    
    # 3. Nombre total d'articles reçus (Somme des quantités dans chaque commande)
    nb_articles = sum(sum(item.quantite for item in c.items.all()) for c in mes_achats)

    return render(request, 'mes_achats.html', {
        'mes_achats': mes_achats,
        'nb_commandes': nb_commandes,
        'total_depense': total_depense,
        'nb_articles': nb_articles,
    })


@login_required
def toggle_publish(request, pk):
    """Publie / dépublie un article (uniquement le propriétaire)."""
    article = get_object_or_404(Article, id=pk, user=request.user)
    article.is_published = not article.is_published
    article.save()
    if article.is_published:
        messages.success(request, f"L'article « {article.titre} » est maintenant publié.")
    else:
        messages.warning(request, f"L'article « {article.titre} » est maintenant dépublié (invisible en boutique).")
    return redirect('my-article')


@login_required
def statistiques(request):
    """Page Statistiques fonctionnelle : chiffres réels calculés depuis la BDD."""
    # --- Mes articles ---
    mes_articles = Article.objects.filter(user=request.user)
    nb_articles_total = mes_articles.count()
    nb_articles_publies = mes_articles.filter(is_published=True).count()
    nb_articles_depublies = nb_articles_total - nb_articles_publies
    stock_total = mes_articles.aggregate(s=Sum('quantite'))['s'] or 0
    valeur_stock = sum((a.prix or 0) * (a.quantite or 0) for a in mes_articles)

    # Likes & commentaires reçus sur mes articles
    likes_recus = sum(a.total_likes() for a in mes_articles)
    commentaires_recus = Commentaire.objects.filter(article__user=request.user).count()

    # --- Mes ventes (ce qu'on m'a acheté) ---
    mes_ventes = CommandeArticle.objects.filter(article__user=request.user).select_related('article', 'commande')
    nb_ventes_lignes = mes_ventes.count()
    nb_commandes_ventes = mes_ventes.values('commande').distinct().count()
    total_revenu = sum(v.get_total for v in mes_ventes)
    nb_produits_vendus = sum(v.quantite for v in mes_ventes)

    # Top 5 articles les plus vendus (par quantité)
    top_vendus = (
        mes_ventes.values('article__id', 'article__titre')
        .annotate(qte=Sum('quantite'))
        .order_by('-qte')[:5]
    )
    top_vendus_labels = [t['article__titre'] for t in top_vendus]
    top_vendus_values = [t['qte'] for t in top_vendus]

    # Répartition de mes articles par catégorie
    par_categorie = (
        mes_articles.values('category__nom')
        .annotate(n=Count('id'))
        .order_by('-n')
    )
    cat_labels = [c['category__nom'] or 'Sans catégorie' for c in par_categorie]
    cat_values = [c['n'] for c in par_categorie]

    # --- Mes achats (ce que j'ai commandé) ---
    mes_achats = Commande.objects.filter(client=request.user)
    nb_commandes_achats = mes_achats.count()
    total_depense = sum(c.total_final for c in mes_achats)
    nb_produits_achetes = sum(sum(item.quantite for item in c.items.all()) for c in mes_achats)

    # --- Boutique globale (repères) ---
    nb_articles_boutique = Article.objects.filter(is_published=True).count()
    nb_vendeurs = Article.objects.values('user').distinct().count()

    return render(request, 'statistiques.html', {
        # articles
        'nb_articles_total': nb_articles_total,
        'nb_articles_publies': nb_articles_publies,
        'nb_articles_depublies': nb_articles_depublies,
        'stock_total': stock_total,
        'valeur_stock': valeur_stock,
        'likes_recus': likes_recus,
        'commentaires_recus': commentaires_recus,
        # ventes
        'nb_ventes_lignes': nb_ventes_lignes,
        'nb_commandes_ventes': nb_commandes_ventes,
        'total_revenu': total_revenu,
        'nb_produits_vendus': nb_produits_vendus,
        'top_vendus': top_vendus,
        'top_vendus_labels': json.dumps(top_vendus_labels, ensure_ascii=False),
        'top_vendus_values': json.dumps(top_vendus_values),
        # categories
        'par_categorie': par_categorie,
        'cat_labels': json.dumps(cat_labels, ensure_ascii=False),
        'cat_values': json.dumps(cat_values),
        # achats
        'nb_commandes_achats': nb_commandes_achats,
        'total_depense': total_depense,
        'nb_produits_achetes': nb_produits_achetes,
        # global
        'nb_articles_boutique': nb_articles_boutique,
        'nb_vendeurs': nb_vendeurs,
    })