from scipy import stats
import pandas as pd
import stock_data_fetcher as sf

def calculate_basic(stock_prices):

    #最近价格
    last_price = stock_prices.iloc[-1]
    last_10_price_mean = stock_prices.iloc[-10:].mean()

    #最近收益
    daily_returns = stock_prices.pct_change(fill_method=None).dropna()
    last_return= daily_returns.iloc[-1]
    last_5_return = daily_returns.iloc[-5:].sum()
    last_30_return = daily_returns.iloc[-30:].sum()
    last_180_return = daily_returns.iloc[-180:].sum()

    return {
        'last_price': last_price,
        'last_10_price_mean':last_10_price_mean,
        'last_return': last_return,
        'last_5_return': last_5_return,
        'last_30_return': last_30_return,
        'last_180_return': last_180_return,
    }

#波动性相关：最大回撤、最大单日涨跌、top涨跌交易日
def calculate_drawdown_metrics(stock_prices):
    cumulative_max = stock_prices.expanding().max() #expanding是指至当前的累计最高价
    drawdown = (stock_prices - cumulative_max)/cumulative_max
    max_drawdown = drawdown.min() #最大回撤（负数）

    #计算最大回撤时间
    max_drawdown_end = drawdown.idxmin()
    max_drawdown_start = stock_prices[:max_drawdown_end].idxmax() #这句没懂

    #最大单日跌幅和涨幅
    daily_returns = stock_prices.pct_change(fill_method=None).dropna()
    max_daily_drop = daily_returns.min()
    max_daily_gain = daily_returns.max()

    #找到对应日期
    max_drop_date = daily_returns.idxmin()
    max_gain_date = daily_returns.idxmax()

    #top波动日期
    top_gains = daily_returns.nlargest(5).index# 涨幅最大的10天
    top_drops = daily_returns.nsmallest(5).index  # 跌幅最大的10天

    return {
        'max_drawdown': max_drawdown,
        'max_drawdown_start': max_drawdown_start,
        'max_drawdown_end': max_drawdown_end,

        'max_daily_drop': max_daily_drop,
        'max_drop_date': max_drop_date,

        'max_daily_gain': max_daily_gain,
        'max_gain_date': max_gain_date,

        'top_gains_date': top_gains,
        'top_drops_date': top_drops
    }
#根据CAPM分析股票相对指数的beta、alpha，并同时返回收益
def calculate_capm_metrics(stock_prices, market_prices):

    #把价格序列处理为收益率序列，并去掉空值
    stock_returns = stock_prices.pct_change(fill_method=None).dropna()
    market_returns = market_prices.pct_change(fill_method=None).dropna()

    #对齐股票收益和市场收益的时间序列
    stock_returns_aligned, market_returns_aligned = stock_returns.align(market_returns, join='inner')

    # 对股票日收益和市场日收益做线性回归:
    slope, intercept, r_value, p_value, std_err = stats.linregress(market_returns_aligned, stock_returns_aligned)

    #计算统计期间总收益:
    stock_total_return = (stock_prices.iloc[-1] / stock_prices.iloc[0] - 1)
    market_total_return = (market_prices.iloc[-1] / market_prices.iloc[0] - 1)
    #计算年化alpha:
    alpha = stock_total_return - slope * market_total_return
    days = len(stock_returns_aligned)
    years = days / 252
    annualized_alpha = ((1 + alpha) ** (1 / years) - 1) if years > 0 else alpha

    return {
        'stock_total_return': stock_total_return,
        'market_total_return': market_total_return,

        'beta': slope,
        'annualized_alpha': annualized_alpha,
        'r2_value': r_value ** 2,
        'p_value': p_value,
    }

def analyze_stocks(df_stock, market_prices):
    results = []  # 创建了空列表

    for stock_code in df_stock.columns:

        stock_prices = df_stock[stock_code]

        #stock_name = sf.get_stock_name(stock_code) #查询股票名
        basic_metrics = calculate_basic(stock_prices)
        drawdown_metrics = calculate_drawdown_metrics(stock_prices) #计算回撤指标
        capm_metrics = calculate_capm_metrics(stock_prices, market_prices) #计算总收益、市场总收益、beta、alpha
        #计算

        results.append({
            #基础指标
            '股票代码': stock_code,
            #'股票名称': stock_name,

            # '股票名称': stock_name,

            # 近期行情
            '昨日收盘价': round(basic_metrics['last_price'], 2),
            '近10日均价': round(basic_metrics['last_10_price_mean'], 2),

            '昨日涨幅': f'{basic_metrics['last_return'] * 100:.1f}%',
            '5日涨幅': f'{basic_metrics['last_5_return'] * 100:.1f}%',
            '30日涨幅': f'{basic_metrics['last_30_return'] * 100:.1f}%',
            '半年涨幅': f'{basic_metrics['last_180_return'] * 100:.1f}%',
            # 波动回撤指标
            '最大回撤': f'{drawdown_metrics['max_drawdown'] * 100:.1f}%',
            '最大回撤起始日期': drawdown_metrics['max_drawdown_start'],
            '最大回撤结束日期': drawdown_metrics['max_drawdown_end'],

            '最大单日跌幅': f'{drawdown_metrics['max_daily_drop'] * 100:.1f}%',
            '最大单日跌幅日期': drawdown_metrics['max_drop_date'],

            '最大单日涨幅': f'{drawdown_metrics['max_daily_gain'] * 100:.1f}%',
            '最大单日涨幅日期': drawdown_metrics['max_gain_date'],
            # capm指标
            '累计涨幅': f'{capm_metrics['stock_total_return'] * 100:.1f}%',
            '市场涨幅': f'{capm_metrics['market_total_return'] * 100:.1f}%',
            'beta': round(capm_metrics['beta'], 2),
            '年化alpha': f'{capm_metrics['annualized_alpha'] * 100:.1f}%',
            'R²值': round(capm_metrics['r2_value'], 2),
            'p值': round(capm_metrics['p_value'], 4)

        })
    df_results = pd.DataFrame(results)
    return df_results