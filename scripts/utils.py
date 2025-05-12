import os
from datetime import datetime

LOG_DIR = "logs"
CURRENT_LOG = os.path.join(LOG_DIR, "descargas_actual.log")

def registrar_descarga_log(nombre_archivo, curso, semana, tema):
    os.makedirs(LOG_DIR, exist_ok=True)
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linea = f"[{fecha}] {curso} | {semana} > {tema} => {nombre_archivo}\n"
    with open(CURRENT_LOG, "a", encoding="utf-8") as f:
        f.write(linea)
