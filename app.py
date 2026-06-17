from flask import Flask, render_template, request, redirect, url_for, jsonify
from paper_engine import PaperEngine
from market_data import get_btc_price

app = Flask(__name__)
engine = PaperEngine()

@app.route('/')
def index():
    price = get_btc_price()
    engine.check_targets(price)
    return render_template('index.html', state=engine.state, price=price)

@app.route('/api/state')
def api_state():
    price = get_btc_price()
    engine.check_targets(price)
    return jsonify({'price': price, 'state': engine.state})

@app.route('/set_targets', methods=['POST'])
def set_targets():
    side = request.form.get('side', 'UP')
    entry_target = float(request.form.get('entry_target', 0))
    exit_target = float(request.form.get('exit_target', 0))
    amount = float(request.form.get('amount', 1))
    engine.set_targets(side, entry_target, exit_target, amount)
    return redirect(url_for('index'))

@app.route('/manual_buy', methods=['POST'])
def manual_buy():
    price = get_btc_price()
    side = request.form.get('side', 'UP')
    amount = float(request.form.get('amount', 1))
    engine.buy(side, amount, price, reason='manual buy')
    return redirect(url_for('index'))

@app.route('/manual_sell', methods=['POST'])
def manual_sell():
    price = get_btc_price()
    engine.sell(price, reason='manual sell')
    return redirect(url_for('index'))

@app.route('/reset', methods=['POST'])
def reset():
    engine.reset()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
