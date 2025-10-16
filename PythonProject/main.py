import stock_data_fetcher as sdf
import data_calculation as dc
import LLM_analysis as la
import pandas as pd
from datetime import datetime
#import visualization
import config

#获取股价数据
china_stock_prices = sdf.fetch_stock_price(config.CHINA_STOCK)
china_market_prices= sdf.fetch_index_price(config.CHINA_MARKET)

america_stock_prices = sdf.fetch_american_stock(config.AMERICA_STOCK)
america_market_prices = sdf.fetch_american_index(config.AMERICA_MARKET)

#获取计算数据结果
china_calculation = dc.analyze_stocks(china_stock_prices, china_market_prices)
america_calculation = dc.analyze_stocks(america_stock_prices, america_market_prices)

combined_calculation = pd.concat([china_calculation, america_calculation], axis=0)

#获取AI分析结果
ai_analysis = la.analyze_stock_with_ai(combined_calculation)

#准备输出结果到md
timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
file_name = f'reports/stock_analysis_{timestamp}.md'

file_content = f'{combined_calculation}\n{ai_analysis}'

with open(file_name, 'w', encoding='utf-8') as f:
    f.write(file_content)

print("分析报告已保存")

#绘制散点图
#visualization.plot_beta_alpha_interactive(results)