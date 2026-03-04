# 📚 LearnHub — MongoDB Database & REST API for an E-Learning Platform

LearnHub est une **plateforme d'apprentissage en ligne** permettant la gestion de cours, d’utilisateurs et d’inscriptions.

Ce projet démontre la **modélisation et la manipulation d’une base de données MongoDB**, l’exposition des données via une **API REST développée avec Flask**, ainsi qu’une **interface web simple en HTML/CSS/JavaScript**.

---

# 🧰 Technologies utilisées

| Technologie | Rôle |
|-------------|------|
| MongoDB | Base de données NoSQL |
| Python Flask | Développement de l'API REST |
| PyMongo | Communication entre Python et MongoDB |
| HTML / CSS / JavaScript | Interface utilisateur |
| Postman | Test des endpoints API |

---

# 🏗 Architecture du projet

Le projet suit une architecture simple en **3 couches** :

```
Frontend (HTML / JS)
        ↓
API REST Flask
        ↓
MongoDB Database
```

---

# 📁 Structure du projet

```
learnhub-projet/
│
├── seed.mongosh.js
│   Script d’initialisation de la base MongoDB
│
├── queries.mongosh.js
│   Ensemble de requêtes MongoDB (CRUD + requêtes métier)
│
├── server.py
│   API REST développée avec Flask
│
├── requirements.txt
│   Dépendances Python
│
├── .env.example
│   Exemple de configuration des variables d’environnement
│
├── index.html
│   Catalogue des cours
│
├── course.html
│   Page détail d’un cours
│
├── dashboard.html
│   Dashboard utilisateur
│
├── enrollment.html
│   Formulaire d'inscription
│
└── My Collection.postman_collection.json
    Collection Postman pour tester l’API
```

---

# 🗄 Modélisation de la base de données

La base **learnhub** est composée de **5 collections principales** :

| Collection | Documents | Description |
|------------|-----------|-------------|
| users | 20 | Étudiants et instructeurs |
| courses | 15 | Cours avec catégorie, difficulté et prix |
| lessons | 30 | Leçons associées aux cours |
| enrollments | 25 | Inscriptions des étudiants |
| reviews | 20 | Avis et notes des cours |

---

# 🚀 Installation et exécution

## Prérequis

- Python 3.x
- MongoDB installé et en cours d'exécution
- pip
- mongosh

---

## 1️⃣ Cloner le projet

```bash
git clone https://github.com/pysimo22/learnhub-projet
cd learnhub-projet
```

---

## 2️⃣ Installer les dépendances

```bash
pip install -r requirements.txt
```

---

## 3️⃣ Configurer les variables d’environnement

Créer un fichier `.env` à la racine du projet :

```
MONGO_URI=mongodb://localhost:27017
PORT=3000
```

---

## 4️⃣ Initialiser la base de données

```bash
mongosh < seed.mongosh.js
```

Ce script crée la base **learnhub** et insère les données initiales.

---

## 5️⃣ Lancer l’API

```bash
python server.py
```

Le serveur sera accessible sur :

```
http://localhost:3000
```

---

## 6️⃣ Ouvrir l’interface web

Ouvrir simplement :

```
index.html
```

dans votre navigateur.

---

# 📡 Endpoints principaux de l’API

| Méthode | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/courses | Liste des cours (filtrage + pagination) |
| GET | /api/courses/search?q= | Recherche de cours |
| POST | /api/courses/bulk | Ajout de plusieurs cours |
| DELETE | /api/courses/:id | Suppression d’un cours |
| POST | /api/users | Création d’un utilisateur |
| GET | /api/users/:id | Récupération d’un utilisateur |
| PATCH | /api/users/:id | Mise à jour d’un utilisateur |
| GET | /api/users/:id/dashboard | Dashboard utilisateur |
| POST | /api/enrollments | Inscription à un cours |
| POST | /api/reviews | Ajout d’un avis |
| GET | /api/stats | Statistiques globales |
| GET | /api/export | Export JSON de la base |

---

# 🧪 Tests API

Les endpoints peuvent être testés avec :

- Postman
- curl
- le frontend HTML fourni

Une collection Postman est incluse dans le projet.

---

# 📄 Rapport

Le rapport du projet est disponible dans le repository :

```
rapport-projet.docx
```

Il décrit :

- la modélisation de la base
- les requêtes MongoDB
- l’implémentation de l’API
- la logique métier
- les fonctionnalités bonus

---

# 👨‍💻 Auteur

Mohamed Touzani  
B3 Cybersécurité — 2025 / 2026

---

# ⭐ Projet académique

Ce projet a été réalisé dans le cadre d’un exercice de **conception et manipulation d’une base de données MongoDB pour une plateforme d’apprentissage en ligne**.