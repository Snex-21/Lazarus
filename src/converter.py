import struct
import math
from pathlib import Path
import numpy as np
from PIL import Image
from pydub import AudioSegment

# Identificadores 'mágicos' (4 bytes) para saber qué tipo de archivo empaquetado es
MAGIC_IMG = b"LZIM"  # Imagen codificada dentro de un audio
MAGIC_AUD = b"LZAU"  # Audio codificado dentro de una imagen
MAGIC_HARMONIC_IMG = b"LZHM"  # Firma mágica para imagen armónica

DEFAULT_SAMPLE_RATE = 44100

# Escala musical pentatónica / Lydian / Acordes enriquecidos (Frecuencias en Hz)
PENTATONIC_FREQS = [
    130.81, 146.83, 164.81, 196.00, 220.00,  # C3, D3, E3, G3, A3
    261.63, 293.66, 329.63, 392.00, 440.00,  # C4, D4, E4, G4, A4
    523.25, 587.33, 659.25, 783.99, 880.00,  # C5, D5, E5, G5, A5
    1046.50, 1174.66, 1318.51, 1567.98       # C6, D6, E6, G6
]


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

    @staticmethod
    def _generate_ambient_harmonics(img_rgb: Image.Image, total_samples: int) -> np.ndarray:
        """Genera una pista musical armónica exuberante, cálida y extendida basada en la imagen."""
        arr = np.array(img_rgb)
        t = np.linspace(0, total_samples / DEFAULT_SAMPLE_RATE, total_samples, endpoint=False)
        
        avg_r = np.mean(arr[:, :, 0]) / 255.0
        root_idx = int(avg_r * 5) % len(PENTATONIC_FREQS)
        root_freq = PENTATONIC_FREQS[root_idx]
        third_freq = PENTATONIC_FREQS[(root_idx + 2) % len(PENTATONIC_FREQS)]
        fifth_freq = PENTATONIC_FREQS[(root_idx + 4) % len(PENTATONIC_FREQS)]
        seventh_freq = PENTATONIC_FREQS[(root_idx + 6) % len(PENTATONIC_FREQS)]

        vibrato = 1.0 + 0.003 * np.sin(2 * np.pi * 0.2 * t)
        lfo = 0.5 + 0.5 * np.sin(2 * np.pi * 0.1 * t)
        
        carrier = 0.35 * np.sin(2 * np.pi * root_freq * t * vibrato)
        carrier += 0.25 * np.sin(2 * np.pi * third_freq * t * vibrato + 0.6)
        carrier += 0.20 * np.sin(2 * np.pi * fifth_freq * t * vibrato + 1.2)
        carrier += 0.15 * np.sin(2 * np.pi * seventh_freq * t * vibrato + 1.8)
        carrier *= lfo

        step = max(1, total_samples // 32)
        for seg in range(0, total_samples, step):
            seg_end = min(total_samples, seg + step)
            seg_len = seg_end - seg
            decay = np.exp(-2.5 * np.linspace(0, 1, seg_len))
            freq_idx = (root_idx + (seg // step) * 3) % len(PENTATONIC_FREQS)
            arp_freq = PENTATONIC_FREQS[freq_idx]
            carrier[seg:seg_end] += 0.18 * np.sin(2 * np.pi * arp_freq * t[seg:seg_end]) * decay

        max_val = np.max(np.abs(carrier))
        if max_val > 0:
            carrier = carrier / max_val
            
        return (carrier * 24000).astype(np.int32)

    @classmethod
    def image_to_harmonic_audio(cls, image_path: str | Path, audio_output_path: str | Path) -> str:
        """Codifica una imagen en un audio WAV armónico musical sin perder reversibilidad (Lossless)."""
        image_path = Path(image_path)
        audio_output_path = Path(audio_output_path)

        with Image.open(image_path) as img:
            img_rgb = img.convert("RGB")
            width, height = img_rgb.size
            raw_pixels = img_rgb.tobytes()

        header = MAGIC_HARMONIC_IMG + struct.pack(">II", width, height)
        payload = header + raw_pixels

        total_bytes = len(payload)
        total_samples = total_bytes * 2  # Cada byte requiere 2 muestras (4 bits c/u en LSB)

        harmonics = cls._generate_ambient_harmonics(img_rgb, total_samples)

        payload_arr = np.frombuffer(payload, dtype=np.uint8)
        nibbles_high = (payload_arr >> 4) & 0x0F
        nibbles_low = payload_arr & 0x0F
        
        nibbles = np.empty(total_samples, dtype=np.uint8)
        nibbles[0::2] = nibbles_high
        nibbles[1::2] = nibbles_low

        carrier_masked = harmonics & ~0x0F
        samples_pcm = (carrier_masked | nibbles).astype(np.int16)

        audio = AudioSegment(
            samples_pcm.tobytes(),
            sample_width=2,
            frame_rate=DEFAULT_SAMPLE_RATE,
            channels=1
        )
        audio.export(str(audio_output_path), format="wav")
        return str(audio_output_path)

    @staticmethod
    def harmonic_audio_to_image_recovery(audio_path: str | Path, image_output_path: str | Path) -> bool:
        """Recupera la imagen idéntica bit a bit desde el audio armónico."""
        audio_path = Path(audio_path)
        image_output_path = Path(image_output_path)

        audio = AudioSegment.from_file(str(audio_path))
        samples = np.frombuffer(audio.raw_data, dtype=np.int16)

        if len(samples) < 24:
            return False

        temp_nibbles = (samples[:24] & 0x0F).astype(np.uint8)
        high_n = temp_nibbles[0::2] << 4
        low_n = temp_nibbles[1::2]
        temp_payload = (high_n | low_n).tobytes()

        if len(temp_payload) < 12 or not temp_payload.startswith(MAGIC_HARMONIC_IMG):
            return False

        _, width, height = struct.unpack(">4sII", temp_payload[:12])
        expected_pixel_bytes = width * height * 3
        total_payload_bytes = 12 + expected_pixel_bytes
        total_payload_samples = total_payload_bytes * 2

        if len(samples) < total_payload_samples:
            return False

        nibbles = (samples[:total_payload_samples] & 0x0F).astype(np.uint8)
        high_nibbles = nibbles[0::2] << 4
        low_nibbles = nibbles[1::2]
        payload = (high_nibbles | low_nibbles).tobytes()

        _, width, height = struct.unpack(">4sII", payload[:12])
        pixel_data = payload[12 : 12 + expected_pixel_bytes]

        if len(pixel_data) < expected_pixel_bytes:
            return False

        img = Image.frombytes("RGB", (width, height), pixel_data)
        img.save(str(image_output_path), format="PNG")
        return True

    @staticmethod
    def is_encoded_as_harmonic_audio(file_path: str | Path) -> bool:
        """Comprueba si un archivo de audio contiene una imagen armónica Lazarus empaquetada."""
        try:
            audio = AudioSegment.from_file(str(file_path))
            samples = np.frombuffer(audio.raw_data, dtype=np.int16)
            if len(samples) < 24:
                return False
            temp_nibbles = (samples[:24] & 0x0F).astype(np.uint8)
            high_n = temp_nibbles[0::2] << 4
            low_n = temp_nibbles[1::2]
            temp_payload = (high_n | low_n).tobytes()
            return temp_payload.startswith(MAGIC_HARMONIC_IMG)
        except Exception:
            return False
