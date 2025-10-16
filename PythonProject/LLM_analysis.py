#传入数据分析后的结论，给到大模型做进一步分析
import pandas as pd
from openai import OpenAI
import config

client = OpenAI(
    api_key=config.DEEPSEEK_TOKEN,
    base_url="https://api.deepseek.com"
)

def draw_down_reason(results):

    data_text = results.to_string(index=False)

    #参考文章
    howard = '''
    © 2025 Oaktree Capital Management, L.P. 保留所有权利

备忘录：致橡树资本（Oaktree）的客户
发信人：霍华德·马克斯（Howard Marks）
主题：无人知晓（再续）

在我看来，迄今为止的关税发展如同足球迷所称之为的"乌龙球" ——队员不慎将球送入自家球门而造成对方得分的情况。这种情况与英国脱欧非常相似，而我们已经知道
    '''
    prompt = f'''
    你是文笔很好的巴菲特，请根据我给你的股票信息和参考文档，给我写一段分析实事的memo。但请不要太长，控制在1000字以内
    以下是股票信息：
    {data_text}
    以下是参考文档：
    {howard}
'''

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}]
    )

    return prompt, response.choices[0].message.content

def analyze_stock_with_ai(results):

    prompt, analysis = draw_down_reason(results)

    file_content = f'{analysis}\n\nprompt:\n{prompt}'

    return file_content