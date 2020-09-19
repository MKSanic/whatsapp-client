# Made by 14 year old NaN8279
#   |   |     |
#   |   |     |
#   |   |     |
#   |    _____|
#   |         |
#   |         |
#   |         |


# Import the needed libraries
from selenium import webdriver
import selenium.common.exceptions
import time
import traceback
import os
from .exceptions import FileTooBigError, ClientNotStartedError
from .exceptions import UnknownFileTypeError, CommandNotFoundError
from .exceptions import UnknownChatError
from .message import Message
from .persons import Self, Other, Person
from webdriver_manager.chrome import ChromeDriverManager
import inspect


class WhatsappClient(object):

    def __init__(self):
        """
        A Whatsapp Client
        """

        # Define the commands dictionary
        self.commands = {}
        self.commands["help"] = [self.__help_menu, "Returns help messages"]
        self.on_messages = []
        self.on_loops = []
        self.global_arguments = {}
        self.command_prefix = "!"
        self.debug_exception = False
        self.debug_traceback = False

    def __handle_error(self, e):
        # If the debug exception mode is turned on, send the exception to
        # Whatsapp
        if self.debug_exception == True:
            self.send_message("Error occured:\n %s" % e)
            
        # Else, if the debug tracebac mode is turned on, send the traceback
        # to Whatsapp
        elif self.debug_traceback == True:
            self.send_message("Error occured:\n %s" %
                               traceback.format_exc())

        # Else, send an error message to Whatsapp
        else:
            self.send_message("An unknown error occured")

    def set_chat(self, chat_name):
        """
        Sets the chat the bot is on\n
        chat_name = string, name of the chat to go to
        """

        chats = self.browser.find_element_by_id("pane-side") \
                            .find_elements_by_tag_name("span")
        for chat in chats:
            if chat.text == chat_name:
                chat.click()
                return
        raise UnknownChatError(chat_name)

    def command(self, name, help_message=None):
        """
        A command decorator\n
        name = name of the command without the prefix, for example 'test'\n
        The prefix of a command is the command_prefix variable of this class\n
        help_message = the help message for the user. Default is None\n
        Can be a function with 1 or 2 argument.\n
        The first argument will be the a list of arguments the user gave\n
        The second argument will be a message object\n
        The string the function returns is the answer for the user.\n
        The function doesn't need to return something
        """

        # Add the command to the commands dictionary
        def add_command(command_function):
            self.commands[name] = [command_function, help_message]

            # Define the function to run the command
            def run_command(arguments):
                command_function(arguments)

            return run_command

        return add_command

    def remove_command(self, name):
        # Try to remove the command from the commands dictionary
        try:
            self.commands.pop(name)
        except KeyError:
            raise CommandNotFoundError()

    def on_message(self, on_message_function):
        """
        A on_message decorator\n
        This runs when a new mesage is received\n
        Must be a function with 1 argument, a message object\n
        """

        # Add the listener to the on_message list
        self.on_messages.append(on_message_function)

        # Define the function to run the listener
        def run_on_message(message):
            on_message_function(message)

        return run_on_message

    def on_loop(self, on_loop_function):
        """
        A on_loop decorator\n
        This runs everytime the bot checks for new messages
        """

        # Add the listener to the on_loops list
        self.on_loops.append(on_loop_function)

        # Define the function to run the listener
        def run_on_message():
            on_loop_function()

        return run_on_message

    def global_argument(self, argument):
        """
        A global_argument decorator\n
        name = name of the first argument after a command\n
        The function runs instead of the normal process command function
        when the user gives the given argument\n
        Must be a function with 2 argument, the first one being the function
        to run for the command, the second one to be the arguments\n
        """

        # Add the argument to the global_arguments dictionary
        def add_command(process_command_function):
            self.global_arguments[argument] = process_command_function

            #  Define the function to run the command
            def run_command(function_name, arguments):
                process_command_function(function_name, arguments)
            return run_command

        return add_command

    def process_commands(self, function_name, arguments, message_object):
        """
        Parses commands\n
        function_name = a function to execute for the command\n
        arguments = arguments the user gave
        """

        try:
            # If the first argument is in global_arguments,
            # run the given function to process the command
            if len(arguments) > 0:
                for global_argument in self.global_arguments:
                    if arguments[0] == global_argument:
                        self.global_arguments[global_argument](function_name,
                                                               arguments[1:])
                        return

            args = inspect.signature(function_name).parameters
            if len(args) < 1:
                answer = function_name()
            elif len(args) == 1:
                answer = function_name(arguments)
            elif len(args) == 2:
                answer = function_name(arguments, message_object)
            # Send the answer
            if answer is not None:
                self.send_message(answer)

        # If there are any errors while running the function, handle the
        # exception
        except Exception as e:
            self.__handle_error(e)

    def process_message_listeners(self, message):
        """
        Executes all on message listeners
        """

        # Get the message listeners
        on_message_listeners = self.on_messages

        # Run the message listeners
        for listener in on_message_listeners:
            try:
                listener(message)
            # If there are any errors while running the function, handle the
            # exception
            except Exception as e:
                self.__handle_error(e)

    def process_loop_listeners(self):
        """
        Executes all on loop listeners
        """

        # Get the message listeners
        on_loop_listeners = self.on_loops

        # Run the message listeners
        for listener in on_loop_listeners:
            try:
                listener()
            # If there are any errors while running the function, handle the
            # exception
            except Exception as e:
                self.__handle_error(e)

    def send_message(self, message):
        """
        Sends a message to the user\n
        message = message to send
        """

        # Make the message a string
        message = str(message)

        # Send a message for each line in the message to send
        for to_send in message.splitlines():
            try:
                self.sendInput.clear()
                self.sendInput.send_keys(to_send + "\n")
            except selenium.common.exceptions.StaleElementReferenceException:
                return None

    def send_file(self, file_path, file_type="other"):
        """
        Sends a file to the user\n
        file_path = file path for the file to send\n
        file_type = type of the file. String. Default other, can be other or img
        """

        # Make the message a string
        file_path = str(file_path)

        # Make sure the file is under the limit of 64MB, else, raise an error
        file_size = os.path.getsize(file_path)
        if file_size > 64000000:
            raise FileTooBigError(file_size)

        # Get the button for attach files and click it
        attach_file_button = self.browser.find_element_by_xpath(
            "/html/body/div[1]/div/div/div[4]/div/footer/div[1]/div[1]/div[2]/div")
        attach_file_button.click()

        # Find the file input box and send the file path
        if file_type == "other":
            file_input = self.browser.find_element_by_xpath(
                "/html/body/div[1]/div/div/div[4]/div/footer/div[1]/div[1]/div[2]/span/div/div/ul/li[3]/button/input")
        elif file_type == "img":
            file_input = self.browser.find_element_by_xpath(
                "/html/body/div[1]/div/div/div[4]/div/footer/div[1]/div[1]/div[2]/span/div/div/ul/li[1]/button/input")
        else:
            raise UnknownFileTypeError()

        file_input.send_keys(file_path)
        file_is_sended = False
        time.sleep(0.5)

        # Wait for the send button to appear and click the send button
        while file_is_sended is False:
            try:
                send_button = self.browser.find_element_by_xpath(
                    "/html/body/div[1]/div/div/div[2]/div[2]/span/div/span/div/div/div[2]/span/div")
                send_button.click()
                file_is_sended = True
            except selenium.common.exceptions.NoSuchElementException:
                time.sleep(0.5)
                continue

    def get_last_message(self):
        """
        Returns the last message
        """

        # Get the messages
        messages = self.browser.find_elements_by_class_name(
            "focusable-list-item")

        # Get the newest message, and if there isnt one, return None
        try:
            new_message = messages[len(messages) - 1]
            new_message_text_element = new_message.find_element_by_css_selector(
                ".selectable-text")

            if "message-out" in new_message.get_attribute("class"):
                sender = Person(Self)
            else:
                sender = Person(Other)

            new_message_text_emoji = self.browser.execute_script("""
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

            return Message(sender, new_message_text_emoji)
        except Exception:
            return None

    def __help_menu(self, arguments):

        # If there are no arguments given, return a list of commands
        if len(arguments) == 0:

            answer = "List of commands:\n"
            for command in self.commands:
                answer = answer + "%s, " % command.replace("!", "")

            return answer

        # Else, look in the command dictionary, if the command the user gave is
        # found, return the help message for that command
        else:

            for command in self.commands:
                if arguments[0] == command.replace("!", ""):
                    answer = self.commands[command][1]

                    return answer

        return "Command not found!"

    def run(self):
        """
        Starts the Whatsapp Client
        """

        self.running = True

        # Open Firefox
        self.browser = webdriver.Chrome(ChromeDriverManager().install())

        # Go to Whatsapp Web
        self.browser.get("https://web.whatsapp.com/")

        # Define the lastMessage variable to prevent spam
        last_message = ""

        # Start the bot loop
        while self.running:

            # Redefine the variable to send answers to, to prevent errors
            try:
                self.sendInput = self.browser.find_element_by_xpath(
                    "/html/body/div[1]/div/div/div[4]/div/footer/div[1]/div[2]/div/div[2]")
            except BaseException:
                time.sleep(5)
                continue

            # Run the on_loop listeners
            self.process_loop_listeners()

            # Get the newest message, and if there isnt one, wait and try again
            new_message_object = self.get_last_message()
            if new_message_object is None:
                time.sleep(0.5)
                continue
            new_message = new_message_object.contents

            # If the message isn't the last message, then return an answer
            if new_message != last_message:
                last_message = new_message
                self.process_message_listeners(new_message_object)

                # Check if the message starts with the command prefix and if it
                # doesn't, continue
                if new_message[0] != self.command_prefix:
                    continue

                command_message = new_message[1:]

                # If the command is not in the commands dictionary, return an
                # error
                try:
                    if not command_message.split()[0] in self.commands:
                        self.send_message("Command not found!")
                        continue
                except IndexError:
                    self.send_message("Command not found!")
                    continue

                # Scan all the commands and check if there is a command
                # matching the users input
                for command in self.commands:
                    if command == command_message.split()[0]:

                        # Get the function name, and the arguments
                        functionName = self.commands[command][0]
                        arguments = command_message.split()[1:]

                        # Send the result to the user
                        self.process_commands(functionName, arguments, new_message_object)

                        # Continue
                        break

    def stop(self):
        """
        Stops the Whatsapp Client
        """

        # Stop the bot loop
        self.running = False

        # Log out of Whatsapp
        # Click the button for the menu
        self.browser.find_element_by_xpath(
            "/html/body/div[1]/div/div/div[3]/div/header/div[2]/div/span/div[3]/div").click()
        # Click the log out button
        time.sleep(1)
        self.browser.find_element_by_xpath(
            "/html/body/div[1]/div/div/div[3]/div/header/div[2]/div/span/div[3]/span/div/ul/li[7]").click()

        # Wait to log out
        time.sleep(1)

        # If there is a log out popup, click log out
        try:
            self.browser.find_element_by_xpath(
                "/html/body/div[1]/div/span[2]/div/div/div/div/div/div/div[3]/div[2]").click()
        except selenium.common.exceptions.NoSuchElementException:
            pass

        # Quit the browser
        self.browser.quit()
