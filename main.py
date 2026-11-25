import time

from brain import AutonomousBrain
from config import CONFIG
from memory import MemoryStore
from web_ui import start_web_server


def run() -> None:
    memory = MemoryStore(CONFIG.db_path)
    brain = AutonomousBrain(CONFIG, memory)
    server = start_web_server(CONFIG.web_host, CONFIG.web_port, memory)

    print(f"Otonomi sistemi başlatıldı -> http://{CONFIG.web_host}:{CONFIG.web_port}")
    try:
        while True:
            try:
                result = brain.step()
                print(
                    f"[Döngü {result['cycle']}] Aksiyon: {result['action']} | "
                    f"Kayıt: {result['research_items']} | Sinyal: {result['social_signal']}"
                )
            except Exception as exc:
                print(f"[Uyarı] Döngü hatası yakalandı, sistem çalışmaya devam ediyor: {exc}")
            time.sleep(CONFIG.loop_interval_seconds)
    except KeyboardInterrupt:
        print("\nKapatma sinyali alındı, sistem durduruluyor...")
    finally:
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    run()
