# Copyright (C) 2025 - Michel Perrocheau (https://github.com/myrrkel).
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
{
    'name': 'Anthropic AI Connector',
    'version': '18.0.0.0.1',
    'author': 'Michel Perrocheau',
    'website': 'https://github.com/myrrkel',
    'summary': "Connector for Anthropic API",
    'sequence': 0,
    'certificate': '',
    'license': 'LGPL-3',
    'depends': [
        'ai_connector',
    ],
    'external_dependencies': {
        'python': ['anthropic'],
    },
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
        'data/ai_provider_data.xml',
    ],
    'assets': {
    },

    'auto_install': False,
    'installable': True,
    'application': False,
}
