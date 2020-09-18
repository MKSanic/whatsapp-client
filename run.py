#Import the needed libraries
import whatsapp
import time
import wikipedia
from requests_html import HTMLSession
from googletrans import Translator
import random
from pytube import YouTube
import os
import importlib
from gtts import gTTS

#Define the responses for the !autosend command
autosend_responses = {}

#Define the default language for the global argument -SP
language = "en"

#Make a Whatsapp Client
client = whatsapp.WhatsappClient()

#Define the !stop command

@client.command("stop", "Stops the Whatsapp Bot")
def stop(arguments):

    #Stop the Whatsapp Client and exit

    client.stop()
    exit()


#Define the !calculate command

@client.command("calculate", """Calculator
                                <first number> <calculation type> <second number>""")
def calculate(arguments):

    #If no arguments given, return an error
    if len(arguments) == 0:
            answer = "Error: no arguments given"
            return answer

    #Make sure the first character of the first argument is a number, for security
    if not arguments[0][0].isdigit():
        answer = "Error: first value is not a number"
    else:
        #Yes, I know, eval is very dangerous, but I couldnt think of anything else
        answer = eval(arguments[0])
    
    return answer


#Define the !wikipedia command

@client.command("wikipedia", """Search for an article summary on Wikipedia
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

    return answer

#Define the !google command

@client.command("google", """Search on Google
                             <Google search>""")
def google(arguments):

    #If no arguments given, return an error

    if len(arguments) == 0:
        answer = "Error: no arguments given"
        return answer

    #Try to look up the search on google

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

    return answer

#Define the !autosend command

@client.command("autosend", """Automatticly responds to messages with the message given in it
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
        if response in message.contents:
            client.send_message(autosend_responses[response])

#Define the !translate command

@client.command("translate", """Google Translate
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

@client.command("random", """Returns a random number
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
    
    answer = random.randint(int(arguments[0]),int(arguments[1]))
    
    return answer

#Define the !spam command

@client.command("spam", """Spams the chat
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

@client.command("movebot", """Move the bot to another chat
                              <chat>""")
def movebot(arguments):
    #These commands are required. Selenium will return an error if the user switch the chat without using !movebot
    client.set_chat(' '.join(arguments[0:]))
    time.sleep(10)
    client.sendInput = client.browser.find_element_by_xpath("/html/body/div[1]/div/div/div[4]/div/footer/div[1]/div[2]/div/div[2]")
    answer = "Bot has been moved to this chat"
    return answer

@client.command("debug", """Toggle debug modes
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

@client.command("ytdownload", """YT downloader
                                 <YT URL>""")
def yt_downloader(arguments):
    if len(arguments) < 1:
        return "Please give 1 argument!"
    vid = YouTube(''.join(arguments[0:]))
    client.send_message("Video title: %s" % vid.title)
    client.send_message("Downloading...")
    vidstrm = vid.streams.first()
    vidstrm.download("./")
    client.send_message("Done!")
    try:
        client.send_file(os.path.realpath("./%s") % vidstrm.default_filename, file_type="img")
    except whatsapp.FileTooBigError:
        client.send_message("File too big to be sended!")
    os.remove("./%s" % vidstrm.default_filename)

@client.command("prefix", "Set the command prefix")
def prefix(arguments):
    if len(arguments) < 1:
        return "This command needs atleast one argument!"
    client.command_prefix = str(arguments[0])[0]
    return "Set command prefix to %s" % str(arguments[0])[0]

@client.command("exec", "Executes script in program")
def execute(arguments):
    try:
        exec(str(arguments[0]), globals())
    except Exception as e:
        client.send_message(e)

@client.command("reload", "Reloads Whatsapp package. Restarts client")
def reload(arguments):
    client.stop()
    importlib.reload(whatsapp)
    client.run()

@client.command("speak", """Returns the text given in a mp3
                            <language> <text>""")
def speak(arguments):
    try:
        speaker = gTTS(lang=arguments[0], text=' '.join(arguments[1:]))
        speaker.save("./message.mp3")
    except AssertionError:
        return "Please give 2 arguments!"
    except ValueError:
        return "Language not supported!"
    client.send_file(os.path.realpath("./message.mp3"), file_type="img")
    os.remove("./message.mp3")

@client.global_argument("-S")
def silent_command(function, arguments):
    function(arguments)


@client.global_argument("-SP")
def speak_command(function, arguments):
    answer = function(arguments)
    speaker = gTTS(lang=language, text=answer)
    speaker.save("./message.mp3")
    client.send_file(os.path.realpath("./message.mp3"), file_type="img")
    os.remove("./message.mp3")

@client.command("splang", "Sets the language for the -SP command")
def splang(arguments):
    language = arguments[0]

#Start the Whatsapp Client
client.run()