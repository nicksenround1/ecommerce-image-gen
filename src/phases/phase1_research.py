import os
from src.models import ProductInfo, InputType
from src.agents.researcher import ProductResearcher


def fetch_url_content(url: str) -> str:
    """使用 firecrawl 抓取 URL 内容"""
    try:
        from firecrawl import FirecrawlApp
        app = FirecrawlApp(api_key=os.environ["FIRECRAWL_API_KEY"])
        result = app.scrape(url, formats=["markdown"])
        return result.markdown or ""
    except Exception as e:
        raise RuntimeError(f"URL 抓取失败: {e}")


def run_phase1(
    researcher: ProductResearcher,
    input_type: InputType,
    input_value: str,
) -> ProductInfo:
    print(f"\n🔍 Phase 1: 产品研究中...")

    if input_type == InputType.URL:
        print(f"  抓取产品页面: {input_value}")
        content = fetch_url_content(input_value)
        product = researcher.extract_from_text(content)
    else:
        print(f"  分析产品图片: {input_value}")
        product = researcher.extract_from_image(input_value)

    print(f"\n✅ 产品信息提取完成：")
    print(f"  产品：{product.name}")
    print(f"  品牌：{product.brand}")
    print(f"  核心卖点：{', '.join(product.core_selling_points[:3])}")
    return product
