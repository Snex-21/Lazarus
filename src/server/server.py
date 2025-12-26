from flask import Flask
import os

# servicio web con Flask para mantener el bot vivo

#creo la app web con Flask
app = Flask(__name__)

#pagina principal del bot
@app.route('/', methods=['GET'])
def home():
    return 'bot funcionando', 200

port = int(os.environ.get('PORT', 5000))

# ejecuto la app
def run_flask():
    app.run(host='0.0.0.0', port=port)