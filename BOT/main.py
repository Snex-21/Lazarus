from PIL import Image
import numpy as np
from pydub import AudioSegment
import os
from dotenv import load_dotenv

load_dotenv()

api_id = int(os.getenv('api_id'))
api_hash = os.getenv('api_hash')
token = os.getenv('token_bot')

def tranformacion_image2audio():
    #busco la ruta absoluta del directorio y despues la convino con las rutas de las subcarpetas
    base_dir = os.getcwd()
    imagen_path = os.path.join(base_dir, 'archivos', 'imagenes', 'ultima_imagen.jpg')
    
    #abro la imagen y la paso en formato RGB
    photo = Image.open(imagen_path).convert('RGB')
    
    #convierto la imagen en un array
    array = np.array(photo)
    
    #divido las partes del array para cada color
    R = array[:, :, 0].flatten() #flatten() pasa la matriz d2 a un vector 1d
    G = array[:, :, 1].flatten()
    B = array[:, :, 2].flatten()

    #escalo los valores para simular ondas de radio
    R = np.interp(R, (0, 255), (-32768, 32767)). astype(np.int16) ##interp()=reescala los valores de un rango a otro
        #pixeles de 0 a 255 son para valores de audio
    G = np.interp(G, (0, 255), (-32768, 32767)). astype(np.int16)
                                #-32768, 32767 son los limites del tipo de dato in16 para el formato de audio PCM (es el tipico)(16 bits por muestra)
    B = np.interp(B, (0, 255), (-10000, 10000)). astype(np.int16)
                                #el rango es menos para que no interfiera con los sonidos principales (cada uno de los valores anteriores va para un canal de la bocina)

    #sumo el canal B a los canales R y G para tener solo dos canalaes
    R_mod = np.clip(R + B,-32768, 32767) #canal izquirdo
            # clip() se asegura que los valores no superen los limites
    G_mod = np.clip(G + B,-32768, 32767) #canal derecho

    #uno los dos canales, internamente es una array tipo en columna de dos de ancho
    stereo = np.column_stack((R_mod, G_mod)).flatten() #flatten() lo convierte en una lista larga a modo de secuencia de muestras
    
    #creo el audio 
    audio = AudioSegment(
    stereo.tobytes(), #secuencia de bytes crudos (PCM)
    frame_rate = 44100, #numero de muestras por segundo (calidad CD)
    sample_width = 2, #cada muestra ocupa 2bytes int16 = 16bits
    channels = 1 #mono, un solo canal. si se pusieran dos se usarion los canales por separado (R y G) (PROBAR EN UN FUTURO)
    )
    
    #rutas de las subcarpetas
    imagen_audio_path = os.path.join(base_dir, 'archivos', 'audios', 'imagen_audio.mp3')
    #guardo el audio
    audio.export(imagen_audio_path, format='mp3')


def transformacion_audio2image():
    #busco la ruta absoluta del directorio y despues la convino con las rutas de las subcarpetas
    base_dir = os.getcwd()
    audio_path = os.path.join(base_dir, 'archivos', 'audios', 'ultimo_audio.mp3')
    
    #marco el ultimo audio en una variable
    audio = AudioSegment.from_file(audio_path)
    
    #transformo los samples del audio en un array
    samples = np.array(audio.get_array_of_samples())
    
    #si el audio tiene dos canales (es estero) los divide. detecta si es estero y lo pasa a mono, basicamente agarra cada segunda muestra del audio para quedarse con un solo canal (PROXIMAMENTE PROBAR CON DOS CANALES)
    if audio.channels == 2:
        samples = samples[::2]

    #esta funcion va poniendo los valores de arr linealmente desde su minimo hasta su maximo (PROXIMAMENTE PROBAR CON uint16 o uno mas grande)
    def normalize(arr):
        return np.interp(arr, (arr.min(), arr.max()), (0, 255)).astype(np.uint8)

    #creo 3 canales con los submuestreos y despues aplico escalas de desplazamiento antes de normalizar a 0-255 para introducir diferencias entre R, G y B
    samples_r = normalize(samples[::3] * 0.5 + 100)
    samples_g = normalize(samples[100::3] * -1)
    samples_b = normalize(samples[200::3] * 2)

    #me aseguro que los tres canales tengan la misma longitud (EXPERIMENTAR CON LA IDEA DE QUE TENGAN DISTINTAS LONGITUDES)
    min_len = min(len(samples_r), len(samples_g), len(samples_b))
    samples_r, samples_g, samples_b = samples_r[:min_len], samples_g[:min_len], samples_b[:min_len]

    #hago que la imagen sea cuadrada (PROBAR CON IMAGENES NO CUADRADAS)
    lado = int(np.sqrt(min_len))
    #recorto sobrantes para que sea lado por lado
    samples_r = samples_r[:lado*lado].reshape((lado, lado))
    samples_g = samples_g[:lado*lado].reshape((lado, lado))
    samples_b = samples_b[:lado*lado].reshape((lado, lado))
    
    #creo un array para la imagen RGB
    img_array = np.stack([samples_r, samples_g, samples_b], axis=-1)

    img = Image.fromarray(img_array.astype(np.uint8))
    #rutas de las subcarpetas
    audio_imagen_path = os.path.join(base_dir, 'archivos', 'imagenes', 'audio_imagen.jpg')
    #guardo la imagen
    img.save(audio_imagen_path)