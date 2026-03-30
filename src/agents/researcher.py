import json
import anthropic
from src.models import ProductInfo

SYSTEM_PROMPT = """你是一名专业的电商产品分析师，专注于 Amazon 详情页优化。
从提供的产品信息中，提取关键数据并以 JSON 格式输出。
必须输出有效的 JSON，字段严格按照指定格式。"""

EXTRACT_PROMPT = """分析以下产品信息，提取关键数据，输出 JSON：

{content}

输出格式（严格 JSON，无多余文字）：
{{
  "name": "产品名称",
  "brand": "品牌",
  "core_selling_points": ["卖点1", "卖点2"],
  "specs": {{"规格名": "规格值"}},
  "usage": "主要用途",
  "target_audience": "目标受众",
  "use_cases": ["使用场景1"],
  "visual_directions": ["视觉方向1"]
}}"""


class ProductResearcher:
    def __init__(self, api_key: str, base_url: str = None):
        self.client = anthropic.Anthropic(api_key=api_key, base_url=base_url)

    def extract_from_text(self, content: str) -> ProductInfo:
        response = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2048,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": EXTRACT_PROMPT.format(content=content[:8000])}],
        )
        raw = response.content[0].text
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as e:
            raise ValueError(f"Claude returned invalid JSON: {e}\nRaw response: {raw[:500]}") from e
        return ProductInfo(
            name=data["name"],
            brand=data["brand"],
            core_selling_points=data["core_selling_points"],
            specs=data["specs"],
            usage=data["usage"],
            target_audience=data["target_audience"],
            use_cases=data["use_cases"],
            visual_directions=data["visual_directions"],
            raw_content=content,
        )

    def extract_from_image(self, image_path: str) -> ProductInfo:
        import base64
        with open(image_path, "rb") as f:
            image_data = base64.standard_b64encode(f.read()).decode("utf-8")
        ext = image_path.split(".")[-1].lower()
        MEDIA_TYPES = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png", "webp": "image/webp", "gif": "image/gif"}
        media_type = MEDIA_TYPES.get(ext, "image/png")

        response = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2048,
            system=SYSTEM_PROMPT,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {"type": "base64", "media_type": media_type, "data": image_data}
                    },
                    {"type": "text", "text": EXTRACT_PROMPT.format(content="[图片中的产品，请从图片视觉信息提取]")}
                ]
            }],
        )
        raw = response.content[0].text
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as e:
            raise ValueError(f"Claude returned invalid JSON: {e}\nRaw response: {raw[:500]}") from e
        return ProductInfo(
            name=data["name"],
            brand=data["brand"],
            core_selling_points=data["core_selling_points"],
            specs=data["specs"],
            usage=data["usage"],
            target_audience=data["target_audience"],
            use_cases=data["use_cases"],
            visual_directions=data["visual_directions"],
            raw_content=f"[image: {image_path}]",
        )
