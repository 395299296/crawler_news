from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from pyvirtualdisplay import Display
from collections import OrderedDict
from common import config
from common import data
import os, time, json
import codecs, logging
import platform
import traceback

class Browser(object):
    """Browser Core"""
    def __init__(self, name=None, home_page=None):
        super(Browser, self).__init__()
        self.name = name
        self.home_page = home_page
        self.item = data.news_item
        self.init_logger()

    def init(self):
        """initialize"""
        self.init_db()
        self.init_play()
        self.init_profile()
        self.init_driver()

    def init_logger(self):
        """init logger"""
        self.logger = logging.getLogger(self.name)
        logging.basicConfig(level=logging.INFO, format='[%(asctime)s]%(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    def init_db(self):
        """init db"""
        self.db = data.MongoPipeline(config.mongo_uri, config.mongo_database, config.mongo_user, config.mongo_pass)

    def init_play(self):
        """init virtual display"""
        self.display = None

    def init_profile(self):
        """init the profile"""
        self.profile = None

    def init_driver(self):
        """init web driver"""
        self.driver = None

    def clone(self, that):
        """clone browser member"""
        self.db = that.db
        self.display = that.display
        self.profile = that.profile
        self.driver = that.driver
        self.items_dict = that.items_dict

    def get_page(self, page):
        """browse target page"""
        self.logger.info("start get page:%s", page)
        self.page = page
        try:
            self.driver.get(page)
        except Exception as e:
            pass
        try:
            self.driver.execute_script("var q=document.body.scrollTop=100000")
            self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        except Exception as e:
            pass
        time.sleep(1)
        self.logger.info("end get page:%s", page)

    def parse_page(self):
        """parse current page source"""
        pass

    def browse_page(self):
        """browse home page"""
        self.driver.start_client()
        try:
            self.get_page(self.home_page)
            self.parse_page()
        except Exception as e:
            self.logger.info(e)
            traceback.print_exc()
        self.driver.stop_client()

    def find_info(self, days=3):
        """find history data in db"""
        self.items_dict = {}
        startdate = int(time.time()) - 3600 * 24 * days
        items = self.db.find_by_date(startdate)
        for x in items:
            self.items_dict[x['title']] = x

    def save_item(self, item):
        """save item data"""
        item['eventtime'] = int(time.time())
        self.db.save_item(item)
        self.items_dict[item['title']] = item

    def read_info(self, filename):
        """read history data from local file"""
        self.items_dict = {}
        input_file = os.path.join(config.output_path, filename)
        if not os.path.exists(input_file):
            return None

        with codecs.open(input_file, 'r', encoding='utf-8') as f:
            txt = f.read()
            if not txt:
                return None
            lines = txt.split('\n\n')
            for x in lines:
                if not x: continue
                item_obj = json.loads(x, object_pairs_hook=OrderedDict)
                self.items_dict[item_obj['title']] = item_obj

    def write_item(self, items_json, filename):
        """write data to local file"""
        if not os.path.exists(config.output_path):
            os.makedirs(config.output_path)
        txt = json.dumps(items_json, ensure_ascii=False, indent=2)
        with codecs.open(os.path.join(config.output_path, filename), 'a', encoding='utf-8') as f:
            f.write(txt)
            f.write('\n\n')

    def clear_up(self):
        try:
            self.db.close()
        except Exception as e:
            pass
        try:
            self.driver.close()
        except Exception as e:
            pass
        try:
            self.driver.quit()
        except Exception as e:
            pass
        try:
            self.display.quit()
        except Exception as e:
            pass

    def start(self):
        """start run"""
        self.init()
        self.find_info()
        self.browse_page()
        self.clear_up()


class PhantomJS(Browser):
    """PhantomJS Browser"""
    def __init__(self, name=None, home_page=None):
        super(PhantomJS, self).__init__(name, home_page)

    def init_driver(self):
        """init web driver"""
        super(PhantomJS, self).init_driver()
        dcap = dict(DesiredCapabilities.PHANTOMJS)
        dcap["phantomjs.page.settings.userAgent"] = (
            "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
        )
        self.driver = webdriver.PhantomJS(executable_path=config.browser_path, desired_capabilities=dcap)


class Firefox(Browser):
    """Firefox Browser"""
    def __init__(self, name=None, home_page=None):
        super(Firefox, self).__init__(name, home_page)

    def init_play(self):
        """init virtual display"""
        super(Firefox, self).init_play()
        if 'Linux' in platform.system():
            self.display = Display(backend="xvfb", size=(1280, 800))
            self.display.start()

    def init_profile(self):
        """init the Firefox profile object"""
        super(Firefox, self).init_profile()
        self.profile = FirefoxProfile()
        ## Disable CSS
        self.profile.set_preference('permissions.default.stylesheet', 2)
        ## Disable images
        self.profile.set_preference('permissions.default.image', 2)
        ## Disable Flash
        self.profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')
        ## 
        self.profile.set_preference('browser.link.open_newwindow.restriction', 1)
        
    def init_driver(self):
        """init web driver"""
        super(Firefox, self).init_driver()
        ## Set the modified profile while creating the browser object
        self.driver = webdriver.Firefox(self.profile)
        ## self.driver.maximize_window()
        ## self.driver.set_window_position(-2000, 0)
        self.driver.set_page_load_timeout(180)
        self.driver.set_script_timeout(60)