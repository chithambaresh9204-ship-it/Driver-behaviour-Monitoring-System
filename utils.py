# utils.py
import pandas as pd

def load_data():
    df = pd.read_csv("final_dataset.csv")
    return df
