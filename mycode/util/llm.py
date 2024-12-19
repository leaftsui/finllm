import re
import json
from openai import OpenAI
import tiktoken

class LLMClient:
    def __init__(self):
        self.zhipu_key = "f689043de7886e8c604802325fa16392.9m8y9PP2XBKP9ZJy"
        self.client = OpenAI(
            api_key=self.zhipu_key,
            base_url="https://open.bigmodel.cn/api/paas/v4/"
        )
        self.enc = tiktoken.encoding_for_model("gpt-4")


    def llm_eval(self, content, check_function=None):
        if check_function:
            llm_res = self.llm(content)
            res = self.super_eval(llm_res)
            if check_function(json.dumps(res)):
                return res
            else:
                messages = [{'role': 'user', 'content': content},
                           {'role': 'assistant', 'content': llm_res},
                           {'role': 'user',
                            'content': 'json格式化检查未通过，请严格按照json格式输出,并且将json内容放在```json\n```内'}
                           ]
                llm_res = self.llm(messages)
                res = self.super_eval(llm_res)
                if check_function(json.dumps(res)):
                    return res
                else:
                    raise ValueError
        else:
            return self.super_eval(self.llm(content))

    def chat(self, content, print_str=True, max_input=70000, max_rounds=25):
        if isinstance(content, str):
            messages = [{'role': 'user', 'content': content}]
        elif isinstance(content, list):
            if len(content) > max_rounds:
                raise ValueError('对话轮数过长')
            messages = content
        else:
            raise ValueError('输入格式错误')

        if len(self.enc.encode(str(messages))) > max_input:
            raise ValueError('消息过长')

        completion = self.client.chat.completions.create(
            model="GLM-4-plus",
            messages=messages,
            top_p=0.7,
            temperature=0.9,
            max_tokens=5000,
            stream=False,
            tools=[{'type': 'web_search', 'web_search': {"enable": False, 'type': 'web_search'}}],
        )

        answer = completion.choices[0].message.content
        if print_str:
            print(answer)

        if isinstance(content, list):
            content.append({"role": "assistant", "content": answer})

        return answer

    def Embedding(self, x):
        if isinstance(x, str):
            return self.client.embeddings.create(input=x, model='Embedding-3').data[0].embedding
        if isinstance(x, list):
            embeddings = self.client.embeddings.create(input=x, model='Embedding-3').data
            return [i.embedding for i in embeddings]

if __name__ == '__main__':
    llm_client = LLMClient()
    llm_client.chat('你好')
    # print(llm_client.Embedding('你好'))
    # print(len(llm_client.Embedding('你好')))
