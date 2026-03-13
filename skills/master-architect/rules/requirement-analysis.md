# Requirement Analysis Protocol

## Analysis Framework

### 1. Stakeholder Identification

```python
def identify_stakeholders(task_description: str) -> list:
    """
    Identify all stakeholders affected by the system.
    
    Returns list of stakeholder profiles with:
    - Role: Who they are
    - Needs: What they need from the system
    - Pain points: Current problems they face
    - Success criteria: How they measure success
    """
    pass
```

### 2. Requirement Categories

| Category | Description | Examples |
|----------|-------------|----------|
| Functional | What the system must do | User authentication, data processing |
| Non-functional | Quality attributes | Performance, security, usability |
| Constraints | Limitations and restrictions | Platform, budget, timeline |
| Assumptions | Accepted as true without proof | User has Python 3.10+ |

### 3. Requirement Elicitation Questions

**For Functional Requirements:**
- What are the main use cases?
- What inputs does the system receive?
- What outputs does the system produce?
- What data must be stored?
- What external systems must integrate?

**For Non-Functional Requirements:**
- How fast must the system respond?
- How many concurrent users?
- What security level is required?
- What platforms must be supported?

**For Constraints:**
- What is the budget?
- What is the timeline?
- What technologies are mandated?
- What skills does the team have?

## Requirement Documentation Template

```markdown
# Requirements Document

## 1. Project Overview
[One paragraph describing the project]

## 2. Stakeholders

| Stakeholder | Role | Needs | Pain Points |
|-------------|------|-------|-------------|
| End User | Consumer | Fast results | Slow current tools |

## 3. Functional Requirements

| ID | Requirement | Priority | Source |
|----|-------------|----------|--------|
| FR-001 | [Description] | High | [Stakeholder] |

## 4. Non-Functional Requirements

| ID | Requirement | Metric | Target |
|----|-------------|--------|--------|
| NFR-001 | Performance | Response time | < 100ms |

## 5. Constraints

| ID | Constraint | Rationale |
|----|------------|-----------|
| C-001 | [Constraint] | [Reason] |

## 6. Assumptions

| ID | Assumption | Risk if Wrong |
|----|------------|---------------|
| A-001 | [Assumption] | [Risk] |

## 7. Out of Scope

- [Feature explicitly excluded]
- [Feature for future release]
```

## Validation Checklist

- [ ] All stakeholders identified
- [ ] All functional requirements listed
- [ ] All non-functional requirements quantified
- [ ] All constraints documented
- [ ] All assumptions stated
- [ ] Requirements are testable
- [ ] Requirements are achievable
- [ ] Requirements are prioritized
- [ ] No conflicting requirements
- [ ] Out of scope items defined