# Copyright (C) 2025 - Michel Perrocheau (https://github.com/myrrkel).
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields, api, _

import logging

_logger = logging.getLogger(__name__)


class AITool(models.Model):
    _inherit = 'ai.tool'

    def get_tool_dict(self, tool_format='default'):
        
        if not tool_format == 'anthropic':
            return super(AITool, self).get_tool_dict(tool_format)
        res = {'name': self.name,
               'description': self.description}
        properties = {}
        for property_id in self.property_ids:
            properties[property_id.name] = {'type': property_id.type,
                                            'description': property_id.description}
        if properties:
            parameters = {'type': 'object',
                          'properties': properties}
            required = [p.name for p in self.required_property_ids]
            if required:
                parameters['required'] = required
            res['input_schema'] = parameters
        return res
