#!/usr/bin/env python3
"""
Credit Card Image Scraper - 只获取信用卡图片URL

Usage:
    python scripts/scrape_card_images.py --bank BMO          # 获取BMO所有卡片图片
    python scripts/scrape_card_images.py --url <card_url>    # 获取单个卡片图片
    python scripts/scrape_card_images.py --list-banks        # 列出支持的银行

Examples:
    python scripts/scrape_card_images.py --bank TD
    python scripts/scrape_card_images.py --url https://www.bmo.com/main/personal/credit-cards/bmo-cashback-mastercard/
"""

import asyncio
import re
import sys
import json
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse
from typing import List, Dict, Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import nest_asyncio
nest_asyncio.apply()

# Try to import crawl4ai
try:
    from crawl4ai import AsyncWebCrawler
    CRAWL4AI_AVAILABLE = True
except ImportError:
    CRAWL4AI_AVAILABLE = False

# Try to import playwright
try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


# 银行信用卡列表页URL
BANK_CARD_LISTINGS = {
    "BMO": "https://www.bmo.com/main/personal/credit-cards/",
    "TD": "https://www.td.com/ca/en/personal-banking/products/credit-cards",
    "RBC": "https://www.rbcroyalbank.com/credit-cards/",
    "CIBC": "https://www.cibc.com/en/personal-banking/credit-cards.html",
    "Scotiabank": "https://www.scotiabank.com/ca/en/personal/credit-cards.html",
    "AMEX": "https://www.americanexpress.com/ca/en/credit-cards/all-cards/",
    "Tangerine": "https://www.tangerine.ca/en/products/spending/creditcard",
    "Simplii": "https://www.simplii.com/en/credit-cards.html",
    "Rogers": "https://www.rogersbank.com/en/credit_cards",
    "Desjardins": "https://www.desjardins.com/en/credit-cards.html",
    "National Bank": "https://www.nbc.ca/personal/credit-cards.html",
}


def is_valid_image_url(url: str) -> bool:
    """检查是否是有效的图片URL"""
    if not url:
        return False
    image_extensions = ('.png', '.jpg', '.jpeg', '.webp', '.svg', '.gif')
    return any(url.lower().endswith(ext) or ext + '?' in url.lower() for ext in image_extensions)


async def scrape_page_html(url: str) -> str:
    """使用Playwright获取页面HTML"""
    if not PLAYWRIGHT_AVAILABLE:
        raise RuntimeError("Playwright not installed. Run: pip install playwright && playwright install")

    async with async_playwright() as p:
        # 使用 chromium，设置更真实的浏览器配置
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080},
            locale='en-CA'
        )
        page = await context.new_page()

        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_timeout(5000)  # 等待动态内容加载
            html = await page.content()
            return html
        finally:
            await context.close()
            await browser.close()


async def extract_card_image_from_url(page_url: str, bank: str = None) -> dict:
    """从卡片页面提取信用卡图片URL"""
    print(f"\n🔍 正在抓取: {page_url}")

    try:
        html = await scrape_page_html(page_url)

        # 提取页面标题作为卡片名称
        title_match = re.search(r'<title>([^<]+)</title>', html, re.IGNORECASE)
        card_name = title_match.group(1).strip() if title_match else "Unknown Card"

        # 查找所有图片URL
        all_imgs = re.findall(r'src="([^"]+\.(?:png|jpg|jpeg|webp)(?:\?[^"]*)?)"', html, re.IGNORECASE)

        if not all_imgs:
            print(f"   ❌ 未找到图片")
            return {"url": page_url, "name": card_name, "image_url": None}

        # 银行特定的图片匹配模式
        bank_patterns = {
            'BMO': [
                r'/dist/images/.*credit-cards/[^/]+\.(png|jpg)',
                r'credit-card.*\.(png|jpg)',
            ],
            'TD': [
                r'/content/dam/.*credit-cards.*\.(png|jpg)',
                r'/personal-banking/images/.*card.*\.(png|jpg)',
            ],
            'RBC': [
                r'/.*cards/.*\.(png|jpg)',
                r'credit.*card.*\.(png|jpg)',
            ],
            'CIBC': [
                r'/.*card.*\.(png|jpg)',
            ],
            'Scotiabank': [
                r'/.*card.*\.(png|jpg)',
            ],
            'AMEX': [
                r'cardart.*\.(png|jpg)',
                r'card.*image.*\.(png|jpg)',
            ],
            'Tangerine': [
                r'card.*\.(png|jpg)',
            ],
        }

        # 猜测银行名称
        if not bank:
            url_lower = page_url.lower()
            for b in BANK_CARD_LISTINGS.keys():
                if b.lower() in url_lower:
                    bank = b
                    break

        # 获取该银行的匹配模式
        patterns = bank_patterns.get(bank, [])

        # 尝试银行特定模式
        for pattern in patterns:
            for img in all_imgs:
                if re.search(pattern, img, re.IGNORECASE):
                    img_url = make_absolute_url(img, page_url)
                    print(f"   ✅ 找到图片: {img_url}")
                    return {"url": page_url, "name": card_name, "image_url": img_url, "bank": bank}

        # 回退：查找包含card关键词的图片
        card_keywords = ['card', 'credit', 'mastercard', 'visa', 'amex']
        skip_keywords = ['icon', 'logo', 'banner', 'hero', 'background', 'apply-now',
                        'product-page', 'mobile', 'tv', 'phone', 'mockup', 'instacart',
                        'badge', 'button', 'arrow', 'check', 'x-mark']

        for img in all_imgs:
            img_lower = img.lower()
            if any(kw in img_lower for kw in card_keywords):
                if any(skip in img_lower for skip in skip_keywords):
                    continue
                img_url = make_absolute_url(img, page_url)
                print(f"   ✅ 找到图片: {img_url}")
                return {"url": page_url, "name": card_name, "image_url": img_url, "bank": bank}

        print(f"   ❌ 未找到信用卡图片")
        return {"url": page_url, "name": card_name, "image_url": None, "bank": bank}

    except Exception as e:
        print(f"   ❌ 错误: {e}")
        return {"url": page_url, "name": "Error", "image_url": None, "error": str(e)}


def make_absolute_url(img_url: str, page_url: str) -> str:
    """将相对URL转换为绝对URL"""
    if img_url.startswith('http'):
        return img_url
    if img_url.startswith('//'):
        return 'https:' + img_url
    if img_url.startswith('/'):
        parsed = urlparse(page_url)
        return f"{parsed.scheme}://{parsed.netloc}{img_url}"
    return img_url


async def discover_card_urls(bank: str) -> List[Dict]:
    """发现银行的所有信用卡页面URL"""
    listing_url = BANK_CARD_LISTINGS.get(bank)
    if not listing_url:
        print(f"❌ 不支持的银行: {bank}")
        print(f"支持的银行: {list(BANK_CARD_LISTINGS.keys())}")
        return []

    print(f"\n🏦 正在发现 {bank} 的信用卡...")
    print(f"   列表页: {listing_url}")

    try:
        html = await scrape_page_html(listing_url)

        # 提取所有链接
        links = re.findall(r'href="([^"]+)"[^>]*>([^<]*)</a>', html, re.IGNORECASE)

        discovered = []
        seen_urls = set()

        for href, text in links:
            # 过滤信用卡相关链接
            href_lower = href.lower()
            text_clean = text.strip()

            # 跳过非卡片链接
            skip_words = ['apply', 'login', 'sign-in', 'compare', 'all-cards', 'help',
                         'faq', 'contact', 'security', 'activate', 'balance', 'payment',
                         '#', 'javascript']
            if any(skip in href_lower for skip in skip_words):
                continue

            # 必须包含card相关词
            if not any(kw in href_lower for kw in ['card', 'credit']):
                continue

            # 跳过太短或太长的文本
            if len(text_clean) < 5 or len(text_clean) > 100:
                continue

            # 跳过通用文本
            generic_texts = ['credit cards', 'learn more', 'view all', 'see all', 'apply now']
            if text_clean.lower() in generic_texts:
                continue

            # 转换为绝对URL
            full_url = make_absolute_url(href, listing_url)

            if full_url not in seen_urls:
                seen_urls.add(full_url)
                discovered.append({
                    "name": text_clean,
                    "url": full_url,
                    "bank": bank
                })

        print(f"   ✅ 发现 {len(discovered)} 张信用卡")
        return discovered

    except Exception as e:
        print(f"   ❌ 错误: {e}")
        return []


async def scrape_bank_card_images(bank: str) -> List[Dict]:
    """抓取银行所有信用卡的图片"""
    # 先发现所有卡片URL
    cards = await discover_card_urls(bank)

    if not cards:
        return []

    results = []
    for card in cards:
        result = await extract_card_image_from_url(card["url"], bank)
        result["name"] = card["name"]  # 使用发现时的名称
        results.append(result)

        # 添加延迟避免被封
        await asyncio.sleep(2)

    return results


def save_results(results: List[Dict], bank: str):
    """保存结果到JSON文件"""
    output_dir = Path(__file__).parent.parent / "data" / "images"
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"{bank}_images_{timestamp}.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n💾 结果已保存到: {output_file}")
    return output_file


def print_results(results: List[Dict]):
    """打印结果"""
    print(f"\n{'='*60}")
    print(f"📊 抓取结果 ({len(results)} 张卡片)")
    print(f"{'='*60}")

    success = [r for r in results if r.get("image_url")]
    failed = [r for r in results if not r.get("image_url")]

    if success:
        print(f"\n✅ 成功获取图片 ({len(success)}):")
        for r in success:
            print(f"   • {r['name']}")
            print(f"     图片: {r['image_url']}")

    if failed:
        print(f"\n❌ 未获取到图片 ({len(failed)}):")
        for r in failed:
            print(f"   • {r['name']}")
            print(f"     URL: {r['url']}")


def list_banks():
    """列出支持的银行"""
    print("\n📋 支持的银行:")
    print("="*60)
    for bank, url in BANK_CARD_LISTINGS.items():
        print(f"  • {bank}")
        print(f"    {url}\n")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="信用卡图片抓取工具 - 只获取信用卡图片URL",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument("--bank", "-b", help="银行名称 (如: BMO, TD, RBC)")
    parser.add_argument("--url", "-u", help="单个信用卡页面URL")
    parser.add_argument("--list-banks", "-l", action="store_true", help="列出支持的银行")
    parser.add_argument("--no-save", action="store_true", help="不保存结果到文件")

    args = parser.parse_args()

    # 检查依赖
    if not PLAYWRIGHT_AVAILABLE:
        print("❌ 错误: Playwright 未安装!")
        print("   请运行: pip install playwright && playwright install")
        sys.exit(1)

    if args.list_banks:
        list_banks()
        return

    if not args.bank and not args.url:
        parser.print_help()
        print("\n❌ 请提供 --bank 或 --url 参数")
        sys.exit(1)

    if args.url:
        # 抓取单个URL
        result = asyncio.run(extract_card_image_from_url(args.url))
        print_results([result])

    elif args.bank:
        # 抓取整个银行
        results = asyncio.run(scrape_bank_card_images(args.bank))
        print_results(results)

        if not args.no_save and results:
            save_results(results, args.bank)


if __name__ == "__main__":
    main()
