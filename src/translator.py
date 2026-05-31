"""
翻译模块
使用 deep-translator 库（Google 翻译后端）实现英译中
"""

import logging
import re
from typing import Optional

from deep_translator import GoogleTranslator

logger = logging.getLogger(__name__)

# 翻译器单例
_translator: Optional[GoogleTranslator] = None


def _get_translator() -> GoogleTranslator:
    """获取翻译器实例（懒加载）"""
    global _translator
    if _translator is None:
        _translator = GoogleTranslator(source="auto", target="zh-CN")
    return _translator


def translate_text(text: str) -> str:
    """
    将文本翻译为中文
    失败时返回原文 + 错误标记
    """
    if not text or not text.strip():
        return ""

    # 如果已经主要是中文，跳过
    chinese_chars = len(re.findall(r"[\u4e00-\u9fff]", text))
    total_chars = len(text.strip())
    if total_chars > 0 and chinese_chars / total_chars > 0.5:
        return text

    try:
        translator = _get_translator()
        # deep-translator 有 5000 字符限制，分段处理
        if len(text) <= 4000:
            result = translator.translate(text)
            return result if result else f"[翻译失败] {text}"
        else:
            # 长文本分段翻译
            sentences = re.split(r"(?<=[.!?\n])\s+", text)
            chunks = []
            current = ""
            for sentence in sentences:
                if len(current) + len(sentence) < 4000:
                    current += " " + sentence
                else:
                    if current:
                        chunks.append(current.strip())
                    current = sentence
            if current:
                chunks.append(current.strip())

            translated_chunks = []
            for chunk in chunks:
                try:
                    result = translator.translate(chunk)
                    translated_chunks.append(result if result else chunk)
                except Exception:
                    translated_chunks.append(chunk)
            return " ".join(translated_chunks)
    except Exception as e:
        logger.warning("翻译失败: %s", e)
        return f"{text}\n[翻译服务暂不可用]"


def translate_comments(comments: list[dict]) -> list[dict]:
    """翻译评论列表"""
    result = []
    for comment in comments:
        translated = translate_text(comment["content"])
        result.append(
            {
                "author": comment["author"],
                "original": comment["content"],
                "translated": translated,
            }
        )
    return result
