import os
import sys
import json
import argparse
import urllib.request


PYGIT_DIR = ".pygit"
CONFIG_FILE = os.path.join(PYGIT_DIR, "config.json")

def init_repo(ip_address):
    """Fakes 'git init' by saving the Pico's IP address."""
    if not os.path.exists(PYGIT_DIR):
        os.makedirs(PYGIT_DIR)
    
    config = {"pico_ip": ip_address}
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)
    
    print(f"Initialized empty PyGit repository.")
    print(f" Linked to Pico hardware at: {ip_address}")

def get_pico_ip():
    """Reads the saved IP address."""
    if not os.path.exists(CONFIG_FILE):
        print("❌ Fatal: Not a PyGit repository. Run 'python3 pygit.py init <IP>' first.")
        sys.exit(1)
    
    with open(CONFIG_FILE, "r") as f:
        return json.load(f).get("pico_ip")

def push_commit(filename, message, author):
    """Fakes 'git commit & push' by hitting our Pico API."""
    ip = get_pico_ip()
    url = f"http://{ip}/api/commit"
    
   
    payload = {
        "file": filename,
        "message": message,
        "author": author
    }
    
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    
    print(f" Pushing '{filename}' to bare-metal hardware...")
    
    try:
        with urllib.request.urlopen(req) as response:
            if response.status == 201:
                result = json.loads(response.read().decode())
                print(f" SUCCESS! File hashed and saved to Pico.")
                print(f" Hash: {result.get('hash', 'UNKNOWN')}")
            else:
                print(f" Pico responded with code {response.status}")
    except Exception as e:
        print(f" Connection to Pico failed: {e}")
        print("Is the Pico running 'userver.py' and connected to Wi-Fi?")

def log_history():
    """Fakes 'git log' by fetching the ledger from the Pico."""
    ip = get_pico_ip()
    url = f"http://{ip}/api/log"
    
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                history = json.loads(response.read().decode())
                
                print("\n" + "="*50)
             
                for commit in reversed(history):
                    print(f"\033[93mcommit {commit['hash']}\033[0m") # Yellow text
                    print(f"Author: {commit['author']}")
                    print(f"Date:   {commit['timestamp']}")
                    print(f"\n    {commit['message']}\n")
                print("="*50 + "\n")
            else:
                print(f" Pico responded with code {response.status}")
    except Exception as e:
        print(f" Could not fetch history: {e}")
def main():
    
    parser = argparse.ArgumentParser(description="PyGit: Bare-metal VCS Client")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    
    init_parser = subparsers.add_parser("init", help="Initialize repo and link Pico IP")
    init_parser.add_argument("ip", help="The local IP address of your Pico W")
    
   
    push_parser = subparsers.add_parser("push", help="Commit and push a file to the hardware")
    push_parser.add_argument("file", help="The target file on the Pico (e.g., sensor1_data.txt)")
    push_parser.add_argument("-m", "--message", required=True, help="Your commit message")
    push_parser.add_argument("-a", "--author", default="Fedora Terminal", help="Author name")
    
    
    log_parser = subparsers.add_parser("log", help="Show the commit history from the hardware")
    
   
    args = parser.parse_args()
    
    
    if args.command == "init":
        init_repo(args.ip)
    elif args.command == "push":
        push_commit(args.file, args.message, args.author)
    elif args.command == "log":
        log_history()
        

if __name__ == "__main__":
    main()