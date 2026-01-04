import os
import sys
from dotenv import load_dotenv

load_dotenv()
# Load environment variables from a .env file where main.py is located

class Config:
    """
    全局配置类
    所有配置项作为静态属性直接调用，如 Config.API_KEY
    """
    
    # DeepSeek Environment Variables
    API_KEY = os.getenv("API_KEY")
    BASE_URL = os.getenv("BASE_URL")
    AI_MODEL = os.getenv("AI_MODEL")

    # Anki Connect Environment Variables
    ANKI_CONNECT_URL = os.getenv("ANKI_CONNECT_URL", 'http://localhost:8765')
    DECK_NAME = os.getenv("DECK_NAME")
    NOTE_TYPE = os.getenv("NOTE_TYPE")

    # === 验证逻辑 (安检门) ===
    # 这个方法会在文件被 import 时自动被定义，在文件内被调用
    @classmethod
    def validate(cls):
        """检查必须的配置项是否存在，不存在就报错"""
        missing_keys = []
        
        if not cls.API_KEY:
            missing_keys.append("DEEPSEEK_API_KEY")
        if not cls.DECK_NAME:
            missing_keys.append("DECK_NAME")
        if not cls.NOTE_TYPE:
            missing_keys.append("NOTE_TYPE")
            
        if missing_keys:
            error_msg = f"❌ 严重错误：配置文件 .env 中缺少以下必须项：{', '.join(missing_keys)}"
            # 直接打印并退出，比抛出异常更直观
            print(f"\n{'!'*60}")
            print(error_msg)
            print("请检查项目根目录下的 .env 文件是否填写正确！")
            print(f"{'!'*60}\n")
            sys.exit(1)

        print("✅ 配置文件验证通过，AI_API和Anki_Connect均已设置。")

# === 在文件末尾直接执行验证 ===
# 这样一旦别的脚本 'import config'，就会自动检查配置
Config.validate()