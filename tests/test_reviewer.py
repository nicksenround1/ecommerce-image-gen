import base64
from unittest.mock import patch, MagicMock
from src.agents.reviewer import ImageReviewer
from src.models import ImageTask, ReviewResult

PNG_1X1 = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
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


def test_reviewer_returns_review_result(tmp_path):
    reviewer = ImageReviewer(api_key="test-key")
    img_path = str(tmp_path / "test.png")
    with open(img_path, "wb") as f:
        f.write(PNG_1X1)
    with patch.object(reviewer.client.messages, 'create', return_value=_mock_response('{"passed":true,"issues":[],"suggestions":["光线可以更强"],"score":8}')):
        result = reviewer.review(img_path, _mock_task())
    assert isinstance(result, ReviewResult)
    assert result.passed is True
    assert result.score == 8


def test_reviewer_fails_on_low_quality(tmp_path):
    reviewer = ImageReviewer(api_key="test-key")
    img_path = str(tmp_path / "test.png")
    with open(img_path, "wb") as f:
        f.write(PNG_1X1)
    with patch.object(reviewer.client.messages, 'create', return_value=_mock_response('{"passed":false,"issues":["产品变形","背景喧宾夺主"],"suggestions":["重新生成"],"score":3}')):
        result = reviewer.review(img_path, _mock_task())
    assert result.passed is False
    assert len(result.issues) == 2


def test_reviewer_raises_on_invalid_json(tmp_path):
    reviewer = ImageReviewer(api_key="test-key")
    img_path = str(tmp_path / "test.png")
    with open(img_path, "wb") as f:
        f.write(PNG_1X1)
    with patch.object(reviewer.client.messages, 'create', return_value=_mock_response("not json")):
        try:
            reviewer.review(img_path, _mock_task())
            assert False, "Should have raised"
        except ValueError as e:
            assert "Invalid JSON" in str(e)
