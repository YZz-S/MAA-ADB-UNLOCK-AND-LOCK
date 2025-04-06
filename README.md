# MAA-ADB-UNLOCK-AND-LOCK

一个配合MAA (Maa Arknights Assistant) 使用的ADB工具，用于自动解锁和锁定手机屏幕，并处理分辨率设置。

## 项目介绍

本项目提供两个Python脚本用于：
1. 通过ADB自动解锁手机屏幕（`unlock_phone_new_with_config.py`）
2. 自动恢复分辨率并启动指定应用程序（`lock_phone_and_recovery_resolution_with_config.py`）

这些脚本可以与MAA等自动化工具配合使用，使其能够在无人值守的情况下完成解锁手机、运行游戏以及恢复状态的全自动流程。

## 主要功能

- 自动通过ADB连接手机设备（支持IP连接）
- 自动解锁手机屏幕（支持PIN码解锁）
- 调整屏幕分辨率适配自动化操作
- 自动启动指定的应用程序
- 在操作失败时通过邮件发送通知

## 使用方法

### 准备工作

1. 确保您的手机已开启USB调试模式
2. 复制`config.example.ini`为`config.ini`并根据自己的情况配置：
   - ADB设备IP地址和端口
   - 邮件通知设置
   - 目标应用程序包名和应用名称

### 配置文件说明

```ini
[ADB]
device_ip = your_phone_adb_ip:your_phone_adb_port  # 手机ADB连接地址和端口

[Email]
smtp_server = smtp.example.com  # SMTP服务器地址
smtp_port = 587  # SMTP端口
sender = your_email@example.com  # 发件人邮箱
receiver = receiver@example.com  # 收件人邮箱
password = your_password  # 邮箱密码

[App]
package_name = com.dev47apps.droidcam  # 目标应用包名
app_name = DroidCam  # 目标应用名称
```

### 运行脚本

1. 解锁手机屏幕：
```
python unlock_phone_new_with_config.py
```

2. 恢复分辨率并启动应用：
```
python lock_phone_and_recovery_resolution_with_config.py
```

## 与MAA集成

您可以将这些脚本添加到MAA的自动化流程中，使其能够：
1. 在启动游戏前自动解锁手机
2. 在完成游戏任务后恢复手机状态

## 注意事项

- 本项目包含ADB可执行文件（Windows版本），无需额外安装ADB
- 确保config.ini中的PIN码等敏感信息安全存储
- 脚本中的分辨率设置可能需要根据您的设备进行调整
