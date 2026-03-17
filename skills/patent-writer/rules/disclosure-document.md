# Disclosure Document Writing

## Overview

The patent disclosure document (专利交底书) is written by the inventor for the patent attorney. It provides the technical foundation for drafting the patent application.

## Purpose

1. Help patent attorney understand the invention
2. Demonstrate advantages over prior art
3. Provide sufficient detail for claims drafting
4. Serve as the technical basis for the application

## Document Structure

### Standard Template

```markdown
# 专利交底书

## 一、发明名称
[简洁、准确地反映技术方案]

## 二、技术领域
[说明发明所属的技术领域]

## 三、背景技术
[说明现有技术状况及其缺点]

### 3.1 现有技术描述
[详细描述最接近的现有技术]

### 3.2 现有技术缺点
[分析现有技术存在的问题]

## 四、发明内容

### 4.1 发明目的
[说明发明要解决的技术问题]

### 4.2 技术方案
[详细描述发明的技术方案]

### 4.3 有益效果
[说明发明相对于现有技术的优点]

## 五、附图说明
[简要说明各附图的内容]

## 六、具体实施方式
[详细描述实现发明的具体方式]

## 七、权利要求概要
[列出主要的权利要求要点]

## 八、关键词
[提取3-5个关键词]
```

## Writing Guidelines

### 1. Title (发明名称)

```
Good examples:
- 一种基于深度学习的图像识别方法
- 一种用于数据加密的系统及方法
- 一种提高电池续航能力的装置

Bad examples:
- 新型技术
- 改进的方法
- 一种东西
```

### 2. Technical Field (技术领域)

```markdown
示例：
本发明涉及计算机技术领域，特别是涉及一种基于自然语言处理
的文本分类方法及系统。
```

### 3. Background Art (背景技术)

```markdown
结构：
1. 介绍技术背景
2. 描述现有技术方案
3. 分析现有技术缺点

示例：
目前，文本分类技术主要采用以下方法：
1. 基于规则的方法：...
   缺点：需要人工编写规则，适应性差
2. 传统机器学习方法：...
   缺点：需要大量特征工程，准确率有限
3. 现有深度学习方法：...
   缺点：模型体积大，推理速度慢

因此，需要一种既保持高准确率又具有快速推理能力的文本分类方法。
```

### 4. Summary of Invention (发明内容)

```markdown
结构：
1. 发明目的 - 要解决什么问题
2. 技术方案 - 如何解决问题（核心！）
3. 有益效果 - 有什么优点

技术方案写法：
本发明提供一种[发明名称]，包括：
步骤1：...
步骤2：...
步骤3：...

其特征在于：
[核心创新点描述]

进一步地，[可选的技术细节]

优选地，[优化方案]
```

### 5. Detailed Description (具体实施方式)

```markdown
要求：
1. 详细、完整地描述技术方案
2. 提供至少一个具体实施例
3. 配合附图进行说明
4. 描述足够清楚，使本领域技术人员能够实现

结构示例：
实施例1：
如图1所示，本实施例包括以下步骤：
S101：[步骤描述]
       具体地，...
S102：[步骤描述]
       具体地，...
...

实施例2：
本实施例与实施例1的区别在于：...
```

### 6. Claims Outline (权利要求概要)

```markdown
独立权利要求要点：
1. 一种[产品/方法]，其特征在于，包括：
   [必要技术特征]

从属权利要求要点：
1. 根据权利要求X所述的[产品/方法]，其特征在于：
   [附加技术特征]
```

## Writing Tips

### Dos ✅

1. **Draw more diagrams**
   - Flowcharts for methods
   - Block diagrams for systems
   - Structural diagrams for devices

2. **Provide examples**
   - Multiple embodiments
   - Comparative examples
   - Use cases

3. **Be specific**
   - Use concrete numbers
   - Define parameters
   - Specify alternatives

4. **Show advantages**
   - Quantitative improvements
   - Qualitative benefits
   - Comparison with prior art

### Don'ts ❌

1. **Too vague**
   - "等"、"之类"
   - No specific parameters
   - Unclear scope

2. **Missing details**
   - Skip steps
   - No examples
   - No drawings

3. **Wrong focus**
   - Market benefits only
   - No technical content
   - Business jargon

4. **Inconsistent**
   - Different terms for same thing
   - Contradictory statements
   - Missing references

## Quality Checklist

```
□ 标题是否准确反映技术方案？
□ 背景技术是否充分？
□ 现有技术缺点是否明确？
□ 发明目的是否清晰？
□ 技术方案是否完整？
□ 实施方式是否足够详细？
□ 附图是否齐全？
□ 权利要求概要是否合理？
□ 有益效果是否有说服力？
□ 是否提供了具体实施例？
□ 技术术语是否统一？
□ 文档格式是否规范？
```

## Example: Good Disclosure Document

```markdown
# 专利交底书

## 发明名称
一种基于注意力机制的文本分类方法及系统

## 技术领域
本发明涉及自然语言处理技术领域，特别是涉及一种基于
注意力机制的文本分类方法及系统。

## 背景技术
文本分类是自然语言处理的基础任务之一，广泛应用于...
现有技术主要包括：
1. 传统机器学习方法：需要大量特征工程...
2. CNN方法：难以捕捉长距离依赖...
3. RNN方法：训练速度慢...

因此，需要一种既能捕捉长距离依赖又具有较快训练速度的
文本分类方法。

## 发明内容

### 发明目的
本发明旨在提供一种基于注意力机制的文本分类方法，
解决现有技术中长距离依赖捕捉能力弱、训练速度慢的问题。

### 技术方案
本发明提供一种基于注意力机制的文本分类方法，包括：
S1：对输入文本进行分词处理，获取词序列；
S2：将词序列转换为词向量序列；
S3：通过多头注意力层提取文本特征；
S4：通过分类层输出分类结果。

其特征在于，步骤S3中采用改进的位置编码方式...

### 有益效果
1. 相比CNN方法，准确率提升5%；
2. 相比RNN方法，训练速度提升3倍；
3. 模型参数量减少40%。

## 具体实施方式
（详见附图及实施例描述...）
```