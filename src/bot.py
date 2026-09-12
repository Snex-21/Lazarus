import os
import uuid
from pathlib import Path
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from .claves import config as cg
from .converter import ReversibleConverter


# la clase del bot (clase principal)
class Lazarus:
    def __init__(self, api_id, api_hash, token, nombre="Lazarus"):
        self.api_id = api_id
        self.api_hash = api_hash
        self.token = token
        self.nombre = nombre
        
        # se asegura de que existan las carpetas necesarias
        CreacionCarpetas()
        
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
        async def start(client, message):
            await message.reply_text(
                'Hola, soy Lazarus.\n\n'
                'Transformo imagenes en secuencias de audio y audios en estructuras visuales.\n'
                'El proceso cuenta con recuperacion bidireccional: reenvia cualquier archivo generado para restaurar su estado original.\n\n'
                'Consulta /info para conocer los detalles tecnicos y modo de operacion.'
            )
            
        # comando /info para ver informacion del bot
        @self.bot.on_message(filters.command('info'))
        async def info_command(client, message):
            await message.reply_text(
                "Lazarus - Especificacion y uso:\n\n"
                "1. Operacion:\n"
                "- Envia una imagen para generar un audio WAV (Distorsionado o Armónico) con su informacion de pixeles.\n"
                "- Envia un audio para generar una imagen PNG estructurada a partir de sus muestras PCM.\n"
                "- Reenvia un archivo generado previamente para recuperar el original sin perdida.\n\n"
                "2. Formatos recomendados:\n"
                "- Imagenes: PNG, JPG.\n"
                "- Audios: WAV, MP3.\n\n"
                "Nota: Para preservar la integridad de datos en la recuperacion, las imagenes generadas se transmiten como archivo."
            )
        
        # filtro para recibir imágenes (como foto o como documento de imagen)
        @self.bot.on_message(filters.photo | (filters.document & filters.create(lambda _, __, m: bool(m.document and m.document.mime_type and m.document.mime_type.startswith('image/')))))
        async def recibir_imagen(client, message):
            file_id = uuid.uuid4().hex
            input_path = cg.root_dir / 'archivos' / 'imagenes' / f'{file_id}_in.png'
            output_audio = cg.root_dir / 'archivos' / 'audios' / f'{file_id}_out.wav'
            
            try:
                await client.download_media(message, str(input_path))
                
                # Comprobar si es una imagen que ya contiene un audio Lazarus empaquetado (recuperación)
                if ReversibleConverter.is_encoded_as_image(input_path):
                    await message.reply_text('Secuencia de audio detectada en imagen. Recuperando archivo original...')
                    recuperado = ReversibleConverter.image_to_audio_recovery(input_path, output_audio)
                    if recuperado:
                        await client.send_audio(
                            chat_id=message.chat.id,
                            audio=str(output_audio),
                            caption='Audio original recuperado.',
                            title='Audio Recuperado',
                            performer='Lazarus',
                        )
                    else:
                        await message.reply_text('Error: No fue posible reconstruir el audio desde los datos provistos.')
                    if input_path.exists():
                        input_path.unlink()
                    if output_audio.exists():
                        output_audio.unlink()
                else:
                    # Es una imagen nueva -> ofrecer selección mediante Inline Keyboard
                    keyboard = InlineKeyboardMarkup([
                        [
                            InlineKeyboardButton("Distorsionado (Raw PCM)", callback_data=f"mode_distorted:{file_id}"),
                            InlineKeyboardButton("Armónico (Musical)", callback_data=f"mode_harmonic:{file_id}")
                        ]
                    ])
                    await message.reply_text(
                        "¿Qué modalidad de audio deseas generar?",
                        reply_markup=keyboard
                    )
            except Exception as e:
                await message.reply_text(f'Error durante el procesamiento: {e}')
                if input_path.exists():
                    input_path.unlink()
                if output_audio.exists():
                    output_audio.unlink()

        # callback handler para la selección de tipo de audio
        @self.bot.on_callback_query(filters.regex(r"^mode_(distorted|harmonic):(.+)$"))
        async def procesar_opcion_audio(client, callback_query):
            mode, file_id = callback_query.data.split(":", 1)
            mode_type = mode.replace("mode_", "")
            
            input_path = cg.root_dir / 'archivos' / 'imagenes' / f'{file_id}_in.png'
            output_audio = cg.root_dir / 'archivos' / 'audios' / f'{file_id}_out.wav'
            
            if not input_path.exists():
                await callback_query.answer("El archivo original ya no está disponible. Por favor, envía la imagen de nuevo.", show_alert=True)
                return
                
            await callback_query.answer()
            
            try:
                if mode_type == "distorted":
                    await callback_query.edit_message_text("Procesando conversión a Audio Distorsionado (PCM Raw)...")
                    ReversibleConverter.image_to_audio(input_path, output_audio)
                    caption_text = "Conversión a Audio Distorsionado completada (WAV).\nReenvía este audio para recuperar la imagen original."
                    title_text = "Audio Distorsionado"
                else:
                    await callback_query.edit_message_text("Procesando conversión a Audio Armónico (Musical)...")
                    ReversibleConverter.image_to_harmonic_audio(input_path, output_audio)
                    caption_text = "Conversión a Audio Armónico completada (WAV).\nReenvía este audio para recuperar la imagen original."
                    title_text = "Audio Armónico"
                    
                await client.send_audio(
                    chat_id=callback_query.message.chat.id,
                    audio=str(output_audio),
                    caption=caption_text,
                    title=title_text,
                    performer="Lazarus",
                )
                try:
                    await callback_query.message.delete()
                except Exception:
                    pass
            except Exception as e:
                await callback_query.edit_message_text(f"Error durante la conversión: {e}")
            finally:
                if input_path.exists():
                    input_path.unlink()
                if output_audio.exists():
                    output_audio.unlink()
            
        # filtro para recibir audios o documentos de audio
        @self.bot.on_message(filters.audio | filters.voice | (filters.document & filters.create(lambda _, __, m: bool(m.document and m.document.mime_type and m.document.mime_type.startswith('audio/')))))
        async def recibir_audio(client, message):
            file_id = uuid.uuid4().hex
            input_path = cg.root_dir / 'archivos' / 'audios' / f'{file_id}_in.wav'
            output_image = cg.root_dir / 'archivos' / 'imagenes' / f'{file_id}_out.png'
            
            try:
                await client.download_media(message, str(input_path))
                
                # Comprobar primero si es un audio armónico Lazarus
                if ReversibleConverter.is_encoded_as_harmonic_audio(input_path):
                    await message.reply_text('Audio detectado. Recuperando imagen original...')
                    recuperado = ReversibleConverter.harmonic_audio_to_image_recovery(input_path, output_image)
                    if recuperado:
                        await client.send_document(
                            chat_id=message.chat.id,
                            document=str(output_image),
                            caption='Imagen original recuperada.'
                        )
                    else:
                        await message.reply_text('Error: No fue posible reconstruir la imagen desde el audio.')
                # Comprobar si es un audio estándar Lazarus (recuperación)
                elif ReversibleConverter.is_encoded_as_audio(input_path):
                    await message.reply_text('Audio detectado. Recuperando imagen original...')
                    recuperado = ReversibleConverter.audio_to_image_recovery(input_path, output_image)
                    if recuperado:
                        await client.send_document(
                            chat_id=message.chat.id,
                            document=str(output_image),
                            caption='Imagen original recuperada.'
                        )
                    else:
                        await message.reply_text('Error: No fue posible reconstruir la imagen desde el audio.')
                else:
                    # Es un audio nuevo -> convertir a imagen
                    await message.reply_text('Audio recibido. Procesando conversion a imagen...')
                    ReversibleConverter.audio_to_image(input_path, output_image)
                    await client.send_document(
                        chat_id=message.chat.id,
                        document=str(output_image),
                        caption='Conversion completada (PNG). Reenvia como archivo para recuperar el audio original.'
                    )
            except Exception as e:
                await message.reply_text(f'Error durante el procesamiento: {e}')
            finally:
                if input_path.exists():
                    input_path.unlink()
                if output_image.exists():
                    output_image.unlink()
            
        @self.bot.on_message(filters.command('easteregg'))
        async def easter_egg(client, message):
            await message.reply_text('felicidades! encontraste mi easter egg en mi proyecto, espero no lo hayas descubierto revisando el code . _.')
            await message.reply_text('como easter egg y dato curioso, este proyecto se inspira y lleva el nombre de un anime que se transmitia en la temporada de invierno y que obviamente me vi. mi reseña del anime, buena la historia, desarollo bien para ser que solo es una temporada de 12 eps pero el final....me esperaba algo mas emocionante (sin spoilers para el que lo quiera ver).')
            await message.reply_text('gracias por usar Lazarus, con todo gusto\n\n              -Snex')
        
    def run(self):
        self.bot.run()


# clase para crear las carpetas necesarias
class CreacionCarpetas:
    def __init__(self):
        # las carpetas y las rutas absolutas usando root_dir
        self.base_dir = cg.root_dir / 'archivos'
        self.audios_dir = self.base_dir / 'audios'
        self.imagenes_dir = self.base_dir / 'imagenes'
        
        self.crear_carpetas()
    
    # metodo que crea las carpetas
    def crear_carpetas(self):
        os.makedirs(self.audios_dir, exist_ok=True)
        os.makedirs(self.imagenes_dir, exist_ok=True)