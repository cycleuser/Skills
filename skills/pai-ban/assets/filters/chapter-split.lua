-- =====================================================================
-- pai-ban / assets/filters/chapter-split.lua
--
--   把 Markdown 的 H1「第2章 LLM API 与本地部署」/「Chapter 2: LLM API…」
--   拆成「编号 + 标题」，输出 raw LaTeX 章命令：
--       \paibanchapter{2}{LLM API 与本地部署}
--       \paibanchapter*{Preface}        （无编号：前言 / 参考文献 / 附录）
--
--   为什么必须拆（spec §4）：章首页的章号是 48pt 大字、标题是 22pt，
--   两者字号与位置完全不同；若标题里留着「第2章」字样，章号会重复出现
--   （spec §11「重复编号 = 0」）。
--
--   拆完之后三处依赖它：
--     * 目录条目   —— \addcontentsline{toc}{chapter}{标题}
--     * PDF 书签   —— hyperref 由同一个锚点（\phantomsection）生成
--     * 页眉       —— \markboth{标题}{标题}（spec §6 奇数页页眉 = 章标题）
--   所以标题必须只出现一次、且是「纯标题」。
--
--   同时接管 H2/H3/H4：源文里节号（2.1）是正文文本，不能让 LaTeX 再自动
--   编号（否则「2.1 2.1 …」）。\paibansection 内部用 \@startsection 排版、
--   手工 \addcontentsline 收目录，见 assets/preamble.tex §2.2。
--
--   页码体制（spec §6）：目录/前言 = 罗马数字，第一个编号章起 = 阿拉伯
--   数字 1。pandoc 的 book 模板会无条件在正文前插 \mainmatter，本技能把
--   它改成空操作（preamble.tex），改由这里在第一个编号章前发
--   \paibanmainmatter。
--
--   UTF-8 陷阱（实测踩过，务必看）：
--   Lua 的 `%s` 在本机 Lua 5.4 上会把字节 0xA0 当作空白（Latin-1 的
--   NBSP）。0xA0 又是大量汉字 UTF-8 编码的尾字节（如「习」= E4 B9 A0），
--   于是 `s:gsub("%s+$","")` 会把「练习」的最后一个字节切掉，XeTeX 收到
--   半个字符 → 日志里 "Missing character (U+FFFD)" + 正文乱码。
--   本文件所有空白匹配一律用显式 ASCII 类 [\t\r\n ]，禁止 %s。
--   同理，含全角字符的**字符类**（如 [：:]）也不可用：Lua 的字符类按字节
--   匹配，全角冒号占 3 字节，会被当成 3 个不同字符 —— 一律改成 plain find。
-- =====================================================================

local is_latex = FORMAT:match("latex") ~= nil

local WS = "[\t\r\n ]"

local function trim_ascii(s)
  return (s:gsub("^" .. WS .. "+", ""):gsub(WS .. "+$", ""))
end

-- 去掉标题前导的分隔符（「第2章：标题」「Chapter 2. 标题」）
local SEPS = { "：", ":", "、", "，", "．", "。", ".", "—", "–", "-" }
local function strip_seps(t)
  local changed = true
  while changed do
    changed = false
    t = trim_ascii(t)
    for _, sep in ipairs(SEPS) do
      if t:sub(1, #sep) == sep then
        t = t:sub(#sep + 1)
        changed = true
      end
    end
  end
  return t
end

-- ---------------------------------------------------------------------
-- 中文数字 → 整数（第二十一章 → 21）。覆盖 1–999，够用于章节。
-- ---------------------------------------------------------------------
local CN_DIGIT = {
  ["零"] = 0, ["〇"] = 0,
  ["一"] = 1, ["二"] = 2, ["两"] = 2, ["三"] = 3, ["四"] = 4,
  ["五"] = 5, ["六"] = 6, ["七"] = 7, ["八"] = 8, ["九"] = 9,
}

local function cn_number(s)
  if not s:match("^[零〇一二两三四五六七八九十百]+$") then return nil end
  local total, num = 0, 0
  for _, cp in utf8.codes(s) do
    local ch = utf8.char(cp)
    if ch == "十" then
      if num == 0 then num = 1 end
      total = total + num * 10
      num = 0
    elseif ch == "百" then
      if num == 0 then num = 1 end
      total = total + num * 100
      num = 0
    else
      local d = CN_DIGIT[ch]
      if d == nil then return nil end
      num = num * 10 + d
    end
  end
  return total + num
end

-- ---------------------------------------------------------------------
-- 纯文本标题拆分：返回 number(string|nil), title(string)
-- ---------------------------------------------------------------------
local function split_title(text)
  local t = trim_ascii(text)

  -- 第2章 / 第 2 章
  local num, rest = t:match("^第" .. WS .. "*(%d+)" .. WS .. "*章(.*)$")
  if num then return num, strip_seps(rest) end

  -- 第十二章
  local cn, rest2 = t:match("^第" .. WS .. "*([零〇一二两三四五六七八九十百]+)" .. WS .. "*章(.*)$")
  if cn then
    local n = cn_number(cn)
    if n then return tostring(n), strip_seps(rest2) end
  end

  -- Chapter 2 / CHAPTER 2: xxx
  local en, rest3 = t:match("^[Cc][Hh][Aa][Pp][Tt][Ee][Rr]" .. WS .. "*(%d+)(.*)$")
  if en then return en, strip_seps(rest3) end

  return nil, t
end

-- ---------------------------------------------------------------------
-- Inline → LaTeX 片段。用 pandoc.write 渲染，保证 _ % # & $ { } 被正确
-- 转义（手写 gsub 一定会漏）。
-- ---------------------------------------------------------------------
local function inlines_to_latex(inlines)
  local doc = pandoc.Pandoc({ pandoc.Plain(inlines) })
  return trim_ascii(pandoc.write(doc, "latex"))
end

local function drop_leading_space(il)
  local out = pandoc.Inlines({})
  local started = false
  for _, el in ipairs(il) do
    if not started and (el.t == "Space" or el.t == "SoftBreak") then
      -- 吞掉编号与标题之间的空白
    else
      started = true
      out:insert(el)
    end
  end
  return out
end

-- ---------------------------------------------------------------------
-- 从 inlines 里剥掉编号前缀。快路径保留行内格式（行内代码 / 强调），
-- 慢路径（前缀跨多个 inline）退化为纯文本标题 —— 宁可丢格式，
-- 也绝不让编号重复。
-- ---------------------------------------------------------------------
local function take_prefix(il)
  if #il == 0 then return nil, il end
  local first = il[1]

  if first.t == "Str" then
    -- 第2章xxx / 第2章：xxx（同一 Str 内）
    local n, tail = first.text:match("^第" .. WS .. "*(%d+)" .. WS .. "*章(.*)$")
    if n then
      local rest = pandoc.Inlines({})
      tail = strip_seps(tail)
      if tail ~= "" then rest:insert(pandoc.Str(tail)) end
      for i = 2, #il do rest:insert(il[i]) end
      return n, drop_leading_space(rest)
    end

    -- 第十二章
    local cn, tail2 = first.text:match("^第" .. WS .. "*([零〇一二两三四五六七八九十百]+)" .. WS .. "*章(.*)$")
    if cn then
      local n2 = cn_number(cn)
      if n2 then
        local rest = pandoc.Inlines({})
        tail2 = strip_seps(tail2)
        if tail2 ~= "" then rest:insert(pandoc.Str(tail2)) end
        for i = 2, #il do rest:insert(il[i]) end
        return tostring(n2), drop_leading_space(rest)
      end
    end

    -- Chapter 2: xxx（同一 Str）
    local en, tail3 = first.text:match(
      "^[Cc][Hh][Aa][Pp][Tt][Ee][Rr]" .. WS .. "*(%d+)(.*)$")
    if en then
      local rest = pandoc.Inlines({})
      tail3 = strip_seps(tail3)
      if tail3 ~= "" then rest:insert(pandoc.Str(tail3)) end
      for i = 2, #il do rest:insert(il[i]) end
      return en, drop_leading_space(rest)
    end

    -- Chapter / CHAPTER + Space + "2: xxx"
    if first.text:match("^[Cc][Hh][Aa][Pp][Tt][Ee][Rr]$") and #il >= 3
        and il[2].t == "Space" and il[3].t == "Str" then
      local nn, tail4 = il[3].text:match("^(%d+)(.*)$")
      if nn then
        local rest = pandoc.Inlines({})
        tail4 = strip_seps(tail4)
        if tail4 ~= "" then rest:insert(pandoc.Str(tail4)) end
        for i = 4, #il do rest:insert(il[i]) end
        return nn, drop_leading_space(rest)
      end
    end
  end

  -- 慢路径：整条标题按纯文本判断
  local text = pandoc.utils.stringify(il)
  local num, rest_text = split_title(text)
  if num then
    return num, pandoc.Inlines({ pandoc.Str(rest_text) })
  end
  return nil, il
end

local mainmatter_done = false

function Header(h)
  if not is_latex then return nil end

  if h.level == 1 then
    local num, rest = take_prefix(h.content)
    if num then
      local title_tex = inlines_to_latex(rest)
      local blocks = {}
      if not mainmatter_done then
        mainmatter_done = true
        blocks[#blocks + 1] = pandoc.RawBlock("latex", "\\paibanmainmatter")
      end
      blocks[#blocks + 1] = pandoc.RawBlock(
        "latex", "\\paibanchapter{" .. num .. "}{" .. title_tex .. "}")
      return blocks
    end
    return pandoc.RawBlock("latex",
      "\\paibanchapter*{" .. inlines_to_latex(h.content) .. "}")
  end

  if h.level == 2 then
    return pandoc.RawBlock("latex",
      "\\paibansection{" .. inlines_to_latex(h.content) .. "}")
  elseif h.level == 3 then
    return pandoc.RawBlock("latex",
      "\\paibansubsection{" .. inlines_to_latex(h.content) .. "}")
  elseif h.level == 4 then
    return pandoc.RawBlock("latex",
      "\\paibansubsubsection{" .. inlines_to_latex(h.content) .. "}")
  end
  return nil
end
