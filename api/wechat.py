# api/wechat.py
import hashlib
import os
import time
import xml.etree.ElementTree as ET
from urllib.parse import parse_qs
from http.server import BaseHTTPRequestHandler
import json

# 微信开发者配置的Token
TOKEN = os.environ.get('WECHAT_TOKEN', 'your_token_here')

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """处理微信服务器验证"""
        try:
            # 解析查询参数
            query_string = self.path.split('?')[1] if '?' in self.path else ''
            params = parse_qs(query_string)
            
            signature = params.get('signature', [''])[0]
            timestamp = params.get('timestamp', [''])[0]
            nonce = params.get('nonce', [''])[0]
            echostr = params.get('echostr', [''])[0]
            
            # 验证签名
            if self.verify_signature(signature, timestamp, nonce):
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(echostr.encode('utf-8'))
                print("微信验证成功")
            else:
                self.send_response(403)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'Verification failed')
                print("微信验证失败")
                
        except Exception as e:
            print(f"GET请求处理错误: {e}")
            self.send_response(500)
            self.end_headers()

    def do_POST(self):
        """处理微信消息"""
        try:
            # 获取请求体
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            # 解析XML消息
            message = self.parse_xml_message(post_data.decode('utf-8'))
            print(f"收到微信消息: {message}")
            
            # 处理消息并生成回复
            response_xml = self.handle_message(message)
            
            # 发送响应
            self.send_response(200)
            self.send_header('Content-type', 'application/xml')
            self.end_headers()
            self.wfile.write(response_xml.encode('utf-8'))
            
        except Exception as e:
            print(f"POST请求处理错误: {e}")
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b'success')

    def verify_signature(self, signature, timestamp, nonce):
        """验证微信签名"""
        try:
            # 将token、timestamp、nonce三个参数进行字典序排序
            tmp_arr = [TOKEN, timestamp, nonce]
            tmp_arr.sort()
            tmp_str = ''.join(tmp_arr)
            
            # 对排序后的字符串进行sha1加密
            sha1 = hashlib.sha1()
            sha1.update(tmp_str.encode('utf-8'))
            hash_code = sha1.hexdigest()
            
            # 比较加密后的字符串与signature
            return hash_code == signature
        except Exception as e:
            print(f"签名验证错误: {e}")
            return False

    def parse_xml_message(self, xml_data):
        """解析XML消息"""
        try:
            root = ET.fromstring(xml_data)
            message = {}
            for child in root:
                message[child.tag] = child.text
            return message
        except Exception as e:
            print(f"XML解析错误: {e}")
            return {}

    def handle_message(self, message):
        """处理不同类型的消息"""
        msg_type = message.get('MsgType', '')
        from_user = message.get('FromUserName', '')
        to_user = message.get('ToUserName', '')
        
        if msg_type == 'text':
            # 处理文本消息
            content = message.get('Content', '')
            reply_content = self.handle_text_message(content)
            return self.create_text_response(from_user, to_user, reply_content)
        
        elif msg_type == 'image':
            # 处理图片消息
            return self.create_text_response(from_user, to_user, '收到了你的图片！')
        
        elif msg_type == 'voice':
            # 处理语音消息
            return self.create_text_response(from_user, to_user, '收到了你的语音消息！')
        
        elif msg_type == 'event':
            # 处理事件消息
            event = message.get('Event', '')
            return self.handle_event_message(from_user, to_user, event)
        
        else:
            # 默认回复
            return self.create_text_response(from_user, to_user, '收到你的消息啦！')

    def handle_text_message(self, content):
        """处理文本消息的具体逻辑"""
        content = content.lower().strip()
        
        if '你好' in content or 'hello' in content:
            return '你好！很高兴见到你！'
        elif '时间' in content:
            return f'现在是：{time.strftime("%Y-%m-%d %H:%M:%S")}'
        elif '帮助' in content:
            return '我可以回复你的消息哦！试试发送"你好"或"时间"'
        else:
            return f'你说了：{content}'

    def handle_event_message(self, from_user, to_user, event):
        """处理事件消息"""
        if event == 'subscribe':
            return self.create_text_response(
                from_user, to_user, 
                '欢迎关注！感谢你的关注，我会为你提供优质服务！'
            )
        elif event == 'unsubscribe':
            return self.create_text_response(from_user, to_user, '谢谢你的关注！')
        else:
            return self.create_text_response(from_user, to_user, '收到事件消息')

    def create_text_response(self, from_user, to_user, content):
        """创建文本回复消息"""
        response_xml = f"""<xml>
<ToUserName><![CDATA[{from_user}]]></ToUserName>
<FromUserName><![CDATA[{to_user}]]></FromUserName>
<CreateTime>{int(time.time())}</CreateTime>
<MsgType><![CDATA[text]]></MsgType>
<Content><![CDATA[{content}]]></Content>
</xml>"""
        return response_xml