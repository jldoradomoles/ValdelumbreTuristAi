You are an expert in TypeScript, Angular, Python, FastAPI, and scalable web application development. You write maintainable, performant, and accessible code following best practices.

## Project Overview

Valdelumbre Tourist AI — a tourist assistant for the fictional town of Valdelumbre. Backend API in Python/FastAPI, frontend in Angular.

## Backend (Python/FastAPI)

- Python 3.12+, FastAPI, Pydantic v2, pydantic-settings
- Data loaded from `references/datos/pois.json` into memory at startup (no database)
- LLM abstraction: `LLMAssistant` interface with Claude and fallback (keyword matching) implementations
- `LLM_PROVIDER` env var controls which implementation: `fallback` (default, no API key needed) or `claude`
- Tests with pytest + pytest-asyncio
- Run backend: `cd backend && uvicorn app.main:app --reload`
- Run tests: `cd backend && pytest`
- Run evaluation: `cd backend && python -m scripts.evaluate --internal`
- Docker: `docker compose up` from project root

### Backend Structure

```
backend/app/
  main.py           # FastAPI app, lifespan, CORS
  config.py         # Settings via pydantic-settings
  models/poi.py     # Domain models (POI, Precio, Horario, etc.)
  models/api.py     # API request/response schemas
  data/loader.py    # JSON loading with data cleaning
  data/store.py     # In-memory POI store
  routers/pois.py   # GET /pois, GET /pois/{id}
  routers/preguntar.py  # POST /preguntar
  services/filter_service.py  # Filtering logic
  services/assistant_service.py  # Orchestrates LLM calls
  llm/base.py       # Abstract LLMAssistant interface
  llm/claude.py     # Claude implementation
  llm/fallback.py   # Keyword-matching fallback
  llm/factory.py    # Factory based on LLM_PROVIDER
```

### Data Cleaning (applied at load time, original JSON untouched)

- poi-004: discarded (duplicate of poi-003)
- poi-011: lat/lon swapped
- poi-013: prompt injection stripped from description
- Prices normalized to typed `Precio` model
- poi-018: `horario_desconocido=True` (always_open=false + empty franjas)

## Python Best Practices

- Use type hints everywhere
- Use Pydantic models for data validation
- Use `async` for I/O-bound operations
- Use `pydantic-settings` for configuration
- Keep business logic in services, not in routers
- Use pytest fixtures for test setup

## TypeScript Best Practices

- Use strict type checking
- Prefer type inference when the type is obvious
- Avoid the `any` type; use `unknown` when type is uncertain

## Angular Best Practices

- Always use standalone components over NgModules
- Must NOT set `standalone: true` inside Angular decorators. It's the default.
- Use signals for state management
- Implement lazy loading for feature routes
- Do NOT use the `@HostBinding` and `@HostListener` decorators. Put host bindings inside the `host` object of the `@Component` or `@Directive` decorator instead
- Use `NgOptimizedImage` for all static images.
  - `NgOptimizedImage` does not work for inline base64 images.

## Components

- Keep components small and focused on a single responsibility
- Use `input()` and `output()` functions instead of decorators
- Use `computed()` for derived state
- Set `changeDetection: ChangeDetectionStrategy.OnPush` in `@Component` decorator
- Prefer inline templates for small components
- Prefer Reactive forms instead of Template-driven ones
- Do NOT use `ngClass`, use `class` bindings instead
- Do NOT use `ngStyle`, use `style` bindings instead

## State Management

- Use signals for local component state
- Use `computed()` for derived state
- Keep state transformations pure and predictable
- Do NOT use `mutate` on signals, use `update` or `set` instead

## Templates

- Keep templates simple and avoid complex logic
- Use native control flow (`@if`, `@for`, `@switch`) instead of `*ngIf`, `*ngFor`, `*ngSwitch`
- Use the async pipe to handle observables

## Services

- Design services around a single responsibility
- Use the `providedIn: 'root'` option for singleton services
- Use the `inject()` function instead of constructor injection
