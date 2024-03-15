# Aidan Kelly

# Imports
import wordListsMethods
import time

# Selenium Imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

# Set up driver
driver = webdriver.Chrome()

# Practice website: use this normally
driver.get("https://www.quordle.com/#/practice")

# Daily Quordle link: test the system against the daily quordle 
# Warning: this will crash after it finishes the daily because there is no button to go next.
#   This feature is just extra
# driver.get("https://www.merriam-webster.com/games/quordle/#/")


# Sets up selenium to receive actions
actions = ActionChains(driver)

# Create Variables
allWords = wordListsMethods.getAllWords()
indivWords = [wordListsMethods.getAllWords(), wordListsMethods.getAllWords(), wordListsMethods.getAllWords(), wordListsMethods.getAllWords()]

# Create variable to track the last word guessed 
guessWord = ""

# Tracking guesses to win and number of losses
winsList = []
numLosses = 0

# Create variable for which word guess iteration
iteration = -1

# Creates squares variable
squares = []

# The list that the last word was guessed from
lastWordGuessedFromList = -1

# Creates a list to determine if a letter was used, to be multiplied by a value
# 0 = used
# 1 = not used
lettersUsed = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]

# Average Letter likelihoods for the complete list, helps to create more variation in letter guesses
avgLikelihoods = wordListsMethods.totalLetterLikelihoods(wordListsMethods.getLetterLikelihoods(allWords))


# Creates a list of all the squares on the board in the given row so their colors can be looked
a = 0
for row in range(1, 10):
    tempSquares = [[], [], [], []]
    for i in range(1, 3):
        for j in range(1, 3):
            for k in range(1, 6):
                if i == 1 and j == 1:
                    a = 0
                elif i == 1 and j == 2:
                    a = 1
                elif i == 2 and j == 1:
                    a = 2
                else:
                    a = 3

                tempSquares[a].append(driver.find_element(By.XPATH, '//*[@id="game-board-row-' + str(i) + '"]/div[' + str(j) + ']/div[' + str(row) + ']/div[' + str(k) + ']'))
    squares.append(tempSquares)

# Set up knowledgeList
knowledgeList = [["", "", "", "", ""], ["", "", "", "", ""], ["", "", "", "", ""], ["", "", "", "", ""]]

# Set up resultsList
resultsList = [["", "", "", "", ""], ["", "", "", "", ""], ["", "", "", "", ""], ["", "", "", "", ""]]

# Changes the results list based on the colors of the 
def changeResultsList():
    for i in range(4):
        for j in range(5):
            if str(squares[iteration][i][j].value_of_css_property("background-color")) == "rgba(0, 204, 136, 1)":
                # Green
                resultsList[i][j] = "C"
                knowledgeList[i][j] = "D"
                
            elif str(squares[iteration][i][j].value_of_css_property("background-color")) == "rgba(255, 204, 0, 1)":
                # Yellow
                resultsList[i][j] = "M"
            elif str(squares[iteration][i][j].value_of_css_property("background-color")) == "rgba(228, 228, 231, 1)":
                # Gray
                resultsList[i][j] = "I"
    

# ListOfNumbers -> Number
# Given a list, finds the index of the highest number
def indexOfMax(numList):
    maxVal = 0
    maxIndex = 0

    for i in range(len(numList)):
        if numList[i] > maxVal:
            maxVal = numList[i]
            maxIndex = i

    return maxIndex            


# ListOfString (Single letter) -> String
# Given a list of letters needed to guess for, returns a filler word
def getFillerWord(lettersList):
    restWordsList = wordListsMethods.getRestWords()

    if len(lettersList) >= 4:
        for i in range(len(restWordsList)):
            if lettersList[0] in restWordsList[i] and lettersList[1] in restWordsList[i] and lettersList[2] in restWordsList[i] and lettersList[3] in restWordsList[i]:
                
                return restWordsList[i]
            
    if len(lettersList) == 3:
        for i in range(len(restWordsList)):
            if lettersList[0] in restWordsList[i] and lettersList[1] in restWordsList[i] and lettersList[2] in restWordsList[i]:
                
                return restWordsList[i]
            
    for i in range(len(restWordsList)):
            if lettersList[0] in restWordsList[i] and lettersList[1] in restWordsList[i]:
                
                return restWordsList[i]
    
    return "XXXXX" # Error check

# Number -> List of Strings
# Gets the missing letters for a filler word
def getMissingLetters(wordNum, ltr):
    missingIndex = ltr
    
    missingLetters = []
    for l in range(len(indivWords[wordNum])):
        missingLetters.append(indivWords[wordNum][l][missingIndex])
    
    return missingLetters

# List of Strings -> List of Numbers
# Gets the positions of the unknown letters in the list of words
def getUnknownLetterPositions(wordList):
    unknownLtrPosList = []
    for ltr in range(5):
        thisLetter = wordList[0][ltr]

        allLettersSame = True
        for wrd in range(1, len(wordList)):
            if not (wordList[wrd][ltr] == thisLetter):
                allLettersSame = False
        
        if not allLettersSame:
            unknownLtrPosList.append(ltr)
    
    return unknownLtrPosList


def minLenNot0():
    minLen = len(indivWords[0])
    # Make it the highest one so it's definitely not 0
    for i in range(1, 4):
        if len(indivWords[i]) > minLen:
            minLen = len(indivWords[i])

    
    for i in range(4):
        if len(indivWords[i]) != 0 and len(indivWords[i]) < minLen:
            
            minLen = len(indivWords[i])
    
    return minLen


# None -> String
# Finds the next best word to guess based 
def findBestWord():
    # Checks each list to see if there's only one possible word left
    for i in range(4):
        if len(indivWords[i]) == 1:
            resultsList[i] = ["C", "C", "C", "C", "C"]
            print("Found word: ", indivWords[i][0], " --- Iteration: ", iteration + 1)
            return indivWords[i][0]
        
    combinedWordsList = []

    wordsLeft = 0
    for i in range(4):
        if knowledgeList[i] == ["D", "D", "D", "D", "D"]:
            wordsLeft += 1

    # Checks for necessary and finds the correct filler word
    for i in range(4):
        if len(indivWords[i]) > 0:
            dCount = 0
            for j in range(5):
                if knowledgeList[i][j] == "D":
                    dCount += 1
            
            unknownLetterPosns = getUnknownLetterPositions(indivWords[i])
            # If has 4 right letters and more than 2 words left in list and not last guess
            # if dCount == 4 and len(indivWords[i]) > 2 and iteration != 7:
            if len(unknownLetterPosns) == 1 and len(indivWords[i]) > 2 and iteration != 7:
                
                missingLetters = getMissingLetters(i, unknownLetterPosns[0])
                # Adds the filler word to the words list
                combinedWordsList.append(getFillerWord(missingLetters))
            
            # elif dCount == 3 and "M" not in resultsList[i] and wordsLeft > 1:
            elif len(unknownLetterPosns) == 2 and "M" not in resultsList[i] and wordsLeft > 1:
                
                missingLetters = getMissingLetters(i, unknownLetterPosns[0])
                missingLetters.extend(getMissingLetters(i, unknownLetterPosns[1]))
                
                missingLetters = list(set(missingLetters))

                # Adds the filler word to the words list
                combinedWordsList.append(getFillerWord(missingLetters))

            else:
                # No filler word needed, add words to list list regular
                for j in range(len(indivWords[i])):
                    combinedWordsList.append(indivWords[i][j])

    # Gets the word values for the list based on letter likelihoods
    wordValueList = []
    likelihoods = wordListsMethods.getLetterLikelihoods(combinedWordsList)
    

    for i in range(5):
        for j in range(26):
            # Letters used adjustment
            likelihoods[i][j] += (avgLikelihoods[j] * lettersUsed[j])
    
    for i in range(len(combinedWordsList)):
        curWordValue = 0

        for j in range(5):
            curLetter = combinedWordsList[i][j]
            curLetterIndex = wordListsMethods.letters.index(curLetter)

            # Makes it so the program guesses less words with duplicate letters
            dupeFactor = 1
            if len(wordListsMethods.getDupsIndexList(j, combinedWordsList[i])) == 2:
                dupeFactor = 2/3
            elif len(wordListsMethods.getDupsIndexList(j, combinedWordsList[i])) == 3:
                dupeFactor = 0.5

            curWordValue += (likelihoods[j][curLetterIndex] * dupeFactor)

        
        # Stops it from guessing from the smallest list
        if iteration > 0:
            inListCounter = 0
            for a in range(4):
                if combinedWordsList[i] in indivWords[a]:
                    inListCounter += 1
        
            for b in range(4):
                if minLenNot0() == len(indivWords[b]) and inListCounter == 1 and combinedWordsList[i] in indivWords[b] and wordsLeft > 1:
                    curWordValue = 0

        # Appends the likelihoods value of the current word to the value list
        wordValueList.append(curWordValue)

    # Returns the highest word
    return combinedWordsList[indexOfMax(wordValueList)]


# String -> None
# Sets the number to 0 in the lettersUsed list if it is used in the word.
def setLettersAsUsed(wrd):
    for i in range(5):
        curLetter = wrd[i]
        curLetterIndex = wordListsMethods.letters.index(curLetter)

        lettersUsed[curLetterIndex] = 0


# Finds the next best word and types it in and submits it
def makeNextMove():
    global guessWord
    global lastWordGuessedFromList
    guessWord = findBestWord()

    setLettersAsUsed(guessWord)

    # Finds the list that the word was guessed from
    for i in range(4):
        for j in range(len(indivWords[i])):
            if guessWord == indivWords[i][j]:
                lastWordGuessedFromList = i

    # Sends word to browser
    actions.send_keys(guessWord).perform()
    actions.key_down(Keys.ENTER).perform()


# Removes words from allWords
def removeWords():
    global allWords
    global indivWords
    lastWord = guessWord

    # Individual words
    for word in range(4):
        # Removes the word that was just guessed
        if lastWord in indivWords[word]:
            indivWords[word].remove(lastWord)
            if indivWords[word] == []:
                continue
        
        # Empties a list if the correct word is guessed
        if resultsList[word] == ["C", "C", "C", "C", "C"]:
            indivWords[word] = []
            continue

        # Handles words with duplicate letters
        for letter in range(5):
            wordListCopy = []
            for a in range(len(indivWords[word])):
                wordListCopy.append(indivWords[word][a])

            if resultsList[word][letter] == "I":
                # Check for duplicate letters
                sameLetterIndexList = wordListsMethods.getDupsIndexList(letter, lastWord)
                
                # Act on duplicate letters
                if len(sameLetterIndexList) > 1:
                    sameLetterResultsList = []
                    for b in range(len(sameLetterIndexList)):
                        sameLetterResultsList.append(resultsList[word][sameLetterIndexList[b]])
                    
                    if "M" in sameLetterResultsList or "C" in sameLetterResultsList:
                        for j in range(len(wordListCopy)):
                            if wordListCopy[j][letter] == lastWord[letter]:
                                indivWords[word].remove(wordListCopy[j])

                else:
                    # No duplicates
                    for i in range(len(wordListCopy)):
                        if wordListsMethods.wordContains(wordListCopy[i], lastWord[letter]):
                            indivWords[word].remove(wordListCopy[i])

            elif resultsList[word][letter] == "M":
                for i in range(len(wordListCopy)):
                    if wordListCopy[i][letter] == lastWord[letter]:
                        indivWords[word].remove(wordListCopy[i])
                        continue

                    if not wordListsMethods.wordContains(wordListCopy[i], lastWord[letter]):
                        indivWords[word].remove(wordListCopy[i])
            else:
                for i in range(len(wordListCopy)):
                    if wordListCopy[i][letter] != lastWord[letter]:
                        indivWords[word].remove(wordListCopy[i])


# Runs a round of the quordle game
def playGame():
    global numLosses
    global indivWords
    global resultsList
    global knowledgeList
    global iteration

    # All variables reset
    indivWords = [wordListsMethods.getAllWords(), wordListsMethods.getAllWords(), wordListsMethods.getAllWords(), wordListsMethods.getAllWords()]
    resultsList = [["", "", "", "", ""], ["", "", "", "", ""], ["", "", "", "", ""], ["", "", "", "", ""]]
    knowledgeList = [["", "", "", "", ""], ["", "", "", "", ""], ["", "", "", "", ""], ["", "", "", "", ""]]
    iteration = -1

    for i in range(10):
        
        # Loss
        if i == 9:
            numLosses += 1
            break

        # Steps to run game
        makeNextMove()
        time.sleep(2.7)
        iteration += 1
        changeResultsList()
        removeWords()

        # Checks for win
        if resultsList == [["C", "C", "C", "C", "C"], ["C", "C", "C", "C", "C"], ["C", "C", "C", "C", "C"], ["C", "C", "C", "C", "C"]]:    
            winsList.append(i+1)
            break


# Makes it so the game can repeat forever
def repeatGame():
    while True:
        # Calls the new game function, reports win to console, and moves to the new game's webpage
        playGame()
        time.sleep(3)

        print("Wins:", len(winsList), "-", numLosses, " --- At iteration: ", iteration + 1)
        print()

        playAgainButton = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[1]/div[2]/div/div[1]/div[1]/div/div/span[2]/span/button")
        playAgainButton.click()

# Pause to let browser load
time.sleep(5)

# Starts game
repeatGame()
