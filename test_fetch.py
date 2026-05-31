from 半导体监控 import fetch_index_data, CONFIG

print('stock_code=', CONFIG['stock_code'])
df = fetch_index_data(CONFIG['stock_code'])
print('type', type(df))
print('rows', None if df is None else len(df))
if df is not None:
    print(df.head(2).to_dict(orient='records'))
