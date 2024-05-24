# Copyright (C) 2024 - Michel Perrocheau (https://github.com/myrrkel).
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from mistralai.models.chat_completion import ChatMessage
from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class AICompletion(models.Model):
    _inherit = 'ai.completion'

    n = fields.Integer(string='Number of results', default=1)
    stop = fields.Char()
    frequency_penalty = fields.Float()
    presence_penalty = fields.Float()

    def prepare_messages(self, messages):
        return super(AICompletion, self).prepare_messages(messages)

    def get_completion_results(self, messages, **kwargs):
        if not self.ai_provider == 'openai':
            return super(AICompletion, self).get_completion_results(messages, **kwargs)
        ai_client = self.get_ai_client()
        stop = kwargs.get('stop', self.stop or '')
        if isinstance(stop, str) and ',' in stop:
            stop = stop.split(',')
        response_format = {'type': kwargs.get('response_format', self.response_format) or 'text'}
        model = self.ai_model_id.name or kwargs.get('model', 'gpt-3.5-turbo') #or self.fine_tuning_id.fine_tuned_model
        temperature = self.temperature or kwargs.get('temperature', 0)
        top_p = self.top_p or kwargs.get('top_p', 0)
        max_tokens = kwargs.get('max_tokens', self.max_tokens or 3000)
        # tools = [t.get_tool_dict() for t in self.tool_ids] if self.tool_ids else None
        _logger.info(f'Create completion: {messages}')
        res = ai_client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            n=self.n or 1,
            temperature=temperature,
            top_p=top_p,
            frequency_penalty=self.frequency_penalty,
            presence_penalty=self.presence_penalty,
            stop=stop,
            response_format=response_format,
            # tools=tools,
            # tool_choice='auto' if tools else None,
        )
        return res.choices, res.usage.prompt_tokens, res.usage.completion_tokens, res.usage.total_tokens
