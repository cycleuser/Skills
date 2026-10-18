-- =====================================================================
-- assets/filters/table-widths.lua
--   pandoc Lua filter：给每张表写入"相对列宽"（→ p{} 折行列）+ 长 ASCII
--   片段插断点。对应 rules/design-spec.md §8 与 §11「零表格越出版心」。
--
-- 为什么必须做
-- ------------
-- pandoc 的 LaTeX writer 只在 colspec 带宽度时输出可折行的 p{} 列；否则
-- 输出自然宽度列（\begin{longtable}[]{@{}lll@{}}），长单元格不换行。
-- 115mm 版心（326pt）里，自然宽度列的表格必然冲出纸边。
--
-- 做法（启发式，不读版面参数）
-- ---------------------------
-- 1. 每列取"最长单元格"的显示宽度（CJK/全角按 2 计；组合符/零宽按 0）；
-- 2. 以该长度的平方根为权重（线性分配会让最长列吃掉整页；平方根 = 承认
--    长度边际收益递减，短列也能保住可读宽度）；
-- 3. 归一化到合计 1.0，夹在 [0.08, 0.55]；
-- 4. 夹紧用注水法（water-filling）：触限的列定死，剩余空间在未定死的列
--    之间按权重再分，直到稳定 → 合计严格 1.0；
-- 5. 单列下限还要兜住"该列最长不可断 token"的实际宽度。TeX 只在空白与
--    连字符后可断，`/` `:` `.` 都不是断点；p{} 列宽放不下一个
--    OpenAI/Anthropic/xAI 就会压到隔壁列的字上。两个手段一起用：
--    下限按 token 反推列宽，同时给长 token 的 / : . _ 后插 \allowbreak。
--
-- pandoc 把 (宽度 × (行宽 - 2·(列数-1)·tabcolsep)) 写进 p{}，已经扣掉列
-- 间距，所以合计 1.0 不会因为 \tabcolsep 溢出。生成形态：
--   >{\raggedright\arraybackslash}p{(\linewidth - 6\tabcolsep) * \real{0.1993}}
-- \real 来自 calc、\arraybackslash 来自 array（preamble.tex 已显式加载）。
--
-- 只用 pandoc 内置 API（pandoc.utils.stringify / utf8），不依赖 luarocks。
-- =====================================================================

local MIN_W = 0.08   -- 单列下限：给「序号/1/2/3」这类极短列兜底
local CAP_W = 0.55   -- 常规上限：单列不超过 55%

-- 只用于"token 下限"估算，不参与相对分配。与 preamble.tex 一致：
--   版心宽 115mm = 326pt；表内 9pt Times New Roman 的 ASCII 平均字宽约
--   4.5pt，取 4.7 略偏宽（宁可列宽多给几 pt，也不能字叠字）；tabcolsep 4pt。
-- 改了纸张/边距/字号要跟着改；忘了改也只是下限估偏，方向是"列偏宽"。
local TEXTWIDTH_PT = 326.0
local PT_PER_UNIT = 4.7
local TABCOLSEP_PT = 4.0

-- 上限的可行性修正
-- ----------------
-- 「合计 = 1.0」与「单列 ≤ 0.55」在列数少时数学上不相容：
--   n=2 时 0.55 + 0.08 = 0.63 < 1 —— 另一列被迫拿 0.45，观感灾难。
-- 所以上限放宽到 1 - MIN_W*(n-1)：n=2→0.92、3→0.84、4→0.76、5→0.68、
-- n≥7 时回到 0.55。列数一多 0.55 自动生效，规则本意（防单列独吞）不变。
local function cap_for(n)
  local relaxed = 1.0 - MIN_W * (n - 1)
  if relaxed > CAP_W then return relaxed end
  return CAP_W
end

-- 单个字符的显示宽度（0 / 1 / 2）
-- 依据 Unicode East Asian Width 的 Wide/Fullwidth 区间（中日常用字、全角
-- 标点、圈码、假名、韩文）。组合符与零宽字符不占位。
local ZERO_W = {
  [0x200B] = true, [0x200C] = true, [0x200D] = true, [0xFE0F] = true,
  [0xFE00] = true, [0xFE01] = true, [0xFE02] = true, [0xFE03] = true,
}

local function char_width(cp)
  if ZERO_W[cp] then return 0 end
  if (cp >= 0x0300 and cp <= 0x036F) then return 0 end            -- combining
  if (cp >= 0x1100 and cp <= 0x115F) then return 2 end            -- Hangul Jamo
  if (cp >= 0x2E80 and cp <= 0x303E) then return 2 end            -- CJK 部首/标点
  if (cp >= 0x3041 and cp <= 0x33FF) then return 2 end            -- 假名/CJK兼容
  if (cp >= 0x3400 and cp <= 0x4DBF) then return 2 end            -- CJK 扩展A
  if (cp >= 0x4E00 and cp <= 0x9FFF) then return 2 end            -- CJK 基本区
  if (cp >= 0xA000 and cp <= 0xA4CF) then return 2 end            -- 彝文
  if (cp >= 0xAC00 and cp <= 0xD7A3) then return 2 end            -- 韩文音节
  if (cp >= 0xF900 and cp <= 0xFAFF) then return 2 end            -- CJK 兼容表意
  if (cp >= 0xFE30 and cp <= 0xFE6F) then return 2 end            -- CJK 兼容形式
  if (cp >= 0xFF00 and cp <= 0xFF60) then return 2 end            -- 全角 ASCII
  if (cp >= 0xFFE0 and cp <= 0xFFE6) then return 2 end            -- 全角符号
  if (cp >= 0x1F300 and cp <= 0x1F9FF) then return 2 end          -- emoji
  if (cp >= 0x20000 and cp <= 0x3FFFD) then return 2 end          -- CJK 扩展B+
  return 1
end

local function display_width(s)
  local w = 0
  for _, cp in utf8.codes(s) do w = w + char_width(cp) end
  return w
end

-- 最长"不可断片段"的显示宽度。
-- TeX 只在空白与连字符后可断；CJK 之间可断；`/` `:` `.` 在普通文字里不断。
-- 与本 filter 的 add_breakpoints 保持一致：长于 14 单位的 ASCII 片段会被插
-- \allowbreak，所以这类片段要按 / : . _ 再切一次，否则下限估得过大，把真正
-- 的长文本列挤没。
local TOKEN_BREAK_MIN = 14
local BREAK_CHARS = { [0x2F] = true, [0x3A] = true, [0x2E] = true, [0x5F] = true }

local function classify(cp)
  -- 0 = 可断（空白/连字符/CJK），1 = 普通字符
  if cp == 0x20 or cp == 0x2D or cp == 0x09 or cp == 0x00A0 then return 0 end
  if char_width(cp) == 2 then return 0 end
  return 1
end

local function longest_token(s)
  local best, cur = 0, 0
  local run = {}
  local function flush()
    if cur > TOKEN_BREAK_MIN then
      local seg = 0
      for _, cp in ipairs(run) do
        seg = seg + 1
        if BREAK_CHARS[cp] then
          if seg > best then best = seg end
          seg = 0
        end
      end
      if seg > best then best = seg end
    elseif cur > best then
      best = cur
    end
    cur, run = 0, {}
  end
  for _, cp in utf8.codes(s) do
    if classify(cp) == 0 then
      flush()
    else
      cur = cur + 1
      run[#run + 1] = cp
    end
  end
  flush()
  return best
end

local function cell_text(cell)
  return pandoc.utils.stringify(cell)
end

local n_tables, n_cols_total, width_hist = 0, 0, {}
local n_breakpoints = 0
local detail = {}
local is_latex = FORMAT:match("latex") ~= nil

-- ---------------------------------------------------------------------
-- 给长 ASCII 片段插断点（仅 LaTeX 目标）
-- ---------------------------------------------------------------------
-- 断点落在 / : . _ 之后（URL/包名/型号名的天然分隔符），观感与 \url 一致。
-- 阈值 14 单位：短 token（qwen3.5:122b = 12、DeepSeek = 8）本来塞得进。
-- 只动 Str（不改 Code/Math）；一个 Str 里可能混着 CJK（"Codex全线瘫痪"），
-- 所以按"ASCII 可见字符段"扫描，只对段内超阈值的部分插断点。
local function emit_ascii_run(run, out)
  if #run > TOKEN_BREAK_MIN and run:find("[/:._]") then
    local pieces, cur = {}, ""
    for ch in run:gmatch(".") do
      cur = cur .. ch
      if ch == "/" or ch == ":" or ch == "." or ch == "_" then
        pieces[#pieces + 1] = cur
        cur = ""
      end
    end
    if cur ~= "" then pieces[#pieces + 1] = cur end
    if #pieces >= 2 then
      for k, piece in ipairs(pieces) do
        out[#out + 1] = pandoc.Str(piece)
        if k < #pieces then
          out[#out + 1] = pandoc.RawInline("latex", "\\allowbreak{}")
        end
      end
      return true
    end
  end
  out[#out + 1] = pandoc.Str(run)
  return false
end

local function breakable_str(s)
  local txt = s.text
  if #txt <= TOKEN_BREAK_MIN then return nil end
  local out, ascii, other, changed = {}, {}, {}, false
  local function flush_ascii()
    if #ascii > 0 then
      if emit_ascii_run(table.concat(ascii), out) then changed = true end
      ascii = {}
    end
  end
  local function flush_other()
    if #other > 0 then
      out[#out + 1] = pandoc.Str(table.concat(other))
      other = {}
    end
  end
  for _, cp in utf8.codes(txt) do
    if cp >= 33 and cp <= 126 then
      flush_other()
      ascii[#ascii + 1] = utf8.char(cp)
    else
      flush_ascii()
      other[#other + 1] = utf8.char(cp)
    end
  end
  flush_ascii()
  flush_other()
  if not changed then return nil end
  n_breakpoints = n_breakpoints + 1
  return out
end

-- Cell 的内容字段在 pandoc 3.x 叫 contents（不是 blocks），
-- 逐格 walk 时用 Div 包一层再取回 content。
local function cell_blocks(cell)
  return cell.contents or cell.body
end

local function add_breakpoints(cell)
  local wrapped = pandoc.Div(cell_blocks(cell))
  local walked = pandoc.walk_block(wrapped, { Str = breakable_str }).content
  if cell.contents ~= nil then
    cell.contents = walked
  else
    cell.body = walked
  end
end

-- 注水法分配：权重 → 严格合计 1.0，且逐列落在 [lo[i], hi[i]]
local function allocate(weights, lo, hi)
  local n = #weights
  local out, fixed = {}, {}
  local lo_sum = 0.0
  for i = 1, n do lo_sum = lo_sum + lo[i] end
  if lo_sum >= 1.0 then            -- 下限总和已超 1：按下限等比压缩（极宽 token 的表）
    for i = 1, n do out[i] = lo[i] / lo_sum end
    return out, false
  end
  local remaining = 1.0
  local free_sum = 0.0
  for i = 1, n do free_sum = free_sum + weights[i] end
  for _ = 1, n + 2 do
    if free_sum <= 0 then break end
    local scale = remaining / free_sum
    local changed = false
    for i = 1, n do
      if not fixed[i] then
        local v = weights[i] * scale
        if v < lo[i] then
          out[i], fixed[i] = lo[i], true
          remaining, free_sum = remaining - lo[i], free_sum - weights[i]
          changed = true
        elseif v > hi[i] then
          out[i], fixed[i] = hi[i], true
          remaining, free_sum = remaining - hi[i], free_sum - weights[i]
          changed = true
        end
      end
    end
    if not changed then
      for i = 1, n do
        if not fixed[i] then out[i] = weights[i] * scale end
      end
      break
    end
  end
  -- 浮点残差归到最后一列，保证合计严格 1.0
  local total = 0.0
  for i = 1, n do total = total + (out[i] or 0) end
  local last = n
  while last > 1 and out[last] == nil do last = last - 1 end
  out[last] = (out[last] or 0) + (1.0 - total)
  return out, true
end

function Table(tbl)
  local n = #tbl.colspecs
  if n == 0 then return nil end
  n_tables = n_tables + 1
  width_hist[n] = (width_hist[n] or 0) + 1
  n_cols_total = n_cols_total + n

  local longest = {}
  local tokenw = {}
  for i = 1, n do longest[i], tokenw[i] = 0, 0 end

  local function scan_rows(rows)
    for _, row in ipairs(rows) do
      for i, cell in ipairs(row.cells) do
        if i <= n then
          local s = cell_text(cell)
          local w = display_width(s)
          if w > longest[i] then longest[i] = w end
          local t = longest_token(s)
          if t > tokenw[i] then tokenw[i] = t end
          if is_latex then add_breakpoints(cell) end
        end
      end
    end
  end
  scan_rows(tbl.head.rows)
  for _, body in ipairs(tbl.bodies) do scan_rows(body.body) end
  scan_rows(tbl.foot.rows)

  -- p{} 列宽是"行宽扣掉列间距"后按比例分
  local usable_pt = TEXTWIDTH_PT - 2.0 * TABCOLSEP_PT * (n - 1)
  local weights, lo, hi = {}, {}, {}
  local base_hi = cap_for(n)
  local lo_sum = 0.0
  for i = 1, n do
    weights[i] = math.sqrt(math.max(longest[i], 1))
    local need = tokenw[i] * PT_PER_UNIT / usable_pt
    if need > 0.5 then need = 0.5 end      -- 单个 token 最多要半行
    lo[i] = math.max(MIN_W, need)
    lo_sum = lo_sum + lo[i]
  end
  for i = 1, n do
    local others = lo_sum - lo[i]
    hi[i] = base_hi
    if 1.0 - others > hi[i] then hi[i] = 1.0 - others end
    if hi[i] < lo[i] then hi[i] = lo[i] end
  end

  local widths = allocate(weights, lo, hi)
  for i = 1, n do
    tbl.colspecs[i] = { tbl.colspecs[i][1], widths[i] }
  end

  local cells = {}
  for i = 1, n do
    cells[#cells + 1] = string.format("%d/tok%d:%.3f", longest[i], tokenw[i], widths[i])
  end
  detail[#detail + 1] = string.format("%d\tlo_sum=%.2f\t%s", n, lo_sum,
                                      table.concat(cells, " "))
  return tbl
end

function Pandoc(doc)
  local hist = {}
  for k, v in pairs(width_hist) do hist[#hist + 1] = k .. "列×" .. v end
  table.sort(hist)
  io.stderr:write(string.format("[table-widths] tables=%d cols=%d hist=%s\n",
                                n_tables, n_cols_total, table.concat(hist, ",")))
  io.stderr:write(string.format("[table-widths] latex=%s breakpoints=%d\n",
                                tostring(is_latex), n_breakpoints))
  local ok, fh = pcall(io.open, "table-widths.log", "w")
  if ok and fh then
    fh:write("# ncols\tlo_sum\tlen/tok:width per column\n")
    fh:write("#   len = 最长单元格显示宽度（CJK=2），tok = 最长不可断片段，width = 相对列宽\n")
    for _, line in ipairs(detail) do fh:write(line, "\n") end
    fh:close()
  end
  return doc
end
