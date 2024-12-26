import json
from openpyxl import Workbook

# 从文件中读取 JSON 数据
json_file = '错误结果.json'
with open(json_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

# 创建一个新的 Excel 工作簿
wb = Workbook()
ws = wb.active
ws.title = "Team Data"

# 写入表头
ws.append(["id", "question", "ai_answer"])

# 遍历每个 team 数据
for team in data:
    # 遍历每个 team 内的条目
    for item in team.get("team", []):
        ws.append([item["id"], item["question"], item["answer"]])

# 保存到文件
output_file = "team_data.xlsx"
wb.save(output_file)

print(f"数据已成功写入到 {output_file}")
