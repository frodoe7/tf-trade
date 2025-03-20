FROM freqtradeorg/freqtrade:stable

RUN pip install datasieve \
    && pip install scikit-learn \
    && pip install joblib \
    && pip install catboost \
    && pip install lightgbm \
    && pip install xgboost \
    && pip install tensorboard \
    && pip freeze > /freqtrade/user_data/installed_packages.txt  # Save installed packages to a file