import base64
from unittest.mock import patch, MagicMock
from src.agents.prompt_engineer import PromptEngineer
from src.models import ImageTask, ProductInfo


def _mock_product():
    return ProductInfo(
        name="工作灯", brand="DAYA", core_selling_points=["14000LM"],
        specs={}, usage="工地", target_audience="工人",
        use_cases=["工地"], visual_directions=["工地"], raw_content=""
    )


def _mock_task():
    return ImageTask(
        index=1, sub_index="1", purpose="主图",
        selling_point="14000LM", composition="居中",
        scene="工地场景", material_request="正面照"
    )


def _mock_response(text: str):
    mock = MagicMock()
    mock.content = [MagicMock(type="text", text=text)]
    return mock


MOCK_PROMPT_JSON = '{"prompt":"A powerful LED work light on construction site, product centered, photorealistic","negative_prompt":"blurry, distorted, deformed, watermark"}'


def test_engineer_returns_prompt_and_negative():
    engineer = PromptEngineer(api_key="test-key")
    with patch.object(engineer.client.messages, 'create', return_value=_mock_response(MOCK_PROMPT_JSON)):
        prompt, negative = engineer.generate(_mock_product(), _mock_task(), "白底正面照")
    assert isinstance(prompt, str)
    assert isinstance(negative, str)
    assert len(prompt) > 10


def test_engineer_refine_returns_tuple():
    engineer = PromptEngineer(api_key="test-key")
    with patch.object(engineer.client.messages, 'create', return_value=_mock_response(MOCK_PROMPT_JSON)):
        prompt, negative = engineer.refine_after_failure(
            _mock_product(), _mock_task(), "original prompt", "product distorted"
        )
    assert isinstance(prompt, str)
    assert isinstance(negative, str)


def test_engineer_raises_on_invalid_json():
    engineer = PromptEngineer(api_key="test-key")
    with patch.object(engineer.client.messages, 'create', return_value=_mock_response("not json")):
        try:
            engineer.generate(_mock_product(), _mock_task(), "material")
            assert False, "Should have raised"
        except ValueError as e:
            assert "Invalid JSON" in str(e)
