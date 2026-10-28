"""
Script de evaluación: ejecuta las preguntas de evaluacion.json contra POST /preguntar
y reporta aciertos por pregunta y precisión global.

Uso:
    python -m scripts.evaluate                          # contra servidor local en 8000
    python -m scripts.evaluate --base-url http://host:port
    python -m scripts.evaluate --internal               # sin servidor, usa TestClient
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import httpx

EVAL_PATH = Path(__file__).resolve().parent.parent.parent / "references" / "datos" / "evaluacion.json"


def load_questions() -> list[dict]:
    return json.loads(EVAL_PATH.read_text(encoding="utf-8"))


def evaluate_external(base_url: str, questions: list[dict]) -> list[dict]:
    results: list[dict] = []
    with httpx.Client(base_url=base_url, timeout=30) as client:
        for q in questions:
            resp = client.post("/preguntar", json={"pregunta": q["pregunta"], "idioma": q["idioma"]})
            resp.raise_for_status()
            data = resp.json()
            results.append(_check(q, data["pois"]))
    return results


def evaluate_internal(questions: list[dict]) -> list[dict]:
    from fastapi.testclient import TestClient

    from app.data.loader import load_pois
    from app.data.store import POIStore
    from app.llm.factory import create_llm_assistant
    from app.config import settings
    from app.main import app
    from app.services.assistant_service import AssistantService

    poi_list = load_pois(settings.DATA_PATH)
    store = POIStore(poi_list)
    llm = create_llm_assistant(settings)
    app.state.store = store
    app.state.assistant = AssistantService(store, llm)

    results: list[dict] = []
    with TestClient(app) as client:
        for q in questions:
            resp = client.post("/preguntar", json={"pregunta": q["pregunta"], "idioma": q["idioma"]})
            resp.raise_for_status()
            data = resp.json()
            results.append(_check(q, data["pois"]))
    return results


def _check(question: dict, returned_pois: list[str]) -> dict:
    returned_set = set(returned_pois)
    expected_include = set(question.get("esperado_incluye", []))
    expected_exclude = set(question.get("esperado_excluye", []))

    missing = expected_include - returned_set
    wrongly_included = expected_exclude & returned_set

    if not expected_include and not expected_exclude:
        passed = len(returned_pois) == 0
    else:
        passed = len(missing) == 0 and len(wrongly_included) == 0

    return {
        "id": question["id"],
        "pregunta": question["pregunta"],
        "passed": passed,
        "returned": returned_pois,
        "expected_include": sorted(expected_include),
        "expected_exclude": sorted(expected_exclude),
        "missing": sorted(missing),
        "wrongly_included": sorted(wrongly_included),
    }


def print_report(results: list[dict]) -> None:
    total = len(results)
    passed = sum(1 for r in results if r["passed"])

    print("\n" + "=" * 60)
    print("EVALUACIÓN DEL ASISTENTE TURÍSTICO DE VALDELUMBRE")
    print("=" * 60)

    for r in results:
        status = "PASS" if r["passed"] else "FAIL"
        print(f"\n[{status}] {r['id']}: {r['pregunta']}")
        print(f"       POIs devueltos:  {r['returned']}")
        print(f"       Esperados:       {r['expected_include']}")
        print(f"       Excluidos:       {r['expected_exclude']}")
        if r["missing"]:
            print(f"       ✗ Faltan (esperados): {r['missing']}")
        if r["wrongly_included"]:
            print(f"       ✗ Incluidos indebidamente: {r['wrongly_included']}")

    print("\n" + "-" * 60)
    print(f"Resultado: {passed}/{total} preguntas correctas ({passed/total*100:.0f}%)")
    print("-" * 60 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Evalúa el endpoint /preguntar")
    parser.add_argument("--base-url", default="http://localhost:8000",
                        help="URL base del servidor (default: http://localhost:8000)")
    parser.add_argument("--internal", action="store_true",
                        help="Ejecutar sin servidor externo, usando TestClient")
    args = parser.parse_args()

    questions = load_questions()
    print(f"Cargadas {len(questions)} preguntas de evaluación.")

    if args.internal:
        print("Modo interno (TestClient, sin servidor externo).")
        results = evaluate_internal(questions)
    else:
        print(f"Evaluando contra {args.base_url}")
        results = evaluate_external(args.base_url, questions)

    print_report(results)

    passed = sum(1 for r in results if r["passed"])
    sys.exit(0 if passed == len(results) else 1)


if __name__ == "__main__":
    main()
