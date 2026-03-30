import json
import anthropic
from src.models import ImageTask, ProductInfo

SYSTEM_PROMPT = """你是 Gemini Nano Banana 2 图片生成提示词专家，专注于 Amazon 电商详情页图片生成。

Nano Banana 2 提示词原则：
1. 英文提示词，具体清晰
2. 先描述主体（产品），再描述场景，最后描述风格
3. 使用专业摄影术语：photorealistic, studio lighting, 8K, sharp focus
4. 明确产品位置和比例：centered, left side, 40% of frame
5. 针对电商图：clean background, product-focused, commercial photography
6. 人物本地化：如有人物，指定 American worker, work gloves, diverse skin tone
7. 场景统一：多图组合时重复相同场景描述"""

ENGINEER_PROMPT = """产品：{product_name}（{brand}）
卖点：{selling_point}
构图要求：{composition}
场景要求：{scene}
用户提供素材：{material_description}

生成 Nano Banana 2 提示词，输出 JSON：
{{
  "prompt": "英文正向提示词（50-150词）",
  "negative_prompt": "英文负向提示词（避免的元素）"
}}

负向提示词必须包含：blurry, distorted, deformed, watermark, text overlay, multiple products"""

REFINE_PROMPT = """上一次生图失败。
原提示词：{original_prompt}
失败原因：{failure_reason}
产品：{product_name}，卖点：{selling_point}

修正提示词，输出 JSON：
{{"prompt": "修正后提示词", "negative_prompt": "负向提示词"}}"""


class PromptEngineer:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)

    def _call_and_parse(self, user_content: str) -> tuple[str, str]:
        response = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_content}],
        )
        raw = response.content[0].text
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON from prompt engineer: {e}\nRaw: {raw[:500]}") from e
        return data["prompt"], data["negative_prompt"]

    def generate(
        self,
        product: ProductInfo,
        task: ImageTask,
        material_description: str,
    ) -> tuple[str, str]:
        return self._call_and_parse(ENGINEER_PROMPT.format(
            product_name=product.name,
            brand=product.brand,
            selling_point=task.selling_point,
            composition=task.composition,
            scene=task.scene,
            material_description=material_description,
        ))

    def refine_after_failure(
        self,
        product: ProductInfo,
        task: ImageTask,
        original_prompt: str,
        failure_reason: str,
    ) -> tuple[str, str]:
        return self._call_and_parse(REFINE_PROMPT.format(
            original_prompt=original_prompt,
            failure_reason=failure_reason,
            product_name=product.name,
            selling_point=task.selling_point,
        ))
