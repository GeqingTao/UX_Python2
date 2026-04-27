# -*- coding: utf-8 -*-
import sys

# 1. 终结中文乱码魔法
reload(sys)
sys.setdefaultencoding('utf-8')

# 2. 指路牌：请把这里换成你真实的 32 位 SDK lib 路径
sys.path.insert(0, r"C:\Python27\Lib\site-packages")

import json
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

# 🌟【关键修改 1】导入我们刚刚写好的高压行为核心库
from nao_behavior_lib import NaoBehaviorController

# ==========================================
# 全局配置与变量
# ==========================================
SERVER_PORT = 8000
robot_controller = None  # 唯一的全局控制器对象


# ==========================================
# 🌟【关键修改 2】极简初始化逻辑
# ==========================================
def init_robot():
    global robot_controller
    try:
        # 尝试直连真实的物理机器人
        robot_controller = NaoBehaviorController(ip="192.168.93.152")
    except Exception as e:
        print("\n[WARNING] 实体机器人连接失败。为了保证网络联调不中断，启用精简虚拟替身...\n")

        # 精简虚拟替身：专门为了让你今天能和组员测试跨端 HTTP 通信
        class MockController(object):
            def speak(self, text): print("📢 [模拟执行]: 说话 -> " + text); return True

            def nod(self): print("💃 [模拟执行]: 点头"); return True

            def shake_head(self): print("💃 [模拟执行]: 摇头"); return True

            def stare_pressure(self): print("😠 [模拟执行]: 压迫性死盯 + 眼睛变红"); return True

            def avert_gaze(self): print("😒 [模拟执行]: 回避视线 + 眼睛变暗"); return True

            def reset_gaze(self): print("😐 [模拟执行]: 恢复正常视线"); return True

            def rest(self): print("🛌 [模拟执行]: 休息"); return True

        robot_controller = MockController()


# ==========================================
# 🌟【关键修改 3】统一的指令路由表 (彻底解耦)
# ==========================================
def route_command(command, payload):
    """将字符串命令映射到 robot_controller 的具体物理动作上"""
    if command == "speak":
        robot_controller.speak(payload.get("text", ""))
    elif command == "nod":
        robot_controller.nod()
    elif command == "shake_head":
        robot_controller.shake_head()
    elif command == "stare":
        robot_controller.stare_pressure()
    elif command == "avert_gaze":
        robot_controller.avert_gaze()
    elif command == "reset_gaze":
        robot_controller.reset_gaze()
    elif command == "rest":
        robot_controller.rest()
    else:
        raise ValueError("未知的指令类型: %s" % command)


    return {"status": "success", "message": command + " action completed"}


# ==========================================
# HTTP 服务器逻辑 (几乎不需要改动)
# ==========================================
class RequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/command':
            content_length = int(self.headers.getheader('content-length', 0))
            post_data = self.rfile.read(content_length)
            try:
                req_json = json.loads(post_data)
                command = req_json.get("command")
                payload = req_json.get("payload", {})

                print("\n" + "=" * 45)
                print("[HTTP] 收到指令 -> 命令: %s" % command)

                # 调用上面的路由函数
                result = route_command(command, payload)
                self._send_response(200, result)

            except ValueError as ve:
                print("[ERROR] 指令错误: ", str(ve))
                self._send_response(400, {"status": "error", "message": str(ve)})
            except Exception as e:
                print("[ERROR] 执行命令异常: ", str(e))
                self._send_response(500, {"status": "error", "message": str(e)})
        else:
            self._send_response(404, {"status": "error"})

    def _send_response(self, status_code, response_dict):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response_dict))


if __name__ == '__main__':
    # 1. 尝试连接机器人 / 开启替身
    init_robot()

    # 2. 启动服务器监听
    httpd = HTTPServer(('', SERVER_PORT), RequestHandler)
    print("\n==============================================")
    print("[INFO] NAO 高压面试控制服务器 已启动...")
    print("[INFO] 监听端口: %d" % SERVER_PORT)
    print("==============================================\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.socket.close()
