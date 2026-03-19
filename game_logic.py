import random
from memory import Memory
from api_client import call_llm, mock_call
import json

# 加载配置
with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)
GAME_CONFIG = config['game']
INTERACTION_TIME_INCREMENT = GAME_CONFIG.get('interaction_time_increment', 5)
AGE_INTERVAL = GAME_CONFIG.get('age_interval', 60)

# 120种职业
PROFESSIONS = """
空姐 护士 总裁 服务员 银行职员 女警 教师 律师 医生 程序员
设计师 模特 厨师 导游 会计 秘书 销售 客服 保洁 保安
演员 歌手 作家 画家 运动员 教练 记者 编辑 翻译 心理咨询师
美容师 理发师 摄影师 导演 编剧 主持人 配音员 舞蹈家 音乐家 调酒师
糕点师 西点师 面点师 咖啡师 茶艺师 品酒师 营养师 健身教练 瑜伽教练 舞蹈教练
游泳教练 网球教练 高尔夫教练 滑雪教练 马术教练 赛车手 飞行员 船员 列车员 地铁司机
公交司机 出租车司机 货车司机 叉车司机 起重机司机 挖机司机 矿工 石油工人 电力工人 水暖工
电工 木工 瓦工 油漆工 焊工 钳工 车工 铣工 磨工 铸工
锻工 热处理工 电镀工 装配工 包装工 质检员 化验员 材料员 库管员 采购员
物流专员 报关员 单证员 货代员 外贸员 电商运营 新媒体运营 社群运营 产品经理 项目经理
市场专员 品牌专员 公关专员 广告专员 会展专员 活动策划 文案策划 内容策划 视频剪辑 后期制作
UI设计师 UX设计师 交互设计师 视觉设计师 服装设计师 珠宝设计师 工业设计师 家具设计师 室内设计师 景观设计师
""".split()

# 基础性格倾向（随机分配，但可自定义）
PERSONALITY_OPTIONS = [
    "热情开朗", "温柔体贴", "高冷理智", "活泼可爱", "沉稳内敛",
    "幽默风趣", "严谨认真", "随和友善", "独立坚强", "敏感细腻"
]
PERSONALITY_BY_PROFESSION = {prof: random.choice(PERSONALITY_OPTIONS) for prof in PROFESSIONS}

# 年龄对应的性格修饰语
AGE_MODIFIERS = {
    (18, 25): "青春活力",
    (26, 35): "成熟稳重",
    (36, 50): "知性优雅",
    (51, 65): "温婉慈祥",
    (66, 80): "睿智平和"
}

# 年龄对应的典型着装风格
AGE_CLOTHES_STYLE = {
    (18, 25): "时尚潮流",
    (26, 35): "干练知性",
    (36, 50): "优雅端庄",
    (51, 65): "温婉大方",
    (66, 80): "朴素舒适"
}

STAGES = ["相亲初识", "互有好感", "恋爱中", "订婚", "已婚", "生子"]

# 外貌相关常量
HEIGHT_RANGE = (140, 190)
WEIGHT_RANGE = (40, 90)
HAIR_STYLES = ["长发", "短发", "卷发", "直发", "马尾", "丸子头", "波波头", "大波浪", "脏辫", "盘发"]
FACE_SHAPES = ["鹅蛋脸", "圆脸", "方脸", "长脸", "瓜子脸", "心形脸", "菱形脸", "梨形脸"]

def random_name():
    first = ["张", "王", "李", "刘", "陈", "杨", "赵", "黄", "周", "吴", "徐", "孙", "马", "朱", "胡"]
    second = ["雨欣", "梓涵", "诗琪", "佳怡", "晓彤", "梦瑶", "静雅", "若曦", "语嫣", "婉清",
              "一诺", "艺涵", "昕怡", "沐晴", "安然", "知意", "南笙", "晚吟", "初雪", "若渝"]
    return random.choice(first) + random.choice(second)

def get_age_range(age):
    for (low, high), val in AGE_MODIFIERS.items():
        if low <= age <= high:
            return (low, high)
    return (18, 25)

def get_personality_with_age(base_personality, age):
    age_range = get_age_range(age)
    modifier = AGE_MODIFIERS[age_range]
    return f"{modifier}的{base_personality}"

def get_clothes_with_age(profession, age):
    style = AGE_CLOTHES_STYLE[get_age_range(age)]
    items = ["连衣裙", "衬衫", "外套", "长裙", "短裙", "牛仔裤", "西装", "运动服", "旗袍", "汉服"]
    colors = ["红色", "蓝色", "白色", "黑色", "粉色", "紫色", "黄色", "绿色", "灰色", "米色"]
    cloth = f"{random.choice(colors)}的{random.choice(items)}"
    return f"{cloth}，风格{style}"

class Girlfriend:
    def __init__(self, profession, age, name=None, height=None, weight=None, hair_style=None, face_shape=None, base_personality=None, use_api=True, api_config=None):
        self.name = name if name else random_name()
        self.profession = profession
        self.age = age
        self.base_personality = base_personality if base_personality else PERSONALITY_BY_PROFESSION[profession]
        self.personality = get_personality_with_age(self.base_personality, age)
        self.clothes = get_clothes_with_age(profession, age)
        
        # 可自定义的身材外貌
        self.height = height if height else random.randint(*HEIGHT_RANGE)
        if weight is None:
            min_weight = int(18.5 * (self.height/100)**2)
            max_weight = int(24 * (self.height/100)**2)
            self.weight = random.randint(min_weight, max_weight)
        else:
            self.weight = weight
        self.hair_style = hair_style if hair_style else random.choice(HAIR_STYLES)
        self.face_shape = face_shape if face_shape else random.choice(FACE_SHAPES)
        
        self.total_interaction_time = 0
        self.affection = 50
        self.stage_index = 0
        self.memory = Memory(max_size=GAME_CONFIG['max_memory'])
        self.use_api = use_api
        self.api_config = api_config  # 用户自定义API配置
        self.memory.add_event("初见", f"你们第一次见面，她穿着{self.clothes}。", 0)
    
    @property
    def stage(self):
        return STAGES[self.stage_index]
    
    def update_stage(self):
        if self.affection >= 90 and self.stage_index < 5:
            self.stage_index = 5
        elif self.affection >= 80 and self.stage_index < 4:
            self.stage_index = 4
        elif self.affection >= 70 and self.stage_index < 3:
            self.stage_index = 3
        elif self.affection >= 60 and self.stage_index < 2:
            self.stage_index = 2
        elif self.affection >= 40 and self.stage_index < 1:
            self.stage_index = 1
    
    def _build_prompt(self, player_action, extra_context=""):
        prompt = f"""你正在扮演一个女友角色，以下是你的基本信息：
- 名字：{self.name}
- 年龄：{self.age}岁
- 身高：{self.height}cm
- 体重：{self.weight}kg
- 发型：{self.hair_style}
- 脸型：{self.face_shape}
- 职业：{self.profession}
- 性格：{self.personality}
- 今日着装：{self.clothes}
- 当前关系阶段：{self.stage}
- 好感度（亲密度）：{self.affection} (0-100)
- 你们累计相处时间：{self.total_interaction_time}分钟

你与玩家的共同记忆（按时间倒序，最近的在前面）：
{self.memory.format_for_prompt()}

现在玩家对你采取了行动：{player_action}
{extra_context}
请根据以上情境，以第一人称“我”的口吻自然、生动地回应玩家，展现你的性格、年龄特点和当前情感。回应要符合关系阶段和好感度。不要出现格式化标记。
"""
        return prompt
    
    def _call_ai(self, player_action, extra_context=""):
        if not self.use_api:
            return mock_call(player_action), "中性"  # 模拟回复默认中性
        
        prompt = self._build_prompt(player_action, extra_context)
        # 在prompt中要求附加情感标签
        prompt += "\n\n请在回复的最后一行单独用格式 [情感:正面/负面/中性] 标明你的情感倾向。"
        
        system = f"你是一个性格{self.personality}的{self.profession}女孩，今年{self.age}岁，名叫{self.name}。请完全沉浸在角色中回应，语气符合年龄特点。"
        response = call_llm(prompt, system, api_config=self.api_config)
        
        # 解析情感标签
        sentiment = "中性"  # 默认
        lines = response.strip().split('\n')
        if lines:
            last_line = lines[-1].strip()
            if last_line.startswith('[情感:') and last_line.endswith(']'):
                sentiment_text = last_line[4:-1]  # 提取正面/负面/中性
                if sentiment_text in ["正面", "负面", "中性"]:
                    sentiment = sentiment_text
                    # 移除最后一行情感标签，只保留对话内容
                    response = '\n'.join(lines[:-1]).strip()
        return response, sentiment
    
    def advance_age(self):
        """年龄增加1岁，更新外貌相关属性"""
        self.age += 1
        self.personality = get_personality_with_age(self.base_personality, self.age)
        self.clothes = get_clothes_with_age(self.profession, self.age)
        # 体重微调
        if self.age < 40:
            change = random.randint(-2, 3)
        elif self.age < 60:
            change = random.randint(0, 4)
        else:
            change = random.randint(-3, 1)
        self.weight = max(40, min(90, self.weight + change))
        # 发型可能变化
        if self.age < 30:
            preferred = ["长发", "卷发", "马尾", "丸子头", "大波浪"]
        elif self.age < 50:
            preferred = ["短发", "卷发", "盘发", "波波头"]
        else:
            preferred = ["短发", "盘发", "直发"]
        if random.random() < 0.3:
            self.hair_style = random.choice(preferred)
    
    def _interact(self, action_func, *args, **kwargs):
        """所有互动包装，增加相处时间并检查年龄增长"""
        result = action_func(*args, **kwargs)
        self.total_interaction_time += INTERACTION_TIME_INCREMENT
        # 检查是否应该增加年龄
        if self.total_interaction_time // AGE_INTERVAL > (self.total_interaction_time - INTERACTION_TIME_INCREMENT) // AGE_INTERVAL:
            self.advance_age()
        return result
    
    def chat(self, player_message=""):
        def _chat():
            player_action = f"和你聊天，说：{player_message if player_message else '（默默看着你）'}"
            response, sentiment = self._call_ai(player_action)
            # 根据情感调整好感度
            change = 0
            if sentiment == "正面":
                change = random.randint(1, 3)
                self.affection += change
            elif sentiment == "负面":
                change = -random.randint(1, 3)
                self.affection = max(0, self.affection + change)
            else:
                change = 0
            self.affection = min(100, self.affection)
            self.memory.add_event("聊天", f"你说：{player_message}\n她回：{response}", change)
            return response
        return self._interact(_chat)
    
    def give_gift(self, gift):
        def _gift():
            player_action = f"送给你一份礼物：{gift}"
            response, sentiment = self._call_ai(player_action)  # 情感标签同样可用，但礼物本身有固定好感度，我们可以选择忽略情感或叠加
            # 礼物基础价值
            gift_value = {"鲜花":5, "巧克力":3, "首饰":10, "书籍":4, "化妆品":6}.get(gift, 2)
            # 情感加成
            if sentiment == "正面":
                gift_value += random.randint(1, 2)
            elif sentiment == "负面":
                gift_value = max(1, gift_value - random.randint(1, 2))
            self.affection += gift_value
            self.affection = min(100, self.affection)
            self.memory.add_event("送礼", f"他送了你{gift}，你{response}", gift_value)
            return response
        return self._interact(_gift)
    
    def date(self, place):
        def _date():
            player_action = f"约你去{place}约会"
            response, sentiment = self._call_ai(player_action)
            effect = {"电影院":3, "餐厅":4, "公园":2, "游乐园":5, "海边":6}.get(place, 1)
            if sentiment == "正面":
                effect += random.randint(1, 2)
            elif sentiment == "负面":
                effect = max(1, effect - random.randint(1, 2))
            self.affection += effect
            self.affection = min(100, self.affection)
            self.memory.add_event("约会", f"你们去了{place}，你{response}", effect)
            return response
        return self._interact(_date)
    
    def quarrel(self, reason=""):
        def _quarrel():
            player_action = f"和你发生了争吵，原因：{reason if reason else '一些小事'}"
            response, sentiment = self._call_ai(player_action, extra_context="这次是负面事件，你可能感到伤心或生气，但不要过度极端。")
            decrease = random.randint(5, 15)
            self.affection = max(0, self.affection - decrease)
            self.memory.add_event("吵架", f"因为{reason}你们吵架了，你{response}", -decrease)
            return response
        return self._interact(_quarrel)
    
    def surprise(self, surprise_type="惊喜"):
        def _surprise():
            player_action = f"为你准备了一个惊喜：{surprise_type}"
            response, sentiment = self._call_ai(player_action, extra_context="你感到非常惊喜和感动。")
            increase = random.randint(8, 20)
            self.affection = min(100, self.affection + increase)
            self.memory.add_event("惊喜", f"他给了你一个{surprise_type}，你{response}", increase)
            return response
        return self._interact(_surprise)
    
    def celebrate_festival(self, festival):
        def _festival():
            player_action = f"和你一起庆祝{festival}"
            response, sentiment = self._call_ai(player_action, extra_context=f"今天是{festival}，你感到很开心。")
            increase = random.randint(5, 15)
            self.affection = min(100, self.affection + increase)
            self.memory.add_event("节日", f"你们一起庆祝{festival}，你{response}", increase)
            return response
        return self._interact(_festival)
    
    def propose(self):
        if self.affection >= 75 and self.stage_index >= 2:
            def _propose():
                player_action = "向你求婚了"
                response, sentiment = self._call_ai(player_action, extra_context="你内心非常感动，但也要符合当前性格。")
                self.affection += 10
                self.stage_index = 3
                self.memory.add_event("求婚", f"他求婚了，你{response}", 10)
                return response
            return self._interact(_propose)
        else:
            return "（她轻轻摇头）我们再多了解彼此一些吧。"
    
    def have_baby(self):
        if self.stage_index >= 4 and self.affection >= 90:
            self.stage_index = 5
            return f"几个月后，你们迎来了爱情的结晶——一个可爱的宝宝。{self.name}看着你和孩子，脸上洋溢着幸福。"
        return None
    
    def to_dict(self):
        return {
            "name": self.name,
            "profession": self.profession,
            "age": self.age,
            "base_personality": self.base_personality,
            "personality": self.personality,
            "clothes": self.clothes,
            "height": self.height,
            "weight": self.weight,
            "hair_style": self.hair_style,
            "face_shape": self.face_shape,
            "total_interaction_time": self.total_interaction_time,
            "affection": self.affection,
            "stage_index": self.stage_index,
            "memory": self.memory.to_dict(),
            "use_api": self.use_api,
            "api_config": self.api_config
        }
    
    @classmethod
    def from_dict(cls, data):
        gf = cls(
            profession=data["profession"],
            age=data["age"],
            name=data["name"],
            height=data["height"],
            weight=data["weight"],
            hair_style=data["hair_style"],
            face_shape=data["face_shape"],
            base_personality=data["base_personality"],
            use_api=data["use_api"],
            api_config=data.get("api_config")
        )
        gf.personality = data["personality"]
        gf.clothes = data["clothes"]
        gf.total_interaction_time = data["total_interaction_time"]
        gf.affection = data["affection"]
        gf.stage_index = data["stage_index"]
        gf.memory = Memory.from_dict(data["memory"])
        return gf
    
    def show_status(self):
        return {
            "name": self.name,
            "age": self.age,
            "height": self.height,
            "weight": self.weight,
            "hair_style": self.hair_style,
            "face_shape": self.face_shape,
            "profession": self.profession,
            "personality": self.personality,
            "clothes": self.clothes,
            "stage": self.stage,
            "affection": self.affection,
            "total_interaction_time": self.total_interaction_time
        }
    
    def rename(self, new_name):
        self.name = new_name
        self.memory.add_event("改名", f"你为她改名为{new_name}", 0)