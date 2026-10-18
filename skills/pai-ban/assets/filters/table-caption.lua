-- =====================================================================
-- pai-ban / assets/filters/table-caption.lua
--
--   这本书的表格题注写成紧跟表格的一行斜体：
--       | …表格… |
--       *表14.1：硬技能与软技能的安全级别对比*
--
--   spec §8 要求题注在**表上方**、9pt、「表 14.1」加粗 + 空格 + 标题、
--   与表间距 4pt。所以本过滤器把它搬上去，并交给
--   \paibantablecaption{表 14.1}{标题}（preamble.tex）排版。
--
--   同时兼容题注本来就写在表上方的情况（英文书 / 后续章节）：
--   只要「题注段落 + 表格」相邻，方向不重要，统一输出成
--   「题注块 + 表格」。
--
--   与 figure-caption.lua 同一套前缀剥离逻辑：Lua 的 pattern 按字节匹配，
--   全角冒号「：」占 3 字节，不能用字符类 [：:]，只能用 plain find。
-- =====================================================================

local is_latex = FORMAT:match("latex") ~= nil

-- 语言开关（zh|en）：build.py 在 main() 里设环境变量 PAIBAN_LANG，
-- 由 pandoc 子进程继承。不设时默认 zh，保持旧版本行为不变。
-- 为什么不用 -M + Meta 函数：pandoc 3.11 的过滤器遍历是**自底向上**的，
-- Blocks 先跑、Meta 最后跑（实测），拿不到语言；加载期 PANDOC_DOCUMENT
-- 又是 nil。环境变量是唯一在 Blocks 里可靠的通道。
-- 用途：题注编号标签「表 14.1」/「Table 14.1」。此前标签写死中文，英文版
-- 会印出「表11.1」——2026-10-18 英文全量构建实测 18 处。
local LANG = (os and os.getenv and os.getenv("PAIBAN_LANG")) or "zh"

local COLON_CN = "："

local function inlines_to_latex(inlines)
  local doc = pandoc.Pandoc({ pandoc.Plain(inlines) })
  return (pandoc.write(doc, "latex"):gsub("[\t\r\n ]+$", ""))
end

local function colon_end(text)
  local i1 = text:find(COLON_CN, 1, true)
  local i2 = text:find(":", 1, true)
  if i1 and (not i2 or i1 < i2) then
    return i1 + #COLON_CN - 1
  elseif i2 then
    return i2
  end
  return nil
end

-- 题注段落：整段一个 Emph/Strong，且以「表14.1：」「表 14.1:」开头
local function caption_only(blk)
  if blk.t ~= "Para" or #blk.content ~= 1 then return nil end
  local emph = blk.content[1]
  if emph.t ~= "Emph" and emph.t ~= "Strong" then return nil end
  local text = pandoc.utils.stringify(emph.content)
  local num = text:match("^表[\t\r\n ]*([%d]+[%.%-][%d]+)")
      or text:match("^[Tt]able[\t\r\n ]*([%d]+[%.%-][%d]+)")
  if not num then return nil end
  local total = colon_end(text)
  if not total then return nil end
  return num, emph.content, total, text
end

-- 剥掉「表14.1：」前缀；前缀落在第一个 Str 里就保留其余行内格式
local function strip_prefix(content, total, text)
  local first = content[1]
  if first and first.t == "Str" and #first.text >= total
      and first.text:sub(1, total) == text:sub(1, total) then
    local out = pandoc.Inlines({})
    local tail = first.text:sub(total + 1)
    if tail ~= "" then out:insert(pandoc.Str(tail)) end
    for i = 2, #content do out:insert(content[i]) end
    return out
  end
  local rest = text:sub(total + 1):gsub("^[\t\r\n ]+", "")
  return pandoc.Inlines({ pandoc.Str(rest) })
end

local function caption_block(num, content)
  -- zh：「表\,14.1」（细空）  en：「Table 14.1」（英文用普通词间空格）
  local label = (LANG == "en") and ("Table " .. num) or ("表\\," .. num)
  return pandoc.RawBlock("latex",
    "\\paibantablecaption{" .. label .. "}{" .. inlines_to_latex(content) .. "}")
end

function Blocks(blocks)
  if not is_latex then return nil end
  local out = pandoc.Blocks({})
  local i, changed = 1, false
  while i <= #blocks do
    local cur, nxt = blocks[i], blocks[i + 1]

    -- 表格 + 紧随其后的题注（本书的写法）
    if cur.t == "Table" and nxt then
      local num, cap_content, total, text = caption_only(nxt)
      if cap_content then
        out:insert(caption_block(num, strip_prefix(cap_content, total, text)))
        out:insert(cur)
        i, changed = i + 2, true
      else
        out:insert(cur); i = i + 1
      end

    -- 题注 + 表格（英文书 / 题注本来就写在上面）
    elseif cur.t == "Para" and nxt and nxt.t == "Table" then
      local num, cap_content, total, text = caption_only(cur)
      if cap_content then
        out:insert(caption_block(num, strip_prefix(cap_content, total, text)))
        out:insert(nxt)
        i, changed = i + 2, true
      else
        out:insert(cur); i = i + 1
      end

    else
      out:insert(cur); i = i + 1
    end
  end
  if not changed then return nil end
  return out
end
