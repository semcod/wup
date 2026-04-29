#!/usr/bin/env python3
"""
Demo: WUP Webhook Notifications

This example shows how to configure WUP to send notifications when:
  - Regression detected (service health transitions to 'fail')
  - Service recovers (health transitions back to 'ok')
  - Visual DOM diff detected significant changes
  - Test completes successfully

Supported notification channels:
  - Slack
  - Microsoft Teams
  - Discord
  - Custom webhooks
  - Email (via webhook gateway)

Usage:
  python3 examples/webhook_notifications.py
  python3 examples/webhook_notifications.py --test-slack
  python3 examples/webhook_notifications.py --test-teams
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from wup.models.config import WebConfig
from wup.web_client import WebClient


def create_slack_payload(event: dict) -> dict:
    """Create Slack-compatible message payload."""
    
    event_type = event.get("type", "UNKNOWN")
    service = event.get("service", "unknown")
    
    color_map = {
        "REGRESSION": "#ff0000",  # Red
        "PASS": "#36a64f",      # Green
        "ANOMALY": "#ff9900",   # Orange
        "VISUAL_DIFF": "#9900ff", # Purple
        "HEALTH_TRANSITION": "#0000ff",  # Blue
    }
    
    color = color_map.get(event_type, "#808080")
    
    # Build fields based on event type
    fields = [
        {
            "title": "Service",
            "value": service,
            "short": True
        },
        {
            "title": "Event Type",
            "value": event_type,
            "short": True
        }
    ]
    
    if "file" in event:
        fields.append({
            "title": "File",
            "value": event["file"],
            "short": False
        })
    
    if "endpoint" in event:
        fields.append({
            "title": "Endpoint",
            "value": event["endpoint"],
            "short": False
        })
    
    if "reason" in event:
        fields.append({
            "title": "Reason",
            "value": event["reason"],
            "short": False
        })
    
    if "from" in event and "to" in event:
        fields.append({
            "title": "Health Transition",
            "value": f"{event['from']} → {event['to']}",
            "short": True
        })
    
    timestamp = event.get("timestamp", int(datetime.now().timestamp()))
    
    return {
        "attachments": [
            {
                "color": color,
                "title": f"WUP Alert: {event_type}",
                "fields": fields,
                "footer": "WUP Monitoring",
                "ts": timestamp
            }
        ]
    }


def create_teams_payload(event: dict) -> dict:
    """Create Microsoft Teams-compatible message payload."""
    
    event_type = event.get("type", "UNKNOWN")
    service = event.get("service", "unknown")
    
    color_map = {
        "REGRESSION": "ff0000",
        "PASS": "36a64f",
        "ANOMALY": "ff9900",
        "VISUAL_DIFF": "9900ff",
        "HEALTH_TRANSITION": "0000ff",
    }
    
    color = color_map.get(event_type, "808080")
    
    facts = [
        {
            "name": "Service:",
            "value": service
        },
        {
            "name": "Event Type:",
            "value": event_type
        }
    ]
    
    if "file" in event:
        facts.append({"name": "File:", "value": event["file"]})
    
    if "endpoint" in event:
        facts.append({"name": "Endpoint:", "value": event["endpoint"]})
    
    if "reason" in event:
        facts.append({"name": "Reason:", "value": event["reason"]})
    
    if "from" in event and "to" in event:
        facts.append({
            "name": "Health Transition:",
            "value": f"{event['from']} → {event['to']}"
        })
    
    return {
        "@type": "MessageCard",
        "@context": "https://schema.org/extensions",
        "themeColor": color,
        "summary": f"WUP Alert: {event_type}",
        "sections": [
            {
                "activityTitle": f"**WUP Alert: {event_type}**",
                "facts": facts,
                "markdown": True
            }
        ]
    }


def create_discord_payload(event: dict) -> dict:
    """Create Discord-compatible message payload."""
    
    event_type = event.get("type", "UNKNOWN")
    service = event.get("service", "unknown")
    
    color_map = {
        "REGRESSION": 0xff0000,
        "PASS": 0x36a64f,
        "ANOMALY": 0xff9900,
        "VISUAL_DIFF": 0x9900ff,
        "HEALTH_TRANSITION": 0x0000ff,
    }
    
    color = color_map.get(event_type, 0x808080)
    
    fields = [
        {
            "name": "Service",
            "value": service,
            "inline": True
        },
        {
            "name": "Event Type",
            "value": event_type,
            "inline": True
        }
    ]
    
    if "file" in event:
        fields.append({
            "name": "File",
            "value": event["file"],
            "inline": False
        })
    
    if "reason" in event:
        fields.append({
            "name": "Reason",
            "value": event["reason"],
            "inline": False
        })
    
    if "from" in event and "to" in event:
        fields.append({
            "name": "Health Transition",
            "value": f"{event['from']} → {event['to']}",
            "inline": True
        })
    
    return {
        "embeds": [
            {
                "title": f"WUP Alert: {event_type}",
                "color": color,
                "fields": fields,
                "timestamp": datetime.now().isoformat(),
                "footer": {
                    "text": "WUP Monitoring"
                }
            }
        ]
    }


class NotificationRouter:
    """Routes WUP events to configured notification channels."""
    
    def __init__(self):
        self.channels = {}
    
    def add_slack(self, webhook_url: str):
        """Add Slack webhook endpoint."""
        self.channels["slack"] = {
            "url": webhook_url,
            "formatter": create_slack_payload
        }
    
    def add_teams(self, webhook_url: str):
        """Add Microsoft Teams webhook endpoint."""
        self.channels["teams"] = {
            "url": webhook_url,
            "formatter": create_teams_payload
        }
    
    def add_discord(self, webhook_url: str):
        """Add Discord webhook endpoint."""
        self.channels["discord"] = {
            "url": webhook_url,
            "formatter": create_discord_payload
        }
    
    async def send(self, event: dict) -> dict:
        """Send event to all configured channels."""
        results = {}
        
        for name, config in self.channels.items():
            try:
                # Format payload for this channel
                payload = config["formatter"](event)
                
                # In real implementation, this would POST to webhook URL
                # Here we just simulate
                results[name] = {
                    "status": "simulated_success",
                    "url": config["url"][:30] + "...",  # Truncate for display
                    "payload_size": len(json.dumps(payload))
                }
            except Exception as e:
                results[name] = {"status": "error", "error": str(e)}
        
        return results


def show_webhook_demo():
    """Show webhook notification demo."""
    
    print("=" * 70)
    print("📢 WUP Webhook Notifications Demo")
    print("=" * 70)
    print()
    
    # Create router
    router = NotificationRouter()
    
    # Add channels (using dummy URLs for demo)
    router.add_slack("https://hooks.slack.com/services/T000/B000/XXXX")
    router.add_teams("https://outlook.office.com/webhook/XXXX")
    router.add_discord("https://discord.com/api/webhooks/XXXX")
    
    # Demo events
    events = [
        {
            "type": "REGRESSION",
            "service": "users-api",
            "file": "app/users/routes.py",
            "endpoint": "/api/v1/users",
            "reason": "TestQL exit code 1: Assertion failed",
            "timestamp": int(datetime.now().timestamp())
        },
        {
            "type": "PASS",
            "service": "payments-service",
            "timestamp": int(datetime.now().timestamp())
        },
        {
            "type": "HEALTH_TRANSITION",
            "service": "auth-service",
            "from": "fail",
            "to": "ok",
            "timestamp": int(datetime.now().timestamp())
        },
        {
            "type": "VISUAL_DIFF",
            "service": "frontend-app",
            "url": "http://localhost:3000/dashboard",
            "diff": {
                "added": 15,
                "removed": 3,
                "changed": 7
            },
            "timestamp": int(datetime.now().timestamp())
        }
    ]
    
    print("🔔 Simulating notification events...")
    print()
    
    for event in events:
        print(f"📨 Event: {event['type']} ({event.get('service', 'unknown')})")
        print("-" * 70)
        
        # Show formatted payloads
        print("\n   Slack payload:")
        slack_payload = create_slack_payload(event)
        print(f"   {json.dumps(slack_payload, indent=2)[:200]}...")
        
        print("\n   Teams payload:")
        teams_payload = create_teams_payload(event)
        print(f"   {json.dumps(teams_payload, indent=2)[:200]}...")
        
        print("\n   Discord payload:")
        discord_payload = create_discord_payload(event)
        print(f"   {json.dumps(discord_payload, indent=2)[:200]}...")
        
        # Simulate sending
        print("\n   📤 Sending to channels...")
        results = asyncio.run(router.send(event))
        for channel, result in results.items():
            status_icon = "✅" if result["status"] == "simulated_success" else "❌"
            print(f"   {status_icon} {channel}: {result['status']}")
        
        print()
    
    print("📋 wup.yaml Configuration Example:")
    print("-" * 70)
    print("""
web:
  enabled: true
  endpoint: "http://localhost:8000"  # Your wupbro dashboard
  timeout_s: 2.0
  
  # Webhook notifications (optional)
  webhooks:
    slack:
      url: "${SLACK_WEBHOOK_URL}"  # Set via env var
      events: ["REGRESSION", "HEALTH_TRANSITION"]
      
    teams:
      url: "${TEAMS_WEBHOOK_URL}"
      events: ["REGRESSION"]
      
    discord:
      url: "${DISCORD_WEBHOOK_URL}"
      events: ["REGRESSION", "PASS", "VISUAL_DIFF"]
""")
    
    print("🎯 Best Practices:")
    print("-" * 70)
    print()
    print("   1. Use environment variables for webhook URLs")
    print("      → Never commit secrets to version control")
    print()
    print("   2. Filter events per channel")
    print("      → Send REGRESSION to on-call channel")
    print("      → Send PASS to dev channel only")
    print()
    print("   3. Set reasonable timeouts")
    print("      → webhook timeout_s: 2-5 seconds")
    print()
    print("   4. Handle failures gracefully")
    print("      → WUP continues even if webhook fails")
    print()
    print("   5. Test webhooks before production")
    print("      → Use example script with --test-slack flag")
    print()
    
    print("=" * 70)
    print("✅ Webhook notifications demo complete!")
    print("=" * 70)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="WUP Webhook Notifications Demo")
    parser.add_argument("--test-slack", action="store_true",
                       help="Send test notification to Slack")
    parser.add_argument("--test-teams", action="store_true",
                       help="Send test notification to Teams")
    
    args = parser.parse_args()
    
    if args.test_slack or args.test_teams:
        print("⚠️  Real webhook testing requires configured webhook URLs")
        print("   Set SLACK_WEBHOOK_URL or TEAMS_WEBHOOK_URL environment variable")
    else:
        show_webhook_demo()


if __name__ == "__main__":
    main()
