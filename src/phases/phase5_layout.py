# src/phases/phase5_layout.py
import anthropic
from src.models import ImageTask, ProductInfo

LAYOUT_PROMPT = """所有场景底图已完成，规划整套排版方案。

产品：{product_name}
完成的场景图：
{scene_list}

输出整套图片统一排版规范：
1. 标题样式（字体大小、颜色、位置）
2. 副标题层级
3. 卖点信息块结构
4. 图标风格
5. 留白规则
6. 全套视觉一致性要求

以 Markdown 格式输出，清晰分点。"""


def run_phase5(
    client: anthropic.Anthropic,
    product: ProductInfo,
    tasks: list[ImageTask],
) -> str:
    print("\n📐 Phase 5: 统一排版规划...")
    completed = [t for t in tasks if t.scene_image_path]
    scene_list = "\n".join([f"- 图{t.sub_index}: {t.purpose}（{t.scene_image_path}）" for t in completed])

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        messages=[{"role": "user", "content": LAYOUT_PROMPT.format(
            product_name=product.name,
            scene_list=scene_list,
        )}],
    )
    layout_plan = response.content[0].text
    print("\n排版规划：")
    print(layout_plan[:500] + "..." if len(layout_plan) > 500 else layout_plan)
    return layout_plan
