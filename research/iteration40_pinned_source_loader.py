"""I40 replay loader for EXACT previously audited historical SNDlib bytes.

SECURITY: try authenticated TLS first. ONLY on a hostname-certificate
verification failure, optionally allow a *second* connection with unverifiable
TLS transport for the TWO PREDECLARED immutable byte streams, and reject those
bytes BEFORE parsing unless independently preregistered SHA256 matches exactly.
This is NOT a general TLS bypass or a replacement for proper server identity.
If replay fallback is not explicitly enabled, raise the original TLS failure.
"""
import hashlib
import io
import os
import re
import ssl
import tarfile
import urllib.error
import urllib.request

import numpy as np

from research.iteration38_joint_capacity_model import (
    SOURCE_NETWORK_URL, parse_nodes, parse_network, parse_demands, temporal_array,
)
from research.iteration39_source_modular_capacity import NETWORK_SHA, ARCHIVE_SHA

ARCHIVE_URL=("https://sndlib.put.poznan.pl/download/"
             "directed-nobel-germany-DFN-aggregated-5min-over-1day-native.tgz")

def _verified_download(url, exact_digest, byte_limit):
    if url not in (SOURCE_NETWORK_URL, ARCHIVE_URL):
        raise ValueError("Only two preregistered exact original files are permitted")
    request=urllib.request.Request(url,headers={"User-Agent":"GAdapt-I40-source-audit/1.0"})
    def read(context):
        with urllib.request.urlopen(request,timeout=45,context=context) as stream:
            if stream.geturl()!=url:
                raise RuntimeError("Unexpected redirect of fixed source URL")
            data=stream.read(byte_limit+1)
        if len(data)>byte_limit:
            raise ValueError("Historical source exceeds frozen size cap")
        return data
    insecure_fallback=False
    try:
        data=read(ssl.create_default_context())
    except urllib.error.URLError as exc:
        if (os.environ.get("I40_PINNED_TLS_REPLAY")!="1" or
                not isinstance(exc.reason,ssl.SSLCertVerificationError)):
            raise
        print("I40_TRANSPORT_WARNING",
              "Original SNDlib HTTPS certificate invalid; using replay ONLY with pinned SHA256; do not use as general TLS trust",
              flush=True)
        insecure_fallback=True
        data=read(ssl._create_unverified_context())
    got=hashlib.sha256(data).hexdigest()
    if got!=exact_digest:
        raise RuntimeError("Source SHA256 pinned replay mismatch; no untrusted bytes may be parsed")
    return data,dict(url=url,sha256=got,bytes=len(data),
                     verified_tls=not insecure_fallback,
                     authenticated_content_by_prior_SHA256_pin=True)

def source_data_gate_i40():
    network,network_meta=_verified_download(SOURCE_NETWORK_URL,NETWORK_SHA,60_000)
    archive,archive_meta=_verified_download(ARCHIVE_URL,ARCHIVE_SHA,1_200_000)
    nodes,links=parse_network(network.decode("utf-8-sig"))
    if len(nodes)!=17 or len(links)!=26 or len(parse_demands(network.decode("utf-8-sig"),nodes))!=121:
        raise RuntimeError("Historical source topology or native demand drift")
    frames=[]
    with tarfile.open(fileobj=io.BytesIO(archive),mode="r:gz") as ar:
        entries=[m for m in ar.getmembers() if m.isfile()]
        if len(entries)>340:
            raise ValueError("Unexpected number of tar entries")
        for item in entries:
            if not 0<=item.size<2_000_000:
                raise ValueError("Unbounded archive member size")
            name=item.name
            raw=ar.extractfile(item).read()
            text=raw.decode("utf-8-sig")
            if re.search(r"(?m)^\s*DEMANDS\s*\(",text):
                frames.append((name,text))
    frames.sort(key=lambda v:v[0])
    if len(frames)!=288 or len({v[0] for v in frames})!=288:
        raise RuntimeError("Pinned archive must yield exactly 288 unique native frames")
    pairs,q=temporal_array(frames,nodes)
    if q.shape!=(288,272) or not np.all(np.isfinite(q)) or np.any(q<0):
        raise RuntimeError("Pinned original temporal 288x272 geometry changed")
    meta=dict(source_network=network_meta,source_matrices=dict(
        **archive_meta, matrix_count=288,first_name=frames[0][0],
        last_name=frames[-1][0]),
        matrix_names=[f[0] for f in frames],
        historical_replay_transport_warning="If verified_tls=false, SHA pin only, source server TLS name not authenticated",
        fit_indices=[0,127],calibration_indices=[128,191],test_indices=[192,287])
    return nodes,links,pairs,q,meta
