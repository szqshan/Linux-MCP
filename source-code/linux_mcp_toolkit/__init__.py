"""
Linux MCP Toolkit - 交互式Linux管理工具包

这是一个基于MCP协议的Linux管理工具包，提供交互式SSH会话、
系统监控、文件操作等功能。
"""

__version__ = "1.0.10"
__author__ = "Linux MCP Toolkit Team"
__email__ = "contact@linuxmcp.com"
__description__ = "Enhanced Linux MCP Toolkit with Interactive Shell Support"

# 导出主要功能
from .main import *

# 版本信息
VERSION = __version__