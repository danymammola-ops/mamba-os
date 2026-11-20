#!/usr/bin/env python3
"""
Test click on Gabriele Vinted in WhatsApp
"""

import sys, os, time, ctypes
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

# 1. Clicca sulla barra del titolo di WhatsApp per dargli il focus reale
print("1. Focus WhatsApp cliccando sul titolo...")
title_x = 450
title_y = 230
smooth_move(title_x, title_y, duration=0.2)
user32.mouse_event(2, 0, 0, 0, 0)
user32.mouse_event(4, 0, 0, 0, 0)
time.sleep(0.3)

# 2. Clicca direttamente sulla riga del contatto Gabriele Vinted (x=370, y=825)
print("2. Clicco sul contatto 'Gabriele Vinted' a (370, 825)...")
smooth_move(370, 825, duration=0.2)
user32.mouse_event(2, 0, 0, 0, 0)
user32.mouse_event(4, 0, 0, 0, 0)
time.sleep(0.8)

# 3. Clicca nella casella del messaggio (a destra, in basso)
# Con la chat aperta, il campo testo è a x=650, y=855
print("3. Clicco nella casella del messaggio a (650, 855)...")
smooth_move(650, 855, duration=0.2)
user32.mouse_event(2, 0, 0, 0, 0)
user32.mouse_event(4, 0, 0, 0, 0)
time.sleep(0.3)

# 4. Incolla il messaggio
messaggio = (
    "Ciao Gabriele! Un grande saluto da parte di Dany! 🎮\n\n"
    "Ti auguro una grandissima sessione di gioco su GTA 6! 🚗💥\n\n"
    "祝你《侠盗猎车手6》(GTA 6) 游戏愉快，玩得开心！\n"
    "(Zhù nǐ 《Xiádào Lièchēshǒu 6》 yóuxì yúkuài, wán de kāixīn!\n"
    "— Buona sessione e buon divertimento con GTA 6!)\n\n"
    "Un abbraccio da Dany! 👊🔥"
)
pyperclip.copy(messaggio)
pyautogui.hotkey('ctrl', 'v')
time.sleep(0.6)

# 5. Invio
print("4. Invio messaggio (Enter)...")
pyautogui.press('enter')
time.sleep(0.5)

# Sposta il mouse
smooth_move(800, 300, duration=0.2)

# Screenshot finale
screenshot_path = r"C:\Users\danym\mio\mamba\mamba\data\verify_gabriele_sent.png"
img = take_screenshot()
img.save(screenshot_path)
print(f"Salvato {screenshot_path}")
