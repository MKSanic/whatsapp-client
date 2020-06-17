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
from selenium.webdriver.common.keys import Keys
import selenium.common.exceptions
import time



class WhatsappClient(object):


    def __init__(self):

        """
        A Whatsapp Client with commands
        """

        #Define the commands dictionary
        self.commands = {}
        self.on_messages = []



    def command(self, name, helpMessage):

        """
        A command decorator\n
        name = name of the command, for example !example\n
        Must be a function with 1 argument, the arguments the user gave\n
        The function must return a string, the answer for the user
        """

        #Add the command to the commands dictionary
        def add_command(command_function):

            self.commands[name] = [command_function, helpMessage]
            #Define the function to run the command
            def run_command(arguments):

                command_function(arguments)

            return run_command

        return add_command
    

    def on_message(self, on_message_function):

        """
        A on_message decorator\n
        This runs when a new mesage is received\n
        Must be a function with 1 argument, the message the user send\n
        """

        #Add the listener to the on_message dictionary

        self.on_messages.append(on_message_function)
        
        #Define the function to run the listener
        def run_on_message(message):

            on_message_function(message)
        
        return run_on_message


    def command_parser(self, functionName, arguments):

        """
        Parses commands\n
        functionName = a function to execute for the command\n
        arguments = arguments the user gave
        """

        #Get the answer
        if len(arguments) < 1:
            answer = functionName(arguments)
            #Send the answer
            self.send_message(answer)
            return

        if arguments[0] == "-S":
            answer = functionName(arguments[1:])
        else:
            answer = functionName(arguments)
            #Send the answer
            self.send_message(answer)

    def execute_on_messages(self, message):
        """
        Executes all on message listeners
        """
        on_message_listeners = self.on_messages
        for listener in on_message_listeners:
            listener(message)

    def send_message(self, message):

        """
        Sends a message to the user\n
        message = message to send
        """

        #Make the message a string
        message = str(message)

        #Send the message
        for toSend in message.splitlines():
            self.sendInput.clear()
            self.sendInput.send_keys(toSend + "\n")


    def get_last_message(self, browser):

        """
        Returns the last message\n
        browser = the browser with Whatsapp on
        """
    
        #Get the messages
        messages = browser.find_elements_by_class_name("focusable-list-item")
        #Get the newest message, and if there isnt one, return None
        try:
            newMessage = messages[len(messages) - 1].find_element_by_css_selector(".selectable-text").text

            return newMessage
        except:
            return None


    def run(self):
        """
        Starts the Whatsapp Client
        """
        
        self.running = True

        #Open Firefox

        self.browser = webdriver.Firefox()

        #Goto Whatsapp Web

        self.browser.get("https://web.whatsapp.com/")

        #Wait for the user to scan the QR-code and select a chat

        time.sleep(15)

        #Define the lastMessage variable to prevent spam

        lastMessage = ""

        #Start the bot loop

        while self.running == True:

            #Redefine the variable to send answers to
            
            try:
                self.sendInput = self.browser.find_element_by_xpath("/html/body/div[1]/div/div/div[4]/div/footer/div[1]/div[2]/div/div[2]")
            except selenium.common.exceptions.NoSuchElementException:
                time.sleep(5)
                continue
            
            #Get the newest message, and if there isnt one, wait and try again
            newMessage = self.get_last_message(self.browser)
            
            if newMessage is None:
                time.sleep(0.5)
                continue
            
            #If the message isn't the last message, then return an answer
            
            if newMessage != lastMessage:
                lastMessage = newMessage

                self.execute_on_messages(newMessage)
            
                #Scan all the commands and check if there is a command matching the users input
            
                for command in self.commands:
                    if command == newMessage.split()[0]:
            
                        #Get the function name, and the arguments
            
                        functionName = self.commands[command][0]
                        arguments = newMessage.split()[1:]
            
                        #Send the result to the user
            
                        self.command_parser(functionName, arguments)

    def stop(self):
        
        """
        Stops the Whatsapp Client
        """
        
        self.running = False
        self.browser.quit()