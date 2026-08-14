import pandas as pd


def first(series: pd.Series):
    return None if len(series) == 0 else series.iloc[0]