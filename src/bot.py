import os
import uuid
from pathlib import Path
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from .claves import config as cg
from .converter import ReversibleConverter
from .bd import guardar_usuario
from .i18n import get_user_lang, get_text


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
        
        # registrar ID de usuario automáticamente en la BD
        @self.bot.on_message(group=-1)
        async def registrar_usuario(client, message):
            if message.from_user:
                guardar_usuario(message.from_user.id)

        @self.bot.on_callback_query(group=-1)
        async def registrar_usuario_callback(client, callback_query):
            if callback_query.from_user:
                guardar_usuario(callback_query.from_user.id)

        # comando /start para cuando se inicia el bot
        @self.bot.on_message(filters.command('start'))
        async def start(client, message):
            lang = get_user_lang(message.from_user)
            await message.reply_text(get_text("start", lang))
            
        # comando /info para ver informacion del bot
        @self.bot.on_message(filters.command('info'))
        async def info_command(client, message):
            lang = get_user_lang(message.from_user)
            await message.reply_text(get_text("info", lang))
        
        # filtro para recibir imágenes (como foto o como documento de imagen)
        @self.bot.on_message(filters.photo | (filters.document & filters.create(lambda _, __, m: bool(m.document and m.document.mime_type and m.document.mime_type.startswith('image/')))))
        async def recibir_imagen(client, message):
            lang = get_user_lang(message.from_user)
            file_id = uuid.uuid4().hex
            input_path = cg.root_dir / 'archivos' / 'imagenes' / f'{file_id}_in.png'
            output_audio = cg.root_dir / 'archivos' / 'audios' / f'{file_id}_out.wav'
            
            try:
                await client.download_media(message, str(input_path))
                
                # Comprobar si es una imagen que ya contiene un audio Lazarus empaquetado (recuperación)
                if ReversibleConverter.is_encoded_as_image(input_path):
                    await message.reply_text(get_text("image_seq_detected", lang))
                    recuperado = ReversibleConverter.image_to_audio_recovery(input_path, output_audio)
                    if recuperado:
                        await client.send_audio(
                            chat_id=message.chat.id,
                            audio=str(output_audio),
                            caption=get_text("audio_recovered_caption", lang),
                            title=get_text("audio_recovered_title", lang),
                            performer='Lazarus',
                        )
                    else:
                        await message.reply_text(get_text("audio_recovery_error", lang))
                    if input_path.exists():
                        input_path.unlink()
                    if output_audio.exists():
                        output_audio.unlink()
                else:
                    # Es una imagen nueva -> ofrecer selección mediante Inline Keyboard
                    keyboard = InlineKeyboardMarkup([
                        [
                            InlineKeyboardButton(get_text("btn_distorted", lang), callback_data=f"mode_distorted:{file_id}"),
                            InlineKeyboardButton(get_text("btn_harmonic", lang), callback_data=f"mode_harmonic:{file_id}")
                        ]
                    ])
                    await message.reply_text(
                        get_text("ask_audio_mode", lang),
                        reply_markup=keyboard
                    )
            except Exception as e:
                await message.reply_text(get_text("error_processing", lang, error=e))
                if input_path.exists():
                    input_path.unlink()
                if output_audio.exists():
                    output_audio.unlink()

        # callback handler para la selección de tipo de audio
        @self.bot.on_callback_query(filters.regex(r"^mode_(distorted|harmonic):(.+)$"))
        async def procesar_opcion_audio(client, callback_query):
            lang = get_user_lang(callback_query.from_user)
            mode, file_id = callback_query.data.split(":", 1)
            mode_type = mode.replace("mode_", "")
            
            input_path = cg.root_dir / 'archivos' / 'imagenes' / f'{file_id}_in.png'
            output_audio = cg.root_dir / 'archivos' / 'audios' / f'{file_id}_out.wav'
            
            if not input_path.exists():
                await callback_query.answer(get_text("file_not_available", lang), show_alert=True)
                return
                
            await callback_query.answer()
            
            try:
                if mode_type == "distorted":
                    await callback_query.edit_message_text(get_text("processing_distorted", lang))
                    ReversibleConverter.image_to_audio(input_path, output_audio)
                    caption_text = get_text("caption_distorted", lang)
                    title_text = get_text("title_distorted", lang)
                else:
                    await callback_query.edit_message_text(get_text("processing_harmonic", lang))
                    ReversibleConverter.image_to_harmonic_audio(input_path, output_audio)
                    caption_text = get_text("caption_harmonic", lang)
                    title_text = get_text("title_harmonic", lang)
                    
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
                await callback_query.edit_message_text(get_text("error_conversion", lang, error=e))
            finally:
                if input_path.exists():
                    input_path.unlink()
                if output_audio.exists():
                    output_audio.unlink()
            
        # filtro para recibir audios o documentos de audio
        @self.bot.on_message(filters.audio | filters.voice | (filters.document & filters.create(lambda _, __, m: bool(m.document and m.document.mime_type and m.document.mime_type.startswith('audio/')))))
        async def recibir_audio(client, message):
            lang = get_user_lang(message.from_user)
            file_id = uuid.uuid4().hex
            input_path = cg.root_dir / 'archivos' / 'audios' / f'{file_id}_in.wav'
            output_image = cg.root_dir / 'archivos' / 'imagenes' / f'{file_id}_out.png'
            
            try:
                await client.download_media(message, str(input_path))
                
                # Comprobar primero si es un audio armónico Lazarus
                if ReversibleConverter.is_encoded_as_harmonic_audio(input_path):
                    await message.reply_text(get_text("audio_detected_recovery", lang))
                    recuperado = ReversibleConverter.harmonic_audio_to_image_recovery(input_path, output_image)
                    if recuperado:
                        await client.send_document(
                            chat_id=message.chat.id,
                            document=str(output_image),
                            caption=get_text("image_recovered_caption", lang)
                        )
                    else:
                        await message.reply_text(get_text("image_recovery_error", lang))
                # Comprobar si es un audio estándar Lazarus (recuperación)
                elif ReversibleConverter.is_encoded_as_audio(input_path):
                    await message.reply_text(get_text("audio_detected_recovery", lang))
                    recuperado = ReversibleConverter.audio_to_image_recovery(input_path, output_image)
                    if recuperado:
                        await client.send_document(
                            chat_id=message.chat.id,
                            document=str(output_image),
                            caption=get_text("image_recovered_caption", lang)
                        )
                    else:
                        await message.reply_text(get_text("image_recovery_error", lang))
                else:
                    # Es un audio nuevo -> convertir a imagen
                    await message.reply_text(get_text("audio_received_processing", lang))
                    ReversibleConverter.audio_to_image(input_path, output_image)
                    await client.send_document(
                        chat_id=message.chat.id,
                        document=str(output_image),
                        caption=get_text("image_converted_caption", lang)
                    )
            except Exception as e:
                await message.reply_text(get_text("error_processing", lang, error=e))
            finally:
                if input_path.exists():
                    input_path.unlink()
                if output_image.exists():
                    output_image.unlink()
            
        @self.bot.on_message(filters.command('easteregg'))
        async def easter_egg(client, message):
            lang = get_user_lang(message.from_user)
            await message.reply_text(get_text("easteregg_1", lang))
            await message.reply_text(get_text("easteregg_2", lang))
            await message.reply_text(get_text("easteregg_3", lang))
        
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
