# 📚 Moodle Downloader (Headless Automation) - UPSO

Una herramienta automatizada para navegar, extraer y estructurar el contenido de plataformas Moodle usando Selenium en modo headless. Organiza el material por curso y semana, y permite automatizar el seguimiento del contenido académico.

Este repositorio es de aplicación específica para la plataforma Moodle de la [UPSO](https://campusvirtual.upso.edu.ar/). 

## ¿Qué hace?

- Se conecta automáticamente al campus virtual con tus credenciales.
- Detecta todos los cursos en los que estás inscripto.
- Te permite elegir cuáles seguir.
- Recorre los contenidos de cada curso (semanas, temas, materiales).
- Genera una estructura jerárquica de cada curso en formato JSON.
- Descarga automáticamente los archivos con extensiones relevantes (.pdf, .docx, .ipynb, .py, etc.).
- Guarda logs y evita duplicados en ejecuciones futuras.
- Marca los temas ya revisados dentro del propio JSON.
- Permite integración con [Todoist](https://www.todoist.com).

> ⚠️ Muchas plataformas Moodle, como la de la UPSO, generan estructuras semanales por defecto que incluyen foros y secciones sin contenido. Esto puede dificultar el seguimiento efectivo de la materia si se hace de forma manual. Moodle Downloader automatiza y filtra inteligentemente esta estructura.

## Estructura del proyecto

```bash
config/
├── creds.txt              # Usuario y contraseña
└── course_links.json      # Cursos seleccionados y seguimiento
└── todoist_token.txt      # API Token de Todoist

data/
├── trees/                 # Estructura jerárquica por curso (semanas y temas)
└── course/                # Contenido descargado 

scripts/
├── session.py             # Login automático
├── fetch_links.py         # Selección de cursos y URLs
└── extract_course_tree.py # Generación de árboles jerárquicos por curso
└── download_files.py      # Descarga de contenido
└── load_todoist.py        # Opcional: Para carga en Bandeja de Entrada de Todoist

main.sh                    # Script bash para orquestar todo
requirements.txt
README.md
```

## Requisitos

- Python 3.10+
- Google Chrome instalado
- bash (para ejecutar main.sh)

## Instalación rápida

Cloná este repositorio:

```bash
git clone https://github.com/matzalazar/moodle-downloader-upso.git
cd moodle-downloader-upso
```

Instalá las dependencias necesarias:

```bash
pip install -r requirements.txt
```

Ejecutá el sistema por primera vez:

```bash
bash main.sh
```

Durante la primera ejecución:

- Se te pedirán tus credenciales de Moodle (guardadas localmente en config/creds.txt).
- Se te preguntará si querés integrar Todoist (opcional).
- Se listarán tus cursos y podrás seleccionar cuáles seguir.

## Selección de cursos a seguir

Durante la ejecución inicial, el script te preguntará si deseás hacer seguimiento de cada curso. Esto se guarda en `config/course_links.json` con un campo `"seguimiento": true`.

Si luego querés modificar esa selección, podés editar manualmente ese archivo.

En futuras ejecuciones, solo se recorrerán los cursos marcados con `"seguimiento": true`.

## 📌 Roadmap

Este proyecto está siendo adaptado para otras plataformas Moodle, incluyendo:

- 🏗️ [moodle-downloader-uns](https://github.com/matzalazar/moodle-downloader-uns) *(en desarrollo)*
- 🏗️ [moodle-downloader-utn](https://github.com/matzalazar/moodle-downloader-utn) *(en desarrollo)*

> 🧪 Estos repositorios estarán disponibles próximamente. Seguime para actualizaciones.

### 🚀 Próximas integraciones

- Exportación de actividades a Notion
- Sincronización con Google Calendar
- Envío de alertas vía Telegram

## 📝 Licencia

Este proyecto está licenciado bajo los términos de la [Licencia MIT](LICENSE).  
Podés utilizarlo, modificarlo y redistribuirlo libremente, siempre que mantengas los créditos correspondientes.
