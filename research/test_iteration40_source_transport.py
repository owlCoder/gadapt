"""I40 source historical authenticity tests, NO network or source-data access."""
import hashlib
import os
import tempfile
from pathlib import Path
import ssl
import unittest
import urllib.error
from unittest.mock import patch

from research.iteration40_pinned_source_loader import (
    _verified_download, _pinned_asset_file, ARCHIVE_URL, SOURCE_NETWORK_URL)


class DummyResponse:
    def __init__(self,payload,url):
        self.payload,self.url=payload,url
    def __enter__(self):return self
    def __exit__(self,*args):return False
    def geturl(self):return self.url
    def read(self,n):return self.payload[:n]


class I40OriginalSHA256AuthenticityTests(unittest.TestCase):
    def test_authenticated_source_download_must_match_sha_before_parse(self):
        raw=b"toy text NOT ORIGINAL SNDlib"
        digest=hashlib.sha256(raw).hexdigest()
        with patch("urllib.request.urlopen",return_value=DummyResponse(raw,SOURCE_NETWORK_URL)):
            found,meta=_verified_download(SOURCE_NETWORK_URL,digest,128)
        self.assertEqual(found,raw)
        self.assertTrue(meta["verified_tls"])
        self.assertTrue(meta["authenticated_content_by_prior_SHA256_pin"])
        with patch("urllib.request.urlopen",return_value=DummyResponse(raw,SOURCE_NETWORK_URL)):
            with self.assertRaisesRegex(RuntimeError,"SHA256"):
                _verified_download(SOURCE_NETWORK_URL,"0"*64,128)

    def test_certificate_failure_without_explicit_replay_fail_closed(self):
        err=urllib.error.URLError(ssl.SSLCertVerificationError(
            "certificate does not cover official source hostname"))
        with patch.dict(os.environ,{"I40_PINNED_TLS_REPLAY":"0"}):
            with patch("urllib.request.urlopen",side_effect=err):
                with self.assertRaises(urllib.error.URLError):
                    _verified_download(ARCHIVE_URL,hashlib.sha256(b"").hexdigest(),128)

    def test_explicit_replay_ONLY_exact_pinned_content_even_on_bad_cert(self):
        raw=b"synthetic replay content"
        digest=hashlib.sha256(raw).hexdigest()
        bad=urllib.error.URLError(ssl.SSLCertVerificationError("hostname mismatch"))
        side=[bad,DummyResponse(raw,ARCHIVE_URL)]
        with patch.dict(os.environ,{"I40_PINNED_TLS_REPLAY":"1"}):
            with patch("urllib.request.urlopen",side_effect=side) as mock:
                found,meta=_verified_download(ARCHIVE_URL,digest,128)
        self.assertEqual(mock.call_count,2)
        self.assertEqual(found,raw)
        self.assertFalse(meta["verified_tls"])
        with patch.dict(os.environ,{"I40_PINNED_TLS_REPLAY":"1"}):
            with patch("urllib.request.urlopen",side_effect=[
                bad,DummyResponse(raw,ARCHIVE_URL)]):
                with self.assertRaisesRegex(RuntimeError,"SHA256"):
                    _verified_download(ARCHIVE_URL,"f"*64,128)

    def test_404_even_after_explicit_replay_never_fabricates_dataset(self):
        bad=urllib.error.URLError(ssl.SSLCertVerificationError("hostname mismatch"))
        with patch.dict(os.environ,{"I40_PINNED_TLS_REPLAY":"1"}):
            with patch("urllib.request.urlopen",side_effect=[
                bad,urllib.error.HTTPError(ARCHIVE_URL,404,"Not Found",None,None)]):
                with self.assertRaises(urllib.error.HTTPError):
                    _verified_download(ARCHIVE_URL,"a"*64,128)

    def test_never_fetch_unregistered_url_or_redirect(self):
        with self.assertRaises(ValueError):
            _verified_download("https://example.com/dataset.tgz","a"*64,1000)
        with patch("urllib.request.urlopen",return_value=DummyResponse(
                b"x","https://thirdparty.example.org")):
            with self.assertRaisesRegex(RuntimeError,"redirect"):
                _verified_download(ARCHIVE_URL,hashlib.sha256(b"x").hexdigest(),100)

    def test_offline_raw_original_accepts_only_identical_sha256_bytes(self):
        # Explicitly SYNTHETIC tiny bytes; no original SNDlib data stored.
        payload=b"synthetic offline SNDlib fixture - not DFN"
        digest=hashlib.sha256(payload).hexdigest()
        with tempfile.TemporaryDirectory() as directory:
            file=Path(directory)/"nobel-germany.txt"
            file.write_bytes(payload)
            with patch("urllib.request.urlopen",side_effect=AssertionError(
                    "Offline verified loader must never use the network")):
                out,meta=_pinned_asset_file(
                    directory,"nobel-germany.txt",SOURCE_NETWORK_URL,digest,200)
            self.assertEqual(out,payload)
            self.assertIsNone(meta["verified_tls"])
            self.assertEqual(meta["source_transport"],
                             "offline_original_bytes_pin_verified")
            with self.assertRaisesRegex(RuntimeError,"SHA256"):
                _pinned_asset_file(directory,"nobel-germany.txt",
                                   SOURCE_NETWORK_URL,"e"*64,200)
            file.unlink()
            with self.assertRaises(FileNotFoundError):
                _pinned_asset_file(directory,"nobel-germany.txt",
                                   SOURCE_NETWORK_URL,digest,200)

    def test_offline_rejects_path_traversal_and_symlink_escape(self):
        payload=b"test fixture only"
        digest=hashlib.sha256(payload).hexdigest()
        with tempfile.TemporaryDirectory() as directory:
            with tempfile.TemporaryDirectory() as outside:
                external=Path(outside)/"outside.txt"
                external.write_bytes(payload)
                (Path(directory)/"nobel-germany.txt").symlink_to(external)
                with self.assertRaises(ValueError):
                    _pinned_asset_file(directory,"nobel-germany.txt",
                                       SOURCE_NETWORK_URL,digest,200)
            with self.assertRaises(FileNotFoundError):
                _pinned_asset_file(directory,"absent.txt",
                                   SOURCE_NETWORK_URL,digest,200)


if __name__=="__main__":
    unittest.main()
