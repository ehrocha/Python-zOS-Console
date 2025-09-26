import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class ZOSMFClient:
    def __init__(self, host, user, password, port=443):
        self.base_url = f"https://{host}:{port}/zosmf"
        self.session = requests.Session()
        self.session.auth = (user, password)

    def tso_command(self, cmd):
        url = f"{self.base_url}/tsoApp/v1/tso"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        payload = {"tsoCmd": cmd}
        response = self.session.put(url, json=payload, headers=headers, verify=False)
        response.raise_for_status()
        data = response.json()
        # Extract all 'message' fields from cmdResponse
        messages = []
        for item in data.get('cmdResponse', []):
            msg = item.get('message')
            if msg:
                messages.append(msg)
        return '\n'.join(messages) if messages else data

    def zos_command(self, cmd):
        # Build console name from user (assume format: USERIDC)
        console_name = f"{self.session.auth[0]}C"
        url = f"{self.base_url}/restconsoles/consoles/{console_name}"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        payload = {"cmd": cmd}
        response = self.session.put(url, json=payload, headers=headers, verify=False)
        response.raise_for_status()
        data = response.json()
        resp = data.get('cmd-response', '')
        return resp.replace('\r', '\n') if resp else resp
