from pyrogram import Client, filters
from pyrogram.types import Message
from flask import Flask, request
import os
import requests
import main 

#se crea la coneccion al bot
bot = Client('Lazarus!',
    api_id=main.api_id,
    api_hash=main.api_hash,
    bot_token = main.token,
)

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return 'bot funcionando', 200

#comando para iniciar /start
@bot.on_message(filters.command('start'))
def start_command(client, message ):
    message.reply_text('Hola, me llamo Lazarus! Soy un bot capaz de convertir imagenes en audios (aunque se escuche todo raro) y audios en imagenes (aunque se vean como glich)')
    message.reply_text('para ver como funciono, mis limites y mis capacidades bien especificadas, usa el comando /info ')
    

ultima_foto = None
#funcion para filtrar la ultima imagen
@bot.on_message(filters.photo)
def recibir_imagen(client, message):
    global ultima_foto
    #descargo la imagen que paso el usuario
    base_dir = os.getcwd()
    imagen_path = os.path.join(base_dir, 'archivos', 'imagenes', 'ultima_imagen.jpg')
    ultima_foto = client.download_media(message, imagen_path)
    #mensajito
    message.reply_text('Imagen recibida, ahora te la transformo en audio :)')

    #importo y  uso la funcion transformacion_image2audio() que hace eso, transforma la imagen en audio
    main.tranformacion_image2audio()
    
    #mando un mensaje
    message.reply_text('Tu imagen ya fue convertida a audio, esperame un momento que ya te la mando :)')
    
    #mando el audio
    imagen_audio_path = os.path.join(base_dir, 'archivos', 'audios', 'imagen_audio.mp3')
    client.send_audio(
        chat_id = message.chat.id,
        audio = imagen_audio_path,
        caption = 'tu imagen convertida a audio',
        title = 'imagen convertida en audio',
        performer = 'Lazarus',
    )


ultimo_audio = None
#funcion para filtrar el ultimo audio
@bot.on_message(filters.audio)
async def recibir_audio(client, message):
    global ultimo_audio
    
    #descargo el ultimo audio
    base_dir = os.getcwd()
    audio_path = os.path.join(base_dir, 'archivos', 'audios', 'ultimo_audio.mp3')
    ultimo_audio = await client.download_media(message, audio_path)
    
    #mando un mensaje
    await message.reply_text('Audio recibido, ahora lo transformo en imagen :)')
    
    #importo y uso la funcion transformacio_audio2image() para transformar el audio en imagen
    main.transformacion_audio2image()
    
    #mando otro mensaje
    await message.reply_text('Tu audio ya fue transformado en imagen, ahora te la muesto :)')
    #mando la imagen
    audio_imagen_path = os.path.join(base_dir, 'archivos', 'imagenes', 'audio_imagen.jpg')
    await client.send_photo(
        chat_id = message.chat.id,
        photo = audio_imagen_path,
        caption = 'Tu audio convertido en imagen'
        )

@bot.on_message(filters.command('info'))
def info_command(client, message):
    message.reply_text("Hola, soy Lazarus.\n\n"
        "Fui creado para experimentar con la conexión entre el sonido y la imagen.\n\n"
        "Qué hago:\n"
        "Puedo transformar imágenes (.jpg) en audios (.mp3) (suenan extraños, pero cada uno guarda algo único de la imagen).\n"
        "También convierto audios (.mp3) en imágenes (a veces abstractas, a veces tipo glitch).\n\n"
        "Cómo usarme:\n"
        "Solo enviame una imagen o un audio y esperá mi respuesta.\n\n"
        "Aclaro que otros formatos aún no fueron testeados, así que lo mejor es usar .jpg (en su defecto png) y .mp3 por ahora.\n\n")


@bot.on_message(filters.command('easteregg'))
def easter_egg(client, message):
    message.reply_text('felicidades! encontraste mi easter egg en mi proyecto, espero no lo hayas descubierto revisando el code . _.')
    message.reply_text('como easter egg y dato curioso, este proyecto se inspira y lleva el nombre de un anime que se transmitia en la temporada de invierno y que obviamente me vi. mi reseña del anime, buena la historia, desarollo bien para ser que solo es una temporada de 12 eps pero el final....me esperaba algo mas emocionante (sin spoilers para el que lo quiera ver).')
    message.reply_text('gracias por usar Lazarus, con todo gusto\n\n              -Snex')

#corro el bot
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    
    from threading import Thread
    def run_flask():
        app.run(host='0.0.0.0', port=port)
    
    Thread(target=run_flask).start()
    
    bot.run()