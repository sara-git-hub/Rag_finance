# Phase 3 : Analyse Frontend (React)

> **Statut** : ✅ Complétée
> **Durée effective** : 4 heures
> **Date** : Décembre 2025

---

## 📋 Synthèse Globale

**Frontend React 18 complet analysé** :
- **19 routes** (2 publiques, 4 utilisateur, 13 admin)
- **17 pages** (Login, Register, Dashboard, etc.)
- **6 composants réutilisables**
- **1 service API centralisé** (api.js avec interceptors Axios)
- **1 Context** (AuthContext avec JWT)
- **1 Hook personnalisé** (useConversation pour RAG)
- **Total** : ~2828 lignes de code JavaScript/JSX

---

## 1. Structure & Architecture

### Vue d'ensemble

```
frontend/src/
├── main.jsx                    # Point d'entrée React
├── App.jsx                     # Configuration des routes
├── index.css                   # Styles globaux
│
├── pages/                      # 17 pages
│   ├── Login.jsx              # Auth
│   ├── Register.jsx           # Auth
│   ├── Dashboard.jsx          # Accueil
│   ├── Upload.jsx             # Admin - Upload PDFs
│   ├── Process.jsx            # Admin - Processing
│   ├── IndexPage.jsx          # Admin - Indexation
│   ├── Users.jsx              # Admin - Gestion users
│   ├── Search.jsx             # User - Recherche vectorielle
│   ├── QA.jsx                 # User - Q&A conversationnel
│   ├── ExchangeRates.jsx      # User - Graphiques taux
│   └── admin/                 # Pages admin CRUD
│       ├── AdminProjects.jsx
│       ├── AdminAssets.jsx
│       ├── AdminChunks.jsx
│       ├── AdminConversations.jsx
│       ├── AdminMessages.jsx
│       ├── AdminVectors.jsx
│       └── AdminExchangeRates.jsx
│
├── components/                 # 6 composants réutilisables
│   ├── ProtectedRoute.jsx     # HOC pour protection routes
│   ├── Navbar.jsx             # Menu navigation
│   ├── ProjectName.jsx        # Affichage nom projet
│   ├── ProjectLanguage.jsx    # Sélecteur langue (FR/EN/AR)
│   └── admin/
│       ├── AdminTable.jsx     # Table CRUD réutilisable
│       └── ConfirmModal.jsx   # Modal confirmation
│
├── services/                   # Services API
│   └── api.js                 # Axios centralisé + interceptors
│
├── context/                    # State management
│   └── AuthContext.jsx        # JWT + user state
│
├── hooks/                      # Custom hooks
│   └── useConversation.js     # Hook RAG conversationnel
│
└── utils/                      # Utilitaires
```

### Technologies & Versions

| Technologie | Version | Usage |
|-------------|---------|-------|
| **React** | 18.x | UI Library (hooks, context) |
| **React Router** | 6.x | Client-side routing (BrowserRouter) |
| **Axios** | Latest | HTTP client avec interceptors |
| **Tailwind CSS** | 3.x | Utility-first CSS framework |
| **Vite** | 5.x | Build tool (dev server + production) |
| **jwt-decode** | Latest | Décodage JWT côté client |

---

## 2. Routing & Routes (19 routes)

### Configuration (App.jsx)

**Architecture** : BrowserRouter avec AuthProvider global

```jsx
<AuthProvider>
  <Router>
    <Routes>
      {/* 19 routes définies */}
    </Routes>
  </Router>
</AuthProvider>
```

### Routes Publiques (2)

| Path | Component | Description | Auth |
|------|-----------|-------------|------|
| `/login` | Login | Authentification (JWT) | Public |
| `/register` | Register | Inscription (1er = admin auto) | Public |

**Redirection par défaut** : `/` → `/login`

### Routes Utilisateur (4) - Auth Required

| Path | Component | Description | Rôle |
|------|-----------|-------------|------|
| `/dashboard` | Dashboard | Page d'accueil (cards fonctionnalités) | User + Admin |
| `/search` | Search | Recherche vectorielle sémantique (top K) | User + Admin |
| `/qa` | QA | Q&A conversationnel avec historique | User + Admin |
| `/exchange-rates` | ExchangeRates | Graphiques MAD/EUR, MAD/USD + prédictions | User + Admin |

### Routes Admin (13) - Admin Only

#### Workflow RAG (4)
| Path | Component | Description |
|------|-----------|-------------|
| `/upload` | Upload | Upload PDFs par projet (max 100MB) |
| `/process` | Process | Processing : extraction texte + chunking |
| `/index` | IndexPage | Indexation vecteurs dans Qdrant |
| `/users` | Users | Gestion utilisateurs (liste + rôles) |

#### CRUD Admin (7)
| Path | Component | Description |
|------|-----------|-------------|
| `/admin/projects` | AdminProjects | CRUD projets |
| `/admin/assets` | AdminAssets | CRUD assets (fichiers PDF) |
| `/admin/chunks` | AdminChunks | CRUD chunks (morceaux texte) |
| `/admin/conversations` | AdminConversations | CRUD conversations |
| `/admin/messages` | AdminMessages | CRUD messages (Q&A) |
| `/admin/vectors` | AdminVectors | Gestion collections vectorielles |
| `/admin/exchange-rates` | AdminExchangeRates | ML : train LSTM, générer prédictions |

### Protection des Routes (ProtectedRoute.jsx)

**HOC (Higher-Order Component)** pour sécuriser l'accès :

```jsx
<ProtectedRoute requireAdmin>
  <Upload />
</ProtectedRoute>
```

**Logique de protection** :
1. Si `loading` : Afficher "Chargement..."
2. Si non authentifié : `<Navigate to="/login" />`
3. Si admin requis ET user non admin : Page "Accès Refusé"
4. Sinon : Afficher `children`

---

## 3. Services API (api.js)

### Architecture Axios Centralisée

**Instance Axios configurée** :
```javascript
const api = axios.create({
  baseURL: '/api/v1',
  headers: { 'Content-Type': 'application/json' }
});
```

### Interceptors

#### Request Interceptor (JWT Auto-inject)
```javascript
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

**Avantage** : Pas besoin d'ajouter manuellement le token à chaque requête.

#### Response Interceptor (Auto-logout 401)
```javascript
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
```

**Avantage** : Déconnexion automatique si token expiré.

### Modules API (6 modules)

#### 1. authAPI - Authentification & User Management

| Fonction | Méthode | Endpoint | Description |
|----------|---------|----------|-------------|
| `login()` | POST | `/auth/login` | Login → JWT (24h) |
| `register()` | POST | `/auth/register` | Inscription |
| `getMe()` | GET | `/auth/me` | User actuel |
| `getAllUsers()` | GET | `/auth/users` | Liste users (admin) |
| `createUser()` | POST | `/auth/admin/users` | **Créer user/admin (admin)** |
| `updateUserPassword()` | PATCH | `/auth/users/{username}/password` | **Modifier mot de passe (admin)** |
| `deleteUser()` | DELETE | `/auth/users/{username}` | **Supprimer user (admin)** |

**Nouveaux endpoints (Décembre 2025)** :
- Gestion complète des utilisateurs par les administrateurs
- Protection auto-suppression dans l'interface (bouton désactivé)

#### 2. dataAPI - Gestion Fichiers

| Fonction | Méthode | Endpoint | Description |
|----------|---------|----------|-------------|
| `uploadFile()` | POST | `/data/upload/{projectId}` | Upload PDF (FormData) |
| `processData()` | POST | `/data/process/{projectId}` | Process → chunks |
| `getProjectLanguage()` | GET | `/data/project/{id}/language` | Récupérer langue |
| `updateProjectLanguage()` | PUT | `/data/project/{id}/language` | Modifier langue (FR/EN/AR) |

**Particularité upload** :
```javascript
const formData = new FormData();
formData.append('file', file);
return api.post(`/data/upload/${projectId}`, formData, {
  headers: { 'Content-Type': 'multipart/form-data' }
});
```

#### 3. nlpAPI - Pipeline RAG

| Fonction | Méthode | Endpoint | Description |
|----------|---------|----------|-------------|
| `pushToIndex()` | POST | `/nlp/index/push/{projectId}` | Indexer chunks |
| `getIndexInfo()` | GET | `/nlp/index/info/{projectId}` | Stats collection |
| `search()` | POST | `/nlp/index/search/{projectId}` | Recherche similarité |
| `answer()` | POST | `/nlp/index/answer/{projectId}` | **RAG Q&A** |

#### 4. conversationAPI - Historique Chat

| Fonction | Méthode | Endpoint | Description |
|----------|---------|----------|-------------|
| `create()` | POST | `/conversations/create` | Créer conversation |
| `listByProject()` | GET | `/conversations/project/{id}` | Liste par projet |
| `getMessages()` | GET | `/conversations/{id}/messages` | Messages historique |
| `delete()` | DELETE | `/conversations/{id}` | Supprimer conversation |

#### 5. adminAPI - CRUD Complet

**7 entités gérées** : Projects, Assets, Chunks, Conversations, Messages, Vectors, Exchange Rates

**Pattern commun** :
- `get{Entity}(page, pageSize, filters)` : Pagination + filtres
- `delete{Entity}(id)` : Suppression

**Exemple Assets** :
```javascript
getAssets: (page = 1, pageSize = 20, projectId = null, assetType = null) => {
  let url = `/admin/assets?page=${page}&page_size=${pageSize}`;
  if (projectId) url += `&project_id=${projectId}`;
  if (assetType) url += `&asset_type=${assetType}`;
  return api.get(url);
}
```

#### 6. publicAPI - Taux de Change

| Fonction | Méthode | Endpoint | Description |
|----------|---------|----------|-------------|
| `getLatestExchangeRates()` | GET | `/exchange-rates/latest` | Derniers taux |
| `getExchangePredictions()` | GET | `/exchange-rates/predictions` | Prédictions LSTM (7j) |
| `getExchangeHistory()` | GET | `/exchange-rates/history` | Historique (max 365j) |

---

## 4. State Management

### AuthContext - JWT & User State

**Architecture** : Context API avec provider global

#### État géré
```javascript
{
  user: { username: 'john', role: 'admin' },
  loading: false
}
```

#### Fonctions exposées

| Fonction | Description | Retour |
|----------|-------------|--------|
| `login(username, password)` | Authentification | `{ success, error }` |
| `register(username, email, password)` | Inscription | `{ success, error }` |
| `logout()` | Déconnexion (clear localStorage) | void |
| `isAuthenticated()` | Vérifier si user connecté | boolean |
| `isAdmin()` | Vérifier si user est admin | boolean |

#### Initialisation au montage

**Auto-login depuis localStorage** :
```javascript
useEffect(() => {
  const token = localStorage.getItem('token');
  if (token) {
    try {
      const decoded = jwtDecode(token);
      // Vérifier expiration
      if (decoded.exp * 1000 > Date.now()) {
        setUser({ username: decoded.sub, role: decoded.role });
      } else {
        localStorage.removeItem('token');
      }
    } catch (error) {
      localStorage.removeItem('token');
    }
  }
  setLoading(false);
}, []);
```

**Avantages** :
- Pas besoin de re-login après rafraîchissement page
- Validation expiration token
- Récupération automatique user depuis JWT

#### Usage dans composants

```jsx
import { useAuth } from '../context/AuthContext';

const MyComponent = () => {
  const { user, isAdmin, logout } = useAuth();

  return (
    <div>
      <p>Bonjour {user?.username}</p>
      {isAdmin() && <AdminPanel />}
      <button onClick={logout}>Déconnexion</button>
    </div>
  );
};
```

---

## 5. Custom Hooks

### useConversation - RAG Conversationnel

**Hook personnalisé** pour gérer les conversations Q&A avec historique.

#### État géré
```javascript
{
  conversations: [],           // Liste conversations projet
  currentConversation: null,   // Conversation active
  messages: [],                // Messages conversation actuelle
  loading: false,              // Chargement requête
  error: null                  // Erreur éventuelle
}
```

#### Fonctions exposées (8)

| Fonction | Description | Paramètres | Retour |
|----------|-------------|------------|--------|
| `createConversation()` | Créer nouvelle conversation | `title?` | `conversation` |
| `loadConversation()` | Charger conversation + messages | `conversationId` | void |
| `askQuestion()` | Poser question RAG | `question, limit=5` | `{ answer, sources }` |
| `deleteConversation()` | Supprimer conversation | `conversationId` | `boolean` |
| `startNewConversation()` | Reset état (nouvelle conv) | - | void |
| `refreshConversations()` | Recharger liste | - | void |
| `hasMessages` | Helper : messages > 0 | - | `boolean` |
| `hasConversations` | Helper : conversations > 0 | - | `boolean` |

#### Logique clé : askQuestion

**Optimistic UI Update** :
```javascript
const askQuestion = async (question, limit = 5) => {
  // 1. Si pas de conversation, en créer une auto
  let conversationId = currentConversation?.conversation_id;
  if (!conversationId) {
    const newConv = await createConversation();
    conversationId = newConv.conversation_id;
  }

  // 2. Ajouter optimistiquement la question (UI réactive)
  const userMessage = {
    message_id: Date.now(),
    role: 'user',
    content: question,
    created_at: new Date().toISOString()
  };
  setMessages(prev => [...prev, userMessage]);

  try {
    // 3. Envoyer au backend
    const response = await nlpAPI.answer(projectId, {
      text: question,
      limit,
      conversation_id: conversationId
    });

    // 4. Ajouter la réponse
    const assistantMessage = {
      message_id: Date.now() + 1,
      role: 'assistant',
      content: response.data.answer,
      created_at: new Date().toISOString()
    };
    setMessages(prev => [...prev, assistantMessage]);

    return response.data;
  } catch (err) {
    // 5. En cas d'erreur, retirer la question optimiste
    setMessages(prev => prev.slice(0, -1));
    setError(err.response?.data?.detail || 'Erreur');
    return null;
  }
};
```

**Avantages** :
- UX réactive (question apparaît immédiatement)
- Gestion automatique création conversation
- Rollback en cas d'erreur
- Historique conversationnel automatique

#### Usage dans QA.jsx

```jsx
const QA = () => {
  const [projectId, setProjectId] = useState('4');
  const [question, setQuestion] = useState('');

  const {
    conversations,
    currentConversation,
    messages,
    loading,
    error,
    askQuestion,
    deleteConversation
  } = useConversation(projectId);

  const handleAsk = async (e) => {
    e.preventDefault();
    if (!question.trim()) return;

    const result = await askQuestion(question, 5);
    if (result) {
      setQuestion(''); // Clear input
    }
  };

  return (
    <div>
      {/* Sidebar conversations */}
      {/* Messages area */}
      {/* Input form */}
    </div>
  );
};
```

---

## 6. Composants Réutilisables (6)

### 6.1 Navbar - Menu Navigation

**Responsabilités** :
- Menu adaptatif selon rôle (user/admin)
- Dropdown "Gestion Admin" (7 pages CRUD)
- Affichage user + badge rôle
- Bouton déconnexion
- Responsive mobile (menu vertical)

**Menus différenciés** :
```javascript
// User menu (4 items)
const userMenuItems = [
  { path: '/dashboard', label: 'Dashboard' },
  { path: '/search', label: 'Recherche' },
  { path: '/qa', label: 'Questions/Réponses' },
  { path: '/exchange-rates', label: 'Taux de Change' }
];

// Admin menu (8 items + dropdown 7 items)
const adminMenuItems = [
  ...userMenuItems,
  { path: '/upload', label: 'Upload Fichiers' },
  { path: '/process', label: 'Traitement' },
  { path: '/index', label: 'Indexation' },
  { path: '/users', label: 'Gestion Utilisateurs' }
];
```

**Dropdown admin** (7 pages CRUD) :
- `/admin/projects` → Projets
- `/admin/assets` → Fichiers
- `/admin/chunks` → Chunks
- `/admin/conversations` → Conversations
- `/admin/messages` → Messages
- `/admin/vectors` → Collections
- `/admin/exchange-rates` → Gestion Taux

**Styles** : Gradient bleu-violet, hover effects, badges rôle colorés.

### 6.2 ProtectedRoute - HOC Sécurité

**Pattern** : Higher-Order Component (HOC)

**Props** :
- `children` : Composant à protéger
- `requireAdmin` : Booléen (défaut: false)

**Logique** :
1. Si `loading` → "Chargement..."
2. Si non authentifié → Redirect `/login`
3. Si admin requis ET user non admin → Page "Accès Refusé" (avec bouton retour)
4. Sinon → Afficher `children`

**Usage** :
```jsx
// User + Admin
<ProtectedRoute>
  <Dashboard />
</ProtectedRoute>

// Admin only
<ProtectedRoute requireAdmin>
  <Upload />
</ProtectedRoute>
```

### 6.3 ProjectName - Affichage Nom Projet

**Responsabilités** :
- Afficher le nom du projet (ou "(Sans nom)" si vide)
- Fetch automatique depuis backend
- Mise à jour automatique lors du changement d'ID

**Props** :
- `projectId` : ID du projet

**Comportement** :
- Appelle `GET /data/project/{id}/language` pour récupérer le nom
- Affiche un badge gris avec le nom du projet
- Loading state pendant le chargement

**Usage** :
```jsx
<ProjectName projectId={projectId} />
```

### 6.4 ProjectLanguage - Sélecteur Langue

**Responsabilités** :
- Afficher langue actuelle du projet (FR/EN/AR)
- Permettre modification (admin seulement)
- Fetch automatique depuis backend
- Badge coloré selon langue

**Props** :
- `projectId` : ID du projet
- `isAdmin` : Booléen (afficher dropdown ou badge simple)

**Comportement** :
- **User** : Badge lecture seule (ex: "🇫🇷 Français")
- **Admin** : Dropdown modifiable (3 options)

**Langues supportées** :
```javascript
const languages = {
  fr: { label: 'Français', flag: '🇫🇷' },
  en: { label: 'English', flag: '🇬🇧' },
  ar: { label: 'العربية', flag: '🇲🇦' }
};
```

### 6.5 AdminTable - Table CRUD Réutilisable

**Composant générique** pour toutes les pages admin CRUD.

**Props** :
```javascript
{
  title: 'Gestion Projets',
  columns: [
    { key: 'project_id', label: 'ID' },
    { key: 'project_name', label: 'Nom', render: (val) => <b>{val}</b> }
  ],
  data: [...],
  totalPages: 5,
  currentPage: 1,
  onPageChange: (page) => {},
  onDelete: (item) => {},
  onRefresh: () => {},
  loading: false,
  filters: [
    { name: 'project_id', label: 'Project ID', type: 'number', value: '', placeholder: '...' }
  ],
  onFilterChange: (name, value) => {}
}
```

**Fonctionnalités** :
- **Table responsive** : Colonnes configurables
- **Pagination** : Précédent/Suivant + indicateur page
- **Filtres dynamiques** : Input text, number, select
- **Actions** : Boutons Modifier (optionnel) et Suppression par ligne
- **Edition** : Callback `onEdit()` optionnel pour modifier un élément
- **Suppression** : Bouton par ligne → Modal confirmation
- **Refresh** : Bouton actualiser
- **Rendu custom** : `column.render()` pour formater cellules
- **Loading states** : Skeleton pendant chargement

**Exemple usage** (AdminProjects.jsx) :
```jsx
<AdminTable
  title="Gestion des Projets"
  columns={[
    { key: 'project_id', label: 'ID' },
    { key: 'project_name', label: 'Nom', render: (val) => val || '(Sans nom)' },
    { key: 'project_language', label: 'Langue' },
    { key: 'created_at', label: 'Date', render: (val) => new Date(val).toLocaleDateString() }
  ]}
  data={projects}
  currentPage={currentPage}
  totalPages={totalPages}
  onPageChange={setCurrentPage}
  onEdit={(item) => openEditModal(item)}
  onDelete={(item) => adminAPI.deleteProject(item.project_id)}
  onRefresh={loadProjects}
  loading={loading}
/>
```

### 6.6 ConfirmModal - Modal Confirmation

**Modal générique** pour confirmer suppressions.

**Props** :
```javascript
{
  isOpen: boolean,
  onClose: () => {},
  onConfirm: () => {},
  title: 'Confirmer la suppression',
  message: 'Êtes-vous sûr ? Cette action est irréversible.',
  isLoading: false
}
```

**UI** :
- Overlay semi-transparent (z-index 50)
- Card centrée avec titre + message
- 2 boutons : "Annuler" (gris) et "Supprimer" (rouge)
- Loading state : "Suppression..." + disabled

**Utilisation** dans AdminTable :
```javascript
const [deleteModal, setDeleteModal] = useState({ isOpen: false, item: null });

// Ouvrir modal
<button onClick={() => setDeleteModal({ isOpen: true, item: row })}>
  Supprimer
</button>

// Modal
<ConfirmModal
  isOpen={deleteModal.isOpen}
  onClose={() => setDeleteModal({ isOpen: false, item: null })}
  onConfirm={handleDelete}
  isLoading={deleting}
/>
```

---

## 7. Pages Principales (17 pages)

### 7.1 Login - Authentification

**Fonctionnalités** :
- Formulaire username + password
- Validation côté client
- Affichage erreurs backend
- Redirection `/dashboard` après succès
- Lien vers `/register`

**Flux** :
1. Submit formulaire
2. `authAPI.login()` → JWT
3. `localStorage.setItem('token')`
4. `setUser({ username, role })` (Context)
5. `navigate('/dashboard')`

### 7.2 Dashboard - Accueil

**UI** : Grid de cards représentant les fonctionnalités

**Cards User** (3) :
- Recherche (icône loupe)
- Questions/Réponses (icône Q&A)
- Taux de Change (icône graphique)

**Cards Admin** (6 supplémentaires) :
- Upload Fichiers
- Traitement
- Indexation
- Gestion Utilisateurs
- + toutes les cards user

**Message personnalisé** selon rôle.

### 7.3 QA - Questions/Réponses Conversationnel

**Composant le plus complexe du frontend** (~309 lignes).

**Architecture** : Split layout 3 colonnes
```
[Sidebar Conversations] [Chat Area]
```

**Sidebar (gauche, 80px)** :
- Input Project ID
- Badge langue (ProjectLanguage)
- Bouton "Nouvelle Conversation"
- Liste conversations (scroll)
- Bouton supprimer par conversation

**Chat Area (centre)** :
- Header : Titre conversation + bouton toggle sidebar
- Messages : Bulles user (droite, bleu) / assistant (gauche, blanc)
- Auto-scroll vers bas
- Loading : 3 dots animés
- Input : Champ question + bouton "Envoyer"

**Fonctionnalités** :
- Historique conversationnel (Context API backend)
- Création auto conversation si aucune
- Optimistic UI (question apparaît immédiatement)
- Timestamps formatés (HH:mm)
- Erreurs affichées en rouge
- Responsive (toggle sidebar mobile)

**Hook utilisé** : `useConversation(projectId)`

**Code clé (auto-scroll)** :
```jsx
const messagesEndRef = useRef(null);

useEffect(() => {
  messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
}, [messages]);
```

### 7.4 Search - Recherche Vectorielle

**Fonctionnalités** :
- Input texte de recherche
- Sélecteur projet (ID)
- Slider K (nombre de résultats : 1-20)
- Affichage résultats avec scores de similarité
- Highlight metadata (source, page, etc.)

**Flux** :
1. User tape requête
2. `nlpAPI.search(projectId, { text, limit: k })`
3. Backend → Embeddings → Qdrant → Top K chunks
4. Affichage : Score + contenu + métadonnées

### 7.5 Upload - Upload Fichiers (Admin)

**Fonctionnalités** :
- Input Project ID
- Drag & drop OU sélection fichier
- Validation : PDF seulement, max 100MB
- Progress bar upload
- Affichage nom fichier + taille
- Bouton "Reset" pour nouveau upload

**Backend endpoint** : `POST /data/upload/{projectId}` (FormData)

### 7.6 Process - Traitement Documents (Admin)

**Fonctionnalités** :
- Input Project ID
- Sélection fichier à traiter (dropdown)
- Paramètres chunking :
  - `chunk_size` (défaut: 1000)
  - `overlap_size` (défaut: 200)
- Checkbox "Reset" (supprimer chunks existants)
- Bouton "Lancer traitement"
- Logs résultats (nombre chunks créés)

**Backend endpoint** : `POST /data/process/{projectId}`

### 7.7 IndexPage - Indexation Vectorielle (Admin)

**Fonctionnalités** :
- Input Project ID
- Bouton "Indexer dans Qdrant"
- Progress bar batch (50 chunks/batch)
- Stats collection (nombre vecteurs, dimension)
- Logs succès/erreur

**Backend endpoint** : `POST /nlp/index/push/{projectId}`

### 7.8 Users - Gestion Utilisateurs (Admin)

**Fonctionnalités** :
- Liste tous les users (table)
- Colonnes : Username, Email, Role, Statut, Actions
- **Formulaire d'ajout** : Création user/admin avec rôle sélectionnable
- **Bouton modifier mot de passe** : Modal pour changer le mot de passe
- **Bouton supprimer** : Suppression avec confirmation (désactivé pour soi-même)
- Statistiques : Total users, admins, users actifs
- Messages de feedback (succès/erreur)

**Backend endpoints** :
- `GET /auth/users` - Liste des utilisateurs
- `POST /auth/admin/users` - Créer un utilisateur
- `PATCH /auth/users/{username}/password` - Modifier mot de passe
- `DELETE /auth/users/{username}` - Supprimer utilisateur

**Protections UI** :
- Admin ne peut pas se supprimer lui-même (bouton désactivé)
- Confirmation avant suppression
- Formulaire repliable (toggle)

### 7.9 ExchangeRates - Taux de Change (User)

**Fonctionnalités** :
- Graphiques interactifs (Chart.js ou Recharts)
- 2 paires : MAD/EUR, MAD/USD
- Historique 30 derniers jours
- Prédictions LSTM 7 jours
- Sélecteur plage dates
- Export CSV/PNG

**Backend endpoints** :
- `GET /exchange-rates/history?currency_pair=MAD/EUR&days=30`
- `GET /exchange-rates/predictions?currency_pair=MAD/EUR&days_ahead=7`

### 7.10-7.16 Pages Admin CRUD (7 pages)

**Pattern commun** : Toutes utilisent `AdminTable` component

**AdminProjects** :
- Colonnes : ID, Language, Created At
- Filtre : Project ID
- Delete : Cascade (assets → chunks → vectors)

**AdminAssets** :
- Colonnes : Asset ID, Project ID, File ID, Type, Created At
- Filtres : Project ID, Asset Type
- Delete : Cascade (chunks → vectors)

**AdminChunks** :
- Colonnes : Chunk ID, Asset ID, Text Preview (100 chars), Created At
- Filtres : Project ID, Asset ID
- Delete : Simple (supprime chunk + vecteur associé)

**AdminConversations** :
- Colonnes : Conv ID, User ID, Project ID, Title, Created At
- Filtres : User ID, Project ID
- Delete : Cascade (messages)

**AdminMessages** :
- Colonnes : Message ID, Conv ID, Role, Content Preview, Created At
- Filtre : Conversation ID
- Delete : Simple

**AdminVectors** :
- Liste collections Qdrant
- Stats par collection (nombre vecteurs, dimension)
- Bouton "Voir vecteurs" → Liste paginated
- Delete collection (avec confirmation)

**AdminExchangeRates** :
- Boutons admin :
  - "Fetch Now" : Récupérer taux Bank Al-Maghrib immédiat
  - "Train Model" : Entraîner LSTM (params : currency_pair, days_history)
  - "Generate Predictions" : Générer prédictions (params : days_ahead)
- Statut scheduler (actif/inactif, dernière exécution)
- Logs ML (perte, epochs, métriques)

---

## 8. Patterns Architecturaux

| Pattern | Localisation | Usage |
|---------|--------------|-------|
| **Context API** | AuthContext | State management global (user, auth) |
| **Custom Hook** | useConversation | Logique réutilisable RAG conversationnel |
| **HOC** | ProtectedRoute | Wrapper sécurité routes |
| **Render Props** | AdminTable columns | Personnalisation rendu cellules |
| **Optimistic UI** | useConversation | Affichage immédiat avant réponse backend |
| **Interceptors** | api.js | Injection JWT auto + gestion 401 |
| **Compound Components** | Navbar + Dropdown | Composition UI flexible |
| **Container/Presentational** | Pages (container) + Components (presentational) | Séparation logique/UI |

---

## 9. Styling & UI/UX

### Tailwind CSS

**Utility classes** utilisées :
- Layout : `flex`, `grid`, `container`
- Spacing : `px-4`, `py-2`, `gap-6`
- Colors : `bg-primary`, `text-white`, `border-gray-300`
- Typography : `text-xl`, `font-bold`
- Effects : `hover:bg-blue-600`, `transition`, `shadow-lg`
- Responsive : `md:flex`, `lg:grid-cols-3`

**Thème personnalisé** (tailwind.config.js) :
```javascript
theme: {
  extend: {
    colors: {
      primary: '#2563eb'  // Bleu
    }
  }
}
```

### Design System

**Couleurs** :
- Primary : Bleu (#2563eb)
- Secondary : Violet (#7c3aed)
- Accent : Vert, Orange, Rouge
- Neutral : Gris (50, 100, 200, ..., 900)

**Composants** :
- Buttons : Arrondis (rounded-lg), hover effects
- Cards : Ombres (shadow-md, shadow-xl)
- Inputs : Focus ring (ring-2, ring-primary)
- Tables : Striped rows, hover rows
- Modals : Overlay semi-transparent (bg-opacity-50)

**Animations** :
- Loading : `animate-spin`, `animate-bounce`
- Transitions : `transition duration-200`
- Hover : Scale, color change

---

## 10. Performance & Optimisations

### Code Splitting

**Vite** : Automatic code splitting par route (lazy loading)

```jsx
// Au lieu de :
import Dashboard from './pages/Dashboard';

// Vite fait automatiquement :
// Dashboard.chunk.js (chargé uniquement si route visitée)
```

### Lazy Loading Images

**Pattern** : `loading="lazy"` sur `<img>`

### Memoization

**Opportunités** (non implémenté actuellement) :
- `React.memo()` sur composants lourds (AdminTable)
- `useMemo()` pour calculs coûteux (filtres, tris)
- `useCallback()` pour fonctions passées en props

### Optimistic Updates

**useConversation** : Messages ajoutés avant réponse backend → UX réactive.

### Debouncing

**Opportunités** (non implémenté) :
- Search input : Attendre 300ms avant requête
- Filtres admin : Éviter requêtes à chaque touche

---

## 11. Gestion des Erreurs

### Interceptor 401

**Auto-logout** si token expiré :
```javascript
if (error.response?.status === 401) {
  localStorage.removeItem('token');
  window.location.href = '/login';
}
```

### Try-Catch Pattern

**Toutes les fonctions async** dans hooks et composants :
```javascript
try {
  const response = await api.get('/endpoint');
  setData(response.data);
} catch (error) {
  setError(error.response?.data?.detail || 'Erreur');
}
```

### Affichage Erreurs UI

**Pattern** : Banner rouge en haut de formulaire
```jsx
{error && (
  <div className="bg-red-50 text-red-800 p-3 rounded-lg border border-red-200">
    {error}
  </div>
)}
```

---

## 12. Accessibilité & UX

### Loading States

**Pattern** : Skeleton loaders, spinners, "Chargement..."
```jsx
{loading ? (
  <div className="animate-spin w-5 h-5 border-2 border-white border-t-transparent rounded-full"></div>
) : (
  'Envoyer'
)}
```

### Disabled States

**Buttons** : `disabled={loading || !valid}` + `disabled:opacity-50`

### Feedback Visuel

- Hover effects : Changement couleur, scale
- Focus states : Ring bleu (ring-2, ring-primary)
- Success : Border verte, texte vert
- Error : Border rouge, texte rouge

### Responsive Design

**Breakpoints** :
- `sm` : 640px
- `md` : 768px (Navbar devient horizontal)
- `lg` : 1024px (Grid 3 colonnes)

**Mobile** :
- Navbar : Menu vertical pliable
- Tables : Scroll horizontal
- QA : Sidebar toggleable

---

## 13. Sécurité Frontend

### JWT Storage

**localStorage** : Token stocké côté client
- ✅ Simple
- ⚠️ Vulnérable XSS (scripts malveillants)

**Recommandation** : Utiliser `httpOnly` cookies (backend set cookie, frontend n'y accède pas)

### Validation Inputs

**Pattern** : Validation côté client AVANT envoi backend
```javascript
if (!question.trim()) return;
if (file.size > 100 * 1024 * 1024) return alert('Max 100MB');
```

### CSRF Protection

**Non implémenté** : Tokens CSRF recommandés pour mutations (POST, PUT, DELETE)

### Sanitization

**Opportunité** : Utiliser `DOMPurify` pour nettoyer HTML user-generated (si affichage Markdown)

---

## 14. Tests (À implémenter)

### Tests Unitaires (Vitest/Jest)

**Cibles** :
- `useConversation` : Logique métier
- `api.js` : Interceptors, modules
- Utilitaires (formattage dates, etc.)

### Tests Intégration (React Testing Library)

**Cibles** :
- Login flow : Formulaire → Success → Redirect
- ProtectedRoute : Auth/non-auth scenarios
- AdminTable : Pagination, filtres, suppression

### Tests E2E (Playwright/Cypress)

**Scénarios critiques** :
- Workflow RAG complet : Upload → Process → Index → Q&A
- Conversation : Créer → Poser questions → Historique → Supprimer
- Admin CRUD : Créer projet → Ajouter asset → Supprimer

---

## 15. Statistiques Finales

### Code Frontend

- **Total lignes** : ~2828 lignes (JS + JSX)
- **Pages** : 17 fichiers
- **Composants** : 6 fichiers
- **Services** : 1 fichier (api.js)
- **Context** : 1 fichier (AuthContext)
- **Hooks** : 1 fichier (useConversation)

### Routes par Authentification

- **Public** : 10% (2/19 routes)
- **User** : 21% (4/19 routes)
- **Admin** : 68% (13/19 routes)

### Composants Réutilisables

- **AdminTable** : Utilisé dans 7 pages admin
- **ConfirmModal** : Utilisé dans AdminTable (toutes pages CRUD)
- **Navbar** : Utilisé dans toutes pages (sauf Login/Register)
- **ProtectedRoute** : Wrapper pour 17/19 routes

### API Calls

- **authAPI** : 7 endpoints (authentification + gestion utilisateurs)
- **dataAPI** : 4 endpoints
- **nlpAPI** : 4 endpoints
- **conversationAPI** : 4 endpoints
- **adminAPI** : ~25 endpoints (CRUD multi-entités)
- **publicAPI** : 3 endpoints (exchange rates)

**Total** : ~47 fonctions API

---

## 16. Points d'Amélioration (→ Phase 6)

### Performance

- **Code splitting** : Lazy load pages avec `React.lazy()`
- **Memoization** : `React.memo`, `useMemo`, `useCallback`
- **Debouncing** : Search inputs, filtres admin
- **Virtual scrolling** : Tables avec milliers de lignes (react-window)
- **Image optimization** : WebP, lazy loading, CDN

### UX/UI

- **Dark mode** : Toggle light/dark avec Context
- **Toasts** : Notifications success/error (react-hot-toast)
- **Skeleton loaders** : Au lieu de "Chargement..."
- **Error boundaries** : Capturer erreurs React
- **Keyboard shortcuts** : Ctrl+K search, Escape fermer modals

### Sécurité

- **httpOnly cookies** : Au lieu de localStorage pour JWT
- **CSRF tokens** : Protection mutations
- **Input sanitization** : DOMPurify pour HTML user-generated
- **Rate limiting** : Côté client (éviter spam requêtes)

### Tests

- **Coverage 80%+** : Tests unitaires + intégration
- **E2E critiques** : Workflow RAG complet
- **Visual regression** : Chromatic/Percy

### Nouvelles Fonctionnalités

- **Streaming SSE** : Réponses RAG token par token
- **Export conversations** : JSON, PDF, TXT
- **Favoris** : Sauvegarder questions/réponses
- **Annotations** : Feedback sur qualité réponses
- **Multi-projets** : Switcher projet sans changer ID manuellement
- **Markdown** : Affichage réponses formatées (code blocks, listes)
- **Voice input** : Speech-to-text pour questions

---

## ✅ Phase 3 Complétée !

**Total analysé** :
- 19 routes (2 publiques, 4 user, 13 admin)
- 17 pages React
- 6 composants réutilisables
- 1 service API (44 fonctions)
- 1 Context (AuthContext)
- 1 Hook (useConversation)
- ~2828 lignes de code

**Prochaine étape** : **Phase 4 - Code Mort & Nettoyage**

---

**Dernière mise à jour** : Décembre 2025
**Durée** : 4 heures
**Statut** : ✅ Complétée
