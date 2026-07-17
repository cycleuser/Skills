# AI Attribution Detection / AI 归属信号检测

Rules for detecting AI participation in commits via attribution signals.
Based on Open Delivery Spec (ODS) methodology — reading what tools self-declare, not detecting code style.

## Core Principle / 核心原则

**ODS 是 signal producer（信号生产者），不是 quality oracle（质量裁判）。**
检测到 AI trailer 只代表"工具申报了参与"，不代表代码有问题，也不代表代码没问题。
PASS 只代表未触发策略规则，不代表代码无问题。

归属信号可以被规避（squash + 改写 message），因此度量的是"申报的 AI 使用"，而非"全部 AI 使用"。

## Signal Sources / 信号来源

### 1. Commit Trailers (Primary / 主要)

AI 工具自动添加的归属 trailer，躺在 git 历史里，机器可读：

```bash
# 检测 Co-Authored-By trailer (Claude Code, GitHub Copilot, Cursor 等)
git log "v${PUBLISHED}"..HEAD --pretty=format:"%H %s%n%b" --grep="Co-Authored-By:.*\(noreply\|ai\|anthropic\|openai\|copilot\|cursor\|gemini\|qwen\|deepseek\|kimi\|doubao\|baichuan\|zhipu\)"

# 检测 Assisted-by trailer (Linux kernel 风格)
git log "v${PUBLISHED}"..HEAD --pretty=format:"%H %s%n%b" --grep="Assisted-by:.*\(Claude\|Copilot\|GPT\|Gemini\|Codium\|Cursor\|Aider\|Qwen\|DeepSeek\|Kimi\|Doubao\|Baichuan\|GLM\|Zhipu\)"

# 提取所有 trailer 并解析
git log "v${PUBLISHED}"..HEAD --pretty=format:"--START--%n%H%n%s%n%b%n--END--" | \
  awk '/--START--/{commit=""} /--END--/{print commit} {commit=commit $0 "\n"}' | \
  grep -E "^(Co-Authored-By|Assisted-by|Generated-by|AI-assisted):"
```

### 2. PR Description (Secondary / 辅助)

PR 模板中的手动声明，可靠性低于 trailer，但仍有价值：

```bash
# 检查 PR 描述中的 AI 声明
gh pr view --json body -q .body | grep -iE "(ai[- ]?generated|copilot|claude|gpt|cursor|generated.*ai|ai.*assist)"
```

### 3. Commit Message Keywords (Tertiary / 补充)

提交信息中直接提及 AI 工具：

```bash
# 提交信息含 AI 工具名
git log "v${PUBLISHED}"..HEAD --oneline --grep="\(copilot\|claude\|cursor\|ai[- ]?generated\|gpt\|gemini\|aider\)"
```

## Trailer Format Reference / Trailer 格式参考

### Co-Authored-By (GitHub 风格)

```
Co-Authored-By: Claude <noreply@anthropic.com>
Co-Authored-By: GitHub Copilot <noreply@github.com>
Co-Authored-By: Cursor <noreply@cursor.sh>
```

### Assisted-by (Linux kernel 风格)

```
Assisted-by: Claude:claude-3-opus coccinelle sparse
Assisted-by: Copilot:gpt-4
```

格式：`Assisted-by: <工具名>:<模型版本> <辅助工具列表>`

### Generated-by (完全生成)

```
Generated-by: Claude:claude-3.5-sonnet
```

## Detection Logic / 检测逻辑

```python
def detect_ai_attribution(commit_range):
    """检测 commit 范围内的 AI 归属信号"""
    signals = []

    for commit in commits_in_range:
        # 1. 检查 trailer
        trailers = parse_trailers(commit.body)
        for trailer in trailers:
            if is_ai_trailer(trailer):
                signals.append({
                    "commit": commit.sha,
                    "type": "trailer",
                    "format": trailer.format,  # co-authored | assisted-by | generated-by
                    "tool": extract_tool(trailer),
                    "model": extract_model(trailer),
                    "message": commit.subject
                })

        # 2. 检查提交信息关键词
        if has_ai_keywords(commit.subject):
            signals.append({
                "commit": commit.sha,
                "type": "message_keyword",
                "tool": "unknown",
                "model": "unknown"
            })

    return signals

def is_ai_trailer(trailer):
    """判断是否为 AI 归属 trailer"""
    ai_patterns = [
        r"Co-Authored-By:.*noreply@(anthropic|github|cursor|openai)\.com",
        r"Co-Authored-By:.*(Claude|Copilot|Cursor|GPT|Gemini|Aider)",
        r"Assisted-by:\s*(Claude|Copilot|GPT|Gemini|Codium|Cursor|Aider|Qwen|DeepSeek|Kimi|Doubao|Baichuan|GLM|Zhipu)",
        r"Generated-by:\s*(Claude|Copilot|GPT|Gemini|Aider|Qwen|DeepSeek|Kimi|Doubao|Baichuan|GLM|Zhipu)",
    ]
    return any(re.match(p, trailer, re.I) for p in ai_patterns)
```

## Attribution Report Format / 归属报告格式

```markdown
## AI Attribution Summary / AI 归属汇总

**AI 参与度/AI Participation**: { commits_with_ai } / { total_commits } commits ({percentage}%)
**涉及工具/Tools Detected**: { tool_list }
**归属格式/Attribution Formats**: { co-authored | assisted-by | generated-by }

### Per-Commit Attribution / 逐提交归属

| Commit | Subject | AI Tool | Model | Format |
|--------|---------|---------|-------|--------|
| abc1234 | feat(auth): add JWT | Claude | claude-3.5-sonnet | Co-Authored-By |
| def5678 | fix(api): null check | Copilot | gpt-4 | Co-Authored-By |
| ghi9012 | docs: update README | — | — | — (纯人工) |

### Risk Multiplier / 风险乘数

| AI 参与度 | 乘数 | 说明 |
|-----------|------|------|
| 0% | 1.0x | 纯人工变更，基础债务 |
| 1-30% | 1.1x | 轻度 AI 辅助 |
| 31-60% | 1.2x | 中度 AI 辅助 |
| 61-90% | 1.3x | 重度 AI 辅助 |
| 91-100% | 1.5x | 几乎全 AI 生成，需重点审查 |

注意：乘数只作为风险加权，不直接判定 BLOCK。干净的 100% AI 变更得分可接近 0。
```

## Scoring Philosophy / 打分哲学

**用 AI 不是罪。** AI 参与度不直接等于债务。

```
技术债 = (基础债务) × (AI 风险乘数)

基础债务 = 高危 issue 数 × 3
        + 中危 issue 数 × 1
        + 覆盖率缺口 × 0.5
        + 重复代码块数 × 0.3

AI 风险乘数 = 1.0 ~ 1.5 (基于 AI 参与度)
```

- 干净的 100% AI 变更（无 issue、测试充分）得分接近 0
- 脏的 0% AI 变更（高危 issue）得分依然很高
- AI 参与只作为风险信号放大器，不作为扣分项

## Review Tier Routing / 审查分级路由

根据 AI 参与度和质量信号，自动路由审查等级：

```rego
package ba-guan.routing

default review_tier := "standard"

# 低风险：AI 参与低 + 无高危 → 快速通道
review_tier := "auto" if {
    ai_participation < 0.3
    count(high_severity_issues) == 0
    total_lines < 200
}

# 高风险：AI 参与高 + 有高危 → 升级审查
review_tier := "elevated" if {
    ai_participation > 0.6
    count(high_severity_issues) > 0
}

# 高风险：全 AI 生成 + 大变更 → 必须人工审查
review_tier := "elevated" if {
    ai_participation > 0.9
    total_lines > 500
}

# 高风险：安全相关文件有 AI 参与 → 升级
review_tier := "elevated" if {
    ai_participation > 0
    touches_security_files == true
}
```

| Tier | 含义 | 动作 |
|------|------|------|
| auto | 低风险，可自动合并 | 跳过人工审查，CI 通过即合并 |
| standard | 常规风险 | 标准审查流程 |
| elevated | 高风险 | 请求额外 reviewer，必须人工确认 |

## Edge Cases / 边界情况

- **Squash merge 抹掉 trailer**: ODS 无法检测，只能度量"申报的 AI 使用"。审查时提醒：squash 会丢失归属信号
- **多个 AI 工具同时参与**: 全部列出，不合并计数
- **trailer 格式不规范**: 记录但不阻塞，在报告中标注"格式异常"
- **人工提交但用了 AI 补全**: 无法检测，这是 ODS 的固有局限

## See Also / 相关规则

- [change-detection.md](change-detection.md) — 变更检测（归属检测在变更检测后执行）
- [review-roles.md](review-roles.md) — 审查角色（elevated tier 触发额外角色）
- [version-bump.md](version-bump.md) — 版本规则（AI 参与度影响版本建议）