import pytest
import os
import base64
from unittest.mock import patch, MagicMock
from src.generators.nano_banana import NanaBananaGenerator
from src.models import GenerationResult

# 1x1 PNG bytes for testing
PNG_1X1 = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
)


def test_generator_initializes_with_api_key():
    gen = NanaBananaGenerator(api_key="test-key")
    assert gen.api_key == "test-key"


def test_generate_returns_result_object():
    gen = NanaBananaGenerator(api_key="test-key")
    with patch.object(gen, '_call_api', return_value=PNG_1X1):
        result = gen.generate(
            prompt="A product on white background",
            negative_prompt="blurry, distorted",
            output_path="/tmp/test_gen.png"
        )
    assert isinstance(result, GenerationResult)


def test_generate_saves_image_on_success(tmp_path):
    gen = NanaBananaGenerator(api_key="test-key")
    output_path = str(tmp_path / "test.png")
    with patch.object(gen, '_call_api', return_value=PNG_1X1):
        result = gen.generate("test prompt", "", output_path)
    assert result.success is True
    assert result.image_path == output_path
    assert os.path.exists(output_path)


def test_generate_returns_failure_on_api_error():
    gen = NanaBananaGenerator(api_key="test-key")
    with patch.object(gen, '_call_api', side_effect=ValueError("API error")):
        result = gen.generate("test prompt", "bad things", "/tmp/fail.png")
    assert result.success is False
    assert result.image_path is None
    assert "API error" in result.error


def test_negative_prompt_appended_to_full_prompt():
    gen = NanaBananaGenerator(api_key="test-key")
    captured = []
    def fake_call(prompt):
        captured.append(prompt)
        return PNG_1X1
    with patch.object(gen, '_call_api', side_effect=fake_call):
        gen.generate("main prompt", "avoid this", "/tmp/t.png")
    assert "avoid this" in captured[0]
    assert "main prompt" in captured[0]
