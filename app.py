from flask import Flask, render_template, request, jsonify
import yfinance as yf
import numpy as np
import os

app = Flask(__name__)

# Нотации от C4 до C5 включительно
NOTE_NAMES = [
    'C4', 'C#4', 'D4', 'D#4', 'E4', 'F4',
    'F#4', 'G4', 'G#4', 'A4', 'A#4', 'B4', 'C5'
]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_data', methods=['POST'])
def get_data():
    try:
        data = request.get_json()
        symbol = data['symbol']
        period = data['period']
        points = int(data['points'])

        stock = yf.Ticker(symbol)
        hist = stock.history(period=period)

        if hist.empty or len(hist['Close'].dropna()) < points:
            return jsonify({'error': 'Недостаточно данных для построения графика.'})

        prices = hist['Close'].dropna().to_numpy()

        # Получаем равномерно распределённые индексы
        sampled_indices = np.linspace(0, len(prices) - 1, points, dtype=int)
        sampled_prices = prices[sampled_indices]
        dates = hist.index[sampled_indices].strftime('%Y-%m-%d').tolist()

        # Нормализация цен в диапазон нот
        p_min, p_max = sampled_prices.min(), sampled_prices.max()
        scale = len(NOTE_NAMES) - 1
        normalized_indices = ((sampled_prices - p_min) / (p_max - p_min + 1e-8) * scale).round().astype(int)
        notes = [NOTE_NAMES[i] for i in normalized_indices]

        return jsonify({
            'prices': sampled_prices.tolist(),
            'dates': dates,
            'notes': notes
        })

    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    # Убедись, что index.html находится в папке templates/
    app.run(debug=True)
