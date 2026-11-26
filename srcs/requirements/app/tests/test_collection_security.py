"""Security regressions, with an in-memory HTTP transport and no external calls."""
import io
import subprocess
from types import SimpleNamespace
from unittest.mock import Mock
import pytest
import requests
from requests.adapters import BaseAdapter
from cti_core.config_model import ConfigModel
from cti_core.pipeline_steps import enrich_results
from tools.providers.http import network
from tools.providers.http.client import HttpClient
from tools.providers.http.download import _persist_content, download_source
from tools.providers.http.download_types import NetworkPolicy, StorageTarget
from tools.providers.http.policies import policy_with_overrides
from tools.providers.http.scanner import run_scan
from tools.result_entry import ResultEntry

class ResponseBody(io.BytesIO):
    def release_conn(self):
        self.close()


class ScriptedAdapter(BaseAdapter):
    def __init__(self, responses):
        self.responses, self.calls, self.bodies = responses, [], []
    def send(self, request, **kwargs):
        self.calls.append(request)
        status, headers, body = self.responses[request.url]
        response = requests.Response()
        response.request, response.url, response.status_code = request, request.url, status
        response.headers = requests.structures.CaseInsensitiveDict(headers)
        response.encoding, response.raw = 'utf-8', ResponseBody(body)
        self.bodies.append(response.raw)
        return response
    def close(self):
        pass

@pytest.fixture
def scripted_http(monkeypatch):
    sessions = []
    def configure(responses):
        session = requests.Session(); session.trust_env = False
        sessions.append(session)
        adapter = ScriptedAdapter(responses)
        session.mount('http://', adapter); session.mount('https://', adapter)
        monkeypatch.setattr(network.requests, 'get', session.get)
        monkeypatch.setattr(network, 'resolve_host_ips', lambda host: ['93.184.216.34'])
        return adapter
    yield configure
    for session in sessions:
        session.close()

@pytest.mark.parametrize('destination', ['http://allowed.example/plain', 'https://other.example/private', 'https://127.0.0.1/private'])
def test_redirect_rejected_before_contact(scripted_http, destination):
    start = 'https://allowed.example/start'
    adapter = scripted_http({start: (302, {'Location': destination}, b''), destination: (200, {}, b'private')})
    result = download_source({'url': start, 'type': 'txt'}, NetworkPolicy(allow_domains={'allowed.example'}))
    assert result.status == 'error'
    assert [r.url for r in adapter.calls] == [start]
    assert adapter.bodies[0].closed

def test_redirect_drops_source_credentials_and_uses_destination_auth(scripted_http):
    start, end = 'https://a.example/start', 'https://b.example/end'
    adapter = scripted_http({start: (302, {'Location': end}, b''), end: (200, {}, b'ok')})
    auth = {'headers': {'X-Global-Secret': 'global'}, 'hosts': {'a.example': {'X-API-Key': 'source-secret', 'Cookie': 'session=secret'}, 'b.example': {'X-Destination-Key': 'destination-secret'}}}
    client = HttpClient(NetworkPolicy(allow_domains={'a.example','b.example'}), respect_robots=False, auth_conf=auth)
    assert client.fetch({'url': start, 'type': 'txt'}).status == 'downloaded'
    assert adapter.calls[0].headers['X-API-Key'] == 'source-secret'
    headers = adapter.calls[1].headers
    assert not {'X-API-Key', 'X-Global-Secret', 'Cookie'}.intersection(headers)
    assert headers['X-Destination-Key'] == 'destination-secret'

def test_relative_redirect_preserves_auth(scripted_http):
    start, end = 'https://a.example/start', 'https://a.example/end'
    adapter = scripted_http({start: (302, {'Location': '/end'}, b''), end: (200, {}, b'ok')})
    result = download_source({'url': start, 'type': 'txt'}, NetworkPolicy(allow_domains={'a.example'}), headers={'X-API-Key':'secret'})
    assert result.status == 'downloaded'
    assert adapter.calls[1].headers['X-API-Key'] == 'secret'

def test_redirect_loop_is_bounded(scripted_http):
    url = 'https://a.example/loop'
    adapter = scripted_http({url: (302, {'Location':'/loop'}, b'')})
    assert download_source({'url':url,'type':'txt'}, NetworkPolicy(allow_domains={'a.example'})).status == 'error'
    assert len(adapter.calls) <= 11
    assert all(body.closed for body in adapter.bodies)

@pytest.mark.parametrize('url', ['file:///etc/passwd','ftp://a.example/file','https:///missing-host','https://user:password@a.example/'])
def test_invalid_url_never_reaches_transport(monkeypatch, url):
    request = Mock(); monkeypatch.setattr(network.requests,'get',request)
    assert download_source({'url':url,'type':'txt'}, NetworkPolicy(block_private=False)).status == 'error'
    request.assert_not_called()

def test_dns_failure_not_allowed(monkeypatch):
    monkeypatch.setattr(network,'resolve_host_ips',lambda host: [])
    request = Mock(); monkeypatch.setattr(network.requests,'get',request)
    assert download_source({'url':'https://a.example/','type':'txt'},NetworkPolicy()).status == 'error'
    request.assert_not_called()

def test_outside_sandbox_not_written(tmp_path):
    outside = tmp_path/'outside'
    saved,error = _persist_content(StorageTarget(outside,'txt','probe'),'.txt',b'probe',NetworkPolicy(sandbox_dir=str(tmp_path/'sandbox')))
    assert error and saved is None
    assert not outside.exists()

def test_symlink_outside_sandbox_not_followed(tmp_path):
    sandbox,outside = tmp_path/'sandbox',tmp_path/'outside'
    sandbox.mkdir(); outside.mkdir(); (sandbox/'txt').symlink_to(outside,target_is_directory=True)
    saved,error = _persist_content(StorageTarget(sandbox,'txt','probe'),'.txt',b'probe',NetworkPolicy(sandbox_dir=str(sandbox)))
    assert error and saved is None
    assert not (outside/'probe.txt').exists()

def test_absolute_storage_outside_sandbox_rejected(tmp_path):
    model = ConfigModel.__new__(ConfigModel)
    model.network_settings = {'save':{'base_dir':str(tmp_path/'outside')},'sandbox_dir':str(tmp_path/'sandbox')}
    with pytest.raises(ValueError,match='sandbox'):
        model._resolve_base_dir()

def test_rejected_download_preserves_existing_artifact(monkeypatch,tmp_path):
    storage = StorageTarget(tmp_path,'txt','probe'); target = storage.path_for('.txt')
    target.parent.mkdir(); target.write_bytes(b'previous validated content')
    monkeypatch.setattr('tools.providers.http.download.run_scan',lambda *a,**kw:'Detected')
    saved,error = _persist_content(storage,'.txt',b'rejected',NetworkPolicy(scan_command='scanner {file}'))
    assert error and saved is None
    assert target.read_bytes() == b'previous validated content'
    assert list(target.parent.iterdir()) == [target]

def test_scan_without_persistent_storage(monkeypatch):
    scanned = []
    def reject(path,*args,**kwargs):
        scanned.append(path.read_bytes()); return 'Detected'
    monkeypatch.setattr('tools.providers.http.download.run_scan',reject)
    saved,error = _persist_content(None,'.txt',b'rejected',NetworkPolicy(scan_command='scanner {file}'))
    assert error and saved is None and scanned == [b'rejected']

def test_yara_match_rejected(monkeypatch,tmp_path):
    monkeypatch.setattr('tools.providers.http.scanner.subprocess.run',lambda *a,**kw:SimpleNamespace(returncode=0,stdout='Suspicious_Executable file\n',stderr=''))
    assert run_scan(tmp_path/'file','yara rules.yar {file}')

def test_scan_path_single_argument(monkeypatch,tmp_path):
    captured=[]
    def execute(args,**kwargs):
        captured.extend(args); return SimpleNamespace(returncode=0,stdout='',stderr='')
    monkeypatch.setattr('tools.providers.http.scanner.subprocess.run',execute)
    path=tmp_path/'file with spaces.txt'
    assert run_scan(path,'scanner {file}') is None
    assert captured == ['scanner',str(path)]

@pytest.mark.parametrize('exc',[FileNotFoundError('missing'),subprocess.TimeoutExpired('scanner',1)])
def test_scan_failure_rejected(monkeypatch,tmp_path,exc):
    def execute(*args,**kwargs): raise exc
    monkeypatch.setattr('tools.providers.http.scanner.subprocess.run',execute)
    assert run_scan(tmp_path/'file','scanner {file}')

def test_rejected_file_not_reparsed(tmp_path):
    path=tmp_path/'rejected.html'; path.write_text('<p>REJECTED PAYLOAD</p>')
    result=ResultEntry('https://a.example','rejected','html','error',error='Scan échoué',saved_path=str(path))
    enrich_results([result],SimpleNamespace(scraping_settings={'html':{'extract':[{'tag':'p'}]}},keywords={}))
    assert result.extracted == []

def test_override_preserves_metrics_and_offline():
    derived=policy_with_overrides(NetworkPolicy(metrics_path='health.json',offline=True),{'max_bytes':100})
    assert derived.metrics_path == 'health.json' and derived.offline is True

def test_robots_redirect_cannot_contact_private_address(scripted_http):
    start,end='https://a.example/robots.txt','https://127.0.0.1/private'
    adapter=scripted_http({start:(302,{'Location':end},b''),end:(200,{},b'User-agent: *\nAllow: /')})
    client=HttpClient(NetworkPolicy(allow_domains={'a.example'}),respect_robots=True)
    assert client.fetch({'url':'https://a.example/page','type':'txt'}).status != 'downloaded'
    assert [r.url for r in adapter.calls] == [start]

def test_guarded_headless_uses_validated_http(monkeypatch):
    strategy=SimpleNamespace(fetch=Mock(return_value='<p>unsafe</p>'))
    monkeypatch.setattr(network,'resolve_host_ips',lambda host:['93.184.216.34'])
    fetch=Mock(return_value=SimpleNamespace(status='downloaded',content='validated HTTP'))
    monkeypatch.setattr('tools.providers.http.client.download_with_context',fetch)
    client=HttpClient(NetworkPolicy(allow_domains={'a.example'}),respect_robots=False,headless_strategy=strategy)
    result=client.fetch({'url':'https://a.example/','type':'html','headless':True})
    strategy.fetch.assert_not_called()
    assert result.content == 'validated HTTP'

def test_headless_size_limit():
    strategy=SimpleNamespace(fetch=Mock(return_value='x'*20))
    client=HttpClient(NetworkPolicy(enforce_https=False,block_private=False,max_bytes=5),respect_robots=False,headless_strategy=strategy)
    result=client.fetch({'url':'http://a.example/','type':'html','headless':True})
    assert result.status == 'error' and result.content is None


def test_validated_artifact_is_published_after_scan(monkeypatch, tmp_path):
    target = StorageTarget(tmp_path, 'txt', 'safe')
    published = target.path_for('.txt')
    def accept(path, *args, **kwargs):
        assert path != published
        assert path.read_bytes() == b'validated'
        assert not published.exists()
        return None
    monkeypatch.setattr('tools.providers.http.download.run_scan', accept)
    saved, error = _persist_content(target, '.txt', b'validated', NetworkPolicy(sandbox_dir=str(tmp_path), scan_command='scanner {file}'))
    assert error is None
    assert saved == published
    assert published.read_bytes() == b'validated'
    assert list(published.parent.iterdir()) == [published]


def test_headless_rejection_does_not_publish_or_return_content(monkeypatch, tmp_path):
    monkeypatch.setattr('tools.providers.http.download.run_scan', lambda *a, **kw: 'Detected')
    strategy = SimpleNamespace(fetch=Mock(return_value='<p>rejected</p>'))
    client = HttpClient(NetworkPolicy(enforce_https=False, block_private=False, sandbox_dir=str(tmp_path), scan_command='scanner {file}'), respect_robots=False, headless_strategy=strategy)
    storage = StorageTarget(tmp_path, 'html', 'probe')
    result = client.fetch({'url':'http://a.example/', 'type':'html', 'headless':True}, storage=storage)
    assert result.status == 'error'
    assert result.saved_path is None and result.content is None
    assert not storage.path_for('.html').exists()


@pytest.mark.parametrize('status,body,allowed', [
    (200,b'User-agent: *\nDisallow: /private',False),
    (200,b'User-agent: *\nAllow: /',True),
    (403,b'',False), (404,b'',True),
])
def test_robots_rules_and_missing_file(scripted_http, status, body, allowed):
    from tools.providers.http.policies import RobotsDelayPolicy
    adapter = scripted_http({'https://a.example/robots.txt': (status, {}, body)})
    policy = RobotsDelayPolicy(network_policy=NetworkPolicy(allow_domains={'a.example'}))
    assert policy.is_allowed('https://a.example/private') == allowed
    assert adapter.bodies[0].closed
    assert policy.is_allowed('https://a.example/private') == allowed
    assert len(adapter.calls) == 1


def test_stream_failure_closes_response_and_returns_error(monkeypatch):
    response = Mock(status_code=200, headers={}, encoding='utf-8')
    response.iter_content.side_effect = requests.ConnectionError('truncated body')
    monkeypatch.setattr(network, 'get_response', lambda *a, **kw: response)
    result = download_source({'url':'https://a.example/', 'type':'txt'}, NetworkPolicy())
    assert result.status == 'error' and result.content is None
    response.close.assert_called()
