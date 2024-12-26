#-*- coding:utf-8 -*-
import json
import requests
from zhipuai import ZhipuAI
import os
MODEL = "glm-4-flash"
# Windows
tools = [
        {
            "type": "function",
            "function": {
                "name": "query_db",
                "description": "调用接口执行SQL语句获取查询结果",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "sql": {
                            "description": "SQL语句",
                            "type": "string"
                        }
                    },
                    "required": ["sql"]
                },
            }
        },
    {
        "type": "function",
        "function": {
            "name": "save_info",
            "description": "保存回答问题所需的相关有效信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "info": {
                        "description": "有效信息",
                        "type": "string"
                    }
                },
                "required": ["info"]
            },
        }
    }
]

def query_db(sql):
    url = "https://comm.chatglm.cn/finglm2/api/query"
    print(sql)
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer a30d01d4630a43b087a1f9851680902a"
    }
    data = {
        "sql": sql,
        "limit": 10
    }
    response = requests.post(url, headers=headers, json=data)
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    return response.json()


info_collect = []
def save_info(info):
    info_collect.append(info)

def parse_function_call(model_response,messages):
    # 处理函数调用结果，根据模型返回参数，调用对应的函数。
    # 调用函数返回结果后构造tool message，再次调用模型，将函数结果输入模型
    # 模型会将函数调用结果以自然语言格式返回给用户。
    tool_call = model_response.choices[0].message.tool_calls[0]
    args = tool_call.function.arguments
    function_name = tool_call.function.name
    function_result = function_map.get(function_name)(**json.loads(args))
    function_result_logger.append(json.dumps(function_result))
    messages.append({
        "role": "tool",
        "content": f"{json.dumps(function_result)}",
        "tool_call_id":tool_call.id
    })
    response = client.chat.completions.create(
        model=MODEL,  # 填写需要调用的模型名称
        messages=messages,
        tools=tools,
    )
    print(response.choices[0].message)
    messages.append(response.choices[0].message.model_dump())

function_map = {
    "query_db":query_db,
    "save_info":save_info
}

function_result_logger = []
def chat(messages):
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=tools,
    )
    print(response.choices[0].message.content)
    return response

if __name__ == '__main__':

    client = ZhipuAI(api_key="f689043de7886e8c604802325fa16392.9m8y9PP2XBKP9ZJy")
    prompt = f"""
    任务：请你根据问题生成SQL一步一步找到相关信息直到查询的信息能够回答问题
    参考步骤：
    1.查询数据库下存在哪些表
    2.查询该表的表结构
    3.根据问题和表结构生成查询语句调用相关工具
    4.根据查询结果回答问题
    
    你可以调用数据库查询接口传入SQL语句获取执行结果
    对于表结构查询你可以参考以下语句：
    ```sql
    SELECT 
    TABLE_NAME AS `Table`, 
    COLUMN_NAME AS `Column`, 
    DATA_TYPE AS `Type`, 
    IS_NULLABLE AS `Null`, 
    NUMERIC_PRECISION AS `Precision`, 
    NUMERIC_SCALE AS `Scale`, 
    COLUMN_KEY AS `Key`, 
    COLUMN_COMMENT AS `Comment`
    FROM 
        information_schema.COLUMNS 
    WHERE 
        TABLE_NAME = '<需要查询的表名称>';
    ```
    查询数据库下有哪些表你可以参考以下语句：
    ```sql
    show tables in <数据库名称>
    ```

    现有数据库描述如下：
    库名中文	库名英文	表英文	表中文	表描述
    常量库	ConstantDB	SecuMain	证券主表	本表收录单个证券品种（股票、基金、债券）的代码、简称、上市交易所等基础信息。
    常量库	ConstantDB	HK_SecuMain	港股证券主表	本表收录港股单个证券品种的简称、上市交易所等基础信息。
    常量库	ConstantDB	CT_SystemConst	系统常量表	本表收录数据库中各种常量值的具体分类和常量名称描述。
    常量库	ConstantDB	QT_TradingDayNew	交易日表(新)	本表收录各个市场的交易日信息，包括每个日期是否是交易日，是否周、月、季、年最后一个交易日
    常量库	ConstantDB	LC_AreaCode	国家城市代码表	本表收录世界所有国家层面的数据信息和我国不同层级行政区域的划分信息。
    机构数据库	InstitutionDB	PS_EventStru	事件体系指引表	收录聚源最新制定的事件分类体系。
    常量库	ConstantDB	US_SecuMain	美股证券主表	本表收录美国等境外市场单个证券品种的简称、上市交易所等基础信息。
    机构数据库	InstitutionDB	PS_NewsSecurity	证券舆情表	收录了全网披露的舆情信息涉及的相关证券，对对应的事件信息，并对相应的事件的正负面情感及情感重要性进行等级划分。
    上市公司基本资料	AStockBasicInfoDB	LC_StockArchives	公司概况	收录上市公司的基本情况，包括：联系方式、注册信息、中介机构、行业和产品、公司证券品种及背景资料等内容。
    上市公司基本资料	AStockBasicInfoDB	LC_NameChange	公司名称更改状况	收录公司名称历次变更情况，包括：中英文名称、中英文缩写名称、更改日期等内容。
    上市公司基本资料	AStockBasicInfoDB	LC_Business	公司经营范围与行业变更	"1.收录上市公司、发债公司的经营范围（包括主营和兼营）以及涉足行业情况。
    
    注意
    1.撰写的select语句中的表名称前面要带上数据库，如：AStockIndustryDB.LC_ExgIndustry
    3.确保生成的SQL语句中的数据库信息和查询结果一致不得随意编造

    """
    question = "600872的全称、A股简称、法人、法律顾问、会计师事务所及董秘是？"
    # question = "请你查询LC_StockArchives表结构并调用相关工具到数据库查询"
    # question = "SecuCode为600872的公司中英文名称和简称"

    messages = [
        {"role": "system", "content": "不要假设或猜测传入函数的参数值。如果用户的描述不明确，请要求用户提供必要信息"},
        {"role": "user", "content": prompt},
        {"role": "user", "content": question}
    ]
    while True:
        # print(info_collect)
        response = chat(messages)
        messages.append(response.choices[0].message.model_dump())
        if response.choices[0].message.tool_calls:
            parse_function_call(response, messages)
            continue
        # if "任务完成" in response.choices[0].message.content:
        #     break





