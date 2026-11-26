# Inventaire des fonctions Intelium

149 fichiers Python, 708 fonctions ou méthodes, dont 301 dans les tests.

Régénération depuis la racine : `python3 docs/audit/inventory.py`.

Les usages sont des candidats par nom, pas un graphe résolu. Les constructeurs, alias, callbacks et méthodes polymorphes nécessitent une lecture manuelle. Les opérations incluent celles des fonctions imbriquées. Les rôles proviennent des docstrings ; leur absence est signalée. Le JSON fournit signatures, opérations et tous les usages candidats.

## cti_core/Source.py

- [`Source.__init__`](../../srcs/requirements/app/cti_core/Source.py#L25) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : normalize_overrides, source.get. Usages candidats : 0.
- [`Source._compute_hash_from_content`](../../srcs/requirements/app/cti_core/Source.py#L36) — Calcule un hash SHA-256 pour du texte ou des bytes.
  Appels effectués : compute_sha256_from_text, hashlib.sha256, hashlib.sha256(content).hexdigest, isinstance. Usages candidats : 3.
- [`Source.normalized_overrides`](../../srcs/requirements/app/cti_core/Source.py#L46) — Retourne les overrides normalisés.
  Appels effectués : normalize_overrides. Usages candidats : 1.
- [`Source.download_manager`](../../srcs/requirements/app/cti_core/Source.py#L50) — Gestionnaire générique qui délègue le téléchargement selon le type de source. Supporte html, api, xml, pdf, csv, image, ignore.
  Appels effectués : Path, StorageTarget, download_source, self.update_hash. Usages candidats : 4.
- [`Source.update_hash`](../../srcs/requirements/app/cti_core/Source.py#L82) — Met à jour le hash à partir du contenu actuel.
  Appels effectués : self._compute_hash_from_content. Usages candidats : 2.
- [`Source.has_changed`](../../srcs/requirements/app/cti_core/Source.py#L90) — Compare le hash actuel avec un ancien pour détecter les changements.
  Appels effectués : self._compute_hash_from_content. Usages candidats : 7.
- [`Source.verify_integrity`](../../srcs/requirements/app/cti_core/Source.py#L99) — Vérifie si le hash enregistré correspond au contenu actuel.
  Appels effectués : self._compute_hash_from_content. Usages candidats : 0.

## cti_core/__init__.py


## cti_core/cli.py

- [`render_progress`](../../srcs/requirements/app/cti_core/cli.py#L8) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : int, max, sys.stdout.flush, sys.stdout.write. Usages candidats : 2.
- [`print_summary`](../../srcs/requirements/app/cti_core/cli.py#L16) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : json.dumps, normalize_results, print. Usages candidats : 1.

## cti_core/config_model.py

- [`ConfigModel.__init__`](../../srcs/requirements/app/cti_core/config_model.py#L23) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : Path, build_crawler_settings, build_http_client_settings, build_network_policy, get_config_as_json_string, load_auth, load_keywords_from_config, load_yaml_config, self._build_sources, self._validate_configs, self.crawler_settings.get, self.network_settings.get, self.yaml_config.get. Usages candidats : 0.
- [`ConfigModel._sanitize_segment`](../../srcs/requirements/app/cti_core/config_model.py#L46) — Nettoie un segment de chemin (nom/type) pour éviter les traversals et les séparateurs. Conserve uniquement les caractères autorisés, remplace le reste par underscore.
  Appels effectués : (value or '').strip, re.sub, text.lstrip, text.replace, text.replace('/', '_').replace. Usages candidats : 2.
- [`ConfigModel._resolve_base_dir`](../../srcs/requirements/app/cti_core/config_model.py#L59) — Détermine le dossier de stockage effectif en respectant un éventuel sandbox_dir. Si sandbox_dir est défini et que base_dir n'est pas déjà dedans, on le reloge sous le sandbox.
  Appels effectués : (sandbox_resolved / base_dir).resolve, Path, ValueError, base_dir.is_absolute, base_dir.resolve, sandbox_path.resolve, self.network_settings.get, self.network_settings.get('save', {}).get. Usages candidats : 2.
- [`ConfigModel.build_storage_target`](../../srcs/requirements/app/cti_core/config_model.py#L89) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : StorageTarget, self._resolve_base_dir, self._sanitize_segment. Usages candidats : 1.
- [`ConfigModel._validate_configs`](../../srcs/requirements/app/cti_core/config_model.py#L95) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : self.errors.extend, self.warnings.extend, validate_config. Usages candidats : 1.
- [`ConfigModel._build_sources`](../../srcs/requirements/app/cti_core/config_model.py#L100) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : (entry.get('type') or 'html').lower, Source, built_sources.append, dict, entry.get, enumerate, isinstance, normalize_overrides, normalized.get, seen_names.add, self.errors.append, self.warnings.append, set. Usages candidats : 1.
- [`ConfigModel.has_errors`](../../srcs/requirements/app/cti_core/config_model.py#L142) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : bool. Usages candidats : 3.
- [`ConfigModel.has_warnings`](../../srcs/requirements/app/cti_core/config_model.py#L145) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : bool. Usages candidats : 2.

## cti_core/crawler_state.py

- [`CrawlerState.__init__`](../../srcs/requirements/app/cti_core/crawler_state.py#L11) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : deque, set, threading.Lock. Usages candidats : 0.
- [`CrawlerState._guard`](../../srcs/requirements/app/cti_core/crawler_state.py#L21) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : contextlib.nullcontext. Usages candidats : 6.
- [`CrawlerState.add`](../../srcs/requirements/app/cti_core/crawler_state.py#L26) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : self._guard, self._normalizer, self.queue.append. Usages candidats : 19.
- [`CrawlerState.has_next`](../../srcs/requirements/app/cti_core/crawler_state.py#L35) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : bool, self._guard. Usages candidats : 0.
- [`CrawlerState.pop`](../../srcs/requirements/app/cti_core/crawler_state.py#L41) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : self._guard, self.queue.popleft. Usages candidats : 9.
- [`CrawlerState.pop_if_any`](../../srcs/requirements/app/cti_core/crawler_state.py#L45) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : self._guard, self._normalizer, self.queue.popleft. Usages candidats : 1.
- [`CrawlerState.mark_visited`](../../srcs/requirements/app/cti_core/crawler_state.py#L60) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : self._guard, self._normalizer, self.visited.add. Usages candidats : 1.
- [`CrawlerState.already_visited`](../../srcs/requirements/app/cti_core/crawler_state.py#L64) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : self._guard, self._normalizer. Usages candidats : 2.

## cti_core/orchestrator.py

- [`Orchestrator.__init__`](../../srcs/requirements/app/cti_core/orchestrator.py#L21) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : load_schedule_config, load_yaml_config, logging.basicConfig, logging.getLogger, threading.Event, threading.Lock, yaml_conf.get. Usages candidats : 0.
- [`Orchestrator.stop`](../../srcs/requirements/app/cti_core/orchestrator.py#L33) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : self._stop.set. Usages candidats : 1.
- [`Orchestrator._run_once`](../../srcs/requirements/app/cti_core/orchestrator.py#L36) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : RunMetrics, record_run, run, self._running.acquire, self._running.release, self.logger.error, self.logger.info, str, time.time. Usages candidats : 1.
- [`Orchestrator._sleep_with_stop`](../../srcs/requirements/app/cti_core/orchestrator.py#L57) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : int, range, self._stop.is_set, time.sleep. Usages candidats : 2.
- [`Orchestrator.serve_forever`](../../srcs/requirements/app/cti_core/orchestrator.py#L63) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : compute_initial_delay, self._run_once, self._sleep_with_stop, self._stop.is_set, self.logger.info. Usages candidats : 2.
- [`run_orchestrator`](../../srcs/requirements/app/cti_core/orchestrator.py#L85) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : Orchestrator, orch.logger.info, orch.serve_forever, orch.stop, signal.signal. Usages candidats : 1.
- [`run_orchestrator._handle_signal`](../../srcs/requirements/app/cti_core/orchestrator.py#L88) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : orch.logger.info, orch.stop. Usages candidats : 0.

## cti_core/pipeline.py

- [`build_cache_manager`](../../srcs/requirements/app/cti_core/pipeline.py#L20) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : build_cache. Usages candidats : 1.
- [`run_fetch`](../../srcs/requirements/app/cti_core/pipeline.py#L24) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : Scraper, len, print, render_progress, scraper.run. Usages candidats : 1.
- [`prepare_results`](../../srcs/requirements/app/cti_core/pipeline.py#L34) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : normalize_results. Usages candidats : 1.
- [`build_output_conf`](../../srcs/requirements/app/cti_core/pipeline.py#L38) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : dict, output_conf.get. Usages candidats : 1.
- [`run_report`](../../srcs/requirements/app/cti_core/pipeline.py#L47) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : Path, ai_conf.get, ai_is_complete, ai_output.read_text, ai_output.resolve, bool, generate_ai_report, logger.warning, output_conf.get, report_path.read_text, report_path.resolve, report_path.write_text, write_report. Usages candidats : 2.
- [`run_pipeline`](../../srcs/requirements/app/cti_core/pipeline.py#L73) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : build_cache_manager, build_output_conf, config_model.yaml_config.get, datetime.now, datetime.now(timezone.utc).isoformat, enrich_results, logger.warning, output_conf.get, output_conf.get('ai_report', {}).get, prepare_results, print_summary, run_fetch, run_report, score_results_payload, send_report_email, str, uuid.uuid4. Usages candidats : 1.

## cti_core/pipeline_steps.py

- [`enrich_results`](../../srcs/requirements/app/cti_core/pipeline_steps.py#L16) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : Extractor, Path, ensure_text, extractor.extract, find_keyword_hits, path.exists, path.read_bytes, res.get. Usages candidats : 2.
- [`score_results_payload`](../../srcs/requirements/app/cti_core/pipeline_steps.py#L51) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : compute_confidence, res.get, score_results, scoring_conf.get. Usages candidats : 1.

## cti_core/result_recorder.py

- [`ResultRecorder.__init__`](../../srcs/requirements/app/cti_core/result_recorder.py#L14) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : build_result_store, dict, threading.Lock. Usages candidats : 0.
- [`ResultRecorder.record_cache_hit`](../../srcs/requirements/app/cti_core/result_recorder.py#L27) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : ResultEntry, compute_confidence, record.extra.update, record.to_dict, self.cache.record_scrape, self.result_store.save, self.results.append. Usages candidats : 1.
- [`ResultRecorder.record_result`](../../srcs/requirements/app/cti_core/result_recorder.py#L59) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : ResultEntry, compute_confidence, getattr, record.extra.update, record.to_dict, self.cache.record_scrape, self.result_store.save, self.results.append, str. Usages candidats : 5.
- [`ResultRecorder.check_or_record_cache_hit`](../../srcs/requirements/app/cti_core/result_recorder.py#L91) — Deprecated: use record_cache_hit with a Source object.
  Appels effectués : aucun appel explicite. Usages candidats : 0.

## cti_core/runner.py

- [`_validate_allowlist`](../../srcs/requirements/app/cti_core/runner.py#L12) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : '; '.join, bool, config_model.crawler_settings.get, getattr, getattr(config_model, 'yaml_config', {}).get, invalid.append, logger.error, ops_conf.get, set, urlparse. Usages candidats : 4.
- [`run`](../../srcs/requirements/app/cti_core/runner.py#L35) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : ConfigModel, _validate_allowlist, check_env_requirements, config_model.has_errors, config_model.has_warnings, config_model.keywords.keys, config_model.yaml_config.get, get_config_as_json_string, list, log_structured, logger.debug, logger.error, logger.info, logger.warning, print, run_pipeline, setup_logger, src.get. Usages candidats : 20.

## cti_core/scraper.py

- [`Scraper.__init__`](../../srcs/requirements/app/cti_core/scraper.py#L24) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : Extractor, Quota, ResultRecorder, UrlPolicy, bool, build_fetcher, crawler_conf.get, getattr, getattr(config_model, 'yaml_config', {}).get, getattr(config_model, 'yaml_config', {}).get('cache', {}).get, int, set. Usages candidats : 0.
- [`Scraper._normalize_url`](../../srcs/requirements/app/cti_core/scraper.py#L56) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : self.url_policy.normalize. Usages candidats : 0.
- [`Scraper._same_domain`](../../srcs/requirements/app/cti_core/scraper.py#L59) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : same_domain. Usages candidats : 0.
- [`Scraper._fetch_and_parse`](../../srcs/requirements/app/cti_core/scraper.py#L62) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : current.normalized_overrides, current.update_hash, datetime.now, datetime.now(timezone.utc).isoformat, hasattr, self.config_model.build_storage_target, self.extractor.extract, self.fetcher.fetch. Usages candidats : 1.
- [`Scraper._parse_cached`](../../srcs/requirements/app/cti_core/scraper.py#L86) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : Path, ensure_text, getattr, path.exists, path.read_bytes, self.extractor.extract. Usages candidats : 1.
- [`Scraper._process_source`](../../srcs/requirements/app/cti_core/scraper.py#L105) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : DownloadResult, enqueue_links, getattr, isinstance, len, self._cache_is_fresh, self._fetch_and_parse, self._parse_cached, self.cache.get, self.global_quota.add_bytes, self.recorder.record_cache_hit, self.recorder.record_result, state.already_visited, state.mark_visited. Usages candidats : 1.
- [`Scraper._cache_is_fresh`](../../srcs/requirements/app/cti_core/scraper.py#L144) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : (datetime.now(timezone.utc) - fetched_at).total_seconds, datetime.fromisoformat, datetime.now, entry.date.replace, fetched_at.replace, float, getattr. Usages candidats : 5.
- [`Scraper._worker_loop`](../../srcs/requirements/app/cti_core/scraper.py#L157) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : DownloadResult, self._process_source, self.global_quota.reserve_page, self.recorder.record_result, state.pop_if_any. Usages candidats : 1.
- [`Scraper._process_single`](../../srcs/requirements/app/cti_core/scraper.py#L170) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : CrawlerState, DownloadResult, ThreadPoolExecutor, executor.submit, future.result, range, self._worker_loop, self.global_quota.remaining_pages, self.recorder.record_result, state.add. Usages candidats : 1.
- [`Scraper.run`](../../srcs/requirements/app/cti_core/scraper.py#L189) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : self._process_single. Usages candidats : 20.

## cti_core/sources_factory.py

- [`enqueue_links`](../../srcs/requirements/app/cti_core/sources_factory.py#L10) — Extrait les liens HTML et les ajoute dans la queue si autorisés.
  Appels effectués : Source, extract_links, isinstance, state.add, state.already_visited, url_policy.can_follow, url_policy.normalize. Usages candidats : 1.

## main.py

- [`main`](../../srcs/requirements/app/main.py#L6) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : argparse.ArgumentParser, parser.add_argument, parser.parse_args, parser.set_defaults, run. Usages candidats : 10.

## scripts/cache_admin.py

- [`_run_action`](../../srcs/requirements/app/scripts/cache_admin.py#L24) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : store.clear, store.stats. Usages candidats : 3.
- [`main`](../../srcs/requirements/app/scripts/cache_admin.py#L28) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : FileCacheStore, MongoCacheStore, Path, PerSiteCacheStore, _run_action, argparse.ArgumentParser, get_secret, json.dumps, parser.add_argument, parser.error, parser.parse_args, print. Usages candidats : 10.

## scripts/health_summary.py


## scripts/metrics_server.py

- [`MetricsHandler.do_GET`](../../srcs/requirements/app/scripts/metrics_server.py#L18) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : self._serve_metrics, self.end_headers, self.path.startswith, self.send_response. Usages candidats : 0.
- [`MetricsHandler._serve_metrics`](../../srcs/requirements/app/scripts/metrics_server.py#L27) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : '\n'.join, (s.get('fetch_per_status', {}) or {}).items, (s.get('fetch_reasons', {}) or {}).items, Path, body.encode, float, json.dumps, len, lines.append, load_health, s.get, self.end_headers, self.send_header, self.send_response, self.wfile.write, str, summary. Usages candidats : 2.
- [`main`](../../srcs/requirements/app/scripts/metrics_server.py#L68) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : HTTPServer, argparse.ArgumentParser, parser.add_argument, parser.parse_args, print, server.serve_forever. Usages candidats : 10.

## scripts/mistral_llm.py

- [`main`](../../srcs/requirements/app/scripts/mistral_llm.py#L18) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : argparse.ArgumentParser, float, int, json.dumps, os.environ.get, parser.add_argument, parser.parse_args, print, prompt.strip, range, requests.post, resp.json, sys.exit, sys.stdin.read, sys.stdout.write, time.sleep. Usages candidats : 10.

## scripts/ollama_llm.py

- [`main`](../../srcs/requirements/app/scripts/ollama_llm.py#L23) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : RuntimeError, _call_cli, _call_http, _ollama_options, argparse.ArgumentParser, data.get, float, host.rstrip, int, os.environ.get, parser.add_argument, parser.parse_args, print, proc.stderr.strip, proc.stdout.strip, prompt.strip, range, requests.post, resp.json, result.strip, subprocess.run, sys.stdin.read, sys.stdout.write, time.sleep. Usages candidats : 10.
- [`main._ollama_options`](../../srcs/requirements/app/scripts/ollama_llm.py#L36) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : float, int, os.environ.get. Usages candidats : 1.
- [`main._call_http`](../../srcs/requirements/app/scripts/ollama_llm.py#L58) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : RuntimeError, _ollama_options, data.get, host.rstrip, requests.post, resp.json. Usages candidats : 1.
- [`main._call_cli`](../../srcs/requirements/app/scripts/ollama_llm.py#L74) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : RuntimeError, proc.stderr.strip, proc.stdout.strip, subprocess.run. Usages candidats : 1.

## scripts/orchestrator.py

- [`main`](../../srcs/requirements/app/scripts/orchestrator.py#L5) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : argparse.ArgumentParser, parser.add_argument, parser.parse_args, run_orchestrator. Usages candidats : 10.

## scripts/smoke.py

- [`main`](../../srcs/requirements/app/scripts/smoke.py#L9) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : ' '.join, print, subprocess.run, sys.exit. Usages candidats : 10.

## scripts/verify_cti_report.py

- [`main`](../../srcs/requirements/app/scripts/verify_cti_report.py#L20) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : '; '.join, (output / 'raw').mkdir, (output / 'results.json').write_text, ConfigModel, HttpClient, Path, ValueError, all, argparse.ArgumentParser, args.results.read_text, artifact.write_bytes, bool, client.fetch, content.encode, datetime.now, datetime.now(timezone.utc).isoformat, generate_ai_report, hashlib.sha256, hashlib.sha256(raw).hexdigest, isinstance, json.dumps, json.loads, len, output.mkdir, parse_content, parser.add_argument, parser.parse_args, path.with_suffix, path.with_suffix('.quality.json').read_text, print, replace, results.append, source.get, str, sum, write_report. Usages candidats : 10.

## tests/conftest.py

- [`DummyConfigModel.__init__`](../../srcs/requirements/app/tests/conftest.py#L7) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : NetworkPolicy, set. Usages candidats : 0.
- [`DummyConfigModel.build_storage_target`](../../srcs/requirements/app/tests/conftest.py#L57) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : StorageTarget. Usages candidats : 1.
- [`dummy_config_model`](../../srcs/requirements/app/tests/conftest.py#L62) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : DummyConfigModel. Usages candidats : 11.
- [`dummy_config_model._build`](../../srcs/requirements/app/tests/conftest.py#L63) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : DummyConfigModel. Usages candidats : 0.
- [`minimal_config`](../../srcs/requirements/app/tests/conftest.py#L83) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : aucun appel explicite. Usages candidats : 0.
- [`fake_client_factory`](../../srcs/requirements/app/tests/conftest.py#L97) — Fabrique un faux client HTTP basé sur une table url->content. Chaque instance expose l'attribut 'calls' pour inspection.
  Appels effectués : DownloadResult, FakeClient, content_map.get, self.calls.append, source.get. Usages candidats : 7.
- [`fake_client_factory._build`](../../srcs/requirements/app/tests/conftest.py#L103) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : DownloadResult, FakeClient, content_map.get, self.calls.append, source.get. Usages candidats : 0.
- [`fake_client_factory._build.FakeClient.__init__`](../../srcs/requirements/app/tests/conftest.py#L105) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : aucun appel explicite. Usages candidats : 0.
- [`fake_client_factory._build.FakeClient.fetch`](../../srcs/requirements/app/tests/conftest.py#L107) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : DownloadResult, content_map.get, self.calls.append, source.get. Usages candidats : 20.

## tests/test_ai_pipeline.py

- [`test_langgraph_runner_builds_prompt_and_uses_llm`](../../srcs/requirements/app/tests/test_ai_pipeline.py#L4) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : LangGraphRunner, runner.generate. Usages candidats : 0.
- [`test_langgraph_runner_builds_prompt_and_uses_llm.fake_llm`](../../srcs/requirements/app/tests/test_ai_pipeline.py#L7) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : aucun appel explicite. Usages candidats : 0.
- [`test_validate_report_text_raises_on_empty`](../../srcs/requirements/app/tests/test_ai_pipeline.py#L18) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : _validate_report_text. Usages candidats : 0.
- [`test_build_cli_llm_runs_command`](../../srcs/requirements/app/tests/test_ai_pipeline.py#L27) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : P, build_cli_llm, llm, monkeypatch.setattr. Usages candidats : 0.
- [`test_build_cli_llm_runs_command.fake_run`](../../srcs/requirements/app/tests/test_ai_pipeline.py#L28) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : P. Usages candidats : 0.

## tests/test_ai_report_completion.py

- [`test_is_complete_requires_marker`](../../srcs/requirements/app/tests/test_ai_report_completion.py#L4) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : _is_complete. Usages candidats : 0.
- [`test_is_complete_normalizes_accents`](../../srcs/requirements/app/tests/test_ai_report_completion.py#L11) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : _is_complete. Usages candidats : 0.

## tests/test_ai_report_extra.py

- [`test_load_template_from_yaml_prompt_key`](../../srcs/requirements/app/tests/test_ai_report_extra.py#L6) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : ai_report.PromptConfig, prompt_conf.load_template, str, tmpl_path.write_text. Usages candidats : 0.
- [`test_generate_ai_report_sets_pass_prompt_as_arg_for_codex`](../../srcs/requirements/app/tests/test_ai_report_extra.py#L17) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : ai_report.generate_ai_report, monkeypatch.setattr, out.read_text. Usages candidats : 0.
- [`test_generate_ai_report_sets_pass_prompt_as_arg_for_codex.fake_run`](../../srcs/requirements/app/tests/test_ai_report_extra.py#L20) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : aucun appel explicite. Usages candidats : 0.
- [`test_generate_ai_report_accepts_incomplete_and_fills_sections`](../../srcs/requirements/app/tests/test_ai_report_extra.py#L40) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : ai_report.generate_ai_report, monkeypatch.setattr, out.read_text. Usages candidats : 0.
- [`test_generate_ai_report_accepts_incomplete_and_fills_sections.fake_run`](../../srcs/requirements/app/tests/test_ai_report_extra.py#L41) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : aucun appel explicite. Usages candidats : 0.

## tests/test_ai_report_langgraph.py

- [`test_generate_ai_report_langgraph_mode`](../../srcs/requirements/app/tests/test_ai_report_langgraph.py#L6) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : ai_report.generate_ai_report, classmethod, monkeypatch.setattr, out.read_text. Usages candidats : 0.
- [`test_generate_ai_report_langgraph_mode.fake_generate`](../../srcs/requirements/app/tests/test_ai_report_langgraph.py#L9) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : aucun appel explicite. Usages candidats : 0.
- [`test_generate_ai_report_langgraph_with_cli_llm`](../../srcs/requirements/app/tests/test_ai_report_langgraph.py#L23) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : P, ai_report.generate_ai_report, classmethod, monkeypatch.setattr, out.read_text. Usages candidats : 0.
- [`test_generate_ai_report_langgraph_with_cli_llm.fake_run`](../../srcs/requirements/app/tests/test_ai_report_langgraph.py#L26) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : P. Usages candidats : 0.

## tests/test_auth.py

- [`test_build_headers_uses_hosts_section_only`](../../srcs/requirements/app/tests/test_auth.py#L6) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : build_headers. Usages candidats : 0.
- [`test_load_auth_env_substitution`](../../srcs/requirements/app/tests/test_auth.py#L20) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : auth_file.write_text, load_auth, monkeypatch.setenv. Usages candidats : 0.

## tests/test_cache.py

- [`test_cache_manager_load_and_update`](../../srcs/requirements/app/tests/test_cache.py#L6) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : CacheEntry, CacheManager, manager.get, manager.save, manager.update, manager2.get. Usages candidats : 0.
- [`test_cache_manager_has_changed`](../../srcs/requirements/app/tests/test_cache.py#L24) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : CacheEntry, CacheManager, manager.has_changed, manager.update. Usages candidats : 0.
- [`test_cache_record_scrape_auto_save`](../../srcs/requirements/app/tests/test_cache.py#L35) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : CacheManager, cache_file.exists, manager.record_scrape, reloaded.get. Usages candidats : 0.
- [`test_cache_record_scrape_preserves_extracted_and_keywords`](../../srcs/requirements/app/tests/test_cache.py#L57) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : CacheManager, manager.get, manager.record_scrape. Usages candidats : 0.
- [`test_cache_registry_separate_files`](../../srcs/requirements/app/tests/test_cache.py#L78) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : CacheRegistry, a_cache.exists, b_cache.exists, reg2.get, registry.record_scrape. Usages candidats : 0.
- [`test_build_cache_store_file_default`](../../srcs/requirements/app/tests/test_cache.py#L105) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : build_cache_store, isinstance, monkeypatch.delenv, str. Usages candidats : 0.
- [`test_build_cache_store_per_site`](../../srcs/requirements/app/tests/test_cache.py#L114) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : build_cache_store, isinstance, monkeypatch.delenv, str. Usages candidats : 0.
- [`test_build_cache_store_mongo_env`](../../srcs/requirements/app/tests/test_cache.py#L123) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : build_cache_store, isinstance, monkeypatch.setenv. Usages candidats : 0.

## tests/test_certkev_parser.py

- [`test_extract_certkev_entries_with_context`](../../srcs/requirements/app/tests/test_certkev_parser.py#L5) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : any, extract_certkev_entries, len. Usages candidats : 0.
- [`test_parser_auto_certkev_on_cert_source`](../../srcs/requirements/app/tests/test_certkev_parser.py#L16) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : any, parser.parse_content. Usages candidats : 0.
- [`test_is_certkev_source_helper`](../../srcs/requirements/app/tests/test_certkev_parser.py#L24) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : is_certkev_source. Usages candidats : 0.

## tests/test_collection_security.py

- [`ResponseBody.release_conn`](../../srcs/requirements/app/tests/test_collection_security.py#L20) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : self.close. Usages candidats : 0.
- [`ScriptedAdapter.__init__`](../../srcs/requirements/app/tests/test_collection_security.py#L25) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : aucun appel explicite. Usages candidats : 0.
- [`ScriptedAdapter.send`](../../srcs/requirements/app/tests/test_collection_security.py#L27) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : ResponseBody, requests.Response, requests.structures.CaseInsensitiveDict, self.bodies.append, self.calls.append. Usages candidats : 0.
- [`ScriptedAdapter.close`](../../srcs/requirements/app/tests/test_collection_security.py#L36) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : aucun appel explicite. Usages candidats : 9.
- [`scripted_http`](../../srcs/requirements/app/tests/test_collection_security.py#L40) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : ScriptedAdapter, monkeypatch.setattr, requests.Session, session.close, session.mount, sessions.append. Usages candidats : 6.
- [`scripted_http.configure`](../../srcs/requirements/app/tests/test_collection_security.py#L42) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : ScriptedAdapter, monkeypatch.setattr, requests.Session, session.mount, sessions.append. Usages candidats : 0.
- [`test_redirect_rejected_before_contact`](../../srcs/requirements/app/tests/test_collection_security.py#L55) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : NetworkPolicy, download_source, pytest.mark.parametrize, scripted_http. Usages candidats : 0.
- [`test_redirect_drops_source_credentials_and_uses_destination_auth`](../../srcs/requirements/app/tests/test_collection_security.py#L63) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : HttpClient, NetworkPolicy, client.fetch, scripted_http, {'X-API-Key', 'X-Global-Secret', 'Cookie'}.intersection. Usages candidats : 0.
- [`test_relative_redirect_preserves_auth`](../../srcs/requirements/app/tests/test_collection_security.py#L74) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : NetworkPolicy, download_source, scripted_http. Usages candidats : 0.
- [`test_redirect_loop_is_bounded`](../../srcs/requirements/app/tests/test_collection_security.py#L81) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : NetworkPolicy, all, download_source, len, scripted_http. Usages candidats : 0.
- [`test_invalid_url_never_reaches_transport`](../../srcs/requirements/app/tests/test_collection_security.py#L89) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : Mock, NetworkPolicy, download_source, monkeypatch.setattr, pytest.mark.parametrize, request.assert_not_called. Usages candidats : 0.
- [`test_dns_failure_not_allowed`](../../srcs/requirements/app/tests/test_collection_security.py#L94) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : Mock, NetworkPolicy, download_source, monkeypatch.setattr, request.assert_not_called. Usages candidats : 0.
- [`test_outside_sandbox_not_written`](../../srcs/requirements/app/tests/test_collection_security.py#L100) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : NetworkPolicy, StorageTarget, _persist_content, outside.exists, str. Usages candidats : 0.
- [`test_symlink_outside_sandbox_not_followed`](../../srcs/requirements/app/tests/test_collection_security.py#L106) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : (outside / 'probe.txt').exists, (sandbox / 'txt').symlink_to, NetworkPolicy, StorageTarget, _persist_content, outside.mkdir, sandbox.mkdir, str. Usages candidats : 0.
- [`test_absolute_storage_outside_sandbox_rejected`](../../srcs/requirements/app/tests/test_collection_security.py#L113) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : ConfigModel.__new__, model._resolve_base_dir, pytest.raises, str. Usages candidats : 0.
- [`test_rejected_download_preserves_existing_artifact`](../../srcs/requirements/app/tests/test_collection_security.py#L119) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : NetworkPolicy, StorageTarget, _persist_content, list, monkeypatch.setattr, storage.path_for, target.parent.iterdir, target.parent.mkdir, target.read_bytes, target.write_bytes. Usages candidats : 0.
- [`test_scan_without_persistent_storage`](../../srcs/requirements/app/tests/test_collection_security.py#L128) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : NetworkPolicy, _persist_content, monkeypatch.setattr, path.read_bytes, scanned.append. Usages candidats : 0.
- [`test_scan_without_persistent_storage.reject`](../../srcs/requirements/app/tests/test_collection_security.py#L130) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : path.read_bytes, scanned.append. Usages candidats : 0.
- [`test_yara_match_rejected`](../../srcs/requirements/app/tests/test_collection_security.py#L136) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : SimpleNamespace, monkeypatch.setattr, run_scan. Usages candidats : 0.
- [`test_scan_path_single_argument`](../../srcs/requirements/app/tests/test_collection_security.py#L140) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : SimpleNamespace, captured.extend, monkeypatch.setattr, run_scan, str. Usages candidats : 0.
- [`test_scan_path_single_argument.execute`](../../srcs/requirements/app/tests/test_collection_security.py#L142) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : SimpleNamespace, captured.extend. Usages candidats : 0.
- [`test_scan_failure_rejected`](../../srcs/requirements/app/tests/test_collection_security.py#L150) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : FileNotFoundError, monkeypatch.setattr, pytest.mark.parametrize, run_scan, subprocess.TimeoutExpired. Usages candidats : 0.
- [`test_scan_failure_rejected.execute`](../../srcs/requirements/app/tests/test_collection_security.py#L151) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : aucun appel explicite. Usages candidats : 0.
- [`test_rejected_file_not_reparsed`](../../srcs/requirements/app/tests/test_collection_security.py#L155) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : ResultEntry, SimpleNamespace, enrich_results, path.write_text, str. Usages candidats : 0.
- [`test_override_preserves_metrics_and_offline`](../../srcs/requirements/app/tests/test_collection_security.py#L161) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : NetworkPolicy, policy_with_overrides. Usages candidats : 0.
- [`test_robots_redirect_cannot_contact_private_address`](../../srcs/requirements/app/tests/test_collection_security.py#L165) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : HttpClient, NetworkPolicy, client.fetch, scripted_http. Usages candidats : 0.
- [`test_guarded_headless_uses_validated_http`](../../srcs/requirements/app/tests/test_collection_security.py#L172) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : HttpClient, Mock, NetworkPolicy, SimpleNamespace, client.fetch, monkeypatch.setattr, strategy.fetch.assert_not_called. Usages candidats : 0.
- [`test_headless_size_limit`](../../srcs/requirements/app/tests/test_collection_security.py#L182) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : HttpClient, Mock, NetworkPolicy, SimpleNamespace, client.fetch. Usages candidats : 0.
- [`test_validated_artifact_is_published_after_scan`](../../srcs/requirements/app/tests/test_collection_security.py#L189) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : NetworkPolicy, StorageTarget, _persist_content, list, monkeypatch.setattr, path.read_bytes, published.exists, published.parent.iterdir, published.read_bytes, str, target.path_for. Usages candidats : 0.
- [`test_validated_artifact_is_published_after_scan.accept`](../../srcs/requirements/app/tests/test_collection_security.py#L192) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : path.read_bytes, published.exists. Usages candidats : 0.
- [`test_headless_rejection_does_not_publish_or_return_content`](../../srcs/requirements/app/tests/test_collection_security.py#L205) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : HttpClient, Mock, NetworkPolicy, SimpleNamespace, StorageTarget, client.fetch, monkeypatch.setattr, storage.path_for, storage.path_for('.html').exists, str. Usages candidats : 0.
- [`test_robots_rules_and_missing_file`](../../srcs/requirements/app/tests/test_collection_security.py#L221) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : NetworkPolicy, RobotsDelayPolicy, len, policy.is_allowed, pytest.mark.parametrize, scripted_http. Usages candidats : 0.
- [`test_stream_failure_closes_response_and_returns_error`](../../srcs/requirements/app/tests/test_collection_security.py#L231) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : Mock, NetworkPolicy, download_source, monkeypatch.setattr, requests.ConnectionError, response.close.assert_called. Usages candidats : 0.

## tests/test_config_builders.py

- [`test_build_http_client_settings_defaults_and_overrides`](../../srcs/requirements/app/tests/test_config_builders.py#L5) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : build_http_client_settings. Usages candidats : 0.
- [`test_build_crawler_settings_global_quota`](../../srcs/requirements/app/tests/test_config_builders.py#L27) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : build_crawler_settings. Usages candidats : 0.

## tests/test_config_model.py

- [`test_config_model_builds_sources_and_keywords`](../../srcs/requirements/app/tests/test_config_model.py#L5) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : ConfigModel, conf_path.parent.mkdir, conf_path.write_text, json.dumps, keywords_path.parent.mkdir, keywords_path.write_text, len, model.has_errors. Usages candidats : 0.
- [`test_config_model_unknown_type_and_missing_url`](../../srcs/requirements/app/tests/test_config_model.py#L30) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : ConfigModel, conf_path.parent.mkdir, conf_path.write_text, json.dumps, keywords_path.parent.mkdir, keywords_path.write_text, model.has_errors, model.has_warnings. Usages candidats : 0.
- [`test_config_model_schedule_loaded`](../../srcs/requirements/app/tests/test_config_model.py#L58) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : ConfigModel, conf_path.parent.mkdir, conf_path.write_text, hasattr, json.dumps, keywords_path.parent.mkdir, keywords_path.write_text. Usages candidats : 0.

## tests/test_config_utils.py

- [`test_to_int_with_defaults`](../../srcs/requirements/app/tests/test_config_utils.py#L4) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : to_int. Usages candidats : 0.
- [`test_to_bool_parses_strings`](../../srcs/requirements/app/tests/test_config_utils.py#L10) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : to_bool. Usages candidats : 0.

## tests/test_config_validator.py

- [`test_validate_config_output_and_auth`](../../srcs/requirements/app/tests/test_config_validator.py#L4) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : any, validate_config. Usages candidats : 0.

## tests/test_crypter.py

- [`test_hash_consistency`](../../srcs/requirements/app/tests/test_crypter.py#L6) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : crypter.compute_sha256, os.remove, tempfile.NamedTemporaryFile, tmp.write. Usages candidats : 0.
- [`test_hash_text`](../../srcs/requirements/app/tests/test_crypter.py#L15) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : crypter.compute_sha256_from_text. Usages candidats : 0.
- [`test_encrypt_decrypt_cycle`](../../srcs/requirements/app/tests/test_crypter.py#L21) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : crypter.decrypt_file, crypter.encrypt_file, crypter.generate_key, f.read, open, os.path.exists, os.remove, tempfile.NamedTemporaryFile, tmp.write. Usages candidats : 0.
- [`test_file_integrity`](../../srcs/requirements/app/tests/test_crypter.py#L38) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : crypter.compute_sha256, crypter.verify_file_integrity, os.remove, tempfile.NamedTemporaryFile, tmp.write. Usages candidats : 0.

## tests/test_download.py

- [`FakeResponse.__init__`](../../srcs/requirements/app/tests/test_download.py#L7) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : text.encode. Usages candidats : 0.
- [`FakeResponse.raise_for_status`](../../srcs/requirements/app/tests/test_download.py#L15) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : download.network.requests.HTTPError. Usages candidats : 3.
- [`FakeResponse.iter_content`](../../srcs/requirements/app/tests/test_download.py#L19) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : len, range. Usages candidats : 2.
- [`FakeResponse.close`](../../srcs/requirements/app/tests/test_download.py#L24) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : aucun appel explicite. Usages candidats : 9.
- [`test_download_html`](../../srcs/requirements/app/tests/test_download.py#L28) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : FakeResponse, NetworkPolicy, download.download_source, monkeypatch.setattr. Usages candidats : 0.
- [`test_download_html.fake_get`](../../srcs/requirements/app/tests/test_download.py#L29) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : FakeResponse. Usages candidats : 0.
- [`test_download_api_content_type_error`](../../srcs/requirements/app/tests/test_download.py#L39) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : FakeResponse, NetworkPolicy, download.download_source, monkeypatch.setattr. Usages candidats : 0.
- [`test_download_api_content_type_error.fake_get`](../../srcs/requirements/app/tests/test_download.py#L40) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : FakeResponse. Usages candidats : 0.
- [`test_download_image`](../../srcs/requirements/app/tests/test_download.py#L49) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : FakeResponse, NetworkPolicy, download.download_source, monkeypatch.setattr, result.content.startswith. Usages candidats : 0.
- [`test_download_image.fake_get`](../../srcs/requirements/app/tests/test_download.py#L50) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : FakeResponse. Usages candidats : 0.
- [`test_download_ignore_type_skipped`](../../srcs/requirements/app/tests/test_download.py#L60) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : NetworkPolicy, download.download_source. Usages candidats : 0.
- [`test_download_unknown_type_fallback`](../../srcs/requirements/app/tests/test_download.py#L67) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : FakeResponse, NetworkPolicy, download.download_source, monkeypatch.setattr. Usages candidats : 0.
- [`test_download_unknown_type_fallback.fake_get`](../../srcs/requirements/app/tests/test_download.py#L68) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : FakeResponse. Usages candidats : 0.
- [`test_download_txt`](../../srcs/requirements/app/tests/test_download.py#L77) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : FakeResponse, NetworkPolicy, download.download_source, monkeypatch.setattr. Usages candidats : 0.
- [`test_download_txt.fake_get`](../../srcs/requirements/app/tests/test_download.py#L78) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : FakeResponse. Usages candidats : 0.
- [`test_download_respects_max_bytes_stream`](../../srcs/requirements/app/tests/test_download.py#L88) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : FakeResponse, NetworkPolicy, download.download_source, monkeypatch.setattr. Usages candidats : 0.
- [`test_download_respects_max_bytes_stream.fake_get`](../../srcs/requirements/app/tests/test_download.py#L89) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : FakeResponse. Usages candidats : 0.
- [`test_download_format_preserves_payload_and_storage`](../../srcs/requirements/app/tests/test_download.py#L108) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : FakeResponse, NetworkPolicy, StorageTarget, download.download_source, monkeypatch.setattr, payload.decode, pytest.fail, pytest.mark.parametrize, result.saved_path.read_bytes, str. Usages candidats : 0.
- [`test_download_format_preserves_payload_and_storage.unexpected_decode`](../../srcs/requirements/app/tests/test_download.py#L113) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : pytest.fail. Usages candidats : 0.

## tests/test_e2e_report.py

- [`test_e2e_scrape_to_report`](../../srcs/requirements/app/tests/test_e2e_report.py#L8) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : CacheManager, DownloadResult, FakeClient, detail_file.exists, dummy_config_model, importlib.import_module, report_module.write_report, report_path.exists, scraper.run, scraper_module.Scraper, source_module.Source. Usages candidats : 0.
- [`test_e2e_scrape_to_report.FakeClient.fetch`](../../srcs/requirements/app/tests/test_e2e_report.py#L22) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : DownloadResult. Usages candidats : 20.
- [`test_runner_ai_report_with_prompt_path`](../../srcs/requirements/app/tests/test_e2e_report.py#L43) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : CacheManager, DownloadResult, FakeClient, ai_path.exists, dummy_config_model, importlib.import_module, monkeypatch.setattr, output_conf.get, prompt_file.write_text, report_module.write_report, report_path.exists, runner_module.generate_ai_report, scraper.run, scraper_module.Scraper, source_module.Source. Usages candidats : 0.
- [`test_runner_ai_report_with_prompt_path.FakeClient.fetch`](../../srcs/requirements/app/tests/test_e2e_report.py#L59) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : DownloadResult. Usages candidats : 20.
- [`test_e2e_multi_sources_overrides_and_reports`](../../srcs/requirements/app/tests/test_e2e_report.py#L84) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : (tmp_path / 'sources' / 'a-d1.md').exists, (tmp_path / 'sources' / 'a.md').exists, (tmp_path / 'sources' / 'b.md').exists, CacheManager, DownloadResult, FakeClient, ai_path.exists, content_map.get, dummy_config_model, importlib.import_module, monkeypatch.setattr, output_conf.get, report_module.write_report, report_path.exists, runner_module.generate_ai_report, scraper.run, scraper_module.Scraper, self.calls.append, source.get, source_module.Source. Usages candidats : 0.
- [`test_e2e_multi_sources_overrides_and_reports.FakeClient.__init__`](../../srcs/requirements/app/tests/test_e2e_report.py#L104) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : aucun appel explicite. Usages candidats : 0.
- [`test_e2e_multi_sources_overrides_and_reports.FakeClient.fetch`](../../srcs/requirements/app/tests/test_e2e_report.py#L107) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : DownloadResult, content_map.get, self.calls.append, source.get. Usages candidats : 20.
- [`test_run_report_restores_base_on_incomplete_ai`](../../srcs/requirements/app/tests/test_e2e_report.py#L137) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : importlib.import_module, monkeypatch.setattr, pipeline_module.run_report, report_path.read_text. Usages candidats : 0.

## tests/test_email_report.py

- [`DummySMTP.__init__`](../../srcs/requirements/app/tests/test_email_report.py#L7) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : aucun appel explicite. Usages candidats : 0.
- [`DummySMTP.__enter__`](../../srcs/requirements/app/tests/test_email_report.py#L15) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : aucun appel explicite. Usages candidats : 0.
- [`DummySMTP.__exit__`](../../srcs/requirements/app/tests/test_email_report.py#L18) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : aucun appel explicite. Usages candidats : 0.
- [`DummySMTP.starttls`](../../srcs/requirements/app/tests/test_email_report.py#L21) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : aucun appel explicite. Usages candidats : 1.
- [`DummySMTP.login`](../../srcs/requirements/app/tests/test_email_report.py#L24) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : aucun appel explicite. Usages candidats : 1.
- [`DummySMTP.send_message`](../../srcs/requirements/app/tests/test_email_report.py#L27) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : aucun appel explicite. Usages candidats : 1.
- [`test_send_report_email_attaches_pdf`](../../srcs/requirements/app/tests/test_email_report.py#L31) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : DummySMTP, dummy.sent.is_multipart, monkeypatch.setattr, monkeypatch.setenv, pdf.write_bytes, report.write_text, send_report_email, str. Usages candidats : 0.
- [`test_send_report_email_uses_summary_source`](../../srcs/requirements/app/tests/test_email_report.py#L56) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : (tmp_path / 'summary.pdf').exists, DummySMTP, monkeypatch.setattr, monkeypatch.setenv, path.write_bytes, report.write_text, send_report_email, str, summary.write_text. Usages candidats : 0.
- [`test_send_report_email_uses_summary_source.fake_render`](../../srcs/requirements/app/tests/test_email_report.py#L71) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : path.write_bytes. Usages candidats : 0.
- [`test_send_report_email_regenerates_invalid_pdf`](../../srcs/requirements/app/tests/test_email_report.py#L90) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : DummySMTP, bad_pdf.read_bytes, bad_pdf.read_bytes().startswith, bad_pdf.write_bytes, monkeypatch.setattr, monkeypatch.setenv, path.write_bytes, report.write_text, send_report_email, str. Usages candidats : 0.
- [`test_send_report_email_regenerates_invalid_pdf.fake_render`](../../srcs/requirements/app/tests/test_email_report.py#L106) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : path.write_bytes. Usages candidats : 0.
- [`test_send_report_email_forces_pdf_regenerate`](../../srcs/requirements/app/tests/test_email_report.py#L122) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : DummySMTP, monkeypatch.setattr, monkeypatch.setenv, path.write_bytes, pdf.read_bytes, pdf.write_bytes, report.write_text, send_report_email, str. Usages candidats : 0.
- [`test_send_report_email_forces_pdf_regenerate.fake_render`](../../srcs/requirements/app/tests/test_email_report.py#L138) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : path.write_bytes. Usages candidats : 0.

## tests/test_health_summary.py

- [`test_summary_includes_last_run_at`](../../srcs/requirements/app/tests/test_health_summary.py#L4) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : health_summary.summary. Usages candidats : 0.

## tests/test_http_client.py

- [`test_http_client_blocks_when_robots_forbid`](../../srcs/requirements/app/tests/test_http_client.py#L7) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : NetworkPolicy, client.fetch, client_module.HttpClient, importlib.import_module, monkeypatch.setattr. Usages candidats : 0.
- [`test_http_client_applies_max_bytes_override`](../../srcs/requirements/app/tests/test_http_client.py#L27) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : DownloadResult, NetworkPolicy, client.fetch, client_module.HttpClient, importlib.import_module, monkeypatch.setattr. Usages candidats : 0.
- [`test_http_client_applies_max_bytes_override.fake_download_with_context`](../../srcs/requirements/app/tests/test_http_client.py#L32) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : DownloadResult. Usages candidats : 0.
- [`test_request_context_applies_user_agent_and_headers`](../../srcs/requirements/app/tests/test_http_client.py#L52) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : DownloadResult, NetworkPolicy, captured_headers.update, client.fetch, client_module.HttpClient, importlib.import_module, monkeypatch.setattr. Usages candidats : 0.
- [`test_request_context_applies_user_agent_and_headers.fake_download_with_context`](../../srcs/requirements/app/tests/test_http_client.py#L61) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : DownloadResult, captured_headers.update. Usages candidats : 0.
- [`test_http_client_retries_on_http_error`](../../srcs/requirements/app/tests/test_http_client.py#L86) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : DownloadResult, NetworkPolicy, client.fetch, client_module.HttpClient, importlib.import_module, monkeypatch.setattr. Usages candidats : 0.
- [`test_http_client_retries_on_http_error.fake_download_with_context`](../../srcs/requirements/app/tests/test_http_client.py#L90) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : DownloadResult. Usages candidats : 0.
- [`test_http_client_backoff_adaptive`](../../srcs/requirements/app/tests/test_http_client.py#L115) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : DownloadResult, NetworkPolicy, client._backoff_delay, client_module.HttpClient, importlib.import_module. Usages candidats : 0.
- [`test_http_client_headless_shortcuts_download`](../../srcs/requirements/app/tests/test_http_client.py#L131) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : DownloadResult, FakeHeadlessStrategy, NetworkPolicy, client.fetch, client_module.HttpClient, importlib.import_module, monkeypatch.setattr. Usages candidats : 0.
- [`test_http_client_headless_shortcuts_download.FakeHeadlessStrategy.fetch`](../../srcs/requirements/app/tests/test_http_client.py#L138) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : aucun appel explicite. Usages candidats : 20.
- [`test_http_client_headless_shortcuts_download.fake_download_with_context`](../../srcs/requirements/app/tests/test_http_client.py#L142) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : DownloadResult. Usages candidats : 0.
- [`test_http_client_enforces_max_bytes_stream`](../../srcs/requirements/app/tests/test_http_client.py#L164) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : FakeResponse, NetworkPolicy, client.fetch, client_module.HttpClient, importlib.import_module, len, monkeypatch.setattr, range, str. Usages candidats : 0.
- [`test_http_client_enforces_max_bytes_stream.FakeResponse.__init__`](../../srcs/requirements/app/tests/test_http_client.py#L169) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : len, str. Usages candidats : 0.
- [`test_http_client_enforces_max_bytes_stream.FakeResponse.raise_for_status`](../../srcs/requirements/app/tests/test_http_client.py#L176) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : aucun appel explicite. Usages candidats : 3.
- [`test_http_client_enforces_max_bytes_stream.FakeResponse.iter_content`](../../srcs/requirements/app/tests/test_http_client.py#L179) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : len, range. Usages candidats : 2.
- [`test_http_client_enforces_max_bytes_stream.FakeResponse.close`](../../srcs/requirements/app/tests/test_http_client.py#L184) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : aucun appel explicite. Usages candidats : 9.
- [`test_http_client_enforces_max_bytes_stream.fake_get`](../../srcs/requirements/app/tests/test_http_client.py#L187) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : FakeResponse. Usages candidats : 0.
- [`test_http_client_uses_proxies_round_robin`](../../srcs/requirements/app/tests/test_http_client.py#L206) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : DownloadResult, NetworkPolicy, captured.append, client.fetch, client_module.HttpClient, importlib.import_module, monkeypatch.setattr. Usages candidats : 0.
- [`test_http_client_uses_proxies_round_robin.fake_download_with_context`](../../srcs/requirements/app/tests/test_http_client.py#L210) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : DownloadResult, captured.append. Usages candidats : 0.
- [`test_http_client_respect_robots_override`](../../srcs/requirements/app/tests/test_http_client.py#L233) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : DownloadResult, NetworkPolicy, calls['allowed'].append, client.fetch, client_module.HttpClient, importlib.import_module, monkeypatch.setattr. Usages candidats : 0.
- [`test_http_client_respect_robots_override.fake_is_allowed`](../../srcs/requirements/app/tests/test_http_client.py#L237) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : calls['allowed'].append. Usages candidats : 0.
- [`test_http_client_respect_robots_override.fake_download_with_context`](../../srcs/requirements/app/tests/test_http_client.py#L244) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : DownloadResult. Usages candidats : 0.
- [`test_http_client_blocks_private_dns_resolution`](../../srcs/requirements/app/tests/test_http_client.py#L262) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : (res.error or '').lower, NetworkPolicy, client.fetch, client_module.HttpClient, importlib.import_module, monkeypatch.setattr. Usages candidats : 0.
- [`test_http_client_user_agent_and_proxy_increment_thread_safe`](../../srcs/requirements/app/tests/test_http_client.py#L285) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : NetworkPolicy, ThreadPoolExecutor, client._next_proxy, client._next_user_agent, client_module.HttpClient, executor.map, importlib.import_module, list, range. Usages candidats : 0.

## tests/test_keywords.py

- [`test_find_keyword_hits_basic`](../../srcs/requirements/app/tests/test_keywords.py#L4) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : find_keyword_hits. Usages candidats : 0.
- [`test_find_keyword_hits_handles_noise_and_case`](../../srcs/requirements/app/tests/test_keywords.py#L14) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : find_keyword_hits, set. Usages candidats : 0.
- [`test_shared_terms_preserve_categories_spelling_and_order`](../../srcs/requirements/app/tests/test_keywords.py#L24) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : find_keyword_hits, iter, list. Usages candidats : 0.

## tests/test_load_config.py

- [`sample_yaml_file`](../../srcs/requirements/app/tests/test_load_config.py#L11) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : yaml_path.parent.mkdir, yaml_path.write_text. Usages candidats : 0.
- [`sample_keyword_file`](../../srcs/requirements/app/tests/test_load_config.py#L23) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : json.dumps, json_path.parent.mkdir, json_path.write_text. Usages candidats : 0.
- [`test_load_yaml_config`](../../srcs/requirements/app/tests/test_load_config.py#L33) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : config.get, isinstance, load_yaml_config. Usages candidats : 0.
- [`test_get_config_as_json_string`](../../srcs/requirements/app/tests/test_load_config.py#L38) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : get_config_as_json_string, isinstance. Usages candidats : 0.
- [`test_load_keywords_from_config`](../../srcs/requirements/app/tests/test_load_config.py#L44) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : isinstance, load_keywords_from_config, load_yaml_config, yaml_path.parent.mkdir, yaml_path.write_text. Usages candidats : 0.
- [`test_load_keywords_from_config_with_fallback`](../../srcs/requirements/app/tests/test_load_config.py#L55) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : fallback_file.parent.mkdir, fallback_file.write_text, json.dumps, load_keywords_from_config. Usages candidats : 0.
- [`test_load_yaml_config_with_include`](../../srcs/requirements/app/tests/test_load_config.py#L67) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : conf_path.parent.mkdir, conf_path.write_text, include_path.parent.mkdir, include_path.write_text, load_yaml_config. Usages candidats : 0.
- [`test_load_yaml_config_merges_lists`](../../srcs/requirements/app/tests/test_load_config.py#L104) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : conf_path.parent.mkdir, conf_path.write_text, include_path.parent.mkdir, include_path.write_text, load_yaml_config. Usages candidats : 0.

## tests/test_metrics.py

- [`test_record_fetch_tracks_status_reason_and_bytes`](../../srcs/requirements/app/tests/test_metrics.py#L5) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : metrics._load_health, metrics.record_fetch. Usages candidats : 0.

## tests/test_ollama_provider.py

- [`sources`](../../srcs/requirements/app/tests/test_ollama_provider.py#L12) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : json.dumps. Usages candidats : 8.
- [`finding`](../../srcs/requirements/app/tests/test_ollama_provider.py#L18) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : aucun appel explicite. Usages candidats : 4.
- [`Response.__init__`](../../srcs/requirements/app/tests/test_ollama_provider.py#L27) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : aucun appel explicite. Usages candidats : 0.
- [`Response.__enter__`](../../srcs/requirements/app/tests/test_ollama_provider.py#L30) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : aucun appel explicite. Usages candidats : 0.
- [`Response.__exit__`](../../srcs/requirements/app/tests/test_ollama_provider.py#L33) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : aucun appel explicite. Usages candidats : 0.
- [`Response.raise_for_status`](../../srcs/requirements/app/tests/test_ollama_provider.py#L36) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : aucun appel explicite. Usages candidats : 3.
- [`Response.json`](../../srcs/requirements/app/tests/test_ollama_provider.py#L39) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : aucun appel explicite. Usages candidats : 4.
- [`Session.__init__`](../../srcs/requirements/app/tests/test_ollama_provider.py#L44) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : aucun appel explicite. Usages candidats : 0.
- [`Session.post`](../../srcs/requirements/app/tests/test_ollama_provider.py#L48) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : Response, json.JSONDecoder, json.JSONDecoder().raw_decode, json.dumps, self.calls.append. Usages candidats : 3.
- [`test_valid_report_archives_and_preserves_technical_report`](../../srcs/requirements/app/tests/test_ollama_provider.py#L58) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : (archive / 'report.md').read_bytes, (archive / name).exists, OllamaProvider, OllamaProvider(session).generate, Session, all, hashlib.sha256, hashlib.sha256((archive / 'report.md').read_bytes()).hexdigest, hashlib.sha256(path.read_bytes()).hexdigest, json.loads, monkeypatch.setenv, path.read_bytes, path.read_text, path.with_suffix, path.with_suffix('.quality.json').read_text, sources, str, technical.read_text, technical.write_text. Usages candidats : 0.
- [`test_invalid_output_is_not_published_as_valid`](../../srcs/requirements/app/tests/test_ollama_provider.py#L78) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : OllamaProvider, OllamaProvider(Session(reason, corrupt)).generate, Session, json.loads, path.read_text, path.with_suffix, path.with_suffix('.quality.json').read_text, pytest.mark.parametrize, sources, str. Usages candidats : 0.
- [`test_no_evidence_does_not_call_model`](../../srcs/requirements/app/tests/test_ollama_provider.py#L86) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : OllamaProvider, OllamaProvider(session).generate, Session, json.loads, path.with_suffix, path.with_suffix('.quality.json').read_text, str. Usages candidats : 0.
- [`test_rejects_invented_identifier_and_quote`](../../srcs/requirements/app/tests/test_ollama_provider.py#L93) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : build_evidence, finding, len, sources, validate_findings. Usages candidats : 0.
- [`test_schema_limits_apply_even_if_model_ignores_them`](../../srcs/requirements/app/tests/test_ollama_provider.py#L102) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : build_evidence, finding, sources, validate_findings. Usages candidats : 0.
- [`test_quotes_are_copied_by_code_not_rewritten_by_model`](../../srcs/requirements/app/tests/test_ollama_provider.py#L111) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : build_evidence, pytest.raises, resolve_decisions, sources, validate_findings. Usages candidats : 0.
- [`test_untranslated_summary_is_rejected`](../../srcs/requirements/app/tests/test_ollama_provider.py#L126) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : any, build_evidence, finding, sources, validate_findings. Usages candidats : 0.
- [`test_csv_preserves_headers_comments_sort_and_bom`](../../srcs/requirements/app/tests/test_ollama_provider.py#L133) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : json.loads, parse_content. Usages candidats : 0.
- [`test_stix_excludes_deprecated_and_remains_reference`](../../srcs/requirements/app/tests/test_ollama_provider.py#L140) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : build_evidence, json.dumps, len, parse_content. Usages candidats : 0.
- [`test_unknown_ransomware_is_not_positive_and_sources_are_diverse`](../../srcs/requirements/app/tests/test_ollama_provider.py#L153) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : build_evidence, len, select_evidence, sources. Usages candidats : 0.
- [`test_exports_exist_even_without_high_priority`](../../srcs/requirements/app/tests/test_ollama_provider.py#L161) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : (tmp_path / 'iocs.csv').read_text, (tmp_path / 'iocs.csv').read_text().splitlines, (tmp_path / 'iocs.json').exists, (tmp_path / 'summary.md').exists, sources, str, write_report. Usages candidats : 0.
- [`test_cache_expiry_preserves_offline_replay`](../../srcs/requirements/app/tests/test_ollama_provider.py#L168) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : SimpleNamespace, datetime.now, datetime.now(timezone.utc).isoformat, object.__new__, scraper._cache_is_fresh. Usages candidats : 0.
- [`test_old_c2_is_explicitly_historical`](../../srcs/requirements/app/tests/test_ollama_provider.py#L183) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : build_evidence, json.dumps. Usages candidats : 0.
- [`test_yara_distinguishes_reference_data_from_active_formats`](../../srcs/requirements/app/tests/test_ollama_provider.py#L197) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : Path, Path(__file__).resolve, bool, path.write_text, pytest.mark.parametrize, pytest.skip, run_scan, shutil.which. Usages candidats : 0.

## tests/test_overrides.py

- [`test_normalize_overrides_headers_and_user_agent`](../../srcs/requirements/app/tests/test_overrides.py#L4) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : normalize_overrides. Usages candidats : 0.
- [`test_merge_headers_applies_user_agent_and_overrides`](../../srcs/requirements/app/tests/test_overrides.py#L21) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : merge_headers. Usages candidats : 0.

## tests/test_parser_configurable.py

- [`test_parse_content_deduplicate_and_limit`](../../srcs/requirements/app/tests/test_parser_configurable.py#L4) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : parser.parse_content. Usages candidats : 0.
- [`test_parse_json_uses_jsonpath_and_limit`](../../srcs/requirements/app/tests/test_parser_configurable.py#L20) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : parser.parse_content. Usages candidats : 0.
- [`test_parse_xml_supports_extract_tags_dicts`](../../srcs/requirements/app/tests/test_parser_configurable.py#L29) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : parser.parse_content. Usages candidats : 0.
- [`test_extract_iocs_enabled`](../../srcs/requirements/app/tests/test_parser_configurable.py#L37) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : parser.parse_content. Usages candidats : 0.
- [`test_sanitize_html_and_xml`](../../srcs/requirements/app/tests/test_parser_configurable.py#L46) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : all, any, parser.parse_content. Usages candidats : 0.
- [`test_custom_parser_registry_injection`](../../srcs/requirements/app/tests/test_parser_configurable.py#L60) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : parser.ParserRegistry, parser.parse_content, registry.register. Usages candidats : 0.
- [`test_custom_parser_registry_injection.fake_parser`](../../srcs/requirements/app/tests/test_parser_configurable.py#L63) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : aucun appel explicite. Usages candidats : 0.
- [`test_min_chars_filters_short_items`](../../srcs/requirements/app/tests/test_parser_configurable.py#L75) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : parser.parse_content. Usages candidats : 0.

## tests/test_parser_cvss.py

- [`test_cvss_extraction_from_api_results`](../../srcs/requirements/app/tests/test_parser_cvss.py#L4) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : any, item.startswith, parser.parse_content. Usages candidats : 0.

## tests/test_parsers_pdf_ocr.py

- [`_png_with_text`](../../srcs/requirements/app/tests/test_parsers_pdf_ocr.py#L7) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : BytesIO, Image.new, ImageDraw.Draw, buf.getvalue, draw.text, img.save. Usages candidats : 2.
- [`test_parse_pdf_extracts_text_and_images`](../../srcs/requirements/app/tests/test_parsers_pdf_ocr.py#L16) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : DummyPage, DummyPdf, all, any, monkeypatch.setattr, pdf_parser.parse_pdf, types.SimpleNamespace. Usages candidats : 0.
- [`test_parse_pdf_extracts_text_and_images.DummyPage.__init__`](../../srcs/requirements/app/tests/test_parsers_pdf_ocr.py#L18) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : aucun appel explicite. Usages candidats : 0.
- [`test_parse_pdf_extracts_text_and_images.DummyPage.extract_text`](../../srcs/requirements/app/tests/test_parsers_pdf_ocr.py#L22) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : aucun appel explicite. Usages candidats : 1.
- [`test_parse_pdf_extracts_text_and_images.DummyPdf.__init__`](../../srcs/requirements/app/tests/test_parsers_pdf_ocr.py#L26) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : aucun appel explicite. Usages candidats : 0.
- [`test_parse_pdf_extracts_text_and_images.DummyPdf.__enter__`](../../srcs/requirements/app/tests/test_parsers_pdf_ocr.py#L29) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : aucun appel explicite. Usages candidats : 0.
- [`test_parse_pdf_extracts_text_and_images.DummyPdf.__exit__`](../../srcs/requirements/app/tests/test_parsers_pdf_ocr.py#L32) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : aucun appel explicite. Usages candidats : 0.
- [`test_parse_pdf_extracts_text_and_images.fake_open`](../../srcs/requirements/app/tests/test_parsers_pdf_ocr.py#L37) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : aucun appel explicite. Usages candidats : 0.
- [`test_parse_pdf_gracefully_handles_missing_library`](../../srcs/requirements/app/tests/test_parsers_pdf_ocr.py#L52) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : monkeypatch.setattr, pdf_parser.parse_pdf. Usages candidats : 0.
- [`test_parse_pdf_respects_max_total_chars`](../../srcs/requirements/app/tests/test_parsers_pdf_ocr.py#L57) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : DummyPage, DummyPdf, monkeypatch.setattr, pdf_parser.parse_pdf, types.SimpleNamespace. Usages candidats : 0.
- [`test_parse_pdf_respects_max_total_chars.DummyPage.__init__`](../../srcs/requirements/app/tests/test_parsers_pdf_ocr.py#L59) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : aucun appel explicite. Usages candidats : 0.
- [`test_parse_pdf_respects_max_total_chars.DummyPage.extract_text`](../../srcs/requirements/app/tests/test_parsers_pdf_ocr.py#L63) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : aucun appel explicite. Usages candidats : 1.
- [`test_parse_pdf_respects_max_total_chars.DummyPdf.__init__`](../../srcs/requirements/app/tests/test_parsers_pdf_ocr.py#L67) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : aucun appel explicite. Usages candidats : 0.
- [`test_parse_pdf_respects_max_total_chars.DummyPdf.__enter__`](../../srcs/requirements/app/tests/test_parsers_pdf_ocr.py#L70) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : aucun appel explicite. Usages candidats : 0.
- [`test_parse_pdf_respects_max_total_chars.DummyPdf.__exit__`](../../srcs/requirements/app/tests/test_parsers_pdf_ocr.py#L73) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : aucun appel explicite. Usages candidats : 0.
- [`test_parse_pdf_respects_max_total_chars.fake_open`](../../srcs/requirements/app/tests/test_parsers_pdf_ocr.py#L78) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : aucun appel explicite. Usages candidats : 0.
- [`test_parse_image_uses_languages_and_limits`](../../srcs/requirements/app/tests/test_parsers_pdf_ocr.py#L88) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : _png_with_text, monkeypatch.setattr, ocr_parser.parse_image, types.SimpleNamespace. Usages candidats : 0.
- [`test_parse_image_uses_languages_and_limits.fake_ocr`](../../srcs/requirements/app/tests/test_parsers_pdf_ocr.py#L91) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : aucun appel explicite. Usages candidats : 0.
- [`test_parse_image_handles_missing_binary`](../../srcs/requirements/app/tests/test_parsers_pdf_ocr.py#L103) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : DummyPytesseract, _png_with_text, monkeypatch.setattr, ocr_parser.parse_image, self.TesseractNotFoundError. Usages candidats : 0.
- [`test_parse_image_handles_missing_binary.DummyPytesseract.image_to_string`](../../srcs/requirements/app/tests/test_parsers_pdf_ocr.py#L108) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : self.TesseractNotFoundError. Usages candidats : 1.

## tests/test_parsers_text.py

- [`test_ensure_text_handles_bytes_and_newlines`](../../srcs/requirements/app/tests/test_parsers_text.py#L5) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : ensure_text. Usages candidats : 0.
- [`test_safe_json_load_with_invalid_json_returns_none`](../../srcs/requirements/app/tests/test_parsers_text.py#L10) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : safe_json_load. Usages candidats : 0.
- [`test_safe_csv_rows_parses_delimiter_and_encoding`](../../srcs/requirements/app/tests/test_parsers_text.py#L14) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : safe_csv_rows. Usages candidats : 0.
- [`test_parse_content_handles_bytes_for_api_and_csv`](../../srcs/requirements/app/tests/test_parsers_text.py#L20) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : parse_content. Usages candidats : 0.

## tests/test_pdf_export.py

- [`DummyPDF.__init__`](../../srcs/requirements/app/tests/test_pdf_export.py#L8) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : aucun appel explicite. Usages candidats : 0.
- [`DummyPDF.set_auto_page_break`](../../srcs/requirements/app/tests/test_pdf_export.py#L15) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : aucun appel explicite. Usages candidats : 1.
- [`DummyPDF.set_margins`](../../srcs/requirements/app/tests/test_pdf_export.py#L18) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : aucun appel explicite. Usages candidats : 1.
- [`DummyPDF.add_page`](../../srcs/requirements/app/tests/test_pdf_export.py#L21) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : aucun appel explicite. Usages candidats : 6.
- [`DummyPDF.set_font`](../../srcs/requirements/app/tests/test_pdf_export.py#L24) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : aucun appel explicite. Usages candidats : 16.
- [`DummyPDF.multi_cell`](../../srcs/requirements/app/tests/test_pdf_export.py#L27) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : len, self.lines.append. Usages candidats : 1.
- [`DummyPDF.cell`](../../srcs/requirements/app/tests/test_pdf_export.py#L31) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : len, self.lines.append. Usages candidats : 10.
- [`DummyPDF.ln`](../../srcs/requirements/app/tests/test_pdf_export.py#L35) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : aucun appel explicite. Usages candidats : 12.
- [`DummyPDF.set_x`](../../srcs/requirements/app/tests/test_pdf_export.py#L38) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : aucun appel explicite. Usages candidats : 2.
- [`DummyPDF.get_string_width`](../../srcs/requirements/app/tests/test_pdf_export.py#L41) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : len. Usages candidats : 10.
- [`DummyPDF.output`](../../srcs/requirements/app/tests/test_pdf_export.py#L44) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : Path, Path(path).write_bytes. Usages candidats : 2.
- [`test_render_markdown_to_pdf_writes_file`](../../srcs/requirements/app/tests/test_pdf_export.py#L48) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : monkeypatch.setattr, out.exists, pdf_export.render_markdown_to_pdf. Usages candidats : 0.
- [`test_render_markdown_to_pdf_sanitizes_table_lines`](../../srcs/requirements/app/tests/test_pdf_export.py#L57) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : monkeypatch.setattr, out.exists, pdf_export.render_markdown_to_pdf. Usages candidats : 0.
- [`test_render_markdown_to_pdf_handles_unicode_dash`](../../srcs/requirements/app/tests/test_pdf_export.py#L66) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : monkeypatch.setattr, out.exists, pdf_export.render_markdown_to_pdf. Usages candidats : 0.
- [`test_render_markdown_to_pdf_strips_bold_headings`](../../srcs/requirements/app/tests/test_pdf_export.py#L75) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : monkeypatch.setattr, out.exists, pdf_export.render_markdown_to_pdf. Usages candidats : 0.

## tests/test_preflight.py

- [`test_preflight_collects_required_env`](../../srcs/requirements/app/tests/test_preflight.py#L4) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : collect_required_env. Usages candidats : 0.
- [`test_preflight_collects_alerting_env_when_required`](../../srcs/requirements/app/tests/test_preflight.py#L17) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : collect_required_env, dict. Usages candidats : 0.
- [`test_preflight_scopes_auth_env_to_sources`](../../srcs/requirements/app/tests/test_preflight.py#L26) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : collect_required_env, dict. Usages candidats : 0.
- [`test_preflight_blocks_when_missing`](../../srcs/requirements/app/tests/test_preflight.py#L42) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : check_env_requirements, monkeypatch.delenv. Usages candidats : 0.
- [`test_preflight_passes_when_present`](../../srcs/requirements/app/tests/test_preflight.py#L59) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : check_env_requirements, monkeypatch.setenv. Usages candidats : 0.
- [`test_preflight_flags_invalid_alerting_env`](../../srcs/requirements/app/tests/test_preflight.py#L72) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : check_env_requirements, dict, monkeypatch.setenv. Usages candidats : 0.

## tests/test_quota.py

- [`test_quota_pages_and_bytes`](../../srcs/requirements/app/tests/test_quota.py#L4) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : Quota, q.add_bytes, q.reserve_page. Usages candidats : 0.

## tests/test_report_writer.py

- [`_sample_results`](../../srcs/requirements/app/tests/test_report_writer.py#L7) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : aucun appel explicite. Usages candidats : 3.
- [`test_markdown_skipped_cache_keeps_existing`](../../srcs/requirements/app/tests/test_report_writer.py#L15) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : ReportWriter, _sample_results, existing.parent.mkdir, existing.read_text, existing.write_text, writer.write. Usages candidats : 0.
- [`test_json_report_creates_detail_and_main`](../../srcs/requirements/app/tests/test_report_writer.py#L27) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : ReportWriter, _sample_results, detail.exists, path.exists, writer.write. Usages candidats : 0.
- [`test_markdown_detail_includes_keywords`](../../srcs/requirements/app/tests/test_report_writer.py#L36) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : ReportWriter, detail.read_text, writer.write. Usages candidats : 0.
- [`test_markdown_main_includes_keywords_when_no_split`](../../srcs/requirements/app/tests/test_report_writer.py#L58) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : ReportWriter, main.read_text, writer.write. Usages candidats : 0.
- [`test_ai_report_writes_file`](../../srcs/requirements/app/tests/test_report_writer.py#L78) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : generate_ai_report, monkeypatch.setattr, out.read_text. Usages candidats : 0.
- [`test_ai_report_writes_file.fake_run`](../../srcs/requirements/app/tests/test_report_writer.py#L81) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : aucun appel explicite. Usages candidats : 0.
- [`test_ai_report_disabled_returns_none`](../../srcs/requirements/app/tests/test_report_writer.py#L95) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : generate_ai_report. Usages candidats : 0.
- [`test_ai_report_autodetect_returns_none_if_not_found`](../../srcs/requirements/app/tests/test_report_writer.py#L100) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : generate_ai_report, monkeypatch.setattr. Usages candidats : 0.
- [`test_ai_report_prompt_path`](../../srcs/requirements/app/tests/test_report_writer.py#L106) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : generate_ai_report, monkeypatch.setattr, prompt_file.write_text. Usages candidats : 0.
- [`test_ai_report_autodetect_codex`](../../srcs/requirements/app/tests/test_report_writer.py#L118) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : generate_ai_report, monkeypatch.setattr. Usages candidats : 0.
- [`test_ai_report_autodetect_codex.fake_which`](../../srcs/requirements/app/tests/test_report_writer.py#L120) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : aucun appel explicite. Usages candidats : 0.
- [`test_report_writer_additional_formats`](../../srcs/requirements/app/tests/test_report_writer.py#L129) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : (tmp_path / 'report.json').exists, (tmp_path / 'report.md').exists, (tmp_path / 'sources' / 'json' / 'root.json').exists, ReportWriter, _sample_results, writer.write. Usages candidats : 0.

## tests/test_result_recorder.py

- [`DummyResultStore.__init__`](../../srcs/requirements/app/tests/test_result_recorder.py#L8) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : aucun appel explicite. Usages candidats : 0.
- [`DummyResultStore.save`](../../srcs/requirements/app/tests/test_result_recorder.py#L11) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : self.saved.append. Usages candidats : 5.
- [`test_result_recorder_includes_run_meta`](../../srcs/requirements/app/tests/test_result_recorder.py#L15) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : CacheManager, DownloadResult, DummyResultStore, ResultRecorder, Source, recorder.record_result. Usages candidats : 0.

## tests/test_runner_allowlist.py

- [`DummySource.__init__`](../../srcs/requirements/app/tests/test_runner_allowlist.py#L7) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : aucun appel explicite. Usages candidats : 0.
- [`DummyLogger.__init__`](../../srcs/requirements/app/tests/test_runner_allowlist.py#L14) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : aucun appel explicite. Usages candidats : 0.
- [`DummyLogger.error`](../../srcs/requirements/app/tests/test_runner_allowlist.py#L17) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : self.errors.append. Usages candidats : 12.
- [`DummyLogger.warning`](../../srcs/requirements/app/tests/test_runner_allowlist.py#L20) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : aucun appel explicite. Usages candidats : 22.
- [`DummyConfig.__init__`](../../srcs/requirements/app/tests/test_runner_allowlist.py#L25) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : set, type, type('NP', (), {'allow_domains': allow_domains}). Usages candidats : 0.
- [`test_validate_allowlist_accepts_in_scope`](../../srcs/requirements/app/tests/test_runner_allowlist.py#L32) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : DummyConfig, DummyLogger, DummySource, _validate_allowlist. Usages candidats : 0.
- [`test_validate_allowlist_rejects_out_of_scope`](../../srcs/requirements/app/tests/test_runner_allowlist.py#L39) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : DummyConfig, DummyLogger, DummySource, _validate_allowlist, any. Usages candidats : 0.
- [`test_validate_allowlist_requires_allowlist_when_configured`](../../srcs/requirements/app/tests/test_runner_allowlist.py#L46) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : DummyConfig, DummyLogger, DummySource, _validate_allowlist, any, set. Usages candidats : 0.

## tests/test_scanner.py

- [`test_run_scan_success`](../../srcs/requirements/app/tests/test_scanner.py#L5) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : f.write_text, run_scan. Usages candidats : 0.
- [`test_run_scan_failure`](../../srcs/requirements/app/tests/test_scanner.py#L12) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : f.write_text, run_scan. Usages candidats : 0.

## tests/test_scheduling.py

- [`test_parse_interval_seconds_variants`](../../srcs/requirements/app/tests/test_scheduling.py#L6) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : parse_interval_seconds. Usages candidats : 0.
- [`test_compute_initial_delay_future_and_past`](../../srcs/requirements/app/tests/test_scheduling.py#L14) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : compute_initial_delay, dt.datetime. Usages candidats : 0.
- [`test_compute_initial_delay_with_timezone_keeps_expected_gap`](../../srcs/requirements/app/tests/test_scheduling.py#L24) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : compute_initial_delay, dt.datetime. Usages candidats : 0.
- [`test_compute_initial_delay_same_minute_is_zero`](../../srcs/requirements/app/tests/test_scheduling.py#L30) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : compute_initial_delay, dt.datetime. Usages candidats : 0.
- [`test_load_schedule_config_defaults`](../../srcs/requirements/app/tests/test_scheduling.py#L36) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : load_schedule_config. Usages candidats : 0.

## tests/test_scorer.py

- [`test_score_results_adds_priority_and_keeps_input_intact`](../../srcs/requirements/app/tests/test_scorer.py#L4) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : len, score_results. Usages candidats : 0.
- [`test_compute_confidence_reflects_status_and_extracted`](../../srcs/requirements/app/tests/test_scorer.py#L21) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : compute_confidence. Usages candidats : 0.

## tests/test_scraper.py

- [`test_scraper_download_and_cache`](../../srcs/requirements/app/tests/test_scraper.py#L7) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : CacheManager, cache.get, dummy_config_model, fake_client_factory, importlib.import_module, len, scraper.run, scraper_module.Scraper, source_module.Source. Usages candidats : 0.
- [`test_scraper_uses_cache`](../../srcs/requirements/app/tests/test_scraper.py#L27) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : CacheEntry, CacheManager, cache.get, cache.update, dummy_config_model, fake_client_factory, importlib.import_module, len, scraper.run, scraper_module.Scraper, source_module.Source. Usages candidats : 0.
- [`test_scraper_cache_hit_parses_saved_content`](../../srcs/requirements/app/tests/test_scraper.py#L47) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : ' '.join, CacheEntry, CacheManager, by_url[root_url].get, cache.update, dummy_config_model, fake_client_factory, importlib.import_module, len, saved_path.write_text, scraper.run, scraper_module.Scraper, source_module.Source, str. Usages candidats : 0.
- [`test_scraper_offline_without_cache_marks_offline`](../../srcs/requirements/app/tests/test_scraper.py#L70) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : CacheManager, dummy_config_model, fake_client_factory, importlib.import_module, len, scraper.run, scraper_module.Scraper, source_module.Source. Usages candidats : 0.
- [`test_scraper_concurrent_workers`](../../srcs/requirements/app/tests/test_scraper.py#L90) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : CacheManager, cache.get, dummy_config_model, fake_client_factory, importlib.import_module, scraper.run, scraper_module.Scraper, set, source_module.Source. Usages candidats : 0.
- [`test_scraper_e2e_multi_sources_with_overrides`](../../srcs/requirements/app/tests/test_scraper.py#L110) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : CacheManager, DownloadResult, MultiFakeClient, cache.get, content_map.get, dummy_config_model, importlib.import_module, scraper.run, scraper_module.Scraper, self.calls.append, source.get, source_module.Source. Usages candidats : 0.
- [`test_scraper_e2e_multi_sources_with_overrides.MultiFakeClient.__init__`](../../srcs/requirements/app/tests/test_scraper.py#L128) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : aucun appel explicite. Usages candidats : 0.
- [`test_scraper_e2e_multi_sources_with_overrides.MultiFakeClient.fetch`](../../srcs/requirements/app/tests/test_scraper.py#L131) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : DownloadResult, content_map.get, self.calls.append, source.get. Usages candidats : 20.
- [`test_scraper_records_keyword_hits`](../../srcs/requirements/app/tests/test_scraper.py#L152) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : CacheManager, by_url[child_url].get, by_url[root_url].get, dummy_config_model, fake_client_factory, importlib.import_module, scraper.run, scraper_module.Scraper, source_module.Source. Usages candidats : 0.
- [`test_scraper_respects_global_page_quota`](../../srcs/requirements/app/tests/test_scraper.py#L178) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : CacheManager, dummy_config_model, fake_client_factory, importlib.import_module, scraper.run, scraper_module.Scraper, source_module.Source. Usages candidats : 0.

## tests/test_source.py

- [`_get_source_module`](../../srcs/requirements/app/tests/test_source.py#L7) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : importlib.import_module. Usages candidats : 4.
- [`test_download_manager_downloaded`](../../srcs/requirements/app/tests/test_source.py#L11) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : NetworkPolicy, Path, Source, StorageTarget, _get_source_module, monkeypatch.setattr, source_module.DownloadResult, source_module.compute_sha256_from_text, src.download_manager. Usages candidats : 0.
- [`test_download_manager_downloaded.fake_download_source`](../../srcs/requirements/app/tests/test_source.py#L17) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : source_module.DownloadResult. Usages candidats : 0.
- [`test_download_manager_error`](../../srcs/requirements/app/tests/test_source.py#L35) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : NetworkPolicy, Path, Source, StorageTarget, _get_source_module, monkeypatch.setattr, source_module.DownloadResult, src.download_manager. Usages candidats : 0.
- [`test_download_manager_error.fake_download_source`](../../srcs/requirements/app/tests/test_source.py#L41) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : source_module.DownloadResult. Usages candidats : 0.
- [`test_download_manager_skipped`](../../srcs/requirements/app/tests/test_source.py#L60) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : NetworkPolicy, Path, Source, StorageTarget, _get_source_module, monkeypatch.setattr, source_module.DownloadResult, src.download_manager. Usages candidats : 0.
- [`test_download_manager_skipped.fake_download_source`](../../srcs/requirements/app/tests/test_source.py#L66) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : source_module.DownloadResult. Usages candidats : 0.
- [`test_download_manager_binary_hash`](../../srcs/requirements/app/tests/test_source.py#L79) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : NetworkPolicy, Path, Source, StorageTarget, _get_source_module, hashlib.sha256, hashlib.sha256(binary_payload).hexdigest, monkeypatch.setattr, source_module.DownloadResult, src.download_manager. Usages candidats : 0.
- [`test_download_manager_binary_hash.fake_download_source`](../../srcs/requirements/app/tests/test_source.py#L86) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : source_module.DownloadResult. Usages candidats : 0.

## tests/test_sources_factory.py

- [`test_normalize_overrides_handles_numeric_and_bool_strings`](../../srcs/requirements/app/tests/test_sources_factory.py#L4) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : normalize_overrides. Usages candidats : 0.
- [`test_normalize_overrides_drops_invalid_values`](../../srcs/requirements/app/tests/test_sources_factory.py#L12) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : normalize_overrides. Usages candidats : 0.

## tests/test_storage_mongo.py

- [`DummyColl.insert_one`](../../srcs/requirements/app/tests/test_storage_mongo.py#L5) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : aucun appel explicite. Usages candidats : 2.
- [`test_save_result_does_not_mutate_original`](../../srcs/requirements/app/tests/test_storage_mongo.py#L10) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : DummyColl, monkeypatch.setattr, storage_mongo.save_result. Usages candidats : 0.
- [`test_save_result_does_not_mutate_original.fake_get_collection`](../../srcs/requirements/app/tests/test_storage_mongo.py#L13) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : DummyColl. Usages candidats : 0.

## tests/test_storage_mongo_mock.py

- [`test_save_result_with_mongomock`](../../srcs/requirements/app/tests/test_storage_mongo_mock.py#L8) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : coll.find, len, list, mongomock.MongoClient, monkeypatch.setattr, monkeypatch.setenv, storage_mongo.save_result. Usages candidats : 0.

## tests/test_validators.py

- [`test_validate_output_format_and_ai_report_dict`](../../srcs/requirements/app/tests/test_validators.py#L6) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : validate_output. Usages candidats : 0.
- [`test_resolve_normalizer_options`](../../srcs/requirements/app/tests/test_validators.py#L15) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : resolve_normalizer, resolve_normalizer('lower'), resolve_normalizer('strip'), resolve_normalizer('strip-lower'), validate_crawler. Usages candidats : 0.
- [`test_validate_auth_hosts_structure`](../../srcs/requirements/app/tests/test_validators.py#L23) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : validate_auth. Usages candidats : 0.

## tools/__init__.py


## tools/auth.py

- [`_apply_env`](../../srcs/requirements/app/tools/auth.py#L12) — Remplace les tokens ${VAR} par la valeur d'environnement correspondante si présente. Supporte les str/dict/list récursivement, laisse intact si env manquant.
  Appels effectués : ENV_PATTERN.sub, _apply_env, isinstance, match.group, os.getenv, value.items. Usages candidats : 3.
- [`_apply_env.repl`](../../srcs/requirements/app/tools/auth.py#L18) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : match.group, os.getenv. Usages candidats : 0.
- [`load_auth`](../../srcs/requirements/app/tools/auth.py#L29) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : Path, Path(path).read_text, _apply_env, data.get, isinstance, yaml.safe_load. Usages candidats : 2.
- [`build_headers`](../../srcs/requirements/app/tools/auth.py#L40) — Fusionne les headers globaux et spécifiques au host (configurables dans auth.yaml). auth_conf peut contenir une clé 'headers' globale et une section 'hosts' avec des entrées par domaine.
  Appels effectués : auth_conf.get, dict, hosts_section.get, isinstance, merged.items, merged.update, urlparse. Usages candidats : 3.

## tools/cache.py

- [`CacheEntry.from_dict`](../../srcs/requirements/app/tools/cache.py#L23) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : cls, data.get. Usages candidats : 2.
- [`CacheEntry.to_dict`](../../srcs/requirements/app/tools/cache.py#L36) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : asdict. Usages candidats : 6.
- [`CacheManager.__init__`](../../srcs/requirements/app/tools/cache.py#L41) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : Path, self._load, threading.Lock. Usages candidats : 0.
- [`CacheManager._load`](../../srcs/requirements/app/tools/cache.py#L48) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : CacheEntry.from_dict, data.items, isinstance, json.loads, self.cache_path.exists, self.cache_path.read_text. Usages candidats : 1.
- [`CacheManager.save`](../../srcs/requirements/app/tools/cache.py#L65) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : entry.to_dict, json.dumps, self._entries.items, self.cache_path.parent.mkdir, self.cache_path.write_text. Usages candidats : 5.
- [`CacheManager.stats`](../../srcs/requirements/app/tools/cache.py#L71) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : len, str. Usages candidats : 4.
- [`CacheManager.get`](../../srcs/requirements/app/tools/cache.py#L76) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : self._entries.get. Usages candidats : 582.
- [`CacheManager.update`](../../srcs/requirements/app/tools/cache.py#L80) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : self.save. Usages candidats : 21.
- [`CacheManager.record_scrape`](../../srcs/requirements/app/tools/cache.py#L86) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : CacheEntry, datetime.now, datetime.now(timezone.utc).isoformat, self.get, self.update. Usages candidats : 11.
- [`CacheManager.has_changed`](../../srcs/requirements/app/tools/cache.py#L120) — Retourne True si l'URL n'est pas en cache ou si le hash diffère.
  Appels effectués : self.get. Usages candidats : 7.
- [`CacheManager.clear`](../../srcs/requirements/app/tools/cache.py#L129) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : self.cache_path.exists, self.cache_path.unlink, str. Usages candidats : 4.
- [`CacheRegistry.__init__`](../../srcs/requirements/app/tools/cache.py#L145) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : Path, threading.Lock. Usages candidats : 0.
- [`CacheRegistry._path_for`](../../srcs/requirements/app/tools/cache.py#L151) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : host.replace, urlparse. Usages candidats : 1.
- [`CacheRegistry._get_manager`](../../srcs/requirements/app/tools/cache.py#L156) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : CacheManager, self._path_for. Usages candidats : 3.
- [`CacheRegistry.get`](../../srcs/requirements/app/tools/cache.py#L163) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : self._get_manager, self._get_manager(url).get. Usages candidats : 582.
- [`CacheRegistry.record_scrape`](../../srcs/requirements/app/tools/cache.py#L166) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : self._get_manager, self._get_manager(url).record_scrape. Usages candidats : 11.
- [`CacheRegistry.has_changed`](../../srcs/requirements/app/tools/cache.py#L190) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : self._get_manager, self._get_manager(url).has_changed. Usages candidats : 7.
- [`CacheRegistry.stats`](../../srcs/requirements/app/tools/cache.py#L193) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : isinstance, json.loads, len, path.read_text, self.base_dir.exists, self.base_dir.glob, str. Usages candidats : 4.
- [`CacheRegistry.clear`](../../srcs/requirements/app/tools/cache.py#L206) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : path.unlink, self.base_dir.exists, self.base_dir.glob, str. Usages candidats : 4.

## tools/config/__init__.py


## tools/config/config_builders.py

- [`build_network_policy`](../../srcs/requirements/app/tools/config/config_builders.py#L8) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : (network_conf.get('scanner') or 'none').lower, (network_conf.get('scanner') or 'none').lower().strip, NetworkPolicy, network_conf.get, set, to_bool, to_int. Usages candidats : 1.
- [`build_crawler_settings`](../../srcs/requirements/app/tools/config/config_builders.py#L57) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : crawler_conf.get, set, to_bool, to_int. Usages candidats : 2.
- [`build_http_client_settings`](../../srcs/requirements/app/tools/config/config_builders.py#L82) — Construit un bundle cohérent des paramètres HTTP issus du bloc crawler. Centralise respect_robots, délai entre requêtes et stratégie de retry.
  Appels effectués : crawler_conf.get, float, to_bool, to_int. Usages candidats : 3.

## tools/config/config_utils.py

- [`to_int`](../../srcs/requirements/app/tools/config/config_utils.py#L6) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : int. Usages candidats : 30.
- [`to_bool`](../../srcs/requirements/app/tools/config/config_utils.py#L13) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : bool, isinstance, value.strip, value.strip().lower. Usages candidats : 17.

## tools/config/config_validator.py

- [`validate_config`](../../srcs/requirements/app/tools/config/config_validator.py#L12) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : config.get, errors.extend, validate_auth, validate_crawler, validate_output. Usages candidats : 2.

## tools/config/load_config.py

- [`load_yaml_config`](../../srcs/requirements/app/tools/config/load_config.py#L7) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : FileNotFoundError, Path, _deep_merge, inc_path.read_text, isinstance, path.exists, path.read_text, yaml.safe_load. Usages candidats : 6.
- [`_deep_merge`](../../srcs/requirements/app/tools/config/load_config.py#L20) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : _deep_merge, dict, isinstance, override.items, result.get. Usages candidats : 2.
- [`get_config_as_json_string`](../../srcs/requirements/app/tools/config/load_config.py#L33) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : json.dumps. Usages candidats : 3.
- [`load_keywords_from_config`](../../srcs/requirements/app/tools/config/load_config.py#L37) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : Path, Path(default_path).read_text, Path(kw_path).read_text, config.get, json.loads. Usages candidats : 3.

## tools/config/overrides.py

- [`_to_int`](../../srcs/requirements/app/tools/config/overrides.py#L6) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : int. Usages candidats : 5.
- [`_to_bool`](../../srcs/requirements/app/tools/config/overrides.py#L13) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : bool, isinstance, value.strip, value.strip().lower. Usages candidats : 2.
- [`normalize_overrides`](../../srcs/requirements/app/tools/config/overrides.py#L19) — Nettoie/normalise les overrides. Supporte : - max_bytes (int) - respect_robots (bool) - crawl_delay_seconds (int) - headers (dict de str) - user_agent (str) - headless (bool)
  Appels effectués : _to_bool, _to_int, dict, isinstance, overrides.get, overrides.pop, user_agent.strip. Usages candidats : 7.
- [`merge_headers`](../../srcs/requirements/app/tools/config/overrides.py#L65) — Fusionne les headers en appliquant un User-Agent par défaut (si fourni) puis les overrides. Les valeurs falsy sont ignorées.
  Appels effectués : (base_headers or {}).items, (override_headers or {}).items, merged.setdefault. Usages candidats : 2.

## tools/config/validators.py

- [`validate_auth`](../../srcs/requirements/app/tools/config/validators.py#L7) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : (hosts or {}).items, auth_conf.get, errors.append, isinstance. Usages candidats : 3.
- [`validate_crawler`](../../srcs/requirements/app/tools/config/validators.py#L20) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : Path, Path(base_dir).exists, crawler_conf.get, errors.append, int, isinstance, resolve_normalizer, save_conf.get. Usages candidats : 2.
- [`validate_output`](../../srcs/requirements/app/tools/config/validators.py#L44) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : errors.append, errors.extend, isinstance, output_conf.get, output_conf.get('format', 'markdown').lower, validate_ai_report. Usages candidats : 4.
- [`validate_ai_report`](../../srcs/requirements/app/tools/config/validators.py#L56) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : Path, Path(analysis_prompt_path).exists, Path(prompt_path).exists, ai_conf.get, analysis_conf.get, errors.append, isinstance. Usages candidats : 1.

## tools/crypter.py

- [`compute_sha256`](../../srcs/requirements/app/tools/crypter.py#L5) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : Path, f.read, h.hexdigest, h.update, hashlib.sha256, iter, path.open. Usages candidats : 4.
- [`compute_sha256_from_text`](../../srcs/requirements/app/tools/crypter.py#L14) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : hashlib.sha256, hashlib.sha256(text.encode('utf-8')).hexdigest, text.encode. Usages candidats : 4.
- [`compute_sha256_from_bytes`](../../srcs/requirements/app/tools/crypter.py#L18) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : hashlib.sha256, hashlib.sha256(data).hexdigest. Usages candidats : 0.
- [`generate_key`](../../srcs/requirements/app/tools/crypter.py#L22) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : Fernet.generate_key. Usages candidats : 2.
- [`encrypt_file`](../../srcs/requirements/app/tools/crypter.py#L26) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : Fernet, Path, Path(out_path).write_bytes, fernet.encrypt, path.read_bytes. Usages candidats : 1.
- [`decrypt_file`](../../srcs/requirements/app/tools/crypter.py#L36) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : Fernet, Path, Path(out_path).write_bytes, fernet.decrypt, path.read_bytes. Usages candidats : 1.
- [`verify_file_integrity`](../../srcs/requirements/app/tools/crypter.py#L45) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : compute_sha256. Usages candidats : 1.

## tools/interfaces.py

- [`GenericFetcher.fetch`](../../srcs/requirements/app/tools/interfaces.py#L12) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : aucun appel explicite. Usages candidats : 20.
- [`AIProvider.generate`](../../srcs/requirements/app/tools/interfaces.py#L21) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : aucun appel explicite. Usages candidats : 8.
- [`Reporter.write`](../../srcs/requirements/app/tools/interfaces.py#L30) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : aucun appel explicite. Usages candidats : 19.
- [`CacheBackend.get`](../../srcs/requirements/app/tools/interfaces.py#L39) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : aucun appel explicite. Usages candidats : 582.
- [`CacheBackend.record_scrape`](../../srcs/requirements/app/tools/interfaces.py#L42) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : aucun appel explicite. Usages candidats : 11.
- [`CacheBackend.has_changed`](../../srcs/requirements/app/tools/interfaces.py#L56) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : aucun appel explicite. Usages candidats : 7.
- [`CacheStore.stats`](../../srcs/requirements/app/tools/interfaces.py#L65) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : aucun appel explicite. Usages candidats : 4.
- [`CacheStore.clear`](../../srcs/requirements/app/tools/interfaces.py#L68) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : aucun appel explicite. Usages candidats : 4.
- [`ResultStore.save`](../../srcs/requirements/app/tools/interfaces.py#L77) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : aucun appel explicite. Usages candidats : 5.

## tools/keywords.py

- [`find_keyword_hits`](../../srcs/requirements/app/tools/keywords.py#L6) — Retourne un dictionnaire {categorie: [mots-clés trouvés]} basé sur une recherche insensible à la casse dans la liste de textes fournie.
  Appels effectués : (word or '').strip, any, found_by_category.setdefault, found_by_category.setdefault(category, set()).add, isinstance, item.lower, keywords.items, needle.lower, set, sorted, terms.items, terms.setdefault, terms.setdefault(needle.lower(), set()).add. Usages candidats : 5.

## tools/logger_utils.py

- [`setup_logger`](../../srcs/requirements/app/tools/logger_utils.py#L8) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : Path, Path(file_path).parent.mkdir, RotatingFileHandler, ch.setFormatter, ch.setLevel, fh.setFormatter, fh.setLevel, getattr, logger.addHandler, logger.setLevel, logger.warning, logging.Formatter, logging.StreamHandler, logging.getLogger, logging_conf.get, logging_conf.get('level', 'INFO').upper. Usages candidats : 1.
- [`mask_sensitive_headers`](../../srcs/requirements/app/tools/logger_utils.py#L38) — Retourne une copie des headers avec masquage des valeurs sensibles. Masque les clés contenant authorization, token, api-key (insensible à la casse).
  Appels effectués : (headers or {}).items, any, isinstance, k.lower. Usages candidats : 1.
- [`log_structured`](../../srcs/requirements/app/tools/logger_utils.py#L56) — Log structuré (JSON) pour l'observabilité.
  Appels effectués : json.dumps, logger.log. Usages candidats : 2.

## tools/observability/__init__.py


## tools/observability/health_summary.py

- [`load_health`](../../srcs/requirements/app/tools/observability/health_summary.py#L8) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : isinstance, json.loads, path.exists, path.read_text. Usages candidats : 2.
- [`summary`](../../srcs/requirements/app/tools/observability/health_summary.py#L18) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : counters.get, fetch.get, float, int, last_run.get, payload.get. Usages candidats : 3.
- [`print_table`](../../srcs/requirements/app/tools/observability/health_summary.py#L50) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : '\n'.join, print. Usages candidats : 1.
- [`print_prometheus`](../../srcs/requirements/app/tools/observability/health_summary.py#L60) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : '\n'.join, (s.get('fetch_per_status', {}) or {}).items, (s.get('fetch_reasons', {}) or {}).items, lines.append, print, s.get. Usages candidats : 1.
- [`main`](../../srcs/requirements/app/tools/observability/health_summary.py#L78) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : Path, argparse.ArgumentParser, load_health, parser.add_argument, parser.parse_args, print_prometheus, print_table, summary. Usages candidats : 10.

## tools/observability/metrics.py

- [`RunMetrics.to_dict`](../../srcs/requirements/app/tools/observability/metrics.py#L19) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : asdict. Usages candidats : 6.
- [`_load_health`](../../srcs/requirements/app/tools/observability/metrics.py#L26) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : isinstance, json.loads, metrics_path.exists, metrics_path.read_text. Usages candidats : 3.
- [`_write_health`](../../srcs/requirements/app/tools/observability/metrics.py#L38) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : json.dumps, metrics_path.parent.mkdir, metrics_path.with_suffix, tmp_path.replace, tmp_path.write_text. Usages candidats : 2.
- [`record_run`](../../srcs/requirements/app/tools/observability/metrics.py#L45) — Enrichit health.json avec le dernier run + compteurs succès/échec.
  Appels effectués : Path, _load_health, _write_health, metrics.to_dict, payload.setdefault. Usages candidats : 1.
- [`record_fetch`](../../srcs/requirements/app/tools/observability/metrics.py#L63) — Enregistre un fetch individuel (succès/erreur) avec comptage et durée cumulée.
  Appels effectués : Path, _load_health, _write_health, fetch.setdefault, float, int, len, payload.setdefault, per_status.get, reasons.get, recent.append, time.time. Usages candidats : 2.
- [`time_block`](../../srcs/requirements/app/tools/observability/metrics.py#L114) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : time.time. Usages candidats : 0.

## tools/parsers/__init__.py


## tools/parsers/certkev.py

- [`_clean`](../../srcs/requirements/app/tools/parsers/certkev.py#L8) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : ' '.join, text.split. Usages candidats : 2.
- [`extract_certkev_entries`](../../srcs/requirements/app/tools/parsers/certkev.py#L12) — Extrait des entrées structurées depuis des bulletins CERT/KEV en combinant l'identifiant (CVE/CERTFR/KEV) et un court contexte.
  Appels effectués : ', '.join, CERT_LIKE.finditer, _clean, cv.upper, entries.append, entry.lower, len, match.end, match.group, match.group(1).upper, match.start, max, min, re.findall, seen.add, set, sorted, str. Usages candidats : 2.
- [`is_certkev_source`](../../srcs/requirements/app/tools/parsers/certkev.py#L41) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : any, source_name.lower. Usages candidats : 4.

## tools/parsers/csv_parser.py

- [`parse_csv`](../../srcs/requirements/app/tools/parsers/csv_parser.py#L6) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : ', '.join, bool, conf.get, enumerate, header.lstrip, header.lstrip('\ufeff').strip, isinstance, json.dumps, len, list, range, results.append, reversed, row[0].lstrip, row[0].lstrip().startswith, safe_csv_rows, sorted. Usages candidats : 0.

## tools/parsers/html_parser.py

- [`parse_html`](../../srcs/requirements/app/tools/parsers/html_parser.py#L14) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : ' | '.join, BeautifulSoup, conf.get, elem.text_content, isinstance, lxml_html.fromstring, node.get_text, node.has_attr, parts.append, results.append, rule.get, selector.get, soup.find_all, soup.get_text, soup.select, str, text.strip, tree.xpath, xp.get. Usages candidats : 0.

## tools/parsers/json_parser.py

- [`_parse_json_path`](../../srcs/requirements/app/tools/parsers/json_parser.py#L11) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : expr.find, head.endswith, head.partition, isinstance, jsonpath_parse, obj.get, path.startswith, path[2:].split, recurse, results.extend. Usages candidats : 1.
- [`_parse_json_path.recurse`](../../srcs/requirements/app/tools/parsers/json_parser.py#L23) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : head.endswith, head.partition, isinstance, obj.get, recurse, results.extend. Usages candidats : 3.
- [`parse_json`](../../srcs/requirements/app/tools/parsers/json_parser.py#L42) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : _parse_json_path, conf.get, field.get, isinstance, results.append, safe_json_load, str. Usages candidats : 0.

## tools/parsers/ocr_parser.py

- [`_lang`](../../srcs/requirements/app/tools/parsers/ocr_parser.py#L25) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : '+'.join, conf.get, isinstance, l.strip, languages.strip. Usages candidats : 1.
- [`_log_error`](../../srcs/requirements/app/tools/parsers/ocr_parser.py#L36) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : conf.get, logger.warning, str, str(conf.get('errors', '')).lower. Usages candidats : 4.
- [`parse_image`](../../srcs/requirements/app/tools/parsers/ocr_parser.py#L42) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : (text or '').strip, BytesIO, Image.open, _lang, _log_error, conf.get, isinstance, pytesseract.image_to_string. Usages candidats : 2.

## tools/parsers/pdf_parser.py

- [`_to_bytes`](../../srcs/requirements/app/tools/parsers/pdf_parser.py#L20) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : ensure_text, ensure_text(content).encode, isinstance. Usages candidats : 1.
- [`_image_description`](../../srcs/requirements/app/tools/parsers/pdf_parser.py#L28) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : ' '.join, float, img.get, int, isinstance, parts.append. Usages candidats : 1.
- [`_log_error`](../../srcs/requirements/app/tools/parsers/pdf_parser.py#L58) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : conf.get, logger.warning, str, str(conf.get('errors', '')).lower. Usages candidats : 4.
- [`parse_pdf`](../../srcs/requirements/app/tools/parsers/pdf_parser.py#L64) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : BytesIO, _image_description, _log_error, _to_bytes, conf.get, enumerate, getattr, isinstance, len, page.extract_text, pdfplumber.open, results.append, text.strip. Usages candidats : 3.

## tools/parsers/stix_parser.py

- [`parse_stix`](../../srcs/requirements/app/tools/parsers/stix_parser.py#L7) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : bundle.get, conf.get, int, isinstance, json.dumps, next, obj.get, p.get, ref.get, reference.get, safe_json_load, sorted. Usages candidats : 0.

## tools/parsers/text_utils.py

- [`ensure_text`](../../srcs/requirements/app/tools/parsers/text_utils.py#L9) — Normalise en chaîne de caractères. - bytes -> décodage (utf-8 par défaut, fallback latin-1) - autres -> str(...) + normalisation des sauts de ligne
  Appels effectués : content.decode, isinstance, str, text.replace, text.replace('\r\n', '\n').replace. Usages candidats : 12.
- [`safe_json_load`](../../srcs/requirements/app/tools/parsers/text_utils.py#L25) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : ensure_text, json.loads. Usages candidats : 3.
- [`safe_csv_rows`](../../srcs/requirements/app/tools/parsers/text_utils.py#L33) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : StringIO, csv.reader, ensure_text, list. Usages candidats : 2.

## tools/parsers/txt_parser.py

- [`parse_txt`](../../srcs/requirements/app/tools/parsers/txt_parser.py#L5) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : conf.get, ensure_text. Usages candidats : 0.

## tools/parsers/xml_parser.py

- [`parse_xml`](../../srcs/requirements/app/tools/parsers/xml_parser.py#L5) — Extrait le texte des tags demandés. Compatibilité : supporte la clé historique `tags` et la clé `extract_tags` utilisée dans scraping.yaml.
  Appels effectués : BeautifulSoup, _name, conf.get, entry.get, isinstance, node.get_text, results.append, soup.find_all. Usages candidats : 0.
- [`parse_xml._name`](../../srcs/requirements/app/tools/parsers/xml_parser.py#L12) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : entry.get, isinstance. Usages candidats : 1.

## tools/parsing/__init__.py


## tools/parsing/content_sanitizer.py

- [`sanitize_html`](../../srcs/requirements/app/tools/parsing/content_sanitizer.py#L11) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : BeautifulSoup, comment.extract, isinstance, soup, soup.find_all, str, tag.decompose. Usages candidats : 2.
- [`sanitize_xml`](../../srcs/requirements/app/tools/parsing/content_sanitizer.py#L22) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : BeautifulSoup, comment.extract, isinstance, soup.find_all, str, tag.decompose. Usages candidats : 1.

## tools/parsing/extractor.py

- [`Extractor.__init__`](../../srcs/requirements/app/tools/parsing/extractor.py#L14) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : aucun appel explicite. Usages candidats : 0.
- [`Extractor.extract`](../../srcs/requirements/app/tools/parsing/extractor.py#L18) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : ensure_text, find_keyword_hits, list, parser.parse_content, texts_for_match.append. Usages candidats : 5.

## tools/parsing/html_links.py

- [`extract_links`](../../srcs/requirements/app/tools/parsing/html_links.py#L9) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : BeautifulSoup, links.add, set, soup.find_all, urljoin. Usages candidats : 1.

## tools/parsing/ioc_extractor.py

- [`_enabled_map`](../../srcs/requirements/app/tools/parsing/ioc_extractor.py#L16) — Normalise la config extract_iocs. - bool => tous les patterns activés ou désactivés - dict => active uniquement les clés truthy (cve/url/ipv4)
  Appels effectués : DEFAULT_PATTERNS.keys, bool, isinstance, options.get. Usages candidats : 1.
- [`extract_iocs`](../../srcs/requirements/app/tools/parsing/ioc_extractor.py#L29) — Extrait des IOC simples (CVE, URLs, IPv4) à partir d'une liste de textes. Utilise des regex rapides pour limiter les faux positifs.
  Appels effectués : DEFAULT_PATTERNS.items, _add, _enabled_map, any, enabled.get, enabled.values, isinstance, m.strip, pattern.findall, results.append, seen.add, set. Usages candidats : 2.
- [`extract_iocs._add`](../../srcs/requirements/app/tools/parsing/ioc_extractor.py#L41) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : results.append, seen.add. Usages candidats : 1.

## tools/parsing/parser.py

- [`ParserRegistry.__init__`](../../srcs/requirements/app/tools/parsing/parser.py#L37) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : dict. Usages candidats : 0.
- [`ParserRegistry.get`](../../srcs/requirements/app/tools/parsing/parser.py#L40) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : self._parsers.get. Usages candidats : 582.
- [`ParserRegistry.register`](../../srcs/requirements/app/tools/parsing/parser.py#L43) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : aucun appel explicite. Usages candidats : 1.
- [`ParserRegistry.unregister`](../../srcs/requirements/app/tools/parsing/parser.py#L46) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : self._parsers.pop. Usages candidats : 0.
- [`_merge_conf`](../../srcs/requirements/app/tools/parsing/parser.py#L53) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : deepcopy, merged.update. Usages candidats : 1.
- [`_normalize_results`](../../srcs/requirements/app/tools/parsing/parser.py#L59) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : ' '.join, isinstance, item.strip, item.strip().split, normed.append, seen.add, set, text.lower. Usages candidats : 1.
- [`_filter_cert_like`](../../srcs/requirements/app/tools/parsing/parser.py#L76) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : any, keep_re.search, re.compile, source_name.lower. Usages candidats : 1.
- [`_post_process`](../../srcs/requirements/app/tools/parsing/parser.py#L89) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : _filter_cert_like, _normalize_results, conf.get, isinstance, len. Usages candidats : 1.
- [`_extract_cvss_if_any`](../../srcs/requirements/app/tools/parsing/parser.py#L102) — Essaie d'extraire un score CVSS depuis un contenu JSON/API: - cherche des clés standards dans l'objet ou dans les extraits si ce sont des dict/JSON. Retourne un float si trouvé, sinon None.
  Appels effectués : _extract_from_obj, candidates.append, float, isinstance, json.loads. Usages candidats : 1.
- [`_extract_cvss_if_any._extract_from_obj`](../../srcs/requirements/app/tools/parsing/parser.py#L110) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : float, isinstance. Usages candidats : 2.
- [`parse_content`](../../srcs/requirements/app/tools/parsing/parser.py#L149) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : (scraping_conf.get('per_source', {}) or {}).get, (scraping_conf.get('per_source', {}) or {}).get(source_name, {}).get, _extract_cvss_if_any, _merge_conf, _post_process, ensure_text, extract_certkev_entries, extract_iocs, is_certkev_source, isinstance, list, parser_fn, registry.get, sanitize_html, sanitize_xml, scraping_conf.get, texts.append, type_conf.get. Usages candidats : 16.

## tools/preflight.py

- [`_find_env_placeholders`](../../srcs/requirements/app/tools/preflight.py#L11) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : ENV_PATTERN.finditer, _find_env_placeholders, found.add, found.update, isinstance, match.group, set, value.values. Usages candidats : 4.
- [`_uses_mistral`](../../srcs/requirements/app/tools/preflight.py#L25) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : ' '.join, ' '.join([str(ai_conf.get('command') or ''), str(ai_conf.get('langgraph_llm_command') or ''), str(ai_conf.get('mode') or '')]).lower, (ai_conf.get('provider') or '').lower, ai_conf.get, str. Usages candidats : 1.
- [`_extract_source_hosts`](../../srcs/requirements/app/tools/preflight.py#L39) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : config.get, host.lower, hosts.add, isinstance, set, sources.get, src.get, urlparse. Usages candidats : 1.
- [`_host_matches`](../../srcs/requirements/app/tools/preflight.py#L58) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : auth_host.lower, src_host.endswith. Usages candidats : 1.
- [`_is_invalid_env_value`](../../srcs/requirements/app/tools/preflight.py#L70) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : int, raw.endswith, raw.startswith, str, str(value).strip, urlparse. Usages candidats : 1.
- [`collect_required_env`](../../srcs/requirements/app/tools/preflight.py#L90) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : (cache_conf.get('backend') or '').lower, _extract_source_hosts, _find_env_placeholders, _host_matches, _uses_mistral, ai_conf.get, auth_conf.get, cache_conf.get, config.get, hosts.items, ops.get, output_conf.get, required.add, required.update, set. Usages candidats : 4.
- [`check_env_requirements`](../../srcs/requirements/app/tools/preflight.py#L126) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : ', '.join, _is_invalid_env_value, bool, collect_required_env, config.get, get_secret, invalid.append, log.error, log.warning, logging.getLogger, missing.append, ops.get, sorted. Usages candidats : 4.

## tools/providers/__init__.py


## tools/providers/ai/__init__.py


## tools/providers/ai/ai_pipeline.py

- [`_validate_report_text`](../../srcs/requirements/app/tools/providers/ai/ai_pipeline.py#L15) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : ValueError, text.strip. Usages candidats : 2.
- [`LangGraphRunner.available`](../../srcs/requirements/app/tools/providers/ai/ai_pipeline.py#L27) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : aucun appel explicite. Usages candidats : 2.
- [`LangGraphRunner.build_prompt`](../../srcs/requirements/app/tools/providers/ai/ai_pipeline.py#L35) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : json.dumps, self.prompt_template.format. Usages candidats : 4.
- [`LangGraphRunner.generate`](../../srcs/requirements/app/tools/providers/ai/ai_pipeline.py#L42) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : RuntimeError, _validate_report_text, self.available, self.build_prompt, self.llm. Usages candidats : 8.
- [`build_cli_llm`](../../srcs/requirements/app/tools/providers/ai/ai_pipeline.py#L53) — Construit une fonction LLM qui appelle un binaire local (codex, ollama...).
  Appels effectués : RuntimeError, proc.stderr.strip, proc.stdout.strip, shlex.split, subprocess.run. Usages candidats : 1.
- [`build_cli_llm.llm`](../../srcs/requirements/app/tools/providers/ai/ai_pipeline.py#L57) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : RuntimeError, proc.stderr.strip, proc.stdout.strip, shlex.split, subprocess.run. Usages candidats : 2.

## tools/providers/ai/ai_report.py

- [`_run_llm`](../../srcs/requirements/app/tools/providers/ai/ai_report.py#L12) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : run_cli_llm. Usages candidats : 0.
- [`generate_ai_report`](../../srcs/requirements/app/tools/providers/ai/ai_report.py#L28) — ai_conf attend : - enabled: bool - command: str (ex: "ollama run llama3" ou "llama.cpp -m model.gguf") - output: chemin du fichier rapport (par défaut reports/ai_report.md) - timeout: optionnel (sec) - prompt_template: optionnel, chaîne utilisable avec `{results_json}` - prompt_path: optionnel, chemin vers un fichier template - pass_prompt_as_arg: bool, si True passe le prompt en argument (utile pour certaines CLI qui ne lisent pas stdin) - prompt_via_file: bool, écrit le prompt dans un fichier temporaire (évite les prompts trop longs et limite l’exposition en logs)
  Appels effectués : DefaultAIProvider, OllamaProvider, OllamaProvider().generate, ai_conf.get, default_provider.generate, logger.warning, normalize_results, provider.generate. Usages candidats : 13.

## tools/providers/ai/ai_runner.py

- [`run_cli_llm`](../../srcs/requirements/app/tools/providers/ai/ai_runner.py#L14) — Exécute une commande LLM locale. - pass_prompt_as_arg : ajoute le prompt (ou le chemin du fichier) aux arguments - prompt_via_file : écrit le prompt dans un fichier temporaire pour éviter les lignes trop longues et le passe en stdin (ou en argument si pass_prompt_as_arg=True)
  Appels effectués : RuntimeError, proc.stderr.strip, proc.stdout.strip, shlex.split, subprocess.run, tempfile.NamedTemporaryFile, tmp.flush, tmp.seek, tmp.write. Usages candidats : 1.

## tools/providers/ai/command_plan.py

- [`detect_local_llm`](../../srcs/requirements/app/tools/providers/ai/command_plan.py#L18) — Essaie de détecter un binaire LLM local et retourne une commande prête à l'emploi. Priorité : ollama -> llama/llama.cpp -> codex -> copilot -> code.
  Appels effectués : shutil.which. Usages candidats : 2.
- [`build_command_plan`](../../srcs/requirements/app/tools/providers/ai/command_plan.py#L38) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : AiCommandPlan, ai_conf.get, any, bool, detect_local_llm, int, logger.warning. Usages candidats : 1.

## tools/providers/ai/ollama_provider.py

- [`evidence_kind`](../../srcs/requirements/app/tools/providers/ai/ollama_provider.py#L45) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : context.get, item.get. Usages candidats : 2.
- [`response_schema`](../../srcs/requirements/app/tools/providers/ai/ollama_provider.py#L58) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : list. Usages candidats : 1.
- [`resolve_decisions`](../../srcs/requirements/app/tools/providers/ai/ollama_provider.py#L71) — Resolve bounded model decisions into source-based French text and exact quotes.
  Appels effectués : SUMMARY_TEMPLATES[kind].format_map, ValueError, defaultdict, evidence_kind, findings.append, isinstance, item.get, item.get('context', {}).items, match.end, re.search, seen.add, set, str. Usages candidats : 5.
- [`validate_findings`](../../srcs/requirements/app/tools/providers/ai/ollama_provider.py#L102) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : IDENTIFIERS.findall, TEXT_LIMITS.items, all, any, enumerate, errors.append, finding.values, finding['quote'].strip, finding[field].lower, index.get, isinstance, len, re.findall, set, token.upper, value.strip, words.intersection. Usages candidats : 6.
- [`_safe_text`](../../srcs/requirements/app/tools/providers/ai/ollama_provider.py#L141) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : str, str(value).replace, str(value).replace('&', '&amp;').replace, str(value).replace('&', '&amp;').replace('<', '&lt;').replace, str(value).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace, str(value).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('[', '\\[').replace, str(value).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('[', '\\[').replace(']', '\\]').replace. Usages candidats : 10.
- [`render_report`](../../srcs/requirements/app/tools/providers/ai/ollama_provider.py#L146) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : ', '.join, '\n'.join, _safe_text, groups.items, groups.setdefault, groups.setdefault(label, []).append, item.get, len, lines.append, sorted, sum. Usages candidats : 2.
- [`write_evidence`](../../srcs/requirements/app/tools/providers/ai/ollama_provider.py#L196) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : '; '.join, (directory / 'attack_types.csv').open, (directory / 'evidence.json').write_text, csv.DictWriter, isinstance, item.get, json.dumps, row.items, str, val.startswith, writer.writeheader, writer.writerow. Usages candidats : 1.
- [`OllamaProvider.__init__`](../../srcs/requirements/app/tools/providers/ai/ollama_provider.py#L208) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : requests.Session. Usages candidats : 0.
- [`OllamaProvider.generate`](../../srcs/requirements/app/tools/providers/ai/ollama_provider.py#L213) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : (archive / 'evidence.json').read_bytes, (archive / 'quality.json').write_text, (archive / 'report.md').write_text, (archive / 'request.json').write_text, (archive / 'response.json').write_text, Path, ValueError, ai_conf.get, archive.mkdir, build_evidence, coverage, data.get, datetime.now, datetime.now(timezone.utc).strftime, entry.get, evidence_kind, float, getattr, hashlib.sha256, hashlib.sha256((archive / 'evidence.json').read_bytes()).hexdigest, hashlib.sha256(latest_report.encode()).hexdigest, hashlib.sha256(prompt.encode()).hexdigest, hashlib.sha256(report.encode()).hexdigest, host.rstrip, int, json.dumps, json.loads, latest_report.encode, logger.warning, next, os.environ.get, output.with_suffix, output.with_suffix('.quality.json').write_text, output.write_text, prompt.encode, quality['errors'].append, render_report, report.encode, resolve_decisions, response.json, response.raise_for_status, response_schema, select_evidence, self.session.get, self.session.post, tags.json, tags.json().get, tags.raise_for_status, type, urlparse, uuid.uuid4, validate_findings, write_evidence. Usages candidats : 8.

## tools/providers/ai/prompt_config.py

- [`PromptConfig.load_template`](../../srcs/requirements/app/tools/providers/ai/prompt_config.py#L16) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : Path, Path(self.prompt_path).read_text, data['prompt'].get, isinstance, logger.warning, yaml.safe_load. Usages candidats : 3.
- [`PromptConfig.build_prompt`](../../srcs/requirements/app/tools/providers/ai/prompt_config.py#L39) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : '\n'.join, fmt_kwargs.update, json.dumps, logger.warning, self.load_template, template.format. Usages candidats : 4.

## tools/providers/ai/providers.py

- [`_make_prompt_conf`](../../srcs/requirements/app/tools/providers/ai/providers.py#L18) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : PromptConfig, conf.get. Usages candidats : 2.
- [`_write_text`](../../srcs/requirements/app/tools/providers/ai/providers.py#L26) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : logger.info, path.parent.mkdir, path.write_text. Usages candidats : 4.
- [`_log_warn`](../../srcs/requirements/app/tools/providers/ai/providers.py#L33) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : len, logger.warning, str. Usages candidats : 5.
- [`_run_cli_task`](../../srcs/requirements/app/tools/providers/ai/providers.py#L42) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : _write_text, run_llm. Usages candidats : 4.
- [`_run_with_retries`](../../srcs/requirements/app/tools/providers/ai/providers.py#L65) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : _log_warn, _run_cli_task, logger.error, range, time.sleep. Usages candidats : 1.
- [`_run_fallback`](../../srcs/requirements/app/tools/providers/ai/providers.py#L100) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : _log_warn, _run_cli_task, ai_conf.get, bool, fallback.get, int. Usages candidats : 1.
- [`_run_local_autodetect`](../../srcs/requirements/app/tools/providers/ai/providers.py#L131) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : _log_warn, _run_cli_task, detect_local_llm. Usages candidats : 1.
- [`_normalize_text`](../../srcs/requirements/app/tools/providers/ai/providers.py#L160) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : normalized.encode, normalized.encode('ascii', 'ignore').decode, stripped.lower, unicodedata.normalize. Usages candidats : 7.
- [`is_complete`](../../srcs/requirements/app/tools/providers/ai/providers.py#L166) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : _normalize_text. Usages candidats : 3.
- [`_is_vuln_entry`](../../srcs/requirements/app/tools/providers/ai/providers.py#L184) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : isinstance, keywords.get, re.search, res.get. Usages candidats : 1.
- [`_filter_vuln_only`](../../srcs/requirements/app/tools/providers/ai/providers.py#L195) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : _is_vuln_entry. Usages candidats : 1.
- [`_to_int`](../../srcs/requirements/app/tools/providers/ai/providers.py#L199) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : int. Usages candidats : 5.
- [`_truncate_text`](../../srcs/requirements/app/tools/providers/ai/providers.py#L206) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : isinstance, len. Usages candidats : 1.
- [`_fill_missing_sections`](../../srcs/requirements/app/tools/providers/ai/providers.py#L214) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : '\n'.join, '\n'.join(lines).rstrip, _normalize_text, lines.append, text.endswith, zip. Usages candidats : 1.
- [`_compact_results`](../../srcs/requirements/app/tools/providers/ai/providers.py#L241) — Réduit la taille du payload envoyé au LLM (limite le nombre de sources et la longueur des extraits).
  Appels effectués : _truncate_text, clone.get, clone.pop, compacted.append, deepcopy, isinstance, trimmed.append. Usages candidats : 1.
- [`DefaultAIProvider.__init__`](../../srcs/requirements/app/tools/providers/ai/providers.py#L274) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : aucun appel explicite. Usages candidats : 0.
- [`DefaultAIProvider.generate`](../../srcs/requirements/app/tools/providers/ai/providers.py#L277) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : Exception, LangGraphRunner, LangGraphRunner.available, Path, _compact_results, _fill_missing_sections, _filter_vuln_only, _log_warn, _make_prompt_conf, _run_cli_task, _run_fallback, _run_local_autodetect, _run_with_retries, _to_int, _write_text, ai_conf.get, analysis_conf.get, analysis_prompt_conf.build_prompt, bool, build_command_plan, filt_conf.get, float, int, is_complete, len, logger.error, logger.warning, max, prompt_conf.build_prompt, prompt_conf.load_template, runner.generate, score_results, scoring_conf.get, self.run_llm. Usages candidats : 8.

## tools/providers/cache_factory.py

- [`build_cache`](../../srcs/requirements/app/tools/providers/cache_factory.py#L5) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : build_cache_store. Usages candidats : 1.

## tools/providers/cache_mongo.py

- [`MongoCache.__init__`](../../srcs/requirements/app/tools/providers/cache_mongo.py#L22) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : self._connect. Usages candidats : 0.
- [`MongoCache._connect`](../../srcs/requirements/app/tools/providers/cache_mongo.py#L30) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : MongoClient. Usages candidats : 4.
- [`MongoCache._collection`](../../srcs/requirements/app/tools/providers/cache_mongo.py#L40) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : self._connect. Usages candidats : 5.
- [`MongoCache.get`](../../srcs/requirements/app/tools/providers/cache_mongo.py#L45) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : CacheEntry.from_dict, coll.find_one, self._collection. Usages candidats : 582.
- [`MongoCache.record_scrape`](../../srcs/requirements/app/tools/providers/cache_mongo.py#L54) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : CacheEntry, coll.update_one, entry.to_dict, self._collection, self.get. Usages candidats : 11.
- [`MongoCache.has_changed`](../../srcs/requirements/app/tools/providers/cache_mongo.py#L92) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : self.get. Usages candidats : 7.
- [`MongoCache.stats`](../../srcs/requirements/app/tools/providers/cache_mongo.py#L100) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : coll.count_documents, self._collection, str. Usages candidats : 4.
- [`MongoCache.clear`](../../srcs/requirements/app/tools/providers/cache_mongo.py#L110) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : coll.delete_many, self._collection, str. Usages candidats : 4.

## tools/providers/cache_store.py

- [`FileCacheStore.__init__`](../../srcs/requirements/app/tools/providers/cache_store.py#L13) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : CacheManager. Usages candidats : 0.
- [`FileCacheStore.get`](../../srcs/requirements/app/tools/providers/cache_store.py#L16) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : self._manager.get. Usages candidats : 582.
- [`FileCacheStore.record_scrape`](../../srcs/requirements/app/tools/providers/cache_store.py#L19) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : self._manager.record_scrape. Usages candidats : 11.
- [`FileCacheStore.has_changed`](../../srcs/requirements/app/tools/providers/cache_store.py#L43) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : self._manager.has_changed. Usages candidats : 7.
- [`FileCacheStore.stats`](../../srcs/requirements/app/tools/providers/cache_store.py#L46) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : self._manager.stats. Usages candidats : 4.
- [`FileCacheStore.clear`](../../srcs/requirements/app/tools/providers/cache_store.py#L49) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : self._manager.clear. Usages candidats : 4.
- [`PerSiteCacheStore.__init__`](../../srcs/requirements/app/tools/providers/cache_store.py#L54) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : CacheRegistry. Usages candidats : 0.
- [`PerSiteCacheStore.get`](../../srcs/requirements/app/tools/providers/cache_store.py#L57) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : self._registry.get. Usages candidats : 582.
- [`PerSiteCacheStore.record_scrape`](../../srcs/requirements/app/tools/providers/cache_store.py#L60) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : self._registry.record_scrape. Usages candidats : 11.
- [`PerSiteCacheStore.has_changed`](../../srcs/requirements/app/tools/providers/cache_store.py#L84) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : self._registry.has_changed. Usages candidats : 7.
- [`PerSiteCacheStore.stats`](../../srcs/requirements/app/tools/providers/cache_store.py#L87) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : self._registry.stats. Usages candidats : 4.
- [`PerSiteCacheStore.clear`](../../srcs/requirements/app/tools/providers/cache_store.py#L90) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : self._registry.clear. Usages candidats : 4.
- [`MongoCacheStore.__init__`](../../srcs/requirements/app/tools/providers/cache_store.py#L95) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : MongoCache. Usages candidats : 0.
- [`MongoCacheStore.get`](../../srcs/requirements/app/tools/providers/cache_store.py#L98) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : self._mongo.get. Usages candidats : 582.
- [`MongoCacheStore.record_scrape`](../../srcs/requirements/app/tools/providers/cache_store.py#L101) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : self._mongo.record_scrape. Usages candidats : 11.
- [`MongoCacheStore.has_changed`](../../srcs/requirements/app/tools/providers/cache_store.py#L125) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : self._mongo.has_changed. Usages candidats : 7.
- [`MongoCacheStore.stats`](../../srcs/requirements/app/tools/providers/cache_store.py#L128) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : self._mongo.stats. Usages candidats : 4.
- [`MongoCacheStore.clear`](../../srcs/requirements/app/tools/providers/cache_store.py#L131) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : self._mongo.clear. Usages candidats : 4.
- [`build_cache_store`](../../srcs/requirements/app/tools/providers/cache_store.py#L135) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : FileCacheStore, MongoCacheStore, PerSiteCacheStore, bool, cache_conf.get, get_secret. Usages candidats : 4.

## tools/providers/fetchers.py

- [`HttpFetcher.__init__`](../../srcs/requirements/app/tools/providers/fetchers.py#L14) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : aucun appel explicite. Usages candidats : 0.
- [`HttpFetcher.fetch`](../../srcs/requirements/app/tools/providers/fetchers.py#L17) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : self.client.fetch. Usages candidats : 20.
- [`build_fetcher`](../../srcs/requirements/app/tools/providers/fetchers.py#L21) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : HttpClient, HttpFetcher, bool, crawler_conf.get, float, getattr, http_settings.get, int. Usages candidats : 1.

## tools/providers/http/__init__.py


## tools/providers/http/client.py

- [`HttpClient.__init__`](../../srcs/requirements/app/tools/providers/http/client.py#L26) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : RobotsDelayPolicy, float, get_default_headless_strategy, getattr, int, max, threading.Lock. Usages candidats : 0.
- [`HttpClient._timed_fetch`](../../srcs/requirements/app/tools/providers/http/client.py#L57) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : time.time. Usages candidats : 1.
- [`HttpClient._next_user_agent`](../../srcs/requirements/app/tools/providers/http/client.py#L61) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : len. Usages candidats : 2.
- [`HttpClient._next_proxy`](../../srcs/requirements/app/tools/providers/http/client.py#L69) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : len. Usages candidats : 2.
- [`HttpClient._should_retry`](../../srcs/requirements/app/tools/providers/http/client.py#L78) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : aucun appel explicite. Usages candidats : 1.
- [`HttpClient._backoff_delay`](../../srcs/requirements/app/tools/providers/http/client.py#L85) — Backoff adaptatif : + agressif sur 429/403. attempt est l'indice de tentative déjà effectuée (>=0).
  Appels effectués : aucun appel explicite. Usages candidats : 3.
- [`HttpClient._run_headless`](../../srcs/requirements/app/tools/providers/http/client.py#L97) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : DownloadResult, _persist_content, _too_large_error, ctx.headers.get, ctx.proxy.get, html.encode, isinstance, len, sanitize_html, self.headless_strategy.fetch, self.logger.warning. Usages candidats : 1.
- [`HttpClient._fetch_with_retries`](../../srcs/requirements/app/tools/providers/http/client.py#L126) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : download_with_context, elapsed, isinstance, parsed._replace, record_fetch, self._backoff_delay, self._robots_delay.wait, self._should_retry, self._timed_fetch, self.logger.warning, source.get, str, time.sleep, urlparse, urlunparse. Usages candidats : 1.
- [`HttpClient.fetch`](../../srcs/requirements/app/tools/providers/http/client.py#L170) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : DownloadResult, bool, build_request_context, getattr, mask_sensitive_headers, self._fetch_with_retries, self._next_proxy, self._next_user_agent, self._robots_delay.is_allowed, self._run_headless, self.logger.debug, source.get, source.get('overrides', {}).get, validate_url. Usages candidats : 20.

## tools/providers/http/download.py

- [`_persist_content`](../../srcs/requirements/app/tools/providers/http/download.py#L35) — Valide et scanne un fichier temporaire avant publication atomique. Un contenu rejeté n'écrase jamais un artefact existant et n'expose aucun saved_path aux étapes suivantes. Le scan s'applique aussi sans stockage.
  Appels effectués : Path, Path(policy.sandbox_dir).resolve, _is_path_in_sandbox, directory.mkdir, handle.write, len, pending.replace, pending.unlink, run_scan, storage.path_for, target.parent.mkdir, target.resolve, tempfile.NamedTemporaryFile. Usages candidats : 7.
- [`_is_path_in_sandbox`](../../srcs/requirements/app/tools/providers/http/download.py#L80) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : Path, Path(sandbox).resolve, path.resolve. Usages candidats : 1.
- [`_too_large_error`](../../srcs/requirements/app/tools/providers/http/download.py#L90) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : DownloadResult. Usages candidats : 3.
- [`_stream_content`](../../srcs/requirements/app/tools/providers/http/download.py#L98) — Lit la réponse en streaming pour éviter de charger de gros fichiers en mémoire. Retourne (content_bytes, truncated_flag).
  Appels effectués : bytearray, bytes, data.extend, len, resp.close, resp.iter_content. Usages candidats : 1.
- [`_check_content_length`](../../srcs/requirements/app/tools/providers/http/download.py#L118) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : int, resp.headers.get. Usages candidats : 1.
- [`download_with_context`](../../srcs/requirements/app/tools/providers/http/download.py#L128) — Pipeline unifié : utilise le RequestContext (policy/headers/proxy) pour télécharger en streaming avec respect de max_bytes et sauvegarde éventuelle.
  Appels effectués : (source.get('type') or 'html').lower, DownloadResult, SANITIZERS.get, _check_content_length, _persist_content, _stream_content, _too_large_error, ctype.split, ensure_text, len, mimetypes.guess_extension, network.get_response, resp.close, resp.headers.get, resp.headers.get('Content-Type', '').lower, resp.raise_for_status, sanitizer, source.get, str. Usages candidats : 2.
- [`download_source`](../../srcs/requirements/app/tools/providers/http/download.py#L198) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : RequestContext, download_with_context. Usages candidats : 15.

## tools/providers/http/download_types.py

- [`StorageTarget.path_for`](../../srcs/requirements/app/tools/providers/http/download_types.py#L32) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : aucun appel explicite. Usages candidats : 4.

## tools/providers/http/headless.py

- [`HeadlessStrategy.fetch`](../../srcs/requirements/app/tools/providers/http/headless.py#L26) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : aucun appel explicite. Usages candidats : 20.
- [`PlaywrightStrategy.fetch`](../../srcs/requirements/app/tools/providers/http/headless.py#L31) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : browser.close, browser.new_context, context.new_page, p.chromium.launch, page.content, page.goto, sync_playwright. Usages candidats : 20.
- [`SeleniumStrategy.fetch`](../../srcs/requirements/app/tools/providers/http/headless.py#L48) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : ChromeOptions, driver.get, driver.quit, driver.set_page_load_timeout, opts.add_argument, webdriver.Chrome. Usages candidats : 20.
- [`get_default_headless_strategy`](../../srcs/requirements/app/tools/providers/http/headless.py#L69) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : PlaywrightStrategy, SeleniumStrategy. Usages candidats : 2.
- [`fetch_headless`](../../srcs/requirements/app/tools/providers/http/headless.py#L77) — Compat : utilise la stratégie par défaut (Playwright si dispo).
  Appels effectués : get_default_headless_strategy, strategy.fetch. Usages candidats : 0.

## tools/providers/http/network.py

- [`resolve_host_ips`](../../srcs/requirements/app/tools/providers/http/network.py#L10) — Résout un hostname en adresses IP. Une liste vide est refusée par validate_url.
  Appels effectués : ips.append, socket.getaddrinfo. Usages candidats : 1.
- [`is_private`](../../srcs/requirements/app/tools/providers/http/network.py#L28) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : ipaddress.ip_address. Usages candidats : 2.
- [`validate_url`](../../srcs/requirements/app/tools/providers/http/network.py#L36) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : any, is_private, resolve_host_ips, urlparse. Usages candidats : 3.
- [`_origin`](../../srcs/requirements/app/tools/providers/http/network.py#L64) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : urlparse. Usages candidats : 2.
- [`get_response`](../../srcs/requirements/app/tools/providers/http/network.py#L69) — GET borné : contrôle chaque saut avant connexion, sans redirection automatique. Les en-têtes applicatifs restent liés à leur origine. Une nouvelle origine ne reçoit que les en-têtes neutres et ses propres identifiants explicites.
  Appels effectués : ValueError, _origin, current_headers.items, current_headers.update, dict, hashlib.sha256, hashlib.sha256(cert).hexdigest, k.lower, range, redirect_headers, requests.get, response.close, response.headers.get, response.raw.connection.sock.getpeercert, urljoin, validate_url. Usages candidats : 2.

## tools/providers/http/policies.py

- [`RobotsDelayPolicy.__init__`](../../srcs/requirements/app/tools/providers/http/policies.py#L17) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : NetworkPolicy, threading.Lock. Usages candidats : 0.
- [`RobotsDelayPolicy.is_allowed`](../../srcs/requirements/app/tools/providers/http/policies.py#L25) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : ValueError, body.decode, body.decode('utf-8', errors='replace').splitlines, body.extend, bytearray, get_response, len, parser.can_fetch, response.close, response.iter_content, rp.parse, rp.set_url, self._robots_cache.get, urllib.robotparser.RobotFileParser, urlparse. Usages candidats : 3.
- [`RobotsDelayPolicy.wait`](../../srcs/requirements/app/tools/providers/http/policies.py#L60) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : self._last_access.get, time.sleep, time.time, urlparse. Usages candidats : 1.
- [`policy_with_overrides`](../../srcs/requirements/app/tools/providers/http/policies.py#L77) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : overrides.get, replace, to_int. Usages candidats : 2.

## tools/providers/http/request_context.py

- [`build_request_context`](../../srcs/requirements/app/tools/providers/http/request_context.py#L20) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : RequestContext, auth_conf.get, bool, build_headers, int, merge_headers, normalize_overrides, overrides.get, policy_with_overrides, source.get. Usages candidats : 1.
- [`build_request_context.redirect_headers`](../../srcs/requirements/app/tools/providers/http/request_context.py#L45) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : auth_conf.get, build_headers. Usages candidats : 1.

## tools/providers/http/scanner.py

- [`run_scan`](../../srcs/requirements/app/tools/providers/http/scanner.py#L13) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : Path, arg.replace, proc.stderr.strip, proc.stdout.strip, shlex.split, str, subprocess.run. Usages candidats : 7.

## tools/providers/http/url_policy.py

- [`UrlPolicy.__init__`](../../srcs/requirements/app/tools/providers/http/url_policy.py#L12) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : resolve_normalizer. Usages candidats : 0.
- [`UrlPolicy.normalize`](../../srcs/requirements/app/tools/providers/http/url_policy.py#L17) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : self.normalizer. Usages candidats : 4.
- [`UrlPolicy.can_follow`](../../srcs/requirements/app/tools/providers/http/url_policy.py#L20) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : same_domain. Usages candidats : 1.

## tools/providers/http/url_utils.py

- [`normalize_url`](../../srcs/requirements/app/tools/providers/http/url_utils.py#L4) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : url.strip. Usages candidats : 0.
- [`normalize_url_lower`](../../srcs/requirements/app/tools/providers/http/url_utils.py#L8) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : url.strip, url.strip().lower. Usages candidats : 0.
- [`resolve_normalizer`](../../srcs/requirements/app/tools/providers/http/url_utils.py#L12) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : ValueError. Usages candidats : 5.
- [`same_domain`](../../srcs/requirements/app/tools/providers/http/url_utils.py#L24) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : urlparse. Usages candidats : 3.
- [`join_url`](../../srcs/requirements/app/tools/providers/http/url_utils.py#L35) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : urljoin. Usages candidats : 0.

## tools/providers/reporters.py

- [`_slugify`](../../srcs/requirements/app/tools/providers/reporters.py#L11) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : re.sub, value.strip, value.strip('-').lower. Usages candidats : 1.
- [`is_vuln_entry`](../../srcs/requirements/app/tools/providers/reporters.py#L17) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : isinstance, keywords.get, re.search, res.get. Usages candidats : 1.
- [`_BaseReporter.__init__`](../../srcs/requirements/app/tools/providers/reporters.py#L29) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : Path, bool, self.output_conf.get. Usages candidats : 0.
- [`_BaseReporter._ensure_dirs`](../../srcs/requirements/app/tools/providers/reporters.py#L36) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : self.detail_dir.mkdir, self.file_path.parent.mkdir. Usages candidats : 2.
- [`_BaseReporter._detail_path`](../../srcs/requirements/app/tools/providers/reporters.py#L41) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : _slugify, res.get. Usages candidats : 2.
- [`_BaseReporter._should_skip_detail`](../../srcs/requirements/app/tools/providers/reporters.py#L45) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : path.exists, res.get. Usages candidats : 2.
- [`MarkdownReporter._summary_block`](../../srcs/requirements/app/tools/providers/reporters.py#L50) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : ', '.join, counts.get, counts.keys, format_status, len, lines.append, res.get, round. Usages candidats : 1.
- [`MarkdownReporter.write_detail`](../../srcs/requirements/app/tools/providers/reporters.py#L88) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : '\n'.join, build_markdown_section, path.write_text, self._detail_path, self._should_skip_detail. Usages candidats : 2.
- [`MarkdownReporter.write`](../../srcs/requirements/app/tools/providers/reporters.py#L95) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : '\n'.join, bool, build_markdown_section, lines.extend, self._ensure_dirs, self._summary_block, self.file_path.write_text, self.write_detail, str. Usages candidats : 19.
- [`JsonReporter.write_detail`](../../srcs/requirements/app/tools/providers/reporters.py#L117) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : json.dumps, path.write_text, self._detail_path, self._should_skip_detail. Usages candidats : 2.
- [`JsonReporter.write`](../../srcs/requirements/app/tools/providers/reporters.py#L123) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : build_json_entry, json.dumps, payload['sources'].append, self._ensure_dirs, self.file_path.write_text, self.write_detail, str. Usages candidats : 19.
- [`build_reporter`](../../srcs/requirements/app/tools/providers/reporters.py#L136) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : (output_conf.get('format') or 'markdown').lower, JsonReporter, MarkdownReporter, output_conf.get. Usages candidats : 1.

## tools/providers/result_store.py

- [`NoopResultStore.save`](../../srcs/requirements/app/tools/providers/result_store.py#L16) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : aucun appel explicite. Usages candidats : 5.
- [`MongoResultStore.__init__`](../../srcs/requirements/app/tools/providers/result_store.py#L21) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : self._connect. Usages candidats : 0.
- [`MongoResultStore._connect`](../../srcs/requirements/app/tools/providers/result_store.py#L29) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : MongoClient. Usages candidats : 4.
- [`MongoResultStore._collection`](../../srcs/requirements/app/tools/providers/result_store.py#L39) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : self._connect. Usages candidats : 5.
- [`MongoResultStore.save`](../../srcs/requirements/app/tools/providers/result_store.py#L44) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : coll.insert_one, dict, self._collection. Usages candidats : 5.
- [`build_result_store`](../../srcs/requirements/app/tools/providers/result_store.py#L54) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : MongoResultStore, NoopResultStore, get_secret, os.getenv. Usages candidats : 1.

## tools/providers/storage_mongo.py

- [`_get_collection`](../../srcs/requirements/app/tools/providers/storage_mongo.py#L24) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : MongoClient, os.getenv. Usages candidats : 1.
- [`save_result`](../../srcs/requirements/app/tools/providers/storage_mongo.py#L41) — Sauvegarde un document résultat dans MongoDB si configuré.
  Appels effectués : _get_collection, coll.insert_one, dict. Usages candidats : 2.

## tools/quota.py

- [`Quota.__init__`](../../srcs/requirements/app/tools/quota.py#L7) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : threading.Lock. Usages candidats : 0.
- [`Quota.reserve_page`](../../srcs/requirements/app/tools/quota.py#L14) — Réserve une page si quota non dépassé. Retourne False sinon.
  Appels effectués : aucun appel explicite. Usages candidats : 4.
- [`Quota.add_bytes`](../../srcs/requirements/app/tools/quota.py#L22) — Ajoute des octets et retourne False si le quota est dépassé après ajout.
  Appels effectués : aucun appel explicite. Usages candidats : 4.
- [`Quota.remaining_pages`](../../srcs/requirements/app/tools/quota.py#L32) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : max. Usages candidats : 1.
- [`Quota.remaining_bytes`](../../srcs/requirements/app/tools/quota.py#L38) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : max. Usages candidats : 0.

## tools/reporting/__init__.py


## tools/reporting/email_report.py

- [`_normalize_recipients`](../../srcs/requirements/app/tools/reporting/email_report.py#L12) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : isinstance, item.strip, str, str(item).strip, value.replace, value.replace(';', ',').split. Usages candidats : 2.
- [`_format_template`](../../srcs/requirements/app/tools/reporting/email_report.py#L23) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : template.format. Usages candidats : 2.
- [`_resolve_pdf_source`](../../srcs/requirements/app/tools/reporting/email_report.py#L30) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : (email_conf.get('pdf_source') or 'report').lower, Path, email_conf.get, exports.get, output_conf.get. Usages candidats : 1.
- [`_build_email_config`](../../srcs/requirements/app/tools/reporting/email_report.py#L42) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : (run_meta or {}).get, Path, _format_template, _normalize_recipients, dt.datetime.now, email_conf.get, get_secret, isinstance, now.strftime, output_conf.get, scheduling_conf.get, to_bool, to_int. Usages candidats : 1.
- [`_ensure_pdf`](../../srcs/requirements/app/tools/reporting/email_report.py#L89) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : is_valid_pdf, logger.info, logger.warning, pdf_path.exists, pdf_path.unlink, render_report_pdf, source_path.exists, source_path.read_text. Usages candidats : 1.
- [`send_report_email`](../../srcs/requirements/app/tools/reporting/email_report.py#L126) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : ', '.join, EmailMessage, _build_email_config, _ensure_pdf, _resolve_pdf_source, cfg.get, int, logger.info, logger.warning, msg.add_attachment, msg.set_content, pdf_path.exists, pdf_path.read_bytes, server.login, server.send_message, server.starttls, smtp_class, source_path.with_suffix. Usages candidats : 5.

## tools/reporting/exports.py

- [`_export_executive_summary`](../../srcs/requirements/app/tools/reporting/exports.py#L12) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : ', '.join, '\n'.join, _brief, dict.fromkeys, isinstance, lines.append, lines.extend, list, path.parent.mkdir, path.write_text, r.get, res.get. Usages candidats : 1.
- [`_export_executive_summary._brief`](../../srcs/requirements/app/tools/reporting/exports.py#L17) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : ', '.join, dict.fromkeys, isinstance, list, res.get. Usages candidats : 2.
- [`_export_ioc_table`](../../srcs/requirements/app/tools/reporting/exports.py#L33) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : ';'.join, _json.dumps, csv.DictWriter, csv_path.open, csv_path.parent.mkdir, extract_iocs, json_path.parent.mkdir, json_path.write_text, res.get, rows.append, writer.writeheader, writer.writerows. Usages candidats : 1.
- [`export_additional_views`](../../srcs/requirements/app/tools/reporting/exports.py#L59) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : (output_conf.get('ai_report', {}) or {}).get, Path, _export_executive_summary, _export_ioc_table, exports.get, output_conf.get, score_results, scoring_conf.get. Usages candidats : 1.

## tools/reporting/pdf/__init__.py


## tools/reporting/pdf/core.py

- [`safe_text`](../../srcs/requirements/app/tools/reporting/pdf/core.py#L33) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : text.encode, text.encode('latin-1', errors='replace').decode, text.translate. Usages candidats : 13.
- [`iter_lines`](../../srcs/requirements/app/tools/reporting/pdf/core.py#L38) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : isinstance, text.splitlines. Usages candidats : 2.
- [`wrap_long_words`](../../srcs/requirements/app/tools/reporting/pdf/core.py#L44) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : ' '.join, len, range, text.split, wrapped.append. Usages candidats : 1.
- [`wrap_to_width`](../../srcs/requirements/app/tools/reporting/pdf/core.py#L58) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : lines.append, pdf.get_string_width, text.split. Usages candidats : 2.
- [`write_wrapped`](../../srcs/requirements/app/tools/reporting/pdf/core.py#L87) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : pdf.cell, pdf.ln, pdf.set_x, safe_text, wrap_to_width. Usages candidats : 5.
- [`is_valid_pdf`](../../srcs/requirements/app/tools/reporting/pdf/core.py#L99) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : data.startswith, len, path.read_bytes. Usages candidats : 3.

## tools/reporting/pdf/layout.py


## tools/reporting/pdf/layout_blocks.py

- [`render_heading`](../../srcs/requirements/app/tools/reporting/pdf/layout_blocks.py#L11) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : core.write_wrapped, pdf.ln, pdf.set_font, pdf.set_text_color. Usages candidats : 1.
- [`render_paragraph`](../../srcs/requirements/app/tools/reporting/pdf/layout_blocks.py#L21) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : core.write_wrapped, pdf.ln. Usages candidats : 1.
- [`render_list`](../../srcs/requirements/app/tools/reporting/pdf/layout_blocks.py#L26) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : core.write_wrapped, pdf.ln. Usages candidats : 1.
- [`render_blocks`](../../srcs/requirements/app/tools/reporting/pdf/layout_blocks.py#L33) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : block.get, int, on_heading, pdf.add_page, render_heading, render_list, render_paragraph, table_renderer.render_table. Usages candidats : 1.

## tools/reporting/pdf/layout_doc.py

- [`configure_document`](../../srcs/requirements/app/tools/reporting/pdf/layout_doc.py#L16) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : pdf.add_page, pdf.set_auto_page_break, pdf.set_font, pdf.set_margins. Usages candidats : 1.
- [`_truncate_to_width`](../../srcs/requirements/app/tools/reporting/pdf/layout_doc.py#L25) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : core.safe_text, len, max, pdf.get_string_width, range. Usages candidats : 1.
- [`render_cover`](../../srcs/requirements/app/tools/reporting/pdf/layout_doc.py#L38) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : core.safe_text, dt.datetime.now, dt.datetime.now().strftime, pdf.add_page, pdf.cell, pdf.ln, pdf.rect, pdf.set_fill_color, pdf.set_font, pdf.set_text_color, pdf.set_xy. Usages candidats : 1.
- [`render_toc`](../../srcs/requirements/app/tools/reporting/pdf/layout_doc.py#L61) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : _truncate_to_width, core.safe_text, entry.get, f"{indent}{entry.get('text', '')}".strip, int, max, min, pdf.add_page, pdf.cell, pdf.get_string_width, pdf.ln, pdf.set_font, str. Usages candidats : 1.
- [`build_toc_entries`](../../srcs/requirements/app/tools/reporting/pdf/layout_doc.py#L84) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : block.get, entries.append. Usages candidats : 1.
- [`assign_toc_page`](../../srcs/requirements/app/tools/reporting/pdf/layout_doc.py#L92) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : block.get. Usages candidats : 1.
- [`CTIPDF.footer`](../../srcs/requirements/app/tools/reporting/pdf/layout_doc.py#L101) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : self.cell, self.page_no, self.set_font, self.set_text_color, self.set_y. Usages candidats : 0.

## tools/reporting/pdf/layout_inline.py

- [`render_line`](../../srcs/requirements/app/tools/reporting/pdf/layout_inline.py#L8) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : core.wrap_long_words, core.write_wrapped, len, line.rstrip, min, pdf.ln, pdf.set_font, raw.lstrip, raw.strip, re.sub, stripped.lstrip, stripped.startswith, stripped[level:].strip. Usages candidats : 1.

## tools/reporting/pdf/markdown.py

- [`strip_markdown_inline`](../../srcs/requirements/app/tools/reporting/pdf/markdown.py#L7) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : heading_match.group, heading_match.group(1).strip, re.match, re.sub. Usages candidats : 7.
- [`normalize_markdown_lines`](../../srcs/requirements/app/tools/reporting/pdf/markdown.py#L21) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : '; '.join, c.strip, cleaned.append, line.rstrip, raw.strip, raw.strip().startswith, re.compile, strip_markdown_inline, stripped.endswith, stripped.startswith, stripped.strip, stripped.strip('|').split, table_sep.match. Usages candidats : 1.
- [`is_table_separator`](../../srcs/requirements/app/tools/reporting/pdf/markdown.py#L46) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : bool, re.match. Usages candidats : 3.
- [`parse_table_row`](../../srcs/requirements/app/tools/reporting/pdf/markdown.py#L50) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : cell.strip, line.strip, line.strip().strip, strip_markdown_inline, stripped.split. Usages candidats : 4.
- [`is_list_item`](../../srcs/requirements/app/tools/reporting/pdf/markdown.py#L55) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : line.lstrip, stripped.startswith. Usages candidats : 4.
- [`split_semicolon_row`](../../srcs/requirements/app/tools/reporting/pdf/markdown.py#L60) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : part.strip, text.split. Usages candidats : 1.
- [`semicolon_table_rows`](../../srcs/requirements/app/tools/reporting/pdf/markdown.py#L64) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : counts.pop, len, split_semicolon_row. Usages candidats : 1.
- [`parse_markdown_blocks`](../../srcs/requirements/app/tools/reporting/pdf/markdown.py#L75) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : ' '.join, ' '.join(paragraph).strip, blocks.append, is_list_item, is_table_separator, items.append, len, line.lstrip, line.startswith, line[level:].strip, list, paragraph.append, parse_table_row, peek.strip, peek.strip().startswith, raw.strip, raw.strip().startswith, raw_lines[i].lstrip, raw_lines[i].lstrip()[2:].strip, raw_lines[i].rstrip, row_line.strip, rows.append, semicolon_table_rows, strip_markdown_inline, strip_markdown_inline(raw).strip. Usages candidats : 1.

## tools/reporting/pdf/renderer.py

- [`_init_pdf`](../../srcs/requirements/app/tools/reporting/pdf/renderer.py#L11) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : hasattr, layout.configure_document, pdf.alias_nb_pages, pdf_cls. Usages candidats : 3.
- [`_render_enterprise_pass`](../../srcs/requirements/app/tools/reporting/pdf/renderer.py#L19) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : layout.assign_toc_page, layout.render_blocks, layout.render_cover, layout.render_toc, pdf.page_no. Usages candidats : 2.
- [`_render_enterprise_pass.on_heading`](../../srcs/requirements/app/tools/reporting/pdf/renderer.py#L31) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : layout.assign_toc_page, pdf.page_no. Usages candidats : 1.
- [`render_markdown_to_pdf`](../../srcs/requirements/app/tools/reporting/pdf/renderer.py#L42) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : RuntimeError, _init_pdf, core.is_valid_pdf, core.iter_lines, core.safe_text, layout.render_line, markdown.normalize_markdown_lines, output_path.parent.mkdir, pdf.ln, pdf.multi_cell, pdf.output, pdf.set_font, str. Usages candidats : 5.
- [`render_enterprise_pdf`](../../srcs/requirements/app/tools/reporting/pdf/renderer.py#L61) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : RuntimeError, _init_pdf, _render_enterprise_pass, core.is_valid_pdf, core.iter_lines, layout.build_toc_entries, markdown.parse_markdown_blocks, output_path.parent.mkdir, pdf.output, str. Usages candidats : 1.
- [`render_report_pdf`](../../srcs/requirements/app/tools/reporting/pdf/renderer.py#L80) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : (style or 'basic').lower, render_enterprise_pdf, render_markdown_to_pdf. Usages candidats : 1.

## tools/reporting/pdf/styles.py


## tools/reporting/pdf/table.py

- [`_normalize_header_cell`](../../srcs/requirements/app/tools/reporting/pdf/table.py#L12) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : normalized.encode, normalized.encode('ascii', 'ignore').decode, re.sub, re.sub('[^a-z0-9]+', ' ', stripped.lower()).strip, stripped.lower, unicodedata.normalize. Usages candidats : 1.
- [`_table_weights`](../../srcs/requirements/app/tools/reporting/pdf/table.py#L18) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : ' '.join, _normalize_header_cell, len. Usages candidats : 1.
- [`_normalize_row_cells`](../../srcs/requirements/app/tools/reporting/pdf/table.py#L37) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : ' / '.join, len. Usages candidats : 3.
- [`_calc_table_widths`](../../srcs/requirements/app/tools/reporting/pdf/table.py#L48) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : _normalize_row_cells, _table_weights, core.safe_text, len, max, pdf.get_string_width, range, sum. Usages candidats : 1.
- [`render_table`](../../srcs/requirements/app/tools/reporting/pdf/table.py#L88) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : _calc_table_widths, _normalize_row_cells, core.safe_text, core.wrap_to_width, enumerate, len, markdown.strip_markdown_inline, max, pdf.add_page, pdf.cell, pdf.get_y, pdf.ln, pdf.rect, pdf.set_fill_color, pdf.set_font, pdf.set_xy, pdf.set_y, render_row, str, wrapped_rows.append. Usages candidats : 1.
- [`render_table.render_row`](../../srcs/requirements/app/tools/reporting/pdf/table.py#L98) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : _normalize_row_cells, core.safe_text, core.wrap_to_width, enumerate, len, markdown.strip_markdown_inline, max, pdf.add_page, pdf.cell, pdf.get_y, pdf.rect, pdf.set_fill_color, pdf.set_font, pdf.set_xy, pdf.set_y, render_row, str, wrapped_rows.append. Usages candidats : 3.

## tools/reporting/pdf_export.py


## tools/reporting/report.py

- [`write_report`](../../srcs/requirements/app/tools/reporting/report.py#L9) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : ReportWriter, export_additional_views, normalize_results, reporter.write. Usages candidats : 6.

## tools/reporting/report_sections.py

- [`_truncate`](../../srcs/requirements/app/tools/reporting/report_sections.py#L15) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : isinstance, len. Usages candidats : 1.
- [`format_status`](../../srcs/requirements/app/tools/reporting/report_sections.py#L23) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : _STATUS_LABELS.get. Usages candidats : 2.
- [`build_markdown_section`](../../srcs/requirements/app/tools/reporting/report_sections.py#L31) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : ', '.join, _truncate, format_status, keywords.items, len, lines.append, res.get. Usages candidats : 2.
- [`build_json_entry`](../../srcs/requirements/app/tools/reporting/report_sections.py#L62) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : dict. Usages candidats : 1.

## tools/reporting/report_writer.py

- [`ReportWriter.__init__`](../../srcs/requirements/app/tools/reporting/report_writer.py#L11) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : (self.output_conf.get('filter') or {}).get, Path, bool, fmt.lower, self.output_conf.get. Usages candidats : 0.
- [`ReportWriter.write`](../../srcs/requirements/app/tools/reporting/report_writer.py#L18) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : Path, ReportWriter, ReportWriter(extra_conf).write, ReportWriter(output_conf).write, base.with_suffix, build_reporter, dict, extra_conf.get, extra_conf.pop, is_vuln_entry, normalize_results, reporter.write, str. Usages candidats : 19.

## tools/reporting/threat_evidence.py

- [`build_evidence`](../../srcs/requirements/app/tools/reporting/threat_evidence.py#L26) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : ' '.join, (str(source.get('url')) + '\n' + text).encode, IDENTIFIERS.findall, PATTERNS.items, datetime.fromisoformat, datetime.fromisoformat(record['last_online']).date, datetime.now, datetime.now(timezone.utc).date, evidence.setdefault, evidence.values, hashlib.sha256, hashlib.sha256((str(source.get('url')) + '\n' + text).encode()).hexdigest, isinstance, json.loads, list, pattern.search, record.get, record.items, set, sorted, source.get, str, text.strip, types.add. Usages candidats : 8.
- [`select_evidence`](../../srcs/requirements/app/tools/reporting/threat_evidence.py#L73) — Round robin prevents a large first feed from hiding all other sources.
  Appels effectués : groups.setdefault, groups.setdefault(item['url'], []).append, groups.values, item['text'].strip, len, range, selected.append. Usages candidats : 2.
- [`coverage`](../../srcs/requirements/app/tools/reporting/threat_evidence.py#L88) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : Counter, dict, len, source.get, sum. Usages candidats : 1.

## tools/result_entry.py

- [`ResultEntry.to_dict`](../../srcs/requirements/app/tools/result_entry.py#L34) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : data.update. Usages candidats : 6.
- [`ResultEntry._keys`](../../srcs/requirements/app/tools/result_entry.py#L50) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : keys.append, keys.extend, self.extra.keys. Usages candidats : 2.
- [`ResultEntry.__getitem__`](../../srcs/requirements/app/tools/result_entry.py#L66) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : KeyError, getattr. Usages candidats : 0.
- [`ResultEntry.get`](../../srcs/requirements/app/tools/result_entry.py#L75) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : aucun appel explicite. Usages candidats : 582.
- [`ResultEntry.__setitem__`](../../srcs/requirements/app/tools/result_entry.py#L81) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : setattr. Usages candidats : 0.
- [`ResultEntry.__delitem__`](../../srcs/requirements/app/tools/result_entry.py#L90) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : KeyError. Usages candidats : 0.
- [`ResultEntry.__iter__`](../../srcs/requirements/app/tools/result_entry.py#L99) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : iter, self._keys. Usages candidats : 0.
- [`ResultEntry.__len__`](../../srcs/requirements/app/tools/result_entry.py#L102) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : len, self._keys. Usages candidats : 0.
- [`as_dict`](../../srcs/requirements/app/tools/result_entry.py#L106) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : dict, isinstance, result.to_dict. Usages candidats : 1.
- [`normalize_results`](../../srcs/requirements/app/tools/result_entry.py#L112) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : as_dict. Usages candidats : 5.

## tools/scheduling.py

- [`parse_interval_seconds`](../../srcs/requirements/app/tools/scheduling.py#L14) — Convertit un intervalle sous forme str ou int en secondes. Accepte "6h", "15m", "30s", "1d" ou un entier (secondes).
  Appels effectués : int, isinstance, text.endswith, to_int, value.strip, value.strip().lower. Usages candidats : 6.
- [`load_schedule_config`](../../srcs/requirements/app/tools/scheduling.py#L52) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : ScheduleConfig, parse_interval_seconds, raw.get, to_bool, to_int. Usages candidats : 2.
- [`_resolve_timezone`](../../srcs/requirements/app/tools/scheduling.py#L65) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : ZoneInfo. Usages candidats : 1.
- [`compute_initial_delay`](../../srcs/requirements/app/tools/scheduling.py#L74) — Retourne le délai (secondes) avant le premier run, en fonction de start_time HH:MM. Si start_time est passé, planifie pour le lendemain.
  Appels effectués : (target - now).total_seconds, _resolve_timezone, dt.datetime.now, dt.timedelta, int, now.astimezone, now.replace, start_time.split. Usages candidats : 5.

## tools/scorer.py

- [`_count_iocs`](../../srcs/requirements/app/tools/scorer.py#L26) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : IOC_PATTERNS.values, isinstance, len, pattern.findall, seen.add, set. Usages candidats : 1.
- [`_has_cve`](../../srcs/requirements/app/tools/scorer.py#L37) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : IOC_PATTERNS['cve'].search, isinstance. Usages candidats : 1.
- [`_priority_from_score`](../../srcs/requirements/app/tools/scorer.py#L46) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : aucun appel explicite. Usages candidats : 1.
- [`_compute_score`](../../srcs/requirements/app/tools/scorer.py#L54) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : _count_iocs, keywords.items, min, per_type.get, res.get, type_weights.get, weights.get. Usages candidats : 1.
- [`compute_confidence`](../../srcs/requirements/app/tools/scorer.py#L80) — Heuristique simple de confiance (0..1) basée sur le statut, les extraits et les mots-clés.
  Appels effectués : (res.get('status') or '').lower, keywords.get, len, max, min, res.get. Usages candidats : 6.
- [`score_results`](../../srcs/requirements/app/tools/scorer.py#L100) — Retourne une copie des résultats avec deux champs supplémentaires : - score (int) : heuristique de priorité - priority (str) : high/medium/low
  Appels effectués : _compute_score, _has_cve, _priority_from_score, bool, cvss_conf.get, deepcopy, entry.get, entry.get('keywords', {}).get, float, scored.append. Usages candidats : 4.

## tools/secrets.py

- [`get_secret`](../../srcs/requirements/app/tools/secrets.py#L18) — Rôle non documenté ; consulter les opérations et le corps de la fonction.
  Appels effectués : client.secrets.kv.v2.read_secret_version, data.get, hvac.Client, os.getenv, resp.get, resp.get('data', {}).get. Usages candidats : 10.
