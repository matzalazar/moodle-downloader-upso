#!/bin/bash

# Archivos de configuración
CREDS_FILE="config/creds.txt"
TODOIST_FILE="config/todoist_token.txt"

# Crear estructura de carpetas si no existen
mkdir -p config
mkdir -p data/trees
mkdir -p data/course
mkdir -p logs

# --- Credenciales de Moodle ---
if [ ! -f "$CREDS_FILE" ]; then
    echo "⚙️  Primera ejecución: introducí tus credenciales de Moodle."
    
    read -p "👤 Usuario: " username
    read -s -p "🔑 Contraseña: " password
    echo ""

    echo "$username" > "$CREDS_FILE"
    echo "$password" >> "$CREDS_FILE"

    echo "✅ Credenciales guardadas en $CREDS_FILE"
else
    echo "🔐 Credenciales ya configuradas. Usando las almacenadas en $CREDS_FILE"
fi

# --- Configuración opcional de Todoist ---
if [ ! -f "$TODOIST_FILE" ]; then
    read -p "📝 ¿Deseás configurar integración con Todoist? (y/n): " respuesta
    if [[ "$respuesta" == "y" || "$respuesta" == "Y" ]]; then
        read -s -p "🔑 Pegá tu token de API de Todoist: " todoist_token
        echo ""
        echo "$todoist_token" > "$TODOIST_FILE"
        echo "✅ Token de Todoist guardado en $TODOIST_FILE"
    else
        echo "ℹ️  Integración con Todoist no configurada."
    fi
else
    echo "🔗 Token de Todoist ya configurado."
fi

# Eliminar log previo antes de comenzar
rm -f logs/descargas_actual.log

# --- Ejecución del scraping y descarga ---
echo "🚀 Ejecutando scraping de Moodle..."
python3 scripts/session.py
python3 scripts/fetch_links.py
python3 scripts/extract_course_tree.py
python3 scripts/download_files.py

# Guardar y renombrar log
if [ -f "logs/descargas_actual.log" ]; then
    timestamp=$(date +"%Y%m%d_%H%M%S")
    final_log="logs/descargas_${timestamp}.log"
    mv logs/descargas_actual.log "$final_log"
    echo "🗂 Log generado: $final_log"

    read -p "📝 ¿Deseás enviar tareas nuevas a Todoist? (y/n): " send_todoist
    if [[ "$send_todoist" == "y" || "$send_todoist" == "Y" ]]; then
        python3 scripts/load_todoist.py
    else
        echo "ℹ️ Tareas no enviadas."
    fi
else
    echo "ℹ️ No se encontraron descargas nuevas en esta ejecución."
fi

echo "✅ Finalizado."
