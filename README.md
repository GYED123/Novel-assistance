# AI Novel Starter (CLI)

一个最小可用的“调用AI帮助写小说”命令行项目。特色：
- 明确的“故事圣经（bible）/大纲（outline）/场景（scenes）”三层结构
- Prompt 模板与代码分离，便于迭代
- 可切换模型提供商（OpenAI 兼容 / 本地 Ollama）
- 中文/日文/英文均可创作

## 快速开始
1. 安装 Python 3.10+，创建虚拟环境：
   ```bash
   python -m venv .venv && source .venv/bin/activate  # Windows 用 .venv\Scripts\activate
   ```
2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
3. 复制环境变量模板：
   ```bash
   cp .env.example .env
   ```
   根据你选择的提供商填写：
   - **OpenAI 兼容**：设置 `OPENAI_API_KEY`（必要），如使用自定义兼容端点（OpenRouter、自建代理等），可设置 `OPENAI_BASE_URL`。
   - **Ollama 本地**：无需 API Key，确保本机 `ollama` 已安装并拉取了模型（如 `llama3.1`）。
4. 运行示例：
   ```bash
   python -m src.main outline --title "双戒之劫" --genres 奇幻 悬疑
   python -m src.main scene --index 1
   python -m src.main critique --file story/scenes/scene_001.md
   ```

## 目录结构
```
ai_novel_starter/
├── .env.example
├── requirements.txt
├── README.md
├── config.yaml
└── src/
    ├── main.py              # Typer CLI 入口
    ├── provider.py          # 模型提供商抽象（OpenAI 兼容 / Ollama）
    ├── io_utils.py          # 读写工具
    ├── prompts/
    │   ├── outline.txt
    │   ├── scene.txt
    │   └── critique.txt
    └── story/
        ├── bible.yaml       # 世界观/人物设定
        ├── outline.yaml     # 章节-节大纲
        └── scenes/          # 场景草稿目录
```

## 工作流建议
1. **建立故事圣经**：完善 `story/bible.yaml`（世界观、人物卡、语气风格）。
2. **生成大纲**：`outline` 子命令根据标题/题材/目标读者等生成多层级大纲，可多轮“再生成/合并/修改”。
3. **扩写场景**：`scene` 子命令按大纲的章节/小节编号生成场景草稿。
4. **自我批评**：`critique` 子命令让模型从节奏、人物弧线、逻辑连贯性等角度提改进意见。
5. **迭代**：手动编辑草稿 + 追加 `scene`/`critique` 循环，逐步打磨。

## 切换模型
在 `.env` 或环境变量中设置：
- `PROVIDER=openai` 与 `MODEL=gpt-4o-mini`（示例）
- `PROVIDER=ollama` 与 `MODEL=llama3.1`

你也可以扩展 `provider.py` 接入 Claude、DeepSeek 等 OpenAI 兼容端点。

## 提示工程 Tips
- 在 `prompts/` 中分离模板；通过 `{placeholders}` 注入故事圣经、目标语气、读者群像等结构化信息。
- 为不同阶段使用不同温度：大纲/脑暴用较高温度（0.8），铺写/润色降温（0.3~0.5）。
- 使用“约束清单”（风格、禁用词、叙事人称、时态）保持一致性。

## 法律与道德
- 尊重版权，避免未经授权的风格复制。
- 生成内容需自行审阅并承担使用责任。
