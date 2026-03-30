# src/phases/phase6_render.py
import os
import json
import re
import anthropic
from src.models import ImageTask, ProductInfo
from src.agents.prompt_engineer import PromptEngineer
from src.generators.nano_banana import NanaBananaGenerator

RENDER_PROMPT = """基于场景底图和排版规范，生成最终排版图的 Nano Banana 提示词。

图片：图{sub_index} - {purpose}
场景底图：{scene_path}
排版规范摘要：{layout_summary}
卖点文案：{selling_point}

输出 JSON：
{{"prompt": "排版合成提示词", "negative_prompt": "负向提示词"}}"""


def _extract_json(raw: str) -> str:
    match = re.search(r"```(?:json)?\s*(\{.*\})\s*```", raw, re.DOTALL)
    if match:
        return match.group(1)
    return raw


def run_phase6(
    tasks: list[ImageTask],
    product: ProductInfo,
    layout_plan: str,
    engineer: PromptEngineer,
    generator: NanaBananaGenerator,
    output_dir: str,
    client: anthropic.Anthropic,
) -> list[ImageTask]:
    print(f"\n🎨 Phase 6: 生成最终排版图...")
    layout_summary = layout_plan[:300]

    for task in tasks:
        if not task.scene_image_path:
            continue
        print(f"  排版图 {task.sub_index}: {task.purpose}...")
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            messages=[{"role": "user", "content": RENDER_PROMPT.format(
                sub_index=task.sub_index,
                purpose=task.purpose,
                scene_path=task.scene_image_path,
                layout_summary=layout_summary,
                selling_point=task.selling_point,
            )}],
        )
        raw = response.content[0].text
        try:
            data = json.loads(_extract_json(raw))
        except json.JSONDecodeError as e:
            print(f"  ⚠️ JSON parse error for task {task.sub_index}: {e}")
            continue
        prompt = data.get("prompt")
        neg = data.get("negative_prompt")
        if not prompt or not neg:
            print(f"  ⚠️ Missing prompt/negative_prompt keys for task {task.sub_index}, skipping")
            continue
        output_path = os.path.join(output_dir, f"final_{task.sub_index}.png")
        result = generator.generate(prompt, neg, output_path)
        if result.success:
            task.layout_image_path = result.image_path
            print(f"  ✅ {output_path}")
        else:
            print(f"  ❌ 失败: {result.error}")
    return tasks
