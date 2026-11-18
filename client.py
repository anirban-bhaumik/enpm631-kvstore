#!/usr/bin/env python3
"""Key-value store TCP client (ENPM631 Week 11).

Interactive:  python3 client.py <host> <port> <username>
Headless:     python3 client.py <host> <port> <username> "SET color blue" "GET color"
              (sends each command, prints each reply, then exits; no keyboard input)
"""
import socket
import sys


def send(sock, rfile, line):
    sock.sendall((line + "\n").encode("utf-8"))
    reply = rfile.readline()
    if not reply:
        raise ConnectionError("server closed the connection")
    return reply.rstrip("\n")


def main():
    if len(sys.argv) < 4:
        print(__doc__)
        sys.exit(2)
    host, port, name = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    commands = sys.argv[4:]

    with socket.create_connection((host, port), timeout=10) as sock, \
            sock.makefile("r", encoding="utf-8") as rfile:
        print(send(sock, rfile, f"HELLO {name}"))

        if commands:  # headless mode
            for cmd in commands:
                print(f"> {cmd}")
                print(send(sock, rfile, cmd))
            send(sock, rfile, "QUIT")
            return

        sock.settimeout(None)  # interactive mode
        print("Commands: SET <key> <value> | GET <key> | DEL <key> | KEYS | QUIT")
        try:
            while True:
                line = input(f"{name}> ").strip()
                if not line:
                    continue
                reply = send(sock, rfile, line)
                print(reply)
                if reply == "BYE":
                    break
        except (EOFError, KeyboardInterrupt):
            send(sock, rfile, "QUIT")
            print()


if __name__ == "__main__":
    main()
