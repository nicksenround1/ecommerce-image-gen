from unittest.mock import patch, MagicMock
from src.agents.planner import ImagePlanner
from src.models import ProductInfo, ImageTask

MOCK_PLAN_JSON = '''[
    {"index":1,"sub_index":"1","purpose":"主图","selling_point":"14000LM超高亮","composition":"居中，预留右侧文案区","scene":"工地场景，夜间","material_request":"产品正面照，白底"},
    {"index":2,"sub_index":"2","purpose":"使用场景图","selling_point":"无线自由","composition":"产品左侧，右侧文案区","scene":"工地混凝土背景","material_request":"产品侧面照45度"}
]'''


def _mock_product():
    return ProductInfo(
        name="工作灯", brand="DAYA",
        core_selling_points=["14000LM", "无线"],
        specs={"power": "60W"}, usage="工地照明",
        target_audience="建筑工人", use_cases=["工地"],
        visual_directions=["工地场景"], raw_content="..."
    )


def _mock_response(text: str):
    mock = MagicMock()
    mock.content = [MagicMock(type="text", text=text)]
    return mock


def test_planner_returns_image_tasks():
    planner = ImagePlanner(api_key="test-key")
    with patch.object(planner.client.messages, 'create', return_value=_mock_response(MOCK_PLAN_JSON)):
        tasks = planner.create_plan(_mock_product())
    assert len(tasks) == 2
    assert all(isinstance(t, ImageTask) for t in tasks)
    assert tasks[0].index == 1
    assert tasks[0].sub_index == "1"


def test_planner_with_feedback_returns_tasks():
    planner = ImagePlanner(api_key="test-key")
    with patch.object(planner.client.messages, 'create', return_value=_mock_response(MOCK_PLAN_JSON)):
        tasks = planner.create_plan_with_feedback(_mock_product(), "减少图片数量")
    assert len(tasks) == 2


def test_format_plan_for_display():
    planner = ImagePlanner(api_key="test-key")
    with patch.object(planner.client.messages, 'create', return_value=_mock_response(MOCK_PLAN_JSON)):
        tasks = planner.create_plan(_mock_product())
    display = planner.format_plan_for_display(tasks)
    assert "主图" in display
    assert "14000LM" in display
