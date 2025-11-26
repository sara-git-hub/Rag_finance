#!/bin/bash
# Script pour télécharger automatiquement les modèles Ollama
# Ce script doit être exécuté après le démarrage du container Ollama

echo "🚀 Initialisation d'Ollama..."
echo "⏳ Attente du démarrage du service Ollama..."

# Attendre que Ollama soit prêt
until curl -s http://ollama:11434/api/tags > /dev/null 2>&1; do
  echo "⏳ En attente d'Ollama..."
  sleep 2
done

echo "✅ Ollama est prêt !"
echo ""

# Liste des modèles à télécharger (vous pouvez en ajouter ou retirer)
MODELS=(
  "mistral"        # 7B - Recommandé pour débuter (4GB)
  # "llama3.1"     # 8B - Très bon pour FR/EN (4.7GB)
  # "gemma2:9b"    # 9B - Performant (5.4GB)
  # "qwen2.5"      # 7B - Multilangue (4.5GB)
  # "phi3"         # 3.8B - Rapide et léger (2.3GB)
)

echo "📦 Téléchargement des modèles Ollama..."
echo "Modèles à installer: ${MODELS[@]}"
echo ""

for model in "${MODELS[@]}"; do
  echo "⬇️  Téléchargement du modèle: $model"
  docker exec ollama ollama pull "$model"

  if [ $? -eq 0 ]; then
    echo "✅ $model téléchargé avec succès"
  else
    echo "❌ Erreur lors du téléchargement de $model"
  fi
  echo ""
done

echo "🎉 Initialisation terminée !"
echo ""
echo "📋 Modèles disponibles:"
docker exec ollama ollama list
