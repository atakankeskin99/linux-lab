# sysinfo-lite

![Learning Focused](https://img.shields.io/badge/status-learning--focused-blue)
![Bash](https://img.shields.io/badge/built%20with-bash-1f425f.svg)
![CLI Tool](https://img.shields.io/badge/type-CLI-lightgrey)
![Linux](https://img.shields.io/badge/platform-Linux-success)

A minimal Bash-based CLI tool that displays essential Linux system information.

This project was created right after installing Linux Mint XFCE on my old ASUS X550CA.  
Instead of consuming tutorials, I decided to start building small terminal-based tools to understand Linux practically.

This is a learning-focused project.

---

## 📁 Context

- Device: ASUS X550CA  
- OS: Linux Mint XFCE  
- Kernel: Linux 6.x  
- Shell: Bash  

The goal was to build something small but real, directly in the terminal environment I set up.

---

## 💡 Features

- User information  
- Hostname  
- Kernel version  
- Architecture  
- CPU model  
- Memory usage  
- Disk usage  

All implemented using pure Bash and standard Linux utilities.

---

## 🛠️ Tech Stack

- Bash  
- Core Linux utilities (`uname`, `lscpu`, `free`, `df`)  

No external dependencies.

---

## Usage

From the project directory:

```bash
chmod +x sysinfo.sh
./sysinfo.sh
```
If installed globally:

```bash
sysinfo
```





---

# 📚 Case Study

## 🎯 Objective

After installing Linux Mint XFCE on my old ASUS X550CA laptop,  
I wanted to move beyond just using Linux and actually build something inside it.

Instead of following tutorials passively,  
I decided to create a small but functional CLI tool to:

- Understand how system information is retrieved
- Practice Bash scripting
- Learn how executables work in Linux
- Understand the `$PATH` mechanism
- Turn a local script into a globally accessible command

---

## 🛠 Process

1. Installed Linux Mint XFCE  
2. Configured development environment (Git, VS Code, terminal tools)  
3. Created a Bash script (`sysinfo.sh`)  
4. Extracted system data using:
   - `uname`
   - `whoami`
   - `hostname`
   - `lscpu`
   - `free`
   - `df`
5. Formatted output cleanly using pipes and `sed`
6. Made the script executable:

   ```bash
   chmod +x sysinfo.sh
   ```

7. Copied it to `/usr/local/bin`:

   ```bash
   sudo cp sysinfo.sh /usr/local/bin/sysinfo
   ```

8. Made it globally executable:

   ```bash
   sudo chmod +x /usr/local/bin/sysinfo
   ```

9. Converted it into a real CLI command:

   ```bash
   sysinfo
   ```

---

## 🧠 What I Learned

- How Linux permissions work (`chmod`)
- How `$PATH` determines executable availability
- Difference between local execution (`./script.sh`) and global commands
- Basic shell piping and text processing
- Structuring a minimal but functional CLI project
- Git workflow (init → add → commit → branch → push)
- Using Personal Access Tokens for GitHub authentication

---

## 🚀 Result

What started as:

> “I just installed Linux.”

Became:

> “I built and deployed my own CLI tool inside a freshly installed Linux environment.”

This is a learning-focused project,  
but it represents the beginning of building tools instead of only using them.








