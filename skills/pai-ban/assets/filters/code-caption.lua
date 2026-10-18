-- =====================================================================
-- pai-ban / assets/filters/code-caption.lua
--
--   源文（mkdocs 风格，build.py 已把围栏属性归一化成 pandoc 原生语法）：
--       ```python title="02.01_ollama_api" linenums="1"
--   变成：
--       \paibancodecaption{02.01\_ollama\_api}   ← 代码块上方 8.5pt muted 标签
--       \begin{lstlisting}[language=Python, numbers=left]
--
--   为什么必须在这里剥掉这两个属性（实测教训）：
--   pandoc 的 LaTeX writer 会把 CodeBlock 的**全部** attribute 原样塞进
--   lstlisting 的可选项 —— `title={...}, linenums=1` 会直接触发
--   "Package keyval Error: linenums undefined." 编译失败。
--   所以 title 要变成独立标签，linenums 要翻译成 listings 认识的
--   `numberLines` 类别（pandoc 见该类会输出 numbers=left）。
--
--   规格：rules/design-spec.md §7（代码标题 8.5pt muted 单行标签、行号仅
--   源文有 linenums 时出现、行号 muted 7pt）。
-- =====================================================================

local is_latex = FORMAT:match("latex") ~= nil

-- LaTeX 特殊字符转义（只用于标签这种纯文本）
local ESCAPE = {
  ["\\"] = "\\textbackslash{}", ["{"] = "\\{", ["}"] = "\\}",
  ["$"] = "\\$", ["&"] = "\\&", ["#"] = "\\#", ["^"] = "\\^{}",
  ["_"] = "\\_", ["%"] = "\\%", ["~"] = "\\~{}",
}

local function tex_escape(s)
  return (s:gsub("[\\{}$&#^_%%~]", ESCAPE))
end

function CodeBlock(cb)
  if not is_latex then return nil end

  local out = {}
  local title = cb.attributes["title"]
  if title and title ~= "" then
    out[#out + 1] = pandoc.RawBlock("latex",
      "\\paibancodecaption{" .. tex_escape(title) .. "}")
    cb.attributes["title"] = nil
  end

  local linenums = cb.attributes["linenums"]
  if linenums ~= nil then
    cb.attributes["linenums"] = nil
    cb.classes:insert("numberLines")
    local n = tonumber(linenums)
    if n and n > 1 then
      cb.attributes["startFrom"] = tostring(n)
    end
  end

  out[#out + 1] = cb
  return out
end
