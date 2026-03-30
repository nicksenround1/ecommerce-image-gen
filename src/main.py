# src/main.py
import os
import sys
from dotenv import load_dotenv
from src.models import InputType, WorkflowState
from src.agents.researcher import ProductResearcher
from src.agents.planner import ImagePlanner
from src.agents.prompt_engineer import PromptEngineer
from src.agents.reviewer import ImageReviewer
from src.generators.nano_banana import NanaBananaGenerator
from src.phases.phase1_research import run_phase1
from src.phases.phase2_plan import run_phase2
from src.phases.phase3_scene import run_phase3_all
from src.phases.phase5_layout import run_phase5
from src.phases.phase6_render import run_phase6
import anthropic

load_dotenv()


def main():
    print("🛍️  电商详情页生图系统")
    print("=" * 50)

    # 初始化客户端
    anthropic_key = os.environ["ANTHROPIC_API_KEY"]
    gemini_key = os.environ["GEMINI_API_KEY"]
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    researcher = ProductResearcher(api_key=anthropic_key)
    planner = ImagePlanner(api_key=anthropic_key)
    engineer = PromptEngineer(api_key=anthropic_key)
    reviewer = ImageReviewer(api_key=anthropic_key)
    generator = NanaBananaGenerator(api_key=gemini_key)
    client = anthropic.Anthropic(api_key=anthropic_key)
    state = WorkflowState(output_dir=output_dir)

    # 输入方式
    print("\n输入方式：")
    print("1. 产品链接（Amazon 等）")
    print("2. 手机拍摄的产品图片路径")
    choice = input("选择 [1/2]: ").strip()

    if choice == "1":
        url = input("输入产品链接: ").strip()
        state.product = run_phase1(researcher, InputType.URL, url)
    else:
        path = input("输入图片路径: ").strip()
        state.product = run_phase1(researcher, InputType.PHOTO, path)

    # Phase 2: 策划
    state.image_tasks = run_phase2(planner, state.product)

    # Phase 3: 逐张生成场景图
    state.image_tasks = run_phase3_all(
        state.image_tasks, state.product,
        engineer, generator, reviewer, output_dir
    )

    # Phase 5: 排版规划
    state.layout_plan = run_phase5(client, state.product, state.image_tasks)

    # Phase 6: 生成最终排版图
    state.image_tasks = run_phase6(
        state.image_tasks, state.product, state.layout_plan,
        engineer, generator, output_dir, client
    )

    # 汇总输出
    completed = [t for t in state.image_tasks if t.layout_image_path]
    print(f"\n🎉 完成！共生成 {len(completed)} 张图片")
    for task in completed:
        print(f"  图{task.sub_index}: {task.layout_image_path}")


if __name__ == "__main__":
    main()
