# 🚀 Linux MCP Toolkit - 革命性的Linux服务器管理工具

## 🎯 项目简介

### 💡 开发背景
在AI时代，开发者需要一个能够**用自然语言管理Linux服务器**的工具。传统的SSH命令行方式对非专业人士太复杂，现有工具又缺乏AI集成能力。

**Linux MCP Toolkit** 应运而生！这是一个专为 **Claude Desktop、Cursor、Windsurf** 等AI客户端设计的MCP服务器，让你能够：
- 🗣️ **用中文对话管理服务器**："帮我看看nginx状态"
- 🤖 **AI智能运维**：自动分析系统问题并给出解决方案
- ⚡ **一键部署**：3分钟完成从安装到使用的全流程

### 🔧 核心功能
| 功能模块 | 能力描述 | 使用场景 |
|---------|----------|----------|
| **🌐 连接管理** | SSH连接、会话保持、自动重连 | 远程服务器管理 |
| **⚡ 命令执行** | 单次命令、交互式会话、长时间任务 | 系统运维、部署 |
| **📁 文件操作** | 上传、下载、编辑、权限管理 | 代码部署、配置管理 |
| **🔧 服务控制** | systemd服务管理、Docker容器操作 | 应用生命周期管理 |
| **📊 系统监控** | 实时资源监控、日志分析 | 性能优化、故障排查 |

## 🚀 部署指南

### 📋 环境要求
- **Python**: 3.8+ (推荐3.10+)
- **操作系统**: Windows/macOS/Linux (开发机)
- **目标服务器**: 任何支持SSH的Linux系统
- **AI客户端**: Claude Desktop、Cursor、Windsurf等支持MCP的客户端

### 📦 安装方式（3选1）

#### 方式1：一键安装（推荐）
```bash
pip install linux-mcp-toolkit
```

#### 方式2：UV安装（更快）
```bash
uv pip install linux-mcp-toolkit
```

#### 方式3：开发版安装
```bash
git clone https://github.com/linux-mcp/linux-mcp-toolkit
cd linux-mcp-toolkit
pip install -e .
```

### ⚙️ 配置文件设置

#### 1. 找到配置文件
| 操作系统 | 配置文件路径 |
|---------|-------------|
| **Windows** | `%APPDATA%/Claude/claude_desktop_config.json` |
| **macOS** | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| **Linux** | `~/.config/Claude/claude_desktop_config.json` |

#### 2. 基础配置（必做）
```json
{
  "mcpServers": {
    "linux-mcp-toolkit": {
      "command": "uvx",
      "args": ["linux-mcp-toolkit"]
    }
  }
}
```

#### 3. 安全配置方式（推荐）

**方式A：SSH密钥认证（最安全）**
```json
{
  "mcpServers": {
    "linux-mcp-toolkit": {
      "command": "uvx",
      "args": ["linux-mcp-toolkit"],
      "env": {
        "HOST": "192.168.1.100",
        "PORT": "22",
        "USERNAME": "root",
        "KEY_FILE": "D:\\MCP\\linux.pem",
        "PASSPHRASE": "",
        "TIMEOUT": "30",
        "RETRY": "3"
      }
    }
  }
}
```

**方式B：系统环境变量（次推荐）**
```json
{
  "mcpServers": {
    "linux-mcp-toolkit": {
      "command": "uvx",
      "args": ["linux-mcp-toolkit"],
      "env": {
        "HOST": "192.168.1.100",
        "PORT": "22",
        "USERNAME": "root",
        "PASSWORD": "$SSH_PASSWORD",
        "KEY_FILE": "$SSH_KEY_PATH",
        "TIMEOUT": "30",
        "RETRY": "3"
      }
    }
  }
}
```

**方式C：密码认证（仅测试用）**
```json
{
  "mcpServers": {
    "linux-mcp-toolkit": {
      "command": "uvx",
      "args": ["linux-mcp-toolkit"],
      "env": {
        "HOST": "192.168.1.100",
        "PORT": "22",
        "USERNAME": "root",
        "PASSWORD": "your_password",
        "TIMEOUT": "30",
        "RETRY": "3"
      }
    }
  }
}
```

#### 🔐 环境变量设置

**Linux/macOS:**
```bash
# 设置密码
export SSH_PASSWORD="your_secure_password"

# 设置密钥路径
export SSH_KEY_PATH="/home/user/.ssh/id_rsa"

# 验证设置
echo $SSH_PASSWORD
echo $SSH_KEY_PATH
```

**Windows:**
```cmd
# 设置密码
set SSH_PASSWORD=your_secure_password

# 设置密钥路径
set SSH_KEY_PATH=C:\Users\youruser\.ssh\id_rsa

# 验证设置
echo %SSH_PASSWORD%
echo %SSH_KEY_PATH%
```

#### 🛡️ 安全最佳实践
1. **优先使用SSH密钥**而非密码认证
2. **设置正确的密钥权限**：`chmod 600 ~/.ssh/id_rsa`
3. **避免在配置文件中存储明文密码**
4. **使用系统环境变量**管理敏感信息
5. **定期轮换密钥**提高安全性
6. **为AI客户端创建专用用户**，避免使用root
7. **使用密钥密码**保护私钥文件

### 🔧 验证安装

#### 步骤1：测试包安装
```bash
python -c "import linux_mcp_toolkit; print('✅ 安装成功')"
```

#### 步骤2：测试命令行
```bash
# 测试连接
linux-mcp-toolkit --host 192.168.1.100 --ping

# 执行简单命令
linux-mcp-toolkit --host 192.168.1.100 --command "uname -a"
```

#### 步骤3：重启AI客户端
重启你的Claude Desktop/Cursor/Windsurf，开始使用！

## 📸 使用示例

### 🎯 场景1：系统信息查询
**用户对话**："帮我看看服务器的系统信息"

**AI响应**：
```
我来帮您查看服务器系统信息：

📊 **系统概览**
- 主机名: web-server-01
- 操作系统: Ubuntu 22.04.3 LTS
- 内核版本: 5.15.0-88-generic
- 架构: x86_64

💾 **资源使用**
- CPU: 2核心，当前使用率 15%
- 内存: 4GB，已使用 2.1GB (52%)
- 磁盘: 40GB，已使用 12GB (30%)
- 负载: 0.25, 0.18, 0.12

🌐 **网络状态**
- 公网IP: 203.0.113.45
- 内网IP: 192.168.1.100
- 网络延迟: 12ms
```

### 🚀 场景2：服务管理
**用户对话**："nginx服务好像有问题，帮我检查一下"

**AI响应**：
```
🔍 **Nginx状态检查**

📊 **服务状态**: active (running) ✅
📅 **运行时间**: 2天 14小时 36分钟
👥 **进程数**: 3个nginx进程
🌐 **监听端口**: 80, 443

📋 **配置文件检查**
✅ /etc/nginx/nginx.conf - 语法正确
✅ /etc/nginx/sites-enabled/ - 配置已启用

🚨 **发现的问题**: 
- 日志显示有404错误 (建议检查网站根目录)
- SSL证书将在15天后过期

💡 **建议操作**: 
1. 检查网站文件权限
2. 更新SSL证书
3. 重启nginx服务
```

### 📁 场景3：文件操作
**用户对话**："帮我在/var/www/html目录下创建一个测试文件"

**AI响应**：
```
📁 **文件操作完成**

✅ **创建文件**: /var/www/html/test.html
📋 **文件内容**:
```html
<!DOCTYPE html>
<html>
<head>
    <title>测试页面</title>
</head>
<body>
    <h1>Linux MCP Toolkit 测试成功！</h1>
    <p>当前时间: 2024-12-27 15:30:45</p>
</body>
</html>
```

🔗 **访问地址**: http://your-server-ip/test.html
📊 **文件权限**: 644 (rw-r--r--)
👤 **所有者**: www-data:www-data
```

### 🐳 场景4：Docker容器管理
**用户对话**："查看所有运行的容器"

**AI响应**：
```
🐳 **Docker容器状态**

📊 **运行中的容器 (3个)**:

1. **nginx-web** (nginx:latest)
   - 状态: ✅ Up 2 days
   - 端口: 0.0.0.0:80->80/tcp
   - 内存: 128MB / 512MB

2. **mysql-db** (mysql:8.0)
   - 状态: ✅ Up 2 days (healthy)
   - 端口: 3306/tcp
   - 内存: 456MB / 1GB

3. **redis-cache** (redis:7-alpine)
   - 状态: ✅ Up 2 days
   - 端口: 6379/tcp
   - 内存: 12MB / 256MB

📈 **资源总计**:
- 容器总数: 5 (运行中: 3, 已停止: 2)
- 总内存使用: 596MB / 1.77GB
- 总CPU使用: 8.5%
```

### ⚡ 场景5：实时日志监控
**用户对话**："实时监控nginx访问日志"

**AI响应**：
```
📊 **开始监控nginx访问日志**

```bash
# 实时日志输出 (按Ctrl+C停止)
tail -f /var/log/nginx/access.log

[15:35:12] 203.0.113.45 - - [27/Dec/2024:15:35:12 +0000] "GET / HTTP/1.1" 200 1234 "-" "Mozilla/5.0"
[15:35:13] 203.0.113.46 - - [27/Dec/2024:15:35:13 +0000] "GET /api/users HTTP/1.1" 200 567 "-" "curl/7.68.0"
[15:35:14] 203.0.113.47 - - [27/Dec/2024:15:35:14 +0000] "POST /login HTTP/1.1" 302 456 "https://example.com/login" "Mozilla/5.0"

# 统计信息
- 当前QPS: 15.3 requests/sec
- 2xx响应: 85%
- 4xx响应: 12%
- 5xx响应: 3%
```

## 🛠️ 故障排除

### 常见问题速查表

| 问题描述 | 解决方案 | 验证命令 |
|---------|----------|----------|
| **连接失败** | 检查SSH服务、防火墙、用户名密码 | `ssh user@host` |
| **权限错误** | 确认用户权限、使用sudo | `sudo -l` |
| **包导入失败** | 重新安装、检查Python路径 | `pip show linux-mcp-toolkit` |
| **AI客户端无响应** | 重启客户端、检查配置文件 | 查看客户端日志 |

### 🔍 调试模式
```bash
# 启用详细日志
linux-mcp-toolkit --debug --host 192.168.1.100 --command "uptime"

# 测试配置文件
linux-mcp-toolkit --config-test
```

## 🎉 3分钟快速上手

1. **📦 安装** (30秒)
   ```bash
   pip install linux-mcp-toolkit
   ```

2. **⚙️ 配置** (60秒)
   - 复制配置JSON到客户端配置文件
   - 填入服务器信息

3. **🔄 重启** (30秒)
   - 重启你的AI客户端

4. **🚀 使用** (60秒)
   - 开始用自然语言管理服务器！

**示例对话**：
- "帮我看看服务器状态"
- "重启nginx服务"
- "查看今天的日志"

---

## 📞 支持与反馈

- **GitHub**: [linux-mcp/linux-mcp-toolkit](https://github.com/linux-mcp/linux-mcp-toolkit)
- **问题反馈**: [提交Issue](https://github.com/linux-mcp/linux-mcp-toolkit/issues)
- **文档**: [完整文档](https://github.com/linux-mcp/linux-mcp-toolkit/wiki)

**⭐ 如果这个项目帮到了你，请给个Star！**