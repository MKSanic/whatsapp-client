"""Used to control groups.
"""
import time
import selenium.webdriver
import selenium.common
import whatsapp.exceptions


class Group:
    """Used to control groups.

    This is going to be extended more later.

    Attributes:
        group_name (str): the name of the group.

    Methods:
        set_name: sets the name of the group.
    """

    def __init__(self, group_name: str, browser: selenium.webdriver.Chrome) -> None:
        self.group_name = group_name
        self.__browser = browser

    def set_name(self, group_name: str) -> None:
        """Sets the group name.

        Args:
            group_name (str): the name of the group.

        Raises:
            whatsapp.exceptions.UnableToSetGroupNameError: when the group name can't be set.
        """
        # The sleeps are to prevent bugs.
        # Change the group_name attribute.
        self.group_name = group_name
        # Click the group bar at the top.
        self.__browser.find_element_by_xpath("/html/body/div[1]/div/div/div[4]/div/header").click()
        time.sleep(0.5)
        # Click the edit button.
        try:
            self.__browser.find_element_by_xpath("/html/body/div[1]/div/div/div[2]/div[3]/span/div/span/div/div/div["
                                                 "1]/div[1]/div[2]/div[1]/span[2]/div").click()
        except selenium.common.exceptions.NoSuchElementException as unable_to_set_group:
            raise whatsapp.exceptions.UnableToSetGroupNameError() from unable_to_set_group
        time.sleep(0.5)
        # Get the group name input.
        group_name_input = self.__browser.find_element_by_xpath("/html/body/div[1]/div/div/div[2]/div["
                                                                "3]/span/div/span/div/div/div[1]/div[1]/div[2]/div["
                                                                "1]/div/div[2]")
        group_name_input.clear()
        group_name_input.send_keys(group_name.splitlines()[0])
        time.sleep(0.5)
        # Click the confirm button.
        self.__browser.find_element_by_xpath("/html/body/div[1]/div/div/div[2]/div[3]/span/div/span/div/div/div["
                                             "1]/div[1]/div[2]/div[1]/span[2]/div").click()
        time.sleep(0.5)
        # Click the close button.
        self.__browser.find_element_by_xpath("/html/body/div[1]/div/div/div[2]/div["
                                             "3]/span/div/span/div/header/div/div[1]/button").click()
