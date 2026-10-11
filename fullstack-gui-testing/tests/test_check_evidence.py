import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'check-evidence.py'


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / 'api.json').write_text('{}', encoding='utf-8')
        (self.root / 'screen.png').write_bytes(b'synthetic-test-artifact')

    def tearDown(self):
        self.temp.cleanup()

    def run_manifest(self, checks, claims=None, **extra):
        data = {'version': 1, 'checks': checks, 'claims': claims or [], **extra}
        manifest = self.root / 'evidence.json'
        manifest.write_text(json.dumps(data), encoding='utf-8')
        result = subprocess.run([sys.executable, str(SCRIPT), str(manifest)], capture_output=True, text=True)
        payload = json.loads(result.stdout)
        self.assertIn('issues', payload)
        self.assertEqual(payload['consistent'], result.returncode == 0)
        return result

    def check(self, **overrides):
        return {'id': 'save', 'layer': 'api', 'status': 'passed', 'fidelity': 'real', 'evidence': ['api.json'], **overrides}

    def test_valid_persisted_save(self):
        result = self.run_manifest([self.check(stateful=True, readback_evidence=['api.json'])])
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_passed_stateful_without_readback(self):
        self.assertNotEqual(self.run_manifest([self.check(stateful=True)]).returncode, 0)

    def test_gui_without_visual_review(self):
        self.assertNotEqual(self.run_manifest([self.check(layer='gui', visual=True, evidence=['screen.png'])]).returncode, 0)

    def test_reviewed_gui(self):
        check = self.check(layer='gui', visual=True, evidence=['screen.png'], visual_review=[{'file': 'screen.png', 'verdict': 'passed', 'notes': 'Opened; no clipping in this viewport.'}])
        self.assertEqual(self.run_manifest([check]).returncode, 0)

    def test_failed_visual_cannot_pass(self):
        check = self.check(layer='gui', visual=True, evidence=['screen.png'], visual_review=[{'file': 'screen.png', 'verdict': 'failed', 'notes': 'Submit obscured.'}])
        self.assertNotEqual(self.run_manifest([check]).returncode, 0)

    def test_fixture_cannot_support_real_claim(self):
        claim = {'text': 'Real database save verified', 'check_ids': ['save'], 'requires_real': True}
        self.assertNotEqual(self.run_manifest([self.check(fidelity='fixture')], [claim]).returncode, 0)

    def test_known_bug_does_not_disappear_in_success(self):
        self.assertNotEqual(self.run_manifest([self.check(failures=['Unsaved edit discarded'])], all_passed=True).returncode, 0)

    def test_failed_check_can_be_recorded_honestly(self):
        self.assertEqual(self.run_manifest([self.check(status='failed', failures=['Unsaved edit discarded'])], all_passed=False).returncode, 0)

    def test_all_passed_with_blocked_check(self):
        self.assertNotEqual(self.run_manifest([self.check(status='blocked', evidence=[])], all_passed=True).returncode, 0)

    def test_missing_artifact(self):
        self.assertNotEqual(self.run_manifest([self.check(evidence=['missing.json'])]).returncode, 0)

    def test_outside_artifact_root(self):
        self.assertNotEqual(self.run_manifest([self.check(evidence=['../api.json'])]).returncode, 0)

    def test_duplicate_id(self):
        self.assertNotEqual(self.run_manifest([self.check(), self.check()]).returncode, 0)

    def test_unexecuted_check_is_not_failure(self):
        self.assertEqual(self.run_manifest([self.check(status='skipped', evidence=[])]).returncode, 0)

    def test_claim_requires_successful_referenced_checks(self):
        self.assertNotEqual(self.run_manifest([self.check(status='failed')], [{'text': 'Save works', 'check_ids': ['save'], 'requires_real': False}]).returncode, 0)

    def test_empty_manifest_is_rejected(self):
        self.assertNotEqual(self.run_manifest([]).returncode, 0)

    def test_invalid_json_fails_cleanly(self):
        target = self.root / 'invalid.json'
        target.write_text('{', encoding='utf-8')
        result = subprocess.run([sys.executable, str(SCRIPT), str(target)], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn('Traceback', result.stderr)

    def test_source_result_fatal_contradicts_pass(self):
        (self.root / 'run.json').write_text(json.dumps({'fatal': 'Save never reached', 'defects': []}), encoding='utf-8')
        check = self.check(source_results=[{'file': 'run.json', 'failure_fields': ['fatal', 'defects']}])
        self.assertNotEqual(self.run_manifest([check]).returncode, 0)

    def test_source_result_defects_contradict_pass(self):
        (self.root / 'run.json').write_text(json.dumps({'knownBugs': ['Unsaved edit lost']}), encoding='utf-8')
        check = self.check(source_results=[{'file': 'run.json', 'failure_fields': ['knownBugs']}])
        self.assertNotEqual(self.run_manifest([check]).returncode, 0)

    def test_source_result_clean_can_pass(self):
        (self.root / 'run.json').write_text(json.dumps({'errors': []}), encoding='utf-8')
        check = self.check(source_results=[{'file': 'run.json', 'failure_fields': ['errors']}])
        self.assertEqual(self.run_manifest([check]).returncode, 0)


if __name__ == '__main__':
    unittest.main()
