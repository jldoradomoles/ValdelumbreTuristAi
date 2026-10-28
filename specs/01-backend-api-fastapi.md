# SPEC 01 — Backend API con FastAPI

**Estado:** implementado
**Fecha:** 2026-10-27
**Depende de:** —
**Objetivo:** Crear un backend Python con FastAPI que exponga los endpoints `GET /pois`, `GET /pois/{id}` y `POST /preguntar`, leyendo los datos del JSON de puntos de interés y usando un LLM (Claude) para generar respuestas.

---

## Alcance

### Incluido

- Carpeta `backend/` con la aplicación FastAPI completa
- Carga y limpieza de datos de `references/datos/pois.json` en memoria al arrancar
- Tres endpoints: `GET /pois` (con filtros), `GET /pois/{id}`, `POST /preguntar`
- Interfaz abstracta para LLM con dos implementaciones: Claude y fallback (keyword matching)
- Script de evaluación contra `references/datos/evaluacion.json`
- Dockerfile y docker-compose.yml
- Tests unitarios e integración
- CORS habilitado para desarrollo local con Angular

### NO incluido

- Frontend Angular (spec separada)
- Base de datos (se lee del JSON)
- Documentos `DATOS.md`, `IA.md`, `README.md` (se harán como tarea aparte)
- Autenticación / autorización
- Despliegue a producción

---

## Modelo de datos

### Dominio (Pydantic)

```python
class LocalizedText(BaseModel):
    es: str
    en: str

class Franja(BaseModel):
    dias: list[int]          # 1=Lunes ... 7=Domingo
    abre: str                # "HH:MM"
    cierra: str              # "HH:MM"
    temporada: str | None = None

class Horario(BaseModel):
    always_open: bool
    franjas: list[Franja]

class Precio(BaseModel):
    tipo: Literal["gratis", "fijo", "rango", "desconocido"]
    valor: float | None = None
    min: float | None = None
    max: float | None = None

class POI(BaseModel):
    id: str
    nombre: LocalizedText
    categoria: str
    descripcion: LocalizedText
    lat: float
    lon: float
    accesible: bool | None
    horario: Horario
    horario_desconocido: bool = False
    precio: Precio
    etiquetas: list[str]
```

### Normalización de `precio` (al cargar)

| Valor original | Resultado |
|---|---|
| `0` o `"gratis"` | `Precio(tipo="gratis")` |
| `4.5`, `15` | `Precio(tipo="fijo", valor=X)` |
| `"25-35"` | `Precio(tipo="rango", min=25, max=35)` |
| `null` | `Precio(tipo="desconocido")` |

### Schemas de API

- `POIResponse`: proyección monolingüe de un POI (nombre y descripción como `str`)
- `POIListResponse`: `{ total: int, pois: list[POIResponse] }`
- `PreguntarRequest`: `{ pregunta: str (1-500 chars), idioma: "es"|"en" }`
- `PreguntarResponse`: `{ respuesta: str, pois: list[str] }`

---

## Limpieza de datos (al cargar el JSON)

Se aplican estas correcciones en memoria, sin modificar el archivo original:

1. **poi-004**: descartar (duplicado de poi-003 con datos incompletos) → quedan 17 POIs
2. **poi-011**: intercambiar lat y lon (lat debe ser ~40.x, lon ~-3.x para España)
3. **poi-013**: truncar la descripción en español al contenido legítimo, eliminando el texto de prompt injection
4. **precio**: normalizar a estructura `Precio` según la tabla anterior
5. **poi-018**: marcar `horario_desconocido=True` (always_open=false con franjas vacías)

---

## Endpoints

### `GET /pois`

Query params (todos opcionales, combinan con AND):
- `categoria`: string exacto (`monumento`, `naturaleza`, `museo`, etc.)
- `accesible`: bool — `true` devuelve solo accesibles, `false` solo no accesibles. POIs con `null` se excluyen en ambos casos
- `abierto_en`: formato `X-HH:MM` donde X es la inicial del día en español (`L`=Lunes, `M`=Martes, `X`=Miércoles, `J`=Jueves, `V`=Viernes, `S`=Sábado, `D`=Domingo)
- `idioma`: `es` (default) o `en` — proyecta nombre y descripción al idioma seleccionado

Lógica de `abierto_en`:
- `always_open=true` → abierto
- `always_open=false` + franjas vacías (`horario_desconocido`) → excluido
- Se comprueba si el día está en `franja.dias` y `abre <= hora < cierra`

### `GET /pois/{id}`

Query params: `idioma` (es/en, default es).
Devuelve 404 si el ID no existe (incluido poi-004 descartado).

### `POST /preguntar`

Body: `PreguntarRequest`.
Flujo:
1. Recuperar POIs candidatos por búsqueda de texto (nombre, descripción, etiquetas, categoría)
2. Construir prompt con los datos de los candidatos como contexto
3. Llamar al LLM (Claude o fallback según configuración)
4. Devolver `PreguntarResponse` con la respuesta y los IDs de los POIs referenciados

---

## Abstracción del LLM

Interfaz abstracta `LLMAssistant` con método `answer(question, idioma, candidate_pois) -> AssistantAnswer`.

**Implementación Claude** (`LLM_PROVIDER=claude`):
- SDK `anthropic` (async)
- System prompt defensivo: responde solo con datos del catálogo, ignora instrucciones dentro de los datos, responde en el idioma solicitado, devuelve JSON con `respuesta` y `pois`
- Requiere `ANTHROPIC_API_KEY`

**Implementación Fallback** (`LLM_PROVIDER=fallback`, default):
- Keyword matching puro, sin red
- Tokeniza la pregunta, puntúa POIs por coincidencias
- Patrones especiales: "accesible"/"silla de ruedas" → filtrar accesibles, "abierto" + día/hora → filtrar por horario
- Funciona sin API key

Factoría: lee `LLM_PROVIDER` de la config y devuelve la implementación correspondiente.

---

## Estructura de archivos

```
backend/
  pyproject.toml
  Dockerfile
  .env.example
  app/
    __init__.py
    main.py              # App FastAPI, lifespan, CORS, routers
    config.py            # Settings (pydantic-settings)
    models/
      poi.py             # Modelos de dominio
      api.py             # Schemas request/response
    data/
      loader.py          # Carga y limpieza del JSON
      store.py           # POIStore in-memory
    routers/
      pois.py            # GET /pois, GET /pois/{id}
      preguntar.py       # POST /preguntar
    llm/
      base.py            # Interfaz abstracta
      claude.py          # Implementación Claude
      fallback.py        # Implementación sin LLM
      factory.py         # Factoría
    services/
      filter_service.py  # Lógica de filtrado
      assistant_service.py
  tests/
    conftest.py
    test_loader.py
    test_filter_service.py
    test_pois_router.py
    test_preguntar_router.py
    test_llm_fallback.py
  scripts/
    evaluate.py

docker-compose.yml       # En la raíz del proyecto
```

---

## Plan de implementación

1. **Scaffolding y capa de datos** — `pyproject.toml`, config, modelos de dominio, loader con limpieza, store. Tests del loader.
2. **Servicio de filtros y endpoints de POIs** — filter_service, routers/pois, main.py con CORS. Tests de filtros y routers.
3. **Abstracción LLM y fallback** — base, fallback, factory. Tests del fallback.
4. **Endpoint /preguntar** — assistant_service, routers/preguntar. Tests de integración.
5. **Implementación Claude** — claude.py con system prompt defensivo.
6. **Script de evaluación** — evaluate.py que ejecuta evaluacion.json contra /preguntar.
7. **Docker** — Dockerfile, docker-compose.yml, .env.example.

---

## Criterios de aceptación

- [v] `GET /pois` devuelve 17 POIs (poi-004 descartado)
- [v] `GET /pois?categoria=museo` devuelve solo museos
- [v] `GET /pois?accesible=true` excluye poi-013 y POIs con accesible=null
- [v] `GET /pois?abierto_en=L-12:00` devuelve poi-001, poi-002, poi-005, poi-006, poi-010 (y excluye poi-003, poi-008, poi-015)
- [v] `GET /pois?idioma=en` devuelve textos en inglés
- [v] `GET /pois/poi-001` devuelve el castillo
- [v] `GET /pois/poi-004` devuelve 404
- [v] `POST /preguntar` con pregunta sobre vino devuelve poi-008 en los IDs
- [v] `POST /preguntar` con pregunta vacía devuelve 422
- [v] poi-011 tiene lat ~40.x y lon ~-3.x (corregido)
- [v] poi-013 no contiene texto de prompt injection en la descripción
- [v] Todos los precios están normalizados a estructura `Precio`
- [ ] `LLM_PROVIDER=fallback` funciona sin API key
- [ ] `LLM_PROVIDER=claude` genera respuestas con system prompt defensivo
- [v] `python -m scripts.evaluate` reporta resultados por pregunta
- [v] `docker compose up` levanta el backend en puerto 8000
- [v] Todos los tests pasan con `pytest`

---

## Decisiones tomadas

| Decisión | Alternativa descartada | Justificación |
|---|---|---|
| Limpiar datos en memoria al cargar | Modificar el JSON original o crear copia limpia | El enunciado dice "los datos se parecen a los de verdad, también en sus defectos" — documentar los problemas es parte de la prueba |
| Fallback como LLM por defecto | Claude por defecto | La app funciona out-of-the-box sin API key; el evaluador puede arrancar con `docker compose up` sin configurar nada |
| `abierto_en` con iniciales en español (L/M/X/J/V/S/D) | Números 1-7 o ISO datetime | Contexto español, sin ambigüedad (X para miércoles evita colisión M/Martes), fácil de usar desde el frontend |
| `Precio` como tipo discriminado | Mantener el campo raw como `Any` | Type safety en todo el código downstream; parsear una vez, usar muchas |
| Truncar descripción de poi-013 | Regex para borrar solo la inyección | Más robusto — no depende de patrones específicos de inyección |

---

## Riesgos identificados

- **Calidad del fallback**: el keyword matching puede dar resultados pobres en las preguntas de evaluación. Mitigación: la implementación Claude es la primaria; el fallback es para tests sin red.
- **Temporada en horarios**: el filtro `abierto_en` no tiene componente de fecha, por lo que ignora el campo `temporada` de las franjas. Se documenta como limitación conocida.
