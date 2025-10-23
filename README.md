## 🚀 Installation

### 1. Créer un environnement virtuel

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
.\venv\Scripts\python.exe -m pip install --only-binary=:all: -r requirements.txt
venv\Scripts\activate  # Windows
```

### 2. Installer les dépendances

```bash
# Option 1: Si vous avez une erreur avec pip, utilisez cette commande (recommandée):
.\venv\Scripts\python.exe -m pip install --only-binary=:all: -r requirements.txt

# Option 2: Si la première option ne fonctionne pas, essayez:
pip install -r requirements.txt
```