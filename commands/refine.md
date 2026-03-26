---
description: Refine - Polish and improve skills iteratively
agent: build
---

Load the skill-refiner skill and refine: $ARGUMENTS

**Usage**: `/refine <skill> [options]`

**Options**:
- `--depth quick` - Quick refinement
- `--depth standard` - Standard refinement (default)
- `--depth deep` - Deep refinement
- `--aspect <dimension>` - Refine specific dimension only
- `--all` - Refine all skills

**Examples**:
- `/refine humanizer` - Standard refinement of humanizer skill
- `/refine power-iterate --depth deep` - Deep refinement
- `/refine --all` - Refine all skills

**Dimensions**: Completeness, Readability, Practicality, Consistency, Extensibility

**Process**: Diagnosis → Plan → Refine → Validate → Report