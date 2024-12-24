import requests
import json

def match_db(query):
    url = 'http://localhost/v1/datasets/70c5288b-ee4c-4224-b6ff-4b0054e998d3/retrieve'
    headers = {
        'Authorization': 'Bearer dataset-yjqJ22vWkInsBnqsqxZ4fnlx',
        'Content-Type': 'application/json'
    }
    data = {
        "query": query,
        "retrieval_model": {
            "search_method": "keyword_search",
            "reranking_enable": False,
            "reranking_mode": None,
            "reranking_model": {
                "reranking_provider_name": "",
                "reranking_model_name": ""
            },
            "weights": None,
            "top_k": 1,
            "score_threshold_enabled": False,
            "score_threshold": None
        }
    }

    data_json = json.dumps(data)
    response = requests.post(url, headers=headers, data=data_json)
    response_data = json.loads(response.content)
    return response_data

if __name__ == '__main__':
    query = "600872的全称、A股简称、法人、法律顾问、会计师事务所及董秘是？"
    response = match_db(query)
    print(response.records[0].segment.content)