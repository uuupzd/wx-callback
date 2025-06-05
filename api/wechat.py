from fastapi import FastAPI, Request
from wechatpy.enterprise.crypto import WeChatCrypto
from fastapi.responses import PlainTextResponse
import os

app = FastAPI()

# 企业微信配置（替换成你自己的）
TOKEN = "PjUxjVF"
ENCODING_AES_KEY = "RcykAQ8QalwC1ZmkdyCwse1VcDKNJJkDyEuRZi3tz7r"
CORP_ID = "wwf66bbdf6c11de897"

crypto = WeChatCrypto(TOKEN, ENCODING_AES_KEY, CORP_ID)


@app.get("/api/wechat")
async def verify(msg_signature: str, timestamp: str, nonce: str, echostr: str):
    try:
        decrypted = crypto.decrypt(echostr, msg_signature, timestamp, nonce)
        return PlainTextResponse(content=decrypted)
    except Exception as e:
        print("验证失败：", e)
        return PlainTextResponse("验证失败", status_code=400)


@app.post("/api/wechat")
async def handle_message(request: Request):
    # 这里可以处理 POST 消息事件，如文本消息、事件回调等
    return PlainTextResponse("success")
