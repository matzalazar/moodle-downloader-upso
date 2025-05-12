import os
import sys
import requests

TODOIST_PATH = "config/todoist_token.txt"
LOG_DIR = "logs"

def crear_tarea_todoist(nombre_archivo, curso, semana, tema, token):
    url = "https://api.todoist.com/rest/v2/tasks"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    contenido = f"Nueva descarga en Moodle: {nombre_archivo}\nCurso: {curso}\nSemana: {semana}\nTema: {tema}"
    data = {
        "content": contenido,
        "due_string": "today",
        "priority": 3
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        print(f"📝 Tarea creada en Todoist: {nombre_archivo}")
    except Exception as e:
        print(f"❌ Error al crear tarea en Todoist: {e}")

def main():
    if not os.path.isfile(TODOIST_PATH):
        print("❌ No se encontró el token de Todoist.")
        sys.exit(1)

    token = open(TODOIST_PATH).read().strip()

    logs = [f for f in os.listdir(LOG_DIR) if f.startswith("descargas_") and f.endswith(".log")]
    if not logs:
        print("ℹ️ No hay log de descargas recientes.")
        return

    latest_log = sorted(logs)[-1]
    print(f"📤 Enviando tareas de {latest_log} a Todoist...")

    with open(os.path.join(LOG_DIR, latest_log), "r", encoding="utf-8") as f:
        for linea in f:
            try:
                nombre_archivo = linea.split("=> ")[1].strip()
                resto = linea.split("] ")[1].split("=> ")[0]
                curso, resto2 = resto.split(" | ")
                semana, tema = resto2.split(" > ")
                crear_tarea_todoist(
                    nombre_archivo.strip(),
                    curso.strip(),
                    semana.strip(),
                    tema.strip(),
                    token
                )
            except Exception as e:
                print(f"⚠️ No se pudo procesar la línea:\n{linea}\nError: {e}")

if __name__ == "__main__":
    main()
