# Copyright (C) 2024 - Michel Perrocheau (https://github.com/myrrkel).
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import models, fields, api, _
from odoo.tools import html2plaintext

import logging

_logger = logging.getLogger(__name__)


class AICompletion(models.Model):
    _name = 'ai.completion'
    _description = 'AI Completion'
    _inherit = ['ai.mixin']

    def _get_post_process_list(self):
        return [('list_to_many2many', _('List to Many2many')),
                ('json_to_questions', _('JSON to questions'))]

    def _get_response_format_list(self):
        return [('text', _('Text')),
                ('json_object', _('JSON Object')),
                ]

    system_template = fields.Text()
    system_template_id = fields.Many2one('ir.ui.view', string='System Template View')
    temperature = fields.Float(default=1)
    max_tokens = fields.Integer(default=10000)
    top_p = fields.Float(default=1)
    test_answer = fields.Text(readonly=True)
    post_process = fields.Selection(selection='_get_post_process_list')
    response_format = fields.Selection(selection='_get_response_format_list', default='text')

    def prepare_messages(self, messages):
        return messages

    def create_completion(self, rec_id=0, messages=None, prompt='', **kwargs):
        response_format = kwargs.get('response_format', self.response_format) or 'text'
        if not messages:
            messages = []
            system_prompt = self.get_system_prompt(rec_id)
            if system_prompt:
                messages.append({'role': 'system', 'content': system_prompt})

            if not prompt:
                prompt = self.get_prompt(rec_id)
            messages.append({'role': 'user', 'content': prompt})
        messages = self.prepare_messages(messages)

        choices, prompt_tokens, completion_tokens, total_tokens = self.get_completion_results(messages, **kwargs)
        result_ids = []
        for choice in choices:
            _logger.info(f'Completion result: {choice.message.content}')
            if rec_id:
                answer = choice.message.content
                if self.save_answer:
                    result_id = self.create_result(rec_id, prompt, answer, prompt_tokens, completion_tokens, total_tokens)
                    result_ids.append(result_id)
                if self.post_process and not self.target_field_id:
                    self.exec_post_process(answer)
                if not self.save_answer:
                    return answer
            else:
                try:
                    return self.get_result_content(response_format, choices)
                except Exception as err:
                    _logger.error(err, exc_info=True)
        return result_ids

    def get_completion_results(self, messages, **kwargs):
        ai_client = self.get_ai_client()
        model = self.ai_model_id.name or kwargs.get('model', '')
        temperature = self.temperature or kwargs.get('temperature', 0)
        top_p = self.top_p or kwargs.get('top_p', 0)
        max_tokens = kwargs.get('max_tokens', self.max_tokens or 10000)
        _logger.info(f'Create completion: {messages}')
        res = ai_client.chat(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
        )
        return res.choices, res.usage.prompt_tokens, res.usage.completion_tokens, res.usage.total_tokens

    def get_result_content(self, response_format, choices):
        def _extract_json(content):
            start_pos = content.find('{')
            end_post = content.rfind('}') + 1
            return content[start_pos:end_post]

        if self.response_format == 'json_object' or response_format == 'json_object':
            return [_extract_json(choice.message.content) for choice in choices]
        return [choice.message.content for choice in choices]

    def ai_create(self, rec_id, method=False):
        return self.create_completion(rec_id)

    def create_result(self, rec_id, prompt, answer, prompt_tokens, completion_tokens, total_tokens):
        values = {'completion_id': self.id,
                  'ai_provider_id': self.ai_provider_id.id,
                  'ai_model_id': self.ai_model_id.id,
                  'model_id': self.model_id.id,
                  'target_field_id': self.target_field_id.id,
                  'res_id': rec_id,
                  'prompt': prompt,
                  'answer': answer,
                  'prompt_tokens': prompt_tokens,
                  'completion_tokens': completion_tokens,
                  'total_tokens': total_tokens,
                  }
        result_id = self.env['ai.completion.result'].create(values)
        return result_id

    def exec_post_process(self, value):
        if not self.post_process:
            return value
        post_process_function = getattr(self, self.post_process)
        return post_process_function(value)

    def get_system_prompt(self, rec_id):
        context = {'html2plaintext': html2plaintext}
        return self._get_prompt(rec_id, self.system_template_id, self.system_template, context)

    def run_test_completion(self):
        rec_id = self.get_records(limit=1).id
        if not rec_id:
            return
        self.test_prompt = self.get_prompt(rec_id)
        res = self.create_completion(rec_id)
        if res and isinstance(res, list):
            self.test_answer = res[0].answer
        else:
            self.test_answer = res
