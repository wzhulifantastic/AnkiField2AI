import os
import sys
import logging

def setup_logging():
    """设置全局日志记录配置"""
    # 1. 强行纠正 Windows 终端编码，防止 Emoji 报错
    sys.stdout.reconfigure(encoding='utf-8')

    # 2. 动态获取日志文件路径 (放在项目根目录下)
    # 获取当前文件 (src/utils.py) 的上一级 (src) 的上一级 (根目录)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(current_dir)
    log_file_path = os.path.join(root_dir, "anki_ai_analysis_log.txt")

    # 3. 配置日志格式
    log_format = (
    "%(asctime)s - "           # 时间
    "%(levelname)s - \n"       # 日志级别
    "   [%(filename)s:%(lineno)d] - \n"  # 文件名和行号
    "   %(message)s\n"              # 消息内容
    )

    date_format = "%d %b %Y %H:%M:%S"

    # 4. 设置 logging
    logging.basicConfig(
    filename = log_file_path,
    level = logging.INFO,
    format = log_format,
    encoding = "utf-8",
    datefmt = date_format
    )

    # 返回路径，方便在 main.py 里打印出来给用户看
    return log_file_path