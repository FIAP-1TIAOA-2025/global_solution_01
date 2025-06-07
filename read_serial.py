#!/usr/bin/env python3
"""
read_serial.py  –  Monitor de log da porta serial do ESP32

Uso típico:
    # Porta e baud auto-detectados
    python tools/read_serial.py

    # Porta explícita (ex.: Windows)
    python tools/read_serial.py -p COM4

    # Porta e baud customizados
    python tools/read_serial.py -p /dev/ttyUSB0 -b 9600
"""

import argparse
import configparser
import os
import sys

import serial
import serial.tools.list_ports

# --- Constantes -------------------------------------------------------------

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INI_FILE = os.path.join(ROOT_DIR, "platformio.ini")
DEFAULT_BAUD = 115_200      # valor achado em Serial.begin(115200)

# --- Funções auxiliares -----------------------------------------------------


def ler_baud_do_ini() -> int | None:
    """Tenta obter monitor_speed do platformio.ini (caso exista)."""
    if not os.path.isfile(INI_FILE):
        return None

    cfg = configparser.ConfigParser()
    cfg.read(INI_FILE, encoding="utf-8")

    for section in cfg.sections():
        if cfg.has_option(section, "monitor_speed"):
            try:
                return int(cfg[section]["monitor_speed"])
            except ValueError:
                pass  # ignora valores inválidos

    return None


def detectar_porta() -> str:
    """
    Escolhe a primeira porta USB que pareça ser de um conversor serial
    (CH340, CP210, Silabs, etc.). Lança RuntimeError se não encontrar nada.
    """
    for porta in serial.tools.list_ports.comports():
        desc = porta.description.lower()
        if any(k in desc for k in ("usb", "uart", "silabs", "cp210", "ch340")):
            return porta.device  # ex.: 'COM4' ou '/dev/cu.SLAB_USBtoUART'
    raise RuntimeError(
        "Nenhuma porta serial compatível encontrada. "
        "Conecte a placa e/ou use o parâmetro --port."
    )


# --- Programa principal -----------------------------------------------------


def main() -> None:
    ini_baud = ler_baud_do_ini()
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-p",
        "--port",
        help="porta serial (ex.: COM4 ou /dev/ttyUSB0). "
        "Se omitido, o script tenta detectar automaticamente.",
    )
    parser.add_argument(
        "-b",
        "--baud",
        type=int,
        default=ini_baud or DEFAULT_BAUD,
        help=f"baud-rate (padrão: {ini_baud or DEFAULT_BAUD})",
    )
    args = parser.parse_args()

    porta = args.port or detectar_porta()

    try:
        with serial.Serial(port=porta, baudrate=args.baud, timeout=1) as ser:
            print(f"▶ Escutando {porta} @ {args.baud} baud — Ctrl+C para sair")
            while True:
                linha = ser.readline().decode(errors="ignore").rstrip()
                if linha:
                    print(linha)
    except serial.SerialException as err:
        sys.exit(f"⚠️  Erro ao abrir porta {porta}: {err}")
    except KeyboardInterrupt:
        print("\nEncerrado pelo usuário")


if __name__ == "__main__":
    main()
