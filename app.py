from flask import Flask, jsonify, request
import requests
import json

app = Flask(__name__)

ZABBIX_URL = "http://192.168.197.131/api_jsonrpc.php"
ZABBIX_USER = "Admin"
ZABBIX_PASSWORD = "zabbix"

def zabbix_login():
    headers = {'Content-Type': 'application/json'}
    payload = {
        "jsonrpc": "2.0",
        "method": "user.login",
        "params": {
            "user": ZABBIX_USER,
            "password": ZABBIX_PASSWORD
        },
        "id": 1
    }
    
    try:
        response = requests.post(ZABBIX_URL, headers=headers, json=payload)
        response.raise_for_status()  # Raise an error for bad responses
        result = response.json()
        
        if 'error' in result:
            print("Zabbix login error:", result['error'])
            return None  # Return None on error
        return result.get('result')
    
    except requests.exceptions.RequestException as e:
        print("Request failed:", e)
        return None
    except json.JSONDecodeError:
        print("Response is not in JSON format:", response.text)
        return None

@app.route('/api/zabbix/items', methods=['GET'])
def get_items():
    auth_token = zabbix_login()
    if not auth_token:
        return jsonify({"error": "Failed to authenticate with Zabbix"}), 401  # Authentication error

    headers = {'Content-Type': 'application/json'}
    payload = {
        "jsonrpc": "2.0",
        "method": "item.get",
        "params": {
            "output": "extend"
        },
        "auth": auth_token,
        "id": 1
    }
    
    try:
        response = requests.post(ZABBIX_URL, headers=headers, json=payload)
        response.raise_for_status()  # Raise an error for bad responses
        return jsonify(response.json())
    
    except requests.exceptions.RequestException as e:
        print("Request to Zabbix API failed:", e)
        return jsonify({"error": "Failed to get items from Zabbix"}), 500
    except json.JSONDecodeError:
        print("Response is not in JSON format:", response.text)
        return jsonify({"error": "Invalid response format"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


