# UX_Python2
Python2 part for NAO robot project
# 🤖 NAO 机器人大模型面试实验 - 动作控制与传感端 (Robot Server)

## 📖 项目简介

本项目是“基于大语言模型（LLM）的 NAO 机器人面试官实验”的**物理控制层（Robot Server）**。

由于 NAO 机器人的底层 SDK (NAOqi) 强制要求 `Python 2.7 (32位)`，而现代大模型分析框架基于 `Python 3`，本项目作为两者之间的关键桥梁，负责管理机器人的“感觉神经”与“运动神经”。

本项目接收来自 Python 3 大脑的指令，并转换为真实的物理动作；同时收集机器人的麦克风和摄像头数据，实时推送给大脑。

---

## 🏗️ 核心架构说明

本项目相当于机器人的**躯干控制器**，包含三个独立的并行进程：

### 1. 运动神经（执行器）
**文件：** `command_server.py` + `nao_behavior_lib.py`
- 监听本地 `8000` 端口。
- 接收远端发送的 JSON 动作指令（如 `speak`, `stare`, `nod`）。
- 将指令解耦并映射为 NAOqi SDK 的底层物理驱动代码。

### 2. 听觉神经（传感器）
**文件：** `asr_realtime_pusher.py`
- 调用机器人麦克风，进行实时语音识别（ASR）。
- 将识别到的文本主动推送给远端大脑。

### 3. 视觉神经（传感器）
**文件：** `gaze_realtime_pusher.py`
- 调用机器人摄像头，进行人脸追踪与视线检测。
- 将眼神交互事件（如视线接触/躲避）推送给远端大脑。

---

## ✅ 已完成工作 (Current Progress)

- [x] **环境隔离与依赖突破**：彻底解决 Python 2.7 32位环境的 `%1 不是有效的 Win32 应用程序` 报错，通过 `sys.path.insert` 实现零配置即插即用。
- [x] **中文编码乱码修复**：解决 `ascii codec` 解码报错，实现顺畅的中文语音合成（TTS）。
- [x] **HTTP 控制服务搭建**：完成 `BaseHTTPServer` 的构建，支持平滑的 JSON 请求解析与 CORS 跨域。
- [x] **底层动作库解耦**：将复杂的 NAOqi API 封装为独立的 `nao_behavior_lib.py` 面向对象类，支持：
  - `speak(text)`: 说话
  - `nod()`: 倾听时点头
  - `shake_head()`: 摇头
  - `stare_pressure()`: 施加压力（低头死盯 + 眼睛变红）
  - `avert_gaze()`: 移开视线（低头 + 眼睛变蓝）
  - `reset_gaze()`: 恢复默认状态
  - `rest()`: 保护电机，蹲下休息
- [x] **路由指令打通**：在 Server 内部建立 `route_command`，实现外部指令字符串与物理动作的 100% 映射。

