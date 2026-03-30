from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class InputType(Enum):
    URL = "url"
    PHOTO = "photo"


class PhaseStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    AWAITING_USER = "awaiting_user"
    COMPLETE = "complete"


@dataclass
class ProductInfo:
    name: str
    brand: str
    core_selling_points: list[str]
    specs: dict[str, str]
    usage: str
    target_audience: str
    use_cases: list[str]
    visual_directions: list[str]
    raw_content: str  # 原始抓取内容


@dataclass
class ImageTask:
    index: int          # 图片序号，如 1, 2, 3
    sub_index: str      # 子序号字符串，如 "1" 或 "2.1"
    purpose: str        # 图片用途
    selling_point: str  # 核心卖点
    composition: str    # 构图描述
    scene: str          # 场景描述
    material_request: str  # 向用户索要的素材说明
    status: PhaseStatus = PhaseStatus.PENDING
    scene_image_path: Optional[str] = None
    layout_image_path: Optional[str] = None


@dataclass
class GenerationResult:
    success: bool
    image_path: Optional[str]
    error: Optional[str] = None
    prompt_used: str = ""
    negative_prompt_used: str = ""


@dataclass
class ReviewResult:
    passed: bool
    issues: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    score: int = 0  # 0-10


@dataclass
class WorkflowState:
    product: Optional[ProductInfo] = None
    image_tasks: list[ImageTask] = field(default_factory=list)
    layout_plan: str = ""
    current_task_index: int = 0
    output_dir: str = "output"
