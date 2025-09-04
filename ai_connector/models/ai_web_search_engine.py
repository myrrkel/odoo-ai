# Copyright (C) 2025 - Michel Perrocheau (https://github.com/myrrkel).
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields, api, _
from odoo.tools import html2plaintext
from googleapiclient.discovery import build
from base64 import b64encode
from bs4 import BeautifulSoup # pylint: disable=missing-manifest-dependency
import requests
import logging

_logger = logging.getLogger(__name__)

def url_to_base64(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    return b64encode(requests.get(url, headers=headers, timeout=120).content).decode("utf-8")


def get_page_text(url):
    request = requests.get(url)
    soup = BeautifulSoup(request.content, "html.parser")
    blocklist = ['style', 'script', 'a', 'meta', 'comment', 'html', '[document]', 'head']
    page_text = ''
    for el in soup.find_all(string=True):
        if el.parent.name in blocklist:
            continue
        _logger.info('%s : %s' % (el.parent.name, el))
        try:
            el_text = html2plaintext(el).strip()
        except Exception as e:
            el_text = ''
        if el_text and el_text not in page_text:
            page_text += el_text + '\n'
    return page_text


class AiWebSearchEngine(models.Model):
    _name = "ai.web.search.engine"
    _description = "AI Web Search Engine"
    _rec_name = "name"

    name = fields.Char(required=True)
    api_key = fields.Char()
    programmable_search_engine_id = fields.Char()

    @api.model
    def web_search(self, query, limit=10):
        api_key = self.api_key or self.env['ir.config_parameter'].sudo().get_param('ai_connector.google_search_api')
        service = build('customsearch', 'v1', developerKey=api_key)
        cx = self.programmable_search_engine_id or self.env['ir.config_parameter'].sudo().get_param('ai_connector.programmable_search_engine_id')
        res = service.cse().list(q=query, cx=cx).execute()
        web_search_result = ''
        items = res['items'][:limit]
        for i, item in enumerate(items):
            text = get_page_text(item['link'])
            item_text = f"\n\n## Result {i + 1}\n\nurl: {item['link']}\ntitle: {item['title']}\nhtmlTitle: {item['htmlTitle']}"
            item_text += f"\ncontent: {item['htmlSnippet']}\n{text}"
            web_search_result += item_text[:3000]
            if len(web_search_result) > 10000:
                return web_search_result[:10000]
        return web_search_result
