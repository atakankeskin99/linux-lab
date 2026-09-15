import argparse
import re
import subprocess


def run_command(command):
    result = subprocess.run(
        command,
        capture_output=True,
        text=True
    )

    return result.stdout


def get_listening_sockets():
    return run_command(["ss", "-H", "-lntp4"])


def get_interfaces():
    output = run_command(["ip", "-br", "-4", "addr"])

    interfaces = {}

    for line in output.splitlines():
        columns = line.split()
        interface = columns[0]

        for column in columns[2:]:
            if "/" in column:
                address = column.split("/", 1)[0]
                interfaces[address] = interface

    return interfaces


def parse_local_address(local_address):
    address, port = local_address.rsplit(":", 1)

    if "%" in address:
        address = address.split("%", 1)[0]

    return address, port


def parse_processes(line):
    matches = re.findall(
        r'\("([^"]+)",pid=(\d+),fd=\d+\)',
        line
    )

    processes = []

    for name, pid in matches:
        processes.append({
            "name": name,
            "pid": int(pid)
        })

    return processes


def classify_scope(address, interfaces):
    if address.startswith("127."):
        return "LOOPBACK"

    if address == "0.0.0.0":
        return "ALL_INTERFACES"

    interface = interfaces.get(address)

    if interface == "tailscale0":
        return "TAILSCALE"

    if interface:
        return interface

    return "UNKNOWN"


def format_processes(processes):
    if not processes:
        return "-"

    return ", ".join(
        f"{process['name']} ({process['pid']})"
        for process in processes
    )


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Inspect listening TCP ports on Linux."
    )

    parser.add_argument(
        "--port",
        type=int,
        help="Show only the specified port"
    )

    return parser.parse_args()


def main():
    args = parse_arguments()

    output = get_listening_sockets()
    interfaces = get_interfaces()

    print(
        f"{'PORT':<8}"
        f"{'ADDRESS':<18}"
        f"{'SCOPE':<18}"
        f"PROCESS"
    )
    print("-" * 75)

    for line in output.splitlines():
        columns = line.split()

        if len(columns) < 4:
            continue

        local_address = columns[3]
        address, port = parse_local_address(local_address)

        if args.port is not None and int(port) != args.port:
            continue

        scope = classify_scope(address, interfaces)
        processes = parse_processes(line)
        process_text = format_processes(processes)

        print(
            f"{port:<8}"
            f"{address:<18}"
            f"{scope:<18}"
            f"{process_text}"
        )


if __name__ == "__main__":
    main()
