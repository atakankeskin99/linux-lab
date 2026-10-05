# Self-Hosted RSS
![FreshRSS](https://img.shields.io/badge/FreshRSS-00847F?style=flat-square&logo=rss&logoColor=white)
![Docker Compose](https://img.shields.io/badge/Docker_Compose-2496ED?style=flat-square&logo=docker&logoColor=white)
![Linux Mint](https://img.shields.io/badge/Linux_Mint-87CF3E?style=flat-square&logo=linuxmint&logoColor=white)
![Self-Hosted](https://img.shields.io/badge/Self--Hosted-555555?style=flat-square&logo=serverfault&logoColor=white)

# Self-Hosted RSS

A small self-hosted RSS reader built with FreshRSS and Docker Compose on a Linux Mint laptop.

The goal was not simply to replace a hosted RSS reader. This project was used to explore container deployment, persistent Docker storage, LAN access, RSS migration, and FreshRSS's feed-refresh mechanism on a real Linux host.

## Goal

The initial goal was to move an existing collection of RSS subscriptions from Feedly to a locally hosted service.

The deployment should:

- run on the existing Linux Mint host;
- be accessible from another machine on the local network;
- preserve subscriptions and application state across container recreation;
- support migration from Feedly through OPML;
- remain simple enough for an on-demand host that is not powered on 24/7.

FreshRSS was selected as the RSS application and Docker Compose was used to manage the deployment.

## Environment

| Component | Role |
| --- | --- |
| ASUS X550CA | FreshRSS host |
| Linux Mint XFCE | Host operating system |
| Docker Engine | Container runtime |
| Docker Compose | Deployment management |
| FreshRSS | RSS reader |
| Windows workstation | Browser and SSH administration client |
| Feedly | Source of the existing RSS subscription collection |

The Linux host is administered remotely over SSH.

## Architecture

```text
Windows workstation
        |
        | HTTP over LAN
        v
Linux Mint host :8080
        |
        | Docker port mapping
        v
FreshRSS container :80
        |
        +---- FreshRSS data
        |        |
        |        v
        |   Docker named volume
        |
        +---- Extensions
                 |
                 v
            Docker named volume
```

The service is intentionally LAN-oriented in its current form. No public Internet exposure or reverse proxy was added.

## Docker Permission Troubleshooting

Before deploying FreshRSS, the Docker installation was checked:

```bash
docker --version
docker compose version
docker info --format '{{.ServerVersion}}'
```

The Docker CLI and Compose plugin were installed, but `docker info` failed with:

```text
permission denied while trying to connect to the docker API at unix:///var/run/docker.sock
```

The Docker socket permissions were inspected:

```bash
ls -l /var/run/docker.sock
```

The socket belonged to:

```text
root docker
```

The current user's supplementary groups were then checked:

```bash
groups
```

The user was not a member of the `docker` group.

The user was added with:

```bash
sudo usermod -aG docker <username>
```

After reconnecting the SSH session, `docker info` succeeded.

### Security note

Membership in the `docker` group provides highly privileged access to the host through the Docker daemon. It should not be treated as an ordinary low-privilege group membership, especially on multi-user systems.

## Deployment

The Compose configuration is stored in [`compose.yaml`](compose.yaml).

The service can be started with:

```bash
docker compose up -d
```

The `-d` flag starts the containers in detached mode.

Status can be checked with:

```bash
docker compose ps
```

The observed port mapping was:

```text
0.0.0.0:8080->80/tcp
```

This exposes the container's HTTP port `80` through port `8080` on the Linux host.

## HTTP Verification

Container status alone does not prove that the application is responding.

FreshRSS was therefore tested from the host:

```bash
curl -I http://localhost:8080
```

FreshRSS returned an HTTP redirect to its installer:

```text
HTTP/1.1 302 Found
Location: /i/...
```

The same request was then made from the Windows workstation against the Linux host's LAN address:

```text
curl.exe -I http://<host-lan-ip>:8080
```

This also returned a valid FreshRSS HTTP response.

This separated application availability from browser-specific behavior and verified the path:

```text
Windows
   |
   v
Linux host :8080
   |
   v
Docker port mapping
   |
   v
FreshRSS :80
```

## FreshRSS Installation Checks

The FreshRSS installer reported successful checks for:

- compatible PHP;
- PDO database support;
- cURL;
- JSON;
- PCRE;
- ctype;
- DOM and XML;
- mbstring;
- internationalisation support;
- fileinfo;
- ZIP support;
- data-directory permissions;
- cache-directory permissions;
- temporary-directory permissions;
- user-directory permissions;
- favicon-directory permissions;
- web-server document root.

The installation then completed successfully and the FreshRSS interface became accessible from the Windows workstation.

## Persistent Storage

Two Docker named volumes are used:

```yaml
volumes:
  - freshrss_data:/var/www/FreshRSS/data
  - freshrss_extensions:/var/www/FreshRSS/extensions
```

The important distinction is:

```text
Container lifecycle != application data lifecycle
```

To verify this rather than assuming it from the Compose configuration, a persistence test was performed.

A FreshRSS article was marked as a favourite and the deployment was removed:

```bash
docker compose down
```

The named volumes remained present.

FreshRSS was then recreated:

```bash
docker compose up -d
```

After reopening the application:

- the user account remained available;
- subscriptions remained available;
- previously fetched articles remained available;
- the article marked as a favourite was still marked.

This confirmed that application state survived container removal and recreation.

> `docker compose down -v` is intentionally avoided during normal operation because `-v` also removes the Compose-managed named volumes.

## Feedly Migration

The existing RSS subscriptions were exported from Feedly as an OPML file.

An SCP transfer to the Linux host was also tested:

```bash
scp <feedly-export.opml> <user>@<host>:/path/to/rss-service/
```

The transferred file was successfully verified on the Linux filesystem.

However, this transfer was not required for FreshRSS itself. The FreshRSS web interface accepts the OPML file directly from the browser, so the server-side copy was removed after the SCP exercise.

The actual migration path was:

```text
Feedly
   |
   | OPML export
   v
Windows workstation
   |
   | browser upload
   v
FreshRSS
```

After import, FreshRSS preserved the subscription structure and populated feeds from categories including software engineering, security, cloud, and systems infrastructure.

Articles from imported feeds were successfully retrieved and displayed in the main stream.

## Automatic Refresh Investigation

After confirming that feeds could be fetched, the next question was whether FreshRSS would automatically refresh them while the service was running.

Processes inside the container were inspected:

```bash
docker exec freshrss ps aux
```

Apache processes were present, but no obvious cron daemon was running.

The container environment was then inspected:

```bash
docker exec freshrss env | grep -Ei 'cron|refresh|freshrss'
```

The relevant result was:

```text
CRON_MIN=
```

The FreshRSS files inside the container were searched for references to this variable:

```bash
docker exec freshrss grep -R "CRON_MIN" \
  /var/www/FreshRSS /entrypoint.sh /usr/local/bin 2>/dev/null
```

The bundled Docker documentation explained that `CRON_MIN` controls the built-in cron job used for automatic feed refresh and that an empty value disables the cron daemon.

Therefore the observed state was:

```text
CRON_MIN empty
      |
      v
built-in cron disabled
```

### Design decision

Automatic polling was deliberately left disabled.

The Linux laptop hosting FreshRSS is not intended to operate continuously. It may be powered off for significant periods, so maintaining a fixed background polling interval provides little benefit for the current use case.

FreshRSS is instead treated as an on-demand local service:

```text
Host powered on
      |
      v
FreshRSS available
      |
      v
Refresh feeds when needed
      |
      v
Read articles
```

This keeps the deployment simple and matches the actual operating model of the hardware.

A limitation of this approach is that a feed could theoretically drop older entries before FreshRSS polls it if the host remains offline for a sufficiently long period.

## Operations Cheat Sheet

### Check service status

```bash
cd ~/rss-service
docker compose ps
```

If FreshRSS reports `Up`, no additional start command is required.

### Start or create the service

```bash
docker compose up -d
```

### Stop the existing container

```bash
docker compose stop
```

### Start a stopped container

```bash
docker compose start
```

### Recreate the deployment

```bash
docker compose down
docker compose up -d
```

The named volumes remain intact unless volume removal is explicitly requested.

### View recent logs

```bash
docker compose logs --tail=50 freshrss
```

### Test HTTP locally

```bash
curl -I http://localhost:8080
```

### Open from another LAN machine

```text
http://<host-lan-ip>:8080
```

## Validation Summary

The following behaviors were demonstrated during the setup:

| Test | Result |
| --- | --- |
| Docker daemon access | Passed after group-permission fix |
| FreshRSS container startup | Passed |
| Host HTTP response | Passed |
| HTTP access from Windows over LAN | Passed |
| FreshRSS installer checks | Passed |
| Feed retrieval | Passed |
| OPML subscription import | Passed |
| Category migration | Passed |
| Container recreation | Passed |
| Persistent application state | Passed |
| Favourite persistence | Passed |
| Built-in automatic cron | Confirmed disabled |
| Reboot auto-start | Not yet tested |

The distinction between **tested behavior** and **expected behavior** is intentional. The Compose policy uses `restart: unless-stopped`, but automatic startup after a full host reboot has not yet been validated.

## Security and Scope

The current deployment is intended for a trusted local network.

Important boundaries:

- FreshRSS is currently served over plain HTTP.
- Port `8080` is published on the host's network interfaces.
- No reverse proxy or TLS termination has been configured.
- No public Internet exposure was intentionally configured.
- Docker group membership gives the administrative user highly privileged access to the host.

These trade-offs are acceptable for the current lab use case but would need to be reconsidered before exposing the service to an untrusted network.

## Possible Next Steps

Potential follow-up experiments include:

- validate FreshRSS startup after a full host reboot;
- test access over Tailscale without exposing the service publicly;
- create and restore a backup of the FreshRSS data volume;
- replace the floating `latest` image tag with an explicitly pinned version;
- investigate TLS or a reverse proxy if the access model changes;
- measure resource consumption while FreshRSS is idle and during feed refresh.

## Result

A working self-hosted RSS reader was deployed on the existing Linux Mint laptop.

The project demonstrated more than application installation: it covered Docker socket permissions, container networking, HTTP verification, persistent volumes, OPML migration, container lifecycle behavior, and investigation of FreshRSS's built-in scheduling mechanism.

The final design intentionally favors a small, on-demand service over a continuously running RSS server.