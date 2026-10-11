from django.shortcuts import render, redirect, get_object_or_404
from .models import Article, Category, Commande, CommandeArticle,Commentaire
from .form import UserCreationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required

# --- NAVIGATION DE BASE ---

@login_required
def home(request):
    """Affiche la page d'accueil avec tous les articles publiés + recherche nom/catégorie."""
    query = request.GET.get("q", request.GET.get("article", "")).strip()
    categorie_id = request.GET.get("categorie", request.GET.get("category", "")).strip()

    # Seuls les articles publiés sont visibles publiquement
    list_article = Article.objects.filter(is_published=True).select_related("category", "user")

    if query:
        list_article = list_article.filter(titre__icontains=query)
    if categorie_id:
        try:
            list_article = list_article.filter(category_id=int(categorie_id))
        except (ValueError, TypeError):
            pass

    list_article = list_article.order_by('-id')
    categories = Category.objects.all().order_by('nom')
    context = {
        "liste": list_article,
        "categories": categories,
        "q": query,
        "categorie_active": str(categorie_id),
    }
    return render(request, "index.html", context)

def detail(request, id_article):
    """Affiche les détails d'un article spécifique et propose des articles similaires."""
    # Récupère l'article par son ID ou renvoie une erreur 404 si introuvable
    article = get_object_or_404(Article, id=id_article)
    # Un article dépublié n'est visible que par son propriétaire
    if not article.is_published and article.user != request.user:
        messages.error(request, "Cet article n'est pas publié pour le moment.")
        return redirect('home')
    category = article.category
    
    # Filtre les articles de la même catégorie en excluant celui qu'on regarde déjà (limite à 5)
    article_relation = Article.objects.filter(category=category).exclude(id=id_article)[:5]
    
    # Debug : vérifie en console si des articles similaires existent
    if article_relation.exists():
        print(f"Image du premier article similaire : {article_relation[0].image.url}")
    else:
        print("Aucun article similaire trouvé.")

    return render(request, 'detail.html', {
        "article": article,
        "aer": article_relation # 'aer' est utilisé dans le template pour la boucle des similaires
    })

def search(request):
    """Recherche des articles publiés par nom (titre) et/ou catégorie."""
    query = request.GET.get("article", request.GET.get("q", "")).strip()
    categorie_id = request.GET.get("categorie", request.GET.get("category", "")).strip()
    # Seuls les publiés sont cherchables publiquement
    liste_article = Article.objects.filter(is_published=True).select_related("category", "user")
    if query:
        # la propriete "icontains" permet de chercher le texte sans tenir compte des majuscules/minuscules
        liste_article = liste_article.filter(titre__icontains=query)
    if categorie_id:
        try:
            liste_article = liste_article.filter(category_id=int(categorie_id))
        except (ValueError, TypeError):
            pass
    liste_article = liste_article.order_by('-id')
    categories = Category.objects.all().order_by('nom')
    return render(request, "search.html", {
        "liste_article": liste_article,
        "categories": categories,
        "q": query,
        "categorie_active": str(categorie_id),
    })


# --- AUTHENTIFICATION (SÉCURITÉ) ---

def inscription(request):
    """Gère la création de nouveaux comptes utilisateurs."""
    if request.method == 'POST': # Si le formulaire est envoyé
        form = UserCreationForm(request.POST) # Remplit le formulaire avec les données reçues
        if form.is_valid(): # Vérifie si les mots de passe correspondent, si le user existe déjà, etc.
            form.save() # Enregistre le nouvel utilisateur dans la base de données
            messages.success(request, "Votre compte a été créé avec succès. Connectez-vous !")
            return redirect('connexion') # Redirige vers la page de login
    else:
        form = UserCreationForm() # Affiche un formulaire vide au premier chargement
    return render(request, 'inscription.html', {'form': form})

def connexion(request):
    """Connecte l'utilisateur en vérifiant ses identifiants."""
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        # Vérifie si le couple username/password est correct
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user) # Ouvre la session utilisateur
            messages.success(request, f"Ravi de vous revoir, {user.username} !")
            return redirect('home')
        else:
            messages.error(request, 'Informations incorrectes') # Message d'erreur si échec
    return render(request, 'connexion.html')

def deconnexion(request):
    """Ferme la session de l'utilisateur et le renvoie vers la connexion."""
    logout(request)
    messages.info(request, "Vous êtes déconnecté. À bientôt !")
    return redirect('connexion')


# --- GESTION DU PANIER (SESSION) ---

def ajouter_au_panier(request, id_article):
    """Ajoute un article au panier et diminue le stock réel."""
    
    # 1. Récupérer l'article dans la base de données
    article = get_object_or_404(Article, id=id_article)

    # Bloquer l'achat d'un article dépublié
    if not article.is_published:
        messages.error(request, f"L'article {article.titre} n'est pas publié pour le moment.")
        return redirect('home')
    
    # 2. Vérifier si le stock est suffisant (Sécurité)
    if article.quantite <= 0:
        messages.error(request, f"Désolé, l'article {article.titre} est en rupture de stock.")
        return redirect('home')

    # 3. Logique du Panier (Session)
    panier = request.session.get('panier', {})
    id_str = str(id_article)

    if id_str in panier:
        panier[id_str] += 1
    else:
        panier[id_str] = 1
    
    # 4. MISE À JOUR DU STOCK RÉEL
    # On diminue la quantité en base de données
    article.quantite -= 1
    article.save()

    # 5. Sauvegarde de la session et redirection
    request.session['panier'] = panier
    messages.success(request, f"{article.titre} a été ajouté au panier.")
    return redirect('home')


def afficher_panier(request):
    """Calcule les totaux et prépare l'affichage des articles du panier."""
    panier = request.session.get('panier', {})
    articles_panier = [] # Liste qui contiendra les objets Articles + leurs quantités
    total_general = 0
    panier_nettoye = {}

    for id_art, quantite in panier.items():
        try:
            article = Article.objects.get(id=id_art)
        except Article.DoesNotExist:
            # Article supprimé entre temps : on l'ignore (nettoyé de la session plus bas)
            continue
        panier_nettoye[id_art] = quantite
        total_ligne = article.prix * quantite # Calcul du sous-total par article
        total_general += total_ligne # Cumul pour le prix total du panier
        
        # On regroupe les infos pour faciliter la boucle dans le template HTML
        articles_panier.append({
            'article': article,
            'quantite': quantite,
            'total_ligne': total_ligne
        })

    if len(panier_nettoye) != len(panier):
        # Des articles ont disparu de la BDD : on nettoie la session
        request.session['panier'] = panier_nettoye

    return render(request, 'panier.html', {
        'articles_panier': articles_panier,
        'total_general': total_general
    })



def annuler_panier(request):
    """Rend les articles au stock et vide complètement le panier."""
    
    # 1. On récupère le contenu du panier avant de le supprimer
    panier = request.session.get('panier', {})

    if panier:
        # 2. On boucle sur chaque article pour rendre les quantités au stock
        for id_article, quantite_commandee in panier.items():
            try:
                # On récupère l'article en base de données
                article = Article.objects.get(id=id_article)
                # On lui rajoute ce qui était dans le panier
                article.quantite += quantite_commandee
                article.save()
            except Article.DoesNotExist:
                # Si l'article a été supprimé entre temps par l'admin, on ignore
                continue

        # 3. Une fois les stocks rendus, on vide la session
        del request.session['panier']
        messages.success(request, "Le panier a été vidé et les articles remis en stock.")

    return redirect('home')


# --- FINALISATION DE LA COMMANDE (BASE DE DONNÉES) ---

@login_required
def confirmer_commande(request):
    """Transforme le panier virtuel (session) en une commande réelle (Base de données)."""
    if request.method == 'POST':
        panier = request.session.get('panier', {})
        if not panier:
            messages.error(request, "Votre panier est vide !")
            return redirect('home')

        # Récupère l'adresse saisie par le client dans le formulaire de livraison
        adresse = request.POST.get('adresse')
        
        # 1. CRÉATION DE L'ENVELOPPE (La commande globale)
        nouvelle_commande = Commande.objects.create(
            client=request.user, # L'utilisateur qui achète
            nom_client_livraison=request.user.username,
            adresse_livraison=adresse,
            complet=True # Indique que la commande est validée
        )

        total_commande = 0
        
        # 2. CRÉATION DES DÉTAILS (Chaque article de la commande)
        for id_art, quantite in panier.items():
            try:
                article = Article.objects.get(id=id_art)
            except Article.DoesNotExist:
                # Article supprimé entre temps : on l'ignore
                continue
            prix_ligne = article.prix * quantite
            total_commande += prix_ligne
            
            # On enregistre chaque article vendu dans la table CommandeArticle
            CommandeArticle.objects.create(
                commande=nouvelle_commande, # Relie cet article à la commande ci-dessus
                article=article,
                quantite=quantite,
                prix_unitaire=article.prix # On fige le prix (si l'article change de prix plus tard, la facture reste juste)
            )

        # 3. MISE À JOUR DU TOTAL ET NETTOYAGE
        nouvelle_commande.total_final = total_commande
        nouvelle_commande.save() # Enregistre le montant total final dans la commande

        del request.session['panier'] # Vide le panier après l'achat réussi

        messages.success(request, f"Félicitations ! Votre commande de {total_commande} FCFA a été enregistrée.")
        return redirect('home')
    
    return redirect('afficher_panier')


###########  pour la fonction liker ##########
def liker_article(request, id_article):
    article = get_object_or_404(Article, id=id_article)
    if not request.user.is_authenticated:
        messages.error(request, "Connectez-vous pour ajouter un favori.")
        return redirect('connexion')
    if article.likes.filter(id=request.user.id).exists():
        article.likes.remove(request.user) # Enlever le like si déjà présent
        messages.info(request, f"« {article.titre} » retiré de vos favoris.")
    else:
        article.likes.add(request.user) # Ajouter le like
        messages.success(request, f"« {article.titre} » ajouté à vos favoris.")
    return redirect('detail', id_article=article.id)

#########  pour la fonction commentaire  ########
def ajouter_commentaire(request, id_article):
    if not request.user.is_authenticated:
        messages.error(request, "Connectez-vous pour commenter.")
        return redirect('connexion')
    if request.method == "POST":
        article = get_object_or_404(Article, id=id_article)
        contenu = (request.POST.get('contenu') or '').strip()
        if contenu:
            Commentaire.objects.create(
                article=article,
                user=request.user,
                contenu=contenu
            )
            messages.success(request, "Commentaire publié.")
        else:
            messages.warning(request, "Votre commentaire est vide.")
    return redirect('detail', id_article=id_article)

######### pour supprimer les commentaires  ######
def supprimer_commentaire(request, id_commentaire):
    # On récupère le commentaire
    commentaire = get_object_or_404(Commentaire, id=id_commentaire)
    id_article = commentaire.article.id # On garde l'ID pour rediriger vers la page de l'article
    
    # Sécurité : Seul l'auteur peut supprimer
    if commentaire.user == request.user:
        commentaire.delete()
        messages.success(request, "Commentaire supprimé avec succès.")
    else:
        messages.error(request, "Vous n'avez pas l'autorisation de supprimer ce commentaire.")
        
    return redirect('detail', id_article=id_article)