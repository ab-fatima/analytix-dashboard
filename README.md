# 📊 AnalytiX — E-Commerce Dashboard

Dashboard analytics fullstack : **FastAPI** (backend) + **Vue.js 3** (frontend) + **PostgreSQL**.

![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green?logo=fastapi)
![Vue.js](https://img.shields.io/badge/Vue.js-3.4-42b883?logo=vue.js)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue?logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker)

---

## ✨ Features

- KPI Cards : Revenu, Commandes, Clients, Panier moyen
- Graphique revenu (line chart)
- Commandes par statut (donut chart)
- Top produits (bar chart)
- Ventes par catégorie (polar area)
- Tableau des dernières commandes
- Auth JWT
- 300 commandes de démo générées automatiquement

---

## 🚀 Lancement

### Prérequis
- Docker Desktop ouvert (point vert "Engine running")

### Une seule commande

```bash
git clone https://github.com/ton-username/analytix.git
cd analytix
docker-compose up --build
```

Attends 2-3 minutes que tout démarre.

### Accès

| URL | Description |
|-----|-------------|
| http://localhost:3001 | Dashboard Vue.js |
| http://localhost:8001/docs | API Documentation |

### Login
```
Email:    admin@demo.com
Password: password
```

---

## 🏗️ Structure

```
analytix/
├── backend/
│   ├── main.py          # API FastAPI complète
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Dashboard.vue  # KPIs + 4 graphiques
│   │   │   └── Login.vue
│   │   ├── App.vue            # Layout sidebar
│   │   └── main.js
│   ├── index.html
│   ├── vite.config.js
│   ├── nginx.conf
│   └── Dockerfile
└── docker-compose.yml
```

---

## 🛠️ Tech Stack

| Layer | Technologie |
|-------|-------------|
| Backend | FastAPI + SQLAlchemy |
| Frontend | Vue.js 3 + Vue Router |
| Charts | Chart.js 4 |
| Database | PostgreSQL 16 |
| Build | Vite 5 |
| Container | Docker + Docker Compose |

---
## Demo

[![Watch Demo](https://img.youtube.com/vi/C6vMQj1Oun0/0.jpg)](https://youtu.be/SV5E75SuZj4)
## 📄 License

MIT
