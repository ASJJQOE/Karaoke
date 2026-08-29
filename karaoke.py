import os
import sys
import time
import yt_dlp
import syncedlyrics
import pygame

def limpiar_pantalla():
    os.system('cls' if os.name == 'nt' else 'clear')

def reproducir_magia(cancion):
    print("\nBuscando letras sincronizadas...")
    letra_lrc = syncedlyrics.search(cancion)
    
    if not letra_lrc:
        print("No se encontraron letras sincronizadas, pero intentaremos reproducir la música.")
        letra_lrc = "[0] ♪ (Sin letra sincronizada disponible) ♪"

    print("Preparando el audio...")
    
    # Usamos el cliente 'ios' o 'tv_embedded' para evitar el bloqueo de bot en la nube
    ydl_opts = {
        'format': 'bestaudio/best',
        'extractor_args': {'youtube': {'player_client': ['ios']}},
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': 'cancion_temp.%(ext)s',
        'quiet': True,
        'no_warnings': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([f"ytsearch1:{cancion} karaoke"])
    except Exception as e:
        print(f"Error al descargar la canción: {e}")
        return

    archivo_audio = "cancion_temp.mp3"
    if not os.path.exists(archivo_audio):
        print("No se pudo generar el archivo de audio.")
        return

    # Parsear la letra LRC
    lineas_parsed = []
    for linea in letra_lrc.splitlines():
        if "]" in linea:
            try:
                tiempo_str, texto = linea.split("]", 1)
                tiempo_str = tiempo_str.replace("[", "")
                partes = tiempo_str.split(":")
                minutos = float(partes[0])
                segundos = float(partes[1])
                tiempo_total = minutos * 60 + segundos
                lineas_parsed.append((tiempo_total, texto.strip()))
            except:
                continue

    # Inicializar reproductor Pygame
    pygame.mixer.init()
    pygame.mixer.music.load(archivo_audio)
    pygame.mixer.music.play()
    
    inicio_tiempo = time.time()
    indice_actual = 0

    limpiar_pantalla()
    print("=== REPRODUCIENDO KARAOKE ===")
    print("Presiona Ctrl+C para salir.\n")

    try:
        while pygame.mixer.music.get_busy():
            tiempo_actual = time.time() - inicio_tiempo
            
            if indice_actual < len(lineas_parsed) and tiempo_actual >= lineas_parsed[indice_actual][0]:
                print(f"♪ {lineas_parsed[indice_actual][1]}")
                indice_actual += 1
            
            time.sleep(0.1)
    except KeyboardInterrupt:
        pygame.mixer.music.stop()
    
    # Limpiar archivo temporal
    if os.path.exists(archivo_audio):
        os.remove(archivo_audio)
    print("\n¡Fin de la canción!")

if __name__ == "__main__":
    limpiar_pantalla()
    print("=== KARAOKE PORTÁTIL ===")
    tema = input("Escribe la canción y el artista: ")
    if tema.strip():
        reproducir_magia(tema)
    else:
        print("No ingresaste ninguna canción.")
        
