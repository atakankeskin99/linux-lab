#!/usr/bin/env bash


echo "===== SYSINFO-LITE ====="
echo

echo "User: $(whoami)"
echo "Hostname: $(hostname)"
echo "Kernel: $(uname -r)"
echo "Architecture: $(uname -m)"
echo

echo "---- CPU ----"
lscpu | grep "Model name" | sed 's/Model name:[[:space:]]*//'
echo

echo "---- Memory ----"
free -h
echo

echo "---- Disk ----"
df -h /
echo

echo "========================"
