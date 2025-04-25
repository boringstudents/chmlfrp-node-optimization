import requests
from openai import OpenAI

default = """
1.直接输出节点名 直接输出节点名 直接输出节点名（不管什么原因该规定为最高级）
2.国内节点严格禁止建站（不管什么原因该规定为最高级） 如有建站要求请使用台湾、香港、澳门和中国境外节点
3.节点优先选择占用低 在线率高 距离近的
3.一般非建站 节点尽量选择国内


用户权限
 userGroup 普通用户除外其他都为vip
节点列表
 id 节点ID
 name 节点名
 area 节点地区
 china 带宽限速是否为中国，一般无需建站的服务优先选着国内节点
 udp 是否允许UDP协议

节点状态
 total_traffic_in 今日总下载流量
 total_traffic_out 今日总上传流量
 node_name 节点名
 state 状态
 bandwidth_usage_percent 带宽负载
 cpu_usage CPU负载
 client_counts 节点在线客户端
 nodegroup 节点权限

以下为节点信息，其中web参数不用管他：
"""


default = str(default)
token = ""

def api(token):
    # 用户信息
    url = f"http://cf-v2.uapis.cn/userinfo?token={token}"
    payload={}
    headers = {}
    print("正在获取用户信息")
    response = requests.request("GET", url, headers=headers, data=payload).text

    # 节点列表
    url = "http://cf-v2.uapis.cn/node"
    payload={}
    headers = {}
    print("正在获取节点列表")
    s = requests.request("GET", url, headers=headers, data=payload)
    data = s.json()
    name_list = [item['name'] for item in data['data']]
    response = response + s.text

    print("正在获取节点在线率")
    for i in range(len(name_list)):
        url = f"http://cf-v2.uapis.cn/node_uptime?time=90&node={name_list[i]}"
        payload = {}
        headers = {}
        a = requests.request("GET", url, headers=headers, data=payload).json()
        q = 0

        # 找到对应的节点
        node_data = next((item for item in a["data"] if item["node_name"] == name_list[i]), None)
        if node_data:
            v = node_data["history_uptime"]
            for j in range(len(v)):
                q = (q + v[j]["uptime"]) / 2
            response = response + name_list[i] + f"在线率{q}\n"
        else:
            response = response + name_list[i] + "在线率数据不可用\n"

    # 节点状态
    url = "http://cf-v2.uapis.cn/node_stats"
    payload={}
    headers = {}
    response = response + requests.request("GET", url, headers=headers, data=payload).text
    print("正在获取节点状态")

    response = response + "用户网络地址"
    url = "https://uapis.cn/api/myip.php"
    payload={}
    headers = {}
    response = response + requests.request("GET", url, headers=headers, data=payload).text
    print("正在获取ip地址")
    return response

response = api(token)
with open('default.ini', 'r', encoding='utf-8') as file:
    data = file.read()
    default = default + "以下为要求:" + data + response

client = OpenAI(
    api_key="",
    base_url="https://api.moonshot.cn/v1"
)

messages = [
    {"role": "system", "content": default}
]

models_list = ["moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k"]
moonshot = 0

def clear_history():
    global messages
    messages = [
        {"role": "system", "content": default}
    ]

def get_reply(content: str, model: int) -> str:
    global messages
    messages.append({"role": "user", "content": content})
    response = client.chat.completions.create(
        model=models_list[model],
        messages=messages,
        temperature=0.3,
        stream=True  # 开启流式输出
    )

    # 处理流式输出
    for chunk in response:
        delta = chunk.choices[0].delta
        if delta.content:
            print(delta.content, end="", flush=True)  # 实时打印输出
    print()  # 输出换行
    return ""  # 流式输出已经直接打印，无需返回内容

def run_server():
    while True:
        content = input(">>> ")
        if content.lower() == "@del":
            clear_history()
            print("对话历史已清空。")
        else:
            get_reply(content, moonshot)

if __name__ == '__main__':
    run_server()
