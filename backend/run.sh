#!/bin/bash
# StarCourier Web - Запуск backend сервера
# Автоматическая проверка свободного порта

echo "========================================"
echo "  StarCourier Web - Backend Server"
echo "========================================"
echo ""

cd "$(dirname "$0")"

# Проверка виртуального окружения
if [ ! -f "venv/bin/python" ]; then
    echo "[ERROR] Виртуальное окружение не найдено!"
    echo "Запустите: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Активация виртуального окружения
source venv/bin/activate

# Функция проверки порта
check_port() {
    python -c "
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
result = sock.connect_ex(('127.0.0.1', $1))
sock.close()
exit(0 if result != 0 else 1)
" 2>/dev/null
}

# Поиск свободного порта
PORT=8000
MAX_PORT=8010

echo "[INFO] Проверка свободного порта..."

while [ $PORT -lt $MAX_PORT ]; do
    if check_port $PORT; then
        echo "[OK] Порт $PORT свободен"
        break
    else
        echo "[WARN] Порт $PORT занят"
        PORT=$((PORT + 1))
    fi
done

if [ $PORT -eq $MAX_PORT ]; then
    echo "[ERROR] Не удалось найти свободный порт в диапазоне 8000-8009"
    exit 1
fi

# Запуск сервера
echo ""
echo "[INFO] Запуск сервера на http://0.0.0.0:$PORT"
echo "[INFO] Docs: http://localhost:$PORT/docs"
echo ""

python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT --reload
