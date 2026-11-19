"""Replay one documented fix-induced defect against pinned production sources.

Only the T5/T6 tests in one existing file run. Their qex/cargo peers are fakes;
the production job service, filesystem transactions and cancellation API run.
The same fixed regression-test bytes run against both source revisions.
"""
import hashlib
import io
import json
import os
import shutil
import subprocess
import tarfile
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPOSITORY = HERE.parent.parent.parent.parent / 'paneweft'
BEFORE = '3fa003c'
AFTER = 'd89c0e7b750786a84ef8bf9a468967707333a9eb'


def git(*arguments):
    return subprocess.check_output(['git', '-C', str(REPOSITORY), *arguments])


def main():
    versions = {name: git('rev-parse', sha).decode().strip() for name, sha in
                [('before', BEFORE), ('after', AFTER)]}
    tests = git('show', AFTER + ':src/v1/jobs.test.ts')
    record = dict(versions=versions, test_sha256=hashlib.sha256(tests).hexdigest(),
                  scope='T5/T6 test cases in src/v1/jobs.test.ts only',
                  independent_claim='The retained production code fails the same regression tests that pass after the fix.',
                  limits=['Fake qex and fake cargo; no real runner interoperability claim.',
                          'Test cases were authored as historical regression tests, not newly blinded adjudication.',
                          'One inspected causal example, not a review-allocation success estimate.'], runs=[])
    try:
        with tempfile.TemporaryDirectory(prefix='review-cancel-replay-') as directory:
            root = Path(directory)
            runtime = root / 'runtime'
            runtime.mkdir()
            package = json.loads(git('show', AFTER + ':package.json'))
            runtime_package = dict(private=True, type='module', dependencies={
                **package['dependencies'], 'vitest': package['devDependencies']['vitest']})
            (runtime / 'package.json').write_text(json.dumps(runtime_package))
            install = subprocess.run(['npm', 'install', '--ignore-scripts', '--no-audit', '--no-fund'],
                                     cwd=runtime, capture_output=True, text=True, timeout=120)
            record['install'] = dict(exit_code=install.returncode, stdout=install.stdout[-2000:],
                                     stderr=install.stderr[-2000:])
            if install.returncode:
                raise RuntimeError('Isolated test runtime installation failed')
            record['runtime_lock'] = json.loads((runtime / 'package-lock.json').read_text())
            for name, sha in versions.items():
                target = root / name
                target.mkdir()
                archive = git('archive', sha, 'src', 'test', 'packages', 'fixtures')
                with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
                    tar.extractall(target, filter='data')
                (target / 'src/v1/jobs.test.ts').write_bytes(tests)
                (target / 'package.json').write_text(json.dumps(runtime_package))
                (target / 'node_modules').symlink_to(runtime / 'node_modules', target_is_directory=True)
                config = '''import { defineConfig } from "vitest/config";
import { fileURLToPath } from "node:url";
export default defineConfig({resolve:{alias:[
{find:"@paneweft/sdk/vitest",replacement:fileURLToPath(new URL("./packages/paneweft-ts/src/vitest.ts",import.meta.url))},
{find:"@paneweft/sdk",replacement:fileURLToPath(new URL("./packages/paneweft-ts/src/index.ts",import.meta.url))}
]},test:{include:["src/v1/jobs.test.ts"],testTimeout:30000,hookTimeout:30000,maxWorkers:1,fileParallelism:false}});'''
                (target / 'vitest.config.ts').write_text(config)
                argv = ['node', str(runtime / 'node_modules/vitest/vitest.mjs'), 'run',
                        'src/v1/jobs.test.ts', '--testNamePattern', r'\[T5\]|\[T6\]', '--reporter=json',
                        '--outputFile', str(root / (name + '-result.json'))]
                run = subprocess.run(argv, cwd=target, capture_output=True, text=True, timeout=120,
                                     env={**os.environ, 'NODE_OPTIONS': '--max-old-space-size=512'})
                report_path = root / (name + '-result.json')
                report = json.loads(report_path.read_text()) if report_path.exists() else None
                record['runs'].append(dict(name=name, sha=sha, exit_code=run.returncode,
                                            stdout=run.stdout[-4000:], stderr=run.stderr[-4000:],
                                            test_report=report))
            before, after = record['runs']
            before_report, after_report = before['test_report'], after['test_report']
            record['reproduced'] = bool(before_report and after_report
                and before_report['numFailedTests'] > 0 and after_report['numFailedTests'] == 0
                and after_report['numPassedTests'] == 3 and after['exit_code'] == 0)
    except Exception as error:
        record['error'] = str(error)
        record['reproduced'] = False
    (HERE / 'cancellation-reproduction.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps(dict(reproduced=record['reproduced'], error=record.get('error'),
                          runs=[dict(name=r['name'], exit_code=r['exit_code'],
                                     failed=(r['test_report'] or {}).get('numFailedTests'),
                                     passed=(r['test_report'] or {}).get('numPassedTests')) for r in record['runs']]), indent=2))
    raise SystemExit(0 if record['reproduced'] else 1)


if __name__ == '__main__':
    main()
