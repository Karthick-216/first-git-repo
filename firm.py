from fastapi import FastAPI
from pydantic import BaseModel
import paramiko
import threading

app = FastAPI()

class Device(BaseModel):
    ip: str
    username: str
    password: str
    firmware: str

def upgrade_device(device: Device, results: dict):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(device.ip, username=device.username, password=device.password)

        # Simulated firmware upgrade command
        stdin, stdout, stderr = ssh.exec_command(f"upgrade {device.firmware}")
        results[device.ip] = stdout.read().decode() or "Upgrade Triggered"
        ssh.close()
    except Exception as e:
        results[device.ip] = f"Failed: {str(e)}"

@app.post("/upgrade")
def upgrade(devices: list[Device]):
    results = {}
    threads = []

    for device in devices:
        t = threading.Thread(target=upgrade_device, args=(device, results))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    return {"results": results}
