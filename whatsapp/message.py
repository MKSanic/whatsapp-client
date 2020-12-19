"""This module is used to contain info about a Whatsapp message.
"""

import selenium.common.exceptions
import selenium.webdriver.common.action_chains
import PIL
import whatsapp.exceptions
import whatsapp.person
import time


class Message:
    """Contains info about a message.

    This class contains info about a message, such as:
        - the sender of the message
        - the contents of the message

    Attributes:
        sender (whatsapp.person.PersonDict): the sender of the message
        contents (str): the contents of the message
        chat_name (str): the name of the chat. None when it couldn't be found.

    Methods:
        get_image: downloads the image attached to the message.
        set_reply: sets the reply for the next message to this message.
        remove: removes the message.
    """

    def __init__(self, sender: whatsapp.person.PersonDict, contents: str, selenium_object,
                 browser, chat_name: str) -> None:
        self.sender = sender
        self.contents = contents
        self.chat_name = chat_name
        self.__selenium_object = selenium_object
        self.__browser = browser

    def get_image(self) -> str:
        """Downloads the image attached to a message and returns the image path in a string.

        Returns:
            str: the path of the image that has been downloaded.

        Raises:
            whatsapp.exceptions.NotAPictureMessageError: the message is not an image.
        """
        # Try to download the image. If the image can"t be find, return an error.
        try:
            # Retrieve the image element from the message and get the image source.
            img_element = self.__selenium_object.find_element_by_xpath("./div/div[1]/div/div/div[1]/div/div[2]/img")
            img_link = img_element.get_attribute("src")
            # Open the image in a new tabblad and switch to it.
            self.__browser.execute_script("window.open(arguments[0], '_blank');", img_link)
            self.__browser.switch_to.window(self.__browser.window_handles[1])
            # Make a screenshot of the image, crop it and save it.
            img_element_screenshot = self.__browser.find_element_by_tag_name("img")
            img_location = img_element_screenshot.location
            img_size = img_element_screenshot.size
            self.__browser.save_screenshot("./picture.png")

            img_x = img_location["x"]
            img_y = img_location["y"]
            width = img_location["x"] + img_size["width"]
            height = img_location["y"] + img_size["height"]

            img = PIL.Image.open("./picture.png")
            img = img.crop((int(img_x), int(img_y), int(width), int(height)))
            img.save("./picture.png")

            self.__browser.close()
            self.__browser.switch_to.window(self.__browser.window_handles[0])
            return "./picture.png"
        except selenium.common.exceptions.NoSuchElementException as picture_not_found_error:
            raise whatsapp.exceptions.NotAPictureMessageError() from picture_not_found_error

    def set_reply(self):
        # The sleeps are to prevent bugs.
        """Sets the reply for the next message to this message.

        Raises:
            whatsapp.exceptions.CantSetReplyError: when an error in Selenium occurs.
        """
        # Hover over the message to show the arrow button for the message menu.
        hover = selenium.webdriver.common.action_chains.ActionChains(
            self.__browser).move_to_element(self.__selenium_object.find_element_by_css_selector(".copyable-text"))
        hover.perform()
        time.sleep(1)
        # Click the arrow button. It can have multiple paths, so try them both.
        try:
            self.__selenium_object.find_element_by_xpath("./div/div/span[2]/div/div").click()
        except selenium.common.exceptions.NoSuchElementException:
            try:
                self.__selenium_object.find_element_by_xpath("./div/div/span/div/div").click()
            except selenium.common.exceptions.NoSuchElementException:
                raise whatsapp.exceptions.CantSetReplyError()
        time.sleep(1)
        # Click the reply button.
        reply = self.__browser.find_element_by_xpath("/html/body/div[1]/div/span[4]/div/ul/li[2]")
        reply.click()

    def remove(self):
        """Removes the message.

        Raises:
            whatsapp.exceptions.CantRemoveMessageError: when the message can't be removed.
        """
        if not self.sender["this_person"]:
            raise whatsapp.exceptions.CantRemoveMessageError()
        # The sleeps are to prevent bugs.
        # Hover over the message to show the arrow button for the message menu.
        hover = selenium.webdriver.common.action_chains.ActionChains(
            self.__browser).move_to_element(self.__selenium_object.find_element_by_css_selector(".copyable-text"))
        hover.perform()
        time.sleep(0.5)
        # Click the arrow button. It can have multiple paths, so try them both.
        try:
            self.__selenium_object.find_element_by_xpath("./div/div/span[2]/div/div").click()
        except selenium.common.exceptions.NoSuchElementException:
            try:
                self.__selenium_object.find_element_by_xpath("./div/div/span/div/div").click()
            except selenium.common.exceptions.NoSuchElementException:
                raise whatsapp.exceptions.CantRemoveMessageError()

        time.sleep(0.5)
        # Click the remove button and then click remove for everyone.
        try:
            remove_button = self.__browser.find_element_by_xpath("/html/body/div[1]/div/span[4]/div/ul/li[5]")
            remove_button.click()
            remove_for_everyone_btn = self.__browser.find_element_by_xpath("/html/body/div[1]/div/span["
                                                                           "2]/div/span/div/div/div/div/div/div["
                                                                           "3]/div/div[3]")
            remove_for_everyone_btn.click()
        except selenium.common.exceptions.NoSuchElementException:
            raise whatsapp.exceptions.CantRemoveMessageError()

        time.sleep(0.5)
        # If a pop-up comes up, ignore it.
        try:
            self.__browser.find_element_by_xpath("/html/body/div[1]/div/span[2]/div/span/div/div/div/div/div/div["
                                                 "2]/div[2]").click()
        except selenium.common.exceptions.NoSuchElementException:
            pass
        time.sleep(1)
