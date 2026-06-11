#!/usr/bin/env python3
"""高性能异步端口扫描器 —— 支持 TCP/UDP 扫描、Banner 抓取、多种输出格式"""

import asyncio
import socket
import argparse
import json
import sys
import time
from ipaddress import ip_address


# ── 常用端口服务名 ──────────────────────────────────────────────
COMMON_PORTS = {
    20: "FTP-DATA", 21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP",
    53: "DNS", 67: "DHCP", 68: "DHCP", 69: "TFTP", 80: "HTTP",
    110: "POP3", 111: "RPC", 123: "NTP", 135: "RPC", 137: "NetBIOS",
    138: "NetBIOS", 139: "NetBIOS", 143: "IMAP", 161: "SNMP", 162: "SNMP",
    389: "LDAP", 443: "HTTPS", 445: "SMB", 465: "SMTPS", 514: "Syslog",
    587: "SMTP", 636: "LDAPS", 873: "Rsync", 993: "IMAPS", 995: "POP3S",
    1080: "SOCKS5", 1433: "MSSQL", 1521: "Oracle", 1723: "PPTP",
    1883: "MQTT", 2049: "NFS", 2375: "Docker", 2376: "Docker-TLS",
    3128: "Squid", 3306: "MySQL", 3389: "RDP", 3690: "SVN",
    4369: "RabbitMQ", 4444: "Metasploit", 4786: "Cisco", 5000: "Docker-Reg",
    5060: "SIP", 5353: "mDNS", 5432: "PostgreSQL", 5672: "RabbitMQ",
    5900: "VNC", 5985: "WinRM-HTTP", 5986: "WinRM-HTTPS", 6379: "Redis",
    6443: "K8s-API", 7000: "Cassandra", 7077: "Spark", 7474: "Neo4j",
    8000: "HTTP-Dev", 8009: "AJP", 8080: "HTTP-Alt", 8443: "HTTPS-Alt",
    8888: "Jupyter", 9000: "SonarQube", 9042: "Cassandra", 9092: "Kafka",
    9200: "ES", 9300: "ES", 9999: "Cassandra", 11211: "Memcached",
    15672: "RabbitMQ-Mgmt", 27017: "MongoDB", 27018: "MongoDB",
    28015: "RethinkDB", 49152: "WinRM-Alt",
}

# 常见端口对应的 Banner 探针（发送后读取响应）
BANNER_PROBES = {
    21:  b"",                          # FTP
    22:  b"",                          # SSH (read only)
    25:  b"EHLO scan.local\r\n",       # SMTP
    80:  b"HEAD / HTTP/1.0\r\n\r\n",  # HTTP
    110: b"",                          # POP3
    143: b"",                          # IMAP
    443: b"HEAD / HTTP/1.0\r\n\r\n",  # HTTPS (will get gibberish)
    3306: b"",                         # MySQL
    5432: b"",                         # PostgreSQL
    6379: b"PING\r\n",                # Redis
}


# ── 解析目标 ────────────────────────────────────────────────────
async def resolve_host(host: str) -> str:
    """解析域名到 IP，如果是 IP 则直接返回"""
    try:
        ip_address(host)
        return host
    except ValueError:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, socket.gethostbyname, host)


# ── 解析端口范围 ────────────────────────────────────────────────
def parse_ports(ports_str: str) -> list[int]:
    """解析端口字符串: 1-1024, 22,80,443, 或单个端口"""
    ports_str = ports_str.strip()
    if "," in ports_str:
        return sorted(set(int(p.strip()) for p in ports_str.split(",")))
    if "-" in ports_str:
        start, end = ports_str.split("-", 1)
        return list(range(int(start), int(end) + 1))
    return [int(ports_str)]


# ── TCP 扫描 ＋ Banner 抓取 ──────────────────────────────────────
def _tcp_connect(host: str, port: int, timeout: float, grab_banner: bool) -> tuple[int, bool, str]:
    """同步 TCP connect —— 在 executor 中运行"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        if sock.connect_ex((host, port)) != 0:
            return port, False, ""
        banner = ""
        if grab_banner:
            probe = BANNER_PROBES.get(port)
            if probe:
                try:
                    sock.sendall(probe)
                    sock.settimeout(timeout)
                    banner = sock.recv(1024).decode("utf-8", errors="replace").strip()
                except (socket.timeout, OSError):
                    pass
            elif probe is None and port in BANNER_PROBES:
                # 空探针 —— 直接读
                try:
                    sock.settimeout(timeout)
                    banner = sock.recv(1024).decode("utf-8", errors="replace").strip()
                except (socket.timeout, OSError):
                    pass
        return port, True, banner
    except OSError:
        return port, False, ""
    finally:
        sock.close()


async def tcp_scan(
    host: str, port: int, timeout: float, grab_banner: bool
) -> tuple[int, bool, str]:
    loop = asyncio.get_running_loop()
    try:
        return await asyncio.wait_for(
            loop.run_in_executor(None, _tcp_connect, host, port, timeout, grab_banner),
            timeout=timeout + 0.5,
        )
    except asyncio.TimeoutError:
        return port, False, ""


# ── UDP 扫描 ─────────────────────────────────────────────────────
def _udp_probe(host: str, port: int, timeout: float) -> tuple[int, bool, str]:
    """同步 UDP probe —— 发空包 + 读 ICMP/响应"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)
    try:
        sock.sendto(b"", (host, port))
        data, _ = sock.recvfrom(1024)
        return port, True, data.decode("utf-8", errors="replace").strip()
    except socket.timeout:
        # UDP 超时 = 可能是 open|filtered（无法区分）
        return port, False, ""
    except ConnectionRefusedError:
        return port, False, "closed"
    except OSError:
        return port, False, ""
    finally:
        sock.close()


async def udp_scan(
    host: str, port: int, timeout: float
) -> tuple[int, bool, str]:
    loop = asyncio.get_running_loop()
    try:
        return await asyncio.wait_for(
            loop.run_in_executor(None, _udp_probe, host, port, timeout),
            timeout=timeout + 0.5,
        )
    except asyncio.TimeoutError:
        return port, False, ""


# ── 主流程 ───────────────────────────────────────────────────────
async def main():
    parser = argparse.ArgumentParser(
        description="高性能异步端口扫描器 —— TCP/UDP 扫描 + Banner 抓取"
    )
    parser.add_argument("host", help="目标主机 (IP 或域名)")
    parser.add_argument("-p", "--ports", default="1-1024",
                        help="端口范围: 1-1024 / 22,80,443 / 8080 (默认 1-1024)")
    parser.add_argument("-t", "--timeout", type=float, default=1.0,
                        help="单端口超时秒数 (默认 1.0)")
    parser.add_argument("-c", "--concurrency", type=int, default=500,
                        help="并发数 (默认 500)")
    parser.add_argument("-u", "--udp", action="store_true",
                        help="UDP 扫描 (默认 TCP)")
    parser.add_argument("--common", action="store_true",
                        help="仅扫描常用端口")
    parser.add_argument("-b", "--banner", action="store_true",
                        help="抓取 Banner (TCP only)")
    parser.add_argument("-j", "--json", action="store_true",
                        help="JSON 格式输出")
    parser.add_argument("-o", "--open-only", action="store_true",
                        help="仅显示开放端口")
    parser.add_argument("-s", "--service", action="store_true",
                        help="仅扫描带已知服务名的端口")
    args = parser.parse_args()

    # 解析端口
    if args.common:
        ports = list(COMMON_PORTS.keys())
    elif args.service:
        ports = sorted(p for p in parse_ports(args.ports) if p in COMMON_PORTS)
        if not ports:
            print("错误: 指定范围内无已知服务端口", file=sys.stderr)
            sys.exit(1)
    else:
        ports = parse_ports(args.ports)

    # 解析主机
    try:
        ip = await resolve_host(args.host)
    except socket.gaierror:
        print(f"错误: 无法解析主机 '{args.host}'", file=sys.stderr)
        sys.exit(1)

    scan_type = "UDP" if args.udp else "TCP"
    print(f"\n{'='*60}")
    print(f"  目标: {args.host}" + (f" ({ip})" if ip != args.host else ""))
    print(f"  协议: {scan_type}")
    print(f"  端口: {ports[0]}-{ports[-1]}  ({len(ports)} 个)")
    print(f"  并发: {args.concurrency}   超时: {args.timeout}s")
    if args.banner and not args.udp:
        print(f"  Banner: 开启")
    print(f"{'='*60}\n")

    start_time = time.perf_counter()
    sem = asyncio.Semaphore(args.concurrency)
    open_results: list[tuple[int, str]] = []

    async def limited_scan(port):
        async with sem:
            if args.udp:
                res = await udp_scan(ip, port, args.timeout)
            else:
                res = await tcp_scan(ip, port, args.timeout, args.banner)
            return res

    tasks = [limited_scan(p) for p in ports]
    results = await asyncio.gather(*tasks)

    for port, is_open, banner in results:
        if is_open:
            svc = COMMON_PORTS.get(port, "?")
            label = (f" ({svc})" + (f"  |  {banner}" if banner else ""))
            if args.json:
                open_results.append((port, svc, banner))
            else:
                print(f"  [开放]  {port}/{scan_type.lower()}" + label)

    elapsed = time.perf_counter() - start_time

    # ── JSON 输出 ──
    if args.json:
        payload = {
            "target": args.host,
            "ip": ip,
            "protocol": scan_type.lower(),
            "scanned": len(ports),
            "open": len(open_results),
            "time_seconds": round(elapsed, 2),
            "ports": [
                {"port": p, "service": s, "banner": b}
                for p, s, b in open_results
            ],
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    print(f"\n{'─'*60}")
    print(f"  扫描 {len(ports)} 端口，耗时 {elapsed:.2f}s")
    print(f"  开放: {len(open_results)}   关闭/过滤: {len(ports) - len(open_results)}")
    print(f"{'─'*60}\n")


if __name__ == "__main__":
    asyncio.run(main())
