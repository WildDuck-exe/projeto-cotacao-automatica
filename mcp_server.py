from flask import Flask, request, jsonify
import pandas as pd
import sys
import os

# Adiciona o diretório pai ao PATH para que mcp.py possa ser importado
sys.path.append(os.path.join(os.path.dirname(__file__), 'mcp'))
from mcp import process_pedido

app = Flask(__name__)

# Caminhos dos arquivos CSV, ajustados para o ambiente do Railway
# No Railway, o diretório de trabalho será a raiz do seu repositório (onde está o Procfile)
# Então, os caminhos devem ser relativos a essa raiz.
PRODUTOS_CSV_PATH = os.path.join(os.path.dirname(__file__), 'data', 'produtos.csv')
SINONIMOS_CSV_PATH = os.path.join(os.path.dirname(__file__), 'data', 'sinonimos.csv')

@app.route('/process_pedido', methods=['POST'])
def handle_process_pedido():
    data = request.get_json()
    pedido_texto = data.get('pedido')

    if not pedido_texto:
        return jsonify({'error': 'Pedido não fornecido'}), 400

    try:
        # Chama a função process_pedido do mcp.py
        cotacao_result = process_pedido(pedido_texto, PRODUTOS_CSV_PATH, SINONIMOS_CSV_PATH)
        return jsonify(cotacao_result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 5000))
