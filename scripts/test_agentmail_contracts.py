"""AgentMail documentation/owned JSON/AST guards; not CLI, service or security tests."""
from pathlib import Path
import ast
import json
import re
import unittest

ROOT=Path(__file__).resolve().parents[1]/'skills/active/email/agentmail'
def read(name='SKILL.md'):return (ROOT/name).read_text()

class AgentMailContracts(unittest.TestCase):
    def test_pi_and_separate_install_account_consent(self):
        t=read()
        for x in ('1.8.0','not installed','one approved','bash','not a PTY','signup','no automatic'):
            self.assertIn(x,t)
        self.assertNotIn('through the `terminal` tool',t)
        self.assertNotIn('npm install -g agentmail-cli@latest',t)
    def test_runtime_provenance_not_platform_promise(self):
        t=read()
        for x in ('darwin','linux','Windows','_nodeVersion','dotenv','runtime_verified'):
            self.assertIn(x,t)
    def test_public_and_private_verification_separate(self):
        t=read()
        for x in ('help/version','not consent','organization','region','scope','no automatic'):
            self.assertIn(x,t)
        self.assertNotIn('verify `agentmail inboxes list',t)
    def test_current_cli_shapes_and_body_formats(self):
        t=read('references/core.md')
        for x in ('inboxes messages list','--labels','--page-token','--json -','--format json','API origin'):
            self.assertIn(x,t)
        self.assertNotIn('--label unread',t)
        self.assertNotIn('<message_id>',t)
    def test_pagination_and_extraction_not_complete(self):
        t=read('references/core.md')
        for x in ('next_page_token','NDJSON','page-limit','exit0','partial','not a sanitizer','not full','empty page'):
            self.assertIn(x,t)
    def test_full_approval_idempotency_and_attachments(self):
        t=read('references/core.md')
        for x in ('Bcc','changed since approval','24 hours','409','client_id','not proof of delivery','expires_at','no bearer','no-clobber','Base64','30 MB'):
            self.assertIn(x,t)
    def test_signup_not_recovery_or_free_test_send(self):
        t=read('references/signup.md')
        for x in ('rotates','invalidates','optional','attach-human','24 hours','10 attempts','cannot be retrieved','referrer','not permission','no automatic'):
            self.assertIn(x,t)
        self.assertNotIn('agentmail inboxes:messages send',t)
        self.assertNotIn('--referrer hermes-agent',t)
    def test_webhook_current_payload_raw_verify_and_durable_ack(self):
        t=read('references/webhooks.md')
        for x in ('event_types','inbox_ids','svix-id','svix-timestamp','svix-signature','raw','durable','before','2xx','not authorization','replay','no receiver'):
            self.assertIn(x,t)
        self.assertNotIn('--event-type message.received',t)
    def test_ws_auth_scope_and_gap_not_replay_guarantee(self):
        t=read('references/websockets.md')
        for x in ('2.0.8','Authorization','Subscribed','event_type','message.received','unchecked','headers','unknown','gap','no automatic','inbox_ids'):
            self.assertIn(x,t)
        self.assertNotIn('?api_key=$AGENTMAIL_API_KEY',t)
        self.assertNotIn('print(event.message.subject',t)
    def test_mcp_secret_no_url_or_auto_configuration(self):
        t=read('references/mcp.md')
        for x in ('OAuth','x-api-key','query','no automatic','region','not approval'):
            self.assertIn(x,t)
        self.assertNotIn('?apiKey=',t)
    def test_owned_json_shapes(self):
        examples=[]
        for p in ROOT.rglob('*.md'):
            examples.extend(json.loads(s) for s in re.findall(r'```json\n(.*?)\n```',p.read_text(),re.S))
        self.assertGreaterEqual(len(examples),4)
        webhook=next(x for x in examples if 'url' in x)
        self.assertEqual(webhook['event_types'],['message.received'])
        self.assertEqual(len(webhook['inbox_ids']),1)
        self.assertNotIn('pod_ids',webhook)
        subscription=next(x for x in examples if x.get('type')=='subscribe')
        self.assertTrue(subscription['inbox_ids'])
        self.assertEqual(subscription['event_types'],['message.received'])
        send=next(x for x in examples if 'subject' in x)
        self.assertEqual(send['track_opens'],False)
        self.assertIsInstance(send['labels'],list)
    def test_python_example_inert_no_secret_print_or_connect(self):
        examples=re.findall(r'```python\n(.*?)\n```',read('references/websockets.md'),re.S)
        self.assertTrue(examples)
        for s in examples:
            tree=ast.parse(s)
            self.assertFalse(any(isinstance(n,ast.Call) and (isinstance(n.func,ast.Name) and n.func.id=='print' or isinstance(n.func,ast.Attribute) and n.func.attr=='connect') for n in ast.walk(tree)))

if __name__=='__main__':unittest.main()
