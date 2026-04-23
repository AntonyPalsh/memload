#!/bin/bash
#
#   FIRST_RUN      – дата и время первого запуска (формат "YYYY-MM-DD HH:MM")
#   MEM_GB         – объём памяти в ГБ
#   HOLD_MINUTES   – сколько минут держать память выделенной
#   REPEAT_DAYS    – интервал повторения в днях
#   SCRIPT_DIR     – путь к папке с mem_load.py (по умолчанию – текущая)

# ================= НАСТРОЙКИ =================
FIRST_RUN="2026-04-24 14:30"
MEM_GB="10.0"
HOLD_MINUTES="30"
REPEAT_DAYS="3"
SCRIPT_DIR="$(pwd)"
CPU_PROCENT="80"
# ==============================================

M_SCRIPT="$SCRIPT_DIR/m_load.py"
C_SCRIPT="$SCRIPT_DIR/c_load.py"

# Проверка наличия Python-скрипта
if [ ! -f "$M_SCRIPT" ]; then
    echo "Ошибка: $M_SCRIPT не найден."
    exit 1
fi

# Преобразование даты первого запуска в секунды с эпохи
if ! NEXT_RUN=$(date -d "$FIRST_RUN" +%s 2>/dev/null); then
    echo "Ошибка: неверный формат FIRST_RUN. Используйте 'YYYY-MM-DD HH:MM'"
    exit 1
fi

echo "=== Планировщик  ==="
echo "Первый запуск:  $FIRST_RUN"
echo "Объём памяти:   $MEM_GB ГБ"
echo "Длительность:   $HOLD_MINUTES минут"
echo "Повтор:         $REPEAT_DAYS дней"
echo "Скрипт Python:  $M_SCRIPT"
echo

# Функция обработки сигналов – завершаем Python-процесс, если он активен
cleanup() {
    echo
    if [ -n "$LOADER_PID" ] && kill -0 "$LOADER_PID" 2>/dev/null; then
        echo "Завершение Python-процесса (PID $LOADER_PID)..."
        kill -TERM "$LOADER_PID"
        wait "$LOADER_PID" 2>/dev/null
    fi
    echo "Планировщик остановлен."
    exit 0
}
trap cleanup SIGINT SIGTERM

while true; do
    NOW=$(date +%s)
    if [ "$NOW" -lt "$NEXT_RUN" ]; then
        WAIT=$(( NEXT_RUN - NOW ))
        echo "Ожидание до $(date -d "@$NEXT_RUN" '+%Y-%m-%d %H:%M:%S') (${WAIT} сек)..."
        sleep $WAIT
    fi

    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Запуск $M_SCRIPT $MEM_GB"

    python3 "$M_SCRIPT" "$MEM_GB" &
    
    M_LOADER_PID=$!
    echo "Python-m-процесс запущен с PID $M_LOADER_PID"

    python3 "$C_SCRIPT" --target-load "$CPU_PROCENT" &
    
    C_LOADER_PID=$!
    echo "Python-m-процесс запущен с PID $C_LOADER_PID"

    # Удерживаем память заданное время
    sleep $(( HOLD_MINUTES * 60 ))

    # Завершаем Python-процесс
    if kill -0 "$M_LOADER_PID" 2>/dev/null; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Завершение Python-процесса (PID $M_LOADER_PID)..."
        kill -TERM "$M_LOADER_PID"
        wait "$M_LOADER_PID" 2>/dev/null
    fi

    if kill -0 "$C_LOADER_PID" 2>/dev/null; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Завершение Python-процесса (PID $C_LOADER_PID)..."
        kill -TERM "$C_LOADER_PID"
        wait "$C_LOADER_PID" 2>/dev/null
    fi

    # Вычисляем время следующего запуска
    NEXT_RUN=$(( NEXT_RUN + REPEAT_DAYS * 24 * 3600 ))
    echo "Следующий запуск запланирован на $(date -d "@$NEXT_RUN" '+%Y-%m-%d %H:%M:%S')"
    echo
done