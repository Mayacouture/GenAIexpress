#!/bin/bash

echo "🙏 LECTIO DIVINA IA - DÉMARRAGE"
echo "=================================="

# Vérifier si l'application est déjà en cours d'exécution
if pgrep -f "streamlit.*app.py" > /dev/null; then
    echo "✅ L'application est déjà en cours d'exécution"
    echo ""
    echo "🌐 Accès à l'application :"
    echo "   URL locale: http://localhost:8501"
    echo "   URL réseau: http://$(hostname -I | awk '{print $1}'):8501"
    echo ""
    echo "📱 Ouvrez votre navigateur et allez à l'une de ces adresses"
    echo ""
    echo "🛑 Pour arrêter l'application:"
    echo "   pkill -f 'streamlit.*app.py'"
    echo ""
    exit 0
fi

# Vérifier les dépendances
echo "🔍 Vérification des dépendances..."
if ! python3 -c "import streamlit" 2>/dev/null; then
    echo "❌ Streamlit non installé. Installation..."
    pip3 install --break-system-packages streamlit python-dotenv openai
fi

# Créer .env si nécessaire
if [ ! -f .env ]; then
    echo "📝 Création du fichier .env..."
    cp .env.example .env
    echo "⚠️  Configurez votre clé OpenAI dans .env"
fi

# Créer les répertoires de données
mkdir -p data/bible data/valtorta

echo ""
echo "🚀 Lancement de l'application..."
echo ""

# Configuration pour l'accès web
export STREAMLIT_SERVER_PORT=8501
export STREAMLIT_SERVER_ADDRESS=0.0.0.0
export STREAMLIT_SERVER_HEADLESS=true
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Lancer l'application
python3 -m streamlit run app.py \
    --server.port=8501 \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --browser.gatherUsageStats=false