import pandas as pd
import io


def parse(content_bytes, rel_path, **tools):
    f = io.BytesIO(content_bytes)
    df = pd.read_csv(f, sep=';', decimal=',')
    df["Datetime"] = pd.to_datetime(df["Index"], format="%d/%m/%Y %H:%M")
    df.index = df["Datetime"]
    df.index.name = None
    del df["Index"]
    del df["Datetime"]
    return df