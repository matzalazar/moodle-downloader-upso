import os
import json
import time
import re
import datetime
from pathlib import Path

from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from session import get_authenticated_browser

# === RUTAS ROBUSTAS (A) ===
BASE_DIR = Path(__file__).resolve().parent.parent  # .../scripts -> proyecto
COURSE_LIST_PATH = BASE_DIR / "config" / "course_links.json"
TREE_DIR = BASE_DIR / "data" / "trees"

# "Semana 11/08/2025 - 17/08/2025"
PATRON_RANGO_FECHA = re.compile(
    r"(?P<ini>\d{2}/\d{2}/\d{4})\s*-\s*(?P<fin>\d{2}/\d{2}/\d{4})"
)

def sanitizar_nombre(nombre):
    nombre = nombre.replace("/", "-")
    return re.sub(r"[^a-zA-Z0-9_-]+", "_", nombre.strip())[:50]

def normalizar_titulo_para_directorio(titulo):
    return titulo.replace("/", "-").strip()

def parsear_rango_semana(titulo):
    m = PATRON_RANGO_FECHA.search(titulo)
    if not m:
        return None, None
    def _d(s):
        return datetime.datetime.strptime(s, "%d/%m/%Y").date()
    return _d(m.group("ini")), _d(m.group("fin"))

# === OPCIONAL (B): ir a “Mis cursos” con selectores estables ===
def ir_a_mis_cursos(browser, timeout=10):
    candidatos = [
        (By.LINK_TEXT, "Mis cursos"),
        (By.PARTIAL_LINK_TEXT, "Mis curso"),
        (By.CSS_SELECTOR, 'a[href*="/my/courses"]'),
        (By.CSS_SELECTOR, 'a[href*="/course/index.php?"]'),
    ]
    for how, what in candidatos:
        try:
            el = WebDriverWait(browser, timeout).until(EC.element_to_be_clickable((how, what)))
            el.click()
            return True
        except TimeoutException:
            continue
    return False  # si no está, no rompemos el flujo del extractor

def expandir_todo(browser):
    # Si tu Moodle tiene botones “Expandir/Colapsar” distintos, ajusta estos selectores.
    XPATH_EXPANDIR = '/html/body//ul/li[1]//a/span[2]'
    XPATH_COLAPSAR = '/html/body//ul/li[1]//a/span[1]'

    try:
        colapsar = browser.find_element(By.XPATH, XPATH_COLAPSAR)
        if colapsar.is_displayed():
            colapsar.click()
            time.sleep(1)
            expandir = browser.find_element(By.XPATH, XPATH_EXPANDIR)
            expandir.click()
            time.sleep(2)
            return
    except NoSuchElementException:
        pass

    try:
        expandir = browser.find_element(By.XPATH, XPATH_EXPANDIR)
        if expandir.is_displayed():
            expandir.click()
            time.sleep(2)
    except NoSuchElementException:
        pass

def extraer_secciones(browser):
    secciones = []
    bloques = browser.find_elements(By.CSS_SELECTOR, "li.section.main.clearfix")

    for bloque in bloques:
        try:
            titulo_elem = bloque.find_element(By.CSS_SELECTOR, "h3.sectionname a")
            titulo = titulo_elem.text.strip()
        except NoSuchElementException:
            try:
                titulo = bloque.find_element(By.CSS_SELECTOR, "h3.sectionname").text.strip()
            except NoSuchElementException:
                titulo = "(Sin título)"

        f_ini, f_fin = parsear_rango_semana(titulo)
        titulo_directorio = normalizar_titulo_para_directorio(titulo)

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
            "titulo_directorio": titulo_directorio,
            "fecha_inicio": f_ini.isoformat() if f_ini else None,
            "fecha_fin":    f_fin.isoformat() if f_fin else None,
            "temas": temas
        })

    secciones.sort(
        key=lambda s: (datetime.date.max if s["fecha_inicio"] is None
                       else datetime.date.fromisoformat(s["fecha_inicio"]))
    )
    return secciones

def merge_secciones(nuevas, anteriores):
    merged = []
    for nueva in nuevas:
        titulo = nueva["titulo"]
        temas_nuevos = nueva["temas"]

        temas_anteriores = []
        for vieja in anteriores:
            if vieja.get("titulo") == titulo:
                temas_anteriores = vieja.get("temas", [])
                break

        temas_mergeados = []
        for nt in temas_nuevos:
            ya = next((t for t in temas_anteriores if t.get("url") == nt.get("url")), None)
            if ya and ya.get("revisado") is True:
                nt["revisado"] = True
            temas_mergeados.append(nt)

        merged.append({
            "titulo": titulo,
            "titulo_directorio": nueva.get("titulo_directorio"),
            "fecha_inicio": nueva.get("fecha_inicio"),
            "fecha_fin": nueva.get("fecha_fin"),
            "temas": temas_mergeados
        })
    return merged

def procesar_curso(browser, curso):
    print(f"Procesando curso: {curso['nombre']}")
    browser.get(curso["url"])
    time.sleep(3)

    # Si querés forzar ir a “Mis cursos” antes:
    # ir_a_mis_cursos(browser)

    expandir_todo(browser)
    nuevas_secciones = extraer_secciones(browser)

    filename = TREE_DIR / f"{sanitizar_nombre(curso['nombre'])}.json"
    if filename.exists():
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

    TREE_DIR.mkdir(parents=True, exist_ok=True)
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(estructura, f, indent=2, ensure_ascii=False)

    print(f"Estructura guardada en {filename}")

def main():
    if not COURSE_LIST_PATH.exists():
        print(f"No existe {COURSE_LIST_PATH}. Crealo con una lista de cursos:")
        print('[{"nombre": "Nombre Curso", "url": "https://...", "seguimiento": true}]')
        return

    with open(COURSE_LIST_PATH, "r", encoding="utf-8") as f:
        cursos = json.load(f)

    cursos_seguimiento = [c for c in cursos if c.get("seguimiento", False)]
    if not cursos_seguimiento:
        print("No hay cursos marcados para seguimiento.")
        return

    browser = get_authenticated_browser()
    try:
        for curso in cursos_seguimiento:
            procesar_curso(browser, curso)
    finally:
        browser.quit()
    print("Finalizado.")

if __name__ == "__main__":
    main()
