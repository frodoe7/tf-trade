from freqtrade.strategy import IStrategy, IntParameter, DecimalParameter
from pandas import DataFrame
import talib.abstract as ta

class bbands(IStrategy):
    timeframe = "30m"
    stoploss = -0.15;
    can_short = True
    
    minimal_roi = {
        "0": 0.326,
        "228": 0.171,
        "571": 0.071,
        "1135": 0
    }
    
    trailing_stop = True
    trailing_stop_positive = 0.01
    trailing_stop_positive_offset = 0.028
    trailing_only_offset_is_reached = True

    bbPeriodBuy = IntParameter(low=8, high=32, default=22, space="buy")
    stDevBuy = DecimalParameter(low=1.0, high=5.0, default=1.901, space="buy")
    
    bbPeriodSell = IntParameter(low=8, high=32, default=27, space="sell")
    stDevSell = DecimalParameter(low=1.0, high=5.0, default=3.712, space="sell")
    
    lvrg = IntParameter(low=2, high=20, default=10, space="roi")
    
    plot_config = {
        "main_plot": {
            "bb_lower_buy": {"color": "green", "plotly": {"opacity": 0.7}},
            "bb_upper_sell": {"color": "red", "plotly": {"opacity": 0.7}},
        },
        "subplots": {},
    }

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # generate values for technical analysis indicators
        bbBuy = ta.BBANDS(
            dataframe,
            timeperiod=self.bbPeriodBuy.value,
            nbdevup=self.stDevBuy.value,
            nbdevdn=self.stDevBuy.value,
        )
        
        bbSell = ta.BBANDS(
            dataframe,
            timeperiod=self.bbPeriodSell.value,
            nbdevup=self.stDevSell.value,
            nbdevdn=self.stDevSell.value,
        )

        # Assign values to dataframe
        dataframe["bb_lower_buy"] = bbBuy["lowerband"]
        
        dataframe["bb_upper_sell"] = bbSell["upperband"]

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[(dataframe["bb_lower_buy"] > dataframe["close"]), "buy"] = 1
        dataframe.loc[(dataframe["bb_upper_sell"] < dataframe["close"]), "sell"] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        return dataframe
    
    def leverage(self, pair, current_time, current_rate, proposed_leverage, max_leverage, entry_tag, side, **kwargs):
        return self.lvrg.value