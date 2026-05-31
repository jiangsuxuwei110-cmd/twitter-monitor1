"""
PushPlus 推送模块
将格式化的 HTML 内容通过 PushPlus 推送到微信
"""

import logging
import requests

logger = logging.getLogger(__name__)

PUSHPLUS_URL = "https://www.pushplus.plus/send"


def send_push(token: str, title: str, content: str, template: str = "html") -> bool:
    """
    通过 PushPlus 发送推送

    Args:
        token: PushPlus token
        title: 推送标题
        content: 推送内容（HTML 格式）
        template: 内容模板类型，默认 html

    Returns:
        是否发送成功
    """
    payload = {
        "token": token,
        "title": title,
        "content": content,
        "template": template,
    }

    try:
        resp = requests.post(PUSHPLUS_URL, json=payload, timeout=20)
        if resp.status_code == 200:
            data = resp.json()
            code = data.get("code", -1)
            if code == 200:
                logger.info("PushPlus 推送成功")
                return True
            else:
                logger.error("PushPlus 返回错误: code=%s, msg=%s", code, data.get("msg", ""))
                return False
        else:
            logger.error("PushPlus 请求失败: status=%d", resp.status_code)
            return False
    except requests.exceptions.Timeout:
        logger.error("PushPlus 请求超时")
        return False
    except Exception as e:
        logger.error("PushPlus 推送异常: %s", e)
        return False


def send_tweet_push(token: str, username: str, html_content: str, count: int) -> bool:
    """
    发送推文更新的推送

    Args:
        token: PushPlus token
        username: 监控的用户名
        html_content: HTML 格式的推送内容
        count: 新推文数量

    Returns:
        是否成功
    """
    title = f"🐦 @{username} 有 {count} 条新推文"
    if count == 1:
        title = f"🐦 @{username} 发布了新推文"

    return send_push(token, title, html_content, template="html")
