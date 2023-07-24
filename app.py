from flask import Flask, render_template, request, jsonify, make_response
import requests
import uuid

app = Flask(__name__)

# 替换成您的API Key和Secret Key
API_KEY = ""
SECRET_KEY = ""

# 获取access_token
TOKEN_URL = f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={API_KEY}&client_secret={SECRET_KEY}"
response = requests.get(TOKEN_URL)
ACCESS_TOKEN = response.json()["access_token"]

# 定义ERNIE-Bot聊天接口地址
CHAT_API_URL = f"https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions?access_token={ACCESS_TOKEN}"
user_chat_histories = {}
@app.route("/")
def index():
    sessionid = str(uuid.uuid4())[:16]  # 生成随机的16位sessionid
    resp = make_response(render_template("index.html"))
    resp.set_cookie("sessionid", sessionid)  # 将sessionid存储在Cookie中
    return resp

@app.route("/chat", methods=["POST"])
def chat_with_ernie_bot():
    # 从前端获取用户输入的对话内容和sessionid
    user_id = request.cookies.get("sessionid")
    user_input = request.json["user_input"]
    # 获取该用户的对话历史，如果用户是首次对话，则新建一个空列表作为其对话历史
    user_history = user_chat_histories.get(user_id, [])
    
    # 将用户输入添加到对话历史中
    user_history.append({"role": "user", "content": user_input})
    # 调用ERNIE-Bot聊天接口
    headers = {"Content-Type": "application/json"}
    data = {"messages": user_history}
    print(user_id,data)
    response = requests.post(CHAT_API_URL, headers=headers, json=data)
    result = response.json()["result"]
    print(result)
    user_history.append({"role": "assistant", "content": result})
    user_chat_histories[user_id] = user_history
    return jsonify({"response": result})

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=13333,debug=False)
