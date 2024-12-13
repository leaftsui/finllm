import pandas as pd
import json
import re
import requests
from zhipuai import ZhipuAI
from tqdm import tqdm  # 导入tqdm

# 初始化API信息
api_key = "f689043de7886e8c604802325fa16392.9m8y9PP2XBKP9ZJy"
access_token = "0099fe8c9593475d96195107b7acf7bd"
fold = "./result/"
# 1. 读取数据字典
def load_data_dictionary(file_path):
    excel_file = pd.ExcelFile(file_path)
    first_sheet = excel_file.parse(0).to_json(orient="records", force_ascii=False)
    second_sheet = excel_file.parse(1).to_json(orient="records", force_ascii=False)
    return json.loads(first_sheet), json.loads(second_sheet)

# 2. 读取问题文件
def load_questions(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# 3. 调用ZhipuAI获取相关库表
def find_database_and_table(questions, database_structure):
    client = ZhipuAI(api_key=api_key)
    results = []

    # 使用tqdm为每个问题组添加进度条
    for question_group in tqdm(questions, desc="Processing Questions", unit="group"):
        chat_message = "".join(q['question'] for q in question_group['team'])
        response = client.chat.completions.create(
            model="glm-4-air",
            messages=[
                {"role": "user", "content": f"已知以下数据库 {json.dumps(database_structure)} 确定解决问题 {chat_message} 所需要的库名与表名"},
                {"role": "user", "content": "按照json格式返回 结构与数据库结构一致 只返回json，不得输出无关内容"}
            ]
        )
        results.append({
            "tid": question_group['tid'],
            "team": question_group['team'],
            "相关数据库字段": response.choices[0].message.content
        })

    with open(fold+"从问题到数据库表结构.json", 'w', encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

    return results

# 4. 匹配字段结构
def match_table_fields(related_db_fields, table_structure):
    for item in tqdm(related_db_fields, desc="Matching Fields", unit="item"):
        item["相关数据字段"] = [field for field in table_structure if field['table_name'] in item['相关数据库字段']]

    with open(fold+"根据库表结构匹配字段.json", 'w', encoding="utf-8") as f:
        json.dump(related_db_fields, f, ensure_ascii=False, indent=4)

    return related_db_fields

# 5. 精简表字段信息
def refine_table_fields(related_fields):
    client = ZhipuAI(api_key=api_key)
    refined_results = []

    # 使用tqdm为每个条目添加进度条
    for item in tqdm(related_fields, desc="Refining Fields", unit="item"):
        response = client.chat.completions.create(
            model="glm-4-air",
            messages=[
                {"role": "user", "content": f"解决问题：{item['历史对话']}需要以下哪些数据库字段支持：{json.dumps(item['相关数据字段'])}"},
                {"role": "user", "content": "按照数据库字段的json格式返回"}
            ]
        )
        item['适配字段'] = response.choices[0].message.content
        refined_results.append(item)

    with open(fold+"根据问题+表结构+字段找到适配字段.json", 'w', encoding="utf-8") as f:
        json.dump(refined_results, f, ensure_ascii=False, indent=4)

    return refined_results

# 6. 生成SQL语句
def generate_sql(refined_fields):
    client = ZhipuAI(api_key=api_key)
    sql_results = []

    # 使用tqdm为每个条目添加进度条
    for item in tqdm(refined_fields, desc="Generating SQL", unit="item"):
        response = client.chat.completions.create(
            model="glm-4-air",
            messages=[
                {"role": "user", "content": f"示例sql ：SELECT * FROM constantdb.secumain LIMIT 10 \n已知：{json.dumps(item)}"},
                {"role": "user", "content": "按照sql格式返回"}
            ]
        )
        item['sql'] = response.choices[0].message.content
        sql_results.append(item)

    with open(fold+"根据问题+表结构+字段生成sql.json", 'w', encoding="utf-8") as f:
        json.dump(sql_results, f, ensure_ascii=False, indent=4)

    return sql_results

# 7. 清洗SQL并获取结果
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

# 主程序入口
def main():
    data_file = "数据字典.xlsx"
    question_file = "question.json"

    # 加载数据
    db_structure, table_structure = load_data_dictionary(data_file)
    questions = load_questions(question_file)[0:1]

    # 执行各阶段处理
    related_db_fields = find_database_and_table(questions, db_structure)
    related_fields = match_table_fields(related_db_fields, table_structure)
    refined_fields = refine_table_fields(related_fields)
    sql_data = generate_sql(refined_fields)
    final_results = execute_sql_and_fetch_results(sql_data)

    print("处理完成，结果已保存。")

if __name__ == "__main__":
    main()
