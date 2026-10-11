from django import forms
from .models import Article

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        # 1. Ajout de 'prix' dans la liste des champs
        fields = ['titre', 'category', 'desc', 'prix', 'image','quantite', 'is_published']
        
        # 2. Ajout d'un label plus propre pour le formulaire
        labels = {
            'titre': 'Titre',
            'category': 'Catégorie',
            'desc': 'Description',
            'prix': 'Prix (FCFA)',
            'quantite': 'Quantite',
            'is_published': 'Publier immédiatement (visible en boutique)',
        }
        
        # 3. Ajout du widget pour que le champ ait le style Bootstrap
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'desc': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'prix': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 5000'}),
            'quantite': forms.NumberInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }