# Copyright (C) 2025 - Michel Perrocheau (https://github.com/myrrkel).
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class AICompletion(models.Model):
    _inherit = 'ai.completion'

    n = fields.Integer(string='Number of results', default=1)
    stop = fields.Char()
    frequency_penalty = fields.Float()
    presence_penalty = fields.Float()

    def prepare_message(self, message, rec_id=0):
        if not self.ai_provider == 'anthropic':
            return super(AICompletion, self).prepare_message(message, rec_id)
        if message.get('role') == 'tool':
            return {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": message.get('tool_call_id'),
                        "content": message.get('content')
                    }
                ]
            }
        if self.vision:
            message = self.prepare_message_image(message, rec_id)
        return message

    def prepare_message_image_content(self, image_binary):
        if not self.ai_provider == 'anthropic':
            return super(AICompletion, self).prepare_message_image_content(image_binary)
        image_content ={
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": 'image/jpeg',
                        "data": image_binary,
                    },
                }
        return image_content

    def get_completion(self, completion_params):
        if self.ai_provider == 'anthropic':
            ai_client = self.get_ai_client()
            return ai_client.messages.create(**completion_params)
        return super(AICompletion, self).get_completion(completion_params)


    def get_tools_params(self):
        if self.ai_provider == 'anthropic':
            return {'tools': [t.get_tool_dict('anthropic') for t in self.tool_ids]}
        return super(AICompletion, self).get_tools_params()

    def get_tool_call_values(self, tool_call):
        if self.ai_provider == 'anthropic':
            return {'function': tool_call.name, 'arguments': tool_call.input}
        return super(AICompletion, self).get_tool_call_values(tool_call)

    def get_completion_results(self, rec_id, messages, **kwargs):
        if not self.ai_provider == 'anthropic':
            return super(AICompletion, self).get_completion_results(rec_id, messages, **kwargs)

        _logger.info(f'Create completion: {messages}')
        completion_params = self.get_completion_params(messages, kwargs)
        choice = self.get_completion(completion_params)
        message = '\n'.join([m.text for m in choice.content if m.type == 'text'])
        if choice.stop_reason == 'tool_use':
            for tool_call in [m for m in choice.content if m.type == 'tool_use']:
                messages.append({"role": "assistant", "content": choice.content})
                tool_result = self.run_tool_call(tool_call)
                messages.append(self.prepare_message(tool_result))
                return self.get_completion_results(rec_id, messages, **kwargs)

        total_tokens = choice.usage.input_tokens + choice.usage.output_tokens

        return [message], choice.usage.input_tokens, choice.usage.output_tokens, total_tokens