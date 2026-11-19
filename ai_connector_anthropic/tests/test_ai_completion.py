# Copyright (C) 2025 - Michel Perrocheau (https://github.com/myrrkel).
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestAICompletionAnthropic(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        provider = cls.env.ref('ai_connector_anthropic.anthropic')
        ai_model = cls.env['ai.model'].create({'name': 'claude-test', 'ai_provider_id': provider.id})
        cls.completion = cls.env['ai.completion'].create({
            'name': 'Test Anthropic completion',
            'ai_provider_id': provider.id,
            'ai_model_id': ai_model.id,
        })

    def test_reasoning_effort_sent_as_output_config(self):
        """The reasoning effort is sent to Anthropic as output_config.effort, through extra_body."""
        self.completion.reasoning_effort = 'medium'
        params = self.completion.get_completion_params([], {})
        self.assertNotIn('reasoning_effort', params)
        self.assertEqual(params['extra_body'], {'output_config': {'effort': 'medium'}})

    def test_no_reasoning_effort(self):
        """Without reasoning effort, no effort parameter is sent to Anthropic."""
        params = self.completion.get_completion_params([], {})
        self.assertNotIn('reasoning_effort', params)
        self.assertNotIn('extra_body', params)
