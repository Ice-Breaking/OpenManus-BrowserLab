# -*- coding: utf-8 -*-
"""
使用 GUI-Plus 视觉方法测试机票查询（重点：日期选择）

背景：直接访问 flights.ctrip.com/itinerary/oneway/... 会被携程反爬拦截，
页面返回空内容（0 个元素）。因此改为访问可正常加载的搜索首页
flights.ctrip.com/online/channel/domestic，用 GUI-Plus 视觉模型填写
出发地/目的地，并对日期选择器进行操作。

当前工具接口（app/tool/browser_use_tool.py）已把旧的 vision_click /
vision_type 重构为统一的 click / type：
  - click(element_description=...) 内部优先用 Playwright/JS 定位，
    失败或日期类描述时自动回退到 GUI-Plus 视觉模型。
  - type(element_description=..., text=...) 同理。
日期类描述（如 "6月26日"）会直接走 GUI-Plus 视觉点击。
"""
import asyncio
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

from app.tool.browser_use_tool import BrowserUseTool
from app.logger import logger

# 查询参数
DEPART_CITY = "上海"
ARRIVE_CITY = "北京"
DEPART_DATE_DESC = "6月26日"  # 日期选择器中要点击的日期


async def run():
    print("=" * 80)
    print("GUI-Plus 视觉方法机票查询测试（上海 -> 北京，6月26日）")
    print("=" * 80)

    browser_tool = BrowserUseTool()

    try:
        # Step 1: 打开携程机票搜索首页（可正常加载，不会被拦截）
        print("\n[Step 1] 打开携程机票搜索首页...")
        result = await browser_tool.execute(
            action="go_to_url",
            url="https://flights.ctrip.com/online/channel/domestic",
        )
        print(f"  结果: {result.output or result.error}")
        await asyncio.sleep(5)

        # Step 2: 输入出发城市
        print(f"\n[Step 2] 输入出发城市: {DEPART_CITY} ...")
        result = await browser_tool.execute(
            action="type",
            element_description="出发城市输入框",
            text=DEPART_CITY,
        )
        print(f"  结果: {result.output or result.error}")
        await asyncio.sleep(2)

        # Step 3: 从下拉列表选择出发城市
        print(f"\n[Step 3] 选择下拉列表中的 {DEPART_CITY} ...")
        result = await browser_tool.execute(
            action="click",
            element_description=f"城市下拉列表中的{DEPART_CITY}选项",
        )
        print(f"  结果: {result.output or result.error}")
        await asyncio.sleep(2)

        # Step 4: 输入到达城市
        print(f"\n[Step 4] 输入到达城市: {ARRIVE_CITY} ...")
        result = await browser_tool.execute(
            action="type",
            element_description="到达城市输入框",
            text=ARRIVE_CITY,
        )
        print(f"  结果: {result.output or result.error}")
        await asyncio.sleep(2)

        # Step 5: 从下拉列表选择到达城市
        print(f"\n[Step 5] 选择下拉列表中的 {ARRIVE_CITY} ...")
        result = await browser_tool.execute(
            action="click",
            element_description=f"城市下拉列表中的{ARRIVE_CITY}选项",
        )
        print(f"  结果: {result.output or result.error}")
        await asyncio.sleep(2)

        # Step 6: 点击出发日期，打开日期选择器
        print("\n[Step 6] 点击出发日期，打开日期选择器...")
        result = await browser_tool.execute(
            action="click",
            element_description="出发日期输入框",
        )
        print(f"  结果: {result.output or result.error}")
        await asyncio.sleep(2)

        # Step 7: GUI-Plus 视觉选择日期（核心步骤）
        print(f"\n[Step 7] GUI-Plus 视觉选择日期: {DEPART_DATE_DESC} ...")
        result = await browser_tool.execute(
            action="click",
            element_description=DEPART_DATE_DESC,
        )
        print(f"  结果: {result.output or result.error}")
        await asyncio.sleep(2)

        # Step 8: 点击搜索
        print("\n[Step 8] 点击搜索按钮...")
        result = await browser_tool.execute(
            action="click",
            element_description="搜索按钮",
        )
        print(f"  结果: {result.output or result.error}")
        await asyncio.sleep(6)

        # Step 9: 提取结果
        print("\n[Step 9] 提取航班信息...")
        result = await browser_tool.execute(
            action="extract_content",
            goal="提取页面上从上海到北京6月26日的航班信息（航班号、时间、价格）",
        )
        print(f"  结果: {result.output or result.error}")

        # 最终状态
        state = await browser_tool.get_current_state()
        if state.output:
            info = json.loads(state.output)
            print(f"\n最终 URL: {info.get('url')}")
            print(f"最终标题: {info.get('title')}")

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
