#!/usr/bin/env python3
"""Generate structured GitHub Release notes for Google Antigravity IDE."""

import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES_FILE = ROOT / "pkgs" / "antigravity-ide" / "sources.json"


def main():
    tag = sys.argv[1] if len(sys.argv) > 1 else ""
    if not SOURCES_FILE.exists():
        sys.exit(f"Error: {SOURCES_FILE} not found")

    sources = json.loads(SOURCES_FILE.read_text())
    version = sources.get("version", "unknown")
    build = sources.get("build", "unknown")
    platforms = sources.get("platforms", {})
    linux_hash = platforms.get("x86_64-linux", {}).get("hash", "unknown")
    linux_url = platforms.get("x86_64-linux", {}).get("url", "")

    if not tag:
        tag = f"v{version}"

    # Determine title
    rev_match = re.search(r"-([0-9]+)$", tag)
    if rev_match:
        title = f"Google Antigravity IDE v{version} (Packaging Revision {rev_match.group(1)})"
    else:
        title = f"Google Antigravity IDE v{version} (NixOS Release)"

    body = f"""### Google Antigravity IDE `{version}` (Build `{build}`)

Automated release tracking official Google Antigravity IDE binaries for NixOS and Linux/macOS systems.

#### Upstream Artifact Details

| Property | Value |
| :--- | :--- |
| **Application** | Google Antigravity IDE |
| **Upstream Version** | `{version}` |
| **Build Identifier** | `{build}` |
| **Upstream Source** | [Official Google Download Portal](https://antigravity.google/download) |
| **Edge Delivery URL** | [`{linux_url}`]({linux_url}) |
| **x86_64-linux SRI** | `{linux_hash}` |

#### Automated CI Verification

- **Flake Evaluation**: Evaluated across architectures (`nix flake check`)
- **Package Build**: Compiled inside isolated sandbox (`nix build .#default`)
- **Runtime Smoke Test**: Verified headless graphical startup with virtual framebuffer (`xvfb-run`)

#### Installation & Pinning

##### Immediate Run
```bash
nix run github:B-Shinchan/antigravity-ide-nixos/{tag}
```

##### Flake Input (`flake.nix`)
Pin this specific release in your system flake:
```nix
inputs.antigravity-ide.url = "github:B-Shinchan/antigravity-ide-nixos/{tag}";
```

##### Home Manager (`home.nix`)
```nix
home.packages = [
  inputs.antigravity-ide.packages.${{pkgs.stdenv.hostPlatform.system}}.default
];
```

---
> [!NOTE]
> **Independent Packaging**: This repository provides independent Nix expressions for packaging official Google vendor binaries. It is not affiliated with, sponsored by, or endorsed by Google LLC.
"""

    if output := os.environ.get("GITHUB_OUTPUT"):
        with open(output, "a") as f:
            f.write(f"title={title}\n")

    print(body.strip())


if __name__ == "__main__":
    main()
