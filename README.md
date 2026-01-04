# AnkiField2AI

AnkiField2AI 是一个基于 Python 的自动化工具，旨在通过 AI（如 DeepSeek）为 Anki 卡片提供强大的“智能字段补全”能力。

## 📖 项目简介

我比较喜欢使用Saladict（沙拉查词）插件记录单词，它支持通过 AnkiConnect 将查词结果同步到 Anki，但默认字段内容较为基础（通常仅包含单词、上下文与翻译）。

**AnkiField2AI** 在此基础上实现了“字段 → AI → 字段”的智能闭环：
- **语境感知**：它会读取你卡片里的上下文（Context），让 AI 给出在该语境下的精确解释。
- **字段自由**：你可以定义任何你想要的字段（如：词根词缀、雅思考点、例句），只需修改 Prompt。
- **全自动化**：每天积攒的几十个生词，一键运行，全部自动补全。

通过本项目，你可以摆脱手动编辑卡片的繁琐流程，构建更系统、更个性化的词汇学习体系。

> [!WARNING]
> **注意**：目前功能尚处于开发阶段，代码结构主要用于学习参考，不推荐在正式生产环境（核心笔记库）中使用，也不推荐普通 Anki 学习者使用。

---

## ✨ 核心功能

- **智能增量更新**：自动检测已有内容的卡片并跳过，仅处理新加入或未完善的卡片。
- **上下文感知**：AI 会结合卡片中的 `Context` 字段提供精准的语义解析，而非死板的字典释义。
- **结构化输出**：强制 AI 输出 JSON 格式，确保数据准确填入 `MeaningStats`、`Synonyms`、`GrammarNote` 等自定义字段。
- **模块化设计**：代码分为通讯、AI 处理、工具函数及 AnkiConnect 通信模块，方便二次开发。

---

## 🛠️ 环境准备（必读）

1. **Anki**: 确保 Anki 处于运行状态。
2. **AnkiConnect 插件**: 在 Anki 中安装 [AnkiConnect](https://ankiweb.net/shared/info/2055492159) 插件。
3. **Python 环境**: Python 3.8+。
4. **API Key**: 拥有 DeepSeek 或兼容 OpenAI 接口协议的 API Key。在.env中手动输入你的API Key。
5. **手动添加字段**：目前需要手动在Anki中添加字段。在 Anki 中点击浏览-》字段-》添加，目前适合的字段有：‘MeaningStats’（上下文含义，并给出常见含义）、‘ExampleSen’（单词例句）、‘Synonyms’（同义词）、‘GrammarNote’（语法解释）。
6. **手动配置牌组名和笔记模板名称**：在.env中手动输入你的牌组和笔记模板名称。在 Anki 中点击添加即可看到。
7. **Python库安装**：请查看requirements.txt。

---

## 🚀 快速开始

### 1. 下载项目
```bash
git clone [https://github.com/你的用户名/AnkiField2AI.git](https://github.com/你的用户名/AnkiField2AI.git)
cd 你存放AnkiField2AI的文件夹
```

### 2. 下载Python库
```bash
pip install -r requirements.txt
```