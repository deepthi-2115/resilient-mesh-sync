import socket, threading, json, time, random

NODE_ID = input("Enter node id: ")
PORT = int(input("Enter port (5000/5001/5002): "))

PEERS = []
for p in [5000,5001,5002]:
    if p != PORT:
        PEERS.append(("127.0.0.1", p))

state = {}
version = {NODE_ID: 0}
lock = threading.Lock()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", PORT))
sock.settimeout(1)

def send_state(peer):
    with lock:
        packet = json.dumps({
            "id": NODE_ID,
            "ver": version,
            "state": state
        })
    sock.sendto(packet.encode(), peer)

def listener():
    while True:
        try:
            data, addr = sock.recvfrom(4096)
            msg = json.loads(data.decode())
            peer = msg["id"]

            with lock:
                for k,v in msg["ver"].items():
                    if k not in version or v > version[k]:
                        version[k] = v

                for k,v in msg["state"].items():
                    state[k] = v

            print("Updated from", peer, state)

        except:
            pass

def sender():
    while True:
        time.sleep(3)

        with lock:
            version[NODE_ID] += 1
            state["val_"+NODE_ID] = version[NODE_ID]

        for p in PEERS:
            send_state(p)

        print("Sent:", state)

threading.Thread(target=listener,daemon=True).start()
threading.Thread(target=sender,daemon=True).start()

while True:

    time.sleep(1)
