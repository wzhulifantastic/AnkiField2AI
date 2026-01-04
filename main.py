# PythonFilename: anki_ai_fields_update_v3.0_31Dec2025.py

import logging
from config import Config
from src.utils import setup_logging
from src.anki_client import fetch_note_ids, fetch_note_info, update_note_fields
from src.ai_client import analyze_text_with_ai

def main():
    """主程序入口"""
    log_file_path = setup_logging()

    print(f"\n{'='*60}")
    print(f"🔥 脚本启动 (v3.0正式运行版) | 日志: {log_file_path}")
    print(f"🎯 目标牌组: {Config.DECK_NAME}")
    print(f"{'='*60}\n")
    logging.info("=== 脚本启动 (智能增量模式) ===")

    note_ids = fetch_note_ids()
    # 1. 获取noteID列表
    if not note_ids:
            print("🤷‍♂️ 未找到任何卡片。")
            return
        
    # 2. 获取详情
    notes_details = fetch_note_info(note_ids)
    # 是一个列表，里面每个元素是一个 note 的详情字典
    if not notes_details:
        print("❌ 获取卡片详情失败。")
        return

    total_count = len(notes_details)
    success_count = 0
    fail_count = 0
    skip_count = 0

    print(f"📊 共加载 {total_count} 张卡片，准备开始处理...\n")

    # 3. 循环处理 （跳过已有4项字段的note）
    for index, note in enumerate(notes_details):
        # 进度前缀
        progress_prefix = f"[{index+1}/{total_count}]"

        # 提取字段
        note_id = note.get("noteId")
        fields = note.get("fields", {})
        
        text = fields.get("Text", {}).get("value", "").strip()
        context = fields.get("Context", {}).get("value", "").strip()
        
        mean_stats = fields.get("MeaningStats", {}).get("value", "").strip()
        synonyms = fields.get("Synonyms", {}).get("value", "").strip()
        gram_note = fields.get("GrammarNote", {}).get("value", "").strip()
        exam_sen = fields.get("ExampleSen", {}).get("value", "").strip()
        
        if not text or not context:
        # 即使是全量更新，空数据也没法跑，所以这个检查必须留着
            logging.warning(f"⚠️ 跳过 (数据缺失): ID={note_id} | 单词: '{text}'")
            print(f"{progress_prefix} ⚠️ 跳过: 单词或例句为空: ID={note_id} | 单词: '{text}'")
            continue
        
        if mean_stats and synonyms and gram_note and exam_sen:
            logging.info(f"⏭️ 跳过 (已存在数据): ID={note_id} | 单词: '{text}'")
            print(f"{progress_prefix} ⏭️ 跳过: 已有 AI 数据: ID={note_id} | 单词: '{text}'")
            skip_count += 1
            continue

        # A. 呼叫 AI
        print(f"{progress_prefix} 🤖 AI正在思考: '{text}'...", end="", flush=True)
        
        ai_json_data = analyze_text_with_ai(text, context)
        
        if not ai_json_data:
            print(" ❌ 失败 (AI无响应)")
            fail_count += 1
            continue
            
        # B. 强制写入 Anki
        # 将 word 传给 update 函数，保证日志里能看到它
        if update_note_fields(note_id, ai_json_data, text):
            print(" ✨ 写入成功！")
            success_count += 1
        else:
            print(" ❌ 写入失败")
            fail_count += 1

    # 4. 汇总结果
    print(f"\n{'='*60}")
    print(f"🎉 任务完成！")
    print(f"✅ 成功补全: {success_count}")
    print(f"⏭️ 跳过处理: {skip_count}")
    print(f"❌ 失败数量: {fail_count}")
    print(f"{'='*60}")
    logging.info(f"=== 任务结束: 成功 {success_count} / 跳过 {skip_count} / 失败 {fail_count} / 总计 {total_count} ===")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(f"程序异常终止：{e}")
        print(f"❌ 程序发生错误：{e}")