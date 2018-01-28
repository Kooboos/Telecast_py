#imports
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as ec
from collections import deque
from selenium.webdriver.common.keys import Keys
import time
#________________________________________________________________________#
#Chromedriver
browser = webdriver.Chrome()
browser.get('https://web.telegram.org/#/im')
#________________________________________________________________________#
#Global variables. get rid of these fucking things ASAP

# Home Group
global HOME_GROUP
HOME_GROUP = 'PAID GROUP'

# GroupQueue
global groupQueue
groupQueue = deque([])

#groupChats
global groupChats

#Selected Group
global selectedGroup

#Last Messagege Dictionary
global lastMessageDict
lastMessageDict = {}

#Message Stack
global MESSAGE_STACK
MESSAGE_STACK = []

#Selected group title
global SELECTED_GROUP_TITLE
SELECTED_GROUP_TITLE = 'Whale Group'

#trigger for bot loop. set after selectGroups runs successfully
global READY
READY = False
#________________________________________________________________________#
#Lets the user select groups to track
def selectGroups():
    index = 1
    global groupChats
    for chat in groupChats:
        title= chat.find_elements_by_css_selector("div.im_dialog_peer")[0].text
        print(str(index) + '. ' + title)
        index+=1
    
    #once chats are printed, ask user for csv of indexes of groupchats they want to track
    listOfIndexOfChats = []
    while True:
        try:
            groupNumber = int(input("Please input the number of the groupchat you want to track (any non-number to proceed): "))
            listOfIndexOfChats.append(groupNumber)
        except ValueError:
            break
            
    #now that we have the group indeces, use global variable to change indeces to chatNames
    userChats = []
    for index in listOfIndexOfChats:
        userChats.append(groupChats[index-1])

    #set global to the selectedUserChats
    groupChats = userChats
    
    print('selectGroups ran successfully')
    print('new chats: \n')

#________________________________________________________________________#
#Creates dictionairy of last messages in each group
def initializeDict():
    print(lastMessageDict)
#     for some reason error on first run after log in unless this line is her
#    groupChats[0].click
    
    for chat in groupChats:
        chat.click()
#         time.sleep(2)
        SELECTED_GROUP_TITLE = chat.find_elements_by_css_selector("div.im_dialog_peer")[0].text
        while True:
            try:
                messages = browser.find_elements_by_class_name("im_message_text")
                textMessages = []
                #change array of WebElements to array of strings. easier to work with, avoid errors
                for webElement in messages:
                    textMessages.append(webElement.text)
                #for some reason there were empty strings being grabbed by selenium. removing them here    
                textMessages = list(filter(None, textMessages))
                key_gc = SELECTED_GROUP_TITLE
                lastMessageDict[key_gc] = textMessages[-1]
                print('finished initializing: ' + SELECTED_GROUP_TITLE)
                break
            except:
                print(SELECTED_GROUP_TITLE + 'did not load yet, trying again.')
    print(lastMessageDict)
    print('initializeDict ran successfully')
#________________________________________________________________________#
#groupQueueBuilder
def groupQueueBuilder():
    for groupChat in groupChats:
        oneBadgeArray = groupChat.find_elements_by_css_selector("span.im_dialog_badge.badge")
#         TO DO : make it not take messages from HOME GROUP
        if(oneBadgeArray[0].text!=""):
            #get index and use this index in titlesArray
            oneTitleArray = groupChat.find_elements_by_css_selector("div.im_dialog_peer")
            if(oneTitleArray[0].text not in groupQueue):
                groupQueue.append(oneTitleArray[0].text)
    print('groupQueueBuilder ran successfully')
    print(groupQueue)
#________________________________________________________________________#
#groupFinder - Takes in name of group finds it selects it
def groupFinder(name):
    groupQueue.popleft()
    #print(chats)
    for chat in groupChats:
        titleArray = chat.find_elements_by_css_selector("div.im_dialog_peer")
        if(titleArray[0].text == name):
            chat.click()
            global SELECTED_GROUP_TITLE
            SELECTED_GROUP_TITLE = titleArray[0].text
            break;
            
    print('groupFinder ran successfully')
print(groupQueue)
#________________________________________________________________________#
#Create push method to click on 'home chat' and paste and send it there.
# checks via dictionary which messages to push
def createMessageStack():
    MESSAGE_STACK.clear()
    messages = browser.find_elements_by_class_name("im_message_text")
    textMessages = []
    #change array of WebElements to array of strings. easier to work with, avoid errors
    for webElement in messages:
        textMessages.append(webElement.text)
    #for some reason there were empty strings being grabbed by selenium. removing them here    
    textMessages = list(filter(None, textMessages))
    #reversing list to make FIFO
    textMessages.reverse()
    print(lastMessageDict[SELECTED_GROUP_TITLE])
    for message in textMessages:
        
        if(message != lastMessageDict[SELECTED_GROUP_TITLE]):
            MESSAGE_STACK.append(message)
        else:
#             SHOULD RUN WHEN MESSAGES ARE PUSHED
            
            break
    print('createMessageStack ran successfully')
    print('message Stack:')
    print(MESSAGE_STACK)
#________________________________________________________________________#
# Broadcast Method
def broadCast():
    #select home chat
    print('Will now be sending:')
    print(MESSAGE_STACK)
    MESSAGE_STACK.reverse()
    for chat in groupChats:
        titleArray = chat.find_elements_by_css_selector("div.im_dialog_peer")
        if(titleArray[0].text == HOME_GROUP):
            chat.click()
            break
    
    #once homechat is selected, send messages one by one.
    textBox = browser.find_elements_by_class_name('composer_rich_textarea')[0]
    for message in MESSAGE_STACK:        
        textBox.send_keys(SELECTED_GROUP_TITLE + ": " + message)
        textBox.send_keys(Keys.RETURN)
    if(len(MESSAGE_STACK) != 0):
        lastMessageDict[SELECTED_GROUP_TITLE] = MESSAGE_STACK[-1]
    #clean up after sending messages.
    MESSAGE_STACK.clear()
    print('broadcast ran successfully')
print(SELECTED_GROUP_TITLE)
#________________________________________________________________________#
#User prompt to run BotLoop
while True:
    print('inside user prompt')
    try:
        userPrompt = input("Please type 'ready' after signing in. Telecast will then run.")            
        
    except ValueError:
        print("You gotta type in 'ready' exactly like that, bud...")
        continue

    else:
        if(userPrompt == 'ready'):
            global READY
            READY = True
            break
        else:
            continue

#________________________________________________________________________#
#BotLoop
#grabs all groupchats
groupChats = browser.find_elements_by_class_name("im_dialog_wrap")

while True:
    print('inside botLoop')
    try:
        if (READY):
            selectGroups()
            initializeDict()
            timeout = 30
            timeout_start = time.time()
            while time.time() < timeout_start + timeout:
                if(len(list(groupQueue)) == 0):
                    #timeout for x second(s)
                    time.sleep(3)
                    groupQueueBuilder()
                else:
                    groupFinder(groupQueue[0])
                    createMessageStack()
                    broadCast()
                    
            print('Finished BotLoop')
                
                
                    #get first in queue and cache / print all messages from it.
                    #For our purpose, batch work scheduler would be better. **prioritizes active groupchats**
    except:
        pass