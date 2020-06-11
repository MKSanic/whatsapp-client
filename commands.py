#Made by 13 year old NaN8279
#   |   ----
#   |       |
#   |       |
#   |   ----
#   |       |
#   |       |
#   |   ----

#Import the libraries for the !wikipedia, the !translate, the !randomnumber, the !movebot and the !google commands
import wikipedia
from requests_html import HTMLSession
from googletrans import Translator
import time
import random

#Define the commands

commands = {
    "!calculate": {"type": "class", "help": """Calculator
                                               <first number> <calculation type> <second number>""", "name": "Calculate"},
    "!wikipedia": {"type": "class", "help": """Search for an article summary on Wikipedia
                                               set_language <language>
                                               <article>""", "name": "Wikipedia"},
    "!google": {"type": "class", "help": """Search on Google
                                            <Google search>""", "name": "Google"},
    "!vvvvvv": {"type": "class", "help": "lol", "name": "Vvvvvv"},
    "!return": {"type": "class", "help": "it returns", "name": "Return"},
    "!translate": {"type": "class", "help": """Google Translate
                                               <source language> <destination language> <sentence>""", "name": "Translate"},
    "!help": {"type": "class", "help": "Returns help messages", "name": "HelpMenu"},
    "!movebot": {"type": "class", "help": "Move the bot to another chat", "name": "MoveBot"},
    "!randomnumber": {"type": "class", "help": """Returns a random number
                                                  <minimum number> <maximum number>""", "name": "RandomNumber"},
    "!spam": {"type": "class", "help": """Spams the chat
                                          <how many times to spam> <spam message>""", "name": "Spam"}
}

#Define the default answer class to be inherited

class Answer(object):
    #Commands to execute when the user sends a message. These commands are a executed in the client
    on_message_commands = None
    #Commands to execute when the checks for a new message. These commands are a executed in the client
    on_renew_commands = None
    def __init__(self, arguments):
        """
        Command class\n
        arguments = the arguments the user gave
        """
        self.answer = "answer"
        self.commands_in_client = None

    def send_answer(self):
        """
        Returns the answer for the command
        """
        return self.answer
        
    #This is used for commands that want to execute a command in the whatsapp client. These commands will always be executed before answering the user
    def execute_commands_in_client(self):
        """
        Returns the commands to be executed in the client
        """
        return self.commands_in_client
    

#Define the class for the !calculate command

class Calculate(Answer):
    def __init__(self, arguments):
        #If no arguments given, return an error
        if len(arguments) == 0:
            self.answer = "Error: no arguments given"
            return
        try:
            #Make sure the first character of the first argument is a number, for security
            if not arguments[0][0].isdigit():
                self.answer = "Error: first value is not a number"
            else:
                #Yes, I know, eval is very dangerous, but I couldnt think of anything else
                self.answer = eval(arguments[0])
        #Return an error if the command failed
        except:
            self.answer = "An unknown error occured"

#Define the class for the !wikipedia command

class Wikipedia(Answer):
    def __init__(self, arguments):
        #If no arguments given, return an error
        if len(arguments) == 0:
            self.answer = "Error: no arguments given"
            return
        #if the first argument is set_language, then set the language for wikipedia
        if arguments[0] == "set_language":
            wikipedia.set_lang(arguments[1])
            self.answer = "Language set to %s" % arguments[1]
            return
        #Else, look up the summary of the requested article for the answer
        try:
            self.answer = wikipedia.summary(" ".join(arguments))
        #Return an error if the page is not found
        except wikipedia.exceptions.PageError:
            self.answer = "Error: page not found"
        #Return an error if the command failed
        except:
            self.answer = "An unknown error occured"

#Define the class for the !google command

class Google(Answer):
    def __init__(self, arguments):
        #If no arguments given, return an error
        if len(arguments) == 0:
            self.answer = "Error: no arguments given"
            return
        #Try to look up the search on google
        try:
            #Format the search argument
            toSearch = " ".join(arguments).replace(" ", "+")
            #Open a HTMLSession
            request = HTMLSession()
            #Get the google search webpage with the search argument
            GoWebpage = request.get("https://www.google.com/search?q=%s" % toSearch)
            #Get the title and the link of the first search
            title = GoWebpage.html.find(".LC20lb",first=True).text
            #Format the URL so it is working
            link = GoWebpage.html.find(".iUh30", first=True).text.replace("›","/").replace(" ","")
            #Return the answer
            self.answer = "%s\n%s" % (title, link)
        #Return an error if the command failed
        except:
            self.answer = "An unknown error occured"

#Define the class for the !vvvvvv command

class Vvvvvv(Answer):
    def __init__(self, arguments):
        self.answer = "There are no easter eggs in this bot!"

#Define the class for the !translate command

class Translate(Answer):
    def __init__(self, arguments):
        #There are 3 arguments needed
        if len(arguments) < 3:
            self.answer = "Error: please give 3 arguments"
            return
        #Try to translate the word, else, return an error
        try:
            translator = Translator()
            self.answer = translator.translate(" ".join(arguments[2:]), src=arguments[0], dest=arguments[1]).text
        except:
            self.answer = "An error during translating occured"

#Define the class for the !randomnumber command

class RandomNumber(Answer):
    def __init__(self, arguments):
        if len(arguments) < 2:
            self.answer = "This command requires 2 arguments!"
            return
        #If number 1 or 2 is not a number, return an error
        if not arguments[0].isdigit() or not arguments[1].isdigit():
            self.answer = "Please enter numbers!"
            return
        #Try to get a random number. If failing, return an error
        try:
            self.answer = random.randint(int(arguments[0]),int(arguments[1]))
        #Return an error if the command failed
        except:
            self.answer = "An unknown error occured"

#Define the class for the !return command

class Return(Answer):
    #The answer is the first argument
    def __init__(self, arguments):
        try:
            self.answer = arguments[0]
        except IndexError:
            self.answer = "return"

#Define the class for the !spam command

class Spam(Answer):
    def __init__(self, arguments):
        #Return an error if there are less than 2 arguments given
        if len(arguments) < 2:
            self.answer = "This command requires 2 arguments!"
            return
        #Return an error if the first argument is not a number
        if not arguments[0].isdigit():
            self.answer = "Error: first argument is not a number"
            return
        #Define the answer
        self.answer = ""
        for i in range(int(arguments[0])):
            self.answer += "%s\n" % " ".join(arguments[1:])

#Define the class for the !movebot command

class MoveBot(Answer):
    def __init__(self, arguments):
        #Answer will be returned after the user has switched the chat
        self.answer = "Bot has been moved to this chat"
        #Define the commands to be executed
        self.commands_in_client = """
#These commands are required. sendInput will return an error if the user switch the chat without using !movebot
global sendInput
time.sleep(10)
sendInput = browser.find_element_by_xpath("/html/body/div[1]/div/div/div[4]/div/footer/div[1]/div[2]/div/div[2]")
            """

#Define the class for the !help command

class HelpMenu(Answer):
    def __init__(self, arguments):
        #If no arguments given, return a list of commands
        if len(arguments) == 0:
            self.answer = "List of commands:\n"
            for command in commands:
                self.answer = self.answer + "%s, " % command.replace("!","")
            return
        #If there is an argument given, check the commands list for the argument and return the help message
        else:
            for command in commands:
                if arguments[0] == command.replace("!", ""):
                    self.answer = commands[command]["help"]
                    return
        #If no command found, return an error
        self.answer = "Command not found"