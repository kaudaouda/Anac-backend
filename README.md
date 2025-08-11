# 🚀 AnacBackend - API Django REST Framework

## 📋 Description
Backend API moderne développé avec Django et Django REST Framework pour l'application Anac. Architecture optimisée pour la performance et la maintenabilité.

## 🏗️ Architecture

```
Naca/
├── 📁 AnacBackend/          # Configuration principale Django
│   ├── __init__.py
│   ├── settings.py          # Paramètres Django + DRF
│   ├── urls.py             # Configuration des URLs
│   ├── wsgi.py             # Configuration WSGI
│   └── asgi.py             # Configuration ASGI
├── 📁 apps/                 # Applications Django
│   ├── users/              # Gestion des utilisateurs
│   ├── products/           # Gestion des produits
│   └── orders/             # Gestion des commandes
├── 📁 media/                # Fichiers uploadés
├── 📁 static/               # Fichiers statiques
├── 📁 django-env/           # Environnement virtuel (ignoré par Git)
├── manage.py                # Script de gestion Django
├── requirements.txt         # Dépendances Python
├── .gitignore              # Fichiers ignorés par Git
└── README.md               # Ce fichier
```

## 🛠️ Technologies

- **Django 5.2.5** - Framework web Python robuste
- **Django REST Framework 3.16.1** - Framework API REST performant
- **Python 3.13** - Langage de programmation moderne
- **SQLite** - Base de données légère (dev) / PostgreSQL (prod)

## 🚀 Installation

### Prérequis
- Python 3.13+
- pip
- Git

### 1. Cloner le projet
```bash
git clone <repository-url>
cd Naca
```

### 2. Créer l'environnement virtuel
```bash
python -m venv django-env
source django-env/bin/activate  # macOS/Linux
# ou
django-env\Scripts\activate     # Windows
```

### 3. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 4. Configuration de la base de données
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser  # Optionnel
```

### 5. Lancer le serveur
```bash
python manage.py runserver
```

🌐 **API accessible sur :** http://127.0.0.1:8000/
🔧 **Admin Django sur :** http://127.0.0.1:8000/admin/

## ⚙️ Configuration

### Variables d'environnement
Créez un fichier `.env` à la racine :
```env
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
```

### Django REST Framework
- **Authentification** : Session + Basic
- **Permissions** : IsAuthenticated par défaut
- **Pagination** : 10 éléments par page
- **Throttling** : Configurable par utilisateur

## 🏗️ Développement

### Créer une nouvelle application
```bash
python manage.py startapp nom_app apps/
```

### Structure d'une application
```
apps/nom_app/
├── __init__.py
├── admin.py
├── apps.py
├── models.py
├── serializers.py      # DRF
├── views.py
├── urls.py
└── tests.py
```

### Modèles Django
```python
from django.db import models
from django.utils import timezone

class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
```

### Sérialiseurs DRF
```python
from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
```

### Vues API
```python
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Product
from .serializers import ProductSerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Product.objects.filter(is_active=True)
```

## 🧪 Tests

### Lancer les tests
```bash
# Tous les tests
python manage.py test

# Tests d'une application
python manage.py test apps.users

# Tests avec couverture
python manage.py test --verbosity=2
```

### Tests API
```python
from rest_framework.test import APITestCase
from django.urls import reverse
from apps.users.models import User

class ProductAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_create_product(self):
        url = reverse('api:product-list')
        data = {'name': 'Test Product', 'price': '29.99'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)
```

## 📊 Performance

### Optimisations recommandées
- **Eager Loading** : `Product.objects.select_related('category')`
- **Pagination** : Limiter à 20-50 éléments par page
- **Cache** : Utiliser Redis pour les données fréquentes
- **Indexes** : Ajouter des index sur les colonnes de recherche

### Monitoring
```bash
# Vérifier la configuration
python manage.py check --deploy

# Analyser les requêtes
python manage.py shell
>>> from django.db import connection
>>> connection.queries
```

## 🚀 Déploiement

### Production
```bash
# Collecter les fichiers statiques
python manage.py collectstatic

# Vérifier la configuration
python manage.py check --deploy

# Gunicorn (recommandé)
gunicorn AnacBackend.wsgi:application
```

### Docker (optionnel)
```dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["gunicorn", "AnacBackend.wsgi:application"]
```

## 🤝 Contribution

### Workflow Git
1. **Fork** le projet
2. **Branche** : `git checkout -b feature/nouvelle-fonctionnalite`
3. **Commit** : `git commit -am 'Ajouter nouvelle fonctionnalité'`
4. **Push** : `git push origin feature/nouvelle-fonctionnalite'`
5. **Pull Request** : Créer une PR avec description détaillée

### Standards de code
- **PEP 8** : Style Python
- **Docstrings** : Documentation des fonctions
- **Tests** : Couverture > 80%
- **Type hints** : Annotations de type (optionnel)

## 📚 Ressources

- [Documentation Django](https://docs.djangoproject.com/)
- [DRF Documentation](https://www.django-rest-framework.org/)
- [Django Best Practices](https://djangobestpractices.com/)
- [Real Python Django](https://realpython.com/tutorials/django/)

## 📞 Support

- **Issues** : GitHub Issues
- **Documentation** : Wiki du projet
- **Équipe** : Contactez l'équipe de développement

## 📄 Licence

Ce projet est sous licence privée. Tous droits réservés.

---

**🚀 Développé avec ❤️ par l'équipe Anac**
