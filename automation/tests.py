from django.test import LiveServerTestCase
from selenium import webdriver


class HostTest(LiveServerTestCase):

    def testhomepage(self):
        driver = webdriver.Chrome()
        driver.get('http://127.0.0.1:8000/')
        assert "Hello Word" in driver.title
