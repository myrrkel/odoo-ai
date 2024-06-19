# Copyright (C) 2024 - Michel Perrocheau (https://github.com/myrrkel).
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
{
    'name': 'AI Connector',
    'version': '16.0.0.0',
    'author': 'Michel Perrocheau',
    'website': 'https://github.com/myrrkel',
    'summary': "Connector for AI platforms",
    'sequence': 0,
    'certificate': '',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'mail',
    ],
    'category': 'AI',
    'complexity': 'easy',
    'qweb': [
    ],
    'demo': [
    ],
    'images': [
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/ai_tool_data.xml',
        'views/ai_provider_views.xml',
        'views/ai_model_views.xml',
        'views/ai_completion_views.xml',
        'views/ai_completion_result_views.xml',
        'views/ai_question_answer_views.xml',
        'views/ai_tool_views.xml',
        'views/ai_fine_tuning_views.xml',
        'wizards/create_question_answer_wizard.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'ai_connector/static/src/scss/style.scss',
        ],
    },

    'auto_install': False,
    'installable': True,
    'application': False,
}
