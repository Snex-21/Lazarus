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

# webhook_path = '/webhook'
# app_url = os.environ.get('APP_URL', 'https://pendiente-poner-la-url.onrender.com')
# webhook_url = app_url + webhook_path

# r = requests.get(f'https://api.telegram.org/bot{main.token}/setWebhook?url={webhook_url}')


app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return 'bot funcionando', 200

# @app.route(webhook_path, methods=['POST'])
# def webhook():
#     update = request.get_json()
#     bot.process_update(update)
#     return 'ok', 200

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
    ultima_foto = client.download_media(message,'c:/Users/Usuario/Desktop/lazarus/archivos/imagenes/ultima_imagen.jpg')
    #mensajito
    message.reply_text('Imagen recibida, ahora te la transformo en audio :)')

    #importo y  uso la funcion transformacion_image2audio() que hace eso, transforma la imagen en audio
    main.tranformacion_image2audio()
    
    #mando un mensaje
    message.reply_text('Tu imagen ya fue convertida a audio, esperame un momento que ya te la mando :)')
    
    #mando el audio
    client.send_audio(
        chat_id = message.chat.id,
        audio = 'c:/Users/Usuario/Desktop/lazarus/archivos/audios/imagen_audio.mp3',
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
    ultimo_audio = await client.download_media(message,'c:/Users/Usuario/Desktop/lazarus/archivos/audios/ultimo_audio.mp3')
    
    #mando un mensaje
    await message.reply_text('Audio recibido, ahora lo transformo en imagen :)')
    
    #importo y uso la funcion transformacio_audio2image() para transformar el audio en imagen
    main.transformacion_audio2image()
    
    #mando otro mensaje
    await message.reply_text('Tu audio ya fue transformado en imagen, ahora te la muesto :)')
    #mando la imagen
    await client.send_photo(
        chat_id = message.chat.id,
        photo = 'c:/Users/Usuario/Desktop/lazarus/archivos/imagenes/audio_imagen.png',
        caption = 'Tu audio convertido en imagen'
        )

@bot.on_message(filters.command('info'))
def info_command(client, message):
    message.reply_text('algo')
    # METER OTRO MENSAJE QUE RECOMIENDE USAR UN COMANDO QUE EXPLICA COMO FUNCIONA EL BOT, ESPECIFICACIONES, LIMITES, INSTRUCCIONES, ETC

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