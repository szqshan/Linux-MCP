# Linux MCP Toolkit

Linux MCP Toolkit 是一个基于 MCP 协议的增强型 Linux 管理工具包，提供交互式 SSH 会话、系统监控、文件操作等功能。

## 🚀 功能特性

- **交互式 SSH 会话**：持久化的 SSH 连接，支持实时命令执行
- **系统监控**：快速获取系统信息、进程监控、网络状态
- **文件操作**：远程文件读写、目录列表、权限管理
- **服务管理**：systemd 服务控制（启动、停止、重启、状态检查）
- **跨平台支持**：Windows、Linux、macOS 全平台兼容
- **MCP 协议**：基于 Model Context Protocol 的标准接口

## 📦 安装

### 通过 PyPI 安装

```bash
pip install linux-mcp-toolkit
```

### 从源码安装

```bash
git clone https://github.com/linux-mcp/linux-mcp-toolkit.git
cd linux-mcp-toolkit
pip install -e .
```

## 🔧 快速开始

### 基本使用

```python
from linux_mcp_toolkit import ping_host, execute_command, create_interactive_session

# 检查主机连通性
result = ping_host("192.168.1.100")
print(result)

# 执行单个命令
output = execute_command("192.168.1.100", "ls -la /home")
print(output)

# 创建交互式会话
session = create_interactive_session("192.168.1.100", "username", "password")
print(session)
```

### MCP 服务器使用

```bash
# 启动 MCP 服务器
python -m linux_mcp_toolkit
```

## 🛠️ 工具函数

### 网络工具
- `ping_host(host, count=4)`: 检查主机连通性
- `network_info(ip_address)`: 获取网络配置信息

### 系统管理
- `quick_system_info(ip_address)`: 快速系统信息
- `monitor_process(ip_address, process_name)`: 进程监控
- `service_control(ip_address, service, action)`: 服务管理

### 文件操作
- `file_operations(ip_address, operation, path, content=None)`: 文件读写操作

### 交互式会话
- `create_interactive_session(ip_address, username, password, port)`: 创建会话
- `execute_interactive_command(ip_address, command, timeout=30)`: 执行命令
- `send_interactive_input(ip_address, input_text)`: 发送输入
- `get_real_time_output(ip_address, duration=5)`: 获取实时输出
- `list_active_sessions()`: 列出活跃会话
- `close_session(ip_address)`: 关闭会话

## 🔐 认证方式

支持两种认证方式：

1. **密码认证**：使用用户名和密码
2. **密钥认证**：使用 SSH 私钥

## 📋 依赖要求

- Python >= 3.8
- paramiko >= 2.7.0 (SSH 客户端)
- mcp >= 1.0.0 (MCP 协议支持)

## 🐛 问题反馈

如果遇到问题，请通过以下方式反馈：

- GitHub Issues: https://github.com/linux-mcp/linux-mcp-toolkit/issues
- 邮件联系: contact@linuxmcp.com

## 📄 许可证

MIT License - 详见 LICENSE 文件

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 🎯 版本历史

- v1.0.0: 初始版本，包含基本功能
  - 交互式 SSH 会话
  - 系统监控工具
  - 文件操作功能
  - 服务管理工具