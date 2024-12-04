from flask import Flask, request
import requests
from svix.webhooks import Webhook

app = Flask(__name__)
secret = "<WEBHOOK SIGNING SECRET>"
api_key = "<API KEY>"
api_url = "https://optipick.api.optioryx.com/latest"

@app.route('/webhook', methods=['POST'])
def hook():
    headers = request.headers
    payload = request.data

    wh = Webhook(secret)
    payload = wh.verify(payload, headers)

    for id in payload["item_ids"]:
        res = requests.get(f"{api_url}/optimize/cluster/{id}", headers={"X-API-KEY": api_key})
        print(id, res.json())

    return "OK"

if __name__ == '__main__':
    app.run()