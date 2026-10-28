# SPEC 02 — Listado completo de POIs con filtros

**Estado:** implementado
**Fecha:** 2026-10-28
**Depende de:** SPEC 01
**Objetivo:** Mostrar los 17 POIs en la landing actual con filtros por categoría (multi-selección), accesibilidad y abierto ahora/en momento concreto.

---

## Alcance

### Incluido

- Barra de filtros integrada en la sección de resultados de la landing actual
- Chips de categoría con multi-selección (filtrado en cliente)
- Toggle de accesibilidad
- Check "Abierto ahora" (hora local del navegador) y selector manual de día/hora (mutuamente excluyentes)
- Carga inicial de todos los POIs (sin límite de 6)
- Contador de resultados actualizado al filtrar
- Parámetros de filtro en `ApiService.listPois()`
- Estado vacío cuando ningún POI coincide con los filtros

### NO incluido

- Paginación ni scroll infinito (17 POIs no lo justifican)
- Cambios en el backend (los endpoints ya soportan los filtros necesarios)
- Persistencia de filtros entre sesiones
- Mapa general con todos los POIs
- Detalle individual de POI (será otra spec)
- Internacionalización del selector de día (se usan las iniciales L/M/X/J/V/S/D del backend)

---

## Modelo de datos

No se introducen nuevos modelos. Se reutilizan `POIResponse` y `POIListResponse` de `src/app/models/poi.model.ts`.

Se añaden interfaces para el estado de los filtros dentro del componente:

```typescript
interface FilterState {
  categorias: Set<string>;       // vacío = todas
  accesible: boolean | null;     // null = sin filtro, true = solo accesibles
  abiertoAhora: boolean;         // usa hora local del navegador
  diaManual: number | null;      // 1-7, null = sin selección
  horaManual: string | null;     // "HH:MM", null = sin selección
}
```

---

## Plan de implementación

1. **Ampliar `ApiService.listPois()`** — Añadir parámetros opcionales `accesible` y `abierto_en` al método. La categoría no se pasa a la API porque el filtro multi-selección se aplica en cliente.

2. **Crear la barra de filtros en la landing** — Añadir una sección de filtros entre el header de resultados y la grid:
   - Fila de chips con las 7 categorías (toggle individual, multi-selección)
   - Toggle/checkbox "♿ Accesible"
   - Checkbox "Abierto ahora" + selector manual de día (dropdown con L/M/X/J/V/S/D) y hora (input time o dropdown HH:MM)
   - Cuando "Abierto ahora" está activo, el selector manual se deshabilita (y viceversa)
   - Botón "×" junto al selector manual para limpiar día/hora y volver al estado sin filtro de horario

3. **Lógica de filtrado en el componente** — Señales (`signal`) para el estado de filtros. `computed()` que combina los filtros:
   - Categoría: filtrado en cliente sobre los POIs ya cargados
   - Accesible y abierto_en: se envían como query params a `GET /pois`
   - Al cambiar filtros de categoría: no se re-llama a la API, se re-filtra el array en memoria
   - Al cambiar accesible o abierto: se re-llama a la API con los params, luego se aplica filtro de categoría en cliente

4. **Construcción del parámetro `abierto_en`** — Función helper que convierte la hora local (o la selección manual) al formato `X-HH:MM`:
   - Mapeo de `Date.getDay()` (0=Domingo) a iniciales españolas: `[D, L, M, X, J, V, S]`
   - Formato: `${inicial}-${HH}:${MM}`

5. **Carga inicial sin límite** — Reemplazar el `slice(0, 6)` actual en `loadInitialPois()` por la carga completa de los 17 POIs.

6. **Estado vacío** — Cuando los filtros no devuelven resultados, mostrar un mensaje tipo "No hay lugares que coincidan con los filtros seleccionados" con un botón para limpiar filtros.

7. **Estilos** — Añadir estilos para la barra de filtros en `landing.scss`: chips con estado activo/inactivo, layout responsive (chips en scroll horizontal en móvil).

---

## Criterios de aceptación

- [ ] Al cargar la landing se ven los 17 POIs (no solo 6)
- [ ] Los 7 chips de categoría se muestran y se pueden activar/desactivar independientemente
- [ ] Con 2 categorías seleccionadas, se ven solo los POIs de esas 2 categorías
- [ ] Con "♿ Accesible" activo, solo se muestran POIs con `accesible=true`
- [ ] "Abierto ahora" envía `abierto_en=X-HH:MM` con el día/hora local del navegador
- [ ] El selector manual de día/hora se deshabilita cuando "Abierto ahora" está activo (y viceversa)
- [ ] Seleccionar día=Lunes y hora=12:00 manualmente envía `abierto_en=L-12:00`
- [ ] Los filtros se combinan con AND: categoría + accesible + abierto filtra correctamente
- [ ] Cuando no hay resultados se muestra el mensaje de estado vacío con botón para limpiar filtros
- [ ] El contador de resultados refleja el número filtrado (ej: "5 lugares en Valdelumbre")
- [ ] La funcionalidad de preguntar con IA sigue funcionando igual que antes
- [ ] La barra de filtros es usable en móvil (chips con scroll horizontal si no caben)

---

## Decisiones tomadas

| Decisión | Alternativa descartada | Justificación |
|---|---|---|
| Filtro de categoría multi-selección en cliente | Una llamada API por categoría | Solo hay 17 POIs; filtrar en cliente es instantáneo y evita llamadas redundantes |
| Accesible y abierto_en se envían a la API | Filtrar todo en cliente | Reutilizar la lógica de filtrado del backend (especialmente la de horarios que es compleja) |
| "Abierto ahora" y selector manual mutuamente excluyentes | Ocultar el manual cuando "ahora" está activo | Mutuamente excluyente es más claro: el usuario siempre ve ambas opciones pero entiende que solo una puede estar activa |
| Sin paginación | Paginación con chunks de 6 | 17 tarjetas no justifican paginación; scroll natural es suficiente |
| Filtros integrados en la landing | Nueva ruta /explorar | El usuario prefiere no fragmentar la navegación; la landing ya tiene la sección de resultados |

---

## Riesgos identificados

- **Interacción filtros + pregunta IA**: la landing tiene dos modos de obtener POIs (filtros y pregunta IA). Hay que definir bien cuándo se usan unos u otros. Mitigación: al hacer una pregunta IA se limpian los filtros y se muestran solo los POIs de la respuesta; al tocar un filtro se vuelve al modo exploración con todos los POIs.
