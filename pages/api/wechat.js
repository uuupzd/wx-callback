const WXBizMsgCrypt = require('wechat-crypto-ts');


const TOKEN = 'PjUxjVF';
const ENCODING_AES_KEY = 'RcykAQ8QalwC1ZmkdyCwse1VcDKNJJkDyEuRZi3tz7r'; // 43位字符
const CORP_ID = "wwf66bbdf6c11de897"; // 企业微信后台查看

const crypto = new WechatCrypto(TOKEN, ENCODING_AES_KEY, CORP_ID);

export default function handler(req, res) {
    if (req.method === 'GET') {
        const { msg_signature, timestamp, nonce, echostr } = req.query;

        try {
            const decrypted = crypto.decrypt(echostr, msg_signature, timestamp, nonce);
            res.status(200).send(decrypted.message);
        } catch (err) {
            console.error('解密失败:', err);
            res.status(400).send('验证失败');
        }
    } else if (req.method === 'POST') {
        res.status(200).send('success');
    } else {
        res.status(405).send('Method Not Allowed');
    }
}