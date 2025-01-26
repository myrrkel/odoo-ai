# Copyright (C) 2025 - Michel Perrocheau (https://github.com/myrrkel).
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
import anthropic
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class AIProvider(models.Model):
    _inherit = 'ai.provider'

    code = fields.Selection(selection_add=[('anthropic', 'Anthropic')], ondelete={'anthropic': 'cascade'})

    def get_ai_model_list(self):
        if not self.code == 'anthropic':
            return super(AIProvider, self).get_ai_model_list()
        try:
            ai_client = self.get_ai_client()
        except Exception as err:
            _logger.error(err)
            return [('claude-3-5-sonnet', 'Claude 3.5 Sonnet')]
        model_list = ai_client.models.list()
        res = [(m.id, m.id) for m in model_list.data]
        res.sort()
        return res

    def get_ai_client(self):
        if not self.code == 'anthropic':
            return super(AIProvider, self).get_ai_client()
        if not self.api_key:
            raise UserError(_('Anthropic API key is required.'))
        client = anthropic.Anthropic(api_key=self.api_key, base_url=self.base_url or None)
        return client
