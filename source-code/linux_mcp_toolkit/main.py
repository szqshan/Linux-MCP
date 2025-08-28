# -*- coding: utf-8 -*-
# Enhanced Linux MCP Toolkit with Interactive Shell Support
import subprocess
import paramiko
import json
import logging
import sys
import time
import threading
import select
import socket
import os
import io
import asyncio
from typing import Dict, Optional, Tuple
from mcp.server.fastmcp import FastMCP

if sys.platform == "win32":
    os.environ['PYTHONIOENCODING'] = 'utf-8'

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger('LinuxMCP')

mcp = FastMCP("Linux Toolkit - Interactive", dependencies=["paramiko"])

# Default SSH connection parameters (优先从环境变量读取，其次从MCP配置)
DEFAULT_SSH_PORT = int(os.environ.get('PORT', 22))
DEFAULT_SSH_USERNAME = os.environ.get('USERNAME', 'root')
DEFAULT_SSH_PASSWORD = os.environ.get('PASSWORD', '请用户输入密码')

# MCP配置存储
def get_mcp_config():
    """从MCP配置文件中读取配置"""
    import json
    import os
    
    # 查找MCP配置文件
    config_paths = [
        os.path.expanduser("~/.mcp/config.json"),
        os.path.expanduser("~/.config/mcp/config.json"),
        os.path.join(os.getcwd(), "mcp_config.json"),
        os.path.join(os.getcwd(), "claude_desktop_config.json")
    ]
    
    for config_path in config_paths:
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # 查找linux-mcp-toolkit的配置
                    if 'mcpServers' in config:
                        servers = config['mcpServers']
                        for server_name, server_config in servers.items():
                            if 'linux-mcp-toolkit' in server_name.lower():
                                # 从args中提取环境变量
                                args = server_config.get('args', [])
                                env_vars = {}
                                
                                # 解析环境变量
                                for arg in args:
                                    if isinstance(arg, str) and '=' in arg:
                                        key, value = arg.split('=', 1)
                                        env_vars[key] = value
                                
                                return {
                                    'host': env_vars.get('HOST'),
                                    'username': env_vars.get('USERNAME'),
                                    'password': env_vars.get('PASSWORD'),
                                    'port': int(env_vars.get('PORT', 22))
                                }
                    
                    # 直接查找linux-mcp-toolkit的env配置
                    for server_name, server_config in servers.items():
                        if 'linux-mcp-toolkit' in server_name.lower():
                            env = server_config.get('env', {})
                            return {
                                'host': env.get('HOST'),
                                'username': env.get('USERNAME'),
                                'password': env.get('PASSWORD'),
                                'port': int(env.get('PORT', 22))
                            }
                            
            except Exception as e:
                logger.warning(f"读取配置文件 {config_path} 失败: {e}")
                continue
    
    return {}

# 初始化MCP配置
MCP_CONFIG = get_mcp_config()



# Global session storage
active_sessions: Dict[str, Dict] = {}

class InteractiveShell:
    """Interactive SSH shell session manager"""
    
    def __init__(self, ip_address: str, username: str = None, password: str = None, port: int = None):
        self.ip_address = ip_address
        self.username = username or DEFAULT_SSH_USERNAME
        self.password = password or DEFAULT_SSH_PASSWORD
        self.port = port or DEFAULT_SSH_PORT
        self.ssh = None
        self.shell = None
        self.output_buffer = []
        self.is_connected = False
        self.last_activity = time.time()
        
    def connect(self):
        """Establish SSH connection and create shell"""
        try:
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh.connect(
                hostname=self.ip_address,
                port=self.port,
                username=self.username,
                password=self.password,
                timeout=10
            )
            logger.info(f"Successfully connected to {self.ip_address}")
            # Create interactive shell
            self.shell = self.ssh.invoke_shell()
            self.shell.settimeout(0.1)  # Non-blocking
            self.is_connected = True
            # Wait for initial prompt
            time.sleep(1)
            self._read_output()
            return True
        except Exception as e:
            logger.error(f"SSH connection failed: {str(e)}")
            return False
    
    def _read_output(self) -> str:
        """Read available output from shell"""
        output = ""
        try:
            while True:
                if self.shell.recv_ready():
                    data = self.shell.recv(4096).decode('utf-8', errors='ignore')
                    output += data
                    self.output_buffer.append(data)
                else:
                    break
        except socket.timeout:
            pass
        except Exception as e:
            logger.error(f"Error reading output: {str(e)}")
        
        return output
    
    def execute_command(self, command: str, timeout: int = 30) -> Tuple[str, bool]:
        """Execute command and return output"""
        if not self.is_connected:
            return "Session not connected", False
            
        try:
            # Clear buffer
            self.output_buffer = []
            
            # Send command
            self.shell.send(command + '\n')
            
            # Read output with timeout
            start_time = time.time()
            output = ""
            
            while (time.time() - start_time) < timeout:
                new_output = self._read_output()
                if new_output:
                    output += new_output
                    self.last_activity = time.time()
                
                # Check if command finished (simple heuristic)
                if output.endswith('$ ') or output.endswith('# ') or output.endswith('> '):
                    break
                    
                time.sleep(0.1)
            
            return output, True
            
        except Exception as e:
            return f"Command execution failed: {str(e)}", False
    
    def send_input(self, input_text: str):
        """Send input to shell (for interactive commands)"""
        if self.is_connected and self.shell:
            self.shell.send(input_text + '\n')
            self.last_activity = time.time()
    
    def get_real_time_output(self, duration: int = 5) -> str:
        """Get real-time output for specified duration"""
        if not self.is_connected:
            return "Session not connected"
        
        output = ""
        start_time = time.time()
        
        while (time.time() - start_time) < duration:
            new_output = self._read_output()
            if new_output:
                output += new_output
            time.sleep(0.1)
        
        return output
    
    def disconnect(self):
        """Close SSH connection"""
        if self.shell:
            self.shell.close()
        if self.ssh:
            self.ssh.close()
        self.is_connected = False

def get_session(ip_address: str = None, create_if_not_exists: bool = True) -> Optional[InteractiveShell]:
    """Get or create interactive session (支持环境变量和MCP配置自动加载)"""
    # 如果没有提供ip_address，从环境变量或MCP配置读取
    if ip_address is None:
        ip_address = os.environ.get('HOST') or MCP_CONFIG.get('host')
        if not ip_address:
            return None
    if ip_address not in active_sessions:
        if create_if_not_exists:
            session = InteractiveShell(ip_address)
            if session.connect():
                active_sessions[ip_address] = {
                    'session': session,
                    'created_at': time.time()
                }
                return session
            else:
                return None
        else:
            return None
    
    session_data = active_sessions[ip_address]
    session = session_data['session']
    
    # Check if session is still alive
    if not session.is_connected:
        if session.connect():
            session_data['created_at'] = time.time()
        else:
            del active_sessions[ip_address]
            return None
    
    return session

def create_ssh_connection(ip_address, username=None, password=None, port=None):
    """Create SSH connection for one-time commands, with password and key fallback"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    # 配置优先级：用户参数 > 环境变量 > MCP配置 > 默认值
    connection_username = username or os.environ.get('USERNAME') or MCP_CONFIG.get('username') or DEFAULT_SSH_USERNAME
    connection_password = password or os.environ.get('PASSWORD') or MCP_CONFIG.get('password') or DEFAULT_SSH_PASSWORD
    connection_port = port or int(os.environ.get('PORT') or str(MCP_CONFIG.get('port', 22)))
    
    try:
        ssh.connect(
            hostname=ip_address,
            port=connection_port,
            username=connection_username,
            password=connection_password,
            timeout=10
        )
        logger.info(f"Successfully connected to {ip_address}")
        return ssh
    except Exception as e:
        ssh.close()
        raise Exception(f"SSH connection failed: {str(e)}")

@mcp.tool()
def connect_default_host() -> str:
    """使用环境变量或MCP配置自动连接到默认主机"""
    host = os.environ.get('HOST') or MCP_CONFIG.get('host')
    if not host:
        return "❌ 未在环境变量或MCP配置中设置HOST，无法自动连接"
    
    try:
        with create_ssh_connection(host) as ssh:
            stdin, stdout, stderr = ssh.exec_command("whoami && hostname && uptime")
            output = stdout.read().decode('utf-8', errors='ignore')
            return f"✅ 成功连接到 {host}\n系统信息:\n{output}"
    except Exception as e:
        return f"❌ 连接到 {host} 失败: {str(e)}"

@mcp.tool()
def ping_host(host: str = None, count: int = 4) -> str:
    """Ping host to check connectivity (cross-platform) - 支持环境变量和MCP配置自动加载"""
    # 如果没有提供host，从环境变量或MCP配置读取
    if host is None:
        host = os.environ.get('HOST') or MCP_CONFIG.get('host')
        if not host:
            return "❌ 未提供host参数且未在环境变量或MCP配置中设置HOST"
    
    try:
        # 检测操作系统类型
        import platform
        system = platform.system().lower()
        
        # 根据操作系统选择ping命令
        if system == "windows":
            # Windows: ping -n count -w timeout_ms host
            cmd = f"ping -n {count} -w 1000 {host}"
        else:
            # Linux/Unix: ping -c count -W timeout_sec host
            cmd = f"ping -c {count} -W 1 {host}"
        
        # 执行ping命令
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=30,
            creationflags=subprocess.CREATE_NO_WINDOW if system == "windows" else 0
        )
        
        # 格式化输出
        output = f"Ping {host} ({system}):\n"
        output += f"Command: {cmd}\n"
        output += f"Return code: {result.returncode}\n"
        
        if result.stdout:
            output += f"Output:\n{result.stdout}\n"
        if result.stderr:
            output += f"Error:\n{result.stderr}\n"
            
        # 简单的连通性判断
        if result.returncode == 0:
            output += "✅ Host is reachable"
        else:
            output += "❌ Host is unreachable"
            
        return output
        
    except subprocess.TimeoutExpired:
        return f"Ping {host}: ⏱️ Timeout after 30 seconds"
    except PermissionError:
        return f"Ping {host}: ❌ Permission denied. Try using alternative connectivity check."
    except FileNotFoundError:
        return f"Ping {host}: ❌ Ping command not found on system"
    except Exception as e:
        return f"Ping {host}: ❌ Error: {str(e)}"

@mcp.tool()
def create_interactive_session(ip_address: str = None, username: str = None, password: str = None, port: int = None) -> str:
    """Create a persistent interactive SSH session - 支持环境变量和MCP配置自动加载"""
    # 配置优先级：用户参数 > 环境变量 > MCP配置 > 默认值
    
    # 如果没有提供ip_address，从环境变量或MCP配置读取
    if ip_address is None:
        ip_address = os.environ.get('HOST') or MCP_CONFIG.get('host')
        if not ip_address:
            return "❌ 未提供ip_address参数且未在环境变量或MCP配置中设置HOST"
    
    # 如果没有提供username，从环境变量或MCP配置读取
    if username is None:
        username = os.environ.get('USERNAME') or MCP_CONFIG.get('username') or DEFAULT_SSH_USERNAME
    
    # 如果没有提供password，从环境变量或MCP配置读取
    if password is None:
        password = os.environ.get('PASSWORD') or MCP_CONFIG.get('password') or DEFAULT_SSH_PASSWORD
    
    # 如果没有提供port，从环境变量或MCP配置读取
    if port is None:
        port = int(os.environ.get('PORT') or str(MCP_CONFIG.get('port', 22)))
    
    try:
        session = InteractiveShell(ip_address, username, password, port)
        if session.connect():
            active_sessions[ip_address] = {
                'session': session,
                'created_at': time.time()
            }
            return f"Interactive session created for {ip_address}. Session ID: {ip_address}"
        else:
            return f"Failed to create interactive session for {ip_address}"
    except Exception as e:
        return f"Session creation failed: {str(e)}"

@mcp.tool()
def execute_interactive_command(ip_address: str, command: str, timeout: int = 30) -> str:
    """Execute command in interactive session with persistent state"""
    session = get_session(ip_address)
    if not session:
        return f"No active session for {ip_address}. Create one first."
    
    output, success = session.execute_command(command, timeout)
    if success:
        return f"Command: {command}\nOutput:\n{output}"
    else:
        return f"Command execution failed: {output}"

@mcp.tool()
def send_interactive_input(ip_address: str, input_text: str) -> str:
    """Send input to interactive command (for commands requiring user input)"""
    session = get_session(ip_address, create_if_not_exists=False)
    if not session:
        return f"No active session for {ip_address}"
    
    session.send_input(input_text)
    # Wait a bit and get output
    time.sleep(1)
    output = session.get_real_time_output(2)
    return f"Input sent: {input_text}\nResponse:\n{output}"

@mcp.tool()
def get_real_time_output(ip_address: str, duration: int = 5) -> str:
    """Get real-time output from interactive session"""
    session = get_session(ip_address, create_if_not_exists=False)
    if not session:
        return f"No active session for {ip_address}"
    
    output = session.get_real_time_output(duration)
    return f"Real-time output ({duration}s):\n{output}"

@mcp.tool()
def execute_command(command: str, ip_address: str = None, timeout: int = 30) -> str:
    """Execute single Linux command (non-interactive) - 支持环境变量和MCP配置自动加载"""
    # 如果没有提供ip_address，从环境变量或MCP配置读取
    if ip_address is None:
        ip_address = os.environ.get('HOST') or MCP_CONFIG.get('host')
        if not ip_address:
            return "❌ 未提供ip_address参数且未在环境变量或MCP配置中设置HOST"
    
    try:
        with create_ssh_connection(ip_address) as ssh:
            stdin, stdout, stderr = ssh.exec_command(command, timeout=timeout)
            
            output = stdout.read().decode('utf-8', errors='ignore')
            error = stderr.read().decode('utf-8', errors='ignore')
            exit_code = stdout.channel.recv_exit_status()
            
            result = f"Exit code: {exit_code}\n"
            if output:
                result += f"Output:\n{output}\n"
            if error:
                result += f"Error:\n{error}\n"
                
            return result
            
    except Exception as e:
        return f"Command execution failed: {str(e)}"

@mcp.tool()
def list_active_sessions() -> str:
    """List all active interactive sessions"""
    if not active_sessions:
        return "No active sessions"
    
    result = "Active Sessions:\n"
    for ip, session_data in active_sessions.items():
        session = session_data['session']
        created_at = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(session_data['created_at']))
        status = "Connected" if session.is_connected else "Disconnected"
        result += f"- {ip}: {status} (Created: {created_at})\n"
    
    return result

@mcp.tool()
def close_session(ip_address: str) -> str:
    """Close interactive session"""
    if ip_address in active_sessions:
        session = active_sessions[ip_address]['session']
        session.disconnect()
        del active_sessions[ip_address]
        return f"Session for {ip_address} closed"
    else:
        return f"No active session for {ip_address}"

@mcp.tool()
def quick_system_info(ip_address: str = None) -> str:
    """Quick system information retrieval - 支持环境变量和MCP配置自动加载"""
    # 如果没有提供ip_address，从环境变量或MCP配置读取
    if ip_address is None:
        ip_address = os.environ.get('HOST') or MCP_CONFIG.get('host')
        if not ip_address:
            return "❌ 未提供ip_address参数且未在环境变量或MCP配置中设置HOST"
    
    info_commands = [
        "uname -a",
        "cat /etc/os-release | head -5",
        "free -h",
        "df -h | head -5", 
        "ps aux | head -10"
    ]
    
    results = []
    for cmd in info_commands:
        result = execute_command(ip_address, cmd)
        results.append(f"=== {cmd} ===\n{result}")
    
    return "\n".join(results)

@mcp.tool()
def file_operations(operation: str, path: str, ip_address: str = None, content: str = None) -> str:
    """Enhanced file operations - 支持环境变量和MCP配置自动加载"""
    # 如果没有提供ip_address，从环境变量或MCP配置读取
    if ip_address is None:
        ip_address = os.environ.get('HOST') or MCP_CONFIG.get('host')
        if not ip_address:
            return "❌ 未提供ip_address参数且未在环境变量或MCP配置中设置HOST"
    
    try:
        with create_ssh_connection(ip_address) as ssh:
            if operation == "read":
                stdin, stdout, stderr = ssh.exec_command(f"cat {path}")
                output = stdout.read().decode('utf-8', errors='ignore')
                return output[:3000] + ("..." if len(output) > 3000 else "")
            
            elif operation == "write" and content:
                # Escape single quotes in content
                escaped_content = content.replace("'", "'\"'\"'")
                stdin, stdout, stderr = ssh.exec_command(f"echo '{escaped_content}' > {path}")
                return f"File written to: {path}"
            
            elif operation == "list":
                stdin, stdout, stderr = ssh.exec_command(f"ls -la {path}")
                return stdout.read().decode('utf-8', errors='ignore')
            
            elif operation == "exists":
                stdin, stdout, stderr = ssh.exec_command(f"test -f {path} && echo 'EXISTS' || echo 'NOT_EXISTS'")
                return stdout.read().decode('utf-8', errors='ignore').strip()
            
            else:
                return "Supported operations: read, write, list, exists"
                
    except Exception as e:
        return f"File operation failed: {str(e)}"

@mcp.tool()
def service_control(ip_address: str, service: str, action: str) -> str:
    """Service control with status information"""
    valid_actions = ["start", "stop", "restart", "status", "enable", "disable"]
    if action not in valid_actions:
        return f"Invalid action. Supported: {valid_actions}"
    
    command = f"systemctl {action} {service}"
    return execute_command(ip_address, command)

@mcp.tool()
def network_info(ip_address: str) -> str:
    """Enhanced network information"""
    network_commands = [
        "ip addr show | head -20",
        "netstat -tlnp | head -15",
        "ss -tlnp | head -15",
        "ufw status 2>/dev/null || echo 'UFW not installed'"
    ]
    
    results = []
    for cmd in network_commands:
        result = execute_command(ip_address, cmd)
        results.append(f"=== {cmd} ===\n{result}")
    
    return "\n".join(results)

@mcp.tool()
def monitor_process(ip_address: str, process_name: str) -> str:
    """Monitor specific process"""
    monitor_commands = [
        f"ps aux | grep {process_name} | grep -v grep",
        f"pgrep -f {process_name} | wc -l",
        f"systemctl is-active {process_name} 2>/dev/null || echo 'Service not found'"
    ]
    
    results = []
    for cmd in monitor_commands:
        result = execute_command(ip_address, cmd)
        results.append(f"=== {cmd} ===\n{result}")
    
    return "\n".join(results)

def main():
    """Main entry point for the linux-mcp-toolkit CLI"""
    try:
        # Enhanced Linux MCP Toolkit Starting...
        # Features:
        # - Interactive SSH sessions
        # - Real-time command output
        # - Persistent shell state
        # - Session management
        # - File operations
        # - System monitoring
        mcp.run()
    except UnicodeEncodeError:
        import sys
        sys.stdout.reconfigure(encoding='utf-8')
        # Linux MCP Toolkit Starting...
        mcp.run()

if __name__ == "__main__":
    main()