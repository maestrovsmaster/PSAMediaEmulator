#!/bin/bash
# Скрипт для збірки десктоп додатка SmegEmulator

echo "Збірка SmegEmulator..."
rm -rf build dist
pyinstaller --onefile --windowed --name=SmegEmulator --additional-hooks-dir=./hooks main.py

if [ $? -eq 0 ]; then
    echo "Збірка завершена успішно!"
    echo "Виконуваний файл: ./dist/SmegEmulator"
    ls -lh dist/SmegEmulator
else
    echo "Помилка збірки!"
    exit 1
fi
