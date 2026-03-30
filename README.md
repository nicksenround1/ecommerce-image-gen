# 电商详情页生图系统

一键生成 Amazon 电商详情页图片的 CLI 工具。输入产品链接或手机拍摄的产品照片，系统自动完成产品研究、图片策划、场景生图、质量审核、排版合成全流程。

## 工作原理

系统按照 SOP 分阶段自动执行：

| 阶段 | 说明 | 使用的 AI |
|------|------|-----------|
| Phase 1 | 产品研究（从链接抓取或从照片分析） | Claude Sonnet |
| Phase 2 | 详情页图片策划（5-8 张图方案） | Claude Sonnet |
| Phase 3 | 逐张生成场景图 + 质量审核 | Gemini 生图 + Claude 审核 |
| Phase 5 | 统一排版规划 | Claude Sonnet |
| Phase 6 | 生成最终排版图 | Gemini 生图 |

每个关键步骤都会暂停，等你确认后再继续。

## 准备工作（只需做一次）

### 1. 安装 Python

如果你还没装 Python，打开终端输入：

```bash
brew install python
```

### 2. 下载项目

```bash
git clone https://github.com/nicksenround1/ecommerce-image-gen.git
cd ecommerce-image-gen
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置 API 密钥

```bash
cp .env.example .env
```

然后用文本编辑器打开 `.env` 文件：

```bash
open .env
```

填入你的真实密钥：

```
ANTHROPIC_API_KEY=sk-ant-你的Claude密钥
GEMINI_API_KEY=AIza你的Gemini密钥
FIRECRAWL_API_KEY=fc-你的Firecrawl密钥
```

**密钥获取方式：**
- Claude 密钥：https://console.anthropic.com/settings/keys
- Gemini 密钥：https://aistudio.google.com/apikey
- Firecrawl 密钥（仅用产品链接时需要）：https://www.firecrawl.dev/

保存关闭。这一步只需要做一次。

## 使用方法

每次使用只需打开终端，输入：

```bash
cd ~/ecommerce-image-gen
python -m src.main
```

### 操作流程

**第一步：选择输入方式**

```
输入方式：
1. 产品链接（Amazon 等）
2. 手机拍摄的产品图片路径
选择 [1/2]:
```

- 输入 `1` 然后粘贴产品链接（比如 Amazon 商品页面地址）
- 输入 `2` 然后输入图片路径（提示：把照片文件直接拖到终端窗口，路径会自动填入）

**第二步：确认产品信息**

系统会显示提取到的产品名称、品牌、卖点，确认无误输入 `y`。

**第三步：确认图片策划方案**

系统会生成 5-8 张图的策划方案，显示每张图的用途、卖点、构图、场景。
- 满意输入 `y`
- 不满意输入 `n`，然后输入你的调整方向，系统会重新策划

**第四步：逐张生成场景图**

每张图系统会：
1. 提示你需要什么素材
2. 你描述你有的素材（或输入图片路径）
3. 自动生成图片并审核
4. 显示审核结果，你确认 `y` 或拒绝 `n`
5. 不通过会自动重试（最多 3 次）

**第五步：自动排版合成**

场景图全部完成后，系统自动规划排版并生成最终图片。

### 查看结果

所有生成的图片保存在 `output/` 文件夹：

```bash
open output/
```

- `scene_1.png`, `scene_2.png` ... — 场景底图
- `final_1.png`, `final_2.png` ... — 最终排版图（这是你要用的）

## 项目结构

```
ecommerce-image-gen/
├── src/
│   ├── main.py              # 主程序入口
│   ├── models.py            # 数据结构定义
│   ├── utils.py             # 工具函数
│   ├── agents/              # AI Agent 模块
│   │   ├── researcher.py    # 产品研究 Agent
│   │   ├── planner.py       # 图片策划 Agent
│   │   ├── prompt_engineer.py # 提示词工程 Agent
│   │   └── reviewer.py      # 图片审核 Agent
│   ├── generators/
│   │   └── nano_banana.py   # Gemini 生图引擎
│   └── phases/              # 各阶段执行逻辑
│       ├── phase1_research.py
│       ├── phase2_plan.py
│       ├── phase3_scene.py
│       ├── phase5_layout.py
│       └── phase6_render.py
├── output/                  # 生成的图片
├── sop/                     # SOP 流程文档
├── tests/                   # 测试文件
├── requirements.txt         # 依赖列表
└── .env.example             # 环境变量模板
```

## 常见问题

**Q: 报错 `Error: ANTHROPIC_API_KEY is not set`**
A: 你还没配置密钥。按上面「配置 API 密钥」步骤操作。

**Q: 报错 `URL 抓取失败`**
A: 检查 FIRECRAWL_API_KEY 是否正确，或者换用方式 2（直接给图片）。

**Q: 生成的图片质量不好**
A: 系统会自动审核并重试。如果 3 次都不理想，会跳过该图，你可以稍后重新运行。

**Q: 可以只重新生成某一张图吗？**
A: 目前需要重新运行整个流程。后续版本会支持单图重跑。

## 技术栈

- Claude Sonnet — 产品分析、策划、提示词工程、图片审核
- Gemini Nano Banana 2 — AI 图片生成
- Firecrawl — 网页内容抓取
- Python 3.11+
