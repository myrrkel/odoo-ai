# Copyright (C) 2024 - Michel Perrocheau (https://github.com/myrrkel).
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class CreateQuestionAnswerWizard(models.TransientModel):
    _name = 'create.question.answer.wizard'
    _description = "Create Question Answer Wizard"
    completion_result_ids = fields.Many2many('ai.completion.result', string='Completion Results',
                                             default=lambda self: self.env.context.get('active_ids', []))
    answer_type = fields.Selection([('answer', 'Answer'), ('original', 'Original')],
                                   string='Answer Type', default='answer')
    tag_ids = fields.Many2many('ai.question.answer.tag', string='Tags')

    def get_completion_answer(self, completion_result_id):
        if self.answer_type == 'answer':
            return completion_result_id.answer
        if self.answer_type == 'original':
            return completion_result_id.origin_answer or completion_result_id.answer

    def create_question_answer(self):
        for rec in self:
            for completion_result_id in rec.completion_result_ids:
                answer = self.get_completion_answer(completion_result_id)
                create_vals = {'name': completion_result_id.prompt,
                               'answer': answer,
                               'answer_completion_id': completion_result_id.completion_id.id,
                               'model_id': completion_result_id.model_id.id,
                               'res_id': completion_result_id.res_id,
                               'tag_ids': [(6, 0, rec.tag_ids.ids)],
                               }
                self.env['ai.question.answer'].create(create_vals)
        return {'type': 'ir.actions.act_window_close'}
