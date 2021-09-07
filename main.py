import pygame
import random

# Music credits to bensound
# Sound effects taken from freesound.org

pygame.init()

# Sets up screen and window
screenSize = (500, 750)
screenX, screenY = screenSize[0], screenSize[1]
window = pygame.display.set_mode(screenSize)
pygame.display.set_caption("Mushroom Snake!")

# Sets up clock and active state
clock = pygame.time.Clock()
active = True

# Sets colors
grass = (2, 138, 15)
wood = pygame.Color("#c8b88a")
dark = (19, 22, 18)
fillColor = pygame.Color("#96cc39")
gold = (255, 215, 0)

# Sets fonts
# Intro animation font
introFont = pygame.font.SysFont("georgiabold", 40)
# Game title font
tFont = pygame.font.SysFont("comicsansms", 60)
# Menu button font (also used in journal and death screen)
bFont = pygame.font.SysFont("comicsansms", 30)
# For buttons in journal
jFont = pygame.font.SysFont("comicsansms", 25)
# For image question marks in journal entry
# For question marks on journal tabs and journal text
qFont = pygame.font.SysFont("comicsansms", 20)

# Sets display options
edgeCount = 15
edgeLength = 25
tLength = edgeLength * edgeCount

# Imports images
mIndex = ["normal", "anger", "antidote", "blind", "confusion", "fear", "growth", "holy", "luck", "resist", "tired"]
mImages = []
mAlmanac = []
for index in mIndex:
    img = pygame.image.load("img/" + index + ".png")
    mImages.append(pygame.transform.scale(img, (edgeLength, edgeLength)))
    img2 = pygame.image.load("imgB/" + index + ".png")
    mAlmanac.append(pygame.transform.scale(img2, (150, 150)))
yStar = pygame.image.load("img/star.png")

# Sets major game parameters
# Counts total  eaten of each mushroom type
mushroomCount = [0] * 11
# Counts highest effects of each mushroom type
mushroomUnique = [0] * 11
# Tracks achievements
achList = [False]*11
# Ach 6 tracks max score, 7 tracks deaths, 9 tracks distance traveled
achProgress = [0] * 11
# Need to reach targets to complete achievement
achTarget = [1, 1, 1, 1, 8, 33, 30, 10, 100, 1000, 10]
gameSongs = ["songs/cute.mp3", "songs/funnysong.mp3", "songs/ukulele.mp3"]
winSound = pygame.mixer.Sound("../sneko2/sounds/win.wav")
# Tracks pop-ups, pops[4] is for managing victory music
pops = [True] * 5
# Becomes true after finishing game
mushroomOverlord = False



# Draws intro sequence
def drawIntro():
    window.fill((0, 0, 0))
    clock.tick(30)
    pygame.display.update()

    # Fades in, then fades out intro text
    for idx in range(300):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        if idx <= 100:
            frameNum = min(3 * idx, 255)
        else:
            frameNum = min(900 - 3 * idx, 255)
        # Prints author text
        introText1 = introFont.render("A Game By", False, (frameNum, frameNum, frameNum))
        introText2 = introFont.render("Jonny Wu", False, (frameNum, frameNum, frameNum))
        window.blit(introText1, (screenX / 2 - introText1.get_width() / 2, screenY * 0.3))
        window.blit(introText2, (screenX / 2 - introText2.get_width() / 2, screenY * 0.4))
        pygame.display.update()

    # Waits one second on dark screen
    window.fill((0, 0, 0))
    pygame.time.delay(1000)



# Centers text given rect
def centerText(text, rect):
    xPos = rect.x + rect.width // 2 - text.get_width() // 2
    yPos = rect.y + rect.height // 2 - text.get_height() // 2
    window.blit(text, (xPos, yPos))
    return

# Draws generic button given position, size, color
def drawButton(x, y, width, height, color):
    pygame.draw.rect(window, dark, (x - 5, y - 5, width + 10, height + 10))
    button = pygame.draw.rect(window, color, (x, y, width, height))
    return button

# Draws generic button in journal/achievements given position, size, color, index
def drawButtonTab(x, y, width, height, color, index, ach):
    pygame.draw.rect(window, dark, (x - 5, y - 5, width + 10, height + 10))
    journalTab = pygame.draw.rect(window, color, (x, y, width, height))
    # Draws tabs for achievement page
    if ach:
        if achList[index]:
            aImg = pygame.transform.scale(yStar, (int(width - 10), int(width - 10)))
            window.blit(aImg, (x + 5, y + 5))
        else:
            qText = qFont.render("?", True, dark)
            centerText(qText, journalTab)
    # Draws tabs for journal page
    else:
        if mushroomUnique[index] > 0:
            mImg = pygame.transform.scale(mImages[index], (int(width - 10), int(width - 10)))
            window.blit(mImg, (x + 5, y + 5))
        else:
            qText = qFont.render("?", True, dark)
            centerText(qText, journalTab)
    return journalTab



# Draws start button on menu
def drawStartButton(color):
    startButton = drawButton(screenX / 4, screenY * 0.58, screenX / 2, screenY * 0.1, color)
    centerText(bFont.render("Start Run", True, dark), startButton)
    return startButton

# Draws journal button on menu
def drawJournalButton(color):
    journalButton = drawButton(screenX / 4, screenY * 0.72, screenX / 2, screenY * 0.1, color)
    centerText(bFont.render("Journal", True, dark), journalButton)
    return journalButton

# Draws achievement button on menu
def drawAchButton(color):
    achButton = drawButton(screenX / 4, screenY * 0.86, screenX / 2, screenY * 0.1, color)
    centerText(bFont.render("Achievements", True, dark), achButton)
    return achButton

# Draws ok button during popups
def drawOk(color):
    nextButton = drawButton(screenX * 0.4, screenY * 0.75, screenX * 0.2, screenY * 0.1, color)
    buttonText = bFont.render("OK", True, dark)
    centerText(buttonText, nextButton)
    return nextButton

# Draws title on menu
def drawTitle(text1, text2):
    top = tFont.render(text1, True, grass)
    window.blit(top, (screenSize[0] // 2 - top.get_width() // 2, 10))
    if text2:
        bottom = tFont.render(text2, True, grass)
        window.blit(bottom, (screenSize[0] // 2 - bottom.get_width() // 2, 65))
    pygame.display.update()

# Draws menu, including title, buttons, snake image
def drawMenu():
    window.fill(fillColor)
    # Draws title snake image
    drawTitle("Mushroom", "Snake")
    snakeImage = pygame.image.load("img/snake.png")
    snakeImageSmall = pygame.transform.scale(snakeImage, (int(screenX * 0.3), int(screenX * 0.3)))
    window.blit(snakeImageSmall, (screenX * 0.55, screenY * 0.25))

    # Draws mushroom image
    mushImage = pygame.image.load("img/normal.png")
    mushImageSmall = pygame.transform.scale(mushImage, (int(screenX * 0.3), int(screenX * 0.3)))
    window.blit(mushImageSmall, (screenX * 0.15, screenY * 0.25))
    return drawStartButton(wood), drawJournalButton(wood), drawAchButton(wood)

# Draws text above game grid (for showing score/high score)
def drawFlavorBar(text):
    flavorBar = drawButton(screenX * 0.25, screenY * 0.20 - 5, screenX * 0.65, screenY * 0.05, wood)
    flavorText = jFont.render(text, True, dark)
    centerText(flavorText, flavorBar)

# Draws back button in journal/achievement screen
def drawBackButton():
    backButton = drawButton(screenX * 0.1, screenY * 0.20 - 5, screenX * 0.15, screenY * 0.05, wood)
    backText = jFont.render("Back", True, dark)
    centerText(backText, backButton)
    return backButton

# Draws prev/mext buttons in journal/achievement screen
def drawScrollButtons(page):
    # Draws Prev button
    if page != 0:
        prevButton = drawButton(screenX * 0.19 + 5, 700, screenX * 0.15, 32.5, wood)
        prevText = jFont.render("Prev", True, dark)
        centerText(prevText, prevButton)
    else:
        prevButton = pygame.draw.rect(window, wood, (screenX * 0.19 + 5, 700 - 5, screenX * 0.15 + 5, 32.5 + 5))

    #Draws next button
    if page != 10:
        nextButton = drawButton(375, 700, screenX * 0.15, 32.5, wood)
        nextText = jFont.render("Next", True, dark)
        centerText(nextText, nextButton)
    else:
        nextButton = pygame.draw.rect(window, wood, (375 - 5, 700 - 5, screenX * 0.15 + 5, 32.5 + 5))

    return prevButton, nextButton



# Mushroom titles and journal entries
mTitle = ["Basic", "Angry", "Antidote", "Blindness", "Confusion", "Fear", "Growth", "Holy", "Luck", "Resistance",
          "Tiredness"]
mEntries = [["No effect", "No effect", "No effect"],
            ["Speed is faster", "Speed is really fast", "Continuous speed increase"],
            ["Heals 1 negative effect", "Heals 2 negative effects", "Chance new negative effects ignored"],
            ["Can't see mushroom type", "Can't see mushroom locations", "Can't see snake body"],
            ["Keys have reversed directions", "Keys might switch back", "Keys have random directions"],
            ["Small chance to randomly turn", "Large chance to randomly turn", "Teleports upon eating mushroom"],
            ["More growth from mushroom", "Massive growth from mushroom", "Continuous growth"],
            ["No effect", "No effect", "Resets ALL effects"],
            ["Spawns more mushrooms", "Spawns a lot more mushrooms", "Increases spawn of holy mushrooms"],
            ["Turns are delayed", "Chance turns are ignored", "Can't turn"],
            ["Eat mushrooms to stay awake", "Fall asleep faster", "Mushrooms don't prevent sleep"]]

# Draws journal entry
pageCenter = screenX / 2 + 25

# Draws journal page
def drawJournalPage(page):
    # Draws page background
    drawButton(screenX * 0.2, screenY * 0.25, screenX * 0.7, 545, wood)

    # Setsmushroom name and drawing image
    if mushroomUnique[page] > 0:
        nameAdd = mTitle[page]
        window.blit(mAlmanac[page],
                    (pageCenter - mAlmanac[page].get_width() / 2, screenSize[1] / 2 - tLength / 2 + 20))
    else:
        nameAdd = "???"
        qText = tFont.render("???", True, dark)
        window.blit(qText, (pageCenter - qText.get_width() / 2, screenY / 4 + 50))

    # Draws mushroom name
    nameText = bFont.render("Name: " + nameAdd, True, dark)
    window.blit(nameText,
                (pageCenter - nameText.get_width() / 2, screenY / 2 - tLength / 2 + 180))

    # Draws mushroom effects
    for idx in range(3):
        if mushroomUnique[page] <= idx:
            effect = "???"
        else:
            effect = mEntries[page][idx]
        qText1 = qFont.render("Effect #" + str(idx + 1) + ":", True, dark)
        qText2 = qFont.render(effect, True, dark)
        window.blit(qText1,
                    (pageCenter - qText1.get_width() / 2,
                     screenSize[1] / 2 - tLength / 2 + 240 + 70 * idx))
        window.blit(qText2,
                    (pageCenter - qText2.get_width() // 2,
                     screenSize[1] / 2 - tLength / 2 + 265 + 70 * idx))

    # Draws total mushrooms found
    totalText = bFont.render("Total Found: " + str(mushroomCount[page]), True, dark)
    window.blit(totalText,
                (pageCenter - totalText.get_width() / 2,
                 screenY / 2 - tLength / 2 + 460))



# Achievement Entries
achEntries = [["The Very Hungry Snake", "Eat no mushrooms on a run"],
              ["Ouroboros", "Eat a snake tail on a run"],
              ["Zzzznake", "Fall asleep on a run"],
              ["Blessing of the Snake", "Cleanse all effects on a run"],
              ["Survivor", "Eat 8 unique mushroom types", "on a run"],
              ["Mushroom Expert", "Complete the journal"],
              ["Cold Blooded", "Reach a max score of 30"],
              ["Dragon Heritage", "Die 10 times"],
              ["The Very Full Snake", "Eat 100 mushrooms in total"],
              ["Marathon Slide", "Travel 1000 blocks in total"],
              ["Mushroom Overlord", "Complete 10 achievements"]]


# Draws achievement page
def drawAchPage(page):
    # Draws page background
    drawButton(screenX * 0.2, screenY * 0.25, screenX * 0.7, 545, wood)

    # Sets mushroom name and drawing image
    if achList[page]:
        window.blit(pygame.transform.scale(yStar, (150, 150)),
                    (pageCenter - mAlmanac[page].get_width() / 2, screenSize[1] / 2 - tLength / 2 + 20))
    else:
        qText = tFont.render("???", True, dark)
        window.blit(qText, (pageCenter - qText.get_width() / 2, screenY / 4 + 50))

    # Draws achievement name and description
    nameText = bFont.render(achEntries[page][0], True, dark)
    window.blit(nameText,
                (pageCenter - nameText.get_width() / 2, screenY / 2 - tLength / 2 + 180))
    descText = jFont.render(achEntries[page][1], True, dark)
    window.blit(descText,
                (pageCenter - descText.get_width() / 2, screenY / 2 - tLength / 2 + 260))
    #Special case for achievement index 4, which takes two lines for the description
    if page == 4:
        descText = jFont.render(achEntries[page][2], True, dark)
        window.blit(descText,
                    (pageCenter - descText.get_width() / 2, screenY / 2 - tLength / 2 + 285))

    # Draws mushroom effects
    if achList[page]:
        progressText = "Completed"
    else:
        progressText = "Progress: " + str(achProgress[page]) + "/" + str(achTarget[page])
    pText = jFont.render(progressText, True, dark)
    window.blit(pText,
                (pageCenter - pText.get_width() / 2,
                 screenY / 2 - tLength // 2 + 320))



# Runs journal and achievement pages
def runJournalAch(page, isAch):
    # Initialize journal
    journalActive = True
    clock.tick(30)

    # Draws journal layout
    window.fill(fillColor)

    # Achievement page logic
    if isAch:
        # Updates achievement progress
        for idx in range(11):
            if idx==10:
                achProgress[10] = sum(achList)
            if achProgress[idx] >= achTarget[idx]:
                achList[idx] = True

        # Displays achievement progress in flavor bar
        drawTitle("Achievements", "")
        drawFlavorBar("Achievements: " + str(sum(achList)) + str("/11"))
    # Journal page logic
    else:
        drawTitle("Journal", "")
        uniqueEffects = 0
        for i in range(len(mushroomUnique)):
            if mushroomUnique[i] > 0:
                uniqueEffects += min(3, mushroomUnique[i])
        drawFlavorBar("Effects Found: " + str(uniqueEffects) + str("/33"))


    # Draws wood background, back button, and tab buttons
    drawButton(screenX * 0.1, screenY * 0.25, screenX * 0.8, 545, wood)
    backButton = drawBackButton()
    buttonList = []
    for idx in range(11):
        if idx != page:
            tabButton = drawButtonTab(screenX * 0.1, screenY * 0.25 + idx * 0.1 * screenX, screenX * 0.09,
                                      screenX * 0.09, wood, idx, isAch)
        else:
            tabButton = drawButtonTab(screenX * 0.1, screenY * 0.25 + idx * 0.1 * screenX, screenX * 0.09,
                                      screenX * 0.09, gold, idx, isAch)
        buttonList.append(tabButton)

    # Draws journal and achievement page
    if isAch:
        drawAchPage(page)
    else:
        drawJournalPage(page)
    prevButton, nextButton = drawScrollButtons(page)
    pygame.display.update()

    # Watches for page changes, return to main menu, quit
    while journalActive:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

            # Logic when mouse clicked
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                click = False

                # Mouse clicked on tabs
                for idx in range(11):
                    if buttonList[idx].collidepoint(pos):
                        drawButtonTab(screenX * 0.1, screenY * 0.25 + page * 0.1 * screenX, screenX * 0.09,
                                      screenX * 0.09, wood, page, isAch)
                        page = idx
                        drawButtonTab(screenX * 0.1, screenY * 0.25 + idx * 0.1 * screenX, screenX * 0.09,
                                      screenX * 0.09, gold, idx, isAch)
                        click = True

                # Back button clicked
                if backButton.collidepoint(pos):
                    journalActive = False

                # Prev button clicked
                if prevButton.collidepoint(pos) and page != 0:
                    drawButtonTab(screenX * 0.1, screenY * 0.25 + page * 0.1 * screenX, screenX * 0.09,
                                  screenX * 0.09, wood, page, isAch)
                    page -= 1
                    drawButtonTab(screenX * 0.1, screenY * 0.25 + page * 0.1 * screenX, screenX * 0.09,
                                  screenX * 0.09, gold, page, isAch)
                    click = True

                # Next button clicked
                if nextButton.collidepoint(pos) and page != 10:
                    drawButtonTab(screenX * 0.1, screenY * 0.25 + page * 0.1 * screenX, screenX * 0.09,
                                  screenX * 0.09, wood, page, isAch)
                    page += 1
                    drawButtonTab(screenX * 0.1, screenY * 0.25 + page * 0.1 * screenX, screenX * 0.09,
                                  screenX * 0.09, gold, page, isAch)
                    click = True

                # Updates screen on click
                if click:
                    if isAch:
                        drawAchPage(page)
                    else:
                        drawJournalPage(page)
                    prevButton, nextButton = drawScrollButtons(page)
            pygame.display.update()



# Initializes screen
introDrawn = False
window.fill((0, 0, 0))
pygame.display.update()

# Arrow key parameters
aKLength = 50
aKBuffer = 25
aBuffer = 10

# Draws up button
def drawUp(color):
    upButton = pygame.draw.rect(window, wood, (
        screenSize[0] // 2 - tLength // 2 + aKLength, screenSize[1] // 2 + tLength // 2 + aKBuffer, aKLength, aKLength))
    pygame.draw.polygon(window, color, [(upButton.x + aBuffer, upButton.y + aKLength - aBuffer),
                                        (upButton.x + aKLength - aBuffer, upButton.y + aKLength - aBuffer),
                                        (upButton.x + aKLength // 2, upButton.y + aBuffer)])
    return upButton

# Draws left button
def drawLeft(color):
    leftButton = pygame.draw.rect(window, wood, (
        screenSize[0] // 2 - tLength // 2, screenSize[1] // 2 + tLength // 2 + aKBuffer + aKLength, aKLength, aKLength))
    pygame.draw.polygon(window, color, [(leftButton.x + aKLength - aBuffer, leftButton.y + aBuffer),
                                        (leftButton.x + aKLength - aBuffer, leftButton.y + aKLength - aBuffer),
                                        (leftButton.x + aBuffer, leftButton.y + aKLength // 2)])
    return leftButton

# Draws right button
def drawRight(color):
    rightButton = pygame.draw.rect(window, wood, (
        screenSize[0] // 2 - tLength // 2 + 2 * aKLength, screenSize[1] // 2 + tLength // 2 + aKBuffer + aKLength,
        aKLength,
        aKLength))
    pygame.draw.polygon(window, color, [(rightButton.x + aBuffer, rightButton.y + aBuffer),
                                        (rightButton.x + aBuffer, rightButton.y + aKLength - aBuffer),
                                        (rightButton.x + aKLength - aBuffer, rightButton.y + aKLength // 2)])
    return rightButton

# Draws down button
def drawDown(color):
    downButton = pygame.draw.rect(window, wood, (
        screenSize[0] // 2 - tLength // 2 + aKLength, screenSize[1] // 2 + tLength // 2 + aKBuffer + 2 * aKLength,
        aKLength,
        aKLength))
    pygame.draw.polygon(window, color, [(downButton.x + aBuffer, downButton.y + aBuffer),
                                        (downButton.x + aKLength - aBuffer, downButton.y + aBuffer),
                                        (downButton.x + aKLength // 2, downButton.y + aKLength - aBuffer)])
    return downButton

# Draws story text
def drawStory(text, lineNum):
    storyText = jFont.render(text, True, dark)
    window.blit(storyText, (
        screenSize[0] // 2 - storyText.get_rect().width // 2, screenSize[1] // 2 - tLength // 2 + 20 * lineNum))



# Adjectives and reasons for minor death causes
adjectiveList = [["Minor", "Slight", "Trivial"], ["Severe", "Serious", "Acute"],
                 ["Devastating", "Crippling", "Overwhelming"]]
reasonsDict = ["Normalness", "Anger", "Antidotes", "Blindness", "Confusion", "Fear", "Growth", "Holiness", "Luck",
               "Resistance", "Tiredness"]

# Draws and runs death screen
def drawDeathScreen(score, effects, deathCause):
    # Draws background and title
    deathActive = True
    window.fill(fillColor)
    drawTitle("Run #" + str(achProgress[7] + 1) + " Recap", "")
    backButton = drawBackButton()
    drawFlavorBar("Score: " + str(score) + "   High Score: " + str(achProgress[6]))
    drawButton(screenX * 0.1, screenY * 0.25, screenX * 0.8, 545, wood)

    # Main death text
    deathText = bFont.render("Main Cause of Death: ", True, dark)
    window.blit(deathText, (
        screenX / 2 - deathText.get_rect().width / 2, screenY / 2 - tLength / 2 + 10))
    drawStory(deathCause, 2.6)

    # Check sleep and ouroboros achievement
    if deathCause in ["Nap Time", "Fell Asleep at the Wheel", "Dreams about Normal Mushrooms"]:
        achList[2] = True
    elif deathCause == "Recreated Ouroboros Legend":
        achList[1] = True

    # Secondary death text
    deathText2 = bFont.render("Minor Causes of Death: ", True, dark)
    window.blit(deathText2, (
        screenSize[0] // 2 - deathText2.get_rect().width // 2, screenSize[1] // 2 - tLength // 2 + 100))

    # Secondary death reasons
    reasons = []
    for i in range(10, -1, -1):
        if effects[i] > 0:
            reasons.append(adjectiveList[min(2, effects[i] - 1)][random.randint(0, 2)] + " " + reasonsDict[~i])
    lineNum = 7
    if not reasons:
        reasons = ["Incompetence"]
    for reas in reasons:
        drawStory(reas, lineNum)
        lineNum += 1.5
    pygame.display.update()

    # Runs death screen page
    while deathActive:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if backButton.collidepoint(pos):
                    deathActive = False



# Draws all arrow keys
def drawAllKeys(color):
    upButton = drawUp(color)
    leftButton = drawLeft(color)
    rightButton = drawRight(color)
    downButton = drawDown(color)
    return upButton, downButton, leftButton, rightButton

# Draws flavor text
def drawFlavor(text):
    pygame.draw.rect(window, fillColor, (0, 130, screenX, 50))
    bFlavor = bFont.render(text, True, grass)
    window.blit(bFlavor, (
        screenX / 2 - bFlavor.get_rect().width // 2, 130))

# Draws pop-up
def drawPop(title, book):
    # Darkens current screen
    darken = pygame.Surface((screenX, screenY))
    darken.set_alpha(128)
    darken.fill((0, 0, 0))
    window.blit(darken, (0, 0))

    # Draws ok button and pop-up window
    drawButton(screenX * 0.08, screenY * 0.1, screenX * 0.84, screenY * 0.8, wood)
    nextButton = drawOk(wood)

    # Draws pop-up title
    titleText = tFont.render(title, True, dark)
    window.blit(titleText, (screenX / 2 - titleText.get_width() / 2, screenY * 0.15))

    # Draws lines in pop-up
    for line in book:
        text = bFont.render(line[0], True, dark)
        window.blit(text, (screenX / 2 - text.get_width() / 2, screenY * 0.2 + 50 * line[1]))
    pygame.display.update()

    # Runs pop-up window
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

            # Mouse clicked
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if nextButton.collidepoint(pos):
                    drawOk(grass)
                    pygame.display.update()

            # Mouse release
            if event.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()
                if nextButton.collidepoint(pos):
                    return
                drawOk(wood)
                pygame.display.update()


# Runs snake game
def startGame(luckyNums):
    # Each tile on grid
    class square(object):
        def __init__(self, x, y, size, gColor):
            self.x = x
            self.y = y
            self.groundColor = gColor
            self.length = size

        # Draws tile in grid
        def drawSquare(self, visited, blindLevel, dir, isHead):
            pygame.draw.rect(window, self.groundColor, (self.x, self.y, self.length, self.length))
            # Checks for mushroom or snake body to draw
            if visited > 0:
                # Blind 3 means no snake body drawn
                if blindLevel < 3:
                    pygame.draw.circle(window, (0, 255, 0),
                                       (self.x + self.length / 2, self.y + self.length // 2),
                                       self.length / 2, 0)
                    # Draws eyes if square has snake head
                    if isHead:
                        if dir == "LEFT":
                            eyeX1, eyeY1, eyeX2, eyeY2 = 0.25, 0.25, 0.25, 0.75
                        elif dir == "RIGHT":
                            eyeX1, eyeY1, eyeX2, eyeY2 = 0.75, 0.25, 0.75, 0.75
                        elif dir == "UP":
                            eyeX1, eyeY1, eyeX2, eyeY2 = 0.25, 0.25, 0.75, 0.25
                        else:
                            eyeX1, eyeY1, eyeX2, eyeY2 = 0.25, 0.75, 0.75, 0.75
                        pygame.draw.circle(window, dark, (self.x + self.length * eyeX1, self.y + self.length * eyeY1),
                                           self.length / 8, 0)
                        pygame.draw.circle(window, dark, (self.x + self.length * eyeX2, self.y + self.length * eyeY2),
                                           self.length / 8, 0)
            # Mushrooms are represented by negative numbers [-11,-1]
            elif visited < 0:
                # Draws mushroom type, draws basic mushroom for blind 1
                if blindLevel == 0:
                    window.blit(mImages[~visited], (self.x, self.y))
                elif blindLevel == 1:
                    window.blit(mImages[0], (self.x, self.y))

    # Collection of tiles
    class grid(object):
        def __init__(self, edgeCount, edgeLength):
            self.x = screenX // 2 - (edgeCount * edgeLength) // 2
            self.y = screenY // 2 - (edgeCount * edgeLength) // 2
            self.matrix = [[0] * edgeCount for _ in range(edgeCount)]
            self.edgeCount = edgeCount
            self.mushroomCount = [0] * 11
            self.mushroomSound = pygame.mixer.Sound('sounds/ding.wav')
            self.crashSound = pygame.mixer.Sound('sounds/crash.wav')

            # Set up tiles in game grid
            for i in range(edgeCount):
                for j in range(edgeCount):
                    self.matrix[i][j] = square(self.x + j * edgeLength, self.y + i * edgeLength, edgeLength,
                                               grass)
            # Visited matrix to track where snake has been
            self.visited = [[0] * edgeCount for _ in range(edgeCount)]

        # Draws game grid
        def drawGrid(self, blindLevel, dir, head):
            for row in range(self.edgeCount):
                for col in range(self.edgeCount):
                    if row == head[0] and col == head[1]:
                        self.matrix[row][col].drawSquare(self.visited[row][col], blindLevel, dir, True)
                    else:
                        self.matrix[row][col].drawSquare(self.visited[row][col], blindLevel, dir, False)
            pygame.display.update()

        # Checks if snake is traveling to valid square, selects death reason if invalid square
        def checkValid(self, row, col):
            if row < 0 or col < 0 or row >= self.edgeCount or col >= self.edgeCount:
                snek.death = random.choice(
                    ["Ran Into Wall", "Used Head As Battering Ram", "Wanted to Test Wall Rigidity"])
                return False
            # Square is going to be vacated upon snake movement
            if self.visited[row][col] <= 1:
                return True
            # Square will have snake tail upon snake movement
            elif self.visited[row][col] == 2:
                snek.death = "Recreated Ouroboros Legend"
            else:
                snek.death = random.choice(
                    ["Wanted Snake For Dinner", "Fought A Snake...And Lost", "Penalty for Snake Homicide"])
            return False

        # Finds empty spot in grid, returns empty list if no empty spots
        def placeGrid(self):
            candidates = []
            for i in range(self.edgeCount):
                for j in range(self.edgeCount):
                    if self.visited[i][j] == 0:
                        candidates.append([i, j])
            if not candidates:
                return []
            emptySpot = random.choice(candidates)
            return emptySpot

        # Places mushroom in empty spot on grid
        def placeMushroom(self):
            mushroomSpot = self.placeGrid()
            # Checks if mushroomSpot is empty
            if not mushroomSpot:
                return
            # Luck 3 increases chance of holy mushrooms
            if snek.effects[-9] >= 3 and random.randint(1, 5) <= 1:
                mType = -8
            else:
                # Set mushroom types
                mType = random.randint(-11, -1)
            self.visited[mushroomSpot[0]][mushroomSpot[1]] = mType

        # PLaces specific mushroom
        def placeLuckyMushroom(self, mushNum):
            mushroomSpot = self.placeGrid()
            self.visited[mushroomSpot[0]][mushroomSpot[1]] = mushNum

        # Simulates snake movement
        def snakeTravel(self, snek):
            snek.traveled += 1

            # Checking for valid move
            if snek.dir == "RIGHT":
                proposedHead = [snek.head[0], snek.head[1] + 1]
            elif snek.dir == "LEFT":
                proposedHead = [snek.head[0], snek.head[1] - 1]
            elif snek.dir == "UP":
                proposedHead = [snek.head[0] - 1, snek.head[1]]
            elif snek.dir == "DOWN":
                proposedHead = [snek.head[0] + 1, snek.head[1]]

            # Valid move logic
            if self.checkValid(proposedHead[0], proposedHead[1]):
                snek.head=proposedHead

                # Snake moves past squares
                for i in range(self.edgeCount):
                    for j in range(self.edgeCount):
                        if self.visited[i][j] > 0:
                            self.visited[i][j] -= 1

                # Eating mushroom
                if self.visited[snek.head[0]][snek.head[1]] < 0:

                    # Tracks mushroom type
                    mType = self.visited[snek.head[0]][snek.head[1]]

                    # Tracks mushroom eaten
                    self.mushroomCount[mType] += 1
                    snek.effects[mType] += 1

                    # Simulates effects that should trigger on every snake movement
                    snek.runEffects()

                    # Fear 3 effect
                    if snek.effects[-6] >= 3:
                        self.visited[snek.head[0]][snek.head[1]] = 0
                        headSpot = self.placeGrid()
                        snek.head = [headSpot[0], headSpot[1]]

                    # Marking current square with snake length
                    self.visited[snek.head[0]][snek.head[1]] = snek.length

                    # Growth 1&2 effect
                    snek.length += snek.effectDict["growBy"]

                    # Simulating snake growth
                    for i in range(self.edgeCount):
                        for j in range(self.edgeCount):
                            if self.visited[i][j] > 0:
                                self.visited[i][j] += snek.effectDict["growBy"]

                    # Antidote 3 effect
                    if snek.effects[-3] >= 3 and mType in [-2, -4, -5, -6, -10, -11]:
                        coin = random.randint(0, 1)
                        if coin == 0:
                            snek.effects[mType] -= 1

                    # Places mushroom and plays mushroom sound
                    self.placeMushroom()
                    self.mushroomSound.play()

                # Visiting non-mushroom square
                else:
                    self.visited[snek.head[0]][snek.head[1]] = snek.length

            # Not valid move
            else:
                pygame.display.update()
                runProgress[0] = False

    # Resets effect variables
    def resetEffects():
        return {"anti1": False, "anti2": False, "angry": False, "angryBuild": 0, "angrySpeed": 3,
                "fearMeter": 0, "growBy": 1, "growthMeter": 0, "luckPlanted": 0,
                "resistActive": False, "resistDir": 0, "tiredMeter": 0}

    # Snake class, stores snake effects and info
    class sneko(object):
        def __init__(self, head, dir, length):
            self.head = head
            self.dir = dir
            self.length = length
            self.death = ""
            self.traveled = 0
            # Effects and maxEffect are reverse indexed
            self.effects = [0] * 11
            self.maxEffect = [0] * 11
            self.effectDict = resetEffects()

        # These effects happen upon eating mushroom or specific mushroom
        def runEffects(self):
            # Antidote 1/2 revert 1/2 negative effects, triggered before other effects are updated
            if (self.effects[-3] == 1 and not self.effectDict["anti1"]) or (
                    self.effects[-3] == 2 and not self.effectDict["anti2"]):
                evilShrooms = [-2, -4, -5, -6, -10, -11]
                cands = []
                for i in evilShrooms:
                    if self.effects[i] > 0:
                        for _ in range(self.effects[i]):
                            cands.append(i)
                if self.effects[-3] == 1 or len(cands) == 1:
                    if len(cands) >= 1:
                        anti = random.choice(cands)
                        self.effects[anti] -= 1
                if self.effects[-3] == 2 and len(cands) >= 2:
                    anti = random.sample(cands, 2)
                    self.effects[anti[0]] -= 1
                    self.effects[anti[1]] -= 1

                # Makes sure Antidote 1&2 trigger only once
                if not self.effectDict["anti1"]:
                    self.effectDict["anti1"] = True
                else:
                    self.effectDict["anti2"] = True

            # Anger 1&2 effects
            if self.effects[-2] == 0:
                self.effectDict["angrySpeed"] = 3
                self.effectDict["angry"] = False
                self.effectDict["angryBuild"] = 0
            elif snek.effects[-2] == 1:
                self.effectDict["angrySpeed"] = 5
                self.effectDict["angry"] = False
                self.effectDict["angryBuild"] = 0
            elif snek.effects[-2] == 2:
                self.effectDict["angrySpeed"] = 8
                self.effectDict["angry"] = False
                self.effectDict["angryBuild"] = 0
            elif snek.effects[-2] >= 3:
                self.effectDict["angry"] = True

            # Sets growth length for Grow 1&2&3
            if self.effects[-7] == 0:
                self.effectDict["growBy"] = 1
            elif self.effects[-7] == 1:
                self.effectDict["growBy"] = 2
            elif self.effects[-7] >= 2:
                self.effectDict["growBy"] = 4

            # Luck 1&2
            if self.effects[-9] >= 1 > self.effectDict["luckPlanted"]:
                if luckyNums:
                    grid.placeLuckyMushroom(random.choice(luckyNums))
                else:
                    grid.placeMushroom()
                self.effectDict["luckPlanted"] += 1
            if self.effects[-9] >= 2 and self.effectDict["luckPlanted"] < 3:
                if luckyNums:
                    grid.placeLuckyMushroom(random.choice(luckyNums))
                    grid.placeLuckyMushroom(random.choice(luckyNums))
                else:
                    grid.placeMushroom()
                    grid.placeMushroom()
                self.effectDict["luckPlanted"] += 2

            # Resetting tired on eating mushroom
            if self.effects[-11] <= 2:
                self.effectDict["tiredMeter"] = 0

            # Max effects update, used to update journal after game
            for i in range(len(snek.maxEffect)):
                self.maxEffect[i] = max(self.maxEffect[i], self.effects[i])
                self.maxEffect[i] = min(3, self.maxEffect[i])

        # The following effects happen every time snake moves
        def constantEffects(self):
            # Anger 3 effect
            if self.effectDict["angry"]:
                self.effectDict["angryBuild"] += 1
                self.effectDict["angrySpeed"] = 8 + self.effectDict["angryBuild"] // 50

            # Growth 3 effect
            if snek.effects[-7] >= 3:
                self.effectDict["growthMeter"] += 1
                if self.effectDict["growthMeter"] >= 10:
                    self.length += 1
                    self.effectDict["growthMeter"] = 0

            # Holy 3 effect
            if self.effects[-8] >= 3:
                self.effects = [0] * 11
                self.maxEffect[-8] = 3
                self.effectDict = resetEffects()
                achList[3] = True

            # Tired 1&2&3 effect
            if self.effects[-11] == 1:
                self.effectDict["tiredMeter"] += 2
            elif self.effects[-11] >= 2:
                self.effectDict["tiredMeter"] += 5

            # Tired ends game if tiredMeter reaches 100
            if self.effectDict["tiredMeter"] >= 100:
                runProgress[0] = False
                self.death = random.choice(
                    ["Nap Time", "Fell Asleep at the Wheel", "Dreams about Normal Mushrooms"])

    # Dicts of movement for normal movement and confusion
    dirList0 = ["LEFT", "RIGHT", "UP", "DOWN"]
    dirList1 = ["RIGHT", "LEFT", "DOWN", "UP"]
    dirList2 = random.choice([dirList0, dirList1])
    dirList = [dirList0, dirList1, dirList2]

    dirPairs = {"LEFT": "RIGHT", "RIGHT": "LEFT", "UP": "DOWN", "DOWN": "UP"}
    keyMap = {pygame.K_LEFT: 0, pygame.K_RIGHT: 1, pygame.K_UP: 2, pygame.K_DOWN: 3}

    # Sets up direction variables
    changeDir = False
    inputDir = 1

    # Draws background, title, grid background, and arrow keys
    window.fill(fillColor)
    drawTitle("Journey #" + str(achProgress[7] + 1), "")
    pygame.draw.rect(window, wood,
                     (screenSize[0] // 2 - tLength // 2 - 5, screenSize[1] // 2 - tLength // 2
                      - 5, tLength + 10, tLength + 10))
    upButton, downButton, leftButton, rightButton = drawAllKeys(dark)

    # Initializes snake and grid, draws grid
    snek = sneko([2, 2], "RIGHT", 3)
    grid = grid(edgeCount, edgeLength)
    drawFlavor("Score: " + str("0") + "   High Score: " + str(achProgress[6]))
    grid.drawGrid(0, snek.dir, snek.head)

    # Draws static snake iamge in bottom right
    snakeImage = pygame.image.load("img/snake.png")
    snakeImageSmall = pygame.transform.scale(snakeImage, (int(screenX * 0.3), int(screenX * 0.3)))
    window.blit(snakeImageSmall, (screenX * 0.55, screenY * 0.78))

    # Places mushrooms
    for _ in range(3):
        grid.placeMushroom()
    if mushroomOverlord:
        for _ in range(100):
            grid.placeMushroom()
    runProgress = [True]
    pygame.display.update()

    # Running game (main game loop)
    while runProgress[0]:
        # Game speed determined by whether Anger is active
        clock.tick(snek.effectDict["angrySpeed"])

        # Tracks user input
        for event in pygame.event.get():
            # Quits game
            if event.type == pygame.QUIT:
                pygame.quit()
            # Arrow key pressed
            if event.type == pygame.KEYDOWN:
                if event.key in keyMap:
                    changeDir = True
                    inputDir = keyMap[event.key]
                    break
            # Mouse button on d-pad pressed
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if leftButton.collidepoint(pos) or rightButton.collidepoint(pos) or upButton.collidepoint(
                        pos) or downButton.collidepoint(pos):
                    changeDir = True
                    if leftButton.collidepoint(pos):
                        inputDir = 0
                    elif rightButton.collidepoint(pos):
                        inputDir = 1
                    elif upButton.collidepoint(pos):
                        inputDir = 2
                    else:
                        inputDir = 3
                    break

        # Resist 1 effect
        if changeDir and snek.effects[-10] >= 1:
            changeDir, snek.effectDict["resistActive"] = snek.effectDict["resistActive"], changeDir
            inputDir, snek.effectDict["resistDir"] = snek.effectDict["resistDir"], inputDir

        # Resist 2&3 effects
        if changeDir and snek.effects[-10] >= 2:
            coin = random.randint(1, 10)
            if snek.effects[-10] >= 3:
                changeDir = False
            elif snek.effects[-10] == 2:
                changeDir = (coin <= 8)

        # Fear 1&2 effects
        if snek.effects[-6] == 1:
            snek.effectDict["fearMeter"] += 1
            if snek.effectDict["fearMeter"] >= 20:
                changeDir = True
                inputDir = random.randint(0, 3)
                snek.effectDict["fearMeter"] = 0
        elif snek.effects[-6] >= 2:
            snek.effectDict["fearMeter"] += 2
            if snek.effectDict["fearMeter"] >= 20:
                changeDir = True
                inputDir = random.randint(0, 3)
                snek.effectDict["fearMeter"] = 0

        # Logic implemented to handle confusion
        if changeDir:
            changeDir = False
            drawAllKeys(dark)
            if snek.effects[-5] <= 2:
                desiredDir = dirList[snek.effects[-5]][inputDir]
            else:
                desiredDir = random.choice(dirList0)
            if snek.dir != dirPairs[desiredDir]:
                snek.dir = desiredDir
                if desiredDir == "LEFT":
                    drawLeft(grass)
                elif desiredDir == "RIGHT":
                    drawRight(grass)
                elif desiredDir == "UP":
                    drawUp(grass)
                else:
                    drawDown(grass)

        # Snake movement, major game function
        grid.snakeTravel(snek)

        # Snake constant effects
        snek.constantEffects()

        # Updates scores (checkpoint) runProgress[0]
        if True:
            grid.score = snek.length - 3
            achProgress[6] = max(achProgress[6], grid.score)
            drawFlavor("Score: " + str(grid.score) + "   High Score: " + str(achProgress[6]))
            grid.drawGrid(snek.effects[-4], snek.dir, snek.head)
            pygame.display.update()

    # Death screen
    pygame.mixer.music.stop()
    grid.crashSound.play()
    pygame.time.delay(1000)
    drawDeathScreen(grid.score, snek.effects, snek.death)

    # Updates mushroom total count, mushroom unique count
    for i in range(len(mushroomCount)):
        mushroomCount[~i] += grid.mushroomCount[i]
        mushroomUnique[~i] = max(snek.maxEffect[i], mushroomUnique[~i])

    # Updates achievements, including entries, deaths, distance traveled, total mushrooms eaten
    if sum(grid.mushroomCount) == 0:
        achList[0] = True
    uniqueMushroomsRun=0
    for effect in snek.maxEffect:
        if effect!=0:
            uniqueMushroomsRun += 1
    achProgress[4] = max(achProgress[4],uniqueMushroomsRun)
    achProgress[5] = sum(mushroomUnique)
    achProgress[7] += 1
    achProgress[8] = sum(mushroomCount)
    achProgress[9] += snek.traveled



# Draws intro screen and loads intro music
drawIntro()
startButton, journalButton, achButton = drawMenu()
pygame.mixer.music.load("../sneko2/songs/ukulele.mp3")
pygame.mixer.music.play(-1)
pygame.display.update()

# Main game loop
while active:
    clock.tick(30)

    # Checks for user input
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            active = False

        # Mouse pressed
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()

            # Checks if menu buttons are pressed
            if startButton.collidepoint(pos):
                drawStartButton(grass)
            elif journalButton.collidepoint(pos):
                drawJournalButton(grass)
            elif achButton.collidepoint(pos):
                drawAchButton(grass)
            pygame.display.update()

        # Mouse release
        if event.type == pygame.MOUSEBUTTONUP:
            pos = pygame.mouse.get_pos()

            # Start button triggered
            if startButton.collidepoint(pos):
                # Pop-up with game instructions
                if pops[0]:
                    pops[0] = False
                    drawPop("Snake Guide",
                            [("Move with Arrow Keys", 2),
                             ("Eat Mushrooms", 3.5),
                             ("Grow Longer", 5),
                             ("Feel Strange Effects", 6.5),
                             ]
                            )

                # Plays music
                pygame.mixer.music.load(gameSongs[achProgress[7] % 3])
                pygame.mixer.music.play(-1)

                # Finds lucky nums (mushrooms with undiscovered effects)
                luckyNums = []
                for idx in range(11):
                    if mushroomUnique[idx] < 3:
                        luckyNums.append(~idx)

                # Starts game
                startGame(luckyNums)

                # Draws menu
                drawMenu()

                # Plays background music
                if mushroomOverlord:
                    if not pops[4]:
                        pygame.mixer.music.load("../sneko2/songs/buddy.mp3")
                        pygame.mixer.music.play(-1)
                    else:
                        pops[4] = False
                else:
                    pygame.mixer.music.load("../sneko2/songs/ukulele.mp3")
                    pygame.mixer.music.play(-1)

            # Journal button triggered
            elif journalButton.collidepoint(pos):
                # Pop-up explaining journal
                if pops[1]:
                    pops[1] = False
                    drawPop("Journal Guide",
                            [("Eat Mushrooms", 2),
                             ("Discover Effects", 3.5),
                             ("Learn Mushroom Types", 5),
                             ("Fill Out Entries", 6.5),
                             ]
                            )

                # Runs journal, then draws menu
                runJournalAch(0, False)
                drawMenu()

            elif achButton.collidepoint(pos):
                # Pop-up explaining achievement page
                if pops[2]:
                    pops[2] = False
                    drawPop("Achievements",
                            [("Do Snake Things", 2),
                             ("Become Skilled Snake", 3.5),
                             ("Accomplish Goals", 5),
                             ("Find Ending", 6.5),
                             ]
                            )

                # Runs achievement page, then draws menu
                runJournalAch(0, True)

                # Checks for all achievement completion
                if pops[3] and sum(achList) == 11:
                    pops[3] = False
                    drawMenu()
                    pygame.display.update()

                    # Plays victory music
                    pygame.mixer.music.stop()
                    winSound.play()
                    pygame.time.delay(2000)
                    pygame.mixer.music.load("../sneko2/songs/buddy.mp3")
                    pygame.mixer.music.play(-1)

                    # Draws ending pop-up
                    drawPop("Ending",
                            [("Harnessed Mushrooms", 2),
                             ("Mastered Effects", 3.5),
                             ("BECAME...", 5),
                             ("MUSHROOM OVERLORD!!!", 6.5),
                             ]
                            )

                    # Activates mushroom overlord
                    mushroomOverlord = True
                    drawMenu()

                # Draws menu
                drawMenu()

            # Reset menu button colors
            drawStartButton(wood)
            drawJournalButton(wood)
            drawAchButton(wood)
            pygame.display.update()

pygame.quit()
