import struct
import math
from pathlib import Path
from PIL import Image
from pydub import AudioSegment

# Identificadores 'mágicos' (4 bytes) para saber qué tipo de archivo empaquetado es
MAGIC_IMG = b"LZIM"  # Imagen codificada dentro de un audio
MAGIC_AUD = b"LZAU"  # Audio codificado dentro de una imagen

DEFAULT_SAMPLE_RATE = 44100


class ReversibleConverter:
    """
    Módulo de conversión bidireccional exacta (sin pérdida / lossless).
    
    1. Imagen -> Audio (WAV):
       Estructura del payload PCM:
       [MAGIC_IMG (4B)] + [Width (4B)] + [Height (4B)] + [Raw RGB Bytes] + [Padding opcional (1B)]
    
    2. Audio -> Imagen (PNG):
       Estructura del payload de píxeles:
       [MAGIC_AUD (4B)] + [FrameRate (4B)] + [SampleWidth (2B)] + [Channels (2B)] + [AudioBytesLen (4B)] + [Raw PCM Bytes] + [Padding RGB (0-2B)]
    """

    @staticmethod
    def image_to_audio(image_path: str | Path, audio_output_path: str | Path, sample_rate: int = DEFAULT_SAMPLE_RATE) -> str:
        """
        Convierte una imagen en un audio WAV reproducible que contiene todos sus píxeles y dimensiones.
        """
        image_path = Path(image_path)
        audio_output_path = Path(audio_output_path)

        with Image.open(image_path) as img:
            img_rgb = img.convert("RGB")
            width, height = img_rgb.size
            raw_pixels = img_rgb.tobytes()

        # Cabecera: MAGIC (4B) + Width (4B) + Height (4B)
        header = MAGIC_IMG + struct.pack(">II", width, height)
        payload = header + raw_pixels

        # PCM de 16-bit requiere un número par de bytes
        if len(payload) % 2 != 0:
            payload += b"\x00"

        audio = AudioSegment(
            data=payload,
            sample_width=2,  # 16-bit
            frame_rate=sample_rate,
            channels=1,  # Mono
        )
        audio.export(str(audio_output_path), format="wav")
        return str(audio_output_path)

    @staticmethod
    def audio_to_image_recovery(audio_path: str | Path, image_output_path: str | Path) -> bool:
        """
        Restaura la imagen original desde un audio generado con image_to_audio.
        Retorna True si fue exitoso, False si no contiene la firma mágica.
        """
        audio_path = Path(audio_path)
        image_output_path = Path(image_output_path)

        audio = AudioSegment.from_file(str(audio_path))
        raw_data = audio.raw_data

        if len(raw_data) < 12 or not raw_data.startswith(MAGIC_IMG):
            return False

        magic, width, height = struct.unpack(">4sII", raw_data[:12])
        expected_bytes = width * height * 3
        pixel_data = raw_data[12 : 12 + expected_bytes]

        if len(pixel_data) < expected_bytes:
            return False

        img = Image.frombytes("RGB", (width, height), pixel_data)
        img.save(str(image_output_path), format="PNG")
        return True

    @staticmethod
    def audio_to_image(audio_path: str | Path, image_output_path: str | Path) -> str:
        """
        Convierte un audio en una imagen PNG glitch visible que contiene los metadatos y muestras del audio.
        """
        audio_path = Path(audio_path)
        image_output_path = Path(image_output_path)

        audio = AudioSegment.from_file(str(audio_path))
        raw_audio_bytes = audio.raw_data

        # Cabecera: MAGIC (4B) + FrameRate (4B) + SampleWidth (2B) + Channels (2B) + TotalAudioBytes (4B) = 16 Bytes
        header = MAGIC_AUD + struct.pack(
            ">IHHI",
            audio.frame_rate,
            audio.sample_width,
            audio.channels,
            len(raw_audio_bytes),
        )
        payload = header + raw_audio_bytes

        # Cada píxel RGB son 3 bytes
        total_pixels = math.ceil(len(payload) / 3)
        # Rellenar con ceros hasta completar múltiplos de 3 bytes
        padding_needed = (total_pixels * 3) - len(payload)
        if padding_needed > 0:
            payload += b"\x00" * padding_needed

        # Dimensionar la imagen como un rectángulo lo más cercano posible a un cuadrado
        width = math.isqrt(total_pixels)
        if width == 0:
            width = 1
        height = math.ceil(total_pixels / width)

        # Ajustar payload al tamaño total width * height * 3
        full_image_size = width * height * 3
        if len(payload) < full_image_size:
            payload += b"\x00" * (full_image_size - len(payload))

        img = Image.frombytes("RGB", (width, height), payload)
        img.save(str(image_output_path), format="PNG")
        return str(image_output_path)

    @staticmethod
    def image_to_audio_recovery(image_path: str | Path, audio_output_path: str | Path) -> bool:
        """
        Restaura el audio original desde una imagen generada con audio_to_image.
        Retorna True si fue exitoso, False si no contiene la firma mágica.
        """
        image_path = Path(image_path)
        audio_output_path = Path(audio_output_path)

        with Image.open(image_path) as img:
            img_rgb = img.convert("RGB")
            raw_data = img_rgb.tobytes()

        if len(raw_data) < 16 or not raw_data.startswith(MAGIC_AUD):
            return False

        magic, frame_rate, sample_width, channels, audio_bytes_len = struct.unpack(
            ">4sIHHI", raw_data[:16]
        )

        audio_data = raw_data[16 : 16 + audio_bytes_len]
        if len(audio_data) < audio_bytes_len:
            return False

        recovered_audio = AudioSegment(
            data=audio_data,
            sample_width=sample_width,
            frame_rate=frame_rate,
            channels=channels,
        )
        recovered_audio.export(str(audio_output_path), format="wav")
        return True

    @staticmethod
    def is_encoded_as_audio(file_path: str | Path) -> bool:
        """Comprueba si un archivo de audio contiene una imagen Lazarus empaquetada."""
        try:
            audio = AudioSegment.from_file(str(file_path))
            return audio.raw_data.startswith(MAGIC_IMG)
        except Exception:
            return False

    @staticmethod
    def is_encoded_as_image(file_path: str | Path) -> bool:
        """Comprueba si un archivo de imagen contiene un audio Lazarus empaquetado."""
        try:
            with Image.open(file_path) as img:
                raw_data = img.convert("RGB").tobytes()
                return raw_data.startswith(MAGIC_AUD)
        except Exception:
            return False
