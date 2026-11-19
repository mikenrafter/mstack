#!/usr/bin/env python3
"""Round-trip this graph through a temporary pinned Paneweft CLI runtime."""
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tarfile
import tempfile

HERE = Path(__file__).resolve().parent
REPOSITORY = HERE.parents[4] / 'paneweft'
REVISION = '2c7b9e2e1002e2352d8a3b117da0b0041b2f1f52'


def main():
    bundle_path = HERE / 'paneweft.bundle.json'
    bundle = json.loads(bundle_path.read_text())
    view = bundle['views'][0]
    record = {'cli_revision': REVISION,
              'bundle_sha256': hashlib.sha256(bundle_path.read_bytes()).hexdigest(), 'checks': []}
    try:
        with tempfile.TemporaryDirectory(prefix='review-evidence-cli-') as directory:
            temporary = Path(directory)
            archive = subprocess.check_output(['git', '--no-replace-objects', '-C', str(REPOSITORY),
                'archive', REVISION, 'src', 'packages', 'package.json'])
            with tarfile.open(fileobj=io.BytesIO(archive)) as source:
                source.extractall(temporary, filter='data')
            package = json.loads((temporary / 'package.json').read_text())
            (temporary / 'package.json').write_text(json.dumps(
                {'private': True, 'type': 'module', 'dependencies': package['dependencies']}))
            installed = subprocess.run(['npm', 'install', '--ignore-scripts', '--no-audit', '--no-fund'],
                cwd=temporary, capture_output=True, text=True, timeout=90)
            record['install'] = {'exit_code': installed.returncode, 'stdout': installed.stdout[-1000:],
                                  'stderr': installed.stderr[-1000:]}
            if installed.returncode:
                raise RuntimeError('Temporary runtime install failed')
            record['resolved_dependencies'] = json.loads((temporary / 'package-lock.json').read_text())
            session = str(temporary / 'session')
            cli = ['node', str(temporary / 'src/cli/bin.ts')]
            operations = [('validate', ['validate', '--file', str(bundle_path)]),
                          ('render', ['render', '--file', str(bundle_path), '--session', session]),
                          ('inspect', ['inspect', '--view', view['id'], '--snapshot', view['snapshotId'],
                                       '--session', session, '--max-bytes', '32768'])]
            for name, arguments in operations:
                run = subprocess.run(cli + arguments + ['--format', 'json'],
                    capture_output=True, text=True, timeout=30)
                record['checks'].append({'name': name, 'exit_code': run.returncode,
                                        'stdout': run.stdout, 'stderr': run.stderr})
                if run.returncode:
                    raise RuntimeError(f'Paneweft {name} failed')
                if name == 'inspect':
                    reply = json.loads(run.stdout)
                    expected = {edge['id']: edge for edge in view['data']['edges']}
                    actual = {edge['id']: edge for edge in reply['items']}
                    if actual != expected or reply['counts']['truncated'] or reply['cursor']:
                        raise RuntimeError('Graph edge evidence changed or was truncated')
                    if reply['freshness']['status'] == 'fresh':
                        raise RuntimeError('Unregistered historical evidence must not imply current freshness')
                    record['roundtrip_edges'] = len(actual)
                    record['freshness'] = reply['freshness']
                    record['provenance'] = reply['provenance']
            record['passed'] = True
    except Exception as error:
        record['passed'] = False
        record['error'] = str(error)
    (HERE / 'cli-checks.json').write_text(json.dumps(record, indent=2)+'\n')
    print(json.dumps({key: value for key, value in record.items()
                      if key not in {'checks', 'resolved_dependencies'}}, indent=2))
    raise SystemExit(0 if record['passed'] else 1)


if __name__ == '__main__':
    main()
