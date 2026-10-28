MESSAGES = {
    "es": {
        "start": (
            "Hola, soy Lazarus.\n\n"
            "Transformo imagenes en secuencias de audio y audios en estructuras visuales.\n"
            "El proceso cuenta con recuperacion bidireccional: reenvia cualquier archivo generado para restaurar su estado original.\n\n"
            "Consulta /info para conocer los detalles tecnicos y modo de operacion."
        ),
        "info": (
            "Lazarus - Especificación y uso:\n\n"
            "1. Operación:\n"
            "- Envia una imagen para generar un audio WAV (Distorsionado o Armónico) con su informacion de pixeles.\n"
            "- Envia un audio para generar una imagen PNG estructurada a partir de sus muestras PCM.\n"
            "- Reenvia un archivo generado previamente para recuperar el original sin perdida.\n\n"
            "2. Formatos recomendados:\n"
            "- Imagenes: PNG, JPG.\n"
            "- Audios: WAV, MP3.\n\n"
            "Nota: Para preservar la integridad de datos en la recuperacion, las imagenes generadas se transmiten como archivo."
        ),
        "image_seq_detected": "Secuencia de audio detectada en imagen. Recuperando archivo original...",
        "audio_recovered_caption": "Audio original recuperado.",
        "audio_recovered_title": "Audio Recuperado",
        "audio_recovery_error": "Error: No fue posible reconstruir el audio desde los datos provistos.",
        "btn_distorted": "Distorsionado (Raw PCM)",
        "btn_harmonic": "Armónico (Musical)",
        "ask_audio_mode": "¿Qué modalidad de audio deseas generar?",
        "file_not_available": "El archivo original ya no está disponible. Por favor, envía la imagen de nuevo.",
        "processing_distorted": "Procesando conversión a Audio Distorsionado (PCM Raw)...",
        "caption_distorted": "Conversión a Audio Distorsionado completada (WAV).\nReenvía este audio para recuperar la imagen original.",
        "title_distorted": "Audio Distorsionado",
        "processing_harmonic": "Procesando conversión a Audio Armónico (Musical)...",
        "caption_harmonic": "Conversión a Audio Armónico completada (WAV).\nReenvía este audio para recuperar la imagen original.",
        "title_harmonic": "Audio Armónico",
        "error_conversion": "Error durante la conversión: {error}",
        "error_processing": "Error durante el procesamiento: {error}",
        "audio_detected_recovery": "Audio detectado. Recuperando imagen original...",
        "image_recovered_caption": "Imagen original recuperada.",
        "image_recovery_error": "Error: No fue posible reconstruir la imagen desde el audio.",
        "audio_received_processing": "Audio recibido. Procesando conversion a imagen...",
        "image_converted_caption": "Conversión completada (PNG). Reenvia como archivo para recuperar el audio original.",
        "easteregg_1": "felicidades! encontraste mi easter egg en mi proyecto, espero no lo hayas descubierto revisando el code . _.",
        "easteregg_2": (
            "Como easter egg y dato curioso, este proyecto se inspira y lleva el nombre de un anime que se transmitia en la temporada de invierno "
            "y que obviamente me ví. Mi reseña del anime, buena la historia, desarollo bien para ser que solo es una temporada de 12 eps pero el final....me esperaba algo más emocionante (sin spoilers para el que lo quiera ver)."
        ),
        "easteregg_3": "gracias por usar Lazarus, con todo gusto\n\n              -Snex"
    },
    "en": {
        "start": (
            "Hello, I am Lazarus.\n\n"
            "I transform images into audio sequences and audios into visual structures.\n"
            "The process features bidirectional recovery: forward any generated file to restore its original state.\n\n"
            "Check /info to learn the technical details and operation mode."
        ),
        "info": (
            "Lazarus - Specification and usage:\n\n"
            "1. Operation:\n"
            "- Send an image to generate a WAV audio (Distorted or Harmonic) with its pixel information.\n"
            "- Send an audio to generate a structured PNG image from its PCM samples.\n"
            "- Forward a previously generated file to recover the original without loss.\n\n"
            "2. Recommended formats:\n"
            "- Images: PNG, JPG.\n"
            "- Audios: WAV, MP3.\n\n"
            "Note: To preserve data integrity during recovery, generated images are transmitted as a file/document."
        ),
        "image_seq_detected": "Audio sequence detected in image. Recovering original file...",
        "audio_recovered_caption": "Original audio recovered.",
        "audio_recovered_title": "Recovered Audio",
        "audio_recovery_error": "Error: Could not reconstruct audio from the provided data.",
        "btn_distorted": "Distorted (Raw PCM)",
        "btn_harmonic": "Harmonic (Musical)",
        "ask_audio_mode": "Which audio mode would you like to generate?",
        "file_not_available": "The original file is no longer available. Please send the image again.",
        "processing_distorted": "Processing conversion to Distorted Audio (Raw PCM)...",
        "caption_distorted": "Conversion to Distorted Audio completed (WAV).\nForward this audio to recover the original image.",
        "title_distorted": "Distorted Audio",
        "processing_harmonic": "Processing conversion to Harmonic Audio (Musical)...",
        "caption_harmonic": "Conversion to Harmonic Audio completed (WAV).\nForward this audio to recover the original image.",
        "title_harmonic": "Harmonic Audio",
        "error_conversion": "Error during conversion: {error}",
        "error_processing": "Error during processing: {error}",
        "audio_detected_recovery": "Audio detected. Recovering original image...",
        "image_recovered_caption": "Original image recovered.",
        "image_recovery_error": "Error: Could not reconstruct image from audio.",
        "audio_received_processing": "Audio received. Processing conversion to image...",
        "image_converted_caption": "Conversion completed (PNG). Forward as a file to recover original audio.",
        "easteregg_1": "congratulations! you found my project's easter egg, I hope you didn't find it by checking the code . _.",
        "easteregg_2": (
            "as an easter egg and fun fact, this project is inspired by and named after an anime that aired in the winter season "
            "which obviously I watched. my review of the anime: good story, developed well considering it's only a 12-episode season, but the ending....I expected something more exciting (no spoilers for anyone who wants to watch it)."
        ),
        "easteregg_3": "thank you for using Lazarus, with pleasure\n\n              -Snex"
    }
}


def get_user_lang(user) -> str:
    """
    Detecta el idioma del usuario basándose en su configuración de Telegram.
    - Si el usuario tiene Telegram en español ('es', 'es-ES', 'es-419', etc.), retorna 'es'.
    - Si tiene cualquier otro idioma (inglés, portugués, francés, etc.) o no está especificado, retorna 'en'.
    """
    if user and getattr(user, "language_code", None):
        code = user.language_code.lower()
        if code.startswith("es"):
            return "es"
    return "en"


def get_text(key: str, lang: str = "es", **kwargs) -> str:
    """
    Obtiene el mensaje localizado para la clave dada.
    Si la clave no está en el idioma seleccionado, recurre al inglés ('en').
    """
    lang_dict = MESSAGES.get(lang, MESSAGES["en"])
    text = lang_dict.get(key, MESSAGES["en"].get(key, key))
    if kwargs:
        return text.format(**kwargs)
    return text
