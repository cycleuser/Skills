-- =====================================================================
-- pai-ban / assets/filters/figure-caption.lua
--
--   这本书的图是「图片段落 + 紧跟一个斜体题注段落」：
--       ![fig20-llm-evolution](figures/pdf/fig20-llm-evolution.pdf)
--       *图20.1：LLM能力演进时间线。…*
--   build.py 已经把 alt 清空（否则 pandoc 会生成 "Figure N: 文件名" 伪题注
--   并把图变成浮动体）。本过滤器把这两段合成一个**不浮动**的 minipage：
--
--       \paibanfigure{\paibaninclude{…}}{\paibanfiglabel{图 2.1}题注…}
--
--   为什么不用 \begin{figure}：
--     * 浮动体位置不可控，图会跑到页顶/页底，与紧跟其后的题注分离；
--     * spec §9 要求「图与题注必须同页」——minipage 不可分页，天然满足；
--     * minipage 里的图高上限 0.72 版心高（preamble 的 \paibaninclude），
--       所以它永远装得进一页（零裁切）。
--
--   规格：§9（居中、最大宽度 = 版心宽、不放大超过原始尺寸 1.15 倍、
--   题注在图下方 9pt、"图 2.1" 加粗 + 空格 + 标题、与图间距 4pt）。
-- =====================================================================

local is_latex = FORMAT:match("latex") ~= nil

local function inlines_to_latex(inlines)
  local doc = pandoc.Pandoc({ pandoc.Plain(inlines) })
  return (pandoc.write(doc, "latex"):gsub("[\t\r\n ]+$", ""))
end

-- 段落里是否"只有一张图"（允许图片被 link 包住）
local function image_only(blk)
  if blk.t ~= "Para" then return nil end
  local found
  for _, el in ipairs(blk.content) do
    if el.t == "Image" then
      if found then return nil end
      found = el
    elseif el.t == "Space" or el.t == "SoftBreak" then
      -- 忽略
    elseif el.t == "Link" then
      for _, sub in ipairs(el.content) do
        if sub.t == "Image" then
          if found then return nil end
          found = sub
        end
      end
    else
      return nil
    end
  end
  return found
end

-- 题注段落：整段是一个 Emph，且以「图2.1：」「图 2.1:」「Fig. 2.1」开头
--
-- 注意：Lua 的 pattern 是**按字节**的，`[：:]` 会被当成 4 个字节的字符类，
-- 只能匹配「：」的 1/3 —— 实测会切在 UTF-8 字符中间，输出两个乱码字节。
-- 所以冒号位置一律用 plain find（第三个参数 true），不做字符类匹配。
local COLON_CN = "："   -- U+FF1A，3 字节

-- 语言开关（zh|en）：环境变量 PAIBAN_LANG（build.py 设，pandoc 继承）；
-- 不设时默认 zh。不要改成 Meta：pandoc 3.11 里 Blocks 先于 Meta 执行。
-- 用途：图题编号标签「图 2.1」/「Figure 2.1」。写死中文会让英文版印出「图」。
local LANG = (os and os.getenv and os.getenv("PAIBAN_LANG")) or "zh"
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

local function caption_only(blk)
  if blk.t ~= "Para" or #blk.content ~= 1 then return nil end
  local emph = blk.content[1]
  if emph.t ~= "Emph" and emph.t ~= "Strong" then return nil end
  local text = pandoc.utils.stringify(emph.content)
  local num = text:match("^图[\t\r\n ]*([%d]+[%.%-][%d]+)") or text:match("^图[\t\r\n ]*([%d]+)")
  if not num then
    num = text:match("^[Ff]ig%.?[\t\r\n ]*([%d]+[%.%-][%d]+)") or text:match("^[Ff]ig%.?[\t\r\n ]*([%d]+)")
  end
  if not num then
    num = text:match("^[Ff]igure[\t\r\n ]*([%d]+[%.%-][%d]+)")
        or text:match("^[Ff]igure[\t\r\n ]*([%d]+)")
  end
  if not num then return nil end
  local total = colon_end(text)
  if not total then return nil end
  return num, emph.content, total, text
end

-- 从题注 inlines 里剥掉「图2.1：」前缀（前缀总长度 = total 字节）。
-- 前缀落在第一个 Str 里就保留其余行内格式；否则退化为纯文本（不丢内容）。
local function strip_prefix(content, total, text)
  local out = pandoc.Inlines({})
  local first = content[1]
  if first and first.t == "Str" and #first.text >= total
      and first.text:sub(1, total) == text:sub(1, total) then
    local tail = first.text:sub(total + 1)
    if tail ~= "" then out:insert(pandoc.Str(tail)) end
    for i = 2, #content do out:insert(content[i]) end
    return out
  end
  local rest = text:sub(total + 1):gsub("^[\t\r\n ]+", "")
  return pandoc.Inlines({ pandoc.Str(rest) })
end

local function figure_block(img, num, cap_inlines, source_latex)
  local path = img.src
  local label = ""
  if num then
    label = (LANG == "en") and ("\\paibanfiglabel{Figure " .. num .. "}")
        or ("\\paibanfiglabel{图\\," .. num .. "}")
  end
  local cap = label .. inlines_to_latex(cap_inlines)
  -- 来源行（> 数据来源：…）如果紧跟在题注后面，塞进同一个放置容器：
  -- inline/wide 走同一个 minipage，rotated 走同一个旋转盒 —— 三种放置下
  -- 来源行都不会与图分离（§9）。
  if source_latex and source_latex ~= "" then
    cap = cap .. "\\paibansource{" .. source_latex .. "}"
  end
  return pandoc.RawBlock("latex", "\\paibanplaced{" .. path .. "}{" .. cap .. "}")
end

-- 来源块：`> 数据来源：…` / `> Source: …` / `> 来源：…`
local SOURCE_PREFIX = { "数据来源", "资料来源", "来源", "Source", "Data source", "Sources" }
local function source_only(blk)
  if blk.t ~= "BlockQuote" then return nil end
  local text = pandoc.utils.stringify(blk)
  local head = text:gsub("^%s+", "")
  for _, p in ipairs(SOURCE_PREFIX) do
    if head:sub(1, #p) == p then
      local tex = pandoc.write(pandoc.Pandoc(blk.content), "latex")
      tex = tex:gsub("^%s+", ""):gsub("%s+$", ""):gsub("\n+", " ")
      return tex
    end
  end
  return nil
end

function Blocks(blocks)
  if not is_latex then return nil end
  local out = pandoc.Blocks({})
  local i = 1
  local changed = false
  while i <= #blocks do
    local img = image_only(blocks[i])
    if img then
      local nxt = blocks[i + 1]
      local num, cap_content, total, text = nil, nil, nil, nil
      if nxt then num, cap_content, total, text = caption_only(nxt) end
      if cap_content then
        -- 题注之后可能紧跟来源行：一起吞进放置容器
        local j = i + 2
        while j <= #blocks and blocks[j].t == "Para"
              and pandoc.utils.stringify(blocks[j]) == "" do
          j = j + 1
        end
        local src = nil
        if j <= #blocks then src = source_only(blocks[j]) end
        out:insert(figure_block(img, num, strip_prefix(cap_content, total, text), src))
        if src then
          i = j + 1          -- 图 + 题注 + 来源行
        else
          i = i + 2          -- 图 + 题注
        end
        changed = true
      else
        -- 没有题注的图：仍然居中、按清单裁边限宽限高
        out:insert(pandoc.RawBlock("latex", "\\paibanplacedonly{" .. img.src .. "}"))
        i = i + 1
        changed = true
      end
    else
      out:insert(blocks[i])
      i = i + 1
    end
  end
  if not changed then return nil end
  return out
end
