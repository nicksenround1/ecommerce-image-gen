from unittest.mock import patch, MagicMock
from src.agents.researcher import ProductResearcher
from src.models import ProductInfo

MOCK_JSON = '{"name":"Test Light","brand":"DAYA","core_selling_points":["14000LM","wireless"],"specs":{"power":"60W"},"usage":"工地照明","target_audience":"建筑工人","use_cases":["工地","车库"],"visual_directions":["工地场景","夜间使用"]}'


def _mock_response(text: str):
    mock = MagicMock()
    mock.content = [MagicMock(type="text", text=text)]
    return mock


def test_researcher_extracts_product_info_from_text():
    researcher = ProductResearcher(api_key="test-key")
    with patch.object(researcher.client.messages, 'create', return_value=_mock_response(MOCK_JSON)):
        result = researcher.extract_from_text("product page content here")
    assert isinstance(result, ProductInfo)
    assert result.name == "Test Light"
    assert result.brand == "DAYA"
    assert len(result.core_selling_points) == 2
    assert result.raw_content == "product page content here"


def test_researcher_extracts_selling_points():
    researcher = ProductResearcher(api_key="test-key")
    with patch.object(researcher.client.messages, 'create', return_value=_mock_response(MOCK_JSON)):
        result = researcher.extract_from_text("any content")
    assert "14000LM" in result.core_selling_points
    assert "wireless" in result.core_selling_points
