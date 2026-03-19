import requests
import json

def load_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def call_llm(prompt, system_prompt="你是一个温柔体贴的女友，请根据情境自然回应。", api_config=None):
    """调用大语言模型生成回复，可传入自定义api_config覆盖全局配置"""
    if api_config is None:
        config = load_config()
        api_config = config['api']
    else:
        # 确保必要字段存在，缺失则从全局配置补全
        config = load_config()
        default_api = config['api']
        for key in default_api:
            if key not in api_config:
                api_config[key] = default_api[key]
    
    headers = {
        "Authorization": f"Bearer {api_config['api_key']}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": api_config.get('model', 'deepseek-chat'),
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "temperature": api_config.get('temperature', 0.8),
        "max_tokens": api_config.get('max_tokens', 200)
    }
    
    try:
        response = requests.post(api_config.get('base_url', 'https://api.deepseek.com/v1/chat/completions'), 
                                 headers=headers, json=data, timeout=30)
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content']
    except Exception as e:
        print(f"API调用失败: {e}")
        return "（AI暂时无法连接，请稍后再试）"

def mock_call(prompt):
    return "（模拟女友回应）嗯，我明白了。"