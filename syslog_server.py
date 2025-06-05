import socket

# Syslog UDP Server Configuration
HOST = "0.0.0.0"  # Listen on all IPs
PORT = 514  # Standard Syslog port

def start_syslog_server():
    """Starts a simple Syslog server to receive logs"""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind((HOST, PORT))
        print(f"Syslog server listening on {HOST}:{PORT}")

        while True:
            data, addr = sock.recvfrom(1024)
            print(f"Received log from {addr}: {data.decode().strip()}")

if __name__ == "__main__":
    start_syslog_server()
