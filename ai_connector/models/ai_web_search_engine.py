# Copyright (C) 2025 - Michel Perrocheau (https://github.com/myrrkel).
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from __future__ import annotations
from odoo import models, fields, api, _
from odoo.tools import html2plaintext
from googleapiclient.discovery import build
from base64 import b64encode
from bs4 import BeautifulSoup # pylint: disable=missing-manifest-dependency
import requests
import logging

from os import environ
from resource import RLIM_INFINITY, RLIMIT_AS, setrlimit
from odoo.service.server import set_limit_memory_hard
try:
    from selenium.webdriver.common.by import By
    from selenium.webdriver import Chrome, ChromeOptions, Remote
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.remote.webdriver import WebDriver
    from selenium.webdriver.support.wait import WebDriverWait
    SELENIUM_INSTALLED = True
except ImportError:
    SELENIUM_INSTALLED = False
    pass

_logger = logging.getLogger(__name__)


class Selenium:
    """Initialize Selenium."""
    _default_chrome_flags = {
        "--headless": "",
        "--no-default-browser-check": "",
        "--no-first-run": "",
        "--disable-extensions": "",
        "--disable-background-networking": "",
        "--disable-background-timer-throttling": "",
        "--disable-backgrounding-occluded-windows": "",
        "--disable-renderer-backgrounding": "",
        "--disable-breakpad": "",
        "--disable-client-side-phishing-detection": "",
        "--disable-crash-reporter": "",
        "--disable-default-apps": "",
        "--disable-dev-shm-usage": "",
        "--disable-device-discovery-notifications": "",
        "--disable-namespace-sandbox": "",
        "--disable-translate": "",
        "--autoplay-policy": "no-user-gesture-required",
        "--window-size": "1376,768",
        "--no-sandbox": "",
        "--disable-gpu": "",
    }

    def __init__(self, *args, **kwargs):
        self.driver: WebDriver | None = None
        self.wait: WebDriverWait | None = None
        self.selenium_timeout: float = environ.get("SELENIUM_TIMEOUT", 10.0)
        self.chrome_flags: dict[str, str] = self._default_chrome_flags.copy()

    def start_selenium(self):
        """Start Selenium"""
        grid_url = environ.get("SELENIUM_GRID_URL", False)
        if grid_url:
            self.driver = Remote(command_executor=grid_url, options=ChromeOptions())
        else:
            setrlimit(RLIMIT_AS, (RLIM_INFINITY, RLIM_INFINITY))

            options = Options()
            for key, value in self.chrome_flags.items():
                options.add_argument(f"{key}={value}" if value else key)

            self.driver = Chrome(service=Service(),options=options)

        self.wait = WebDriverWait(self.driver, timeout=self.selenium_timeout, poll_frequency=1)
        self.driver.implicitly_wait(self.selenium_timeout)

    def stop_selenium(self):
        """Stop Selenium"""
        self.driver.quit()
        set_limit_memory_hard()

    def navigate(self, url: str):
        self.driver.get(url)

    def get_page_text(self, url: str):
        self.navigate(url)
        return self.driver.find_element(By.XPATH, "/html/body").text


def url_to_base64(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    return b64encode(requests.get(url, headers=headers, timeout=10).content).decode("utf-8")


def get_page_text(url):
    try:
        request = requests.get(url, timeout=3)
        soup = BeautifulSoup(request.content, "html.parser")
        blocklist = ['style', 'script', 'a', 'meta', 'comment', 'html', '[document]', 'head']
        page_text = ''
        for el in soup.find_all(string=True):
            if el.parent.name in blocklist:
                continue
            el_text = html2plaintext(el).strip()
            if el_text and el_text not in page_text:
                page_text += el_text + '\n'
        return page_text
    except Exception as err:
        _logger.error(err)
        return ''


class AiWebSearchEngine(models.Model):
    _name = "ai.web.search.engine"
    _description = "AI Web Search Engine"
    _rec_name = "name"

    name = fields.Char(required=True)
    api_key = fields.Char()
    programmable_search_engine_id = fields.Char()
    use_selenium = fields.Boolean()

    @api.model
    def web_search(self, query, limit=10):
        excluded_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt']
        selenium = None
        api_key = self.api_key or self.env['ir.config_parameter'].sudo().get_param('ai_connector.google_search_api')
        service = build('customsearch', 'v1', developerKey=api_key)
        cx = self.programmable_search_engine_id or self.env['ir.config_parameter'].sudo().get_param('ai_connector.programmable_search_engine_id')
        try:
            res = service.cse().list(q=query, cx=cx).execute()
        except Exception as err:
            _logger.error(err)
            return ''
        web_search_result = ''
        items = res['items'][:limit]
        if items and SELENIUM_INSTALLED and self.use_selenium:
            selenium = Selenium()
            selenium.start_selenium()
        for i, item in enumerate(items):
            url = item['link']
            if any(url.endswith(ext) for ext in excluded_extensions):
                continue
            if selenium:
                text = selenium.get_page_text(url)
            else:
                text = get_page_text(url)
            item_text = f"\n\n## Result {i + 1}\n\nurl: {url}\ntitle: {item['title']}\nhtmlTitle: {item['htmlTitle']}"
            _logger.info(item_text)
            item_text += f"\ncontent: {item['htmlSnippet']}\n{text}"
            web_search_result += item_text[:3000]
            if len(web_search_result) > 10000:
                return web_search_result[:10000]

        if selenium:
            selenium.stop_selenium()
        return web_search_result
