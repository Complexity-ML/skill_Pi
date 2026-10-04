"""Documentation and owned TOML parsing, not CLI, MML, consent or mail tests."""
from pathlib import Path
import re
import unittest
try:
    import tomllib
except ImportError:
    tomllib = None

ROOT = Path(__file__).resolve().parents[1]/'skills/active/email/himalaya'
def text(name='SKILL.md'):return (ROOT/name).read_text()

class HimalayaContracts(unittest.TestCase):
    def test_version_boundary_and_no_remote_shell_install(self):
        t=text()
        for term in ('2.2.1', '--json', '--backend', 'v1', 'not installed'):
            self.assertIn(term,t)
        self.assertNotIn('curl -sSL',t)
        self.assertNotIn('pty=true',t)
        self.assertNotIn('process tool',t)
    def test_current_command_shapes(self):
        t=text()
        for term in ('mailbox list','envelope search','message read','--raw','--mailbox','--from','--to','--dir'):
            self.assertIn(term,t)
        for old in ('himalaya template send','himalaya folder list','--downloads-dir','--output json'):
            self.assertNotIn(old,t)
    def test_read_and_output_not_universal_privacy_or_mime(self):
        t=text()
        for term in ('--seen', 'UTF-8', 'stdout', 'not byte-preserving', 'backend', 'partial'):
            self.assertIn(term,t)
        for term in ('map_while', 'CRLF', 'positional', 'UTF-8'):
            self.assertIn(term,text('references/message-composition.md'))
    def test_send_approval_and_uncertain_queue(self):
        t=text()
        for term in ('Bcc','changed since approval','queued','copy failure','not proof of delivery','do not resend'):
            self.assertIn(term,t)
        self.assertNotIn("sed 's/",t)
    def test_attachments_not_atomic_or_all_or_nothing(self):
        t=text()
        for term in ('1023','not atomic','dangling symlink','partial writes','0700','part IDs'):
            self.assertIn(term,t)
    def test_configuration_source_conflict_and_credentials(self):
        t=text('references/configuration.md')
        for term in ('mailbox.alias','imap.server','smtp.starttls','native keyring','external broker','configure','README','colon','proxy'):
            self.assertIn(term,t)
        self.assertNotIn('backend.auth.raw =',t)
        self.assertNotIn('backend.auth.keyring =',t)
    def test_owned_toml_examples(self):
        if tomllib is None:self.skipTest('tomllib unavailable; no install')
        examples=re.findall(r'```toml\n(.*?)\n```',text('references/configuration.md'),re.S)
        self.assertTrue(examples)
        for example in examples:
            account=tomllib.loads(example)['accounts']['example']
            self.assertEqual(account['imap']['server'],'imaps://imap.example.invalid:993')
            self.assertTrue(account['smtp']['starttls'])
            self.assertIn('command',account['imap']['sasl']['plain']['password'])
    def test_mml_separate_compile_review_and_no_auto_send(self):
        t=text('references/message-composition.md')
        for term in ('standalone','mml compile','RFC 5322','not a sanitizer','attachment','no-clobber','JSON','Bcc','signature'):
            self.assertIn(term,t)
        self.assertNotIn('himalaya template send',t)
        self.assertNotIn('exit the editor to send',t)
        self.assertNotIn('>(himalaya',t)

if __name__=='__main__':unittest.main()
