# Copyright (C) 2024 - Michel Perrocheau (https://github.com/myrrkel).
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from mistralai.models.chat_completion import ChatMessage
from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class AICompletion(models.Model):
    _inherit = 'ai.completion'

    def prepare_message(self, message):
        if self.ai_provider == 'mistralai' and isinstance(message, dict):
            return ChatMessage(**message)
        return super(AICompletion, self).prepare_message(message)
