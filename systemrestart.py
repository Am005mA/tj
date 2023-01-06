import json
import subprocess

json_path = "/root/tj/data.json"

def get_json_data(path):
    data_dict = dict()
    with open(path,'r') as _json_file_:
        data_dict = json.load(_json_file_)
    return data_dict

user_data = get_json_data(json_path)
for _uuid_ in user_data:
    subprocess.run(['trojan-go', '-api-addr', '127.0.0.1:10000', '-api', 'set', '-add-profile', '-target-password', _uuid_])
    subprocess.run(['trojan-go', '-api-addr', '127.0.0.1:10000', '-api', 'set', '-modify-profile', '-target-password', _uuid_, '-ip-limit', user_data[_uuid_]["user_limit"]])

subprocess.run(['trojan-go', '-config', '/root/tj/trogoconf.json'])
