import shlex
import sys
import argparse

end_status = 0
commands = ["ls", "cd", "exit", "conf-dump"]

parser = argparse.ArgumentParser(description="Эмулятор оболочки ОС")
parser.add_argument("--vfs-path", default="/home/user", help="Путь к физическому расположению VFS")
parser.add_argument("--script", help="Путь к стартовому скрипту")
args = parser.parse_args()

config = {
    "vfs-path": args.vfs_path,
    "script": args.script if args.script else "не задан"
}

def command(command_line):
    try:
        user_input = shlex.split(command_line)
    except ValueError as err:
        print(f"Ошибка парсинга: {err}")
        return True

    if not user_input:
        return True
    cmd = user_input[0]
    args = user_input[1:]

    if cmd not in commands:
        print(f"Неизвестная команда: {cmd}")
        return True

    if cmd == "ls":
        print(cmd, args)
    elif cmd == "cd":
        print(cmd, args)
    elif cmd == "conf-dump":
        for k, v in config.items():
            print(f"{k} = {v}")
    elif cmd == "exit":
        print("Выход")
        return False
    return True

if args.script:
    try:
        with open(args.script, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                print(f"<VFS> {line}")
                running = command(line)
                if not running:
                    end_status = 1
                    break
    except Exception as e:
        print(f"Ошибка при выполнении скрипта: {e}")

# --- REPL ---
while not end_status:
    command_line = input("<VFS> ")
    if not command(command_line):
        sys.exit(0)
