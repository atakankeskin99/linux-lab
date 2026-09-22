# Benchmark Results

This file preserves the raw measurements used by the main README.

## Environment

| Field | Value |
|---|---|
| Host OS | Linux Mint 22.3 “Zena” |
| Architecture | x86_64 / amd64 |
| Host kernel | 7.0.0-31-generic |
| Docker Engine | 29.8.1 |
| Runtime | Python 3.13 |
| Application | Flask HTTP service |

## Bare base-image baseline

| Metric | Alpine | Debian bookworm-slim |
|---|---:|---:|
| Root filesystem | 8.7 MB | 82 MB |
| Docker disk usage | 13 MB | 116 MB |
| Content size | 3.94 MB | 30.6 MB |

## Final application images

| Metric | Alpine | Debian Slim |
|---|---:|---:|
| Docker disk usage | 90.5 MB | 197 MB |
| Content size | 22 MB | 48.1 MB |
| Container filesystem | 64.5 MB | 138 MB |
| Idle memory | 24.24 MiB | 22.05 MiB |

## Build-time samples

Method: warm base images already local, application build forced with `--no-cache`.

| Run | Alpine | Debian Slim |
|---:|---:|---:|
| 1 | 38.54 s | 30.21 s |
| 2 | 31.73 s | 31.21 s |
| 3 | 31.22 s | 28.36 s |
| **Average** | **33.83 s** | **29.93 s** |

## Docker lifecycle diagnostic

Command shape:

```bash
/usr/bin/time -f 'docker run elapsed: %e s' \
  sudo docker run --rm system-probe:alpine \
  python -c 'print("ready")'
```

Alpine samples:

```text
3.84 s
3.85 s
4.05 s
```

Average: **3.91 s**

This test includes create/start/process/exit/cleanup and was used to show that `docker run` lifecycle overhead was contaminating the first startup benchmark design.

## Start-to-ready

Definition:

```text
pre-created stopped container
    -> docker start
    -> poll /health every 10 ms
    -> first HTTP 200
```

### Exploratory Alpine sample

```text
1730 ms
```

It is valid but not included in the matched five-run comparison below.

### Matched five-run series

| Run | Alpine | Debian Slim |
|---:|---:|---:|
| 1 | 2169 ms | 3632 ms |
| 2 | 1583 ms | 1488 ms |
| 3 | 1612 ms | 1480 ms |
| 4 | 1605 ms | 1471 ms |
| 5 | 1666 ms | 1475 ms |

### Summary

| Statistic | Alpine | Debian Slim |
|---|---:|---:|
| Average | 1727 ms | 1909 ms |
| Median | 1612 ms | 1480 ms |
| Minimum | 1583 ms | 1471 ms |
| Maximum | 2169 ms | 3632 ms |
| Runs 2–5 average | 1616.5 ms | 1478.5 ms |

Debian Slim's runs 2–5 average was **8.5% shorter** than Alpine's in this local test.

## Runtime ecosystem

| Property | Alpine | Debian Slim |
|---|---|---|
| libc | musl 1.2.6 | glibc 2.41 |
| Core userspace | BusyBox | GNU/coreutils-style userspace |
| Package manager | apk | apt / dpkg |
| Package entries | 29 | 87 |

## Interpretation

The strongest Alpine advantage measured here is **storage footprint**.

The experiment does not show an Alpine advantage in idle RAM, build time, or repeated application readiness. Those results are workload- and host-specific and should not be generalized beyond this lab.
