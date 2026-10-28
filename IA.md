# IA.md — Uso de inteligencia artificial en el proyecto

## Herramienta utilizada

**Claude Code** (CLI de Anthropic) con el modelo Claude Opus. Todo el desarrollo se ha realizado mediante conversación iterativa con la IA, usando un enfoque de *spec-driven development*: Con este enfoque de desarrollo, redacto un prompt no muy extenso, máximo dos o tres líneas, en las cuales se describe una feature, y con este prompt, la IA crea un archivo Markdown con los pasos que se van a seguir para su implementación. Cada archivo de spec ha sido debatido en su creación para que esté más acorde con lo que se persigue desarrollar, una vez creado el archivo Markdown puede ser editado antes de su implementación. En cada paso de su implementación, estos pueden ser revisados y comprobar los cambios insertados por la IA, de forma que se pueden hacer ediciones en cada uno de los pasos. 

---

## Metodología: desarrollo guiado por specs

El flujo de trabajo ha sido:

1. **Redactar una spec** (`specs/XX-nombre.md`) que define alcance, modelo de datos, plan de implementación, criterios de aceptación y decisiones de diseño.
2. **La IA implementa** siguiendo la spec como referencia.
3. **Revisión humana**: Compruebo el resultado final y realizo correcciones si es necesario.

Este enfoque me permite mantener el control sobre la arquitectura y las decisiones de producto, delegando a la IA la generación de código y la implementación de lógica ya definida.

---

## SPEC 01 — Backend API con FastAPI

### Qué se le pidió

Crear el backend completo en Python/FastAPI a partir de la spec `specs/01-backend-api-fastapi.md`, que incluía:

- Estructura de carpetas con separación clara (modelos, routers, servicios, capa LLM).
- Carga del JSON de POIs en memoria con limpieza de datos (duplicados, coordenadas invertidas, prompt injection, precios heterogéneos, horarios incoherentes).
- Tres endpoints: `GET /pois` con filtros, `GET /pois/{id}` y `POST /preguntar`.
- Abstracción del LLM con interfaz, implementación Claude y fallback por keyword matching.
- Tests unitarios e integración con pytest.
- Script de evaluación contra `evaluacion.json`.
- Docker y docker-compose.

### Qué se aceptó directamente

- **Estructura del proyecto**: la IA generó una organización de carpetas limpia y coherente con la spec. Se aceptó tal cual.
- **Modelos Pydantic**: los modelos de dominio (`POI`, `Precio`, `Horario`, `Franja`) y los schemas de API se generaron correctamente a la primera.
- **Limpieza de datos**: la lógica para descartar poi-004, intercambiar coordenadas de poi-011, normalizar precios y marcar poi-018 como horario desconocido funcionó sin correcciones.
- **Servicio de filtrado**: la lógica de `filter_service.py` para combinar filtros de categoría, accesibilidad y horario fue correcta.
- **Fallback LLM**: el keyword matching como implementación sin red funcionó bien para las necesidades del proyecto.
- **Docker y docker-compose**: la configuración se generó correcta y funcional.

### Qué se corrigió o ajustó

- **Prompt injection en poi-013**: la IA propuso inicialmente usar una regex para eliminar el texto inyectado. Se le indicó que era más robusto truncar la descripción al contenido legítimo, sin depender de patrones específicos de inyección que podrían variar.
- **Criterios de aceptación del filtro `abierto_en`**: hubo que verificar manualmente qué POIs debían aparecer para `L-12:00` y corregir los que la spec listaba, contrastando con los datos reales del JSON.
- **Script de evaluación**: se ajustó el formato de salida para que reportara de forma más clara los resultados por pregunta, indicando cuáles POIs esperados se encontraron y cuáles no.

### Decisiones de diseño tomadas

- **Fallback como LLM por defecto** (`LLM_PROVIDER=fallback`): Se usa Claude por defecto. Se decidió que el fallback fuera por defecto para que la app funcione sin API key — se puede arrancar con `docker compose up` sin configurar nada.
- **Formato de `abierto_en`** con iniciales en español (L/M/X/J/V/S/D): he usado este formato porque la X podria provocar colisión M/Martes vs M/Miércoles.
- **Limpiar datos en memoria sin tocar el JSON original**: Se ha decidido realizar la limpieza de datos en memoria para no tocar el archivo original de datos. 

---

## SPEC 02 — Listado completo de POIs con filtros

### Qué se le pidió

Implementar el sistema de filtros en el frontend Angular, según la spec `specs/02-listado-filtros-pois.md`:

- Mostrar los 17 POIs completos.
- Barra de filtros con chips de categoría (multi-selección), toggle de accesibilidad, "Abierto ahora" y selector manual de día/hora.
- Filtro de categoría en cliente, accesibilidad y horario vía API.
- Estado vacío cuando ningún filtro coincide.
- Botón para limpiar día y hora seleccionados manualmente.
- Interacción correcta entre modo exploración (filtros) y modo IA (preguntar).

### Qué se aceptó directamente

- **Estructura de señales (signals)**: la IA usó correctamente `signal()` y `computed()` para el estado de filtros y resultados filtrados, siguiendo las buenas prácticas de Angular 20.
- **Lógica de `buildAbiertoEn()`**: la conversión de `Date.getDay()` (donde 0=Domingo) a las iniciales españolas.
- **Chips de categoría**: la multi-selección con `Set<string>` y el `computed()` que filtra en cliente.
- **Mutua exclusión** entre "Abierto ahora" y selector manual: la lógica de deshabilitar uno cuando el otro está activo.
- **Estado vacío**: el mensaje y botón de limpiar filtros.

### Qué se corrigió o ajustó

- **Separación cliente/servidor de filtros**: la IA inicialmente me propuso enviar todos los filtros a la API, incluida la categoría. Le pedí que la categoría debía filtrarse en cliente, para evitar tener que hacer otro endpoint ya que no lo vi necesario, accesibilidad y horario sí van a la API porque reutilizan la lógica compleja del backend.
- **Modo exploración vs. modo IA**: hubo que definir con claridad el comportamiento: al hacer una pregunta IA se limpian los filtros y se muestran solo los POIs de la respuesta; al tocar cualquier filtro se vuelve al modo exploración con la carga completa. La IA no tenía claro este flujo y se lo tuve que explicar.


### Decisiones de diseño tomadas por el desarrollador

- **Sin paginación**: 17 tarjetas no justifican paginación; el scroll natural es suficiente. La IA sugirió añadir paginación "por si crece", pero se descartó por innecesario.
- **Filtros integrados en la landing**: se valoró crear una ruta `/explorar` separada, pero se decidió mantener todo en la landing para no fragmentar la navegación en una app tan pequeña.
- **Multi-selección de categorías en cliente**: la alternativa era una llamada API por categoría seleccionada, pero con 17 POIs es instantáneo filtrar en memoria y se evitan llamadas redundantes al backend.

---

## Resumen

| Aspecto | Aportación de la IA | Aportación humana |
|---|---|---|
| Arquitectura backend | Generó la estructura de carpetas y la separación de responsabilidades | Definió la spec previa con las decisiones de diseño |
| Limpieza de datos | Implementó las 5 correcciones del JSON | Identificó los problemas en los datos y decidió la estrategia (limpiar en memoria) |
| Abstracción LLM | Generó interfaz, fallback y Claude impl. | Decidió que fallback fuera el default |
| Filtros frontend | Implementó signals, computed y lógica de filtrado | Decidió qué filtros van a cliente vs. API, diseñó la interacción entre modos |
| Tests | Generó la batería de tests unitarios e integración | Verificó que cubrieran los casos correctos |
| Estilos | Generó los estilos base | Iteró sobre el diseño visual hasta que fue usable |
| Docker | Generó Dockerfile y compose | Verificó que funcionara end-to-end |

La IA ha sido especialmente útil para generar código repetitivo (modelos, schemas, tests), implementar lógica ya definida en las specs y mantener la coherencia entre backend y frontend. Las decisiones de arquitectura, producto y experiencia de usuario se han tomado siempre por el desarrollador, usando la IA como herramienta de ejecución, no de diseño.

## Diseño de UI 

Se ha usado la herramienta nativa Cloud Design para generar los estilos en base a un prompt dado. Se ha instalado la skill de 'impeccable' para afinar los estilos de forma que parezcan menos generados por IA, pero finalmente no se ha usado. 