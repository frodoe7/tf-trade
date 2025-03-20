from freqtrade.strategy import IStrategy, IntParameter, DecimalParameter
import talib.abstract as ta
import pandas as pd


class andy(IStrategy):
    minimal_roi = {
        "0": 0.139,
        "13": 0.025,
        "61": 0.011,
        "127": 0
    }

    stoploss = -0.249

    trailing_stop = True
    trailing_stop_positive = 0.242
    trailing_stop_positive_offset = 0.247
    trailing_only_offset_is_reached = True

    stake_currency = "USDT:USDT"

    can_short = True
    max_open_trades = 10

    timeframe = "5m"
    initial_stack_amount = DecimalParameter(
        low=5, high=10, default=5, space="roi", optimize=False
    )
    stack_amount = initial_stack_amount.value

    max_doubling = IntParameter(low=1, high=10, default=7, space="roi", optimize=False)
    max_consecutive_direction = IntParameter(
        low=1, high=10, default=5, space="roi", optimize=False
    )
    lvrg = IntParameter(low=2, high=20, default=1, space="roi", optimize=False)

    buy_sell_index = 0
    current_doubling_index = 1
    
    initial_stack_amount = DecimalParameter(
        low=5, high=10, default=5, space="roi", optimize=False
    )
    
    initial_stack_amount = DecimalParameter(
        low=5, high=10, default=5, space="roi", optimize=False
    )

    initial_stack_amount = DecimalParameter(
        low=5, high=10, default=5, space="roi", optimize=False
    )
    
    mfi_down_point = IntParameter(
        low=10, high=30, default=28, space="buy", optimize=True
    )
    
    mfi_up_point = IntParameter(
        low=70, high=90, default=87, space="buy", optimize=True
    )
    
    # bop_up_point = DecimalParameter(
    #     low=0.6, high=0.8, default=0.793, space="buy", optimize=True
    # )
    
    # bop_down_point = DecimalParameter(
    #     low=-0.8, high=-0.6, default=-0.787, space="buy", optimize=True
    # )
    
    roc_down_point = DecimalParameter(
        low=-5.0, high=-4.0, default=-4.369, space="buy", optimize=True
    )
    
    roc_up_point = DecimalParameter(
        low=4.0, high=5.0, default=4.577, space="buy", optimize=True
    )

    def populate_indicators(
        self, dataframe: pd.DataFrame, metadata: dict
    ) -> pd.DataFrame:
        # dataframe["bop"] = ta.BOP(dataframe["open"], dataframe["high"], dataframe["low"], dataframe["close"])
        dataframe["roc"] = ta.ROC(dataframe["close"], timeperiod=9)
        dataframe["mfi"] = ta.MFI(dataframe["high"], dataframe["low"], dataframe["close"], dataframe["volume"], timeperiod=14)
        
        return dataframe

    def populate_entry_trend(self, df, metadata):
        df.loc[(df["roc"] <= self.roc_down_point.value) & (df["mfi"] <= self.mfi_down_point.value), "enter_long"] = 1
        df.loc[(df["roc"] >= self.roc_up_point.value) & (df["mfi"] >= self.mfi_up_point.value), "enter_short"] = 1

        return df

    def populate_exit_trend(self, df, metadata):
        return df

    def leverage(
        self,
        pair,
        current_time,
        current_rate,
        proposed_leverage,
        max_leverage,
        entry_tag,
        side,
        **kwargs
    ):
        return self.lvrg.value

    def custom_stake_amount(
        self,
        pair,
        current_time,
        current_rate,
        proposed_stake,
        min_stake,
        max_stake,
        leverage,
        entry_tag,
        side,
        **kwargs
    ):
        return self.stack_amount

    def confirm_trade_entry(
        self,
        pair,
        order_type,
        amount,
        rate,
        time_in_force,
        current_time,
        entry_tag,
        side,
        **kwargs
    ):
        # if side == "long":
        #     if self.buy_sell_index >= self.max_consecutive_direction.value:
        #         return False
        # else:
        #     if self.buy_sell_index <= (-1 * self.max_consecutive_direction.value):
        #         return False

        return True

    def confirm_trade_exit(
        self,
        pair,
        trade,
        order_type,
        amount,
        rate,
        time_in_force,
        exit_reason,
        current_time,
        **kwargs
    ):
        isWin = trade.close_profit is not None and trade.close_profit > 0.0

        # if trade.is_short:
        #     self.buy_sell_index += 1
        # else:
        #     self.buy_sell_index -= 1

        if isWin:
            self.stack_amount = self.initial_stack_amount.value
            self.current_doubling_index = 1
        else:
            if self.current_doubling_index <= self.max_doubling.value:
                self.stack_amount *= 2
                self.current_doubling_index += 1
            else:
                self.stack_amount = self.initial_stack_amount.value
                self.current_doubling_index = 1
        
        return True
