#!/bin/bash

# Путь к эмулятору
EMULATOR="python3 1stage.py"

# Путь к VFS
VFS_PATH="/tmp/vfs"

# Массив тестовых скриптов
TEST_SCRIPTS=("init.sh" "init1.sh" "init2.sh")

# Запуск эмулятора с каждым скриптом
for SCRIPT in "${TEST_SCRIPTS[@]}"; do
    echo "=== Запуск $SCRIPT ==="
    $EMULATOR --vfs-path "$VFS_PATH" --script "$SCRIPT"
    echo ""
done