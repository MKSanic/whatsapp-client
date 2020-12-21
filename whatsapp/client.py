"""Used to make a connection with Whatsapp.

This module can be used to:
    - set the chat the client sends messages to
    - make commands for the bot to respond to
    - remove commands
    - run functions everytime a new message has been send or received
    - run functions everytime the bot checks for new messages
    - run functions when the bot is ready.
    - send text and files to the Whatsapp chat.
    - send error messages to the Whatsapp chat.
    - get the last message in the Whatsapp chat.
"""
# Please ignore the PyCharm comments.

import time
import os
import functools
import typing
import PIL.Image
import selenium.webdriver
import selenium.webdriver.chrome.options
import selenium.common
import webdriver_manager.chrome
import whatsapp.exceptions
import whatsapp.message
import whatsapp.person
import whatsapp.group
import whatsapp._logger


# noinspection PyArgumentList
class WhatsappClient:
    # noinspection PyUnresolvedReferences
    """This creates a Whatsapp client.

        This class can be used to:
            - set the chat the client sends messages to
            - make commands for the bot to respond to
            - remove commands
            - run functions everytime a new message has been send or received
            - run functions everytime the bot checks for new messages
            - run functions when the bot is ready.
            - send text and files to the Whatsapp chat.
            - send error messages to the Whatsapp chat.
            - get the last message in the Whatsapp chat.
        The client has a build in help command.
        This command can be removed by using the remove_command() method.

        Attributes:
            command_prefix (str): the prefix the user needs to add to the command. Default "!".
            log_level (int): the level of logging:
                             20: the client logs info, warnings and errors.
                             30: the client logs warnings and errors.
                             40: the client logs only errors.
                             Default 40.

        Methods:
            set_chat: set the chat the client is on.
            remove_command: remove a command from the client.
            send_message: send a message to the chat the client is on.
            send_file: send a file to the chat the client is on.
            send_error_message: send an error message to the chat the client is on.
            get_last_message: get the last message from the chat the client is on.
            run: run the client.
        """

    def __init__(self) -> None:
        self.__running = False
        self.__commands = {"help": [self.__help_menu, "Returns help messages"]}
        self.__on_ready = []
        self.__on_messages = []
        self.__on_loops = []
        self.__command_prefix = "!"
        self.__logger = whatsapp._logger.Logger()
        self.__logger.log_level = 40
        self.__browser = None
        self.__send_input = None
        self.__user_data_dir = f"{os.path.dirname(os.path.realpath(__file__))}/whatsapp_data"
        if not os.path.isdir(self.__user_data_dir):
            os.mkdir(self.__user_data_dir)

    def __str__(self) -> str:
        string = "A Whatsapp client. Commands:"
        for cmd in self.__commands:
            string = string + f"{cmd}\n"
        return string

    @property
    def command_prefix(self) -> str:
        """Command prefix property.
        """
        return self.__command_prefix

    @command_prefix.setter
    def command_prefix(self, prefix: str) -> None:
        """Command prefix setter.

        Raises:
            whatsapp.exceptions.InvalidPrefixError: when an invalid prefix has been given.
        """
        if not isinstance(prefix, str):
            raise whatsapp.exceptions.InvalidPrefixError()
        elif len(prefix) != 1:
            raise whatsapp.exceptions.InvalidPrefixError()
        elif not prefix.isascii():
            raise whatsapp.exceptions.InvalidPrefixError()
        else:
            self.__command_prefix = prefix

    @property
    def log_level(self) -> int:
        """Log level property.
        """
        return self.__logger.log_level

    @log_level.setter
    def log_level(self, value: typing.Literal[20, 30, 40]):
        """Log level setter.
        """
        self.__logger.log_level = value

    # noinspection PyMethodParameters
    def __needs_client_running(function: typing.Callable) -> typing.Callable:
        """The function this decorator decorates will raise an error when the client is not running.
        """
        @functools.wraps(function)
        def wrapper(self, *args, **kwargs):
            if self.__running:
                return function(self, *args, **kwargs)
            else:
                raise whatsapp.exceptions.ClientNotStartedError

        return wrapper

    # noinspection PyMethodParameters
    def __error_handler(error_level: typing.Literal[30, 40], executing: str) -> typing.Callable:
        """The function this decorator decorates will automatically handle an exception.

        Args:
            error_level: the error level for the logger when an error occurs.
            executing: what the function is executing.
        """
        if error_level == 30:
            def handler(function: typing.Callable):
                @functools.wraps(function)
                def wrapper(self, *args, **kwargs):
                    try:
                        return function(self, *args, **kwargs)
                    except Exception as error:
                        self.__logger.log_warning(error, executing)
                return wrapper
        else:
            def handler(function: typing.Callable):
                @functools.wraps(function)
                def wrapper(self, *args, **kwargs):
                    try:
                        return function(self, *args, **kwargs)
                    except Exception as error:
                        self.__logger.log_error(error, executing)
                return wrapper
        return handler

    @__needs_client_running
    def set_chat(self, chat_name: typing.Union[str, whatsapp.group.Group, whatsapp.person.PersonDict]) -> None:
        """Sets the chat the bot is on.

        Args:
            chat_name (typing.Union[str, whatsapp.group.Group, whatsapp.person.PersonDict[): the name of the chat.
                                                                                             Can be a string,
                                                                                             a whatsapp.group.Group
                                                                                             object or a
                                                                                             whatsapp.person.PersonDict
                                                                                             dict.

        Raises:
            whatsapp.exceptions.UnknownChatError: raises when the chat is not found.
        """
        if isinstance(chat_name, whatsapp.group.Group):
            chat_name = chat_name.group_name
        elif isinstance(chat_name, whatsapp.person.PersonDict):
            chat_name = chat_name["person"]
        # Retrieve all the chats from the sidebar.
        chats = self.__browser.find_element_by_id("pane-side").find_elements_by_tag_name("span")
        for chat in chats:
            if chat.text == chat_name:
                chat.click()
                time.sleep(5)
                # Reset the __send_input variable to prevent bugs.
                self.__send_input = self.__browser.find_element_by_xpath(
                    "/html/body/div[1]/div/div/div[4]/div/footer/div[1]/div[2]/div/div[2]")
                return
        raise whatsapp.exceptions.UnknownChatError(chat_name)

    def command(self, name: str, help_message=None) -> typing.Callable:
        """This is a decorator for adding commands.

        The function will be run when the client receives a message
        with the command prefix + the command name.
        The function must have the following arguments in the following order:
        - a list. This will be a list of arguments the user gave.
        - a whatsapp.message.Message object. This will contain info about the message.

        Args:
            name (str): the name of the command.
            help_message: the help message of the command. Default None.
        """

        def add_command(command_function: typing.Callable[[list, whatsapp.message.Message], typing.Any]):
            self.__commands[name] = [command_function, help_message]

            return command_function

        return add_command

    def remove_command(self, name: str) -> None:
        """Remove a command from the client.

        Args:
            name (str): the name of the command.

        Raises:
            whatsapp.exceptions.CommandNotFoundError: when the given command can't be found.
        """
        try:
            self.__commands.pop(name)
        except KeyError as command_not_found:
            raise whatsapp.exceptions.CommandNotFoundError() from command_not_found

    def on_message(self, on_message_function: typing.Callable[[whatsapp.message.Message],
                                                              typing.Any]) -> typing.Callable:
        """on_message decorator.

        The function will be run when the client receives a new message.
        The function will receive one argument, a whatsapp.message.Message object
        containing info about the message.
        """
        self.__on_messages.append(on_message_function)

        def run_on_message(msg):
            on_message_function(msg)

        return run_on_message

    def on_ready(self, on_ready_function: typing.Callable[[], typing.Any]) -> typing.Callable:

        """on_ready decorator
        .
        The function will be run when the client is ready.
        """
        self.__on_ready.append(on_ready_function)

        def run_on_ready():
            on_ready_function()

        return run_on_ready

    def on_loop(self, on_loop_function: typing.Callable[[], typing.Any]) -> typing.Callable:
        """on_loop decorator.

        The function will be run when the client checks for new messages.
        """
        self.__on_loops.append(on_loop_function)

        def run_on_message():
            on_loop_function()

        return run_on_message

    @__error_handler(error_level=30, executing="a command")
    @__needs_client_running
    def __process_commands(self, function: typing.Callable, arguments: list,
                           message_object: whatsapp.message.Message, command_name: str) -> None:
        """Processes a command.

        Args:
            function (method): the function to execute.
            arguments (list): the arguments the user gave.
            message_object (whatsapp.message.Message): the message object.
        """
        self.__logger.log_command(command_name, function)
        function(arguments, message_object)

    @__error_handler(error_level=40, executing="message listeners")
    @__needs_client_running
    def __process_message_listeners(self, msg_object: whatsapp.message.Message) -> None:
        """Processes the message listeners.

        Args:
            msg_object (whatsapp.message.Message): the message object.
        """
        on_message_listeners = self.__on_messages
        for listener in on_message_listeners:
            self.__logger.log_msg_listener(listener, msg_object)
            listener(msg_object)

    @__error_handler(error_level=40, executing="loop listeners")
    @__needs_client_running
    def __process_loop_listeners(self) -> None:
        """Processes the loop listeners.
        """
        on_loop_listeners = self.__on_loops
        for listener in on_loop_listeners:
            listener()

    @__error_handler(error_level=40, executing="ready listeners")
    @__needs_client_running
    def __run_ready_functions(self) -> None:
        """Runs the on ready functions."""
        for function in self.__on_ready:
            function()

    @__needs_client_running
    def send_message(self, msg: str) -> None:
        """Sends a message to the chat the client is on.

        Args:
            msg (str): the message to send.
        """
        for to_send in msg.splitlines():
            try:
                self.__send_input.clear()
                self.__send_input.send_keys(to_send + "\n")
            except selenium.common.exceptions.StaleElementReferenceException:
                pass

    def send_error_message(self, exception: Exception, executing: str) -> None:
        """Sends an error message to the chat the client is on.

        Args:
            exception (Exception): the exception that occurred.
            executing (str): what the program was executing.
        """
        self.send_message(f"An error occurred while executing {executing}. Exception: {str(exception)}")

    @__needs_client_running
    def send_file(self, file_path: str, file_type="other") -> None:
        """Sends a file to the chat the client is on.

        Args:
            file_path (str): the path of the file.
            file_type (str): the type of the file. Can be "other" of "img".

        Raises:
            whatsapp.exceptions.FileTooBigError: raises when the given file is over the limit of 64 MB.
            whatsapp.exceptions.UnknownFileTypeError: raises when an unknown file type is given.
        """
        file_size = os.path.getsize(file_path)
        if file_size > 64000000:
            raise whatsapp.exceptions.FileTooBigError(file_size)
        # Retrieve the button to attach files and click it.
        attach_file_button = self.__browser.find_element_by_xpath(
            "/html/body/div[1]/div/div/div[4]/div/footer/div[1]/div[1]/div[2]/div")
        attach_file_button.click()
        if file_type == "other":
            # Retrieve the upload input for the 'other' file button if the given file type is 'other'.
            file_input = self.__browser.find_element_by_xpath("/html/body/div[1]/div/div/div[4]/div/footer/div["
                                                              "1]/div[1]/div[2]/div/span/div/div/ul/li["
                                                              "3]/button/input")
        elif file_type == "img":
            # Retrieve the 'image' file input if the given file type is 'img'.
            file_input = self.__browser.find_element_by_xpath("/html/body/div[1]/div/div/div[4]/div/footer/div["
                                                              "1]/div[1]/div[2]/div/span/div/div/ul/li["
                                                              "1]/button/input")
        else:
            raise whatsapp.exceptions.UnknownFileTypeError()

        # Enter the file path to the retrieved input.
        file_input.send_keys(file_path)
        file_is_sended = False
        time.sleep(0.5)

        # Wait for the send button to appear and click the send button.
        while file_is_sended is False:
            try:
                send_button = self.__browser.find_element_by_xpath(
                    "/html/body/div[1]/div/div/div[2]/div[2]/span/div/span/div/div/div[2]/span/div")
                send_button.click()
                file_is_sended = True
            except selenium.common.exceptions.NoSuchElementException:
                time.sleep(0.5)
                continue

    @__needs_client_running
    def get_last_message(self) -> whatsapp.message.Message:
        """Gets the last message.

        Returns:
            a whatsapp.message.Message object.

        Raises:
            whatsapp.exceptions.CannotFindMessageError: raises when the client can't find any message.
        """
        # Retrieve all the messages.
        messages = self.__browser.find_elements_by_class_name(
            "focusable-list-item")

        # Check for the chat name. If it couldn't be found, chat name = None
        try:
            chat_element = self.__browser.find_element_by_xpath(
                "/html/body/div[1]/div/div/div[4]/div/header/div[2]/div["
                "1]/div/span")
            chat_name = chat_element.text
        except selenium.common.exceptions.NoSuchElementException:
            chat_name = None
        # Check if the chat is a group. If a Selenium error occurs, user = None.
        try:
            chat_img = self.__browser.find_element_by_xpath("/html/body/div[1]/div/div/div[4]/div/header/div["
                                                            "1]/div/div/span")
            if chat_img.get_attribute("data-icon") == "default-user":
                user = True
            else:
                user = False
        except selenium.common.exceptions.NoSuchElementException:
            user = None
        # Select the newest message.
        try:
            new_message = messages[-1]
        except IndexError as message_not_found:
            raise whatsapp.exceptions.CantFindMessageError() from message_not_found
        try:
            # Retrieve the text in the message.
            new_message_text_element = new_message.find_element_by_css_selector(
                ".selectable-text")
            # This is done with JS to get the emoticons from the message too.
            new_message_text = self.__browser.execute_script("""
                                        var new_message = arguments[0];
                                        var text = new_message.firstChild;
                                        var child = text.firstChild;
                                        var ret = "";
                                        while(child) {
                                        if (child.nodeType === Node.TEXT_NODE){
                                            ret += child.textContent;
                                        }
                                        else if(child.tagName.toLowerCase() === "img"){
                                            ret += child.alt;
                                        }
                                        child = child.nextSibling;
                                        }
                                        return ret;
                                    """, new_message_text_element)
        except selenium.common.exceptions.NoSuchElementException:
            try:
                # The message could possibly be an image. If so, retrieve the image and set the message text to "".
                new_message.find_element_by_xpath("./div/div[1]/div/div/div[1]/div/div[2]/img")
                new_message_text = ""
            except (selenium.common.exceptions.NoSuchElementException,
                    selenium.common.exceptions.StaleElementReferenceException):
                try:
                    # Sometimes the image is on a different xpath
                    new_message.find_element_by_xpath("./div/div[1]/div/div/div[2]/div[1]/div[4]/img")
                    new_message_text = ""
                except (selenium.common.exceptions.NoSuchElementException,
                        selenium.common.exceptions.StaleElementReferenceException) as msg_not_found:
                    raise whatsapp.exceptions.CantFindMessageError() from msg_not_found

        except selenium.common.exceptions.StaleElementReferenceException as msg_not_found:
            raise whatsapp.exceptions.CantFindMessageError() from msg_not_found

        group = None
        if user:
            if "message-out" in new_message.get_attribute("class"):
                sender: whatsapp.person.PersonDict = {
                    "this_person": True,
                    "person": None
                }
            else:
                sender: whatsapp.person.PersonDict = {
                    "this_person": False,
                    "person": chat_name
                }
        else:
            sender: whatsapp.person.PersonDict = {
                "this_person": False
            }
            if "message-out" not in new_message.get_attribute("class"):
                try:
                    person_element = new_message.find_element_by_xpath("./div/div/div/div[1]/span")
                    person = person_element.text
                except selenium.common.exceptions.NoSuchElementException:
                    person = None
            else:
                sender["this_person"] = True
                person = None
            sender["person"] = person
            group = whatsapp.group.Group(chat_name, self.__browser)

        return whatsapp.message.Message(sender, new_message_text, new_message, self.__browser, group)

    # noinspection PyUnusedLocal
    @__needs_client_running
    def __help_menu(self, arguments: list, message_obj: whatsapp.message.Message) -> None:
        if len(arguments) == 0:
            answer = "List of commands:\n"
            for command in self.__commands:
                answer = answer + f"{command.replace(self.command_prefix, '')}, "

            self.send_message(answer)
            return
        else:
            for command in self.__commands:
                if arguments[0] == command.replace(self.command_prefix, ""):
                    answer = self.__commands[command][1]
                    self.send_message(answer)
                    return

        self.send_message("Command not found!")

    def run(self, headless: bool = False) -> None:
        """Starts the client.

        Args: headless (bool): if True, the program will show the QR-code in a picture viewer.
                               This doesn't start Chrome in headless mode yet because of bugs.

        Raises:
            whatsapp.exceptions.InvalidPrefixError: when an invalid prefix has been set.
        """

        self.__running = True

        self.__logger.log(20, "Starting client.")

        options = selenium.webdriver.chrome.options.Options()
        options.add_argument(f"user-data-dir={self.__user_data_dir}")

        self.__browser = selenium.webdriver.Chrome(webdriver_manager.chrome.ChromeDriverManager(log_level=50).install(),
                                                   chrome_options=options)

        self.__browser.get("https://web.whatsapp.com/")

        # Find the QR-code element if the headless argument is True. If Whatsapp is already logged in,
        # skip this process.
        if headless:
            qr_code_found = False
            qr_code_element = None
            while True:
                try:
                    self.__browser.find_element_by_id("pane-side").find_elements_by_tag_name("span")
                    break
                except selenium.common.exceptions.NoSuchElementException:
                    try:
                        qr_code_element = self.__browser.find_element_by_xpath(
                            "/html/body/div[1]/div/div/div[2]/div[1]/div/div["
                            "2]/div/canvas")
                        qr_code_found = True
                        break
                    except selenium.common.exceptions.NoSuchElementException:
                        time.sleep(1)
                        continue
            if qr_code_found:
                qr_code_size = qr_code_element.size
                qr_code_loc = qr_code_element.location
                self.__browser.save_screenshot("qr.png")
                pos_x = qr_code_loc["x"]
                pos_y = qr_code_loc["y"]
                width = pos_x + qr_code_size["width"]
                height = pos_y + qr_code_size["height"]
                img = PIL.Image.open("qr.png")
                img = img.crop((int(pos_x), int(pos_y), int(width), int(height)))
                img.save("qr.png")
                img.show()
                while True:
                    try:
                        self.__browser.find_element_by_xpath("/html/body/div[1]/div/div/div[2]/div[1]/div/div["
                                                             "2]/div/canvas")
                    except selenium.common.exceptions.NoSuchElementException:
                        img.close()
                        break

        last_message = ""

        # Wait for Whatsapp to become ready to use.
        while True:
            try:
                self.__browser.find_element_by_id("pane-side").find_elements_by_tag_name("span")
                break
            except selenium.common.exceptions.NoSuchElementException:
                time.sleep(1)
                continue

        self.__run_ready_functions()

        while self.__running:

            # Reset the __send_input variable to prevent bugs.
            try:
                self.__send_input = self.__browser.find_element_by_xpath(
                    "/html/body/div[1]/div/div/div[4]/div/footer/div[1]/div[2]/div/div[2]")
            except selenium.common.exceptions.NoSuchElementException:
                time.sleep(5)
                continue

            self.__process_loop_listeners()

            try:
                new_message_object = self.get_last_message()
            except whatsapp.exceptions.CantFindMessageError:
                continue

            if new_message_object is None:
                time.sleep(0.5)
                continue
            new_message = new_message_object.contents

            if new_message != last_message:
                last_message = new_message
                self.__process_message_listeners(new_message_object)

                try:
                    if new_message[0] != self.command_prefix:
                        continue
                except IndexError as message_error:
                    if new_message == "":
                        continue
                    raise whatsapp.exceptions.InvalidPrefixError() from message_error

                command_message = new_message[1:]

                try:
                    if not command_message.split()[0] in self.__commands:
                        self.send_message("Command not found!")
                        continue
                except IndexError:
                    self.send_message("Command not found!")
                    continue

                for command in self.__commands:
                    if command == command_message.split()[0]:
                        function_name = self.__commands[command][0]
                        arguments = command_message.split()[1:]
                        self.__process_commands(function_name, arguments, new_message_object, command)
                        break

    @__needs_client_running
    def log_out(self) -> None:
        """Logs out of Whatsapp.
        After this being called, the function will automatically call whatsapp.client.WhatsappClient.stop().
        """
        self.__logger.log(20, "Logging out.")
        # Retrieve the settings button and click it.
        self.__browser.find_element_by_xpath(
            "/html/body/div[1]/div/div/div[3]/div/header/div[2]/div/span/div[3]/div").click()
        time.sleep(1)

        # Retrieve the logout button and click it.
        self.__browser.find_element_by_xpath(
            "/html/body/div[1]/div/div/div[3]/div/header/div[2]/div/span/div[3]/span/div/ul/li[7]").click()
        time.sleep(1)
        # If there is a warning pop up, click confirm.
        try:
            self.__browser.find_element_by_xpath(
                "/html/body/div[1]/div/span[2]/div/div/div/div/div/div/div[3]/div[2]").click()
        except selenium.common.exceptions.NoSuchElementException:
            pass
        self.stop()

    @__needs_client_running
    def stop(self) -> None:
        """Stops the Whatsapp Client (Doesn't log out).
        """
        self.__logger.log(20, "Stopping client.")
        self.__running = False

        self.__browser.quit()
