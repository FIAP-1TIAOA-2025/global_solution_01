import os
import serial

# --- Constantes -------------------------------------------------------------

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INI_FILE = os.path.join(ROOT_DIR, "platformio.ini")
SERIAL_URL = 'rfc2217://localhost:8180'
BAUDRATE = 115200


def flood_sensor() -> None:
    ser = serial.serial_for_url(SERIAL_URL, baudrate=BAUDRATE, timeout=5000)
    
    while True :
        try: 
            line = ser.readline().decode('utf-8').strip()
            if not line:
                return {
                "flood_risk": False,
                "probability": 0.0
                }
            elif "ALERTA" in line.upper():
                print("Recebido:", line)
                return {
                    "flood_risk": True,
                    "probability": 1.0
                }
            
            
        except KeyboardInterrupt:
            print("Parado pelo usuário.")
            break
        except Exception as e:
            print("Erro:", e)
            continue


if __name__ == "__main__":
    flood_sensor()
