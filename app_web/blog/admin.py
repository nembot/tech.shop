from django.contrib import admin
from .models import Article,Category,Commande,CommandeArticle,Commentaire
# Register your models here.

admin.site.register(Article) ## cet commande permet de dire que dans la partie admin met la table article 
admin.site.register(Category)
admin.site.register(Commande)
admin.site.register(CommandeArticle)
admin.site.register(Commentaire)


