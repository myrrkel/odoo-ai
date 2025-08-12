# Copyright (C) 2024 - Michel Perrocheau (https://github.com/myrrkel).
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class AIAgent(models.Model):
    _name = 'ai.agent'
    _description = 'AI Agent'

    name = fields.Char(required=True)
    external_id = fields.Char(string='External ID', readonly=True, copy=False)
    description = fields.Text()
    instructions = fields.Text()
    web_search = fields.Boolean()
    ai_provider_id = fields.Many2one('ai.provider', string='AI Provider', required=False,
                                     default=lambda self: self.env['ai.provider'].search([], limit=1))
    ai_model_id = fields.Many2one('ai.model', string='AI Model',
                                  default=lambda self: self.env['ai.model'].search([], limit=1))
    ai_provider = fields.Selection(string='AI Provider Code', related='ai_provider_id.code')
    tool_ids = fields.Many2many('ai.tool', string='Tools', copy=True)
    temperature = fields.Float(default=1)
    top_p = fields.Float(default=1)

    def get_ai_client(self):
        return self.ai_provider_id.get_ai_client()

    def _create_agent(self, create_params):
        raise NotImplementedError("Agent creation not implemented for %s" % self.ai_provider_id.name)

    def _start_conversation(self, conversation_params):
        raise NotImplementedError("Start conversation not implemented for %s" % self.ai_provider_id.name)

    def create_agent(self):
        create_params = {'model': self.ai_model_id.name,
                         'description': self.description,
                         'name': self.name,
                         'instructions': self.instructions}
        if self.web_search:
            create_params['tools'] = [{'type': 'web_search'}]
        if self.tool_ids:
            tools = [t.get_tool_dict() for t in self.tool_ids]
            if 'tools' not in create_params:
                create_params['tools'] = tools
            else:
                create_params['tools'].extend(tools)

        create_params['completion_args'] = {'temperature': self.temperature,
                                            'top_p': self.top_p}

        res = self._create_agent(create_params)
        self.external_id = res.id
        return res

    def get_completion(self, completion_params):
        conversation_params = {'agent_id': self.external_id,
                               'inputs': completion_params.get('messages', [])
                               }
        try:
            res = self._start_conversation(conversation_params)
        except Exception as err:
            _logger.error(err)
            raise UserError(err)
        return res
