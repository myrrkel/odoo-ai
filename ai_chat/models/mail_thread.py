# Copyright (C) 2024 - Michel Perrocheau (https://github.com/myrrkel).
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    def _message_post_after_hook(self, message, msg_vals):
        res = super(MailThread, self)._message_post_after_hook(message, msg_vals)
        self.env['mail.ai.bot']._answer_to_message(self, msg_vals)
        return res
