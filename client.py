#Import the needed libraries
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
import types
import json
#Import the answer classes and commands
from commands import *

def command_parser(commandType, returnName, arguments):

    """
    Parses a command and then sends a message to the user\n
    commandType = the type command. class or return\n
    answerName = the class to call if the commandType = class or the answer to send if the commandType = return\n
    arguments = the arguments the user gave\n
    """

    #If the command type is return, just return the return text
    if commandType == "return":
        send_message(returnName)

    #If the command type is a class, call the class and return the answer the class gives
    elif commandType == "class":
        #Call the class
        answerClass = globals()[returnName](arguments)
        #If the class has commands to execute in the client, execute them, and return the answer
        try:
            exec(answerClass.execute_commands_in_client())
            send_message(answerClass.send_answer())
        #If the class hasnt commands to execute in the client, return the answer
        except AttributeError:
            send_message(answerClass.send_answer())
            

    #Else, return an unknown command type
    else:
        send_message("Unknown commandtype!")

def send_message(message):

    """
    Sends a message to the user\n
    message = message to send
    """

    global sendInput
    for toSend in message.splitlines():
        sendInput.clear()
        sendInput.send_keys(toSend + "\n")

def get_last_message():

    """
    Returns the last message
    """
    
    global browser
    #Get the messages
    messages = browser.find_elements_by_class_name("_3FXB1")
    #Get the newest message, and if there isnt one, return None
    try:
        newMessage = messages[len(messages) - 1].text
        return newMessage
    except:
        return None

#Open Firefox

browser = webdriver.Firefox()

#Goto Whatsapp Web

browser.get("https://web.whatsapp.com/")

#Wait for the user to scan the QR-code and select a chat

time.sleep(15)

#Define the lastMessage variable to prevent spam

lastMessage = ""

#Define the variable to send answers to

sendInput = browser.find_elements_by_class_name("_2S1VP")[1]

#Start the bot loop

while True:
    #Get the newest message, and if there isnt one, wait and try again
    newMessage = get_last_message()
    if newMessage is None:
        time.sleep(0.5)
        continue
    #If the message isn't the last message, then return an answer
    if newMessage != lastMessage:
        #The last message is now this message
        lastMessage = newMessage
        #Scan all the commands and check if there is a command matching the users input
        for command in commands:
            if command == newMessage.split()[0]:
                #Get the command type, the return name, the arguments and the result
                commandType = commands[command]["type"]
                returnName = commands[command]["name"]
                arguments = newMessage.split()[1:]
                #Send the result to the user
                command_parser(commandType,returnName, arguments)