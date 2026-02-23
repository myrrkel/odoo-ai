# Copyright (C) 2025 - Michel Perrocheau (https://github.com/myrrkel).
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields, api, _

import logging

_logger = logging.getLogger(__name__)


class AIAgent(models.Model):
    _inherit = 'ai.connector.agent'
    _description = 'AI Agent'

    def _create_agent(self, create_params):
        if self.ai_provider == 'mistralai':
            ai_client = self.get_ai_client()
            return ai_client.beta.agents.create(**create_params)
        else:
            return super(AIAgent, self)._create_agent(create_params)

    def _start_conversation(self, conversation_params):
        if self.ai_provider == 'mistralai':
            ai_client = self.get_ai_client()
            return ai_client.beta.conversations.start(**conversation_params)
        else:
            return super(AIAgent, self)._start_conversation(conversation_params)
