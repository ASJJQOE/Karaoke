import os
import sys
import time
import urllib.request
import json
import yt_dlp
import syncedlyrics
import pygame

def limpiar_pantalla():
    os.system('cls' if os.name == 'nt' else 'clear')

def buscar_audio_alternativo(query):
    """Busca el video usando la API pública de Piped para evitar el bloqueo de YouTube en la nube"""
    print("Buscando pista de audio alternativa...")
    url_api = f"https://pipedapi.kavin.rocks/search?q={urllib.parse.quote(query + ' karaoke')}&filter=videos"
    
    req = urllib.request.Request(
        url_api,
        headers={'User-Agent': 'Mozilla/5.0'}
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            if 'items' in data and len(data['items']) > 0:
                # Extrae el ID del video del primer resultado
                video_url = "https://www.youtube.com" + data['items'][0]['url']
                return video_url
    except Exception as e:
        print(f"Error en la búsqueda alternativa: {e}")
    
    return None

def reproducir_magia(cancion):
    print("\nBuscando letras sincronizadas...")
    letra_lrc = syncedlyrics.search(cancion)
    
    if not letra_lrc:
        print("No se encontraron letras sincronizadas, pero intentaremos reproducir la música.")
        letra_lrc = "[0] ♪ (Sin letra sincronizada disponible) ♪"

    # Obtener enlace mediante API pública en lugar de búsqueda directa bloqueada
    video_url = buscar_audio_alternativo(cancion)
    if not video_url:
        print("No se pudo encontrar un enlace de audio válido.")
        return

    print("Preparando el audio...")
    
    ydl_opts = {
        'format': 'bestaudio/best',
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
            ydl.download([video_url])
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
        
