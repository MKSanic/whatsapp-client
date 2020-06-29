#Import the needed libraries
import whatsapp
import time
import wikipedia
from requests_html import HTMLSession
from googletrans import Translator
import random
import pytube
import os

#Define the responses for the !autosend command
autosend_responses = {}

#Make a Whatsapp Client
client = whatsapp.WhatsappClient()

#Define the !help command
@client.command("!help", "Returns help messages")
def helpMenu(arguments):

    #If there are no arguments given, return a list of commands
    
    if len(arguments) == 0:
    
        answer = "List of commands:\n"
        for command in client.commands:
            answer = answer + "%s, " % command.replace("!","")
    
        return answer
    
    #Else, look in the command dictionary, if the command the user gave is found, return the help message for that command
    
    else:
    
        for command in client.commands:
            if arguments[0] == command.replace("!", ""):
                answer = client.commands[command][1]
                
                return answer
    
    return "Command not found!"

#Define the !stop command

@client.command("!stop", "Stops the Whatsapp Bot")
def stop(arguments):

    #Stop the Whatsapp Client and exit

    client.stop()
    exit()


#Define the !calculate command

@client.command("!calculate", """Calculator
                                 <first number> <calculation type> <second number>""")
def calculate(arguments):

    #If no arguments given, return an error
    if len(arguments) == 0:
            answer = "Error: no arguments given"
            return answer

    try:

        #Make sure the first character of the first argument is a number, for security
        if not arguments[0][0].isdigit():
            answer = "Error: first value is not a number"
        else:
            #Yes, I know, eval is very dangerous, but I couldnt think of anything else
            answer = eval(arguments[0])

    #Return an error if the command failed
    except:
        answer = "An unknown error occured"
    
    return answer


#Define the !wikipedia command

@client.command("!wikipedia", """Search for an article summary on Wikipedia
                                 set_language <language>
                                 <article>""")
def wikipedia_command(arguments):
    
    #If no arguments given, return an error

    if len(arguments) == 0:
        answer = "Error: no arguments given"
        return answer

    #If the first argument is set_language, then set the language for wikipedia

    if arguments[0] == "set_language":
        wikipedia.set_lang(arguments[1])
        answer = "Language set to %s" % arguments[1]
        return answer

    #Else, look up the summary of the requested article for the answer

    try:
        answer = wikipedia.summary(" ".join(arguments))

    #Return an error if the page is not found

    except wikipedia.exceptions.PageError:
        answer = "Error: page not found"

    #Return an error if the command failed
    '''
    except:
        answer = "An unknown error occured"
    '''
    return answer

#Define the !google command

@client.command("!google", """Search on Google
                              <Google search>""")
def google(arguments):

    #If no arguments given, return an error

    if len(arguments) == 0:
        answer = "Error: no arguments given"
        return answer

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
        answer = "%s\n%s" % (title, link)

    #Return an error if the command failed

    except:
        answer = "An unknown error occured"

    return answer

#Define the !autosend command

@client.command("!autosend", """Automatticly responds to messages with the message given in it
                                add <message> <response>
                                remove <message>
                                list""")
def autosend(arguments):
    global autosend_responses
    #If there are no arguments given, return an error
    if len(arguments) < 1:
        answer = "This command needs atleast 1 argument!"
        return answer

    if arguments[0] == "add":
        #If the user wants to add a response, there are atleast 3 arguments needed
        if len(arguments) < 3:
            answer = "This command needs atleast 3 arguments!"
            return answer
        #Add the resonse to the response dictionary and return
        autosend_responses[arguments[1]] = ' '.join(arguments[2:])
        
        answer = "Added %s with response %s" % (arguments[1], ' '.join(arguments[2:]))
        return answer
    
    elif arguments[0] == "remove":
        #If the user wants to remove a response, atleast 2 arguments are needed
        if len(arguments) < 2:
            answer = "This command needs atleast 2 arguments!"
            return answer
        try:
            #Remove the response from the response dictionary, and if it isn't in the dictionary, return an error
            autosend_responses.pop(arguments[1])
            answer = "Removed %s" % arguments[1]
        except KeyError:
            answer = "Couldn't find message %s" % arguments[1]
        return answer

    elif arguments[0] == "list":
        #Return a list of responses
        answer = "List of responses:\n"
        for response in autosend_responses:
            answer = answer + "%s: %s\n" % (response, autosend_responses[response])
        return answer
    #Else, return an error
    else:
        answer = "Unknown argument"
        return answer

#Define the message listener for the !autosend command

@client.on_message
def auto_respond(message):
    global autosend_responses
    #If the message the user sent is in the response dictionary, then send the response
    for response in autosend_responses:
        if response in message:
            client.send_message(autosend_responses[response])

#Define the !translate command

@client.command("!translate", """Google Translate
                                 <source language> <destination language> <sentence>""")
def translate(arguments):

    #There are 3 arguments needed

    if len(arguments) < 3:
        answer = "Error: please give 3 arguments"
        return answer
    
    #Try to translate the word, else, return an error
    
    try:
        translator = Translator()
        answer = translator.translate(" ".join(arguments[2:]), src=arguments[0], dest=arguments[1]).text
    
    except:
    
        answer = "An error during translating occured"
    
    return answer

#Define the !random command

@client.command("!random", """Returns a random number
                              <minimum number> <maximum number>""")
def randomnumber(arguments):
    #If there are less than 2 arguments given, return an error
    if len(arguments) < 2:
        answer = "This command requires 2 arguments!"
        return answer

    #If number 1 or 2 is not a number, return an error
    
    if not arguments[0].isdigit() or not arguments[1].isdigit():
        answer = "Please enter numbers!"
        return answer
    
    #Try to get a random number. If failing, return an error
    
    try:
        answer = random.randint(int(arguments[0]),int(arguments[1]))
    
    #Return an error if the command failed
    
    except:
        answer = "An unknown error occured"
    
    return answer

#Define the !spam command

@client.command("!spam", """Spams the chat
                            <how many times to spam> <spam message>""")
def spam(arguments):
    
    #Return an error if there are less than 2 arguments given
    
    if len(arguments) < 2:
        answer = "This command requires 2 arguments!"
        return answer
    
    #Return an error if the first argument is not a number
    
    if not arguments[0].isdigit():
        answer = "Error: first argument is not a number"
        return answer
    
    #Define the answer
    
    answer = ""
    for i in range(int(arguments[0])):
        answer += "%s\n" % " ".join(arguments[1:])
    
    return answer

#Define the !movebot command

@client.command("!movebot", "Move the bot to another chat")
def movebot(arguments):
    #These commands are required. Selenium will return an error if the user switch the chat without using !movebot
    time.sleep(10)
    client.sendInput = client.browser.find_element_by_xpath("/html/body/div[1]/div/div/div[4]/div/footer/div[1]/div[2]/div/div[2]")
    answer = "Bot has been moved to this chat"
    return answer

@client.command("!debug", """Toggle debug modes
                             <mode>
                             Modes are: exception, traceback and off""")
def debug(arguments):
    if len(arguments) < 1:
        return "This command needs atleast one argument!"
    if arguments[0] == "exception":
        client.debug_exception = True
        client.debug_traceback = False
        return "Turned mode exception on"
    elif arguments[0] == "traceback":
        client.debug_exception = False
        client.debug_traceback = True
        return "Turned mode traceback on"
    elif arguments[0] == "off":
        client.debug_exception = False
        client.debug_traceback = False
        return "Turned debugging off"
    else:
        return "Unknown mode!"

@client.command("!ytdownload", """YT downloader
                                  <YT URL>""")
def yt_downloader(arguments):
    if len(arguments) < 1:
        return "Please give 1 argument!"
    vid = pytube.YouTube(arguments[0])
    client.send_message("Video title: %s" % vid.title)
    client.send_message("Downloading...")
    vidstrm = vid.streams.first()
    vidstrm.download("./")
    client.send_message("Done!")
    try:
        client.send_file(os.path.realpath("./%s") % vidstrm.default_filename)
    except whatsapp.FileTooBigError:
        client.send_message("File too big to be sended!")
    os.remove("./%s" % vidstrm.default_filename)

#Start the Whatsapp Client
client.run()