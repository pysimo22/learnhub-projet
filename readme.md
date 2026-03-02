# 📚 LearnHub — Plateforme de Gestion de Cours en Ligne

> Base de données MongoDB + API REST Python Flask + Interface HTML

---

## 🛠️ Technologies utilisées

| Technologie | Rôle |
|-------------|------|
| **MongoDB** | Base de données NoSQL |
| **Python Flask** | API REST backend |
| **PyMongo** | Driver MongoDB pour Python |
| **Flask-CORS** | Gestion des requêtes cross-origin |
| **HTML / CSS / JavaScript** | Interface frontend (Vanilla JS) |
| **Postman** | Test des endpoints API |

---

## 📁 Structure du projet

```
learnhub-projet/
│
├── seed.mongosh.js               # Insertion des données initiales
├── queries.mongosh.js            # Requêtes MongoDB
├── server.py                     # API REST Flask
├── requirements.txt              # Dépendances Python
├── .env                          # Variables d'environnement
│
├── index.html                    # Catalogue des cours
├── course.html                   # Détail d'un cours
├── dashboard.html                # Dashboard utilisateur
├── enrollment.html               # Formulaire d'inscription
│
└── My Collection.postman_collection.json   # Collection Postman
```

---

## 🗄️ Base de données

La base de données **learnhub** contient 5 collections :

| Collection | Documents | Description |
|------------|-----------|-------------|
| `users` | 20 | Étudiants et instructeurs |
| `courses` | 15 | Cours avec catégorie, prix et difficulté |
| `lessons` | 30 | Leçons rattachées aux cours |
| `enrollments` | 25 | Inscriptions des étudiants |
| `reviews` | 20 | Avis et notations |

---

## 🚀 Installation et démarrage

### Prérequis
- Python 3.x
- MongoDB (en cours d'exécution sur le port 27017)
- pip

### 1. Cloner le projet

```bash
git clone https://github.com/ton-username/learnhub-projet.git
cd learnhub-projet
```

### 2. Installer les dépendances Python

```bash
pip install -r requirements.txt
```

### 3. Configurer les variables d'environnement

Créer un fichier `.env` à la racine :

```env
MONGO_URI=mongodb://localhost:27017
PORT=3000
```

### 4. Insérer les données initiales

```bash
mongosh < seed.mongosh.js
```

### 5. Démarrer le serveur

```bash
python server.py
```

Le serveur démarre sur **http://localhost:3000**

### 6. Ouvrir le frontend

Ouvrir `index.html` directement dans le navigateur.

---

## 📡 Endpoints API

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/api/courses` | Liste des cours (filtres + pagination) |
| `GET` | `/api/courses/search?q=` | Recherche textuelle |
| `POST` | `/api/courses/bulk` | Insérer plusieurs cours |
| `DELETE` | `/api/courses/:id` | Supprimer un cours |
| `GET` | `/api/users/:id` | Récupérer un utilisateur |
| `POST` | `/api/users` | Créer un utilisateur |
| `PATCH` | `/api/users/:id` | Mettre à jour un utilisateur |
| `GET` | `/api/users/:id/dashboard` | Dashboard utilisateur |
| `POST` | `/api/enrollments` | S'inscrire à un cours |
| `POST` | `/api/reviews` | Soumettre un avis |
| `GET` | `/api/stats` | Statistiques de la plateforme |
| `GET` | `/api/export` | Export JSON complet |

---

## 👤 Auteur

**Simo** — 2025–2026