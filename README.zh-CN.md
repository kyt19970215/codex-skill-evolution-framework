# Codex Skill 进化框架

[English](README.md)

这是一个可复用、可公开分享且不含个人信息的 Codex Skill 进化框架。它通过分层路由避免把所有规则堆进一个巨大的提示词。

完整框架包含六个独立 Skill：

1. `skill-evolution-core`：创建、更新、拆分、合并、验证、吸收和维护 Skill。
2. `skill-evolution-router`：判断长期规则和经验应该保存在哪里。
3. `project-rules-router`：处理非简单项目任务前选择对应的项目规则。
4. `coding-debug-rules`：排查 Shell、编码、路径、依赖、构建和测试问题。
5. `research-verification`：通过当前公开来源验证工具、API、版本和报错行为。
6. `codex-capability-router`：从已安装的 Skill、插件、应用和 MCP 工具中选择合适能力。

快捷触发词属于每位使用者自己的本地配置。首次安装时，使用者分别选择一个完整进化入口和一个能力吸收入口；公开框架不预设个人触发词。

框架还包含一个可选的全局规则模板：`templates/global-agents-template/AGENTS.md`。它提供回答风格、最小充分执行路径、资料源与方案门禁、确认节奏、四层规则、验证习惯、文件安全和 Skill 演化路由的干净起点。模板不会自动安装，因为填好的全局 `AGENTS.md` 属于个人配置。

Skill 演化现在支持按轻重分级处理，也加入了“先观察、再建议”的被动触发探针。探针可以记录或建议可能路由，但不会自动执行工作流、改文件、安装工具、提交、推送、发布或操作账号。

## 隐私边界

公开仓库不包含真实触发记录、本机能力数据库、绝对路径、账号资料、私有项目名、日志、截图、对话记录或项目专用来源。

`trigger-candidates.md`、`devolution-ledger.md` 和 `external-skill-registry.md` 都是空白模板；能力数据库和被动触发事件日志只在使用者本机生成，并已被 Git 忽略。

## 安装或更新

克隆或下载仓库后，在仓库根目录运行：

```text
python scripts/install_or_update.py
```

首次安装会要求选择两个不同的快捷入口，并安装完整的六个路由 Skill。无人值守安装时必须显式传入两个选择：

```text
python scripts/install_or_update.py --non-interactive --evolution-trigger "YOUR_EVOLUTION_SHORTCUT" --absorption-trigger "YOUR_ABSORPTION_SHORTCUT"
```

拉取新版仓库后再次运行同一脚本即可更新。脚本默认保留已选入口和本地个人进化：未修改的框架文件会自动升级；检测到本地修改时保留原文件，并把新版放入 `~/.codex/.skill-evolution-updates/` 供使用者比较。

对于还没有安装清单的旧版本，更新器采用保守策略：已有文件不覆盖，新版进入待处理目录。安装器需要 Python 3，且只依赖 Python 标准库。

## 验证

在仓库根目录运行：

```text
python scripts/validate_framework.py
```

验证器会检查 Skill 元数据、目录命名、引用文件、Python 语法、禁止发布的生成文件以及常见隐私泄漏。

## 安全定制

- 长期个人偏好放入个人全局规则，不要提交到公开 Skill。
- 可以从 `templates/global-agents-template/AGENTS.md` 开始建立私有全局规则，但要在本地替换占位符。
- 仓库命令和约定放入该仓库的 `AGENTS.md`。
- 使用 `templates/project-skill-template/` 创建私有项目 Skill。
- `skill-evolution-entry/`、`trigger-candidates.md`、`devolution-ledger.md` 和 `external-skill-registry.md` 属于本地个人数据，更新器永不覆盖。
- 被动触发事件日志也只保留在本地，即使已做脱敏，也不要提交。
- 真实触发记录和本机能力数据库始终保持私有。
- 公开定制版本前重新运行验证器和[隐私检查表](docs/privacy-checklist.md)。

本项目采用 MIT License。
