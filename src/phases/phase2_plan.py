from src.models import ProductInfo, ImageTask
from src.agents.planner import ImagePlanner
from src.utils import confirm


def run_phase2(planner: ImagePlanner, product: ProductInfo) -> list[ImageTask]:
    print(f"\n📋 Phase 2: 生成详情页策划...")
    tasks = planner.create_plan(product)

    print(f"\n策划方案（共 {len(tasks)} 张图）：")
    print(planner.format_plan_for_display(tasks))

    if not confirm("确认此策划方案？"):
        print("请重新描述调整方向：")
        feedback = input("> ")
        tasks = planner.create_plan_with_feedback(product, feedback)
        print(planner.format_plan_for_display(tasks))
        confirm("确认调整后的方案？")

    return tasks
