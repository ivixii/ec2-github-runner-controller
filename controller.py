import os
import hmac
import hashlib
import json
import subprocess
from flask import Flask, request, abort
from github import Github, GithubIntegration
from dotenv import load_dotenv

load_dotenv()

# Load environment variables
APP_ID = os.getenv("GH_APP_ID")
PRIVATE_KEY_PATH = os.getenv("GH_APP_PRIVATE_KEY_PATH")
WEBHOOK_SECRET = os.getenv("GH_WEBHOOK_SECRET")
RUNNER_LABELS = os.getenv("RUNNER_LABELS", "self-hosted,linux")
RUNNER_DIR = os.path.abspath("runner/github-runner")
ENTRYPOINT = "/runner/entrypoint.sh"

app = Flask(__name__)

def verify_signature(payload, signature):
    mac = hmac.new(WEBHOOK_SECRET.encode(), msg=payload, digestmod=hashlib.sha256)
    expected_signature = f"sha256={mac.hexdigest()}"
    return hmac.compare_digest(expected_signature, signature)

def get_installation_token(installation_id):
    integration = GithubIntegration(APP_ID, open(PRIVATE_KEY_PATH).read())
    token = integration.get_access_token(installation_id)
    return token.token

def launch_container(image, repo_full_name, token):
    print(f"[+] Launching container with image: {image}")

    cmd = [
        "docker", "run", "--rm", "-d",
        "-e", f"GH_REPO_URL=https://github.com/{repo_full_name}",
        "-e", f"GH_RUNNER_TOKEN={token}",
        "-e", f"LABELS={RUNNER_LABELS}",
        "-v", f"{RUNNER_DIR}:/runner",
        image,
        ENTRYPOINT
    ]

    subprocess.run(cmd, check=True)

@app.route("/webhook", methods=["POST"])
def webhook():
    payload = request.data
    signature = request.headers.get("X-Hub-Signature-256")

    if not signature or not verify_signature(payload, signature):
        print("[-] Webhook signature verification failed.")
        abort(403)

    event = request.headers.get("X-GitHub-Event")
    if event != "workflow_job":
        return "Ignored", 200

    data = json.loads(payload)
    action = data.get("action")
    job = data.get("workflow_job")

    if action != "queued" or not job:
        return "Ignored", 200

    image = job.get("container", {}).get("image")
    repo = data.get("repository", {}).get("full_name")
    installation_id = data.get("installation", {}).get("id")

    if not image or not repo or not installation_id:
        print("[-] Missing required fields in payload.")
        return "Bad Request", 400

    try:
        token = get_installation_token(installation_id)
        g = Github(token)
        runner_token = g.get_repo(repo).create_self_hosted_runner_registration_token().token
        launch_container(image, repo, runner_token)
        return "Runner launched", 200
    except Exception as e:
        print(f"[-] Error: {e}")
        return "Internal Server Error", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
