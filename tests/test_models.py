from src.models import ProductInfo, ImageTask, WorkflowState, PhaseStatus, GenerationResult, ReviewResult


def test_workflow_state_initialization():
    state = WorkflowState()
    assert state.product is None
    assert state.image_tasks == []
    assert state.current_task_index == 0


def test_image_task_default_status():
    task = ImageTask(
        index=1, sub_index="1", purpose="主图",
        selling_point="亮度高", composition="居中",
        scene="工地场景", material_request="正面照"
    )
    assert task.status == PhaseStatus.PENDING
    assert task.scene_image_path is None


def test_generation_result_success():
    result = GenerationResult(success=True, image_path="output/test.png")
    assert result.image_path == "output/test.png"
    assert result.error is None


def test_generation_result_failure():
    result = GenerationResult(success=False, error="API error")
    assert result.image_path is None
    assert result.success is False


def test_review_result_defaults():
    result = ReviewResult(passed=True)
    assert result.issues == []
    assert result.suggestions == []
    assert result.score == 0
