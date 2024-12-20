import json
import requests
from zhipuai import ZhipuAI

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
        }
]

def query_db(sql):
    url = "https://comm.chatglm.cn/finglm2/api/query"
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

def parse_function_call(model_response,messages):
    # 处理函数调用结果，根据模型返回参数，调用对应的函数。
    # 调用函数返回结果后构造tool message，再次调用模型，将函数结果输入模型
    # 模型会将函数调用结果以自然语言格式返回给用户。
    if model_response.choices[0].message.tool_calls:
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
            model="glm-4",  # 填写需要调用的模型名称
            messages=messages,
            tools=tools,
        )
        print(response.choices[0].message)
        messages.append(response.choices[0].message.model_dump())

function_map = {
    "query_db":query_db
}
function_result_logger = []
def chat(messages):

    response = client.chat.completions.create(
        model="glm-4",  # 填写需要调用的模型名称
        messages=messages,
        tools=tools,
    )
    print(response.choices[0].message)
    return response

if __name__ == '__main__':

    client = ZhipuAI(api_key="f689043de7886e8c604802325fa16392.9m8y9PP2XBKP9ZJy")

    messages = [
        {"role": "system", "content": "不要假设或猜测传入函数的参数值。如果用户的描述不明确，请要求用户提供必要信息"},
    ]

    # response = chat(messages)
    # messages.append(response.choices[0].message.model_dump())
    # parse_function_call(response, messages)

    # messages.append({"role": "user", "content": "这趟航班的价格是多少？"})
    # response = chat(messages)
    # messages.append(response.choices[0].message.model_dump())
    # parse_function_call(response, messages)

    messages.append({"role": "user", "content": "SELECT * FROM constantdb.secumain LIMIT 10"})
    response = chat(messages)
    messages.append(response.choices[0].message.model_dump())
    parse_function_call(response, messages)

