from datetime import datetime, timedelta

#查询周期
END_DATE = datetime.now()
START_DATE = (datetime.now() - timedelta(days=365*3))

#查询标的
CHINA_MARKET = '000300.SH' #沪深300
CHINA_STOCK = ['688981.SH',#寒武纪
               '688256.SH' #中芯国际
                ]
CHINA_ETF = []


AMERICA_MARKET = '^IXIC'
AMERICA_STOCK = ['AAPL',
                 'MSFT',
                 'QLD'
                 'TSLA',
                 'NVDA',
                 ]

#token
TUSHARE_TOKEN = 'ab75a5effbf918542640f2fb68dfefb0f6f5f04e804b9939d2651fca'
DEEPSEEK_TOKEN = 'sk-2247335a215a4405a9c6b5f759ff4f70'
FRED_TOKEN = 'cb3e01f5068a06b2acac6467af4be5a6'