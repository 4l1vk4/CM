import json
import sys
import urllib.request
from pathlib import Path

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

def get_dependencies(cfg):
    print("\nСбор данных о зависимостях")
    repo_url = cfg["repository_url"]
    mode = cfg["test_repo_mode"]

    try:
        if mode == "local":
            path = Path(repo_url)
            if not path.exists():
                raise FileNotFoundError(f"Локальный файл не найден: {path}")
            data = json.loads(path.read_text(encoding="utf-8"))
        elif mode == "remote":
            with urllib.request.urlopen(repo_url) as response:
                data = json.loads(response.read().decode("utf-8"))
        else:
            raise ValueError(f"Неизвестный режим: {mode}")
    except Exception as e:
        print(f"[Ошибка при загрузке данных]: {e}")
        sys.exit(1)

    pkg_version = data.get("version")
    if pkg_version is None:
        print("[Информация] У пакета нет явной версии, используется единственная доступная версия.")
    elif pkg_version != cfg["package_version"]:
        print(f"[Внимание] Версия пакета ({pkg_version}) не совпадает с указанной в конфиге ({cfg['package_version']})")

    deps = data.get("dependencies", {})
    if not deps:
        print("У пакета нет прямых зависимостей.")
    else:
        filter_substr = cfg.get("filter_substring", "").lower()
        filtered = {name: ver for name, ver in deps.items() if filter_substr in name.lower()} if filter_substr else deps

        print("Прямые зависимости:")
        for name, ver in filtered.items():
            print(f"- {name}: {ver}")

def main():
    if len(sys.argv) < 2:
        print("Ошибка: укажите путь к файлу конфигурации (JSON).")
        sys.exit(1)

    try:
        cfg = load(sys.argv[1])
        cfg = validate(cfg)
        for k, v in cfg.items():
            print(f"{k}: {v}")
        get_dependencies(cfg)
    except (FileNotFoundError, json.JSONDecodeError, TypeError, ValueError) as e:
        print("[Ошибка]", e)
        sys.exit(1)

if __name__ == "__main__":
    main()