"""
Script de prueba para la conversión bidireccional exacta de Lazarus.

Prueba dos flujos completos:
1. Imagen -> Audio -> Recuperar Imagen (Comprobación bit a bit)
2. Audio -> Imagen -> Recuperar Audio (Comprobación PCM bit a bit)
"""

import sys
from pathlib import Path
from PIL import Image
import numpy as np
from pydub import AudioSegment
from pydub.generators import Sine

# Asegurar que podamos importar desde src
ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))

from src.converter import ReversibleConverter

TEMP_DIR = ROOT_DIR / "test_temp"


def setup():
    TEMP_DIR.mkdir(exist_ok=True)


def cleanup():
    if TEMP_DIR.exists():
        for file in TEMP_DIR.glob("*"):
            try:
                file.unlink()
            except Exception:
                pass
        try:
            TEMP_DIR.rmdir()
        except Exception:
            pass


def test_flujo_imagen_a_audio_y_recuperacion(custom_image_path: Path = None):
    print("\n" + "=" * 60)
    print("TEST 1: Imagen -> Audio (WAV) -> Recuperar Imagen")
    print("=" * 60)

    # 1. Obtener o generar imagen original
    if custom_image_path and custom_image_path.exists():
        print(f"[+] Usando imagen personalizada: {custom_image_path}")
        orig_img_path = custom_image_path
    else:
        print("[+] Generando imagen sintética de prueba (150x100 RGB)...")
        orig_img_path = TEMP_DIR / "original_image.png"
        arr = np.random.randint(0, 256, (100, 150, 3), dtype=np.uint8)
        img = Image.fromarray(arr)
        img.save(orig_img_path, format="PNG")

    audio_path = TEMP_DIR / "imagen_convertida_a_audio.wav"
    recov_img_path = TEMP_DIR / "imagen_recuperada.png"

    # 2. Convertir imagen a audio
    print("[1] Codificando imagen en audio WAV...")
    ReversibleConverter.image_to_audio(orig_img_path, audio_path)
    print(f"    -> Audio generado: {audio_path.name}")

    # 3. Detectar firma mágica
    is_lazarus = ReversibleConverter.is_encoded_as_audio(audio_path)
    print(f"    -> ¿Audio contiene firma de imagen Lazarus (LZIM)?: {is_lazarus}")
    assert is_lazarus, "Error: No se detectó la cabecera mágica LZIM en el audio"

    # 4. Recuperar imagen desde el audio
    print("[2] Recuperando imagen desde el audio...")
    recuperado_ok = ReversibleConverter.audio_to_image_recovery(audio_path, recov_img_path)
    assert recuperado_ok, "Error: Falló la recuperación de la imagen"
    print(f"    -> Imagen recuperada: {recov_img_path.name}")

    # 5. Comparación bit a bit
    with Image.open(orig_img_path) as i1, Image.open(recov_img_path) as i2:
        orig_bytes = i1.convert("RGB").tobytes()
        recov_bytes = i2.convert("RGB").tobytes()
        dimensiones_iguales = (i1.size == i2.size)
        bytes_iguales = (orig_bytes == recov_bytes)

    print("\n--- Resultados Test 1 ---")
    print(f"    Dimensiones coinciden: {dimensiones_iguales} ({i1.size} vs {i2.size})")
    print(f"    Píxeles 100% idénticos bit a bit: {bytes_iguales}")

    if dimensiones_iguales and bytes_iguales:
        print(">>> RESULTADO TEST 1: ¡ÉXITO TOTAL (Lossless)! <<<")
    else:
        print(">>> RESULTADO TEST 1: FALLO <<<")


def test_flujo_audio_a_imagen_y_recuperacion(custom_audio_path: Path = None):
    print("\n" + "=" * 60)
    print("TEST 2: Audio -> Imagen (PNG) -> Recuperar Audio")
    print("=" * 60)

    # 1. Obtener o generar audio original
    if custom_audio_path and custom_audio_path.exists():
        print(f"[+] Usando audio personalizado: {custom_audio_path}")
        orig_audio_path = custom_audio_path
    else:
        print("[+] Generando audio sintético de prueba (Tono 440Hz, 1.5s)...")
        orig_audio_path = TEMP_DIR / "original_audio.wav"
        tono = Sine(440).to_audio_segment(duration=1500)
        tono.export(str(orig_audio_path), format="wav")

    image_path = TEMP_DIR / "audio_convertido_a_imagen.png"
    recov_audio_path = TEMP_DIR / "audio_recuperado.wav"

    # 2. Convertir audio a imagen
    print("[1] Codificando audio en imagen PNG...")
    ReversibleConverter.audio_to_image(orig_audio_path, image_path)
    print(f"    -> Imagen generada: {image_path.name}")

    # 3. Detectar firma mágica
    is_lazarus = ReversibleConverter.is_encoded_as_image(image_path)
    print(f"    -> ¿Imagen contiene firma de audio Lazarus (LZAU)?: {is_lazarus}")
    assert is_lazarus, "Error: No se detectó la cabecera mágica LZAU en la imagen"

    # 4. Recuperar audio desde la imagen
    print("[2] Recuperando audio desde la imagen...")
    recuperado_ok = ReversibleConverter.image_to_audio_recovery(image_path, recov_audio_path)
    assert recuperado_ok, "Error: Falló la recuperación del audio"
    print(f"    -> Audio recuperado: {recov_audio_path.name}")

    # 5. Comparación PCM bit a bit
    a1 = AudioSegment.from_file(str(orig_audio_path))
    a2 = AudioSegment.from_file(str(recov_audio_path))
    propiedades_iguales = (
        a1.frame_rate == a2.frame_rate
        and a1.sample_width == a2.sample_width
        and a1.channels == a2.channels
    )
    bytes_pcm_iguales = (a1.raw_data == a2.raw_data)

    print("\n--- Resultados Test 2 ---")
    print(f"    Propiedades coinciden: {propiedades_iguales} (SampleRate: {a1.frame_rate}, Canales: {a1.channels})")
    print(f"    Muestras de Audio 100% idénticas bit a bit: {bytes_pcm_iguales}")

    if propiedades_iguales and bytes_pcm_iguales:
        print(">>> RESULTADO TEST 2: ¡ÉXITO TOTAL (Lossless)! <<<")
    else:
        print(">>> RESULTADO TEST 2: FALLO <<<")


if __name__ == "__main__":
    setup()
    try:
        # Si tienes archivos propios puedes pasar sus rutas aquí, ej:
        # test_flujo_imagen_a_audio_y_recuperacion(Path("lazarus.jpg"))
        # test_flujo_audio_a_imagen_y_recuperacion(Path("tu_audio.wav"))
        
        # Ejecución por defecto con datos sintéticos autocontenidos:
        test_flujo_imagen_a_audio_y_recuperacion()
        test_flujo_audio_a_imagen_y_recuperacion()
    finally:
        # Si deseas inspeccionar los archivos generados en test_temp/, comenta la siguiente línea:
        # cleanup()
        pass
