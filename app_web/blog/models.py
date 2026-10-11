from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    nom = models.CharField(max_length=120)

    def __str__(self):
        return self.nom

# Create your models here.
class Article(models.Model):### models est un module python dans lequel se trouve la class Model
    #les attributs de la classe == champs de la table
    titre = models.CharField(max_length=100) #charfield veut dire chaine de caratere et max_lenght longueur max de la chaine de caratere
    desc = models.TextField()
    prix = models.FloatField()
    quantite = models.IntegerField(default=0)
    # Ajout de related_name='articles' pour faciliter les requêtes inverses
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='articles')## on_delete signifie que lorqu'on supprime une category sa supprime tous les aeticle de la category
    image = models.ImageField(null=True,blank=True) # Il est préférable de préciser un dossier d'upload
    created_at = models.DateField(auto_now_add=True)## auto_now_add veut mettre la date du jour de la creation de l'article
    updated_at = models.DateField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True)
    likes = models.ManyToManyField(User, related_name='article_likes', blank=True)
    is_published = models.BooleanField(default=True, verbose_name="Publié")
    
    def total_likes(self):
        return self.likes.count()

    def __str__(self):
        return self.titre
    


class Utilisateur(models.Model):
    nom = models.CharField(max_length=50)
    mot_de_passe = models.CharField(max_length=50)

class Commande(models.Model):
    # On lie la commande à l'utilisateur Django
    client = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    date_commande = models.DateTimeField(auto_now_add=True)
    complet = models.BooleanField(default=False)
    # Infos de livraison de ta capture d'écran
    nom_client_livraison = models.CharField(max_length=200, null=True)
    adresse_livraison = models.CharField(max_length=200, null=True)
    total_final = models.FloatField(default=0)

    def __str__(self):
        return f"Commande N° {self.id}"

class CommandeArticle(models.Model):
    # On lie l'article spécifique
    article = models.ForeignKey(Article, on_delete=models.SET_NULL, null=True)
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE, related_name='items')
    quantite = models.IntegerField(default=0)
    prix_unitaire = models.FloatField() # On stocke le prix au moment de l'achat
    date_ajoute = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.article.titre} (x{self.quantite})"
    
    ########## pour le calcul des cadrants #######
    @property
    def get_total(self):
        return self.prix_unitaire * self.quantite
    

class Commentaire(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='commentaires')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    contenu = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Commentaire de {self.user.username} sur {self.article.titre}"##### c'est a la lisibilite dans l'interface admin
