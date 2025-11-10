import json
import sys
import urllib.request
from pathlib import Path
from collections import deque

CONFIG = {
    "package_name": str,
    "repository_url": str,
    "test_repo_mode": str,
    "package_version": str,
    "ascii_tree_mode": bool,
    "filter_substring": str,
}

def load(path):
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Не найден файл конфигурации: {p}")
    return json.loads(p.read_text(encoding="utf-8"))

def validate(cfg):
    errors = []
    for key, typ in CONFIG.items():
        if key not in cfg:
            errors.append(f"[Ошибка] Отсутствует параметр: {key}")
            continue
        if not isinstance(cfg[key], typ):
            errors.append(
                f"[Ошибка] Неверный тип у параметра '{key}': ожидался {typ.__name__}, получен {type(cfg[key]).__name__}"
            )

    if errors:
        for e in errors:
            print(e)
        sys.exit(1)
    return cfg

def build_dependency_graph(cfg):
    print("\n=== Построение графа зависимостей ===")

    start_pkg = cfg["package_name"]
    mode = cfg["test_repo_mode"]
    repo_url = cfg["repository_url"]
    filter_substr = cfg.get("filter_substring", "").lower()

    try:
        # Загружаем данные в зависимости от режима
        if mode == "graph" or mode == "local":
            path = Path(repo_url)
            if not path.exists():
                raise FileNotFoundError(f"Файл графа не найден: {path}")
            data = json.loads(path.read_text(encoding="utf-8"))
        elif mode == "remote":
            with urllib.request.urlopen(repo_url) as response:
                data = json.loads(response.read().decode("utf-8"))
        else:
            raise ValueError(f"Неизвестный режим: {mode}")
    except Exception as e:
        print(f"[Ошибка при загрузке данных]: {e}")
        sys.exit(1)

    # Проверяем тип данных
    if not isinstance(data, dict):
        print("[Ошибка] Неверный формат данных графа (ожидается объект JSON).")
        sys.exit(1)

    # Если указан фильтр — исключаем пакеты, которые содержат подстроку
    if filter_substr:
        data = {k: v for k, v in data.items() if filter_substr not in k.lower()}

    visited = set()
    queue = [start_pkg]
    graph = {}
    has_cycle = False

    while queue:
        pkg = queue.pop(0)
        if pkg in visited:
            has_cycle = True
            continue
        visited.add(pkg)

        deps = data.get(pkg, [])
        if not isinstance(deps, list):
            deps = []

        # Учитываем фильтр для зависимостей
        deps = [d for d in deps if filter_substr not in d.lower()] if filter_substr else deps

        graph[pkg] = deps
        for dep in deps:
            if dep not in visited:
                queue.append(dep)

    print("\nГраф зависимостей (BFS):")
    for pkg, deps in graph.items():
        if deps:
            print(f"- {pkg} -> {', '.join(deps)}")
        else:
            print(f"- {pkg} -> (нет зависимостей)")

    if has_cycle:
        print("\nОбнаружены циклические зависимости")
    else:
        print("\nЦиклов не обнаружено.")


def main():
    if len(sys.argv) < 2:
        print("Ошибка: укажите путь к файлу конфигурации (JSON).")
        sys.exit(1)

    try:
        cfg = load(sys.argv[1])
        cfg = validate(cfg)
        for k, v in cfg.items():
            print(f"{k}: {v}")

        build_dependency_graph(cfg)

    except (FileNotFoundError, json.JSONDecodeError, TypeError, ValueError) as e:
        print("[Ошибка]", e)
        sys.exit(1)

if __name__ == "__main__":
    main()