import abc
import numpy as np
from typing import Callable
from utils import assert_msg, crossover, SMA


class Strategy(metaclass = abc.ABCMeta):
    def __init__(self, broker, data):
        self._broker = broker
        self._data = data
        self._tick = 0
        self._indicators = []
        
    def I(self, func: Callable, *args) -> np.ndarray:
        value = func(*args)
        value = np.asarray(value)
        assert_msg(value.shape[-1] == len(self._data.Close), 'The length of indicator must equal to that of data!')
        self._indicators.append(value)
        return value
    
    @property
    def tick(self):
        return self._tick
    
    @property
    def data(self):
        return self._data
    
    def buy(self):
        self._broker.buy()
    
    def sell(self):
        self._broker.sell()
        
    @abc.abstractmethod
    def init(self):
        pass
    
    @abc.abstractmethod
    def next(self):
        pass
    

class SmaCross(Strategy):
    
    fast = 30
    slow = 90
    
    def init(self):
        self.sma1 = self.I(SMA, self.data.Close, self.fast)
        self.sma2 = self.I(SMA, self.data.Close, self.slow)
        
    def next(self, tick):
        if crossover(self.sma1[:tick], self.sma2[:tick]):
            self.buy()
        elif crossover(self.sma2[:tick], self.sma1[:tick]):
            self.sell()
        else:
            pass