import json
import anthropic
from src.models import ProductInfo, ImageTask

SYSTEM_PROMPT = """你是一名专业的 Amazon 详情页视觉策划师。
基于产品信息，规划一套 5-8 张图片的详情页方案。
每张图片必须有明确任务、卖点、构图、场景和素材需求。
按照"先场景图，后功能图，最后对比/参数图"的顺序组织。"""

PLAN_PROMPT = """产品信息：
名称：{name}
品牌：{brand}
核心卖点：{selling_points}
规格：{specs}
使用场景：{use_cases}
视觉方向：{visual_directions}

规划详情页图片方案，输出 JSON 数组，每个元素格式：
{{
  "index": 图片序号整数,
  "sub_index": "子序号字符串如'1'或'2.1'",
  "purpose": "图片用途",
  "selling_point": "本图核心卖点",
  "composition": "构图描述（产品位置、留白区域、视觉重心）",
  "scene": "场景描述（背景、光线、氛围）",
  "material_request": "需要用户提供的素材说明"
}}

输出纯 JSON 数组，无多余文字。"""


class ImagePlanner:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)

    def _parse_tasks(self, text: str) -> list[ImageTask]:
        data = json.loads(text)
        return [
            ImageTask(
                index=item["index"],
                sub_index=item["sub_index"],
                purpose=item["purpose"],
                selling_point=item["selling_point"],
                composition=item["composition"],
                scene=item["scene"],
                material_request=item["material_request"],
            )
            for item in data
        ]

    def create_plan(self, product: ProductInfo) -> list[ImageTask]:
        response = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": PLAN_PROMPT.format(
                name=product.name,
                brand=product.brand,
                selling_points=", ".join(product.core_selling_points),
                specs=str(product.specs),
                use_cases=", ".join(product.use_cases),
                visual_directions=", ".join(product.visual_directions),
            )}],
        )
        return self._parse_tasks(response.content[0].text)

    def create_plan_with_feedback(self, product: ProductInfo, feedback: str) -> list[ImageTask]:
        response = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": PLAN_PROMPT.format(
                name=product.name,
                brand=product.brand,
                selling_points=", ".join(product.core_selling_points),
                specs=str(product.specs),
                use_cases=", ".join(product.use_cases),
                visual_directions=", ".join(product.visual_directions),
            ) + f"\n\n用户反馈调整方向：{feedback}"}],
        )
        return self._parse_tasks(response.content[0].text)

    def format_plan_for_display(self, tasks: list[ImageTask]) -> str:
        lines = ["📋 详情页图片策划方案\n"]
        for task in tasks:
            lines.append(f"图 {task.sub_index}：{task.purpose}")
            lines.append(f"  卖点：{task.selling_point}")
            lines.append(f"  构图：{task.composition}")
            lines.append(f"  场景：{task.scene}")
            lines.append("")
        return "\n".join(lines)
