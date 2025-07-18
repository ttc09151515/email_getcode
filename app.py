from flask import Flask, jsonify, request, render_template
import requests
import os

app = Flask(__name__)

def get_verification_code(email):
    api_url = "https://domain-open-api.cuiqiu.com/v1/message/list"
    
    # 从环境变量中获取 token
    token = os.getenv("API_TOKEN", "0e67a1356be643b9b3644c3d3df1dcf6")

    # 定义请求的参数和数据
    form_data = {
        "token": token,
        "folder": "Inbox",
        "mail_id": "1732607589833756811",
        "start_time": "2024-05-01",
        "end_time": "2025-12-24",
        "page": "1",
        "limit": "10",
        "to": email,
    }

    try:
        # 发送 POST 请求
        response = requests.post(api_url, data=form_data)
        response.raise_for_status()  # 如果请求失败（状态码不是 2xx），则会抛出异常
        return response.json()
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching verification code: {e}")
        return None

# 路由处理
@app.route('/get_code/<email>', methods=['GET'])
def get_code(email):
    try:
        # 获取验证码邮件数据
        response_data = get_verification_code(email)
        
        if response_data and response_data.get("code") == 200:
            emails = response_data.get("data", {}).get("list", [])
            
            # 只取最新的前5条邮件
            latest_emails = [
                {
                    "recipient": email_data["to"][0]["address"],
                    "subject": email_data["subject"],
                    "time": email_data["time"]
                }
                for email_data in emails[:5]
            ]
            
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
    # 启动 Flask 应用，监听所有外部请求
    app.run(host='0.0.0.0', port=int(os.getenv("PORT", 5000)))
