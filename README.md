# MAA-ADB-UNLOCK-AND-LOCK

一个配合MAA (Maa Arknights Assistant) 使用的ADB工具，用于自动解锁和锁定手机屏幕，并智能管理分辨率设置。

## 项目介绍

本项目提供两个Python脚本用于：
1. 通过ADB自动解锁手机屏幕（`unlock_phone_new_with_config.py`）
2. 自动恢复分辨率并启动指定应用程序（`lock_phone_and_recovery_resolution_with_config.py`）

这些脚本可以与MAA等自动化工具配合使用，使其能够在无人值守的情况下完成解锁手机、运行游戏以及恢复状态的全自动流程。

## 主要功能

### 🔓 自动解锁功能
- 自动通过ADB连接手机设备（支持IP连接）
- 自动解锁手机屏幕（支持PIN码解锁）
- 智能状态检测，确保解锁成功

### 📱 智能分辨率管理 ✨
- **自动保存原始分辨率**：解锁前自动保存设备当前分辨率
- **智能分辨率切换**：解锁时使用适合的分辨率，锁屏时恢复原始分辨率
- **配置化管理**：支持在配置文件中自定义各种分辨率
- **容错机制**：如果无法恢复原始分辨率，自动使用备用方案

### 📧 邮件通知系统
- 操作失败时自动发送邮件通知
- 支持QQ邮箱、Gmail等主流邮箱服务
- 智能错误处理，确保邮件发送稳定性

### 🔧 应用管理
- 自动启动指定的应用程序
- 支持多种启动方式（直接启动、monkey启动）
- 详细的应用检测和启动日志

## 核心组件

- `unlock_phone_new_with_config.py` - 解锁脚本，负责保存分辨率并解锁手机
- `lock_phone_and_recovery_resolution_with_config.py` - 锁屏脚本，负责恢复分辨率并启动应用
- `resolution_manager.py` - 分辨率管理核心模块
- `config.ini` - 主配置文件
- `EMAIL_FIX_REPORT.md` - 邮件修复详细报告
- `RESOLUTION_MANAGEMENT.md` - 分辨率管理功能详细说明

## 使用方法

### 准备工作

1. **手机设置**
   - 确保您的手机已开启USB调试模式
   - 如果使用WiFi连接，确保手机和电脑在同一网络

2. **配置文件设置**
   - 复制`config.example.ini`为`config.ini`
   - 根据您的实际情况配置各项参数

### 完整配置文件说明

```ini
[ADB]
device_ip = 192.168.1.100:5555  # 手机ADB连接地址和端口
lock_password = 123456  # 手机解锁密码
require_unlock = true  # 是否需要解锁操作

[Email]
smtp_server = smtp.qq.com  # SMTP服务器地址
smtp_port = 587  # SMTP端口（QQ邮箱推荐587）
sender = your_email@qq.com  # 发件人邮箱
receiver = receiver@qq.com  # 收件人邮箱
password = your_auth_code  # 邮箱授权码（非登录密码）

[App]
package_name = com.dev47apps.droidcam  # 目标应用包名
app_name = DroidCam  # 目标应用名称

[Resolution]
# 解锁操作时使用的分辨率
unlock_resolution = 720x1280
# 锁屏操作时使用的分辨率（备用方案）
lock_resolution = 1080x2400
# 是否保存和恢复原始分辨率
save_original_resolution = true
# 原始分辨率保存文件路径
original_resolution_file = original_resolution.txt
```

### 运行脚本

1. **解锁手机屏幕**：
```bash
python unlock_phone_new_with_config.py
```
此脚本会：
- 保存当前分辨率
- 设置为解锁专用分辨率
- 执行解锁操作
- 验证解锁状态

2. **恢复分辨率并启动应用**：
```bash
python lock_phone_and_recovery_resolution_with_config.py
```
此脚本会：
- 恢复到原始分辨率
- 启动指定应用程序
- 验证启动状态

### 分辨率管理独立使用

您也可以独立使用分辨率管理功能：

```python
from resolution_manager import ResolutionManager

# 创建管理器实例
manager = ResolutionManager()

# 保存当前分辨率
manager.save_original_resolution()

# 设置解锁分辨率
manager.set_unlock_resolution()

# 恢复原始分辨率
manager.restore_original_resolution()
```

## 与MAA集成

### 基础集成
您可以将这些脚本添加到MAA的自动化流程中：

1. **启动前**：运行 `unlock_phone_new_with_config.py` 解锁手机
2. **完成后**：运行 `lock_phone_and_recovery_resolution_with_config.py` 恢复状态

### 高级集成
利用分辨率管理功能，可以实现：
- 为MAA运行设置最佳分辨率
- 完成后自动恢复用户偏好的分辨率
- 确保不同应用都有最适合的显示设置

## 最新更新

### v2.1.0 - 智能分辨率管理
- ✨ 新增智能分辨率管理系统
- ✨ 自动保存和恢复原始分辨率
- ✨ 支持配置化的分辨率设置
- 🐛 修复QQ邮箱发送问题
- 📚 完善文档和示例

### v2.0.1 - 邮件系统修复
- 🐛 修复SMTP服务器配置问题
- 🐛 解决QQ邮箱连接关闭错误
- ✨ 增加双重发送策略（STARTTLS + SSL）
- 📧 优化邮件发送可靠性

## 故障排查

### 常见问题

1. **ADB连接失败**
   - 检查设备IP地址和端口是否正确
   - 确认手机已开启USB调试或无线调试
   - 尝试手动连接：`adb connect your_ip:port`

2. **邮件发送失败**
   - 确认使用正确的SMTP服务器和端口
   - 对于QQ邮箱，请使用授权码而非登录密码
   - 检查网络连接和防火墙设置

3. **分辨率设置问题**
   - 确认设备支持指定的分辨率格式
   - 检查ADB权限是否足够
   - 查看详细日志排查具体问题

4. **应用启动失败**
   - 确认应用包名正确
   - 检查应用是否已安装
   - 尝试不同的启动方式

### 日志查看
脚本运行时会输出详细日志，包括：
- ADB连接状态
- 分辨率变更记录
- 邮件发送状态
- 应用启动结果

## 注意事项

- ⚠️ 本项目包含ADB可执行文件（Windows版本），无需额外安装ADB
- 🔒 确保`config.ini`中的敏感信息（如密码）安全存储
- 📱 分辨率设置会临时改变设备显示，属于正常现象
- 🌐 使用WiFi ADB连接时，确保网络稳定
- 📧 邮件功能需要正确的SMTP配置和网络访问权限

## 技术支持

- 📖 详细分辨率管理说明：查看 `RESOLUTION_MANAGEMENT.md`
- 📧 邮件问题修复报告：查看 `EMAIL_FIX_REPORT.md`
- 🐛 问题反馈：请在GitHub Issues中报告
- 💡 功能建议：欢迎提交Pull Request

## 许可证

本项目采用开源许可证，详见 `LICENSE` 文件。
