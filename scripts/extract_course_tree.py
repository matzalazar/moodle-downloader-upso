import os
import json
import time
import re
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from session import get_authenticated_browser

COURSE_LIST_PATH = os.path.join("config", "course_links.json")
TREE_DIR = os.path.join("data", "trees")

def sanitizar_nombre(nombre):
    return re.sub(r'[^a-zA-Z0-9_-]+', '_', nombre.strip())[:50]

def expandir_todo(browser):
    XPATH_EXPANDIR = '/html/body/div[2]/div[5]/div/div[3]/div/section/div/div/div/ul/li[1]/div[1]/div[4]/a/span[2]'
    XPATH_COLAPSAR = '/html/body/div[2]/div[5]/div/div[3]/div/section/div/div/div/ul/li[1]/div[1]/div[4]/a/span[1]'

    try:
        colapsar = browser.find_element(By.XPATH, XPATH_COLAPSAR)
        if colapsar.is_displayed():
            print("🔁 Estado actual: expandido. Colapsando para reiniciar...")
            colapsar.click()
            time.sleep(1)
            expandir = browser.find_element(By.XPATH, XPATH_EXPANDIR)
            expandir.click()
            time.sleep(2)
            print("🔓 Secciones expandidas.")
            return
    except NoSuchElementException:
        pass

    try:
        expandir = browser.find_element(By.XPATH, XPATH_EXPANDIR)
        if expandir.is_displayed():
            expandir.click()
            time.sleep(2)
            print("🔓 Secciones expandidas.")
    except NoSuchElementException:
        print("⚠️ No se encontró ningún botón para expandir o colapsar.")

def extraer_secciones(browser):
    secciones = []
    bloques = browser.find_elements(By.CSS_SELECTOR, "li.section.main.clearfix")

    for bloque in bloques:
        try:
            titulo = bloque.find_element(By.CSS_SELECTOR, "h3.sectionname").text.strip()
        except NoSuchElementException:
            titulo = "(Sin título)"

        temas = []
        actividades = bloque.find_elements(By.CSS_SELECTOR, "li.activity")
        for actividad in actividades:
            try:
                enlace = actividad.find_element(By.CSS_SELECTOR, "a.aalink")
                nombre_completo = enlace.text.strip()
                url = enlace.get_attribute("href")

                if "\n" in nombre_completo:
                    nombre, tipo = nombre_completo.split("\n", 1)
                else:
                    nombre, tipo = nombre_completo, ""

                temas.append({
                    "nombre": nombre.strip(),
                    "tipo": tipo.strip(),
                    "url": url
                })
            except NoSuchElementException:
                continue

        secciones.append({
            "titulo": titulo,
            "temas": temas
        })

    return secciones

def merge_secciones(nuevas, anteriores):
    merged = []

    for nueva in nuevas:
        titulo = nueva["titulo"]
        temas_nuevos = nueva["temas"]

        temas_anteriores = []
        for vieja in anteriores:
            if vieja["titulo"] == titulo:
                temas_anteriores = vieja["temas"]
                break

        # mantener revisado si ya existía
        temas_mergeados = []
        for nuevo_tema in temas_nuevos:
            ya_existente = next((t for t in temas_anteriores if t["url"] == nuevo_tema["url"]), None)
            if ya_existente and ya_existente.get("revisado") is True:
                nuevo_tema["revisado"] = True
            temas_mergeados.append(nuevo_tema)

        merged.append({
            "titulo": titulo,
            "temas": temas_mergeados
        })

    return merged

def procesar_curso(browser, curso):
    print(f"📘 Procesando curso: {curso['nombre']}")
    browser.get(curso["url"])
    time.sleep(3)

    expandir_todo(browser)
    nuevas_secciones = extraer_secciones(browser)

    filename = os.path.join(TREE_DIR, f"{sanitizar_nombre(curso['nombre'])}.json")

    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            anterior = json.load(f)
            anteriores_secciones = anterior.get("semanas", [])
    else:
        anteriores_secciones = []

    secciones_actualizadas = merge_secciones(nuevas_secciones, anteriores_secciones)

    estructura = {
        "curso": curso["nombre"],
        "semanas": secciones_actualizadas
    }

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(estructura, f, indent=2, ensure_ascii=False)

    print(f"✅ Estructura guardada en {filename}")

def main():
    os.makedirs(TREE_DIR, exist_ok=True)

    with open(COURSE_LIST_PATH, "r", encoding="utf-8") as f:
        cursos = json.load(f)

    cursos_seguimiento = [c for c in cursos if c.get("seguimiento", False)]

    if not cursos_seguimiento:
        print("⚠️ No hay cursos marcados para seguimiento.")
        return

    browser = get_authenticated_browser()
    for curso in cursos_seguimiento:
        procesar_curso(browser, curso)

    browser.quit()
    print("🏁 Finalizado.")

if __name__ == "__main__":
    main()
