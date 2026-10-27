# Prueba técnica · Ingeniería de producto

**Tiempo orientativo:** 3-4 horas. No hace falta terminarlo todo: preferimos poco y bien razonado.
**Entrega:** un repositorio Git (enlace o ZIP) en el plazo acordado.
**Herramientas de IA:** permitidas y bienvenidas (Claude, Cursor, Copilot…). Te pediremos que cuentes cómo las has usado.

## El contexto

Valdelumbre es un pueblo inventado que quiere un pequeño asistente turístico.
Te damos su catálogo de puntos de interés (`datos/pois.json`) y unas preguntas de prueba (`datos/evaluacion.json`).
Los datos se parecen a los de verdad, **también en sus defectos**.

## Qué construir

### 1. API (Python, preferiblemente FastAPI)
- `GET /pois` con filtros: `categoria`, `accesible`, `abierto_en` (día de la semana y hora) e `idioma` (`es`/`en`).
- `GET /pois/{id}`.
- `POST /preguntar` con `{ "pregunta": "...", "idioma": "es" }`. Devuelve una respuesta en texto **y los ids de los puntos en los que se apoya**.

### 2. El asistente
- Recupera los puntos relevantes para la pregunta y responde **solo con lo que hay en el catálogo**.
- Puedes usar un LLM con tu propia clave, uno local o ninguno: un generador de respuesta sencillo sin LLM es válido. **No te vamos a puntuar el modelo, sino lo que lo rodea.**
- Si usas un LLM, déjalo detrás de una interfaz para que se pueda cambiar de proveedor o ejecutar los tests sin red.

### 3. Una pantalla (Angular preferiblemente; vale otro framework si lo justificas)
- Una caja para preguntar, la respuesta y las fichas de los puntos citados.
- Un listado de todos los puntos con los filtros de `GET /pois` (categoría, accesible, abierto ahora).
- Opcional, si te da tiempo: un mapa sencillo con los puntos (no hace falta ninguna librería de mapas).
- Que se pueda usar solo con teclado y con lector de pantalla.

### 4. Calidad
- Tests de lo que consideres crítico.
- Un script que pase `datos/evaluacion.json` contra tu `/preguntar` y saque cuántas acierta.

## Qué entregar
Un repositorio con **todo el código** (API, asistente, pantalla, tests y script de evaluación) y, en la raíz, estos tres documentos:
- `README.md`: cómo arrancarlo (un comando, idealmente Docker Compose), decisiones tomadas y qué harías con más tiempo.
- `DATOS.md`: los problemas que has encontrado en los datos y qué has hecho con cada uno.
- `IA.md`: cómo has usado la IA. Qué le pediste, qué aceptaste y **qué corregiste o descartaste, y por qué**.

Lo corregimos con lo que entregues, sin sesión posterior: que el README baste para arrancarlo y entenderlo.
