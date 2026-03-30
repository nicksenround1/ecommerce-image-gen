import os
from src.models import ImageTask, ProductInfo, PhaseStatus
from src.agents.prompt_engineer import PromptEngineer
from src.agents.reviewer import ImageReviewer
from src.generators.nano_banana import NanaBananaGenerator
from src.utils import confirm

MAX_RETRIES = 3


def run_phase3_single(
    task: ImageTask,
    product: ProductInfo,
    engineer: PromptEngineer,
    generator: NanaBananaGenerator,
    reviewer: ImageReviewer,
    output_dir: str,
) -> ImageTask:
    print(f"\n🎨 图 {task.sub_index}：{task.purpose}")
    print(f"  卖点：{task.selling_point}")
    print(f"\n  📸 素材需求：")
    print(f"  {task.material_request}")

    material_desc = input("\n请描述你提供的素材（或输入图片路径）: ").strip()

    prompt, negative = engineer.generate(product, task, material_desc)
    print(f"\n  🤖 生图提示词已生成，执行生图...")

    output_path = os.path.join(output_dir, f"scene_{task.sub_index}.png")

    for attempt in range(1, MAX_RETRIES + 1):
        print(f"  生图中（第 {attempt} 次）...")
        result = generator.generate(prompt, negative, output_path)

        if not result.success:
            print(f"  ❌ 生图失败: {result.error}")
            if attempt < MAX_RETRIES:
                print("  重试中...")
            continue

        print(f"  ✅ 图片已生成: {result.image_path}")
        review = reviewer.review(result.image_path, task)
        print(f"\n  审核结果：{'✅ 通过' if review.passed else '❌ 不通过'} (评分 {review.score}/10)")

        if review.issues:
            print(f"  问题：{', '.join(review.issues)}")

        if review.passed:
            if confirm("确认此图片？"):
                task.scene_image_path = result.image_path
                task.status = PhaseStatus.COMPLETE
                return task
            elif attempt < MAX_RETRIES:
                feedback = input("请说明修改方向: ")
                prompt, negative = engineer.refine_after_failure(product, task, prompt, feedback)
        elif attempt < MAX_RETRIES:
            failure_reason = "; ".join(review.issues)
            prompt, negative = engineer.refine_after_failure(product, task, prompt, failure_reason)

    print(f"  ⚠️ 图 {task.sub_index} 达到最大重试次数，暂时跳过")
    task.status = PhaseStatus.PENDING
    return task


def run_phase3_all(
    tasks: list[ImageTask],
    product: ProductInfo,
    engineer: PromptEngineer,
    generator: NanaBananaGenerator,
    reviewer: ImageReviewer,
    output_dir: str,
) -> list[ImageTask]:
    print(f"\n🚀 Phase 3: 逐张生成场景图（共 {len(tasks)} 张）")
    for i, task in enumerate(tasks):
        print(f"\n{'='*50}")
        print(f"进度：{i+1}/{len(tasks)}")
        tasks[i] = run_phase3_single(task, product, engineer, generator, reviewer, output_dir)
    return tasks
