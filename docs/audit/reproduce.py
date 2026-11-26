"""Harmless local reproductions: fake data, no network or real secrets."""
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
from unittest.mock import patch

APP = Path(__file__).resolve().parents[2] / 'srcs/requirements/app'
sys.path.insert(0, str(APP))
from cti_core.scraper import Scraper
from tools.logger_utils import mask_sensitive_headers
from tools.providers.http import network
from tools.providers.http.download_types import NetworkPolicy


def main():
    with tempfile.TemporaryDirectory() as directory:
        outside = Path(directory) / 'fake-secret.txt'
        outside.write_text('AUDIT_FAKE_SECRET')
        scraper = object.__new__(Scraper)
        scraper.policy = NetworkPolicy(sandbox_dir=str(Path(directory) / 'sandbox'))
        scraper.extractor = SimpleNamespace(extract=lambda kind, data, **kw: ([data], {}))
        result, _ = scraper._parse_cached(
            SimpleNamespace(type='txt', name='audit'),
            SimpleNamespace(extracted=None, saved_path=str(outside)))
        assert result == ['AUDIT_FAKE_SECRET']
        print('CACHE: fichier factice hors sandbox transmis à extract().')
    masked = mask_sensitive_headers({'Cookie': 'FAKE_SESSION', 'Authorization': 'FAKE_TOKEN'})
    assert masked['Cookie'] == 'FAKE_SESSION' and masked['Authorization'] == '***'
    print('LOG: Cookie factice conservé par le masque.')
    response = SimpleNamespace(status_code=200)
    with patch.object(network, 'resolve_host_ips', return_value=['93.184.216.34']), patch.object(network.requests, 'get', return_value=response) as transport:
        network.get_response('https://audit.example/', NetworkPolicy(allow_domains={'audit.example'}))
        assert transport.call_args.args[0] == 'https://audit.example/'
        print('DNS: transport reçoit le hostname, pas une IP validée fixée. Preuve de conception, pas exploitation réseau.')


if __name__ == '__main__':
    main()
