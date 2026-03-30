import json
import re
import base64
import anthropic
from src.models import ImageTask, ReviewResult


def _extract_json(raw: str) -> str:
    match = re.search(r"```(?:json)?\s*(\{.*\})\s*```", raw, re.DOTALL)
    if match:
        return match.group(1)
    return raw

SYSTEM_PROMPT = """你是 Amazon 电商详情页图片质量审核专家。
严格按照质量标准审核图片，输出 JSON 格式审核结果。"""

REVIEW_PROMPT = """审核此图片是否满足电商详情页要求。

图片任务：
- 用途：{purpose}
- 核心卖点：{selling_point}
- 构图要求：{composition}
- 场景要求：{scene}

质量标准（必须全部满足才能 passed=true）：
1. 产品主体清楚可见
2. 产品形态稳定，无变形、无比例失真
3. 产品角度符合任务要求
4. 场景服务卖点，不喧宾夺主
5. 画面有足够留白供后续排版
6. 无明显电商禁忌（无多余配件、无错误材质）
7. 商业摄影级别质量

输出 JSON：
{{
  "passed": true或false,
  "issues": ["问题1"],
  "suggestions": ["建议1"],
  "score": 0到10的整数
}}"""


class ImageReviewer:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)

    def review(self, image_path: str, task: ImageTask) -> ReviewResult:
        with open(image_path, "rb") as f:
            image_data = base64.standard_b64encode(f.read()).decode("utf-8")
        ext = image_path.split(".")[-1].lower()
        MEDIA_TYPES = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png", "webp": "image/webp", "gif": "image/gif"}
        media_type = MEDIA_TYPES.get(ext, "image/png")

        response = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {"type": "base64", "media_type": media_type, "data": image_data}
                    },
                    {"type": "text", "text": REVIEW_PROMPT.format(
                        purpose=task.purpose,
                        selling_point=task.selling_point,
                        composition=task.composition,
                        scene=task.scene,
                    )}
                ]
            }],
        )
        raw = response.content[0].text
        try:
            data = json.loads(_extract_json(raw))
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON from reviewer: {e}\nRaw: {raw[:500]}") from e
        return ReviewResult(
            passed=data["passed"],
            issues=data.get("issues", []),
            suggestions=data.get("suggestions", []),
            score=data.get("score", 0),
        )
