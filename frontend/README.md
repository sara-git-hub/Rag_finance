# RAG Finance - Frontend React

Frontend de l'application RAG Finance construit avec React, Tailwind CSS et Vite.

## 🚀 Fonctionnalités

- ✅ Authentification JWT (Login/Register)
- ✅ Menus différents selon le rôle (Admin/User)
- ✅ Routes protégées
- ✅ Design moderne avec Tailwind CSS
- ✅ Responsive

## 📋 Pages Implémentées

### Pages Publiques
- `/login` - Connexion
- `/register` - Inscription

### Pages Authentifiées
- `/dashboard` - Tableau de bord
- `/search` - Recherche (User + Admin)
- `/qa` - Questions/Réponses (User + Admin)

### Pages Admin Uniquement
- `/upload` - Upload de fichiers
- `/process` - Traitement des documents
- `/index` - Indexation vectorielle
- `/users` - Gestion des utilisateurs

## 🛠️ Technologies

- **React 18** - Framework UI
- **React Router 6** - Navigation
- **Tailwind CSS 3** - Styling
- **Axios** - API calls
- **Vite** - Build tool
- **JWT Decode** - Token management

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
│   ├── components/         # Composants réutilisables
│   │   ├── Navbar.jsx     # Menu navigation
│   │   └── ProtectedRoute.jsx
│   ├── pages/             # Pages de l'application
│   │   ├── Login.jsx
│   │   ├── Register.jsx
│   │   └── Dashboard.jsx
│   ├── services/          # API calls
│   │   └── api.js
│   ├── context/           # Context React
│   │   └── AuthContext.jsx
│   ├── App.jsx            # Routes principales
│   ├── main.jsx           # Point d'entrée
│   └── index.css          # Styles Tailwind
├── Dockerfile             # Configuration Docker
├── nginx.conf             # Config Nginx
├── vite.config.js         # Config Vite
├── tailwind.config.js     # Config Tailwind
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

## 📝 À Implémenter

Les pages suivantes ont des placeholders et doivent être implémentées:

- [ ] Page Upload
- [ ] Page Process
- [ ] Page Indexation
- [ ] Page Recherche
- [ ] Page Q&A
- [ ] Page Gestion Utilisateurs

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
