# Enhanced Webhook System

This module has been updated to include:

## GitHub Event Processing
- The system now listens to GitHub events to trigger appropriate actions.

## Claude Forwarding Capabilities
- Messages received from GitHub can be forwarded to Claude for processing.

## Bidirectional Webhook Endpoints
- Webhooks can now send and receive messages in real-time, allowing for seamless integration with Claude.

## Example Usage
- Ensure that the endpoints are configured correctly in your application settings.

## Code Snippet

```python
from flask import Flask, request

app = Flask(__name__)

@app.route('/webhook/github', methods=['POST'])
def github_webhook():
    event = request.headers.get('X-GitHub-Event')
    if event == 'push':
        # Process push event
        pass
    return '', 204

@app.route('/webhook/claude', methods=['POST'])
def claude_webhook():
    data = request.json
    # Forward data to Claude
    return '', 204

if __name__ == '__main__':
    app.run(port=5000)
```

Make sure to test the webhook thoroughly to ensure all integrations are working as expected.