from flask import Flask, jsonify, request, render_template
import http.client
import json
from codecs import encode
import os

app = Flask(__name__)

# 根据提供的邮箱地址获取验证码
def get_verification_code(email):
    # 创建连接
    conn = http.client.HTTPSConnection("domain-open-api.cuiqiu.com")

    # 构造 multipart/form-data 请求的内容
    dataList = []
    boundary = 'wL36Yn8afVp8Ag7AmP8qZ0SA4n1v9T'

    # 添加 token
    dataList.append(encode('--' + boundary))
    dataList.append(encode('Content-Disposition: form-data; name=token;'))
    dataList.append(encode('Content-Type: {}'.format('text/plain')))
    dataList.append(encode(''))
    dataList.append(encode("0e67a1356be643b9b3644c3d3df1dcf6"))

    # 添加 folder
    dataList.append(encode('--' + boundary))
    dataList.append(encode('Content-Disposition: form-data; name=folder;'))
    dataList.append(encode('Content-Type: {}'.format('text/plain')))
    dataList.append(encode(''))
    dataList.append(encode("Inbox"))

    # 添加 mail_id
    dataList.append(encode('--' + boundary))
    dataList.append(encode('Content-Disposition: form-data; name=mail_id;'))
    dataList.append(encode('Content-Type: {}'.format('text/plain')))
    dataList.append(encode(''))
    dataList.append(encode("1732607589833756811"))

    # 添加 start_time
    dataList.append(encode('--' + boundary))
    dataList.append(encode('Content-Disposition: form-data; name=start_time;'))
    dataList.append(encode('Content-Type: {}'.format('text/plain')))
    dataList.append(encode(''))
    dataList.append(encode("2024-05-01"))

    # 添加 end_time
    dataList.append(encode('--' + boundary))
    dataList.append(encode('Content-Disposition: form-data; name=end_time;'))
    dataList.append(encode('Content-Type: {}'.format('text/plain')))
    dataList.append(encode(''))
    dataList.append(encode("2025-12-24"))

    # 添加 page 和 limit
    dataList.append(encode('--' + boundary))
    dataList.append(encode('Content-Disposition: form-data; name=page;'))
    dataList.append(encode('Content-Type: {}'.format('text/plain')))
    dataList.append(encode(''))
    dataList.append(encode("1"))

    dataList.append(encode('--' + boundary))
    dataList.append(encode('Content-Disposition: form-data; name=limit;'))
    dataList.append(encode('Content-Type: {}'.format('text/plain')))
    dataList.append(encode(''))
    dataList.append(encode("10"))

    # 添加收件邮箱
    dataList.append(encode('--' + boundary))
    dataList.append(encode('Content-Disposition: form-data; name=to;'))
    dataList.append(encode('Content-Type: {}'.format('text/plain')))
    dataList.append(encode(''))
    dataList.append(encode(email))

    # 完成请求的结束标记
    dataList.append(encode('--' + boundary + '--'))
    dataList.append(encode(''))

    # 构建请求体
    body = b'\r\n'.join(dataList)

    # 设置请求头
    headers = {
        'Content-type': 'multipart/form-data; boundary={}'.format(boundary)
    }

    # 发送 POST 请求
    conn.request("POST", "/v1/message/list", body, headers)

    # 获取响应
    res = conn.getresponse()
    data = res.read()

    # 返回解析后的响应数据
    return json.loads(data.decode("utf-8"))

# 路由处理
@app.route('/get_code/<email>', methods=['GET'])
def get_code(email):
    try:
        # 获取验证码邮件数据
        response_data = get_verification_code(email)
        
        # 提取邮件列表
        if response_data["code"] == 200:
            emails = response_data["data"]["list"]
            
            # 只取最新的前5条邮件
            latest_emails = []
            for email_data in emails[:5]:
                latest_emails.append({
                    "recipient": email_data["to"][0]["address"],  # 收件人
                    "subject": email_data["subject"],              # 标题
                    "time": email_data["time"]                     # 时间
                })
            
            return render_template('index.html', emails=latest_emails)
        else:
            return jsonify({
                "status": "error",
                "message": "Failed to retrieve emails"
            }), 500
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    # 启动 Flask 应用，确保监听所有外部请求
    app.run(host='0.0.0.0', port=int(os.getenv("PORT", 5000)))  # Railway 会自动设置环境变量 PORT
