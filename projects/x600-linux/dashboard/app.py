from flask import Flask, render_template_string
import platform
import shutil
import socket
import subprocess

app = Flask(__name__)


def safe_read(path, default="N/A"):
    try:
        with open(path, "r") as file:
            return file.read().strip()
    except Exception:
        return default


def get_uptime():
    try:
        raw = safe_read("/proc/uptime")
        seconds = float(raw.split()[0])
        days = int(seconds // 86400)
        hours = int((seconds % 86400) // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{days}d {hours}h {minutes}m" if days else f"{hours}h {minutes}m"
    except Exception:
        return "N/A"


def get_memory():
    try:
        meminfo = {}
        with open("/proc/meminfo", "r") as file:
            for line in file:
                if ":" not in line:
                    continue
                key, value = line.split(":", 1)
                parts = value.strip().split()
                if parts:
                    meminfo[key] = int(parts[0])

        total_kb = meminfo.get("MemTotal")
        available_kb = meminfo.get("MemAvailable")
        if not total_kb or available_kb is None:
            return "N/A", "N/A", "N/A"

        used_kb = total_kb - available_kb
        return (
            round(used_kb / 1024 / 1024, 2),
            round(total_kb / 1024 / 1024, 2),
            round((used_kb / total_kb) * 100, 1),
        )
    except Exception:
        return "N/A", "N/A", "N/A"


def get_disk():
    try:
        disk = shutil.disk_usage("/")
        return (
            round(disk.used / 1024**3, 2),
            round(disk.total / 1024**3, 2),
            round((disk.used / disk.total) * 100, 1),
        )
    except Exception:
        return "N/A", "N/A", "N/A"


def get_command_output(command):
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=2)
        return result.stdout.strip() or "N/A"
    except Exception:
        return "N/A"


def get_ip():
    try:
        result = subprocess.run(
            ["ip", "-4", "addr", "show", "wlan0"],
            capture_output=True,
            text=True,
            timeout=2,
        )
        for line in result.stdout.splitlines():
            line = line.strip()
            if line.startswith("inet "):
                return line.split()[1].split("/")[0]
    except Exception:
        pass
    return "N/A"


def get_battery():
    for path in (
        "/sys/class/power_supply/battery/capacity",
        "/sys/class/power_supply/Battery/capacity",
    ):
        value = safe_read(path, default=None)
        if value is not None:
            return f"{value}%"
    return "N/A"


def process_running(name):
    try:
        result = subprocess.run(
            ["pgrep", "-f", name], capture_output=True, text=True, timeout=2
        )
        return result.returncode == 0
    except Exception:
        return False


@app.route("/")
def index():
    used_ram, total_ram, ram_percent = get_memory()
    used_disk, total_disk, disk_percent = get_disk()

    html = """
    <!doctype html>
    <html lang="en">
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <title>X600 System Dashboard</title>
      <style>
        * { box-sizing: border-box; }
        body { margin: 0; font-family: Arial, sans-serif; background: #111827; color: #f9fafb; }
        .container { max-width: 1100px; margin: auto; padding: 30px; }
        h1 { margin: 0 0 5px; }
        .subtitle { color: #9ca3af; margin-bottom: 30px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 15px; }
        .card { background: #1f2937; border-radius: 14px; padding: 20px; }
        .label { color: #9ca3af; font-size: 14px; margin-bottom: 8px; }
        .value { font-size: 25px; font-weight: bold; word-break: break-word; }
        .status-on { color: #4ade80; }
        .status-off { color: #f87171; }
        .footer { margin-top: 30px; color: #6b7280; font-size: 13px; }
      </style>
    </head>
    <body>
      <div class="container">
        <h1>OMIX X600 System Dashboard</h1>
        <div class="subtitle">Android-hosted Linux environment</div>
        <div class="grid">
          <div class="card"><div class="label">Device</div><div class="value">{{ device }}</div></div>
          <div class="card"><div class="label">Android</div><div class="value">{{ android }}</div></div>
          <div class="card"><div class="label">Architecture</div><div class="value">{{ arch }}</div></div>
          <div class="card"><div class="label">Hostname</div><div class="value">{{ hostname }}</div></div>
          <div class="card"><div class="label">IP Address</div><div class="value">{{ ip }}</div></div>
          <div class="card"><div class="label">Uptime</div><div class="value">{{ uptime }}</div></div>
          <div class="card"><div class="label">Battery</div><div class="value">{{ battery }}</div></div>
          <div class="card"><div class="label">RAM</div><div class="value">{{ used_ram }} / {{ total_ram }} GB</div><div class="label">{{ ram_percent }}%</div></div>
          <div class="card"><div class="label">Storage</div><div class="value">{{ used_disk }} / {{ total_disk }} GB</div><div class="label">{{ disk_percent }}%</div></div>
          <div class="card"><div class="label">SSH</div><div class="value {{ 'status-on' if ssh else 'status-off' }}">{{ 'RUNNING' if ssh else 'STOPPED' }}</div></div>
          <div class="card"><div class="label">VNC</div><div class="value {{ 'status-on' if vnc else 'status-off' }}">{{ 'RUNNING' if vnc else 'STOPPED' }}</div></div>
          <div class="card"><div class="label">XFCE</div><div class="value {{ 'status-on' if xfce else 'status-off' }}">{{ 'RUNNING' if xfce else 'STOPPED' }}</div></div>
        </div>
        <div class="footer">Refresh the page to update metrics.</div>
      </div>
    </body>
    </html>
    """

    return render_template_string(
        html,
        device=get_command_output(["getprop", "ro.product.model"]),
        android=get_command_output(["getprop", "ro.build.version.release"]),
        arch=platform.machine(),
        hostname=socket.gethostname(),
        ip=get_ip(),
        uptime=get_uptime(),
        battery=get_battery(),
        used_ram=used_ram,
        total_ram=total_ram,
        ram_percent=ram_percent,
        used_disk=used_disk,
        total_disk=total_disk,
        disk_percent=disk_percent,
        ssh=process_running("sshd"),
        vnc=process_running("Xvnc"),
        xfce=process_running("xfce4-session"),
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
