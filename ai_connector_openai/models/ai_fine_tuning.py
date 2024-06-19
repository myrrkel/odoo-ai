# Copyright (C) 2024 - Michel Perrocheau (https://github.com/myrrkel).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _

import logging

_logger = logging.getLogger(__name__)


class AIFineTuning(models.Model):
    _inherit = 'ai.fine.tuning'

    def get_fine_tuning_job_client(self):
        if self.ai_provider == 'openai':
            client = self.get_ai_client()
            return client.fine_tuning.jobs
        return super(AIFineTuning, self).get_fine_tuning_job_client()

