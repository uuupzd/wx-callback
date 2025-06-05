import { WechatCrypto } from 'wechat-enterprise';

const TOKEN = 'PjUxjVF';
const ENCODING_AES_KEY = 'RcykAQ8QalwC1ZmkdyCwse1VcDKNJJkDyEuRZi3tz7r'; // 43位字符
const CORP_ID = "wwf66bbdf6c11de897"; // 企业微信后台查看

const cryptor = new WechatCrypto(TOKEN, ENCODING_AES_KEY, CORP_ID);

export default function handler(req, res) {
    if (req.method === 'GET') {
        const { msg_signature, timestamp, nonce, echostr } = req.query;

        try {
            const decodedStr = cryptor.decrypt(echostr, msg_signature, timestamp, nonce);
            res.setHeader('Content-Type', 'text/plain');
            res.status(200).send(decodedStr);
        } catch (err) {
            console.error('验证失败', err);
            res.status(400).send('验证失败');
        }
    } else if (req.method === 'POST') {
        res.status(200).send('success');
    } else {
        res.status(405).send('Method Not Allowed');
    }
}

