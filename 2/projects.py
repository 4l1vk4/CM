import json
import sys
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
        raise FileNotFoundError(f"Не найден файл: {p}")
    return json.loads(p.read_text(encoding="utf-8"))

def validate(cfg):
    errors = []
    for key, typ in CONFIG.items():
        if key not in cfg:
            errors.append(f"[Ошибка] Отсутствует параметр: {key}")
            continue
        if not isinstance(cfg[key], typ):
            errors.append(
                f"[Ошибка] Неверный тип у параметра '{key}': ожидался {typ.__name__}, получен {type(cfg[key]).__name__}")

    if errors:
        return errors
    return cfg

def main():
    if len(sys.argv) < 2:
        print("В вводных данных отсутствует файл конфигурации")
        sys.exit(1)
    try:
        cfg = load(sys.argv[1])
        cfg = validate(cfg)
    except (FileNotFoundError, json.JSONDecodeError, KeyError, TypeError) as e:
        print("[Ошибка]", e)
        sys.exit(1)

    if cfg:
        print("\n".join(cfg))
    else:
        for k, v in cfg.items():
            print(f"{k}: {v}")

if __name__ == "__main__":
    main()