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
            groupNumber = int(input("Please input the number of the groupchat you want to track (any non-number to proceed): "))
            listOfIndexOfChats.append(groupNumber)
        except ValueError:
            break
    
    #now that we have the group indeces, use global variable to change indeces to chatNames
    userChats = []
    for index in listOfIndexOfChats:
        userChats.append(groupChats[index-1])

    #return userChats
    return userChats
    
    print('selectGroups ran successfully')

#________________________________________________________________________#
#Creates dictionairy of last messages in each group
def initializeDict(groupChats):
    lastMessageDict = {}
    for chat in groupChats:
        chat.click()
#         time.sleep(2)
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
                print('finished initializing: ' + selectedGroupTitle)
                break
            except:
                print(selectedGroupTitle + 'did not load yet, trying again.')
    print(lastMessageDict)
    print('initializeDict ran successfully')
#________________________________________________________________________#
#groupQueueBuilder
def groupQueueBuilder(groupChats):
    for groupChat in groupChats:
        oneBadgeArray = groupChat.find_elements_by_css_selector("span.im_dialog_badge.badge")
#         TO DO : make it not take messages from HOME GROUP
        if(oneBadgeArray[0].text!=""):
            #get index and use this index in titlesArray
            oneTitleArray = groupChat.find_elements_by_css_selector("div.im_dialog_peer")
            if(oneTitleArray[0].text not in groupQueue):
                groupQueue.append(oneTitleArray[0].text)
    return groupQueue
    print('groupQueueBuilder ran successfully')
#________________________________________________________________________#
#groupFinder - Takes in name of group finds it selects it, returns title of slected chat
def groupFinder(name):
    for chat in groupChats:
        titleArray = chat.find_elements_by_css_selector("div.im_dialog_peer")
        if(titleArray[0].text == name):
            chat.click()
            print('groupFinder ran successfully')
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
    #change array of WebElements to array of strings. easier to work with, avoid errors
    for webElement in messages:
        textMessages.append(webElement.text)
    #for some reason there were empty strings being grabbed by selenium. removing them here    
    textMessages = list(filter(None, textMessages))
    #reversing list to make FIFO
    textMessages.reverse()
    print(lastMessageDict[selectedGroupTitle])
    for message in textMessages:
        
        if(message != lastMessageDict[selectedGroupTitle]):
            messageStack.append(message)
        else:
#             SHOULD RUN WHEN MESSAGES ARE PUSHED
            break
    return messageStack
    print('createMessageStack ran successfully')
#________________________________________________________________________#
# Broadcast Method
def broadCast(messageStack, selectedGroupTitle, groupChats):
    #select home chat
    print('Will now be sending:')
    print(messageStack)
    messageStack.reverse()
    for chat in groupChats:
        titleArray = chat.find_elements_by_css_selector("div.im_dialog_peer")
        if(titleArray[0].text == 'PAID GROUP'):
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
    print('broadcast ran successfully')
#________________________________________________________________________#
#User prompt to run BotLoop
global READY
READY = False

while True:
    print('inside user prompt')
    try:
        userPrompt = input("Please type 'ready' after signing in. Telecast will then run.")            
        
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
    #_____________________________________
    trackedChats = selectGroups(groupChats)
    lastMessageDict = initializeDict(trackedChats)
    timeout = 90
    timeout_start = time.time()
    while time.time() < timeout_start + timeout:
        if(len(list(groupQueue)) == 0):
            time.sleep(3)
            groupQueue = groupQueueBuilder(trackedChats)
        else:
            selectedGroupTitle = groupFinder(groupQueue.popleft())
            messageStack = createMessageStack(selectedGroupTitle, lastMessageDict)
            broadCast(messageStack, selectedGroupTitle, userChats)
            
    print('Finished BotLoop')
        
        
            #get first in queue and cache / print all messages from it.
            #For our purpose, batch work scheduler would be better. **prioritizes active groupchats**
    # except:
        # pass