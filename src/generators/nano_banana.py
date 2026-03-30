import os
import base64
from pathlib import Path
from google import genai
from src.models import GenerationResult

MODEL = "gemini-3.1-flash-image-preview"


class NanaBananaGenerator:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = genai.Client(api_key=api_key)

    def _call_api(self, prompt: str) -> bytes:
        response = self.client.models.generate_content(
            model=MODEL,
            contents=[prompt],
        )
        for part in response.parts:
            if part.inline_data is not None:
                return part.inline_data.data
        raise ValueError("Gemini returned no image data")

    def generate(
        self,
        prompt: str,
        negative_prompt: str,
        output_path: str,
    ) -> GenerationResult:
        full_prompt = prompt
        if negative_prompt:
            full_prompt += f"\n\nAvoid: {negative_prompt}"

        try:
            image_bytes = self._call_api(full_prompt)
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(image_bytes)
            return GenerationResult(
                success=True,
                image_path=output_path,
                prompt_used=prompt,
                negative_prompt_used=negative_prompt,
            )
        except Exception as e:
            return GenerationResult(
                success=False,
                error=str(e),
                prompt_used=prompt,
                negative_prompt_used=negative_prompt,
            )
