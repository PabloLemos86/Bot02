import requests
import config

url = f"https://api.telegram.org/bot{config.TOKEN}/setWebhook"
webhook_url = f"https://seu-projeto.up.railway.app/{config.TOKEN}"

resp = requests.post(url, data={"url": webhook_url})
print(resp.json())