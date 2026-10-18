-- =====================================================================
-- assets/filters/break-long-tokens.lua
--   给"没有空格、也没有 TeX 断点"的超长 ASCII token 插 \allowbreak。
--   对应 rules/design-spec.md §7/§11（零 Overfull、零越界）。
--
-- 为什么必须做
-- ------------
-- 英文源文里有一批引用键写成
--   [Brown+2020+Language+Models+are+Few-Shot+Learners+2005.14165]
-- 共 73 个字符、内部只有 `+`。TeX 只在空白、连字符、显式 \discretionary
-- 处断行，`+` 不是断点 → 整个 token 视作一个词。115mm 版心（326pt）里
-- 11pt Times 装不下（实测 Overfull 148.55pt，直接把行顶到纸边，verify 的
-- 「内容越出纸边」与「内容越出版心」两条同时红）。
--
-- 中文源文里没有这种 token（`+` 连接的长键只在英文版出现，CN 计数 0），
-- 所以本过滤器对中文书是严格的 no-op —— 不会改变 CN 版的任何一行。
--
-- 做法
-- ----
-- 只处理 Str 节点（行内文本），条件是：
--   * 输出目标是 LaTeX（其他格式原样放行）；
--   * **纯 ASCII**（任何一个字节 >127 就跳过）。这一条是关键：中文没有
--     空格，一整段中文就是一个 Str，若放行会把「表格+正文+证据」这种
--     中文短语切开 —— 实测 CN chapter-02 会多出 12 处 \allowbreak，全是
--     误伤。引用键是纯 ASCII，中文段落不是，用这一条把两者干净分开，
--     从而保证本过滤器对中文书是严格 no-op。
--   * 字节长度 >= MIN_LEN（短词如 C++、GPT-4+ 不动）；
--   * 含 ASCII '+'。
-- 在 '+' 之后插 RawInline("latex", "\\allowbreak{}")。{} 的作用是把紧随
-- 其后的 Str 与前一个词分开，避免 \allowbreak 变成下一个词的前缀。
--
-- 为什么用 \allowbreak 而不是 U+200B：XeTeX 不把 U+200B 当断点（它只是
-- 一个零宽字符，不是 glue/penalty），实测无效；\allowbreak = \penalty0，
-- 在词内也能断。
--
-- 阈值 24 的依据：现有最长普通词（含 URL 之外的标识符）不足 20 字节；
-- 真正需要断的都是 60+ 字节的引用键。宁可阈值偏大（少插断点），也不要
-- 把正常单词切开。
-- =====================================================================

local MIN_LEN = 24

-- ---------------------------------------------------------------------
-- 长 URL 段落：局部加大 \emergencystretch（§7 的"词距不被拉伸"保障）
--
-- 为什么需要：preamble 的全局 \emergencystretch=6em 只够让"整本书能排下去"。
-- 正文里带 40+ 字符 HTTP 链接的段落，链接本身是一个长不可断块，TeX 为了把
-- 它塞进 115mm 行宽，会把同一个段落里其它行的词距拉开（实测英文版有的行
-- 拉到 3 倍以上）。这里只对"含长 URL 的段落"把 emergencystretch 抬到 12em：
-- TeX 只有在真的排不下时才用这份伸缩量，排得下的段落一个字节都不变，
-- 所以不会动到没有 URL 的正文（也不会改版面网格）。
--
-- 为什么不用 \RaggedRight：那会把整段改成左齐右不齐——对 1–2 句的短段
-- 观感差异明显；emergencystretch 是"只在必要时生效"的软闸。
local URL_MIN_LEN = 40
local URL_PAT = "https?://[%w%-%._~:/%?#%[%]@!%$&'%(%)%*%+,;=]+"

local function has_long_url(inlines)
  local text = pandoc.utils.stringify(inlines)
  for u in text:gmatch(URL_PAT) do
    if #u >= URL_MIN_LEN then return true end
  end
  return false
end

function Para(el)
  if not FORMAT:match("latex") then return nil end
  if not has_long_url(el.content) then return nil end
  local out = pandoc.Inlines({ pandoc.RawInline("latex",
    "{\\setlength{\\emergencystretch}{12em}") })
  out:extend(el.content)
  out:insert(pandoc.RawInline("latex", "\\par}"))
  return pandoc.Para(out)
end

local function split_on_plus(s)
  local parts, i = {}, 1
  while true do
    local j = s:find("+", i, true)
    if not j then
      parts[#parts + 1] = s:sub(i)
      break
    end
    parts[#parts + 1] = s:sub(i, j)     -- 含 '+'
    i = j + 1
  end
  return parts
end

function Str(el)
  if not FORMAT:match("latex") then return nil end
  local s = el.text
  if #s < MIN_LEN then return nil end
  if not s:find("+", 1, true) then return nil end

  -- 纯 ASCII 守卫：含任何非 ASCII 字节（中文、全角标点、emoji）一律放行
  for i = 1, #s do
    if s:byte(i) > 127 then return nil end
  end
  
  local parts = split_on_plus(s)
  if #parts < 2 then return nil end

  local out = pandoc.Inlines({})
  for k, p in ipairs(parts) do
    if k > 1 then
      out:insert(pandoc.RawInline("latex", "\\allowbreak{}"))
    end
    if p ~= "" then out:insert(pandoc.Str(p)) end
  end
  return out
end
