# 代码与开发文档反AIGC检测规则

代码项目的README、文档字符串、提交信息等同样面临AIGC检测。

## 核心原则

代码文档反AIGC的关键是**具体到项目**。AI倾向生成"万能README"，读起来正确但放在任何项目上都适用。人类工程师写的README会写具体的命令、具体的数据、具体的约束。

## 代码文档AIGC高发模式

### 1. README万能模板（权重30%）

```
❌ AI模式：
"XX是一个强大的工具，提供丰富的功能"
"易于使用，简单配置即可上手"
"具有良好的扩展性"

✅ 专业写法：
"XX做一件事：把CSV文件聚合为按时间分组的统计表。不支持Excel，不支持JSON，不支持流式输入。如果需要这些功能，用pandas。"
```

### 2. 注释空洞（权重25%）

```
❌ AI模式：
# Initialize the data processor
def __init__(self):
    # Set up configuration
    self.config = load_config()
    # Prepare the pipeline
    self.pipeline = Pipeline()

✅ 专业写法：
# Single-process init; for multiprocessing use .from_config() instead
def __init__(self):
    self.config = load_config()  # config.yaml or ENV override
    self.pipeline = Pipeline()   # lazy-load: actual model weights at first .process() call
```

### 3. 提交信息机械（权重20%）

```
❌ AI模式：
"feat: add new feature"
"fix: fix bug"
"refactor: improve code quality"
"docs: update documentation"

✅ 专业写法：
"fix: handle empty CSV in aggregate() — skip header-only files, return empty ToolResult"
"feat: add --timeout flag to cli, default 30s, aligns with global-rules bash-safety"
```

### 4. API文档没有例子（权重15%）

```
❌ AI模式：
"process_data(input_path: str) -> ToolResult: Process the input data."

✅ 专业写法：
"process_data(input_path: str) -> ToolResult:
Process CSV at input_path and return aggregated statistics.
Empty files return ToolResult(success=True, data={}) with no error.
Files >100MB raise MemoryError — use chunk_size parameter for large files.

>>> from mytool import process_data
>>> r = process_data("sales_2024.csv")
>>> r.success
True
>>> r.data["total"]
154280
```

### 5. 代码本身"正确但平庸"（权重10%）

```
❌ AI代码特征：
- 变量名过-generic：data, result, item, value, info
- 错误处理全是pass或generic Exception
- 函数名描述不了行为：process(), handle(), calculate()
- 注释只重复代码：count += 1  # increment count

✅ 专业代码特征：
- 变量名具体：aggregate_result, pending_rows, deduplicated_keys
- 错误处理具体：raise ValueError(f"CSV has no numeric columns: {path}")
- 函数名描述行为：aggregate_by_time(), deduplicate_on_key(), validate_schema()
- 注释解释为什么而非是什么：count += 1  # skip header row on re-read after seek(0)
```

## 反AIGC五原则

### 1. README写具体限制

好的README不只写能做什么，更要写不能做什么。

### 2. 注释写"为什么"

注释解释设计决策和约束，不重复代码。

### 3. 提交信息写做了什么

不用generic的feat/fix，写具体改了什么。

### 4. API文档必带例子

没有可运行例子的API文档等于没有文档。

### 5. 代码命名具体

变量名、函数名具体到这个项目，而非通用名。

## AIGC率检测清单

- [ ] README是否有"强大/丰富/易于/良好"等空洞词？→有=AI
- [ ] 注释是否只重复代码？→是=AI
- [ ] 提交信息是否generic？→是=AI
- [ ] API文档是否有可运行示例？→无=AI
- [ ] 变量名是否过-generic？→是=AI
- [ ] 错误处理是否catch all Exception然后pass？→是=AI
- [ ] 每个限制和约束是否明确写出？→未写出=AI

### AIGC率评分标准

- 0-15%：专业工程师级别，所有文档具体可执行
- 16-30%：合格，有少量可优化项
- 31-50%：需要修改，像模板填空
- 51-70%：需要重写，空洞无实质
- 71-100%：纯AI生成的通用模板