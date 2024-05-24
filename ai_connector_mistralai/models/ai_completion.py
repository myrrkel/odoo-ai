# Copyright (C) 2024 - Michel Perrocheau (https://github.com/myrrkel).
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from mistralai.models.chat_completion import ChatMessage
from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class AICompletion(models.Model):
    _inherit = 'ai.completion'

    def prepare_messages(self, messages):
        if self.ai_provider == 'mistralai':
            messages = [ChatMessage(role=m['role'], content=m['content']) for m in messages]
            return messages
        return super(AICompletion, self).prepare_messages(messages)

    @api.onchange('ai_provider_id')
    def _onchange_ai_provider_id(self):
        if not self.ai_provider_id or self.ai_model_id not in self.ai_provider_id.ai_model_ids:
            self.ai_model_id = False
