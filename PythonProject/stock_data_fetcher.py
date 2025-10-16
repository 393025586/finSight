import pandas as pd
import tushare as ts
import yfinance as yf
import time
import config

#导入config设置的token
if config.TUSHARE_TOKEN:
    ts.set_token(config.TUSHARE_TOKEN)
    pro = ts.pro_api()
else:
    pro = None
    print("⚠️未设置TUSHARE_TOKEN，A股功能将不可用")

#A股长周期股价
def fetch_stock_price(target_stock, start_date=None, end_date=None):
    stock_dict = {}

    if start_date is None:
        start_date = config.START_DATE.strftime('%Y%m%d')
    if end_date is None:
        end_date = config.END_DATE.strftime('%Y%m%d')

    for stock in target_stock:
        try:
            df = pro.daily(ts_code=stock, adj='qfq', start_date=start_date, end_date=end_date)
            if df is None or df.empty:
                continue
            df = df.set_index('trade_date')
            df = df.sort_index()
            df.index = pd.to_datetime(df.index)
            stock_dict[stock] = df['close']

            time.sleep(0.4)  # 防止被封

        except Exception as e:
            print(f'{stock}:{e}')
    return pd.DataFrame(stock_dict)

#A股股票名称
def get_stock_name(stock_code):
    """通过股票代码获取股票名称"""
    try:
        df = pro.stock_basic(ts_code=stock_code, fields='ts_code,name,industry,market')
        if not df.empty:
            return df['name'].iloc[0]
        else:
            return '未知'
    except Exception as e:
        print(f'获取股票名称失败: {e}')
        return '未知'
#使用tushare获取A股指数价格
def fetch_index_price(index=config.CHINA_MARKET, start_date=None, end_date=None):

    if start_date is None:
        start_date = config.START_DATE.strftime('%Y%m%d')
    if end_date is None:
        end_date = config.END_DATE.strftime('%Y%m%d')

    try:
        df = pro.index_daily(ts_code=index, start_date=start_date, end_date=end_date)
        if df is None or df.empty:
            return pd.Series()
        df = df.set_index('trade_date')
        df = df.sort_index()
        df.index = pd.to_datetime(df.index)
        return df['close']

    except Exception as e:
        print(e)
        return pd.Series()

#使用yfinance获取美股数据
def fetch_american_stock(target_stock, start_date=None, end_date=None):

    if start_date is None:
        start_date = config.START_DATE
    if end_date is None:
        end_date = config.END_DATE

    tickers = target_stock
    data = yf.download(tickers, start=start_date, end=end_date, auto_adjust=True)

    price_data = data.loc[:,'Close']

    return(price_data)
def fetch_american_index(target_index, start_date=None, end_date=None):

    if start_date is None:
        start_date = config.START_DATE
    if end_date is None:
        end_date = config.END_DATE

    ticker = yf.download(target_index, start=start_date, end=end_date, auto_adjust=True)
    price_data = ticker['Close']
    return(price_data.squeeze())

# 测试模块
if __name__ == '__main__':
    ticker = yf.Ticker('AAPL')

    md = f"#是例 \n\n"

    for key, value in ticker.info.items():
        md += f"**{key}**: {value}\n\n"


    with open('xinxi.md', 'w', encoding='utf-8') as f:
        f.write(md)
