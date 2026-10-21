"""Probe SNDlib archived 15-minute measured/scaled GÉANT traffic matrices.

Official source: https://sndlib.put.poznan.pl/geant.overview.action
Provenance: https://sndlib.put.poznan.pl/download/geant-rm.txt
No private or unscaled original traffic is requested or reconstructed.
This is a data-quality pilot, not yet an optimization benchmark.
"""
import hashlib
import io
import math
import re
import statistics
import tarfile
import urllib.request

from research.geant_capacity import extract_section

ARCHIVE = ("https://sndlib.put.poznan.pl/download/"
           "directed-geant-uhlig-15min-over-4months-ALL-native.tgz")
TIMESTAMPS = ["20050505-1200", "20050615-1200",
              "20050720-1200", "20050815-1200"]


def parse_demand_matrix(text):
    demands = []
    for line in extract_section(text, "DEMANDS"):
        m = re.fullmatch(
            r"\S+\s+\(\s*(\S+)\s+(\S+)\s*\)\s+"
            r"[\d.]+\s+([\d.]+)\s+\S+", line)
        if m is None:
            raise ValueError("Unrecognized dynamic demand row: " + line)
        src, dst, value = m.groups()
        amount = float(value)
        if not math.isfinite(amount) or amount < 0:
            raise ValueError("Invalid traffic value in published matrix")
        demands.append((src, dst, amount))
    return demands


def main():
    request = urllib.request.Request(
        ARCHIVE, headers={"User-Agent": "GAdapt-research/1.0"})
    with urllib.request.urlopen(request, timeout=120) as response:
        archive = response.read()
    print("ARCHIVE_SHA256", hashlib.sha256(archive).hexdigest(),
          "BYTES", len(archive), flush=True)
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:gz") as handle:
        members = [m for m in handle.getmembers() if m.isfile()]
        print("MEMBERS", len(members),
              "EXAMPLE", [x.name for x in members[:3]], flush=True)
        for stamp in TIMESTAMPS:
            candidates = [m for m in members if stamp in m.name]
            if len(candidates) != 1:
                raise ValueError(f"Ambiguous/missing time {stamp}: {len(candidates)}")
            member = candidates[0]
            if member.size > 1000000:
                raise ValueError("Unexpectedly large traffic snapshot")
            with handle.extractfile(member) as f:
                content = f.read().decode("utf-8-sig")
            demands = parse_demand_matrix(content)
            volume = sum(x[2] for x in demands)
            print("SNAPSHOT", stamp, "demand_count", len(demands),
                  "total_mbps", round(volume, 5),
                  "peak_demand_mbps", max(x[2] for x in demands) if demands else 0,
                  "file_sha256", hashlib.sha256(content.encode()).hexdigest(),
                  flush=True)
            if len(demands) < 100 or volume <= 0 or volume > 1e7:
                raise ValueError("Empty/implausible measured traffic snapshot: " + stamp)


if __name__ == "__main__":
    main()
