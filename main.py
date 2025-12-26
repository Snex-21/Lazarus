from src.bot import Lazarus
from src.claves import config as cg
from src.server.server import run_server
from threading import Thread

if __name__ == '__main__':
    # se inicia el servidor en un hilo separado para no bloquear al bot
    flask_thread = Thread(target=run_server)
    flask_thread.daemon = True
    flask_thread.start()
    
    # se conecta al bot y se inicia
    Lazarus_bot = Lazarus(
        api_hash = cg.api_hash,
        api_id = cg.api_id,
        token = cg.token,
    )
    
    Lazarus_bot.run()