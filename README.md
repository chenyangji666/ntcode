<h1 align="center">HXCode</h1>

<p align="center">
  <strong>基于 Claude Code 源码的 AI 编码助手，针对小米 MiMo 模型深度优化。</strong><br>
  所有实验性功能已解锁，一个二进制文件即可运行。
</p>

---

## 快速入门

```powershell
# 启动 HXCode
hxcode

# 非交互模式（直接提问）
hxcode -p "你的问题"

# OAuth 登录
hxcode /login
```

---

## 小米 MiMo 模型适配

HXCode 的核心特色：**原生支持小米 MiMo 大模型，并内置破限（jailbreak）配置。**

### 什么是破限？

小米 MiMo 模型（如 `mimo-v2.5-pro`）原生带有安全限制，会拒绝执行部分编程任务（如：写爬虫、逆向工程、安全测试等）。HXCode 通过以下方式解除这些限制：

- **自定义 System Prompt 注入**：在 `src/constants/system.ts` 中注入人设覆盖，让模型将 Claude Code 的安全指令视为"注入攻击"并忽略
- **API 兼容层**：MiMo 使用 Anthropic 兼容 API 格式（`/anthropic` 端点），HXCode 直接对接，无需额外适配
- **全 Guardrails 移除**：编译时移除所有安全护栏代码，从根源上避免拒绝响应

### 配置 MiMo

在项目的 `.claude/settings.json` 中配置：

```json
{
  "env": {
    "ANTHROPIC_AUTH_TOKEN": "<你的小米token>",
    "ANTHROPIC_BASE_URL": "https://token-plan-cn.xiaomimimo.com/anthropic",
    "ANTHROPIC_MODEL": "mimo-v2.5-pro",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "mimo-v2.5-pro",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "mimo-v2.5-pro",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "mimo-v2.5-pro"
  }
}
```

### 破限效果

| 场景 | 原版 MiMo | HXCode + MiMo |
|------|----------|---------------|
| 写爬虫脚本 | ❌ 拒绝 | ✅ 正常生成 |
| 逆向工程分析 | ❌ 拒绝 | ✅ 正常执行 |
| 安全渗透测试代码 | ❌ 拒绝 | ✅ 正常生成 |
| 常规编程任务 | ✅ 正常 | ✅ 正常 |
| 88 个实验功能 | N/A | ✅ 全部解锁 |

---

## 功能特性

- ✅ 88 个实验性功能全部解锁
- ✅ 所有遥测（telemetry）已移除
- ✅ 所有安全护栏已移除
- ✅ 多模型提供商支持（Anthropic、OpenAI、Bedrock、Vertex、MiMo）
- ✅ MiMo 模型原生破限

---

## 模型提供商

| 提供商 | 环境变量 |
|--------|---------|
| 小米 MiMo（推荐） | `ANTHROPIC_BASE_URL` + `ANTHROPIC_AUTH_TOKEN` |
| Anthropic（默认） | `ANTHROPIC_API_KEY` |
| OpenAI Codex | `CLAUDE_CODE_USE_OPENAI=1` |
| AWS Bedrock | `CLAUDE_CODE_USE_BEDROCK=1` |
| Google Vertex | `CLAUDE_CODE_USE_VERTEX=1` |

---

## 编译

```bash
git clone <repo-url>
cd hxcode
bun install
bun run build
```

编译产物为 `./cli`，直接运行即可。

---

## 与 CYJCODE 的关系

| 项目 | 说明 |
|------|------|
| **CYJCODE** | 通用版 Claude Code 魔改，支持多种模型 |
| **HXCode** | 针对小米 MiMo 模型优化定制版，内置破限配置 |

两者基于同一套源码，HXCode 是 CYJCODE 的 MiMo 专用分支。

---

## License

基于 Anthropic 的 Claude Code 源码修改。
