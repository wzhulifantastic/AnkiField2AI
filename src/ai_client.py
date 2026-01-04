from openai import OpenAI
from config import Config
import logging
import json

# 初始化客户端 (因为 DeepSeek 兼容 OpenAI 的 SDK,这一步是创建了一个 SDK 客户端，后面client.chat.completions.create()调用时用它发请求)
client = OpenAI(
    api_key=Config.API_KEY, 
    base_url=Config.BASE_URL
    )

def analyze_text_with_ai(text, context = ""):
    """调用 DeepSeek 生成：深度含义解析(含占比)、同义词辨析、核心语法、[新增]例句。"""
    ai_prompt = f"""你是一个雅思8分以上水平的专业英语助教，只被允许输出 JSON 数据的后端 API。你的任务是分析输入的【单词】和【上下文例句】，返回一个纯 JSON 字符串。
    
    【核心指令】
    1. 格式：只输出一个纯 JSON 字符串。严禁输出 Markdown 标记（如 ```json），严禁输出“好的”、“以下是单词的常见用法...”等废话。
    2. 键名：JSON 必须包含以下四个键： 
        - "MeaningStats", 
        - "Synonyms", 
        - "GrammarNote", 
        - "ExampleSen"。
    3. 内容要求：
        - 风格专业、简练，适合雅思6分以上的高水平学习者。
        - 各字段内容详实、有深度，避免空洞和泛泛而谈。
        - 例句必须实用且贴近生活，确保自然流畅。
    
    【通用排版规则】
    1. 强制列表格式：涉及列表时，每个不同内容必须使用阿拉伯数字+点+空格"1. ", "2. "作为序号。
    2. 换行规则：JSON 值内部的所有换行必须使用 HTML 标签 <br>。严禁使用 \\n。
    3. 强调规则：关键词请使用 <b>...</b> 标签加粗。
    
    
    【字段详细要求】
    【MeaningStats - 含义与占比】
    - 结构要求：
        1. 首先解释该单词在原句中的具体含义。
        2. 然后列出该单词在英语中 3 个最常见的含义/用法，并预估该单词/词组在所有的使用方法中这种用法的占比(%)（三种用法的%按实际情况给出，总和不必须为100%）。
    - 格式示例：
        原句含义：<i>你的对句子内容的简要解释和补充说明</i><br>。（原句含义中涉及到原词的部分用 <b></b>加粗。）
        常见用法分布：<br>
        1. <b>[60%]</b> 含义A：解释...<br>
        2. <b>[30%]</b> 含义B：解释...<br>
        3. <b>[10%]</b> 含义C：解释...
        （其中关键词，关键含义用 <b>加粗</b>。）
    
    【Synonyms - 同义词辨析】
    - 列出 3-5 个在该语境下可替换的近义词。
    - 核心要求：必须进行“辨析”。说明为什么要用原词而不用这个词（如语气更强、更正式、褒贬色彩等）。
    - 关键词，关键含义，关键信息用 <b>加粗</b>。
    - 格式示例：
        1. <b>WordA</b>：含义...，但原词语气更强。<br>
        2. <b>WordB</b>：含义...，但不如原词正式。<br>
    
    【GrammarNote - 语法笔记】
    - 分析原句用了哪些关键语法点、句型结构或搭配。
    - 限制：最多只列出核心的 3 个点。
    - 如果原句很简单，没有复杂语法，则说明该词在句中做什么成分（如“作定语修饰xxx”）。
    - 关键语法结构加粗，如： <b>被动语态</b>， <b>虚拟语气</b>， <b>主系表结构</b>, <b>xxx引导的定语从句</b>。
    - 关键内容加粗，如：其中 <b>"to stave off" 为不定式</b>，<b>"ageing" 作宾语</b>。
    
    【ExampleSen - 实用例句】
    - 生成 3 个中英文对照的实用例句（涵盖不同场景/时态）。
    - 英文部分用 <i>斜体</i>。
    - 单词本体（或变体）用 <b>加粗</b>。
    - 示例句子中中文对应的原单词部分用<b>加粗</b>。
    - 格式要求：每组例句之间用 <br> 换行。
    - 格式示例：
        1. <i>This is a <b>sample</b> sentence.</i> 这是一个<b>示例</b>句子。<br>
        2. <i>Another <b>sample</b> here.</i> 这里是另一个<b>示例</b>。
"""
    user_prompt = f"""
    单词/短语: {text}
    上下文例句: {context}
    """
    
    logging.info(f"🤖 正在调用 AI 分析单词: {text} ...")
    
    try:
    # 调用 DeepSeek (client 已经在最上面初始化过了)
        messages_to_ai = client.chat.completions.create(
            model=Config.AI_MODEL,
            messages=[
            {"role": "system", "content": ai_prompt},
            {"role": "user", "content": user_prompt},
        ],
            temperature=0.1, 
            response_format={ "type": "json_object" }
            )
        # 为 deep seek 发起请求
        
        ai_response = messages_to_ai.choices[0].message.content
        # 接收从 deep seek 返回的信息
        
        ai_json_data = json.loads(ai_response) # 把 JSON 字符串转换成 Python 字典
        return ai_json_data
    
    except json.JSONDecodeError:
        logging.error(f"❌ AI 返回的不是有效 JSON，解析失败。返回内容: {ai_response}")
        return None
    
    except Exception as e:
        logging.error(f"❌ AI 分析单词时发生错误: {e}")
        return None
