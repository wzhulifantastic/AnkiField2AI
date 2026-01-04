import requests
import json
import logging

# 从项目根目录的 config.py 导入配置类
# 注意：这里能导入是因为你最终是在根目录运行 main.py
from config import Config

def send_anki_request(action, params=None):
    """
    通用函数：向 AnkiConnect 发送请求。
    """
    if params is None: # 每次函数被调用时，检测到是 None，就在函数内部现场新建一个 {}。必须那么写，否则容易出错。如果在定义时把params默认值写成 {}，会导致每一次调用时重复使用同一个字典,不停在这一个字典里修改数据。
        params = {}
        
    payload_to_anki = {
            "action": action, # :param action: AnkiConnect 的指令名称（如 "findNotes", "updateNoteFields"）
            "version": 6, # 指定 AnkiConnect 版本号
            "params": params # :param params: 指令对应的参数字典
        }

    # 记录发送给anki的json字典里是什么内容？debug级别最低，要在utils.py内logging.basicConfig(level=logging.DEBUG)才会生效
    logging.debug(f"正在发送数据至AnkiConnect: \n{json.dumps(payload_to_anki, indent=4, ensure_ascii=False)}") 

    try:
        response_object = requests.post(Config.ANKI_CONNECT_URL, json=payload_to_anki) # post()使用 json=传参。post()不只有发送给某个url，还有返回的对象，这个对象隶属于Response。
        request_result = response_object.json() # 将返回的json字符串转换成 Python 字典并返回。继承自 requests.Response 类的对象可以用 json() 方法
        
        # :return: Anki 返回的 json 结果。如果连接失败，返回空字典 {} 以防止程序崩溃。
        return request_result

    except requests.exceptions.ConnectionError:
            # 如果 Anki 没开，或者端口不对，会走到这里
            logging.error("❌ 无法连接到 Anki！请检查 Anki 是否已打开，且 AnkiConnect 插件正常运行。")
            # 返回一个空字典，让后面的代码能通过 if 判断来处理错误，而不是直接红字报错退出
            return {}
        
    except Exception as e:
            # 捕获其他未知的杂七杂八的错误
            logging.error(f"❌ Anki 请求发生未知错误: {e}")
            return {}

def fetch_note_ids():
    """根据全局变量 DECK_NAME，去 Anki 查获取符合条件的Note的ID列表。
    一个 Note 可以生成正反两张 Card。这两张卡片其实都指向同一个单词。所以应该查 note。"""
    query_str = f'deck:"{Config.DECK_NAME}"'  # 构造查询语句，f-string 格式化字符串， Config.DECK_NAME传入时没有引号，要手动加上引号
    logging.info(f"🔍 [1/3] 正在查询 Anki 牌组: {Config.DECK_NAME}")
    
    request_result = send_anki_request("findNotes", {"query": query_str})
    
    logging.info(f"Anki 返回数据: \n{json.dumps(request_result, indent=4, ensure_ascii=False)}")
    
    note_ids = request_result.get("result", []) # .get() 是 Python 字典（dict）的一个安全访问方法，用于获取字典中指定键的值，如果键不存在则返回默认值（而不是抛出异常）。如果用request_result["result"]，当"result"键不存在时会报错。
    return note_ids

def fetch_note_info(note_ids):
    """根据 note_id 列表，获取这些 Note 的详细内容， 得到一个列表，包括字段和内容。"""
    if not note_ids: # 如果 note_ids 是“None, [], 0, False”，就执行下面的代码。if X: → 当 X 为 True 时执行；if not X: → 当 X 为 False 时执行
        logging.warning("⚠️ 没有收到 ID 列表，跳过获取详情步骤。")
        # 如果没有 ID，直接把请求拦截下来，别发网络请求, 否则api可能报错
        return []
    
    logging.info(f"📄 [2/3] 正在获取 {len(note_ids)} 张卡片的详细内容...")
    request_result = send_anki_request("notesInfo", {"notes": note_ids})
    # Action: notesInfo (注意是复数 s)
    # Params: {"notes": [...]}
    note_info = request_result.get("result") or []
    # 比("result", [])的写法更好，所有假值（None, [], 0, False）都会被替换成 []
    
    if not note_info:
        logging.warning("⚠️ 注意：提供了 NoteID 但Anki 返回的 'result' 字段为空。这通常意味着卡片已被删除。")
    
    if len(note_info) > 0:
    # 只要列表里有东西，就打印第一个看看样子
        logging.info(f"打印第一张卡片的详情样本: \n{json.dumps(note_info[0], indent=4, ensure_ascii=False)}")

    return note_info

def update_note_fields(note_id, ai_json_data, text = "Unknown"):
    """
    将 AI 生成的 JSON 数据写入 Anki 的对应字段。
    
    :param note_id: 笔记 ID
    :param ai_data: AI 返回的字典，包含 MeaningStats, Synonyms, GrammarNote, ExampleSen
    """
    
    # 1. 构造字段映射
    # 左边是 Anki 里的字段名（必须一字不差），右边是 AI 字典里的键名
    fields_payload = {
        "MeaningStats": ai_json_data.get("MeaningStats", ""),
        "Synonyms":     ai_json_data.get("Synonyms", ""),
        "GrammarNote":  ai_json_data.get("GrammarNote", ""),
        "ExampleSen":   ai_json_data.get("ExampleSen", "")  # 新增的例句字段
    }
    
    # 2. 构造请求包
    payload = {
        "note": {
            "id": note_id,
            "fields": fields_payload
        }
    }
    
    # 3. 发送请求 (直接在main()里剥壳传进来的 text 变量)
    logging.info(f"💾 正在写入 Anki (ID={note_id}) | 单词: {text} ...")
    requests_result = send_anki_request("updateNoteFields", payload)
    
    # 4. 结果校验
    # updateNoteFields 成功时，AnkiConnect 返回的 'error' 应该是 None
    if requests_result.get("error"):
        logging.error(f"❌ 更新失败 (ID={note_id}) | 单词: {text} ...: {requests_result.get('error')}")
        return False
    
    # 如果没有 error，说明成功
    logging.info(f"✅ 成功更新 note_id={note_id}")
    return True