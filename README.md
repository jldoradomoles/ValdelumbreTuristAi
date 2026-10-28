# Valdelumbre Tourist AI

Asistente turístico para el pueblo ficticio de Valdelumbre. Incluye una API backend (Python/FastAPI) y un frontend (Angular).

## Arquitectura

```
valdelumbre-turist-ai/
├── backend/              # API FastAPI (Python 3.12+)
│   ├── app/
│   │   ├── main.py       # App FastAPI, lifespan, CORS
│   │   ├── config.py     # Settings (pydantic-settings)
│   │   ├── models/       # Modelos de dominio y schemas API
│   │   ├── data/         # Carga de datos y store in-memory
│   │   ├── routers/      # Endpoints: /pois, /preguntar
│   │   ├── services/     # Filtrado y asistente
│   │   └── llm/          # Abstracción LLM (Claude + fallback)
│   ├── tests/
│   ├── scripts/          # Script de evaluación
│   ├── Dockerfile
│   └── pyproject.toml
├── src/                  # Frontend Angular
├── references/           # Enunciado y datos originales
│   └── datos/
│       ├── pois.json         # 18 POIs (con defectos intencionados)
│       └── evaluacion.json   # 6 preguntas de evaluación
├── docker-compose.yml
└── specs/                # Especificaciones técnicas
```

## Arranque rápido

### Con Docker Compose (recomendado)

```bash
docker compose up
```

Esto levanta el backend en `http://localhost:8000`. No requiere API key — usa el asistente fallback por defecto.

Para usar Claude como LLM:

```bash
ANTHROPIC_API_KEY=sk-ant-... LLM_PROVIDER=claude docker compose up
```

### Sin Docker (desarrollo local)

#### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate     # Linux/macOS
# .venv\Scripts\activate      # Windows
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

El backend arranca en `http://localhost:8000`. La documentación interactiva de la API está en `http://localhost:8000/docs`.

#### Frontend

```bash
npm install
ng serve
```

El frontend arranca en `http://localhost:4200`.

## Configuración

Variables de entorno (se pueden poner en `backend/.env`):

| Variable | Valor por defecto | Descripción |
|---|---|---|
| `LLM_PROVIDER` | `fallback` | `fallback` (keyword matching, sin red) o `claude` (API de Anthropic) |
| `ANTHROPIC_API_KEY` | _(vacío)_ | Clave de API de Anthropic. Solo necesaria si `LLM_PROVIDER=claude` |
| `DATA_PATH` | `references/datos/pois.json` | Ruta al archivo JSON de puntos de interés |
| `ALLOWED_ORIGINS` | `["http://localhost:4200"]` | Orígenes CORS permitidos |

Ver `backend/.env.example` para un archivo de ejemplo.

## Endpoints de la API

### `GET /pois`

Lista puntos de interés con filtros opcionales (combinan con AND):

| Parámetro | Tipo | Descripción |
|---|---|---|
| `categoria` | string | Categoría exacta: `monumento`, `naturaleza`, `museo`, `gastronomia`, `espacio_publico`, `ruta`, `servicio` |
| `accesible` | bool | `true` = solo accesibles, `false` = solo no accesibles. POIs con `null` se excluyen |
| `abierto_en` | string | Formato `X-HH:MM`. X = inicial del día en español: `L`=Lunes, `M`=Martes, `X`=Miércoles, `J`=Jueves, `V`=Viernes, `S`=Sábado, `D`=Domingo |
| `idioma` | string | `es` (defecto) o `en`. Proyecta nombre y descripción al idioma |

Ejemplo: `GET /pois?categoria=museo&accesible=true&idioma=es`

### `GET /pois/{id}`

Devuelve un POI por ID. Parámetro opcional: `idioma`.

### `POST /preguntar`

Pregunta al asistente turístico.

```json
{
  "pregunta": "¿Dónde puedo probar vino de la zona?",
  "idioma": "es"
}
```

Respuesta:

```json
{
  "respuesta": "Según el catálogo, estos puntos de interés coinciden...",
  "pois": ["poi-008"]
}
```

## Tests

```bash
cd backend
pytest
```

Los tests cubren:
- **Carga de datos**: descarte de duplicados, corrección de coordenadas, limpieza de inyección, normalización de precios, detección de horario desconocido
- **Servicio de filtros**: filtrado por categoría, accesibilidad, horario; parsing de `abierto_en`
- **Routers de POIs**: listado, detalle, 404, idioma, filtros combinados, validación
- **Router /preguntar**: pregunta válida, vacía, idioma inválido, inglés, sin resultados
- **Fallback LLM**: preguntas sobre vino, accesibilidad, horario, inglés, preguntas sin respuesta

## Script de evaluación

Ejecuta las 6 preguntas de `evaluacion.json` contra `/preguntar` y reporta aciertos:

```bash
cd backend

# Contra un servidor corriendo
python -m scripts.evaluate

# Sin servidor (usa TestClient internamente)
python -m scripts.evaluate --internal

# Contra otro host
python -m scripts.evaluate --base-url http://host:puerto
```

## Decisiones tomadas

| Decisión | Justificación |
|---|---|
| Datos limpios en memoria, JSON original intacto | El enunciado dice que los datos "se parecen a los de verdad, también en sus defectos" — documentar y corregir en tiempo de carga |
| Fallback como LLM por defecto | La app funciona sin API key; `docker compose up` arranca sin configurar nada |
| `abierto_en` con iniciales en español (L/M/X/J/V/S/D) | Contexto español, sin ambigüedad (X = miércoles), fácil de usar |
| `Precio` como tipo discriminado | Type safety en todo el código; parsear una vez, usar muchas |
| System prompt defensivo para Claude | Protege contra prompt injection en los datos (ver poi-013) |
| Interfaz abstracta `LLMAssistant` | Permite cambiar de proveedor o ejecutar tests sin red |

## Qué haría con más tiempo

- Frontend Angular completo con caja de preguntas, fichas de POIs y filtros
- Mapa sencillo con los puntos de interés
- Soporte de temporada en el filtro `abierto_en` (actualmente se ignora el campo `temporada` de las franjas horarias)
- Cache de respuestas del LLM para preguntas frecuentes
- Rate limiting en el endpoint `/preguntar`
- Paginación en `GET /pois`
- Tests E2E con Playwright
