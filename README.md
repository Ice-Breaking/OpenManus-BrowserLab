# OpenManus-BrowserLab

浏览器自动化实验室：围绕同一道真实难题，用三条不同技术路线改造 [OpenManus](https://github.com/FoundationAgents/OpenManus)。

本项目的基准任务是「用携程查询 1 月 30 日从上海到北京的机票」。真正的难点不在搜索，而在于**日历选择器**：弹层里的日期格子是动态渲染的，靠 DOM 元素编号（`[40]<input>出发日期</input>`）定位极不稳定——同一个数字 `6` 可能匹配到 `16`、`26`。本仓库的三个目录，就是三种应对思路的完整实现。

## 三条路线

| 目录 | 路线 | 核心做法 | 关键文件 |
|---|---|---|---|
| `OpenManus-cy` | **基座**（对照组） | 完整的 OpenManus 框架 + Daytona 云沙箱；浏览器交互沿用元素编号模式，LLM 依据 `[index]<type>text</type>` 选择元素 | `app/agent/{base,react,toolcall,manus}.py`、`app/daytona/`、`app/tool/sandbox/`、`sandbox_main.py` |
| `OpenManus-rag` | **知识库注入**（稳定优先） | 启动时把 `knowledge/*.txt` 全文拼进 system prompt，引导 Agent 用携程深链 URL 直达航班列表，从根上绕开日历；配套 `ElementClassifier` 给元素打 14 类标签与置信度 | `knowledge/travel_tools.txt`、`app/prompt/manus.py`、`app/tool/element_classifier.py`、`app/tool/url_helper.py` |
| `OpenManus-gui` | **视觉操作**（通用优先） | 把浏览器接口简化为 `click` / `type` 两个动作，内部三层定位：Playwright Locator → JS 动态查找 → `gui-plus` 视觉模型看截图返回坐标；每次操作自动存 HTML/截图便于排查 | `app/tool/browser_use_tool.py`、`app/prompt/manus.py`、`debug_html/`（运行时产物） |

一句话取舍：RAG 路线**确定但不通用**（换个网站就失效），GUI 路线**通用但不稳定**（视觉坐标可能偏）。这也是浏览器自动化方案落地时的核心权衡。

## 环境准备

要求 Python 3.12+。

```bash
# 进入任一子目录后执行
cd OpenManus-cy          # 或 OpenManus-rag / OpenManus-gui
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium    # 浏览器工具依赖
```

模型走阿里云百炼（DashScope），需要环境变量：

```bash
export DASHSCOPE_API_KEY="你的百炼 API Key"
```

`config/config.toml` 中 `[llm] api_key` 留空时会自动回落到该环境变量。

## 配置说明

每个子项目的本地配置文件是 `config/config.toml`，**不入库**（上游 `.gitignore` 约定，防止密钥泄露）。克隆后先从示例复制一份，再把 `[llm]` 改成 DashScope：

```bash
cd OpenManus-cy   # 或 OpenManus-rag / OpenManus-gui
cp config/config.example.toml config/config.toml
```

`[llm]` 与 `[llm.vision]` 的 DashScope 写法（主模型 `qwen-max`，视觉模型 `qwen-vl-plus`）：

```toml
[llm]
api_type = "openai"
model = "qwen-max"
base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
api_key = ""        # 留空则自动读环境变量 DASHSCOPE_API_KEY

[llm.vision]
api_type = "openai"
model = "qwen-vl-plus"
base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
api_key = ""
```

| 配置块 | 说明 |
|---|---|
| `[llm]` / `[llm.vision]` | 主模型与视觉模型，`api_key` 留空则读 `DASHSCOPE_API_KEY` |
| `[browser]` | 无头模式、安全策略、Chromium 启动参数 |
| `[search]` | 搜索引擎（默认百度）与回退链 |
| `[mcp]` | MCP 服务器模块引用 |
| `[daytona]` | Daytona 云沙箱，仅 `OpenManus-cy` 的沙箱相关入口需要 |

`[daytona] daytona_api_key` **默认为空**，`app/daytona/sandbox.py` 在 key 为空时只会打印提示并禁用 Daytona 能力，不影响其他功能。需要沙箱时在本地填入自己的 key：

```toml
[daytona]
daytona_api_key = "dtn_xxx"
daytona_server_url = "https://app.daytona.io/api"
daytona_target = "us"
```

> `config/config.toml` 整个文件被 `.gitignore` 忽略，填入真实密钥也不会被提交。

## 运行入口

各子项目结构一致，入口相同：

| 入口 | 用途 |
|---|---|
| `python main.py` | 命令行单 Agent 对话，最常用 |
| `python app.py` | Web 界面（FastAPI + SSE 流式输出），默认 http://localhost:5172 |
| `python run_flow.py` | PlanningFlow 多 Agent 编排，适合复杂任务拆解 |
| `python run_mcp.py` | 作为 MCP 客户端连接外部 MCP 服务器 |
| `python run_mcp_server.py` | 把 OpenManus 自身暴露为 MCP 服务器 |
| `python sandbox_main.py` | Daytona 云沙箱版（仅 `OpenManus-cy`） |

示例：

```bash
python main.py --prompt "用携程查询 1 月 30 日从上海到北京的机票"
```

## 目录结构

```
OpenManus-BrowserLab/
├── README.md
├── LICENSE
├── OpenManus-cy/            # 基座：完整框架 + Daytona 沙箱
│   ├── app/                 # agent / flow / tool / prompt / config 等核心模块
│   ├── config/              # config.toml 与各模型示例配置
│   ├── protocol/a2a/        # A2A 协议服务器
│   ├── tests/               # 沙箱相关测试
│   └── main.py / app.py / run_flow.py / run_mcp.py / sandbox_main.py
├── OpenManus-rag/           # RAG 策略：知识库注入 + URL 直跳
│   ├── knowledge/           # 场景知识库（*.txt，启动时注入 system prompt）
│   └── app/tool/{element_classifier,url_helper}.py
└── OpenManus-gui/           # GUI 策略：click/type + gui-plus 视觉
    ├── app/tool/browser_use_tool.py   # 三层定位核心实现
    ├── 7-gui-plus使用.py              # 视觉模型最小示例
    ├── analyze_date_picker.py         # 日历 HTML 离线分析脚本
    ├── test_*.py                      # 手工调试脚本，非自动化测试
    └── debug_html/                    # 运行时生成的页面快照（已忽略）
```

`OpenManus-gui` 根目录的 `test_*.py` 是迭代过程中手工运行的调试脚本（如 `test_whaleguard_bypass.py` 验证携程反爬预热、`test_smart_mode.py` 对比 HTML 定位路线），不属于单元测试套件。

## 已知限制

- `OpenManus-gui` 中 `test_vision_click.py` 调用的 `vision_click` 动作在最终版已并入 `click`/`type` 内部路由，属过程脚本
- `gui-plus` 的 base_url 在 `browser_use_tool.py` 内硬编码为 DashScope，未读取 `[llm.vision]`
- 携程等电商站点有反爬策略（whaleguard），失败属预期现象

## 致谢

本项目基于 [FoundationAgents/OpenManus](https://github.com/FoundationAgents/OpenManus)（MIT License, Copyright (c) 2025 manna_and_poem）改编。三个子目录内保留了上游的多语言 README。

## License

[MIT](LICENSE)
