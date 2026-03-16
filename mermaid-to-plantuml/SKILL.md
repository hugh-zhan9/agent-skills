---
name: mermaid-to-plantuml
description: Convert Mermaid diagrams to compatible PlantUML with minimal syntax.
metadata:
  short-description: Mermaid to PlantUML conversion rules and examples
---

# Mermaid to PlantUML Conversion Skill

## 目标
将 Mermaid 图表转换为兼容性更好的 PlantUML 格式，确保在各种渲染器中都能正常显示。

## 核心原则

### 1. 使用最简洁的语法
- ❌ 避免复杂的样式配置
- ❌ 避免 `skinparam` 中的嵌套配置
- ✅ 优先使用 PlantUML 的默认样式
- ✅ 如果需要样式，使用最基础的 skinparam

### 2. 避免的语法陷阱

#### 活动图 (Activity Diagram)
❌ **避免在 partition 内使用控制流结束**
```plantuml
partition "阶段" {
  if (条件?) then (是)
    :处理;
    stop  ← 会导致语法错误
  endif
}
```

✅ **将控制流移到 partition 外部**
```plantuml
partition "阶段" {
  :处理;
}

if (条件?) then (是)
  :继续;
  stop  ← 正确
endif
```

❌ **避免使用 skinparam activity 样式配置**
```plantuml
skinparam activity {
  BackgroundColor #E3F2FD
  BorderColor #1976D2
}
```

✅ **使用最简洁的语法**
```plantuml
@startuml
start
:步骤1;
:步骤2;
stop
@enduml
```

#### 矩形图 (Rectangle Diagram)
❌ **避免使用 rectangle 关键字**
```plantuml
rectangle "服务名\n说明" as A  ← 换行符可能导致错误
```

✅ **使用组件图语法**
```plantuml
[服务名\n说明] as A  ← 兼容性好，支持换行
```

#### 时序图 (Sequence Diagram)
❌ **避免使用 Mermaid 的 rect 背景色**
```mermaid
rect rgb(255, 244, 230)
  A->>B: 消息
end
```

✅ **使用 PlantUML 的 group**
```plantuml
group 描述
  A -> B: 消息
end
```

## 常见图表类型转换规则

### 1. 流程图 (Flowchart / Activity Diagram)

#### Mermaid 语法
```mermaid
graph TB
    A[开始] --> B{判断}
    B -->|是| C[处理]
    B -->|否| D[结束]
    
    style A fill:#e1f5dd
    style D fill:#ffe6e6
```

#### PlantUML 语法
```plantuml
@startuml
start
:开始;
if (判断?) then (是)
  :处理;
else (否)
  :结束;
endif
stop
@enduml
```

### 2. 时序图 (Sequence Diagram)

#### Mermaid 语法
```mermaid
sequenceDiagram
    participant A as 服务A
    participant B as 服务B
    
    A->>B: 请求
    B-->>A: 响应
    
    rect rgb(255, 244, 230)
        Note over A,B: 事务处理
        A->>B: 提交
        B-->>A: 确认
    end
```

#### PlantUML 语法
```plantuml
@startuml
participant "服务A" as A
participant "服务B" as B

A -> B: 请求
B --> A: 响应

group 事务处理
  note over A,B: 事务处理
  A -> B: 提交
  B --> A: 确认
end

@enduml
```

**关键差异：**
- `->` 实线箭头（Mermaid 中是 `->>`)
- `-->` 虚线箭头（Mermaid 中是 `-->>`)
- 使用 `group` 代替 `rect`

### 3. 组件图 / 架构图

#### Mermaid 语法
```mermaid
graph LR
    A[服务A] --> B[服务B]
    B --> C[服务C]
    
    style A fill:#e6f3ff
    style B fill:#e1f5dd
    style C fill:#fff4e6
```

#### PlantUML 语法（方式1：组件图）
```plantuml
@startuml
[服务A] as A
[服务B] as B
[服务C] as C

A --> B
B --> C
@enduml
```

#### PlantUML 语法（方式2：简单矩形）
```plantuml
@startuml
component "服务A" as A
component "服务B" as B
component "服务C" as C

A --> B
B --> C
@enduml
```

### 4. 状态图 (State Diagram)

#### Mermaid 语法
```mermaid
stateDiagram-v2
    [*] --> 待处理
    待处理 --> 处理中
    处理中 --> 已完成
    已完成 --> [*]
```
