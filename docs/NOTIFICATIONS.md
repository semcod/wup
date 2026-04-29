# Browser Notifications Guide

WUP Browser Dashboard (wupbro) supports real-time browser notifications
for regression events, health changes, and anomalies.

## Overview

Notifications are sent via Server-Sent Events (SSE) and displayed using
the native Browser Notifications API. They work even when the dashboard
tab is not active.

## Quick Setup

### 1. Enable Notifications in Dashboard

Open the dashboard at `http://localhost:8000` and click:

```
🔔 Włącz powiadomienia
```

Grant permission when browser prompts.

### 2. Configure What to Receive

Click `⚙️ Konfiguracja` to open the notification panel:

```
🔔 Konfiguracja powiadomień [abc123]

🚨 Regresje
  [✓] Nowa regresja
  [ ] Kolejna regresja (≤30s)
  [✓] Odzyskanie (fail→pass)

🔄 Zmiany stanu
  [✓] Dowolna zmiana
  [✓] Zdrowie usługi
  [✓] Nowa anomalia

👁️ Inne
  [ ] Różnica wizualna
  
Cooldown: 5s
```

### 3. Test Notification

Click `🧪 Test` to send a test notification.

## Notification Types

| Type | Icon | Trigger | Default |
|------|------|---------|---------|
| `REGRESSION_NEW` | 🚨 | New regression detected | ✅ |
| `REGRESSION_DIFF` | ⚠️ | Multiple regressions within 30s | ❌ |
| `STATUS_TRANSITION` | 🔄 | Any status change | ✅ |
| `PASS_RECOVERY` | ✅ | Service recovered (fail → pass) | ✅ |
| `ANOMALY_NEW` | 🔶 | New anomaly in metrics | ✅ |
| `VISUAL_DIFF_NEW` | 👁️ | Visual DOM difference detected | ❌ |
| `HEALTH_CHANGE` | 💓 | Service health state changed | ✅ |

## How It Works

### Architecture

```
┌──────────────────┐    POST /events    ┌──────────────────┐
│   WUP Agent      │ ─────────────────> │   wupbro Server  │
│   (file watcher) │                    │   (FastAPI)      │
└──────────────────┘                    └────────┬─────────┘
                                                  │
                                                  │ SSE
                                                  ▼
┌──────────────────┐                    ┌──────────────────┐
│  Browser Tab     │ <── EventSource ─│  Browser Client  │
│  (inactive)      │                    │  (Dashboard)     │
└──────────────────┘                    └────────┬─────────┘
                                                  │
                                                  ▼
                                          ┌──────────────────┐
                                          │  Notification    │
                                          │  (System API)    │
                                          └──────────────────┘
```

### Event Flow

1. WUP agent detects change and POSTs event to `/events`
2. Server processes event through `NotificationManager`
3. Matching subscriptions trigger notifications
4. Notifications pushed via SSE to connected clients
5. Browser displays native notification

## API Reference

### Subscribe to Notifications

```bash
POST /notifications/subscribe
Content-Type: application/json

{
  "enabled": true,
  "regression_new": true,
  "regression_diff": false,
  "regression_diff_seconds": 30,
  "status_transition": true,
  "status_transition_type": "ANY",
  "anomaly_new": true,
  "visual_diff_new": false,
  "health_change": true,
  "pass_recovery": true,
  "cooldown_seconds": 5,
  "services_include": [],
  "services_exclude": []
}
```

Response:
```json
{
  "subscription_id": "abc123",
  "config": { ... },
  "created_at": 1714411200,
  "last_notification_at": null
}
```

### Connect to SSE Stream

```javascript
const eventSource = new EventSource(
  '/notifications/stream?subscription_id=abc123'
);

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  if (data.type === 'connected') {
    console.log('Connected:', data);
    return;
  }
  
  // Show notification
  new Notification(data.title, {
    body: data.body,
    icon: '/favicon.ico',
    tag: data.notification_type
  });
};
```

### Update Configuration

```bash
PUT /notifications/subscriptions/{subscription_id}
Content-Type: application/json

{
  "enabled": true,
  "regression_new": false,  // Disable this type
  ...
}
```

### Send Test Notification

```bash
POST /notifications/test?subscription_id={subscription_id}
```

## Configuration Options

### Status Transition Types

| Type | Description | Example |
|------|-------------|---------|
| `HEALTHY_TO_UNHEALTHY` | Healthy → Unhealthy | PASS → FAIL |
| `UNHEALTHY_TO_HEALTHY` | Unhealthy → Healthy | FAIL → PASS |
| `ANY` | Any status change | Any transition |

### Service Filtering

```json
{
  "services_include": ["users-web", "payments-api"],
  "services_exclude": ["legacy-service"]
}
```

Empty `services_include` = all services.

### Cooldown

Prevents notification spam:

```json
{
  "cooldown_seconds": 30  // Minimum 30s between notifications
}
```

## Client-Side Storage

Configuration is persisted in localStorage:

```javascript
// Saved automatically
localStorage.setItem('wupbro_subscription_id', 'abc123');
localStorage.setItem('wupbro_notification_config', JSON.stringify(config));
```

## Customizing Notification Content

### Server-Side (Python)

Create custom payload in `NotificationManager._create_payload()`:

```python
NotificationPayload(
    notification_type="CUSTOM_TYPE",
    title="Custom Title",
    body="Custom message with {variable}",
    icon="/custom-icon.png",
    data={"custom": "data"}
)
```

### Client-Side (JavaScript)

Handle notification in dashboard:

```javascript
function showBrowserNotification(data) {
  const notification = new Notification(data.title, {
    body: data.body,
    icon: data.icon || '/favicon.ico',
    tag: data.notification_type,
    requireInteraction: data.severity === 'critical'
  });
  
  notification.onclick = () => {
    window.focus();
    // Navigate to relevant view
    if (data.service) {
      showServiceDetails(data.service);
    }
    notification.close();
  };
}
```

## Troubleshooting

### Notifications Not Showing

1. **Check permission:**
   ```javascript
   Notification.permission === 'granted'
   ```

2. **Check subscription:**
   ```bash
   GET /notifications/subscriptions/{id}
   ```

3. **Check SSE connection:**
   - Open DevTools → Network → EventStream
   - Look for `/notifications/stream` connection

4. **Check event processing:**
   - POST event should return `notifications_sent` count
   ```json
   {"accepted": true, "notifications_sent": 2}
   ```

### Too Many Notifications

Adjust configuration:

```json
{
  "cooldown_seconds": 60,        // Increase cooldown
  "regression_diff": false,      // Disable rapid-fire
  "services_include": ["prod-*"] // Filter to production only
}
```

### Notifications Delayed

Check SSE connection health:

```javascript
eventSource.onerror = (err) => {
  console.error('SSE error:', err);
  // Auto-reconnect after 5s
  setTimeout(connectSSE, 5000);
};
```

## Advanced Usage

### Programmatic Subscription

```python
import requests

# Subscribe
response = requests.post('http://localhost:8000/notifications/subscribe', json={
    'regression_new': True,
    'pass_recovery': True
})
sub_id = response.json()['subscription_id']

# Connect to SSE
import sseclient
import requests

response = requests.get(
    f'http://localhost:8000/notifications/stream?subscription_id={sub_id}',
    stream=True
)
client = sseclient.SSEClient(response)

for event in client.events():
    data = json.loads(event.data)
    print(f"Notification: {data['title']}")
```

### Slack Integration

Forward notifications to Slack:

```python
# In your notification handler
import requests

def on_notification(payload):
    requests.post('https://hooks.slack.com/...', json={
        'text': f"🚨 {payload.title}\n{payload.body}"
    })
```

## Security Considerations

- Subscription IDs are random 8-char strings
- No authentication required (local dashboard)
- For production, add API key header:
  ```
  Authorization: Bearer {api_key}
  ```

## Browser Support

| Browser | Notifications | SSE | Status |
|---------|--------------|-----|--------|
| Chrome | ✅ | ✅ | Full support |
| Firefox | ✅ | ✅ | Full support |
| Safari | ✅ | ✅ | Full support |
| Edge | ✅ | ✅ | Full support |

Mobile browsers have limited background notification support.
