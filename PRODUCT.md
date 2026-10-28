# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Technical evaluator reviewing a full-stack coding challenge. The app simulates a tourist assistant for the fictional town of Valdelumbre; the evaluator assesses code quality, architecture decisions, data handling, and the resulting UI as a working demo.

## Product Purpose

Demonstrate full-stack engineering competence through a tourist assistant that answers natural-language questions about points of interest in Valdelumbre. The backend (FastAPI) is complete: 17 POIs loaded from JSON with data-cleaning pipeline, bilingual support (es/en), filtering, and an LLM abstraction (Claude + keyword-matching fallback). The frontend (Angular) needs to surface these capabilities as a polished, functional interface. Success means the evaluator sees a well-crafted product that could serve real tourists, built with clean, idiomatic code.

## Positioning

A technical demo that goes beyond "it works": deliberate data-quality decisions (duplicate detection, coordinate correction, prompt-injection defense, price normalization), a pluggable LLM layer, and a frontend that treats the demo scenario with production-grade care.

## Operating Context

The evaluator runs `docker compose up` or local dev commands, opens the app in a browser, explores POIs, asks questions via the chat interface, and reviews the codebase. The backend API is at localhost:8000, the frontend at localhost:4200. No API key is needed for the default fallback mode.

## Capabilities and Constraints

- 17 POIs across 7 categories: monumento, naturaleza, museo, gastronomia, espacio_publico, ruta, servicio
- Bilingual content (Spanish/English) for names and descriptions
- Filtering by category, accessibility, and open-at (day+time)
- Natural-language question answering via POST /preguntar
- No database; all data loaded from JSON into memory at startup
- No user authentication or persistence
- Season-aware filtering not yet implemented (known limitation)
- Undecided: map visualization, pagination

## Evidence on Hand

- `references/datos/pois.json`: 18 raw POIs (17 after deduplication) with intentional defects documented in DATOS.md
- `references/datos/evaluacion.json`: 6 evaluation questions with expected POI answers
- No images, logos, or visual assets exist. Valdelumbre is entirely fictional.

## Product Principles

1. **Show the thinking, not just the code.** Every data-cleaning decision is documented and tested; the evaluator should see deliberate engineering, not accidental correctness.
2. **Work without setup.** Default configuration requires zero API keys or external services. `docker compose up` and it runs.
3. **Treat the fiction seriously.** The UI should feel like a real tourist tool, not a throwaway demo screen. The quality of the simulation is part of the demonstration.
