---
name: daenerys-tool
description: "用于安装、更新并使用公司内部 Daenerys 代码生成工具（daenerys/dae），生成 Go 服务（HTTP/RPC），理解生成的项目结构，以及按文档完成构建/运行/配置流程。"
---

# Daenerys Tool

## 概览

用于指导 daenerys/dae 代码生成工具的安装与使用，并基于官方文档排查常见生成/编译问题。

## 使用流程

### 1) 前置检查

- 确认 Go 已安装（文档要求 1.17+）。
- 确认 `GOPATH` 已设置，并已加入 `PATH`。
- 确认 `inkedep` 已安装。
- 确认基础库为最新：`git.inke.cn/inkelogic/daenerys`、`git.inke.cn/BackendPlatform/golang`。
- 若出现 proto 报错，确认 `protoc` 版本 >= 3.6.1。

具体命令与版本说明请查阅 `references/daenerys-tool.md`。

### 2) 安装代码生成工具

按文档顺序：
- `inkedep get git.inke.cn/BackendPlatform/daenerys-tool`
- 进入 `daenerys-tool/daenerys` 执行 `go install`
- 可选：进入 `daenerys-tool/dae` 执行 `go install`（快捷方式）

确保 `daenerys` 或 `dae` 在 `PATH` 中可直接调用。

### 3) 生成项目

选择类型并生成：
- HTTP 服务：`daenerys new --type http <项目名>`
- 快捷方式：`dae new <项目名>`

默认在 `$GOPATH/src/git.inke.cn` 下创建项目目录。

RPC 服务需参考文档中的 RPC 生成流程，并确保 `protoc-gen-daenerys` 可用。

### 4) 构建与运行

在生成的 `app/` 目录下：
- `go build`
- `./app --config ./config/<env>/config.toml`

使用 `curl http://localhost:<port>/ping` 校验默认接口。

### 5) 常见问题排查

- **找不到 proto 文件**：安装/升级 `protoc`。
- **依赖缺失**：在项目根目录执行 `inkedep build`。
- **GOPATH 报错**：检查环境变量与 `PATH`。
- **内部包路径错误**：确保代码在 `GOPATH/src/git.inke.cn/...` 下。

## 自动编译与启动

当用户说“帮我编译这个项目/启动这个服务”，优先使用脚本：

```
scripts/build_and_run_http.sh <project_dir> [config_env]
```

参数说明：
- `project_dir`：项目根目录（包含 `app/` 目录）
- `config_env`：配置子目录名，默认 `ali-test`

示例：
```
scripts/build_and_run_http.sh /Users/zhangyukun/go/src/git.inke.cn/https-test ali-test
```

## 参考资料

- `references/daenerys-tool.md`：完整文档提取，包含命令、目录结构和配置示例。可用 `rg` 快速定位（如 `rg -n \"RPC\" references/daenerys-tool.md`）。
