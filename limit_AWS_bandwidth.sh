#!/usr/bin/env bash
set -euo pipefail
# Limit ONLY download (ingress) for dst port (default 6042) using IFB + HTB.
# Works without cls_flower (uses u32 'match ip dport').

MODE="${1:-}"; shift || true
PORT=6042
RATE=""
IFACE=""
# Unlimited class “ceil” 给个很大值，基本等于不限制
CEIL="10000mbit"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --port)  PORT="$2"; shift 2;;
    --rate)  RATE="$2"; shift 2;;
    --iface) IFACE="$2"; shift 2;;
    -h|--help)
      echo "Usage: sudo $0 <apply|status|clear> [--port 6042] --rate 30mbit [--iface ens5]"
      exit 0;;
    *) echo "Unknown arg: $1" >&2; exit 1;;
  esac
done

auto_iface() {
  ip route get 1.1.1.1 2>/dev/null | awk '/dev/ {for(i=1;i<=NF;i++){if($i=="dev"){print $(i+1); exit}}}'
}

ensure_ifb() {
  modprobe -q ifb || true
  ip link show ifb0 >/dev/null 2>&1 || ip link add ifb0 type ifb
  ip link set ifb0 up
}

has_flower() {
  tc filter add dev lo ingress pref 999 protocol ip flower skip_hw >/dev/null 2>&1 && \
  tc filter del dev lo ingress pref 999 >/dev/null 2>&1
}

apply_limit() {
  [[ -n "$RATE" ]] || { echo "apply 需要 --rate，例如 --rate 30mbit"; exit 2; }
  [[ -n "$IFACE" ]] || IFACE="$(auto_iface)"
  [[ -n "$IFACE" ]] || { echo "无法自动检测网卡，请用 --iface 指定"; exit 2; }

  ensure_ifb

  # 1) 在真实网卡上挂 ingress，并把所有 ingress 重定向到 ifb0
  tc qdisc show dev "$IFACE" | grep -q "ingress" || tc qdisc add dev "$IFACE" ingress
  # 先清掉我们可能加过的 redirect（保持其它用户规则不动：只删我们的 pref）
  for p in 90; do tc filter del dev "$IFACE" ingress pref $p 2>/dev/null || true; done

  if has_flower; then
    # 用 flower 的 matchall；不依赖 flower 也行，下面有 u32 方案
    tc filter add dev "$IFACE" ingress pref 90 protocol all flower \
      action mirred egress redirect dev ifb0
  else
    # 没有 flower 就用 u32 的“任意匹配”
    tc filter add dev "$IFACE" parent ffff: protocol ip u32 match u32 0 0 \
      action mirred egress redirect dev ifb0
    #（若有 IPv6 但无 flower，上面这条不覆盖 IPv6；大多数 EC2 环境只走 IPv4）
  fi

  # 2) 在 ifb0 上建立 HTB：1:1 限速类（给端口 6042），1:2 “近似无限制”类（默认所有其它流量）
  tc qdisc replace dev ifb0 root handle 1: htb default 2
  tc class replace dev ifb0 parent 1: classid 1:1 htb rate "$RATE" ceil "$RATE"
  tc class replace dev ifb0 parent 1: classid 1:2 htb rate "$CEIL" ceil "$CEIL"

  # 3) 过滤：把“目的端口=PORT”的（下载方向）分到 1:1，其余走 1:2
  # IPv4 TCP/UDP（无需偏移，直接用 u32 helpers）
  tc filter replace dev ifb0 parent 1: protocol ip prio 10 u32 \
    match ip dport "$PORT" 0xffff flowid 1:1
  # 兜底：其它 IPv4 全到 1:2（可选）
  tc filter replace dev ifb0 parent 1: protocol ip prio 20 u32 \
    match u32 0 0 flowid 1:2

  # 可选：如内核支持 flower，就顺手把 IPv6 的 6042 也分到 1:1
  if has_flower; then
    tc filter replace dev ifb0 parent 1: protocol ipv6 prio 11 flower \
      ip_proto tcp dst_port "$PORT" flowid 1:1
    tc filter replace dev ifb0 parent 1: protocol ipv6 prio 12 flower \
      ip_proto udp dst_port "$PORT" flowid 1:1
    tc filter replace dev ifb0 parent 1: protocol ipv6 prio 21 flower \
      flowid 1:2
  fi

  echo "[OK] IFACE=$IFACE 仅对 dst port=$PORT 的下载限速 rate=$RATE，其他端口不受限"
}

status_show() {
  [[ -n "$IFACE" ]] || IFACE="$(auto_iface)"
  echo "=== IFACE: $IFACE ==="
  echo "--- qdisc on $IFACE ---"
  tc -s qdisc show dev "$IFACE" || true
  echo "--- filters on $IFACE (ingress) ---"
  tc -s filter show dev "$IFACE" ingress || true
  echo "--- qdisc on ifb0 ---"
  tc -s qdisc show dev ifb0 || true
  echo "--- filters on ifb0 (HTB) ---"
  tc -s filter show dev ifb0 parent 1: || true
  echo "--- classes on ifb0 (HTB) ---"
  tc -s class show dev ifb0 || true
}

clear_limit() {
  [[ -n "$IFACE" ]] || IFACE="$(auto_iface)"

  # 删我们用的 pref=90 的 redirect
  tc filter del dev "$IFACE" ingress pref 90 2>/dev/null || true
  # ifb0 上的 HTB 整体移除
  tc qdisc del dev ifb0 root 2>/dev/null || true

  # 如果 $IFACE 上没有其它 ingress 规则，可以顺带把 ingress qdisc 也删掉（可选）
  if ! tc filter show dev "$IFACE" ingress 2>/dev/null | grep -q 'filter'; then
    tc qdisc del dev "$IFACE" ingress 2>/dev/null || true
  fi

  echo "[OK] 已清除端口限速（IFACE=$IFACE）"
}

case "${MODE}" in
  apply)  apply_limit ;;
  status) status_show ;;
  clear)  clear_limit ;;
  *) echo "Usage: sudo $0 <apply|status|clear> [--port 6042] --rate 30mbit [--iface ens5]"; exit 1;;
esac

#execute: sudo ./limit_AWS_bandwidth.sh apply --port 6042 --rate 60mbit