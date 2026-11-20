#!/usr/bin/env python3
"""
mamba/moves/send_gabriele_final.py - Clicca Gabriele Vinted e invia messaggio
"""

import sys, time, ctypes
import pyautogui, pyperclip

sys.path.insert(0, r"C:\Users\danym\mio\mamba")
from mamba.moves.user_moves import (
    attach_to_user_desktop,
    smooth_move,
    click_at,
    take_screenshot
)

attach_to_user_desktop()
user32 = ctypes.windll.user32
import uiautomation as auto

root = auto.GetRootControl()
wa = next((w for w in root.GetChildren() if 'whatsapp' in (w.Name or '').lower()), None)
if wa:
    user32.SwitchToThisWindow(wa.NativeWindowHandle, True)
    time.sleep(0.3)

# 1. Clicca su Gabriele Vinted nella lista chat a (180, 715)
print("1. 👤 Clicco sul contatto Gabriele Vinted a (180, 715)...")
smooth_move(180, 715, duration=0.2)
user32.mouse_event(2, 0, 0, 0, 0)
user32.mouse_event(4, 0, 0, 0, 0)
time.sleep(0.8)

# 2. Clicca nel campo messaggio in basso a destra a (450, 835)
print("2. ✍️ Clicco nel campo di testo messaggio a (450, 835)...")
smooth_move(450, 835, duration=0.2)
user32.mouse_event(2, 0, 0, 0, 0)
user32.mouse_event(4, 0, 0, 0, 0)
time.sleep(0.3)

# 3. Incolla il messaggio
messaggio = (
    "Ciao Gabriele! Un grande saluto da parte di Dany! 🎮\n\n"
    "Ti auguro una grandissima sessione di gioco su GTA 6! 🚗💥\n\n"
    "祝你《侠盗猎车手6》(GTA 6) 游戏愉快，玩得开心！\n"
    "(Zhù nǐ 《Xiádào Lièchēshǒu 6》 yóuxì yúkuài, wán de kāixīn!\n"
    "— Buona sessione e buon divertimento con GTA 6!)\n\n"
    "Un abbraccio da Dany! 👊🔥"
)

print("3. 📋 Incollo il messaggio con il saluto e l'augurio in cinese per GTA 6...")
pyperclip.copy(messaggio)
pyautogui.hotkey('ctrl', 'v')
time.sleep(0.5)

# 4. Invio
print("4. 🚀 Invio il messaggio (Enter)...")
pyautogui.press('enter')
time.sleep(0.5)

# Sposta il mouse
smooth_move(200, 200, duration=0.2)

# Screenshot
path = r"C:\Users\danym\mio\mamba\mamba\data\verify_gabriele_delivered.png"
take_screenshot().save(path)
print(f"✅ Messaggio inviato! Screenshot salvato in {path}")
