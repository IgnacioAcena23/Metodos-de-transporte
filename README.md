# Integrantes:

- Ignacio Aceña
- Roberto Siracusa

# Métodos de Transporte

Aplicaciones de escritorio con interfaz gráfica (GUI) para resolver problemas clásicos de **programación lineal de transporte**. Cada método genera una solución básica factible inicial y permite analizarla con inteligencia artificial usando la API de **Groq**.

---

## Archivos del proyecto

| Archivo               | Descripción                                                                                                       |
| --------------------- | ----------------------------------------------------------------------------------------------------------------- |
| `esquina_noroeste.py` | Método de la Esquina Noroeste — asigna desde la celda superior izquierda avanzando secuencialmente                |
| `costo_minimo.py`     | Método de Costo Mínimo — siempre asigna a la celda de menor costo disponible en toda la tabla                     |
| `vogel.py`            | Método de Aproximación de Vogel (VAM) — usa penalidades por fila y columna para obtener la mejor solución inicial |
| `groq_client.py`      | Módulo compartido para conectarse a la API de Groq y analizar resultados con IA                                   |
| `.env`                | Archivo de configuración con tu clave de API de Groq (no se sube a GitHub)                                        |
| `.gitignore`          | Excluye el archivo `.env` del control de versiones                                                                |

---

## ¿Qué es Groq y para qué se usa?

[Groq](https://groq.com) es una plataforma de inteligencia artificial que ofrece acceso a modelos de lenguaje de gran escala (LLMs) a través de una API. En este proyecto se usa para generar un **análisis personalizado e inteligente** de cada solución de transporte que el usuario resuelva.

El modelo utilizado es **`llama-3.1-8b-instant`**, que es rápido, gratuito dentro del plan básico, y responde en español perfectamente.

---

## ¿Cómo funciona `groq_client.py`?

`groq_client.py` es un módulo auxiliar compartido por los tres programas. Se encarga de toda la comunicación con la API de Groq sin necesidad de instalar ninguna librería externa (usa solo `urllib`, `json` y `os` de la librería estándar de Python).

**Flujo interno paso a paso:**

1. Al iniciarse, lee automáticamente tu `GROQ_API_KEY` desde el archivo `.env` que tenés en la carpeta del proyecto.
2. Cuando hacés clic en **" Analizar con Groq"**, el programa construye un _prompt_ en español con todos los datos del problema que acabás de resolver: nombres de orígenes y destinos, oferta, demanda, asignaciones realizadas y costo total.
3. Ese prompt se envía al servidor de Groq mediante una solicitud HTTP `POST`.
4. El modelo de IA procesa el prompt y devuelve un análisis en texto plano.
5. La respuesta se muestra directamente en el panel derecho de la aplicación.

**¿Qué dice el análisis que genera la IA?**

- Explica paso a paso qué hizo el método de transporte elegido.
- Evalúa si la solución obtenida es razonable o si parece costosa.
- Recomienda si conviene optimizar con el método MODI o Stepping-Stone.

> **Sin el archivo `.env` con una clave válida, el botón de IA mostrará un error.** Las demás funciones (resolver, limpiar, generar tabla) funcionan perfectamente sin conexión a internet.

---

## Requisitos previos

- **Python 3.8 o superior** — la interfaz gráfica usa `tkinter`, que viene incluido por defecto.
- **Sin dependencias externas** — no es necesario instalar librerías adicionales con `pip`.
- **Conexión a internet** — solo para usar el botón "Analizar con Groq".

---

## Instalación y ejecución

### Windows

**1. Verificar que Python está instalado**

Abre una terminal (`cmd` o PowerShell) y ejecuta:

```powershell
python --version
```

Si no está instalado, descárgalo desde [python.org](https://www.python.org/downloads/) y asegúrate de marcar la opción **"Add Python to PATH"** durante la instalación.

**2. Clonar o descargar el repositorio**

```powershell
git clone https://github.com/IgnacioAcena23/Metodos-de-transporte.git
cd Metodos-de-transporte
```

O si descargaste el ZIP, extráelo y navega a la carpeta con:

```powershell
cd C:\ruta\a\la\carpeta\Metodos-de-transporte
```

**3. Crear el archivo `.env` con tu clave de Groq**

```powershell
echo GROQ_API_KEY=tu_clave_aqui > .env
```

Reemplaza `tu_clave_aqui` con tu clave real de [console.groq.com](https://console.groq.com/keys).

**4. Ejecutar el método deseado**

```powershell
# Método de la Esquina Noroeste
python esquina_noroeste.py

# Método de Costo Mínimo
python costo_minimo.py

# Método de Aproximación de Vogel
python vogel.py
```

---

### Linux

**1. Verificar que Python y tkinter están instalados**

```bash
python3 --version
```

En muchas distribuciones, `tkinter` viene por separado. Instálalo según tu sistema:

```bash
# Ubuntu / Debian / Linux Mint
sudo apt update && sudo apt install python3-tk

# Fedora / RHEL
sudo dnf install python3-tkinter

# Arch Linux
sudo pacman -S tk
```

**2. Clonar o descargar el repositorio**

```bash
git clone https://github.com/IgnacioAcena23/Metodos-de-transporte.git
cd Metodos-de-transporte
```

**3. Crear el archivo `.env` con tu clave de Groq**

```bash
echo "GROQ_API_KEY=tu_clave_aqui" > .env
```

Reemplaza `tu_clave_aqui` con tu clave real de [console.groq.com](https://console.groq.com/keys).

**4. Ejecutar el método deseado**

```bash
# Método de la Esquina Noroeste
python3 esquina_noroeste.py

# Método de Costo Mínimo
python3 costo_minimo.py

# Método de Aproximación de Vogel
python3 vogel.py
```

---

## Cómo usar cada aplicación

1. **Generar tabla** — elige el número de orígenes (2–8) y destinos (2–8) y haz clic en " Generar tabla".
2. **Ingresar datos** — escribe los nombres de orígenes y destinos, los costos unitarios de transporte, los valores de oferta y demanda.
3. **Resolver** — haz clic en " Resolver" para ejecutar el método. Las celdas con asignación se resaltarán en color.
4. **Analizar con IA** — haz clic en " Analizar con Groq" para obtener un análisis en español del resultado.
5. **Limpiar** — el botón " Limpiar" restablece todos los valores a cero sin borrar la tabla.

> El problema puede ser **balanceado** (oferta = demanda) o **desbalanceado**. En ese caso, el programa agrega automáticamente un origen o destino ficticio.

---

## Métodos implementados

### Esquina Noroeste

Asigna la mayor cantidad posible a la celda superior izquierda de la tabla y avanza hacia la derecha o hacia abajo. Es el método más sencillo pero generalmente produce la solución inicial de mayor costo.

### Costo Mínimo

En cada iteración selecciona la celda con el menor costo unitario disponible en toda la tabla y le asigna la mayor cantidad posible. Tiende a producir mejores soluciones iniciales que la Esquina Noroeste.

### Vogel (VAM)

Calcula una **penalidad** para cada fila y columna (diferencia entre el menor y el segundo menor costo). Asigna primero en la fila o columna con mayor penalidad, eligiendo la celda de menor costo. Suele dar la solución inicial más cercana al óptimo.

---

## API Key de Groq — Por qué necesitás la tuya propia

> **La API Key que figura en el archivo `.env` de este repositorio es personal del autor del proyecto.**
> Cada llamada a Groq consume cuota de la cuenta asociada a esa clave, y compartirla públicamente podría agotar los límites gratuitos o generar costos inesperados.
> **Por eso, si vas a usar la funcionalidad de IA, debés generar tu propia API Key gratuita.**

### ¿Qué es una API Key?

Es un código único que identifica tu cuenta ante el servidor de Groq. Cada vez que hacés clic en "Analizar con Groq", el programa usa esa clave para autenticarse y consumir el servicio. **Sin ella, la IA no puede responder.**

### Cómo obtener tu API Key gratuita (paso a paso)

1. Abrí tu navegador y andá a **[console.groq.com/keys](https://console.groq.com/keys)**.
2. Hacé clic en **"Sign Up"** para crear una cuenta gratuita (podés usar tu cuenta de Google o GitHub).
3. Una vez dentro, hacé clic en **"Create API Key"**.
4. Poné un nombre descriptivo (ej: `metodos-transporte`) y confirmá.
5. **Copiá la clave generada** — solo se muestra una vez.
6. Abrí (o creá) el archivo `.env` en la carpeta del proyecto y pegá tu clave así:

```
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxx
```

> **El plan gratuito de Groq** incluye miles de tokens por día con el modelo `llama-3.1-8b-instant`, más que suficiente para analizar decenas de problemas de transporte sin costo.

### ¿Qué pasa si no configurás tu propia API Key?

- Si el archivo `.env` **no existe**: la app muestra el error `No se encontró GROQ_API_KEY` al presionar el botón de IA.
- Si usás una clave ajena que ya superó su cuota: la app muestra `HTTP 429 – Too Many Requests`.
- En ambos casos, **el resto de la aplicación sigue funcionando normalmente** (resolver, limpiar, etc.).

---

## Problemas frecuentes

| Problema                                         | Solución                                                   |
| ------------------------------------------------ | ---------------------------------------------------------- |
| `ModuleNotFoundError: No module named 'tkinter'` | Instala tkinter: `sudo apt install python3-tk` (Linux)     |
| `No se encontró GROQ_API_KEY`                    | Crea el archivo `.env` en la misma carpeta con tu clave    |
| La ventana no se abre en Linux                   | Asegúrate de tener un entorno gráfico activo (X11/Wayland) |
| `HTTP 401` al usar Groq                          | Tu clave de API es inválida o expiró, genera una nueva     |
