import os
import json
import time
import re
import requests
from urllib.parse import urlparse
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from session import get_authenticated_browser
from utils import registrar_descarga_log  # ✅ NUEVO

TREES_DIR = "data/trees"
COURSE_DIR = "data/course"

EXTENSIONES_VALIDAS = {".pdf", ".docx", ".xlsx", ".zip", ".ipynb", ".py", ".txt", ".csv", ".pptx"}

def sanitizar(nombre):
    return re.sub(r'[^a-zA-Z0-9_-]+', '_', nombre.strip())[:50]

def tiene_extension_valida(url):
    path = urlparse(url).path
    return any(path.lower().endswith(ext) for ext in EXTENSIONES_VALIDAS)

def descargar_archivo(url, destino, cookies):
    try:
        r = requests.get(url, cookies=cookies, stream=True)
        r.raise_for_status()
        os.makedirs(os.path.dirname(destino), exist_ok=True)
        with open(destino, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"⬇️  Descargado: {os.path.basename(destino)}")
        return True
    except Exception as e:
        print(f"❌ Error descargando {url}: {e}")
        return False

def obtener_cookies_selenium(browser):
    return {c['name']: c['value'] for c in browser.get_cookies()}

def procesar_curso(browser, curso_json, curso_file_path):
    curso_nombre = curso_json["curso"]
    curso_sanitizado = sanitizar(curso_nombre)
    curso_url = [c["url"] for c in json.load(open("config/course_links.json", "r", encoding="utf-8")) if c["nombre"] == curso_nombre][0]

    browser.get(curso_url)
    time.sleep(2)
    cookies = obtener_cookies_selenium(browser)

    for s_idx, semana in enumerate(curso_json["semanas"]):
        semana_nombre = sanitizar(semana["titulo"])
        for t_idx, tema in enumerate(semana["temas"]):
            tema_nombre = sanitizar(tema.get("nombre", "Tema"))
            tema_url = tema.get("url")

            if not tema_url:
                print(f"⚠️  Tema sin URL: {tema_nombre}")
                continue

            if tema.get("revisado") is True:
                print(f"🔁 Tema ya revisado previamente: {tema_nombre}")
                continue

            try:
                print(f"🔎 Procesando tema: {tema_nombre}")
                main_tab = browser.current_window_handle
                browser.execute_script("window.open(arguments[0]);", tema_url)
                browser.switch_to.window(browser.window_handles[-1])
                time.sleep(2)

                WebDriverWait(browser, 5).until(
                    EC.presence_of_element_located((By.TAG_NAME, "a"))
                )

                todos_los_links = browser.find_elements(By.TAG_NAME, "a")
                links_descargables = []

                for l in todos_los_links:
                    href = l.get_attribute("href")
                    if href and tiene_extension_valida(href):
                        visible = l.text.strip() or os.path.basename(href)
                        links_descargables.append((href, visible))

                if not links_descargables:
                    print(f"⚠️  No se encontraron archivos válidos en el tema '{tema_nombre}'")
                else:
                    for archivo_url, nombre_visible in links_descargables:
                        archivo_nombre = sanitizar(nombre_visible)
                        destino = os.path.join(COURSE_DIR, curso_sanitizado, semana_nombre, tema_nombre, archivo_nombre)
                        if descargar_archivo(archivo_url, destino, cookies):
                            registrar_descarga_log(archivo_nombre, curso_nombre, semana["titulo"], tema.get("nombre", "Tema"))  # ✅ NUEVO

                curso_json["semanas"][s_idx]["temas"][t_idx]["revisado"] = True

                browser.close()
                browser.switch_to.window(main_tab)
                time.sleep(1)

            except Exception as e:
                print(f"❌ Error al procesar '{tema_nombre}': {e}")
                try:
                    browser.close()
                    browser.switch_to.window(main_tab)
                except:
                    pass

    with open(curso_file_path, "w", encoding="utf-8") as f:
        json.dump(curso_json, f, indent=2, ensure_ascii=False)

def main():
    os.makedirs(COURSE_DIR, exist_ok=True)
    browser = get_authenticated_browser()

    for filename in os.listdir(TREES_DIR):
        if not filename.endswith(".json"):
            continue
        path = os.path.join(TREES_DIR, filename)
        with open(path, "r", encoding="utf-8") as f:
            curso_json = json.load(f)
            print(f"📥 Procesando descargas para: {curso_json['curso']}")
            procesar_curso(browser, curso_json, path)

    browser.quit()
    print("🏁 Descarga finalizada.")

if __name__ == "__main__":
    main()
