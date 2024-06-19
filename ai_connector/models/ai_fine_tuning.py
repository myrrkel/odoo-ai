# Copyright (C) 2024 - Michel Perrocheau (https://github.com/myrrkel).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import json
from odoo import models, fields, api, _
from odoo.tools.safe_eval import safe_eval
from odoo.addons.base.models.ir_model import SAFE_EVAL_BASE

import logging

_logger = logging.getLogger(__name__)


class AIFineTuning(models.Model):
    _name = 'ai.fine.tuning'
    _description = 'AI Fine-Tuning'

    name = fields.Char()
    ai_provider_id = fields.Many2one('ai.provider', string='AI Provider', required=True, ondelete='cascade',
                                     default=lambda self: self.env['ai.provider'].search([], limit=1))
    ai_model_id = fields.Many2one('ai.model', string='AI Model', required=True, ondelete='cascade',
                                  default=lambda self: self.env['ai.model'].search([], limit=1))
    ai_provider = fields.Selection(string='AI Provider Code', related='ai_provider_id.code')
    training_file_id = fields.Char('Training File ID', readonly=True, copy=False)
    fine_tuning_job_id = fields.Char('Fine-Tuning Job ID', readonly=True, copy=False)
    fine_tuned_model = fields.Char('Fine-Tuned Model', readonly=True, copy=False)
    question_answer_domain = fields.Char()
    question_answer_tag_ids = fields.Many2many('ai.question.answer.tag', string='Tags')
    question_answer_ids = fields.Many2many('ai.question.answer', string='Questions - Answers',
                                           compute='_compute_question_answers',
                                           store=False)
    training_question_answer_ids = fields.Many2many('ai.question.answer',
                                                    string='Training Questions - Answers',
                                                    store=True, readonly=True, copy=False)
    system_role_content = fields.Char()
    job_status = fields.Char(readonly=True, copy=False)

    def get_ai_client(self):
        return self.ai_provider_id.get_ai_client()

    def get_fine_tuning_job_client(self):
        client = self.get_ai_client()
        return client.jobs

    @api.onchange('question_answer_tag_ids', 'question_answer_domain')
    def _compute_question_answers(self):
        for rec in self:
            domain = safe_eval(rec.question_answer_domain,
                               SAFE_EVAL_BASE,
                               {'self': rec}) if rec.question_answer_domain else []
            question_answer_ids = self.env['ai.question.answer'].search(domain)
            question_answer_ids = question_answer_ids.filtered(lambda x: x.tag_ids & rec.question_answer_tag_ids)
            rec.question_answer_ids = question_answer_ids

    def get_training_content(self):
        content = ''
        for question_answer_id in self.question_answer_ids:
            messages = []
            if self.system_role_content:
                messages.append({'role': 'system', 'content': self.system_role_content})

            messages.extend(question_answer_id.get_training_content())

            values = {'messages': messages}
            content += json.dumps(values) + '\n'
        return bytes(content, 'utf-8')

    def create_training_file(self):
        client = self.get_ai_client()
        file = ('training_%s' % self.id, self.get_training_content())
        res = client.files.create(file=file, purpose='fine-tune')
        self.training_file_id = res.id

    def get_create_fine_tuning_job_params(self):
        return {
            'training_file': self.training_file_id,
            'model': self.ai_model_id.name
        }

    def create_fine_tuning(self):
        jobs = self.get_fine_tuning_job_client()
        params = self.get_create_fine_tuning_job_params()
        res = jobs.create(**params)
        self.fine_tuning_job_id = res.id
        _logger.info(res)

    def update_fine_tuned_model(self):
        jobs = self.get_fine_tuning_job_client()
        res = jobs.retrieve(self.fine_tuning_job_id)
        self.fine_tuned_model = res.fine_tuned_model
        if res.status == 'SUCCESS' and res.status != self.job_status:
            self.job_status = res.status
            self.env['ai.model'].create({'name': self.fine_tuned_model,
                                         'display_name': 'Fine-Tuned - %s' % self.name,
                                         'ai_provider_id': self.ai_provider_id.id})
        _logger.info(res)

    def action_create_training_file(self):
        for rec in self:
            rec.create_training_file()
            rec.training_question_answer_ids = rec.question_answer_ids

    def action_create_fine_tuning(self):
        for rec in self:
            rec.create_fine_tuning()

    def action_update_fine_tuned_model(self):
        for rec in self:
            rec.update_fine_tuned_model()
