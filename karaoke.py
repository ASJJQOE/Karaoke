import os
import sys
import time
import urllib.request
import json
import syncedlyrics
import pygame

def limpiar_pantalla():
    os.system('cls' if os.name == 'nt' else 'clear')

def descargar_audio_directo(query):
    print("Buscando pista de audio...")
    url_api = f"https://pipedapi.kavin.rocks/search?q={urllib.parse.quote(query + ' karaoke')}&filter=videos"
    
    req = urllib.request.Request(
        url_api,
        headers={'User-Agent': 'Mozilla/5.0'}
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            if 'items' in data and len(data['items']) > 0:
                # Obtenemos el ID del video de Piped
                video_id = data['items'][0]['url'].split("v=")[1]
                
                # Consultamos los detalles del video en Piped para obtener el enlace de audio directo
                url_streams = f"https://pipedapi.kavin.rocks/streams/{video_id}"
                req_stream = urllib.request.Request(url_streams, headers={'User-Agent': 'Mozilla/5.0'})
                
                with urllib.request.urlopen(req_stream) as resp_stream:
                    stream_data = json.loads(resp_stream.read().decode())
                    audio_streams = [s for s in stream_data.get('audioStreams', []) if s.get('mimeType', '').startswith('audio/')]
                    
                    if audio_streams:
                        # Tomamos el primer stream de audio disponible
                        audio_url = audio_streams[0]['url']
                        print("Descargando audio...")
                        
                        # Descargar el archivo directamente sin yt-dlp
                        urllib.request.urlretrieve(audio_url, 'cancion_temp.mp3')
                        return True
    except Exception as e:
        print(f"Error al obtener el audio: {e}")
    
    return False

def reproducir_magia(cancion):
    print("\nBuscando letras sincronizadas...")
    letra_lrc = syncedlyrics.search(cancion)
    
    if not letra_lrc:
        print("No se encontraron letras sincronizadas, pero intentaremos reproducir la música.")
        letra_lrc = "[0] ♪ (Sin letra sincronizada disponible) ♪"

    if not descargar_audio_directo(cancion):
        print("No se pudo descargar el audio de la canción.")
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
        
