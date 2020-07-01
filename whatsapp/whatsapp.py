#Made by 13 year old NaN8279
#   |   ----
#   |       |
#   |       |
#   |   ----
#   |       |
#   |       |
#   |   ----


#Import the needed libraries
from selenium import webdriver
import selenium.common.exceptions
import time
import traceback
import os
from .exceptions import FileTooBigError, NoFileMessageError, UnknownFileTypeError, CommandNotFoundError, UnknownChatError
from webdriver_manager.chrome import ChromeDriverManager


class WhatsappClient(object):


    def __init__(self):

        """
        A Whatsapp Client
        """

        #Define the commands dictionary
        self.commands = {}
        self.commands["help"] = [self.helpMenu, "Returns help messages"]
        self.on_messages = []
        self.on_loops = []
        self.global_arguments = {}
        self.command_prefix = "!"
        self.debug_exception = False
        self.debug_traceback = False

    def set_chat(self, chatName):
        """
        Sets the chat the bot is on\n
        chatName = string, name of the chat to go to
        """
        chats = self.browser.find_element_by_id("pane-side").find_elements_by_tag_name("span")
        for chat in chats:
            if chat.text == chatName:
                chat.click()
                return
        raise UnknownChatError("Couldn't find chat %s" % chatName)

    def command(self, name, helpMessage = None):

        """
        A command decorator\n
        name = name of the command without the prefix, for example 'test'\n
        The prefix of a command is the command_prefix variable of this class\n
        helpMessage = the help message for the user. Default is None\n
        Must be a function with 1 argument, the arguments the user gave\n
        The string the function returns is the answer for the user. The function doesn't need to return something
        """

        #Add the command to the commands dictionary
        def add_command(command_function):

            self.commands[name] = [command_function, helpMessage]
            #Define the function to run the command
            def run_command(arguments):

                command_function(arguments)

            return run_command

        return add_command
    
    def remove_command(self, name):
        try:
            self.commands.pop(name)
        except KeyError:
            raise CommandNotFoundError("The specified command couldn't be found")

    def on_message(self, on_message_function):

        """
        A on_message decorator\n
        This runs when a new mesage is received\n
        Must be a function with 1 argument, the message the user send\n
        """

        #Add the listener to the on_message list

        self.on_messages.append(on_message_function)
        
        #Define the function to run the listener
        def run_on_message(message):

            on_message_function(message)
        
        return run_on_message

    def on_loop(self, on_loop_function):
        
        """
        A on_loop decorator\n
        This runs everytime the bot checks for new messages
        """

        #Add the listener to the on_loops list

        self.on_loops.append(on_loop_function)
        
        #Define the function to run the listener
        def run_on_message():

            on_loop_function()
        
        return run_on_message

    def global_argument(self, argument):
        """
        A global_argument decorator\n
        name = name of the first argument after a command\n
        The function runs instead of the normal process command function when the user gives the given argument\n
        Must be a function with 2 argument, the first one being the function to run for the command, the second one to be the arguments\n
        """

        #Add the argument to the global_arguments dictionary
        def add_command(process_command_function):

            self.global_arguments[argument] = process_command_function
            #Define the function to run the command
            def run_command(functionName, arguments):

                process_command_function(functionName, arguments)

            return run_command

        return add_command

    def process_commands(self, functionName, arguments):

        """
        Parses commands\n
        functionName = a function to execute for the command\n
        arguments = arguments the user gave
        """

        try:
            #If the first argument isn't -S, run the function and return an answer if the answer is not None
            if len(arguments) < 1:
                answer = functionName(arguments)
                #Send the answer if the function didn't return None
                if answer is not None:
                    self.send_message(answer)
                return

            #If the first argument is in global_arguments, run the given function to process the command
            for global_argument in self.global_arguments:
                if arguments[0] == global_argument:
                    self.global_arguments[global_argument](functionName, arguments[1:])
                    return
            #Else, run the function and send an answer if the answer isn't None
            else:
                answer = functionName(arguments)
                #Send the answer
                if answer is not None:
                    self.send_message(answer)
        
        #If there are any errors while running the function, handle the exception
        except Exception as e:
            #If the debug exception mode is turned on, send the exception to Whatsapp
            if self.debug_exception == True:
                self.send_message("Error occured:\n %s" % e)
            #Else, if the debug tracebac mode is turned on, send the traceback to Whatsapp
            elif self.debug_traceback == True:
                self.send_message("Error occured:\n %s" % traceback.format_exc())
            #Else, send an error message to Whatsapp
            else:
                self.send_message("An unknown error occured")

    def process_message_listeners(self, message):
        """
        Executes all on message listeners
        """
        #Get the message listeners
        on_message_listeners = self.on_messages
        #Run the message listeners
        for listener in on_message_listeners:
            try:
                listener(message)
            #If there are any errors while running the function, handle the exception
            except Exception as e:
                #If the debug exception mode is turned on, send the exception to Whatsapp
                if self.debug_exception == True:
                    self.send_message("Error occured:\n %s" % e)
                #Else, if the debug tracebac mode is turned on, send the traceback to Whatsapp
                elif self.debug_traceback == True:
                    self.send_message("Error occured:\n %s" % traceback.format_exc())
                #Else, send an error message to Whatsapp
                else:
                    self.send_message("An unknown error occured")

    def process_loop_listeners(self):
        """
        Executes all on loop listeners
        """
        #Get the message listeners
        on_loop_listeners = self.on_loops
        #Run the message listeners
        for listener in on_loop_listeners:
            try:
                listener()
            #If there are any errors while running the function, handle the exception
            except Exception as e:
                #If the debug exception mode is turned on, send the exception to Whatsapp
                if self.debug_exception == True:
                    self.send_message("Error occured:\n %s" % e)
                #Else, if the debug tracebac mode is turned on, send the traceback to Whatsapp
                elif self.debug_traceback == True:
                    self.send_message("Error occured:\n %s" % traceback.format_exc())
                #Else, send an error message to Whatsapp
                else:
                    self.send_message("An unknown error occured")

    def send_message(self, message):

        """
        Sends a message to the user\n
        message = message to send
        """

        #Make the message a string
        message = str(message)

        #Send a message for each line in the message to send
        for toSend in message.splitlines():
            try:
                self.sendInput.clear()
                self.sendInput.send_keys(toSend + "\n")
            except selenium.common.exceptions.StaleElementReferenceException:
                return None

    def send_file(self, file_path, file_type="other"):
        """
        Sends a file to the user\n
        file_path = file path for the file to send\n
        file_type = type of the file. String. Default other, can be other or img
        """

        #Make the message a string
        file_path = str(file_path)

        #Make sure the file is under the limit of 64MB, else, raise an error

        file_size = os.path.getsize(file_path)
        if file_size > 64000000:
            raise FileTooBigError("The file is over 64MB (file is %s bytes)" % file_size)

        #Get the button for attach files and click it
        attach_file_button = self.browser.find_element_by_xpath("/html/body/div[1]/div/div/div[4]/div/header/div[3]/div/div[2]")
        attach_file_button.click()
        #Find the file input box and send the file path
        if file_type == "other":
            file_input = self.browser.find_element_by_xpath("/html/body/div[1]/div/div/div[4]/div/header/div[3]/div/div[2]/span/div/div/ul/li[3]/button/input")
        elif file_type == "img":
            file_input = self.browser.find_element_by_xpath("/html/body/div[1]/div/div/div[4]/div/header/div[3]/div/div[2]/span/div/div/ul/li[1]/button/input")
        else:
            raise UnknownFileTypeError("There was given an unknown file type to the send_file function")
        file_input.send_keys(file_path)
        
        file_is_sended = False
        
        time.sleep(0.5)

        #Wait for the send button to appear and click the send button
        while file_is_sended is False:
            try:
                send_button = self.browser.find_element_by_xpath("/html/body/div[1]/div/div/div[2]/div[2]/span/div/span/div/div/div[2]/span/div/div")
                send_button.click()
                file_is_sended = True
            except selenium.common.exceptions.NoSuchElementException:
                time.sleep(0.5)
                continue

    def get_last_message(self):

        """
        Returns the last message
        """
    
        #Get the messages
        messages = self.browser.find_elements_by_class_name("focusable-list-item")
        #Get the newest message, and if there isnt one, return None
        try:
            newMessage = messages[len(messages) - 1]
            newMessageTextElement = newMessage.find_element_by_css_selector(".selectable-text")
            newMessageText = newMessageTextElement.text
            
            newMessageTextEmoji = self.browser.execute_script("""
                                            var newMessage = arguments[0];
                                            var text = newMessage.firstChild;
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
                                        """, newMessageTextElement)

            return newMessageText
        except Exception:
            return None

    def get_last_message_element(self):
        
        """
        Returns the last message elements
        """
    
        #Get the messages
        messages = self.browser.find_elements_by_class_name("focusable-list-item")
        #Get the newest message, and if there isnt one, return None
        try:
            newMessage = messages[len(messages) - 1]

            return newMessage
        except:
            return None

    def helpMenu(self, arguments):
        #If there are no arguments given, return a list of commands
    
        if len(arguments) == 0:
    
            answer = "List of commands:\n"
            for command in self.commands:
                answer = answer + "%s, " % command.replace("!","")
    
            return answer
    
        #Else, look in the command dictionary, if the command the user gave is found, return the help message for that command
    
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

        #Open Firefox

        self.browser = webdriver.Chrome(ChromeDriverManager().install())

        #Goto Whatsapp Web

        self.browser.get("https://web.whatsapp.com/")

        #Define the lastMessage variable to prevent spam

        lastMessage = ""

        #Start the bot loop

        while self.running:

            #Redefine the variable to send answers to, to prevent errors
            
            try:
                self.sendInput = self.browser.find_element_by_xpath("/html/body/div[1]/div/div/div[4]/div/footer/div[1]/div[2]/div/div[2]")
            except:
                time.sleep(5)
                continue

            #Run the on_loop listeners

            self.process_loop_listeners()
            
            #Get the newest message, and if there isnt one, wait and try again
            newMessage = self.get_last_message()
            
            if newMessage is None or newMessage == "":
                time.sleep(0.5)
                continue
            
            #If the message isn't the last message, then return an answer
            
            if newMessage != lastMessage:
                lastMessage = newMessage

                self.process_message_listeners(newMessage)

                #Check if the message starts with the command prefix and if it doesn't, continue

                if newMessage[0] != self.command_prefix:
                    continue

                commandMessage = newMessage[1:]

                #If the command is not in the commands dictionary, return an error
                if not commandMessage.split()[0] in self.commands:
                    self.send_message("Command not found!")
                    continue

                #Scan all the commands and check if there is a command matching the users input
            
                for command in self.commands:
                    if command == commandMessage.split()[0]:
            
                        #Get the function name, and the arguments
            
                        functionName = self.commands[command][0]
                        arguments = commandMessage.split()[1:]
            
                        #Send the result to the user
            
                        self.process_commands(functionName, arguments)
                        
                        #Continue
                        break

    def stop(self):
        
        """
        Stops the Whatsapp Client
        """
        #Stop the bot loop
        self.running = False
        #Log out of Whatsapp
        #Click the button for the menu
        self.browser.find_element_by_xpath("/html/body/div[1]/div/div/div[3]/div/header/div[2]/div/span/div[3]/div").click()
        #Click the log out button
        time.sleep(1)
        self.browser.find_element_by_xpath("/html/body/div[1]/div/div/div[3]/div/header/div[2]/div/span/div[3]/span/div/ul/li[6]").click()
        #Wait to log out
        time.sleep(1)
        #If there is a log out popup, click log out
        try:
            self.browser.find_element_by_xpath("/html/body/div[1]/div/span[2]/div/div/div/div/div/div/div[3]/div[2]").click()
        except selenium.common.exceptions.NoSuchElementException:
            pass
        #Quit the browser
        self.browser.quit()