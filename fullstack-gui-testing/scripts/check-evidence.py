#!/usr/bin/env python3
"""Read an audit manifest and detect contradictory evidence claims. Stdlib only."""
import argparse
import json
from pathlib import Path
import sys


def validate(data, root):
    issues = []
    if not isinstance(data, dict) or data.get('version') != 1:
        return ['Expected an object with version: 1']
    checks = data.get('checks')
    if not isinstance(checks, list) or not checks:
        return ['checks must be a nonempty list']
    by_id = {}

    def files(values, label):
        if not isinstance(values, list) or not all(isinstance(v, str) and v for v in values):
            issues.append(f'{label}: expected a list of relative artifact paths')
            return []
        for value in values:
            target = (root / value).resolve()
            if not target.is_relative_to(root) or Path(value).is_absolute():
                issues.append(f'{label}: artifact escapes manifest directory')
            elif not target.is_file():
                issues.append(f'{label}: missing artifact {value}')
        return values

    for index, check in enumerate(checks):
        if not isinstance(check, dict):
            issues.append(f'checks[{index}]: expected an object')
            continue
        ident = check.get('id')
        if not isinstance(ident, str) or not ident:
            issues.append(f'checks[{index}]: missing id')
            continue
        if ident in by_id:
            issues.append(f'{ident}: duplicate id')
        by_id[ident] = check
        status = check.get('status')
        if status not in {'passed', 'failed', 'blocked', 'skipped'}:
            issues.append(f'{ident}: invalid status')
        if check.get('layer') not in {'unit', 'api', 'integration', 'gui', 'performance'}:
            issues.append(f'{ident}: invalid layer')
        if check.get('fidelity') not in {'real', 'fixture', 'simulated'}:
            issues.append(f'{ident}: invalid fidelity')
        evidence = files(check.get('evidence', []), f'{ident}.evidence')
        if status in {'passed', 'failed'} and not evidence:
            issues.append(f'{ident}: executed check needs evidence')
        if status == 'passed' and check.get('failures'):
            issues.append(f'{ident}: failures contradict passed status')
        sources = check.get('source_results', [])
        if not isinstance(sources, list):
            issues.append(f'{ident}: source_results must be a list')
            sources = []
        for source in sources:
            if not isinstance(source, dict):
                issues.append(f'{ident}: source result must be an object')
                continue
            source_files = files([source.get('file')], f'{ident}.source_results')
            fields = source.get('failure_fields')
            if not isinstance(fields, list) or not fields or not all(isinstance(f, str) and f for f in fields):
                issues.append(f'{ident}: source result needs explicit failure_fields')
                continue
            if not source_files:
                continue
            target = (root / source_files[0]).resolve()
            if not target.is_relative_to(root) or not target.is_file():
                continue
            try:
                source_data = json.loads(target.read_text(encoding='utf-8-sig'))
                if not isinstance(source_data, dict):
                    raise ValueError('expected JSON object')
            except (OSError, ValueError) as error:
                issues.append(f'{ident}: cannot read source result: {error}')
                continue
            if status == 'passed' and any(source_data.get(field) for field in fields):
                issues.append(f'{ident}: source result contains declared failures')
        if check.get('stateful') and status == 'passed':
            if not files(check.get('readback_evidence', []), f'{ident}.readback_evidence'):
                issues.append(f'{ident}: stateful pass needs readback evidence')
        if check.get('visual') and status == 'passed':
            reviews = check.get('visual_review', [])
            if not isinstance(reviews, list) or not reviews:
                issues.append(f'{ident}: visual pass needs a review of opened screenshots')
                continue
            for review in reviews:
                if not isinstance(review, dict) or not isinstance(review.get('notes'), str) or not review.get('notes', '').strip():
                    issues.append(f'{ident}: visual review needs notes')
                    continue
                files([review.get('file')], f'{ident}.visual_review')
                if review.get('verdict') != 'passed':
                    issues.append(f'{ident}: visual review contradicts passed status')
                if review.get('file') not in evidence:
                    issues.append(f'{ident}: reviewed screenshot absent from evidence')
    if data.get('all_passed') is True and any(c.get('status') != 'passed' or c.get('failures') for c in by_id.values()):
        issues.append('all_passed contradicts failed, blocked or skipped checks')
    claims = data.get('claims', [])
    if not isinstance(claims, list):
        return issues + ['claims must be a list']
    for index, claim in enumerate(claims):
        if not isinstance(claim, dict):
            issues.append(f'claims[{index}]: expected an object')
            continue
        ids = claim.get('check_ids', [])
        if not isinstance(ids, list) or not ids or not all(isinstance(i, str) for i in ids):
            issues.append(f'claims[{index}]: missing supporting check_ids')
            continue
        for ident in ids:
            check = by_id.get(ident)
            if not check or check.get('status') != 'passed' or check.get('failures'):
                issues.append(f'claims[{index}]: unsupported by {ident}')
            elif claim.get('requires_real') is True and check.get('fidelity') != 'real':
                issues.append(f'claims[{index}]: {ident} cannot support a real-system claim')
    return issues


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', type=Path)
    args = parser.parse_args()
    try:
        data = json.loads(args.manifest.read_text(encoding='utf-8-sig'))
        issues = validate(data, args.manifest.resolve().parent)
    except (OSError, ValueError) as error:
        print(json.dumps({'consistent': False, 'issues': [str(error)]}, ensure_ascii=False))
        return 2
    print(json.dumps({'consistent': not issues, 'issues': issues}, ensure_ascii=False, indent=2))
    return 1 if issues else 0


if __name__ == '__main__':
    sys.exit(main())
