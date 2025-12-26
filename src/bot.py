from pyrogram import Client, filters
from PIL import Image
import numpy as np
from pydub import AudioSegment
from .claves import config as cg
import os

# variables globales
ultima_foto = None
ultimo_audio = None

# la clase del bot (clase principal)
class Lazarus:
    def __init__(self, api_id, api_hash, token, nombre="Lazarus"):
        self.api_id = api_id
        self.api_hash = api_hash
        self.token = token
        self.nombre = nombre
        
        # se conecta al bot
        self.bot = Client(
            name=self.nombre,
            api_id=self.api_id,
            api_hash=self.api_hash,
            bot_token=self.token,
        )
        
        self.comandos()
    
    # comandos del bot
    def comandos(self):
        
        # comando /start para cuando se inicia el bot
        @self.bot.on_message(filters.command('start'))
        def start(client, message):
            message.reply_text('Hola, me llamo Lazarus! Soy un bot capaz de convertir imagenes en audios (aunque se escuche todo raro) y audios en imagenes (aunque se vean como glich)')
            message.reply_text('para ver como funciono, mis limites y mis capacidades bien especificadas, usa el comando /info ') #mejorar estos mensajes
            
        # comando /info para ver informacion del bot
        @self.bot.on_message(filters.command('info'))
        def info_command(client, message):
            # pposible mejora de este texto
            message.reply_text("Hola, soy Lazarus.\n\n"
                "Fui creado para experimentar con la conexión entre el sonido y la imagen.\n\n"
                "Qué hago:\n"
                "Puedo transformar imágenes (.jpg) en audios (.mp3) (suenan extraños, pero cada uno guarda algo único de la imagen).\n"
                "También convierto audios (.mp3) en imágenes (a veces abstractas, a veces tipo glitch).\n\n"
                "Cómo usarme:\n"
                "Solo enviame una imagen o un audio y esperá mi respuesta.\n\n"
                "Aclaro que otros formatos aún no fueron testeados, así que lo mejor es usar .jpg (en su defecto png) y .mp3 por ahora.\n\n")
        
        #filtro para recibir las imagenes del usuario
        @self.bot.on_message(filters.photo)
        def recibir_imagen(client, message):
            global ultima_foto
            
            # ruta absoluta + ruta donde se guarda la ultima imagen
            self.imagen_path = cg.root_dir / 'archivos' / 'imagenes' / 'ultima_imagen.jpg'
            #descargo la imagen que paso el usuario
            ultima_foto = client.download_media(message, self.imagen_path)
            
            #mensajito
            message.reply_text('Imagen recibida, ahora te la transformo en audio :)') #mejorar mensaje
            
            # uso la clase con su metodo para transformar la imagen en audio
            Transformador().tranformacion_image2audio()
            
            #mando un mensaje
            message.reply_text('Tu imagen ya fue convertida a audio, esperame un momento que ya te la mando :)') #mejorar mensaje
            
            # ruta absoluta + ruta donde se guarda la imagen convertida en audio
            self.imagen_audio_path = cg.root_dir / 'archivos' / 'audios' / 'imagen_audio.mp3'
            
            #mando el audio
            client.send_audio(
                chat_id = message.chat.id,
                audio = self.imagen_audio_path,
                caption = 'tu imagen convertida a audio',
                title = 'imagen convertida en audio',
                performer = 'Lazarus',
            )
            
        @self.bot.on_message(filters.audio)
        async def recibir_audio(client, message):
            global ultimo_audio
            
            # ruta absoluta + ruta donde se guarda el ultimo audio
            self.audio_path = cg.root_dir / 'archivos' / 'audios' / 'ultimo_audio.mp3'
            #descargo el ultimo audio
            ultimo_audio = await client.download_media(message, self.audio_path)
            
            #mando un mensaje
            await message.reply_text('Audio recibido, ahora lo transformo en imagen :)') #mejorar mensaje
            
            #uso la clase con su metodo para transformar el audio en imagen
            Transformador().transformacion_audio2image()
            
            #mando otro mensaje
            await message.reply_text('Tu audio ya fue transformado en imagen, ahora te la muesto :)') #mejorar mensaje
            
            # ruta absoluta + ruta donde se guarda el audio transformado en imagen
            self.audio_imagen_path = cg.root_dir / 'archivos' / 'imagenes' / 'audio_imagen.jpg'
            
            #mando la imagen
            await client.send_photo(
                chat_id = message.chat.id,
                photo = self.audio_imagen_path,
                caption = 'Tu audio convertido en imagen'
                )
            
        @self.bot.on_message(filters.command('easteregg'))
        def easter_egg(client, message):
            message.reply_text('felicidades! encontraste mi easter egg en mi proyecto, espero no lo hayas descubierto revisando el code . _.')
            message.reply_text('como easter egg y dato curioso, este proyecto se inspira y lleva el nombre de un anime que se transmitia en la temporada de invierno y que obviamente me vi. mi reseña del anime, buena la historia, desarollo bien para ser que solo es una temporada de 12 eps pero el final....me esperaba algo mas emocionante (sin spoilers para el que lo quiera ver).')
            message.reply_text('gracias por usar Lazarus, con todo gusto\n\n              -Snex')
        
    def run(self):
        self.bot.run()

# clase quue se encarga de pasar los audios a imagenes y las imagenes a audios
class Transformador:
    def __init__(self):
        CreacionCarpetas()
    
    # metodo para transformar imagen en audio
    def tranformacion_image2audio(self):
        # ruta absoluta + ruta donde se guarda la ultima imagen
        self.image_path = cg.root_dir / 'archivos' / 'imagenes' / 'ultima_imagen.jpg'
        
        #abro la imagen y la paso en formato RGB
        photo = Image.open(self.image_path).convert('RGB')
        
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
        
        # ruta absoluta + ruta donde se guarda la imagen convertida en audio
        self.imagen_audio_path = cg.root_dir / 'archivos' / 'audios' / 'imagen_audio.mp3'
        #guardo el audio
        audio.export(self.imagen_audio_path, format='mp3')
    
    def transformacion_audio2image(self):
        # ruta absoluta + ruta donde se guarda el ultimo audio
        self.audio_path = cg.root_dir / 'archivos' / 'audios' / 'ultimo_audio.mp3'
        
        #marco el ultimo audio en una variable
        audio = AudioSegment.from_file(self.audio_path)
        
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
        # ruta absoluta + ruta donde se guarda el audio convertido en imagen
        self.audio_imagen_path = cg.root_dir / 'archivos' / 'imagenes' / 'audio_imagen.jpg'
        #guardo la imagen
        img.save(self.audio_imagen_path)

# clase para crear las carpetas necesarias
class CreacionCarpetas:
    def __init__(self):
        # las carpetas y las rutas
        self.base_dir = 'archivos'
        self.audios_dir = os.path.join(self.base_dir, 'audios')
        self.imagenes_dir = os.path.join(self.base_dir, 'imagenes')
        
        self.crear_carpetas()
    
    # metodo que crea las carpetas
    def crear_carpetas(self):
        os.makedirs(self.audios_dir, exist_ok=True)
        os.makedirs(self.imagenes_dir, exist_ok=True)