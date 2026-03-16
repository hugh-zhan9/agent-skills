# Skills 目录

本目录包含项目特定的 AI 助手技能定义。

## 可用 Skills

### 1. mermaid-to-plantuml
**用途**: 将 Mermaid 图表转换为兼容性更好的 PlantUML 格式

**何时使用**:
- 文档中有 Mermaid 图表需要转为 PlantUML
- PlantUML 代码出现渲染错误需要修复
- 需要确保图表在各种平台上都能正确显示

**使用方法**:
```
请使用 mermaid-to-plantuml skill 将这个 Mermaid 图表转换为 PlantUML
```

**关键能力**:
- Mermaid → PlantUML 语法转换
- 修复常见的 PlantUML 语法错误
- 移除不兼容的样式配置
- 确保最大兼容性

## 如何创建新的 Skill

1. 在 `.skills/` 目录下创建新的 `.md` 文件
2. 使用清晰的结构描述技能的目标、规则和示例
3. 包含足够的示例代码和最佳实践
4. 在此 README 中添加说明

## Skill 文件结构建议

```markdown
# Skill 名称

## 目标
简要说明这个 skill 的用途

## 核心原则
列出关键规则和最佳实践

## 示例
提供具体的转换示例

## 使用场景
说明何时应该使用这个 skill

## 输出要求
明确输出的标准和质量要求
```
