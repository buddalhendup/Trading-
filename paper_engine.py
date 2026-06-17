import json
import os
from datetime import datetime

STATE_FILE = 'paper_state.json'

class PaperEngine:
    def __init__(self):
        self.state = self.load_state()

    def default_state(self):
        return {
            'paper_balance': 100.00,
            'position': None,
            'targets': None,
            'trade_log': []
        }

    def load_state(self):
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        return self.default_state()

    def save(self):
        with open(STATE_FILE, 'w') as f:
            json.dump(self.state, f, indent=2)

    def log(self, message):
        self.state['trade_log'].insert(0, {
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'message': message
        })
        self.state['trade_log'] = self.state['trade_log'][:50]
        self.save()

    def set_targets(self, side, entry_target, exit_target, amount):
        self.state['targets'] = {
            'side': side,
            'entry_target': entry_target,
            'exit_target': exit_target,
            'amount': amount,
            'active': True
        }
        self.log(f'Targets set: {side}, entry {entry_target}, exit {exit_target}, amount ${amount}')

    def buy(self, side, amount, price, reason='auto target buy'):
        if self.state['position'] is not None:
            self.log('Buy skipped: already in a position')
            return
        if amount <= 0 or amount > self.state['paper_balance']:
            self.log('Buy skipped: invalid amount')
            return
        self.state['paper_balance'] -= amount
        self.state['position'] = {
            'side': side,
            'amount': amount,
            'entry_price': price,
            'entry_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        self.log(f'PAPER BUY {side}: ${amount} at BTC ${price:.2f} because {reason}')

    def sell(self, price, reason='auto target sell'):
        pos = self.state['position']
        if pos is None:
            self.log('Sell skipped: no open position')
            return

        entry = pos['entry_price']
        amount = pos['amount']
        side = pos['side']

        if side == 'UP':
            pct_change = (price - entry) / entry
        else:
            pct_change = (entry - price) / entry

        simulated_pnl = amount * pct_change * 20
        returned = amount + simulated_pnl
        self.state['paper_balance'] += returned
        self.log(f'PAPER SELL {side}: exit BTC ${price:.2f}, P/L ${simulated_pnl:.2f}, reason {reason}')
        self.state['position'] = None
        self.save()

    def check_targets(self, price):
        t = self.state.get('targets')
        pos = self.state.get('position')
        if not t or not t.get('active'):
            return

        side = t['side']
        entry = t['entry_target']
        exit_target = t['exit_target']
        amount = t['amount']

        if pos is None:
            if side == 'UP' and price >= entry:
                self.buy(side, amount, price)
            elif side == 'DOWN' and price <= entry:
                self.buy(side, amount, price)
        else:
            if pos['side'] == 'UP' and price >= exit_target:
                self.sell(price)
            elif pos['side'] == 'DOWN' and price <= exit_target:
                self.sell(price)

    def reset(self):
        self.state = self.default_state()
        self.save()
