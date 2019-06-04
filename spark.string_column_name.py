import pandas as pd
import unidecode

df = df.applymap(str)

for x in df.columns:
    df = df.rename(columns = {x : re.sub('[^A-Za-z0-9]+', '_', unidecode.unidecode(x)).lower()})
    for x in df.columns:
        if x[len(x)-1:] == '_':
            df = df.rename(columns = {x : x[0:len(x)-1]})
            
df.to_parquet(OUTPUT_PATH, compression='snappy')
