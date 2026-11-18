#!/usr/bin/env python3
"""Key-value store TCP server (ENPM631 Week 11).

Line-based text protocol, one command per line:
    HELLO <name>        -> WELCOME <name>
    SET <key> <value>   -> OK
    GET <key>           -> VALUE <value>  |  NOT_FOUND
    DEL <key>           -> DELETED        |  NOT_FOUND
    KEYS                -> KEYS <k1> <k2> ...
    QUIT                -> BYE (server closes the connection)

One thread per client connection; a lock protects the shared dictionary.
"""
import os
import socket
import threading

HOST = os.environ.get("KV_HOST", "0.0.0.0")
PORT = int(os.environ.get("KV_PORT", "5050"))

store = {}
lock = threading.Lock()


def log(msg):
    print(msg, flush=True)


def handle(cmd_line, name):
    parts = cmd_line.split(" ", 2)
    cmd = parts[0].upper()

    if cmd == "HELLO" and len(parts) >= 2:
        return f"WELCOME {parts[1]}", parts[1]
    if cmd == "SET" and len(parts) == 3:
        with lock:
            store[parts[1]] = parts[2]
        return "OK", name
    if cmd == "GET" and len(parts) == 2:
        with lock:
            value = store.get(parts[1])
        return (f"VALUE {value}" if value is not None else "NOT_FOUND"), name
    if cmd == "DEL" and len(parts) == 2:
        with lock:
            existed = store.pop(parts[1], None) is not None
        return ("DELETED" if existed else "NOT_FOUND"), name
    if cmd == "KEYS" and len(parts) == 1:
        with lock:
            keys = " ".join(sorted(store))
        return f"KEYS {keys}".rstrip(), name
    if cmd == "QUIT":
        return "BYE", name
    return "ERR usage: SET <key> <value> | GET <key> | DEL <key> | KEYS | QUIT", name


def serve_client(conn, addr):
    name = f"{addr[0]}:{addr[1]}"
    active = False  # stay quiet for bare connect/close probes (e.g. healthchecks)
    with conn, conn.makefile("r", encoding="utf-8") as rfile:
        for line in rfile:
            line = line.strip()
            if not line:
                continue
            if not active:
                log(f"[+] connection from {addr[0]}:{addr[1]}")
                active = True
            reply, name = handle(line, name)
            log(f"[{name}] {line} -> {reply}")
            conn.sendall((reply + "\n").encode("utf-8"))
            if reply == "BYE":
                break
    if active:
        log(f"[-] {name} disconnected")


def main():
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((HOST, PORT))
    srv.listen()
    log(f"KV server listening on {HOST}:{PORT}")
    try:
        while True:
            conn, addr = srv.accept()
            threading.Thread(target=serve_client, args=(conn, addr), daemon=True).start()
    except KeyboardInterrupt:
        log("shutting down")
    finally:
        srv.close()


if __name__ == "__main__":
    main()
