# Copyright (C) 2024 - Michel Perrocheau (https://github.com/myrrkel).
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import models, fields, api, _

import logging

_logger = logging.getLogger(__name__)


class AIModel(models.Model):
    _name = 'ai.model'
    _description = 'AI Model'

    active = fields.Boolean(default=True)
    name = fields.Char(required=True)
    display_name = fields.Char()
    ai_provider_id = fields.Many2one('ai.provider', string='AI Provider', required=True)
