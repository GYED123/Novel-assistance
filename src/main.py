from __future__ import annotations
import os, sys, json, typer
from typing import List, Optional
from dotenv import load_dotenv
from rich import print
from pydantic import BaseModel
import yaml

from .provider import LLMProvider
from .io_utils import load_yaml, dump_yaml, read_prompt, next_scene_path, STORY_DIR

app = typer.Typer(no_args_is_help=True, add_completion=False)

class Cfg(BaseModel):
    provider: str = os.getenv("PROVIDER", "openai")
    model: str = os.getenv("MODEL", "gpt-4o-mini")
    language: str = "zh"
    temperature_outline: float = 0.8
    temperature_scene: float = 0.5
    temperature_critique: float = 0.3
    max_output_tokens: int = 1200

def get_cfg() -> Cfg:
    # 支持从 config.yaml 读取默认值
    cfg = Cfg()
    cfg_path = os.path.join(os.path.dirname(__file__), "..", "config.yaml")
    cfg_path = os.path.abspath(cfg_path)
    try:
        with open(cfg_path, "r", encoding="utf-8") as f:
            import re, os
            text = f.read()
            # 环境变量替换
            for k, v in os.environ.items():
                text = text.replace(f"${{{k}}}", v)
            data = yaml.safe_load(text) or {}
            for k, v in data.items():
                if hasattr(cfg, k):
                    setattr(cfg, k, v)
    except FileNotFoundError:
        pass
    return cfg

def build_messages(system_prompt: str, user_content: str):
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content},
    ]

@app.command()
def outline(
    title: str = typer.Option(..., help="作品标题"),
    genres: List[str] = typer.Option([], help="题材/风格标签，可多选"),
    audience: str = typer.Option("大众读者", help="目标读者"),
    length: str = typer.Option("中篇", help="篇幅：短篇/中篇/长篇"),
    language: str = typer.Option(None, help="输出语言（默认跟随 config.yaml）"),
):
    """生成/重写 章节-小节 多层级大纲。"""
    load_dotenv()
    cfg = get_cfg()
    if language: cfg.language = language
    provider = LLMProvider(cfg.model, cfg.provider)

    bible = load_yaml(STORY_DIR / "bible.yaml")
    sys_prompt = read_prompt("outline")
    user_req = json.dumps({
        "title": title,
        "genres": genres,
        "audience": audience,
        "length": length,
        "language": cfg.language,
        "bible": bible
    }, ensure_ascii=False, indent=2)

    out = provider.completion(
        messages=build_messages(sys_prompt, user_req),
        temperature=cfg.temperature_outline,
        max_tokens=cfg.max_output_tokens
    )
    # 将模型返回解析为 YAML 结构（若失败则原文落盘）
    try:
        data = yaml.safe_load(out)
        if isinstance(data, dict):
            dump_yaml(STORY_DIR / "outline.yaml", data)
            print("[green]✓ 已生成大纲到 story/outline.yaml[/green]")
        else:
            raise ValueError("not a dict")
    except Exception:
        with open(STORY_DIR / "outline.yaml", "w", encoding="utf-8") as f:
            f.write("# 模型未返回合法 YAML，以下为原始内容：\n")
            f.write(out)
        print("[yellow]! 大纲未解析为 YAML，已原文保存到 story/outline.yaml[/yellow]")

@app.command()
def scene(
    index: Optional[int] = typer.Option(None, help="场景索引（默认自动递增）"),
    chapter: Optional[str] = typer.Option(None, help="可指定章节名或编号"),
    section: Optional[str] = typer.Option(None, help="可指定小节名或编号"),
    language: str = typer.Option(None, help="输出语言（默认跟随 config.yaml）"),
):
    """根据大纲扩写单个场景到 markdown。"""
    from .io_utils import STORY_DIR
    load_dotenv()
    cfg = get_cfg()
    if language: cfg.language = language
    provider = LLMProvider(cfg.model, cfg.provider)

    bible = load_yaml(STORY_DIR / "bible.yaml")
    outline = load_yaml(STORY_DIR / "outline.yaml")
    sys_prompt = read_prompt("scene")
    user_req = yaml.safe_dump({
        "language": cfg.language,
        "bible": bible,
        "outline": outline,
        "target": {"chapter": chapter, "section": section}
    }, allow_unicode=True, sort_keys=False)

    out = provider.completion(
        messages=build_messages(sys_prompt, user_req),
        temperature=cfg.temperature_scene,
        max_tokens=cfg.max_output_tokens
    )
    path = next_scene_path(index)
    with open(path, "w", encoding="utf-8") as f:
        f.write(out)
    print(f"[green]✓ 场景已生成：{path}[/green]")

@app.command()
def critique(
    file: str = typer.Option(..., help="要批评/诊断的 markdown 文件"),
    focus: List[str] = typer.Option([], help="关注点：如 节奏 人设 弧线 逻辑 设定一致性 文风 读者画像"),
    language: str = typer.Option(None, help="输出语言（默认跟随 config.yaml）"),
):
    """对某个场景或章节进行“编辑点评 + 修改建议 + 具体重写片段”。"""
    load_dotenv()
    cfg = get_cfg()
    if language: cfg.language = language
    provider = LLMProvider(cfg.model, cfg.provider)

    with open(file, "r", encoding="utf-8") as f:
        text = f.read()

    bible = load_yaml(STORY_DIR / "bible.yaml")
    sys_prompt = read_prompt("critique")
    user_req = yaml.safe_dump({
        "language": cfg.language,
        "focus": focus,
        "bible": bible,
        "draft": text
    }, allow_unicode=True, sort_keys=False)

    out = provider.completion(
        messages=build_messages(sys_prompt, user_req),
        temperature=cfg.temperature_critique,
        max_tokens=cfg.max_output_tokens
    )
    print(out)

if __name__ == "__main__":
    app()
