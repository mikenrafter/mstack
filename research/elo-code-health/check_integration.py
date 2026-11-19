"""Validate and round-trip the export using an isolated copy of Paneweft's CLI.

Runtime dependencies install only in a temporary directory; subject checkouts
remain untouched. A real CLI failure is recorded and exits nonzero.
"""
import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

import jsonschema
from referencing import Registry, Resource

from replay import HERE, ROOT, write_json

repository = ROOT / 'paneweft'
schema_root = repository / 'src/schemas'
schemas = [json.loads(p.read_text()) for p in schema_root.rglob('*.json')]
registry = Registry().with_resources((s['$id'], Resource.from_contents(s)) for s in schemas if '$id' in s)
bundle_path = HERE / 'paneweft.bundle.json'
bundle = json.loads(bundle_path.read_text())
schema = json.loads((schema_root / 'bundle.schema.json').read_text())
errors = list(jsonschema.Draft202012Validator(schema, registry=registry,
              format_checker=jsonschema.FormatChecker()).iter_errors(bundle))
record = dict(wire_schema_errors=[str(e) for e in errors],
              paneweft_revision=subprocess.check_output(['git', '-C', str(repository),
                                      'rev-parse', 'HEAD'], text=True).strip(),
              bundle_sha256=hashlib.sha256(bundle_path.read_bytes()).hexdigest(),
              checks=[])
try:
    if errors:
        raise RuntimeError('Independent wire-schema validation failed')
    with tempfile.TemporaryDirectory(prefix='elo-paneweft-') as directory:
        temporary = Path(directory)
        shutil.copytree(repository / 'src', temporary / 'src')
        shutil.copytree(repository / 'packages', temporary / 'packages')
        package = json.loads((repository / 'package.json').read_text())
        (temporary / 'package.json').write_text(json.dumps(dict(
            private=True, type='module', dependencies=package['dependencies'])))
        installed = subprocess.run(['npm', 'install', '--ignore-scripts', '--no-audit', '--no-fund'],
                                   cwd=temporary, capture_output=True, text=True, timeout=90)
        record['dependency_install'] = dict(exit_code=installed.returncode,
                                            stdout=installed.stdout[-1500:], stderr=installed.stderr[-1500:])
        if installed.returncode:
            raise RuntimeError('Isolated runtime dependency installation failed')
        record['resolved_dependencies'] = json.loads((temporary / 'package-lock.json').read_text())
        cli = ['node', str(temporary / 'src/cli/bin.ts')]
        session = str(HERE / '.paneweft-session' / record['bundle_sha256'][:16])
        record['session'] = session
        for name, arguments in [
            ('validate', ['validate', '--file', str(bundle_path), '--format', 'json']),
            ('render', ['render', '--file', str(bundle_path), '--session', session, '--format', 'json']),
            ('inspect', ['inspect', '--view', 'health-activity', '--snapshot', bundle['views'][0]['snapshotId'],
                         '--session', session, '--format', 'json']),
        ]:
            run = subprocess.run(cli + arguments, capture_output=True, text=True, timeout=30)
            record['checks'].append(dict(name=name, exit_code=run.returncode,
                                          stdout=run.stdout, stderr=run.stderr))
            if run.returncode:
                raise RuntimeError(f'Paneweft {name} failed')
            if name == 'inspect':
                inspected = json.loads(run.stdout)
                expected = {r['id']: r['cells'] for r in bundle['views'][0]['data']['rows']}
                actual = {r['id']: r['cells'] for r in inspected['items']}
                if actual != expected:
                    raise RuntimeError('Stored rows differ from exported evidence')
                record['roundtrip_rows'] = len(actual)
                record['freshness'] = inspected['freshness']
        record['passed'] = True
except Exception as error:
    record['passed'] = False
    record['error'] = str(error)
write_json('integration-checks.json', record)
print(json.dumps({k: v for k, v in record.items() if k not in {'checks', 'resolved_dependencies'}}, indent=2))
raise SystemExit(0 if record['passed'] else 1)
