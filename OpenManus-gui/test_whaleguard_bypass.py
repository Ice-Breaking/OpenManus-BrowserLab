# -*- coding: utf-8 -*-
"""
诊断 whaleguard 拦截：测试"先访问携程首页获取 cookie，再进入机票页"是否能绕过拦截。

结论判定：
- 如果直接访问 flights 页是 432/whaleguard，但经首页过渡后能正常加载（截图变大、有元素），
  说明拦截是缺少 whaleguard 放行 cookie 导致，按"先过首页"流程即可解决。
- 如果经首页过渡后仍被拦截，说明是自动化指纹被识别，需要连接真实 Chrome。
"""
import asyncio
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

from app.tool.browser_use_tool import BrowserUseTool


async def check_page(browser_tool, label):
    page = await (await browser_tool._ensure_browser_initialized()).get_current_page()
    title = await page.title()
    content = await page.content()
    blocked = "whaleguard" in content.lower()
    print(f"  [{label}] url={page.url}")
    print(f"  [{label}] title='{title}' html_len={len(content)} blocked={blocked}")
    return blocked


async def run():
    print("=" * 80)
    print("whaleguard 绕过诊断：首页过渡 -> 机票页")
    print("=" * 80)

    browser_tool = BrowserUseTool()
    try:
        # 1. 直接访问机票页（预期被拦截）
        print("\n[1] 直接访问 flights.ctrip.com ...")
        await browser_tool.execute(action="go_to_url", url="https://flights.ctrip.com")
        await asyncio.sleep(3)
        await check_page(browser_tool, "直接访问")

        # 2. 访问携程首页，获取 *.ctrip.com 的 whaleguard 放行 cookie
        print("\n[2] 访问携程首页 www.ctrip.com ...")
        await browser_tool.execute(action="go_to_url", url="https://www.ctrip.com")
        await asyncio.sleep(5)
        await check_page(browser_tool, "首页")

        # 3. 在同一上下文（共享 cookie）再进入机票搜索页
        print("\n[3] 再进入 flights.ctrip.com/online/channel/domestic ...")
        await browser_tool.execute(
            action="go_to_url",
            url="https://flights.ctrip.com/online/channel/domestic",
        )
        await asyncio.sleep(6)
        blocked = await check_page(browser_tool, "过渡后")

        print("\n" + "=" * 80)
        if blocked:
            print("结论: 经首页过渡后仍被拦截 -> 自动化指纹被识别，需连接真实 Chrome (CDP)。")
        else:
            print("结论: 经首页过渡后可正常加载 -> 缺 cookie 导致，按'先过首页'流程即可解决。")
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
