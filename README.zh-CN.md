# Codex Skill 进化框架

[English](README.md)

这是一个可复用、可公开分享且不含个人信息的 Codex Skill 进化框架。它通过分层路由避免把所有规则堆进一个巨大的提示词。

完整框架包含六个独立 Skill：

1. `skill-evolution-core`：创建、更新、拆分、合并、验证和吸收 Skill。
2. `skill-evolution-router`：判断长期规则和经验应该保存在哪里。
3. `project-rules-router`：处理非简单项目任务前选择对应的项目规则。
4. `coding-debug-rules`：排查 Shell、编码、路径、依赖、构建和测试问题。
5. `research-verification`：通过当前公开来源验证工具、API、版本和报错行为。
6. `codex-capability-router`：从已安装的 Skill、插件、应用和 MCP 工具中选择合适能力。

默认保留两个中文快捷触发词：`进化` 用于完整进化流程，`吞噬` 用于吸收并整合外部能力。安装后可以自行修改或删除。

## 隐私边界

公开仓库不包含真实触发记录、本机能力数据库、绝对路径、账号资料、私有项目名、日志、截图、对话记录或项目专用来源。

`trigger-candidates.md` 和 `external-skill-registry.md` 都是空白模板；能力数据库只在使用者本机生成，并已被 Git 忽略。

## 安装

将 `skills/` 下需要的目录复制到 `~/.codex/skills/`。若要获得完整路由功能，请安装全部六个 Skill。

框架主体只使用 Markdown 和 YAML；本机能力索引与验证脚本需要 Python 3，且只依赖 Python 标准库。

## 验证

在仓库根目录运行：

```text
python scripts/validate_framework.py
```

验证器会检查 Skill 元数据、目录命名、引用文件、Python 语法、禁止发布的生成文件以及常见隐私泄漏。

## 安全定制

- 长期个人偏好放入个人全局规则，不要提交到公开 Skill。
- 仓库命令和约定放入该仓库的 `AGENTS.md`。
- 使用 `templates/project-skill-template/` 创建私有项目 Skill。
- 真实触发记录和本机能力数据库始终保持私有。
- 公开定制版本前重新运行验证器和[隐私检查表](docs/privacy-checklist.md)。

本项目采用 MIT License。
