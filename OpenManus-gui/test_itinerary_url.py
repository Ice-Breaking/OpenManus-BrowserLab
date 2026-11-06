# -*- coding: utf-8 -*-
"""
验证 whaleguard 预热修复后，携程机票深链 URL（直接编码出发地/目的地/日期）
能否正常加载航班列表。这是最可靠的查询方式：城市与日期都写在 URL 里，
无需视觉填表。
"""
import asyncio
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

from app.tool.browser_use_tool import BrowserUseTool


async def run():
    print("=" * 80)
    print("深链 URL 机票查询测试（上海 -> 北京，6月26日）")
    print("=" * 80)

    browser_tool = BrowserUseTool()
    try:
        url = "https://flights.ctrip.com/itinerary/oneway/sha-bjs?date=2026-06-26"
        print(f"\n[1] 访问深链: {url}")
        result = await browser_tool.execute(action="go_to_url", url=url)
        print(f"  结果: {result.output or result.error}")
        await asyncio.sleep(8)

        state = await browser_tool.get_current_state()
        info = json.loads(state.output)
        elem = info.get("interactive_elements", "")
        print(f"\n  URL: {info.get('url')}")
        print(f"  标题: {info.get('title')}")
        print(f"  交互元素数量: {elem.count('[')}")

        print("\n[2] 提取航班信息...")
        result = await browser_tool.execute(
            action="extract_content",
            goal="提取航班列表：航空公司、航班号、起飞/到达时间、价格",
        )
        print(f"  结果: {result.output or result.error}")

        print("\n" + "=" * 80)
        print("测试完成!")
        print("=" * 80)
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback

        traceback.print_exc()
    finally:
        print("\n清理资源...")
        await browser_tool.cleanup()
        print("资源已清理。")


if __name__ == "__main__":
    asyncio.run(run())
