#imports
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as ec
from collections import deque
from selenium.webdriver.common.keys import Keys
import time

#Chromedriver
browser = webdriver.Chrome()
browser.get('https://web.telegram.org/#/im')

#________________________________________________________________________#
#Lets the user select groups to track
def selectGroups(groupChats):
    index = 1
    for chat in groupChats:
        title= chat.find_elements_by_css_selector("div.im_dialog_peer")[0].text
        print(str(index) + '. ' + title)
        index+=1
    
    #once chats are printed, ask user for csv of indexes of groupchats they want to track
    listOfIndexOfChats = []
    while True:
        try:
            groupNumber = int(input("Please input the number of"+
                                    " the groupchat you want to track (any non-number to proceed): "))
            listOfIndexOfChats.append(groupNumber)
        except ValueError:
            break
            
    #now that we have the group indeces, use global variable to change indeces to chatNames
    userChats = []
    for index in listOfIndexOfChats:
        userChats.append(groupChats[index-1])
    print('You have selected the following groups: ')
    #return userChats
    return userChats
    
#________________________________________________________________________#
def selectHomeGroup(groupChats):
    index = int(input("Please input the number of the Home Group: "))
    homeGroup = groupChats[index-1].find_elements_by_css_selector("div.im_dialog_peer")[0].text
    print('Selected '+ homeGroup+' as homegroup.')
    return homeGroup

#________________________________________________________________________#
#Creates dictionairy of last messages in each group
def initializeDict(groupChats):
    lastMessageDict = {}
    for chat in groupChats:
        chat.click()
        selectedGroupTitle = chat.find_elements_by_css_selector("div.im_dialog_peer")[0].text
        while True:
            try:
                messages = browser.find_elements_by_class_name("im_message_text")
                textMessages = []
                #change array of WebElements to array of strings. easier to work with, avoid errors
                for webElement in messages:
                    textMessages.append(webElement.text)
                #for some reason there were empty strings being grabbed by selenium. removing them here    
                textMessages = list(filter(None, textMessages))
                key_gc = selectedGroupTitle
                lastMessageDict[key_gc] = textMessages[-1]
                print('Loaded ' + selectedGroupTitle + ': '+ lastMessageDict[key_gc])
                break
            except:
                print(selectedGroupTitle + 'did not load yet, retrying.')
    print(lastMessageDict)
    print('Recorded most recent messages in every group. New messages will be pushed to homegroup.')
    return lastMessageDict
#________________________________________________________________________#
#groupQueueBuilder
def groupQueueBuilder(trackedChats):
    for groupChat in trackedChats:
        oneBadgeArray = groupChat.find_elements_by_css_selector("span.im_dialog_badge.badge")
#         TO DO : make it not take messages from HOME GROUP
        if(oneBadgeArray[0].text!=""):
            #get index and use this index in titlesArray
            oneTitleArray = groupChat.find_elements_by_css_selector("div.im_dialog_peer")
            if(oneTitleArray[0].text not in groupQueue):
                groupQueue.append(oneTitleArray[0].text)
    print(groupQueue)
    return groupQueue
#________________________________________________________________________#
#groupFinder - Takes in name of group finds it selects it, returns title of slected chat
def groupFinder(name, trackedChats):
    print('Finding '+ name)
    for chat in trackedChats:
        titleArray = chat.find_elements_by_css_selector("div.im_dialog_peer")
        if(titleArray[0].text == name):
            chat.click()
            print('Clicked on ' + name)
            return(titleArray[0].text)
    print('groupFinder Could not find group: '+ name)
    return 'noGroupError'
    
#________________________________________________________________________#
#Create push method to click on 'home chat' and paste and send it there.
# checks via dictionary which messages to push
def createMessageStack(selectedGroupTitle, lastMessageDict):
    messageStack = []
    messages = browser.find_elements_by_class_name("im_message_text")
    textMessages = []
    print('Loading '+str(len(messages))+' new messages')
    #change array of WebElements to array of strings. easier to work with, avoid errors
    for webElement in messages:
        if(webElement.text !=''):
            print(webElement.text)
        textMessages.append(webElement.text)
    #for some reason there were empty strings being grabbed by selenium. removing them here    
    textMessages = list(filter(None, textMessages))
    #reversing list to make FIFO
    textMessages.reverse()
    for message in textMessages:
        if(message != lastMessageDict[selectedGroupTitle]):
            messageStack.append(message)
        else:
#             SHOULD RUN WHEN MESSAGES ARE PUSHED
            break
    print('Messages Loaded')
    print(messageStack)
    return messageStack
 #________________________________________________________________________#
# Broadcast Method
def broadCast(messageStack, selectedGroupTitle, groupChats, homeGroup):
    #select home chat
    print('Sending...')
    messageStack.reverse()
    print(messageStack)
    for chat in groupChats:
        titleArray = chat.find_elements_by_css_selector("div.im_dialog_peer")
        if(titleArray[0].text == homeGroup):
            chat.click()
            break
    
    #once homechat is selected, send messages one by one.
    textBox = browser.find_elements_by_class_name('composer_rich_textarea')[0]
    for message in messageStack:        
        textBox.send_keys(selectedGroupTitle + ": " + message)
        textBox.send_keys(Keys.RETURN)
    if(len(messageStack) != 0):
        lastMessageDict[selectedGroupTitle] = messageStack[-1]
    #clean up after sending messages.
    messageStack.clear()
    print('Messages sent!')
    print(messageStack)
    return 0
#________________________________________________________________________#
def fillGroupQueue(trackedChats):
    groupQueue = deque([])
    for webElement in trackedChats:
        titleArray = webElement.find_elements_by_css_selector("div.im_dialog_peer")
        groupQueue.append(titleArray[0].text)
    print('Time to check every group for missed messages')
    print(groupQueue)
    return groupQueue
        
#________________________________________________________________________#
#User prompt to run BotLoop
global READY
READY = False

while True:
    print('______________________________________________________________')
    print('READ DIRECTIONS CAREFULLY.')
    try:
        userPrompt = input("Please type 'ready' after signing in to continue. ")            
        
    except ValueError:
        print("You gotta type in 'ready' exactly like that, bud...")
        continue

    else:
        if(userPrompt == 'ready'):
            READY = True
            break
        else:
            continue

#________________________________________________________________________#
#BotLoop
#grabs all groupchats

# while True:
#     print('inside botLoop')
# try:
if (READY):
    #Create Runtime Variables inside here.
    groupChats = browser.find_elements_by_class_name("im_dialog_wrap") 
    groupQueue = deque([])
    trackedChats = selectGroups(groupChats)
    homeGroup = selectHomeGroup(groupChats)
    lastMessageDict = initializeDict(trackedChats)
    timeout = 120
    timeout_start = time.time()
    cleanupTimeout = time.time()
    # month timeout:
    # while time.time() < 1517278786 + 259200:
    while time.time() < timeout_start + timeout:
        if(len(list(groupQueue)) == 0):
            time.sleep(1)
            if(time.time() > cleanupTimeout + 10):
                groupQueue = fillGroupQueue(trackedChats)
                cleanupTimeout = time.time()
            else:
                groupQueue = groupQueueBuilder(trackedChats)
                if(len(list(groupQueue)) != 0):
                    cleanupTimeout = time.time()
                
        else:
            selectedGroupTitle = groupFinder(groupQueue.popleft(), trackedChats)
            messageStack = createMessageStack(selectedGroupTitle, lastMessageDict)
            broadCast(messageStack, selectedGroupTitle, groupChats,homeGroup)
            cleanupTimeout = time.time()

    print('Finished BotLoop')
    
    
        
        
            #get first in queue and cache / print all messages from it.
            #For our purpose, batch work scheduler would be better. **prioritizes active groupchats**
    # except:
        # pass