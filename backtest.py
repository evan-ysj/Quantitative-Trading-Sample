import numpy as np
import pandas as pd
from numbers import Number

from Strategy import Strategy, SmaCross
from utils import assert_msg, crossover, SMA, read_file


class ExchangeAPI:
    def __init__(self, data, cash, commission):
        assert_msg(cash > 0, 'Initial cash must be greater than 0!')
        assert_msg(0 <= commission <= 0.05, 
                   'Commission must be a positive integer which is usually smaller that 0.05')
        self._initial_cash = cash
        self._cash = cash
        self._position = 0
        self._data = data
        self._commission = commission
        self._i = 0
        
    @property
    def cash(self):
        return self._cash
    
    @property
    def initial_cash(self):
        return self._initial_cash
    
    @property
    def position(self):
        return self._position
    
    @property
    def current_price(self):
        return self._data.Close[self._i]
    
    @property
    def market_value(self):
        return self._cash + self.current_price * self._position
    
    def buy(self):
        self._position = float((self._cash * (1 - self._commission)) / self.current_price)
        self._cash = 0
        
    def sell(self):
        self._cash += float(self._position * self.current_price * (1 - self._commission))
        self._position = 0
        
    def next(self, tick):
        self._i = tick
        

class Backtest:
    def __init__(self,
                 data: pd.DataFrame,
                 strategy_type: type(Strategy),
                 broker_type: type(ExchangeAPI),
                 cash: float = 10000.0,
                 commission: float = 0.0005):
        
        assert_msg(issubclass(strategy_type, Strategy), 'Input "strategy_type" is not a "Strategy" type!')
        assert_msg(issubclass(broker_type, ExchangeAPI), 'Input "broker_type" is not a "ExchangeAPI" type!')
        assert_msg(isinstance(commission, Number), 'Input "commission" is not a float number!')
        
        data = data.copy(False)
        
        if 'Volume' not in data:
            data['Volume'] = np.nan
            
        assert_msg(len(data.columns & {'Open', 'High', 'Low', 'Close', 'Volume'}) == 5, 
                   'Incorrect data format. At least include "Open, High, Low, Close"!')
        
        assert_msg(not data[['Open', 'High', 'Low', 'Close', 'Volume']].max().isnull().any(), 
                   'Blank content in OHLC, please delete or fill the blank parts!')
        
        if not data.index.is_monotonic_increasing:
            data = data.sort_index()
            
        self._data = data
        self._result = None
        self._broker = broker_type(data, cash, commission)
        self._strategy = strategy_type(self._broker, self._data)
        
    def run(self) -> pd.Series:
        
        strategy = self._strategy
        broker = self._broker
        
        strategy.init()
        
        start = 100
        end = len(self._data)
        
        for i in range(start, end):
            broker.next(i)
            strategy.next(i)
        
        self._results = self._compute_result(broker)
        return self._results
    
    def _compute_result(self, broker):
        s = pd.Series()
        s['Initial value:'] = broker.initial_cash
        s['Final value:'] = broker.market_value
        s['Profit:'] = broker.market_value - broker.initial_cash
        return s
    

def main():
    BTCUSD = read_file('BTCUSD_GEMINI.csv')
    backtest = Backtest(BTCUSD, SmaCross, ExchangeAPI, 10000.0, 0.0006)
    ret = backtest.run()
    print(ret)
    
if __name__ == '__main__':
    main()
        