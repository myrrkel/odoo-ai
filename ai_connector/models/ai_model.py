# Copyright (C) 2024 - Michel Perrocheau (https://github.com/myrrkel).
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import models, fields, api, _

import logging

_logger = logging.getLogger(__name__)


class AIModel(models.Model):
    _name = 'ai.model'
    _description = 'AI Model'
    _order = 'ai_provider_sequence, default desc, sequence'

    active = fields.Boolean(default=True)
    default = fields.Boolean()
    sequence = fields.Integer()
    name = fields.Char(required=True)
    display_name = fields.Char()
    ai_provider_id = fields.Many2one('ai.provider', string='AI Provider', required=True, index=True, ondelete='cascade')
    ai_provider_sequence = fields.Integer(related='ai_provider_id.sequence', string='AI Provider Sequence',
                                          store=True, index=True)
