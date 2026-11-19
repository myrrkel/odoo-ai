# Copyright (C) 2024 - Michel Perrocheau (https://github.com/myrrkel).
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class AICompletion(models.Model):
    _inherit = 'ai.completion'

    def prepare_message(self, message, rec_id=0):
        if self.ai_provider == 'mistralai' and self.vision and 'ocr' in self.ai_model_id.name:
            return self.prepare_message_ocr(rec_id)
        else:
            return super(AICompletion, self).prepare_message(message, rec_id)

    def prepare_message_ocr(self, rec_id):
        image_binary = self.get_image_binary(rec_id)
        if image_binary:
            return self.prepare_message_image_content(image_binary)

    def get_completion_params(self, messages, kwargs):
        if self.ai_provider == 'mistralai' and self.vision and 'ocr' in self.ai_model_id.name:
            if not messages:
                return {}
            model = self.ai_model_id.name or kwargs.get('model', '')
            return {'model': model,
                    'document': messages[0]}
        else:
            return super(AICompletion, self).get_completion_params(messages, kwargs)

    def get_completion(self, completion_params):
        if self.ai_provider == 'mistralai' and self.vision and 'ocr' in self.ai_model_id.name:
            ai_client = self.get_ai_client()
            res =  ai_client.ocr.process(**completion_params)
            return "\n\n".join([f"{p.markdown}" for p in res.pages])
        else:
            return super(AICompletion, self).get_completion(completion_params)

    def get_completion_results(self, rec_id, messages, **kwargs):
        if self.ai_provider == 'mistralai' and self.vision and 'ocr' in self.ai_model_id.name:
            completion_params = self.get_completion_params(messages, kwargs)
            ocr_text = self.get_completion(completion_params)
            return [ocr_text], 0, 0, 0
        choices, prompt_tokens, completion_tokens, total_tokens = super(AICompletion, self).get_completion_results(
            rec_id, messages, **kwargs)
        if self.ai_provider == 'mistralai':
            choices = [self._get_mistral_text_content(content) for content in choices]
        return choices, prompt_tokens, completion_tokens, total_tokens

    @api.model
    def _get_mistral_text_content(self, content):
        """Return the final answer text of a Mistral message content.

        Reasoning models (e.g. Mistral Large 4) return the content as a list of chunks:
        a ``thinking`` chunk holding the reasoning trace, then ``text`` chunks holding the answer.
        Only the ``text`` chunks are kept. A plain string content is returned unchanged.

        :param content: message content returned by the Mistral API (``str``, list of chunks or ``None``)
        :return: the answer text
        :rtype: str
        """
        if isinstance(content, list):
            return ''.join(chunk.text for chunk in content if getattr(chunk, 'type', None) == 'text')
        return content