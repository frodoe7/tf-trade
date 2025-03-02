from freqtrade.strategy import IStrategy, IntParameter, DecimalParameter
import talib.abstract as ta
import pandas as pd

class kama(IStrategy):
    minimal_roi = {
        "0": 0.316,
        "149": 0.113,
        "410": 0.072,
        "818": 0
    }

    stoploss = -0.206

    trailing_stop = True
    trailing_stop_positive = 0.02
    trailing_stop_positive_offset = 0.03
    trailing_only_offset_is_reached = True

    timeframe = "30m"
    
    periodBuy = IntParameter(low=8, high=24, default=12, space="buy")
    periodSell = IntParameter(low=8, high=24, default=19, space="sell")
    buy_threshold = DecimalParameter(low=0.001, high=0.01, default=0.001, space="buy")
    sell_threshold = DecimalParameter(low=0.001, high=0.01, default=0.001, space="sell")
    
    lvrg = IntParameter(low=2, high=20, default=10, space="roi")

    def populate_indicators(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        dataframe["kama_buy"] = ta.KAMA(dataframe["close"], timeperiod=self.periodBuy.value)
        dataframe["kama_sell"] = ta.KAMA(dataframe["close"], timeperiod=self.periodSell.value)
        dataframe["kama_buy_change"] = (dataframe["kama_buy"] - dataframe["kama_buy"].shift(1)) / dataframe["kama_buy"].shift(1)
        dataframe["kama_sell_change"] = (dataframe["kama_sell"] - dataframe["kama_sell"].shift(1)) / dataframe["kama_sell"].shift(1)

        return dataframe

    def populate_entry_trend(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        dataframe.loc[
            (dataframe["kama_buy_change"] > self.buy_threshold.value), "buy"
        ] = 1

        dataframe.loc[
            (dataframe["kama_sell_change"] < -self.sell_threshold.value), "sell"
        ] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        return dataframe

    def leverage(self, pair, current_time, current_rate, proposed_leverage, max_leverage, entry_tag, side, **kwargs):
        return self.lvrg.value
