# ENPM631 Week 11 Homework – TCP Key-Value Store

**Theme 2: Key-value store (`GET` / `SET` / `DEL`)**, written in Python.

- One TCP server (`server.py`) and one client program (`client.py`) that runs either **interactive** or **headless**.
- Containerized as a single image with a pinned tag: **`bhaumik/kvstore:1.0`**.
- Run with **Docker Compose** on a user-defined bridge network (`kvnet`); clients reach the server by its service name **`kvserver`**, not `localhost`. Port `5050` is published so a laptop (host) client can connect too.

## Files

| File | Purpose |
|---|---|
| `server.py` | TCP server; one thread per client, a lock protects the shared dictionary |
| `client.py` | Client; interactive when given only host/port/username, headless when commands follow |
| `Dockerfile` | Builds the image from `python:3.12-slim` (contains both server and client) |
| `compose.yaml` | `kvserver` + two headless clients (`alice`, `bob`) on network `kvnet` |
| `demo/` | Screenshots and logs of the shell demo and the Compose demo |

## Protocol

Plain text over TCP, one command per line, one reply per line.

| Command | Reply |
|---|---|
| `HELLO <name>` | `WELCOME <name>` (sent automatically by the client) |
| `SET <key> <value>` | `OK` |
| `GET <key>` | `VALUE <value>` or `NOT_FOUND` |
| `DEL <key>` | `DELETED` or `NOT_FOUND` |
| `KEYS` | `KEYS <key1> <key2> ...` |
| `QUIT` | `BYE`, then the server closes the connection |

Anything else returns `ERR usage: ...`.

## Client usage

```bash
# Interactive (reads commands from the keyboard)
python3 client.py <host> <port> <username>

# Headless (sends the given commands, prints each reply, exits; no keyboard input)
python3 client.py <host> <port> <username> "SET color blue" "GET color"
```

## Environment used

- Ubuntu on a Dell laptop, Python 3.12.3
- Docker 29.9.3 (Docker Desktop, context `desktop-linux`), Docker Compose v5.6.1

All commands below are run from the repository root.

## Part 1 – Shell demo (no containers)

Three terminal tabs. Bob (interactive) stays connected while Alice (headless) runs, so the server is serving two clients at the same time.

**Tab 1 – server**
```bash
mkdir -p demo
python3 server.py | tee demo/shell-server.log
```

**Tab 2 – Bob, interactive** (leave at the `bob>` prompt)
```bash
python3 client.py localhost 5050 bob
```

**Tab 3 – Alice, headless**
```bash
python3 client.py localhost 5050 alice "SET color blue" "SET course ENPM631" "KEYS" | tee demo/shell-alice.log
```

**Back in Tab 2**, at the `bob>` prompt:
```
GET color
DEL color
GET color
GET course
QUIT
```

Expected: Bob sees `VALUE blue`, `DELETED`, `NOT_FOUND`, `VALUE ENPM631`, `BYE`. Stop the server with `Ctrl+C`.

Evidence: `demo/shell-server.log`, `demo/shell-alice.log`, `demo/shell-server.png`, `demo/shell-alice-headless.png`, `demo/shell-bob-interactive.png`, `demo/shell-server-stopped.png`.

## Part 2 – Container demo

**Build the image with a pinned tag**
```bash
docker build -t bhaumik/kvstore:1.0 .
docker images | grep kvstore
```

**Start the stack** (server, then headless `alice`, then headless `bob`)
```bash
docker compose up -d
sleep 10
docker compose ps -a
docker network ls | grep kvnet
docker compose logs --no-color | tee demo/compose-demo.log
```

Expected: `kvserver` is `Up (healthy)` with `0.0.0.0:5050->5050/tcp`; `alice` and `bob` are `Exited (0)`; network `enpm631-kvstore_kvnet` exists. Alice and Bob connect to `kvserver:5050` by service name.

Startup order is handled in `compose.yaml`: `alice` waits for the server's healthcheck to pass, and `bob` waits for `alice` to finish successfully.

**Laptop (host) client through the published port**
```bash
python3 client.py localhost 5050 carol "GET course" "SET laptop yes" | tee demo/compose-laptop-client.log
```

**Interactive client inside the Docker network** (uses the same image, connects by service name)
```bash
docker compose run --rm --no-deps bob python client.py kvserver 5050 dave
```
At the `dave>` prompt: `GET laptop`, `KEYS`, `QUIT` → `VALUE yes`, `KEYS course laptop`, `BYE`.

**Server's view of all clients**
```bash
docker compose logs kvserver --no-color | tee demo/compose-server-final.log
```
The log shows `alice`, `bob` and `dave` connecting from container addresses on `kvnet` (`172.19.0.x`) and `carol` arriving from the network gateway (`172.19.0.1`, i.e. the host via the published port).

**Tear down**
```bash
docker compose down
```

Evidence: `demo/compose-demo.log`, `demo/compose-laptop-client.log`, `demo/compose-server-final.log`, `demo/compose-build.png`, `demo/compose-up-ps.png`, `demo/compose-network-logs.png`, `demo/compose-logs-bob.png`, `demo/compose-server-final.png`, `demo/compose-laptop-client.png`, `demo/compose-dave-interactive.png`.

## AI usage

I used Claude (Anthropic) in a claude.ai Project for ENPM631 to plan the work and generate `server.py`, `client.py`, `Dockerfile`, `compose.yaml` and this README. I ran every command myself on my Ubuntu machine and checked the output at each step; the screenshots and logs in `demo/` come from those runs.

### Prompts

My main prompts, in order, lightly edited for length. Screenshots I pasted for review are noted in brackets.

1. I want to use this thread for my course project. The project builds up in the form of a series of three consecutive homework assignments, provided in three consecutive weeks.
2. You can read the instructions for the 1st week assignment provided by the professor. I am attaching the PDF. *(attached: Week 11 Homework Instructions)*
3. A few baselines I wanted to discuss with you: 1. I will use my Dell-Ubuntu 2. I plan to use my GitHub and share the repo, not a zip.
4. The professor mentioned in the class to keep a simple architecture with 1 server and 2 clients. Why are we repeating instructions that clearly say that "containerize one image (or two) with a pinned tag"?
5. Before I proceed, I renamed yourname to 'bhaumik' matching my umd email. Then deleted demo folder, and ran everything again. Check all screenshots. *(screenshots: shell demo)*
