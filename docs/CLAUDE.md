# CLAUDE.md - Documentation Directory

This file provides specific guidance for Claude Code when working with markdown files in the `/docs` directory.

## Markdown Documentation Standards

When creating or editing markdown files in this directory, follow these standards:

### Required Header Format

Every markdown file MUST start with the following header format:

```markdown
# Document Title

**Created:** 2024-07-01T15:30:45Z  
**Category:** [overview|technical|analysis|planning|misc]

[Document content follows...]
```

### Documentation Rules

1. **Date Format**: Use RFC3339 format (YYYY-MM-DDTHH:MM:SSZ)
2. **Category Selection**: Choose exactly one from:
   - `overview` - High-level project overviews and introductions
   - `technical` - Technical specifications, API docs, code analysis
   - `analysis` - Research findings, data analysis, performance studies
   - `planning` - Project plans, roadmaps, task breakdowns
   - `misc` - Everything else that doesn't fit other categories

3. **Header Placement**: Date and category info must appear immediately after the main title
4. **Formatting**: Use bold text for labels, maintain consistent spacing

### Important Notes
- ALWAYS apply these rules when creating new markdown files in `/docs`
- When editing existing markdown files, add the header if missing
- Use current timestamp when creating the **Created** field
- These rules are synchronized with Cursor IDE rules in `.cursor/rules/markdown-rule.mdc`

### Document Portal Integration

Files created with proper headers will be automatically categorized and displayed in the documentation portal (`docs/index.html`). The categorization system helps organize documents into logical groups for better navigation.

### Quality Standards

- Use clear, descriptive titles
- Include comprehensive sections with proper heading hierarchy
- Add code examples where applicable
- Include diagrams (Mermaid) for complex relationships
- Maintain consistent formatting throughout
- Use Korean comments for Korean-language content
- Use English for technical terms and international standards