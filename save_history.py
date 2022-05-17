#!/usr/bin/env python
import pandas as pd

def save_history(data,file):
    try:
        df = pd.read_csv(file)
    except FileNotFoundError:
        data.to_csv(file, index = False)
    else:
        pd.concat([df,data]).to_csv(file, index = False)

def clear_history(filter_field,value,file):
    try: 
        df = pd.read_csv(file)
    except FileNotFoundError:
        return "File does not exist"
    else:
        df = df[df[filter_field] != value]
        df.to_csv(file)
        return None