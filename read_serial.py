import os
import serial

# --- Constantes -------------------------------------------------------------

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INI_FILE = os.path.join(ROOT_DIR, "platformio.ini")
DEFAULT_BAUD = 115_200      # valor achado em Serial.begin(115200)
SERIAL_URL = 'rfc2217://localhost:8180'
BAUDRATE = 115200


def main() -> None:
    ser = serial.serial_for_url(SERIAL_URL, baudrate=BAUDRATE, timeout=2)
    
    while True :
        try: 
            line = ser.readline().decode('utf-8').strip()
            if not line:
                continue
            print("Recebido:", line)
        
        except KeyboardInterrupt:
            print("Parado pelo usuário.")
            break
        except Exception as e:
            print("Erro:", e)
            continue


if __name__ == "__main__":
    main()
