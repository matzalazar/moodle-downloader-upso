# scripts/fetch_links.py

import time
import json
import os
from selenium.webdriver.common.by import By
from session import get_authenticated_browser

MIS_CURSOS_XPATH = '/html/body/div[2]/nav/div[1]/nav/ul/li[3]/a'
OUTPUT_PATH = os.path.join("config", "course_links.json")

def ya_configurado(filepath):
    if not os.path.exists(filepath):
        return False
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
        return all("seguimiento" in curso for curso in data)

def ir_a_mis_cursos(browser):
    try:
        mis_cursos_btn = browser.find_element(By.XPATH, MIS_CURSOS_XPATH)
        mis_cursos_btn.click()
        time.sleep(2)
    except Exception as e:
        print(f"❌ No se pudo acceder a 'Mis cursos': {e}")
        browser.quit()
        exit(1)

def preguntar_seguimiento(nombre):
    while True:
        resp = input(f"¿Deseás hacer seguimiento de \"{nombre}\"? (y/n): ").strip().lower()
        if resp in ("y", "n"):
            return resp == "y"

def extraer_links_de_cursos(browser):
    cursos = []
    time.sleep(2)
    enlaces = browser.find_elements(By.CSS_SELECTOR, "a.aalink.coursename")

    for enlace in enlaces:
        nombre = enlace.text.strip().replace("Nombre del curso\n", "", 1)
        url = enlace.get_attribute("href")
        seguimiento = preguntar_seguimiento(nombre)
        cursos.append({
            "nombre": nombre,
            "url": url,
            "seguimiento": seguimiento
        })

    return cursos

def guardar_links(cursos):
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(cursos, f, indent=2, ensure_ascii=False)
    print(f"✅ Enlaces de cursos guardados en {OUTPUT_PATH}")

def main():
    if ya_configurado(OUTPUT_PATH):
        print(f"✅ Archivo {OUTPUT_PATH} ya existe y tiene seguimiento configurado. Usando ese.")
        return

    browser = get_authenticated_browser()
    ir_a_mis_cursos(browser)
    cursos = extraer_links_de_cursos(browser)
    guardar_links(cursos)
    browser.quit()

if __name__ == "__main__":
    main()
