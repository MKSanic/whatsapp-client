from .exceptions import NotAPictureMessage
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
import time
from PIL import Image

class Message(object):
    """
    A Message object.\n
    This object has 2 variables: sender and contents\n
    sender will return a person object
    contents will return the message text
    """
    def __init__(self, sender, contents, selenium_object):
        self.sender = sender
        self.contents = contents
        self.__selenium_object = selenium_object
    
    def get_image(self, browser):
        try:
            img_element = self.__selenium_object.find_element_by_xpath("./div/div[1]/div/div/div[1]/div/div[2]/img")
            img_link = img_element.get_attribute("src")
            browser.execute_script("window.open(arguments[0], '_blank');", img_link)
            browser.switch_to.window(browser.window_handles[1])
            img_element_screenshot = browser.find_element_by_tag_name("img")
            img_location = img_element_screenshot.location
            img_size = img_element_screenshot.size
            browser.save_screenshot("./picture.png")

            x = img_location['x']
            y = img_location['y']
            width = img_location['x'] + img_size['width']
            height = img_location['y'] + img_size['height']

            img = Image.open("./picture.png")
            img = img.crop((int(x), int(y), int(width), int(height)))
            img.save('./picture.png')

            browser.close()
            browser.switch_to.window(browser.window_handles[0])
            return "./picture.png"
        except NoSuchElementException:
            raise NotAPictureMessage()