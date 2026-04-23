#!/usr/bin/env python3
"""
memory_scheduler.py – автономный планировщик загрузки ОЗУ.

Настройки (меняйте только значения переменных ниже):
    FIRST_RUN      - дата и время первого запуска в формате "YYYY-MM-DD HH:MM"
    MEMORY_GB      - объём памяти в гигабайтах (1–50)
    HOLD_MINUTES   - длительность удержания памяти в минутах
    REPEAT_DAYS    - интервал повторения в днях (целое число)
"""

import time
import datetime
import sys

# ================== НАСТРОЙКИ ==================
FIRST_RUN = "2026-04-24 14:30"   # Год-месяц-день часы:минуты
MEMORY_GB = 10.0                  # Объём ОЗУ в ГБ
HOLD_MINUTES = 30                 # Длительность загрузки в минутах
REPEAT_DAYS = 3                   # Повторять каждые N дней
# ================================================

def parse_datetime(dt_str):
    """Преобразует строку в объект datetime."""
    try:
        return datetime.datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
    except ValueError as e:
        print(f"Ошибка в формате FIRST_RUN: {e}")
        sys.exit(1)

def allocate_memory(size_gb):
    """Выделяет блок памяти указанного размера (в ГБ) и возвращает его."""
    size_bytes = int(size_gb * 1024 ** 3)
    print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
          f"Выделение {size_gb:.2f} ГБ ({size_bytes:,} байт)...")
    try:
        data = bytearray(size_bytes)
        # Касаемся каждой страницы для реального выделения физической памяти
        page_size = 4096
        for i in range(0, size_bytes, page_size):
            data[i] = 0xFF
        print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
              f"Память выделена и инициализирована.")
        return data
    except MemoryError:
        print("Ошибка: недостаточно памяти. Уменьшите MEMORY_GB.")
        sys.exit(1)

def main():
    # Проверка входных значений
    if MEMORY_GB < 1 or MEMORY_GB > 50:
        print("MEMORY_GB должен быть от 1 до 50.")
        sys.exit(1)
    if HOLD_MINUTES <= 0:
        print("HOLD_MINUTES должно быть положительным числом.")
        sys.exit(1)
    if REPEAT_DAYS <= 0:
        print("REPEAT_DAYS должно быть положительным целым числом.")
        sys.exit(1)

    first_run_dt = parse_datetime(FIRST_RUN)
    next_run = first_run_dt

    print("=== Планировщик загрузки ОЗУ запущен ===")
    print(f"Первый запуск: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Объём памяти: {MEMORY_GB} ГБ")
    print(f"Длительность удержания: {HOLD_MINUTES} минут")
    print(f"Интервал повторения: {REPEAT_DAYS} дней")
    print("Для остановки нажмите Ctrl+C\n")

    try:
        while True:
            now = datetime.datetime.now()
            if now < next_run:
                wait_seconds = (next_run - now).total_seconds()
                print(f"Ожидание до {next_run.strftime('%Y-%m-%d %H:%M:%S')} "
                      f"({wait_seconds / 3600:.2f} часов)...")
                time.sleep(wait_seconds)

            # Фаза загрузки памяти
            mem_block = allocate_memory(MEMORY_GB)
            print(f"Удержание памяти {HOLD_MINUTES} минут...")
            time.sleep(HOLD_MINUTES * 60)
            del mem_block
            print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
                  f"Память освобождена.")

            # Вычисляем время следующего запуска (добавляем REPEAT_DAYS к текущему next_run)
            next_run += datetime.timedelta(days=REPEAT_DAYS)
            print(f"Следующий запуск запланирован на: "
                  f"{next_run.strftime('%Y-%m-%d %H:%M:%S')}\n")

    except KeyboardInterrupt:
        print("\nПолучен сигнал остановки. Завершение работы.")
        sys.exit(0)

if __name__ == "__main__":
    main()