# RAG Finance - Frontend React

Frontend de l'application RAG Finance construit avec React, Tailwind CSS et Vite.

## 🚀 Fonctionnalités

- ✅ Authentification JWT (Login/Register)
- ✅ Menus différents selon le rôle (Admin/User)
- ✅ Routes protégées
- ✅ Design moderne avec Tailwind CSS
- ✅ Responsive
- ✅ Visualisation des taux de change avec graphiques (Recharts)

## 📋 Pages Implémentées

### Pages Publiques
- `/login` - Connexion
- `/register` - Inscription

### Pages Authentifiées (User + Admin)
- `/dashboard` - Tableau de bord
- `/search` - Recherche sémantique
- `/qa` - Questions/Réponses RAG
- `/exchange-rates` - Visualisation taux de change EUR/MAD et USD/MAD

### Pages Admin Uniquement
- `/upload` - Upload de fichiers PDF/TXT
- `/process` - Traitement des documents
- `/index` - Indexation vectorielle
- `/users` - Gestion des utilisateurs

### Pages Admin - Gestion Base de Données
- `/admin/projects` - Gestion des projets
- `/admin/assets` - Gestion des assets (fichiers)
- `/admin/chunks` - Gestion des chunks de documents
- `/admin/conversations` - Gestion des conversations
- `/admin/messages` - Gestion des messages
- `/admin/vectors` - Gestion des vecteurs (Qdrant)
- `/admin/exchange-rates` - Gestion des taux de change (admin)

## 🛠️ Technologies

- **React 18** - Framework UI
- **React Router 6** - Navigation
- **Tailwind CSS 3** - Styling
- **Axios** - API calls
- **Vite 5** - Build tool
- **JWT Decode** - Token management
- **Recharts** - Graphiques et visualisation

## 🐳 Lancer avec Docker

```bash
cd docker
docker-compose up -d
```

Le frontend sera accessible sur **http://localhost**

## 💻 Développement Local (sans Docker)

```bash
cd frontend

# Installer les dépendances
npm install

# Lancer en mode développement
npm run dev

# Build pour production
npm run build

# Prévisualiser le build
npm run preview
```

## 🔐 Comptes de Test

### Admin
- Username: `admin`
- Password: `admin`

### User
- Username: `testuser`
- Password: (à définir lors de l'inscription)

## 📁 Structure du Projet

```
frontend/
├── src/
│   ├── components/              # Composants réutilisables
│   │   ├── Navbar.jsx          # Menu navigation
│   │   ├── ProtectedRoute.jsx  # Protection routes
│   │   ├── ProjectName.jsx     # Composant nom projet
│   │   ├── ProjectLanguage.jsx # Composant langue projet
│   │   └── admin/              # Composants admin
│   ├── pages/                  # Pages de l'application
│   │   ├── Login.jsx
│   │   ├── Register.jsx
│   │   ├── Dashboard.jsx
│   │   ├── Upload.jsx
│   │   ├── Process.jsx
│   │   ├── IndexPage.jsx
│   │   ├── Search.jsx
│   │   ├── QA.jsx
│   │   ├── Users.jsx
│   │   ├── ExchangeRates.jsx
│   │   └── admin/              # Pages admin DB
│   │       ├── AdminProjects.jsx
│   │       ├── AdminAssets.jsx
│   │       ├── AdminChunks.jsx
│   │       ├── AdminConversations.jsx
│   │       ├── AdminMessages.jsx
│   │       ├── AdminVectors.jsx
│   │       └── AdminExchangeRates.jsx
│   ├── services/               # API calls
│   │   └── api.js
│   ├── context/                # Context React
│   │   └── AuthContext.jsx
│   ├── hooks/                  # Custom hooks
│   │   └── useConversation.js
│   ├── App.jsx                 # Routes principales
│   ├── main.jsx                # Point d'entrée
│   └── index.css               # Styles Tailwind
├── Dockerfile                  # Configuration Docker
├── nginx.conf                  # Config Nginx
├── vite.config.js              # Config Vite
├── tailwind.config.js          # Config Tailwind
└── package.json
```

## 🔄 Flux d'Authentification

1. User se connecte → Token JWT reçu
2. Token stocké dans localStorage
3. Token ajouté automatiquement à chaque requête API
4. Si token expiré → Redirection vers login
5. Menu affiché selon le rôle (admin/user)

## 🎨 Personnalisation

### Couleurs Tailwind
Modifier dans `tailwind.config.js`:

```js
colors: {
  primary: '#3B82F6',    // Bleu
  secondary: '#10B981',  // Vert
}
```

### API URL
Modifier dans `src/services/api.js`:

```js
const API_URL = '/api/v1';
```

## 🐛 Troubleshooting

### Le frontend ne charge pas
```bash
# Vérifier que nginx redirige bien
docker logs nginx

# Rebuild le frontend
docker-compose build frontend
docker-compose up -d
```

### Erreurs CORS
Vérifier que nginx proxy bien les requêtes API vers FastAPI (port 8000)

### Token non transmis
Vérifier le header `Authorization` dans nginx.conf
