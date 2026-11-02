#!/bin/sh
# PC Anti-Hacker Lock

iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT ACCEPT
iptables -A INPUT -i lo -j ACCEPT
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
iptables -A INPUT -p tcp --dport 22 -j ACCEPT

systemctl disable bluetooth cups avahi-daemon 2>/dev/null
systemctl stop bluetooth cups avahi-daemon 2>/dev/null

chmod 700 /root