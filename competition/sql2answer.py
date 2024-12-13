import pandas as pd
import json
import re
import requests
from zhipuai import ZhipuAI
from tqdm import tqdm

api_key = "f689043de7886e8c604802325fa16392.9m8y9PP2XBKP9ZJy"
access_token = "0099fe8c9593475d96195107b7acf7bd"
fold = "./result/"

def execute_sql_and_fetch_results(sql_data):
    pattern = r'(?s)\```sql\n(.*?)\n\```'
    results = []

    # 使用tqdm为每个条目添加进度条
    for item in tqdm(sql_data, desc="Executing SQL", unit="item"):
        match = re.search(pattern, item.get('sql', ''))
        if match:
            extracted_sql = match.group(1)
            url = "https://comm.chatglm.cn/finglm2/api/query"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}"
            }
            data = {"sql": extracted_sql, "limit": 10}
            response = requests.post(url, headers=headers, json=data)
            item['query_result'] = response.json()
            results.append(item)

    with open(fold+'result.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

    return results