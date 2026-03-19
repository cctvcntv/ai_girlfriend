from flask import Flask, render_template, request, jsonify, session
from game_logic import Girlfriend, PROFESSIONS, HAIR_STYLES, FACE_SHAPES, PERSONALITY_OPTIONS, HEIGHT_RANGE, WEIGHT_RANGE
import secrets
import json
import os
import threading
import time

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# 存储女友对象的内存字典
girlfriend_sessions = {}

# 保存目录
SAVE_DIR = 'saves'
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

def save_girlfriend(user_id):
    """保存女友数据到文件"""
    gf = girlfriend_sessions.get(user_id)
    if not gf:
        return
    file_path = os.path.join(SAVE_DIR, f"{user_id}.json")
    data = gf.to_dict()
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_girlfriend(user_id):
    """从文件加载女友数据"""
    file_path = os.path.join(SAVE_DIR, f"{user_id}.json")
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            gf = Girlfriend.from_dict(data)
            girlfriend_sessions[user_id] = gf
            return gf
        except Exception as e:
            print(f"加载失败 {user_id}: {e}")
    return None

@app.before_request
def before_request():
    """在请求前确保用户有session，并尝试加载女友"""
    if 'user_id' not in session:
        session['user_id'] = secrets.token_urlsafe(16)
    user_id = session['user_id']
    if user_id not in girlfriend_sessions:
        load_girlfriend(user_id)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/professions')
def get_professions():
    return jsonify(PROFESSIONS)

@app.route('/api/constants')
def get_constants():
    return jsonify({
        "hair_styles": HAIR_STYLES,
        "face_shapes": FACE_SHAPES,
        "personality_options": PERSONALITY_OPTIONS,
        "height_range": HEIGHT_RANGE,
        "weight_range": WEIGHT_RANGE
    })

@app.route('/api/create', methods=['POST'])
def create_girlfriend():
    data = request.get_json()
    profession = data.get('profession')
    age = data.get('age')
    name = data.get('name')
    height = data.get('height')
    weight = data.get('weight')
    hair_style = data.get('hair_style')
    face_shape = data.get('face_shape')
    base_personality = data.get('base_personality')
    use_api = data.get('use_api', True)
    api_config = data.get('api_config')
    
    gf = Girlfriend(
        profession=profession,
        age=age,
        name=name,
        height=height,
        weight=weight,
        hair_style=hair_style,
        face_shape=face_shape,
        base_personality=base_personality,
        use_api=use_api,
        api_config=api_config
    )
    
    user_id = session.get('user_id')
    girlfriend_sessions[user_id] = gf
    save_girlfriend(user_id)  # 立即保存
    
    return jsonify({"success": True, "status": gf.show_status()})

@app.route('/api/status', methods=['GET'])
def get_status():
    user_id = session.get('user_id')
    gf = girlfriend_sessions.get(user_id)
    if not gf:
        return jsonify({"error": "No girlfriend found"}), 404
    return jsonify(gf.show_status())

@app.route('/api/rename', methods=['POST'])
def rename():
    data = request.get_json()
    new_name = data.get('new_name')
    user_id = session.get('user_id')
    gf = girlfriend_sessions.get(user_id)
    if not gf:
        return jsonify({"error": "No girlfriend found"}), 404
    gf.rename(new_name)
    save_girlfriend(user_id)
    return jsonify({"success": True, "status": gf.show_status()})

@app.route('/api/settings', methods=['GET', 'POST'])
def settings():
    user_id = session.get('user_id')
    gf = girlfriend_sessions.get(user_id)
    if not gf:
        return jsonify({"error": "No girlfriend found"}), 404
    
    if request.method == 'GET':
        if gf.api_config:
            config = gf.api_config.copy()
            if 'api_key' in config:
                config['api_key'] = '********'
        else:
            with open('config.json', 'r', encoding='utf-8') as f:
                global_config = json.load(f)['api']
            config = global_config.copy()
            config['api_key'] = '********'
        return jsonify(config)
    else:
        data = request.get_json()
        new_config = data.get('api_config', {})
        current_config = gf.api_config if gf.api_config else {}
        merged = current_config.copy()
        for key, value in new_config.items():
            if key == 'api_key' and (value == '' or value == '********'):
                continue
            merged[key] = value
        gf.api_config = merged
        save_girlfriend(user_id)
        return jsonify({"success": True})

@app.route('/api/test_connection', methods=['POST'])
def test_connection():
    data = request.get_json()
    api_config = data.get('api_config', {})
    with open('config.json', 'r', encoding='utf-8') as f:
        default_config = json.load(f)['api']
    test_config = default_config.copy()
    test_config.update(api_config)
    
    try:
        from api_client import call_llm
        response = call_llm(
            prompt="请回复一个简短的问候语，只需要说'连接成功'即可。",
            system_prompt="你是一个AI助手。",
            api_config=test_config
        )
        return jsonify({"success": True, "message": response})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/save', methods=['POST'])
def save():
    """前端定时调用保存"""
    user_id = session.get('user_id')
    if not user_id or user_id not in girlfriend_sessions:
        return jsonify({"error": "No girlfriend"}), 404
    save_girlfriend(user_id)
    return jsonify({"success": True})

@app.route('/api/reset', methods=['POST'])
def reset():
    """重新相亲：删除当前用户的数据并返回成功"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "No session"}), 400
    # 从内存删除
    if user_id in girlfriend_sessions:
        del girlfriend_sessions[user_id]
    # 删除文件
    file_path = os.path.join(SAVE_DIR, f"{user_id}.json")
    if os.path.exists(file_path):
        os.remove(file_path)
    return jsonify({"success": True})

@app.route('/api/action', methods=['POST'])
def action():
    data = request.get_json()
    action_type = data.get('action')
    params = data.get('params', {})
    
    user_id = session.get('user_id')
    gf = girlfriend_sessions.get(user_id)
    if not gf:
        return jsonify({"error": "No girlfriend found"}), 404
    
    try:
        if action_type == 'chat':
            msg = params.get('message', '')
            response = gf.chat(msg)
        elif action_type == 'gift':
            gift = params.get('gift')
            response = gf.give_gift(gift)
        elif action_type == 'date':
            place = params.get('place')
            response = gf.date(place)
        elif action_type == 'quarrel':
            reason = params.get('reason', '')
            response = gf.quarrel(reason)
        elif action_type == 'surprise':
            surprise_type = params.get('surprise_type', '惊喜')
            response = gf.surprise(surprise_type)
        elif action_type == 'festival':
            festival = params.get('festival', '节日')
            response = gf.celebrate_festival(festival)
        elif action_type == 'propose':
            response = gf.propose()
        else:
            return jsonify({"error": "Unknown action"}), 400
        
        baby_msg = gf.have_baby()
        # 保存（也可由前端定时保存，但这里也存一次确保数据安全）
        save_girlfriend(user_id)
        
        if baby_msg:
            return jsonify({
                "success": True,
                "response": response,
                "baby_event": baby_msg,
                "status": gf.show_status()
            })
        
        return jsonify({
            "success": True,
            "response": response,
            "status": gf.show_status()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    from waitress import serve
    print("Starting server on http://0.0.0.0:8080")
    serve(app, host='0.0.0.0', port=8080)