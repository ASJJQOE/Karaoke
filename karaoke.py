import os
import time
import pygame
import yt_dlp
import syncedlyrics

# Colores de consola
CYAN = "\033[96m"
AMARILLO = "\033[93m"
BLANCO = "\033[37m"

def obtener_letras(cancion):
    print(f"{CYAN}Buscando letras sincronizadas...{BLANCO}")
    lrc = syncedlyrics.search(cancion)
    if not lrc:
        return None
    
    # Procesar formato [min:seg.ms]
    lineas = []
    for linea in lrc.split('\n'):
        if linea.startswith('[') and ']' in linea:
            try:
                tiempo_str, texto = linea.split(']', 1)
                m, s = tiempo_str[1:].split(':')
                segundos = int(m) * 60 + float(s)
                if texto.strip():
                    lineas.append((segundos, texto.strip()))
            except:
                pass
    return lineas

def reproducir_magia(cancion):
    letras = obtener_letras(cancion)
    if not letras:
        print("No se encontraron letras exactas para sincronizar.")
        return

    print(f"{CYAN}Preparando el audio en la sombra...{BLANCO}")
    archivo_temp = "audio_temporal"
    opciones = {
        'format': 'bestaudio',
        'outtmpl': f'{archivo_temp}.%(ext)s',
        'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3'}],
        'quiet': True,
        'noplaylist': True
    }
    
    with yt_dlp.YoutubeDL(opciones) as ydl:
        ydl.download([f"ytsearch1:{cancion}"])
        
    pygame.mixer.init()
    pygame.mixer.music.load(f"{archivo_temp}.mp3")
    pygame.mixer.music.play()
    
    inicio = time.time()
    print(f"\n{CYAN}--- ¡Música Maestro! ---{AMARILLO}\n")
    
    for i, (tiempo, texto) in enumerate(letras):
        espera = tiempo - (time.time() - inicio)
        if espera > 0:
            time.sleep(espera)
            
        # Calcular velocidad para el efecto de máquina de escribir
        duracion = 2.0
        if i < len(letras) - 1:
            duracion = letras[i+1][0] - tiempo
            
        tiempo_por_letra = (duracion * 0.7) / max(len(texto), 1)
        
        for letra in texto:
            print(letra, end="", flush=True)
            time.sleep(max(tiempo_por_letra, 0.02)) # Límite de velocidad
        print()
        
    while pygame.mixer.music.get_busy():
        time.sleep(1)
        
    pygame.mixer.quit()
    os.remove(f"{archivo_temp}.mp3")
    print(f"\n{BLANCO}Limpieza completada. No quedó rastro.")

if __name__ == "__main__":
    tema = input("Escribe la canción y el artista: ")
    reproducir_magia(tema)
