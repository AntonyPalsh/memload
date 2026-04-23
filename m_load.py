#!/usr/bin/env python3
"""
mem_load.py – выделяет ОЗУ заданного объёма и удерживает её до получения сигнала завершения.

Использование:
    ./mem_load.py <ГБ>
Пример:
    ./mem_load.py 10.5
"""

import sys
import time
import signal

def allocate_memory(size_gb: float):
    size_bytes = int(size_gb * 1024 ** 3)
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Выделение {size_gb:.2f} ГБ ({size_bytes:,} байт)...", flush=True)
    try:
        data = bytearray(size_bytes)
        # Принудительно выделяем физические страницы
        page_size = 4096
        for i in range(0, size_bytes, page_size):
            data[i] = 0xFF
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Память выделена. Ожидание завершения процесса (PID: {os.getpid()})...", flush=True)
        return data
    except MemoryError:
        print("Ошибка: недостаточно памяти для выгрузки.", flush=True)
        sys.exit(1)

def main():
    if len(sys.argv) != 2:
        print("Укажите объём передачи памяти в ГБ как единственный аргумент.")
        sys.exit(1)

    try:
        size_gb = float(sys.argv[1])
    except ValueError:
        print("Аргумент должен быть числом (ГБ).")
        sys.exit(1)

    if size_gb <= 0 or size_gb > 50:
        print("Объём должен быть от 1 до 50 ГБ.")
        sys.exit(1)

    import os
    # Игнорируем SIGTERM (будет использоваться для мягкого завершения)
    signal.signal(signal.SIGTERM, lambda signum, frame: sys.exit(0))
    # Игнорируем SIGINT (Ctrl+C) – управление только через kill
    signal.signal(signal.SIGINT, signal.SIG_IGN)

    mem_block = allocate_memory(size_gb)

    # Бесконечное ожидание, пока процесс не будет убит снаружи
    try:
        signal.pause()
    except KeyboardInterrupt:
        # На случай, если SIGINT всё же пройдёт
        pass
    finally:
        del mem_block
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Память освобождена для следующей выгрузки.", flush=True)

if __name__ == "__main__":
    main()