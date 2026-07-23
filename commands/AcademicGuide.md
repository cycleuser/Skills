# /AcademicGuide

Load the academic-guide skill and execute the full 4-phase field navigation workflow.

## Usage

```
/AcademicGuide <field name>
```

## 4 Phases

1. **Dissertations**: Search recent PhD theses (Google Scholar, NDLTD, OATD, ProQuest, CNKI). Label as 🆓/🏫/🔒. Chase preprints for 🏫 items.

2. **Professional Sites**: Find authoritative forums, databases, platforms. Exclude generic encyclopedias. Record URL, description, update frequency.

3. **Search Records**: Log every search with ISO 8601 timestamp, engine name, keywords, result count. Save to /tmp/academic-guide/{timestamp}/.

4. **Citation Verification**: Open every URL in the final report independently. Mark ✅/⚠️/❌. Try Wayback Machine for dead links. Remove unverifiable ones.

## Output

Written to /tmp/academic-guide/{YYYYMMDD-HHmmss}/final-report.md

## Rule Files

Read these before executing:
- ~/.config/opencode/skills/academic-guide/rules/dissertation-search.md
- ~/.config/opencode/skills/academic-guide/rules/professional-sites.md
- ~/.config/opencode/skills/academic-guide/rules/search-records.md
- ~/.config/opencode/skills/academic-guide/rules/citation-verification.md
- ~/.config/opencode/skills/academic-guide/rules/output-format.md
- ~/.config/opencode/skills/academic-guide/rules/anti-aigc.md
