from freqtrade.strategy import IStrategy, IntParameter, DecimalParameter
import talib.abstract as ta
import pandas as pd

class psar(IStrategy):
    minimal_roi = {
        "0": 0.299,
        "345": 0.207,
        "1019": 0.061,
        "2354": 0
    }

    stoploss = -0.27

    trailing_stop = True
    trailing_stop_positive = 0.02
    trailing_stop_positive_offset = 0.03
    trailing_only_offset_is_reached = True

    timeframe = "1h"

    acceleration_buy = DecimalParameter(low=0.001, high=0.05, default=0.045, space="buy")
    maximum_buy = DecimalParameter(low=0.1, high=0.5, default=0.403, space="buy")
    
    acceleration_sell = DecimalParameter(low=0.001, high=0.05, default=0.015, space="sell")
    maximum_sell = DecimalParameter(low=0.1, high=0.5, default=0.344, space="sell")

    sar_candles_confirm_buy = IntParameter(low=2, high=5, default=5, space="buy")
    sar_candles_confirm_sell = IntParameter(low=2, high=5, default=5, space="sell")
    
    lvrg = IntParameter(low=2, high=20, default=10, space="roi")

    def populate_indicators(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        dataframe["sar_buy"] = ta.SAR(dataframe, acceleration=self.acceleration_buy.value, maximum=self.maximum_buy.value)
        dataframe["sar_sell"] = ta.SAR(dataframe, acceleration=self.acceleration_sell.value, maximum=self.maximum_sell.value)
        
        dataframe["sar_below"] = (dataframe["sar_buy"] < dataframe["close"]).astype(int)
        dataframe["sar_above"] = (dataframe["sar_sell"] > dataframe["close"]).astype(int)

        dataframe["sar_below_count"] = dataframe["sar_below"].groupby((dataframe["sar_below"] != dataframe["sar_below"].shift()).cumsum()).cumsum()
        dataframe["sar_above_count"] = dataframe["sar_above"].groupby((dataframe["sar_above"] != dataframe["sar_above"].shift()).cumsum()).cumsum()

        return dataframe

    def populate_entry_trend(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        dataframe.loc[
            (dataframe["sar_below_count"] >= self.sar_candles_confirm_buy.value), "buy"
        ] = 1
        
        dataframe.loc[
            (dataframe["sar_above_count"] >= self.sar_candles_confirm_sell.value), "sell"
        ] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        return dataframe
    
    def leverage(self, pair, current_time, current_rate, proposed_leverage, max_leverage, entry_tag, side, **kwargs):
        return self.lvrg.value