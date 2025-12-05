# 🔍 EYE Watcher Mode - Continuous Monitoring

## Overview
Watcher Mode enables continuous monitoring of your infrastructure to detect changes in real-time. It automatically re-scans the target at specified intervals and alerts you when new assets or vulnerabilities are discovered.

## Features

### 🔄 Continuous Scanning
- Runs scans at configurable intervals (default: 6 hours)
- Persistent monitoring without manual intervention
- Graceful handling of errors and automatic retry

### 📊 Change Detection
- **New Subdomains**: Detects newly discovered subdomains
- **New Open Ports**: Identifies ports that were closed before
- **Removed Subdomains**: Tracks subdomains that are no longer resolvable
- **Closed Ports**: Monitors ports that were open but are now closed

### 💾 State Management
- Saves scan state to `state_{domain}.json`
- Tracks scan history and change timeline
- Preserves data between runs

### 🚨 Telegram Alerts
- Automatic notifications when changes are detected
- Detailed breakdown of new assets and vulnerabilities
- Works with existing `--alert` flag

## Usage

### Basic Monitoring
```bash
python main.py -d example.com --monitor
```

### Custom Interval (1 hour)
```bash
python main.py -d example.com --monitor --interval 3600
```

### With Telegram Alerts
```bash
python main.py -d example.com --monitor --alert
```

### With Custom Settings
```bash
python main.py -d example.com --monitor --interval 7200 --alert --no-fuzz
```

## Command-Line Arguments

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `--monitor` | flag | False | Enable continuous monitoring mode |
| `--interval` | int | 21600 | Scan interval in seconds (21600 = 6 hours) |
| `--alert` | flag | False | Enable Telegram notifications for changes |
| `--no-fuzz` | flag | False | Skip sensitive file fuzzing (faster scans) |

## State File Format

The watcher saves state to `state_{domain}.json`:

```json
{
  "timestamp": "2025-12-05T10:30:00",
  "domain": "example.com",
  "subdomains": ["sub1.example.com", "sub2.example.com"],
  "scan_results": [...],
  "statistics": {...},
  "scan_count": 5
}
```

## Change Detection Logic

### New Subdomains
Compares current subdomain list against previous state:
- **New**: Present in current scan but not in previous
- **Removed**: Present in previous scan but not in current

### Port Changes
Tracks open ports per host:
- **New Ports**: Port is open now but was closed before
- **Closed Ports**: Port was open before but is closed now
- **New Hosts**: Entirely new hosts with open ports

## Telegram Alert Format

When changes are detected, you'll receive an alert like:

```
🚨 Infrastructure Changes Detected
📍 Target: example.com
⏰ Time: 2025-12-05 10:30:00

🆕 New Subdomains (2):
  • api.example.com
  • dev.example.com

🔓 New Open Ports (1):
  • api.example.com: 8080, 9090
```

## Best Practices

### Recommended Intervals
- **Development/Staging**: 1-2 hours (`--interval 3600`)
- **Production**: 6-12 hours (`--interval 21600`)
- **Critical Assets**: 30 minutes - 1 hour (`--interval 1800`)

### Performance Tips
1. Use `--no-fuzz` for faster scans if you don't need file fuzzing
2. Longer intervals reduce resource usage
3. Monitor during off-peak hours to avoid detection

### Security Considerations
1. Run from a dedicated monitoring server
2. Ensure proper authorization for continuous scanning
3. Rotate IP addresses if performing external monitoring
4. Review state files regularly for anomalies

## Stopping the Watcher

To stop monitoring gracefully:
1. Press `Ctrl+C` in the terminal
2. The watcher will complete the current scan
3. Save the final state
4. Display summary statistics

## Example Workflow

### Initial Setup
```bash
# Start monitoring with hourly scans and alerts
python main.py -d target.com --monitor --interval 3600 --alert
```

### Output
```
════════════════════════════════════════════════════════════
                🔍 WATCHER MODE ACTIVATED
════════════════════════════════════════════════════════════
[*] Target: target.com
[*] Interval: 3600 seconds (1.0 hours)
[*] State file: state_target.com.json
[*] Press Ctrl+C to stop monitoring
════════════════════════════════════════════════════════════

[+] Telegram alerts enabled for change detection

════════════════════════════════════════════════════════════
🔄 SCAN #1 - 2025-12-05 10:00:00
════════════════════════════════════════════════════════════

[... scan output ...]

════════════════════════════════════════════════════════════
                     🔍 CHANGE DETECTION
════════════════════════════════════════════════════════════
[*] No previous state found. This is the first scan.
[*] State saved to state_target.com.json

════════════════════════════════════════════════════════════
✓ Scan #1 Complete
════════════════════════════════════════════════════════════
[*] Next scan in 3600 seconds (1.0 hours)
[*] Sleeping until 2025-12-05 11:00:00
```

## Integration with Existing Features

### Works With
- ✅ Telegram notifications (`--alert`)
- ✅ Sensitive file fuzzing (default) or `--no-fuzz`
- ✅ All scanning modules (subdomain, port, CORS, etc.)
- ✅ IP address scanning
- ✅ Domain scanning

### Automatic Features
- Change detection runs after every scan
- State is saved automatically after each scan
- Alerts are sent only when changes are detected
- First scan establishes baseline (no alerts)

## Troubleshooting

### No Changes Detected
- Ensure sufficient time has passed for infrastructure changes
- Verify the target is accessible
- Check state file exists and is valid JSON

### Watcher Stops Unexpectedly
- Check system resources (CPU, memory, network)
- Review error messages in console
- Verify target domain is still resolvable
- Check internet connectivity

### State File Issues
- Delete `state_{domain}.json` to reset baseline
- Verify write permissions in the EYE directory
- Ensure sufficient disk space

## Advanced Usage

### Multiple Targets
Run separate watcher instances for different targets:

```bash
# Terminal 1
python main.py -d target1.com --monitor --interval 3600

# Terminal 2
python main.py -d target2.com --monitor --interval 7200

# Terminal 3
python main.py -d target3.com --monitor --interval 1800
```

### Background Execution (Linux/Mac)
```bash
nohup python main.py -d example.com --monitor --alert > watcher.log 2>&1 &
```

### Scheduled Scans (Alternative to Watcher)
For non-continuous monitoring, use cron (Linux) or Task Scheduler (Windows):

```bash
# Cron: Run every 6 hours
0 */6 * * * cd /path/to/EYE && python main.py -d example.com --alert
```

## Technical Details

### Architecture
- **AssetWatcher Class**: Core monitoring logic
- **Async Loop**: Non-blocking execution using `asyncio`
- **State Persistence**: JSON-based storage
- **Change Detection**: Set-based comparison for efficiency

### Error Handling
- Scan failures trigger 60-second retry
- State file errors logged but don't stop monitoring
- Network timeouts handled gracefully
- Keyboard interrupt (Ctrl+C) stops cleanly

### Performance
- State file size: ~1-10 KB per domain
- Memory usage: Comparable to single scan
- CPU usage: Minimal between scans (sleeping)
- Network: Only during active scanning

## Future Enhancements

Planned features for future releases:
- [ ] Database storage for historical data
- [ ] Web dashboard for monitoring multiple targets
- [ ] Customizable change detection rules
- [ ] Webhook support for external integrations
- [ ] Email notifications
- [ ] Slack/Discord integration
- [ ] Automated response actions

---

**Note**: This tool is for authorized security testing only. Continuous monitoring may trigger rate limiting or detection systems. Use responsibly and ethically.
