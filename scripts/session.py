# scripts/session.py

import os
import sys
import time
import shutil
import platform
import subprocess

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

CREDS_PATH = os.path.join("config", "creds.txt")
LOGIN_URL = "https://campusvirtual.upso.edu.ar/login/index.php"

# Leer usuario y contraseña desde config/creds.txt
def get_credentials():
    try:
        with open(CREDS_PATH, "r") as f:
            lines = f.read().strip().splitlines()
            if len(lines) != 2:
                raise ValueError("Archivo de credenciales inválido.")
            return lines[0], lines[1]
    except Exception as e:
        print(f"❌ Error al leer credenciales: {e}")
        sys.exit(1)

# Detectar versión local de Chrome instalada
def obtener_version_chrome():
    try:
        sistema = platform.system()
        if sistema == "Windows":
            version = subprocess.check_output(
                r'reg query "HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon" /v version',
                shell=True
            )
            return version.decode().strip().split()[-1]
        elif sistema in ["Linux", "Darwin"]:
            for cmd in ["google-chrome", "google-chrome-stable", "chromium-browser", "chrome"]:
                try:
                    version = subprocess.check_output([cmd, "--version"]).decode().strip()
                    return version.split()[-1]
                except Exception:
                    continue
        else:
            print(f"⚠️ Sistema operativo no soportado: {sistema}")
            return None
    except Exception as e:
        print(f"⚠️ No se pudo obtener la versión de Chrome: {e}")
        return None

# Inicializar navegador con ChromeDriver
def init_browser():
    chrome_version = obtener_version_chrome()

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-gpu")

    try:
        if chrome_version and int(chrome_version.split('.')[0]) >= 115:
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        else:
            driver = webdriver.Chrome(
                service=Service(ChromeDriverManager(version=chrome_version).install()), options=options
            )
        return driver
    except Exception as e:
        print(f"❌ Error al iniciar navegador: {e}")
        return None

# Ejecutar login en Moodle
def login_moodle(browser, username, password):
    print("🌐 Abriendo página de login...")
    browser.get(LOGIN_URL)
    time.sleep(2)

    try:
        user_input = browser.find_element(By.ID, "username")
        pass_input = browser.find_element(By.ID, "password")
        login_button = browser.find_element(By.ID, "loginbtn")

        user_input.send_keys(username)
        pass_input.send_keys(password)
        login_button.click()
        time.sleep(3)

        if "login" in browser.current_url:
            print("❌ Inicio de sesión fallido.")
            browser.quit()
            sys.exit(1)

        print("✅ Sesión iniciada correctamente.")
        return browser

    except Exception as e:
        print(f"❌ Error durante login: {e}")
        browser.quit()
        sys.exit(1)

# Punto de entrada para cualquier módulo que quiera un navegador autenticado
def get_authenticated_browser():
    username, password = get_credentials()
    browser = init_browser()
    if not browser:
        print("❌ Error iniciando navegador.")
        sys.exit(1)
    return login_moodle(browser, username, password)
