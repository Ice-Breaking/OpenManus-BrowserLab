# -*- coding: utf-8 -*-
"""
独立验证 GUI-Plus 对"日期选择器"的操作能力。

流程：
1. whaleguard 预热 + 打开携程机票搜索页
2. 切到"单程"，避免返回日期/多余下拉干扰
3. 点击出发日期，打开日历
4. 用 GUI-Plus 在日历中选择一个明显非默认的日期(7月15日)
5. 读取出发日期框文本，验证是否变为 2026-07-15
"""
import asyncio
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

from app.tool.browser_use_tool import BrowserUseTool

TARGET_DATE_DESC = "6月29日"
EXPECT_IN_FIELD = "06-29"


async def read_depart_date(browser_tool):
    """读取页面上出发日期相关的可见文本，用于验证。"""
    page = await (await browser_tool._ensure_browser_initialized()).get_current_page()
    texts = await page.evaluate(
        """
        () => {
            const out = [];
            const nodes = document.querySelectorAll('input, [class*="date"], [class*="Date"]');
            for (const el of nodes) {
                const v = (el.value || el.innerText || '').trim();
                if (v && /\\d{4}-\\d{2}-\\d{2}|\\d{2}-\\d{2}/.test(v)) out.push(v);
            }
            return out.slice(0, 20);
        }
        """
    )
    return texts


async def run():
    print("=" * 80)
    print(f"GUI-Plus 日期选择器测试（目标日期：{TARGET_DATE_DESC}）")
    print("=" * 80)

    browser_tool = BrowserUseTool()
    try:
        print("\n[1] 预热 + 打开机票搜索页...")
        r = await browser_tool.execute(
            action="go_to_url",
            url="https://flights.ctrip.com/online/channel/domestic",
        )
        print(f"  {r.output or r.error}")
        await asyncio.sleep(5)

        print("\n[2] 用 Playwright 精确点击出发日期触发器，打开日历...")
        page = await (await browser_tool._ensure_browser_initialized()).get_current_page()
        # 出发日期触发器：#datePicker 下的 .depart-date（u_key=date_picker）
        trigger = page.locator("#datePicker .depart-date, #datePicker [u_key='date_picker']").first
        await trigger.click()
        await asyncio.sleep(2)

        # 截图确认日历已打开
        shot = await page.screenshot(type="png", full_page=False)
        from pathlib import Path
        Path("debug_html").mkdir(exist_ok=True)
        cal_path = "debug_html/_calendar_opened.png"
        with open(cal_path, "wb") as f:
            f.write(shot)
        print(f"  已保存日历截图: {cal_path}")

        before = await read_depart_date(browser_tool)
        print(f"  选择前日期文本: {before}")

        print(f"\n[4] GUI-Plus 选择日期 {TARGET_DATE_DESC} ...")
        r = await browser_tool.execute(action="click", element_description=TARGET_DATE_DESC)
        print(f"  {r.output or r.error}")
        await asyncio.sleep(2)

        after = await read_depart_date(browser_tool)
        print(f"  选择后日期文本: {after}")

        ok = any(EXPECT_IN_FIELD in t for t in after)
        print("\n" + "=" * 80)
        print(f"验证结果: {'成功 - 出发日期已变为 ' + EXPECT_IN_FIELD if ok else '未检测到目标日期，请查看截图 debug_html'}")
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
