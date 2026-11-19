# Copyright (C) 2024 - Michel Perrocheau (https://github.com/myrrkel).
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from unittest.mock import patch

from mistralai.client.models import ChatCompletionResponse

from odoo.tests.common import TransactionCase, tagged

ANSWER = '{"ocr_score": 100, "amount": 42.5}'


def _make_response(content):
    """Build a Mistral chat completion response parsed by the SDK, as returned by ``chat.complete``."""
    return ChatCompletionResponse.model_validate({
        'id': 'test',
        'object': 'chat.completion',
        'model': 'mistral-large-latest',
        'created': 1,
        'usage': {'prompt_tokens': 10, 'completion_tokens': 20, 'total_tokens': 30},
        'choices': [{
            'index': 0,
            'finish_reason': 'stop',
            'message': {'role': 'assistant', 'tool_calls': None, 'content': content},
        }],
    })


@tagged('post_install', '-at_install')
class TestAICompletionMistral(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        provider = cls.env.ref('ai_connector_mistralai.mistralai')
        ai_model = cls.env['ai.model'].create({'name': 'mistral-large-test', 'ai_provider_id': provider.id})
        cls.completion = cls.env['ai.completion'].create({
            'name': 'Test Mistral completion',
            'ai_provider_id': provider.id,
            'ai_model_id': ai_model.id,
            'response_format': 'json_object',
        })

    def _run_completion(self, content):
        with patch.object(type(self.completion), 'get_completion', return_value=_make_response(content)):
            return self.completion.create_completion(prompt='Extract the expense data')

    def test_reasoning_content_keeps_text_chunks_only(self):
        """A reasoning model answer (thinking chunk + text chunk) returns only the text answer."""
        content = [
            {'type': 'thinking', 'thinking': [{'type': 'text', 'text': 'The invoice total is {42.5}.'}]},
            {'type': 'text', 'text': ANSWER},
        ]
        self.assertEqual(self._run_completion(content), [ANSWER])

    def test_string_content_unchanged(self):
        """A non reasoning model answer (plain string content) is returned unchanged."""
        self.assertEqual(self._run_completion(ANSWER), [ANSWER])

    def test_reasoning_effort_param(self):
        """The reasoning effort is sent to Mistral as a top-level parameter, only when it is set."""
        self.assertNotIn('reasoning_effort', self.completion.get_completion_params([], {}))
        self.completion.reasoning_effort = 'low'
        self.assertEqual(self.completion.get_completion_params([], {})['reasoning_effort'], 'low')
        self.assertEqual(
            self.completion.get_completion_params([], {'reasoning_effort': 'high'})['reasoning_effort'], 'high')
