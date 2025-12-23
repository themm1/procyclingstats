# 🚴 Cycling Race Viewer

Una aplicación web moderna para visualizar resultados de carreras de ciclismo desde ProCyclingStats.

## 🌟 Características

- **Interfaz moderna y atractiva** con diseño dark mode
- **Carga dinámica** de carreras desde Excel en Dropbox
- **Visualización de resultados** en tabla interactiva
- **Animaciones suaves** y efectos visuales premium
- **Responsive design** para dispositivos móviles

## 🚀 Cómo usar

### 1. Instalar dependencias

Asegúrate de tener instaladas las siguientes dependencias de Python:

```bash
pip install flask flask-cors pandas openpyxl procyclingstats pillow requests
```

### 2. Iniciar el servidor

Ejecuta el servidor Flask desde el directorio `web_carreras`:

```bash
python server.py
```

El servidor se iniciará en `http://localhost:5000`

### 3. Abrir la aplicación

Abre el archivo `index.html` en tu navegador web favorito. Puedes hacerlo de dos formas:

- **Opción 1**: Haz doble clic en `index.html`
- **Opción 2**: Abre tu navegador y arrastra el archivo `index.html` a la ventana

### 4. Usar la aplicación

1. **Selecciona una carrera** del menú desplegable
2. **Haz clic en "Load Results"** para cargar los resultados
3. **Visualiza los datos** en la tabla interactiva

## 📁 Estructura de archivos

```
web_carreras/
├── index.html      # Página principal
├── style.css       # Estilos y diseño
├── script.js       # Lógica del frontend
├── server.py       # API backend (Flask)
└── README.md       # Este archivo
```

## � API Endpoints

### GET `/api/races`
Obtiene la lista de carreras disponibles desde el archivo Excel.

**Respuesta:**
```json
{
  "success": true,
  "races": [
    {
      "carrera": "GP d'Ouverture",
      "url": "race/gp-d-ouverture/2026"
    }
  ]
}
```

### POST `/api/results`
Obtiene los resultados de una carrera específica.

**Request:**
```json
{
  "url": "race/gp-d-ouverture/2026"
}
```

**Respuesta:**
```json
{
  "success": true,
  "results": [
    {
      "rider_name": "John Doe",
      "team_name": "Team XYZ",
      "rank": "1",
      "uci_points": "100"
    }
  ]
}
```

### GET `/api/health`
Verifica el estado del servidor.

## 🎨 Diseño

La aplicación utiliza:
- **Fuente**: Inter (Google Fonts)
- **Colores**: Paleta moderna con tonos azul/púrpura
- **Efectos**: Glassmorphism, gradientes, animaciones CSS
- **Framework CSS**: Vanilla CSS (sin dependencias)

## ⚠️ Solución de problemas

### El servidor no inicia
- Verifica que todas las dependencias estén instaladas
- Asegúrate de que el puerto 5000 no esté en uso

### No se cargan las carreras
- Verifica tu conexión a internet (se necesita para acceder al Excel en Dropbox)
- Revisa la consola del navegador para errores

### Error al cargar resultados
- Algunos resultados pueden tardar en cargar desde ProCyclingStats
- Verifica que la URL de la carrera sea válida

## 📝 Notas

- La aplicación carga las primeras 5 carreras del archivo Excel
- Para carreras de un día, muestra los top 5 ciclistas
- Los resultados se guardan también en archivos Excel locales

## 📦 Recursos y logos

- Ubicación estándar del logo: coloca tu imagen en `web_carreras/assets/logo.png`.
- Alternativa: define la variable de entorno `PCS_LOGO_PATH` apuntando al fichero del logo.
- Si el logo no existe, la generación de Excel continuará sin insertar la imagen.
