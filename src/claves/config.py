from dotenv import load_dotenv
import os

# cargo las variables de entorno
load_dotenv()

# variables de entorno
api_id = int(os.getenv('api_id'))
api_hash = os.getenv('api_hash')
token = os.getenv('token_bot')

from pathlib import Path

# ruta de la raiz del proyecto
root_dir = Path(__file__).parent.parent.parent