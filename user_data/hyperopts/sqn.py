from freqtrade.optimize.hyperopt import IHyperOptLoss
import pandas as pd
import numpy as np

class SQNLoss(IHyperOptLoss):
    @staticmethod
    def hyperopt_loss_function(results: pd.DataFrame, trade_count: int, **kwargs) -> float:
        # if trade_count < 500:
        #     return 1

        risk_per_trade = results["profit_abs"].abs().mean()
        if risk_per_trade == 0:
            return 10

        results["r_multiple"] = results["profit_abs"] / risk_per_trade

        # Compute SQN
        mean_r = results["r_multiple"].mean()
        std_r = results["r_multiple"].std(ddof=0)
        sqn = (mean_r / std_r) * np.sqrt(trade_count) if std_r > 0 else 0

        return -sqn
