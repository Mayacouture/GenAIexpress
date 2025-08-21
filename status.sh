#!/bin/bash

echo "🔍 Vérification du statut de Lectio Divina IA"
echo "=============================================="

# Vérifier si l'application est en cours d'exécution
if pgrep -f "streamlit.*app.py" > /dev/null; then
    echo "✅ Application en cours d'exécution"
    echo ""
    echo "🌐 URLs d'accès :"
    echo "   Local:  http://localhost:8501"
    echo "   Réseau: http://172.30.0.2:8501"
    echo ""
    echo "📱 Ouvrez votre navigateur et allez à l'une de ces adresses"
    echo ""
    echo "🛑 Pour arrêter: pkill -f 'streamlit.*app.py'"
    echo "🔄 Pour redémarrer: ./start_app.sh"
else
    echo "❌ Application non démarrée"
    echo ""
    echo "🚀 Pour démarrer l'application :"
    echo "   ./start_app.sh"
    echo "   ou"
    echo "   ./.run"
fi

echo ""
echo "📊 Informations système :"
echo "   Port utilisé: 8501"
echo "   Processus: $(pgrep -f 'streamlit.*app.py' 2>/dev/null || echo 'Aucun')"
echo "   Fichier .env: $(if [ -f .env ]; then echo '✅ Présent'; else echo '❌ Manquant'; fi)"
echo "   Répertoires data: $(if [ -d data/bible ] && [ -d data/valtorta ]; then echo '✅ Présents'; else echo '❌ Manquants'; fi)"