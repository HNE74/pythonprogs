#Import Modules
import sys, os, pygame, random
import pygame.gfxdraw
import pygame.surface
import pygame.color
import pygame.mixer
from pygame.locals import *
from pygame.color import *

#######################################################
### Cave Copter - by Heiko Nolte, February 2010
### To execute install Python 2.x and PyGame API
### This is freeware.
#######################################################

# images
_copterImage=None
_ufoImage=None
_ufoKillImage=None
_ufoShotImage=None
_fuelImage=None
_ammoImage=None
_rocketImage=None
_mineImage=None
_titleImage=None

# sounds
_heliSound=None
_missleSound=None
_enemySound=None
_enemyKillSound=None
_fuelSound=None
_fuelDownSound=None
_ammoSound=None
_mineSound=None
_copterKillSound=None

# screen dimensions
_backgroundWidth=800
_backgroundHeight=600

# High score
_highScore=0

##############################################################
### Utility functions
##############################################################

# load image
def loadImage(name, colorkey=None):

    fullname = name
    try:
        image = pygame.image.load(fullname)
    except pygame.error, message:
        print 'Cannot load image:', fullname
        raise SystemExit, message
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image, image.get_rect()

# preload images
def loadImages():

    global _copterImage
    global _ufoImage
    global _ufoKillImage
    global _ufoShotImage
    global _fuelImage
    global _rocketImage
    global _ammoImage
    global _mineImage
    global _titleImage

    _copterImage=loadImage('res\\copter1.png', (0,0,0))
    _ufoImage=loadImage('res\\enemyUFO.png', (0,0,0))
    _ufoKillImage=loadImage('res\\enemyUFOKill.png', (0,0,0))
    _ufoShotImage=loadImage('res\\ufoShot.png', (0,0,0))
    _fuelImage=loadImage('res\\fuelTank.png', (0,0,0))
    _rocketImage=loadImage('res\\rocket.png', (0,0,0))
    _ammoImage=loadImage('res\\ammo.png', (0,0,0))
    _mineImage=loadImage('res\\enemyMine.png', (0,0,0))
    _titleImage=loadImage('res\\title.png',  (0,0,0))

# load sound
def loadSound(name):

    class NoneSound:
        def play(self): pass
    if not pygame.mixer or not pygame.mixer.get_init():
        return NoneSound()
    fullname = name
    try:
        sound = pygame.mixer.Sound(fullname)
    except pygame.error, message:
        print 'Cannot load sound:', fullname
        raise SystemExit, message
    return sound

# preload sounds
def loadSounds():

    global _heliSound
    global _missleSound
    global _enemySound
    global _enemyKillSound
    global _fuelSound
    global _fuelDownSound
    global _ammoSound
    global _mineSound
    global _copterKillSound

    _heliSound=loadSound('res\\heli.wav')
    _missleSound=loadSound('res\\missle.wav')
    _enemySound=loadSound('res\\enemy.wav')
    _enemyKillSound=loadSound('res\\enemyKill.wav')
    _fuelSound=loadSound('res\\fuel.wav')
    _fuelDownSound=loadSound('res\\fuelDown.wav')
    _ammoSound=loadSound('res\\ammo.wav')
    _mineSound=loadSound('res\\mine.wav')
    _copterKillSound=loadSound('res\\copterKill.wav')

    _enemyKillSound.set_volume(0.5)
    _heliSound.set_volume(0.5)
    _fuelDownSound.set_volume(0.2)
    _fuelSound.set_volume(0.05)
    _ammoSound.set_volume(0.5)
    _mineSound.set_volume(0.1)
    _copterKillSound.set_volume(0.5)

# Initialize the game window
def initWindow(width, height):

    pygame.init()
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption('Cave Copter')
    pygame.mouse.set_visible(1)
    return screen

# Create an empty background
def createEmptySurface(screen, rect):

    background = pygame.Surface(rect)
    background = background.convert()
    background.fill((0, 0, 0))
    return background

# Carry out scroll operation of landscape on background by delta
def scrollLandscape(background, delta, tile, topspace):

    shiftDim=(delta, topspace, background.get_rect().width-delta, background.get_rect().height-topspace)
    shiftBackground=background.subsurface(shiftDim)

    shiftLandscape=tile.fetchTile()

    newBackground=pygame.Surface((background.get_rect().width, background.get_rect().height))
    newBackground.blit(shiftBackground, (0,topspace))
    newBackground.blit(shiftLandscape, (background.get_rect().width-delta,topspace))

    return newBackground

# Check background collision of provided sprite
def checkBackgroundCollision(background, toCheck, toCheckGroup):

        try:
            # Carry out check
            result=True
            bgtile=BgTile(background, toCheck.rect)
            tiles = pygame.sprite.RenderPlain()
            tiles.add(bgtile)
            collgroup = pygame.sprite.spritecollide(bgtile, toCheckGroup, 0, pygame.sprite.collide_mask)

            # Communicate check result
            if len(collgroup) > 0: # collision
                collgroup[0].collidedBackground()
                collgroup.remove(toCheck)
                result=False

            # Cleanup
            tiles.remove(bgtile)
        except:
            result=True

        return result

# Checks UFO collisions with other objects
def checkUfoCollisions(ufoGroup, rocketGroup, killedGroup, state, background):

    # Check rocket collision with UFO
    collgroup=pygame.sprite.groupcollide(rocketGroup, ufoGroup, 1, 1)
    for collrocket in collgroup.keys():
        _enemyKillSound.play()
        collufo=collgroup[collrocket][0]
        collufo.image=_ufoKillImage[0]
        killedGroup.add(collufo)
        state.rocketCnt=state.rocketCnt-1
        state.copterScore=state.copterScore+100
        state.ufoCnt=state.ufoCnt-1

    # Avoid ufo collisions with cave
    ufos=ufoGroup.sprites()
    for ndx in range(len(ufos)):
        ufo=ufos[ndx]
        if ufo.rect.left>=0:
            checkBackgroundCollision(background,ufo,ufoGroup)

    # Handle killed UFOs
    handleKilledEnemies(killedGroup)

# Checks copter collisions with other objects
def checkCopterCollisions(copter, ufoGroup, fuelGroup, ammoGroup, \
                          mineGroup, ufoShotGroup, state):
            # Check helicopter collision with UFO
        collgroup=pygame.sprite.spritecollide(copter, ufoGroup, 0, pygame.sprite.collide_mask)
        if len(collgroup) > 0:
            _fuelDownSound.play()
            state.copterFuel=state.copterFuel-5
            if state.fuelCnt<0:
                state.fuelCnt=0

        # Check helicopter collision with fuel tank
        collgroup=pygame.sprite.spritecollide(copter, fuelGroup, 0)
        if len(collgroup) > 0:
            _fuelSound.play()
            collgroup[0].fuel=collgroup[0].fuel-1
            if collgroup[0].fuel<=0:
                fuelGroup.remove(collgroup[0])
                state.fuelCnt=state.fuelCnt-1
                state.lastFuelCnt=0
            state.copterFuel=state.copterFuel+1

        # Check helicopter collision with ammo
        collgroup=pygame.sprite.spritecollide(copter, ammoGroup, 1)
        if len(collgroup) > 0:
            _ammoSound.play()
            state.copterRockets=state.copterRockets+3
            state.ammoCnt=0

        # Check helicopter collision with mine
        collgroup=pygame.sprite.spritecollide(copter, mineGroup, 1)
        if len(collgroup) > 0:
            _fuelDownSound.play()
            state.mineCnt=state.mineCnt-1
            state.copterFuel=state.copterFuel-50

        # Check helicopter collision with ufo shot
        collgroup=pygame.sprite.spritecollide(copter, ufoShotGroup, 1)
        if len(collgroup) > 0:
            _fuelDownSound.play()
            state.ufoShotCnt=state.ufoShotCnt-1
            state.copterFuel=state.copterFuel-50

# Checks rocket collisions with background
def checkRocketCollisions(rocketGroup, mineGroup, state, background):

        # Check rocket collisions with cave
        rockets=rocketGroup.sprites()
        for ndx in range(len(rockets)):
            rocket=rockets[ndx]
            checkBackgroundCollision(background,rocket,rocketGroup)

        # Check rocket collision with mine
        collgroup=pygame.sprite.groupcollide(rocketGroup, mineGroup, 1, 1)
        for collrocket in collgroup.keys():
            _enemyKillSound.play()
            state.rocketCnt=state.rocketCnt-1
            state.copterScore=state.copterScore+25
            state.mineCnt=state.mineCnt-1

# Checks ufo shot collisions with background
def checkUfoShotCollisions(ufoShotGroup, state, background):

        # Check shot collisions with cave
        shots=ufoShotGroup.sprites()
        for ndx in range(len(shots)):
            shot=shots[ndx]
            checkBackgroundCollision(background, shot, ufoShotGroup)

# Handles disappearence of killed enemies from screen
def handleKilledEnemies(killedGroup):

    # Check if there are exploded ufos to be removed
    toBeRemoved=[]
    for ndx in range(len(killedGroup.sprites())):
        killed=killedGroup.sprites()[ndx]
        killed.killCnt=killed.killCnt-1
        if killed.killCnt<=0:
            toBeRemoved.append(killed)

    for ndx in range(len(toBeRemoved)):
        killedGroup.remove(toBeRemoved[ndx])

# Adds randomly fuel tanks
def addFuel(tile, fuelGroup, state, topSpace):

    global _backgroundWidth
    global _backgroundHeight

    state.lastFuelCnt=state.lastFuelCnt+1
    doAdd=random.randint(1,100)
    if state.fuelCnt<state.fuelMax and state.lastFuelCnt>state.doFuelCnt:
        if doAdd==1:
            x=random.randint(1, 2)
            if x==1:
                position=tile.top_tileHeight+topSpace+random.randint(20, 40)
            else:
                position=_backgroundHeight-tile.btm_tileHeight-random.randint(30, 50)
            fuel=FuelTank(_backgroundWidth-50, position, fuelGroup, state)
            fuelGroup.add(fuel)
            state.fuelCnt=state.fuelCnt+1
            state.lastFuelCnt=0

# Adds randomly ammo
def addAmmo(tile, ammoGroup, state, topSpace):

    global _backgroundWidth
    global _backgroundHeight

    state.lastAmmoCnt=state.lastAmmoCnt+1
    doAdd=random.randint(1,100)
    if state.ammoCnt<state.ammoMax and state.lastAmmoCnt>state.doAmmoCnt:
        if doAdd==1:
            x=random.randint(1, 2)
            if x==1:
                position=tile.top_tileHeight+topSpace+random.randint(20, 40)
            else:
                position=_backgroundHeight-tile.btm_tileHeight-random.randint(30, 50)
            ammo=Ammo(_backgroundWidth-50, position, ammoGroup, state)
            ammoGroup.add(ammo)
            state.ammoCnt=state.ammoCnt+1
            state.lastAmmoCnt=0

# Adds randomly enemy mines
def addMine(ufoGroup, mineGroup, state):

    global _mineSound

    # Iterate over ufos and create mines randomly
    for ndx in range(len(ufoGroup.sprites())):
        ufo=ufoGroup.sprites()[ndx]
        if state.mineCnt<state.mineMax:
            mineDeterminator=random.randint(1, state.mineRnd)
            if mineDeterminator<=state.doMine:
                _mineSound.play()
                state.mineCnt=state.mineCnt+1
                mine=Mine(ufo.rect.left+10, ufo.rect.top+20, mineGroup, state)
                mineGroup.add(mine)


# Adds randomly ufo shots
def addUfoShot(copter, ufoGroup, ufoShotGroup, state):

    global _mineSound

    # Iterate over ufos and create mines randomly
    for ndx in range(len(ufoGroup.sprites())):
        ufo=ufoGroup.sprites()[ndx]
        if state.ufoShotCnt<state.ufoShotMax:
            shotDeterminator=random.randint(1, state.ufoShotRnd)
            if shotDeterminator<=state.doUfoShot:
                _mineSound.play()
                state.ufoShotCnt=state.ufoShotCnt+1
                xdist=ufo.rect.left-copter.rect.left
                ydist=ufo.rect.top-copter.rect.top
                if abs(xdist)>abs(ydist):
                    if xdist < 0:
                        xmove=4
                    else:
                        xmove=-4
                    ymove=0
                else:
                    if ydist < 0:
                        ymove=4
                    else:
                        ymove=-4
                    xmove=0

                shot=UFOShot(ufo.rect.left+10, ufo.rect.top+20, xmove, ymove, ufoShotGroup, state)
                ufoShotGroup.add(shot)

# Adds randomly enemy UFOs
def addUfo(tile, ufoGroup, state, topSpace):

    global _backgroundWidth
    global _backgroundHeight
    global _enemySound

    state.lastUfoCnt=state.lastUfoCnt+1
    doAdd=random.randint(1, 30)
    if state.ufoCnt<state.ufoMax and state.lastUfoCnt>state.doUfoCnt:
        if doAdd==1:
            x=random.randint(1, 2)
            if x==1:
                ymove=random.randint(1,state.maxYDelta)
                position=tile.top_tileHeight+topSpace+random.randint(20, 30)
            else:
                ymove=-random.randint(1,state.maxYDelta)
                position=_backgroundHeight-tile.btm_tileHeight-random.randint(20, 30)

            _enemySound.play()
            ufo=Ufo(_backgroundWidth-50, position-ymove, ufoGroup, state)
            ufo.ymove=ymove
            ufoGroup.add(ufo)
            state.ufoCnt=state.ufoCnt+1
            state.lastUfoCnt=0

# Helicopter fires a rocket
def fireRocket(rocketGroup, copter, state):

    global _missleSound
    global _heliSound

    # Maximum number of rockets not reached and rockets in stock
    if state.rocketCnt<state.rocketMax and state.copterRockets>0:
        _missleSound.play()
        xpos=copter.rect.left+copter.rect.width-20
        ypos=copter.rect.top+copter.rect.height/2
        rocket=Rocket(xpos, ypos, rocketGroup, state)
        rocketGroup.add(rocket)
        state.rocketCnt=state.rocketCnt+1
        state.copterRockets=state.copterRockets-1

# Add text to provided background
def addText(text, background, xpos, ypos, \
            color=(255,255,255), bgcolor=(0,0,0), size=22, center=False):

    font=pygame.font.SysFont("Arial", size, True)
    text=font.render(text, 4, color)
    textpos=text.get_rect()
    textpos.left=0
    textpos.top=0
    if center == True:
        xpos = background.get_width()/2 - textpos.width/2
    cleanrec=(xpos-1, ypos-1, textpos.width, textpos.height)
    if bgcolor!=None:
        background.fill(bgcolor, cleanrec);
    background.blit(text, (xpos, ypos));

# Update game information on top of the screen
def updateCopterInfo(background, state):

    addText("Fuel: " + str(state.copterFuel), background, 15, 3, THECOLORS['lightgrey'], (0,0,0), 20)
    addText("Sector: " + str(state.sector), background, 210, 3, THECOLORS[state.sectorColor], (0,0,0), 20)
    addText("Score: " + str(state.copterScore), background, 440, 3, THECOLORS['cyan'], (0,0,0), 20)
    addText("Rockets: " + str(state.copterRockets), background, 680, 3, THECOLORS['lightgreen'], (0,0,0), 20)

# Explodes sprite into several fragments returned in a sprite group
def explodeSprite(toExplode=None, xtiles=0, ytiles=0):

    # Calculate number of tiles for explosion
    tileWidth=toExplode.image.get_rect().width/xtiles
    tileHeight=toExplode.image.get_rect().height/ytiles

    tileGroup = pygame.sprite.RenderPlain()
    tileTop=toExplode.rect.top
    for ycnt in range(ytiles):
        # Determine y tile dimension
        tileTop=tileTop+tileHeight
        ypos=ycnt*tileHeight
        currentTileHeight=tileHeight
        if ypos+currentTileHeight>toExplode.rect.height:
            currentTileHeight=toExplode.rect.height-ypos

        tileLeft=toExplode.rect.left
        for xcnt in range(xtiles):
            # Determine x tile dimension
            tileLeft=tileLeft+tileWidth
            xpos=xcnt*tileWidth
            currentTileWidth=tileWidth
            if xpos+currentTileWidth>toExplode.rect.width:
                currentTileWidth=toExplode.rect.width-xpos

            # Fetch tile
            tileDim=(xpos, ypos, currentTileWidth, currentTileHeight)
            tileImage=toExplode.image.subsurface(tileDim)

            # Create sprite and add it to sprite group
            tile=ExplodeTile(tileImage, tileLeft, tileTop)
            tileGroup.add(tile)

    return tileGroup




#############################################################
### Classes
#############################################################

# Vertical tile of cave
class CaveTile():

    # Create a cave tile
    def __init__(self, \
                 tileWidth=5, landHeight=600, topSpace=40, \
                 minSpace=350, color=THECOLORS['orange'], \
                 top_tileHeight=100, top_tileDiff=2, \
                 top_maxHeight=300, top_minHeight=50,
                 btm_tileHeight=100, btm_tileDiff=2, \
                 btm_maxHeight=300, btm_minHeight=50):

        self.tileWidth=tileWidth
        self.landHeight=landHeight
        self.color=color
        self.minSpace=minSpace
        self.topSpace=topSpace

        self.top_tileHeight=top_tileHeight
        self.top_maxHeight=top_maxHeight
        self.top_minHeight=top_minHeight
        self.top_tileDiff=top_tileDiff

        self.btm_tileHeight=btm_tileHeight
        self.btm_maxHeight=btm_maxHeight
        self.btm_minHeight=btm_minHeight
        self.btm_tileDiff=btm_tileDiff

    # Fetch a cave tile and set generate next one randomly
    def fetchTile(self):
        tile = pygame.Surface((self.tileWidth, self.landHeight))
        pygame.gfxdraw.box(tile, (0,self.landHeight-self.btm_tileHeight, \
                           self.tileWidth,self.landHeight), self.color)
        pygame.gfxdraw.box(tile,(0,0,self.tileWidth,self.top_tileHeight), self.color)

        # Adjust top tile height
        vec=random.randint(1, 10)
        if vec==1 or vec ==2:
            self.top_tileHeight=self.top_tileHeight+self.top_tileDiff
        elif vec==9 or vec==10:
            self.top_tileHeight=self.top_tileHeight-self.top_tileDiff
        if self.top_tileHeight<=self.top_minHeight:
            self.top_tileHeight=self.top_minHeight
        elif self.top_tileHeight>=self.top_maxHeight:
            self.top_tileHeight=self.top_maxHeight

        # Adjust top tile diff
        vec=random.randint(1, 3)
        if vec==1:
            self.top_tileDiff=self.top_tileDiff+1
            if self.top_tileDiff>5:
                self.top_tileDiff=5
        elif vec==2:
            self.top_tileDiff=self.top_tileDiff-1
            if self.top_tileDiff<1:
                self.top_tileDiff=1

        # Adjust bottom tile height
        vec=random.randint(1, 10)
        if vec==1 or vec ==2:
            self.btm_tileHeight=self.btm_tileHeight-self.btm_tileDiff
        elif vec==9 or vec==10:
            self.btm_tileHeight=self.btm_tileHeight+self.btm_tileDiff
        if self.btm_tileHeight<=self.btm_minHeight:
            self.btm_tileHeight=self.btm_minHeight
        elif self.btm_tileHeight>=self.btm_maxHeight:
            self.btm_tileHeight=self.btm_maxHeight

        # Adjust bottom tile diff
        vec=random.randint(1, 3)
        if vec==1:
            self.btm_tileDiff=self.btm_tileDiff+1
            if self.btm_tileDiff>5:
                self.btm_tileDiff=5
        elif vec==2:
            self.btm_tileDiff=self.btm_tileDiff-1
            if self.btm_tileDiff<1:
                self.btm_tileDiff=1

        # Leave enough space
        restSpace=self.landHeight-self.top_tileHeight-self.btm_tileHeight
        if restSpace<self.minSpace:
            self.top_tileHeight=self.top_tileHeight-(self.minSpace-restSpace)

        return tile

# Sprite to detect background collision
class BgTile(pygame.sprite.Sprite):

    # Initialize background tile
    def __init__(self, background, tiledim):

        pygame.sprite.Sprite.__init__(self)
        self.image=background.subsurface(tiledim)
        self.image.set_colorkey((0,0,0))
        self.rect=tiledim

# Sprite to detect background collision
class ExplodeTile(pygame.sprite.Sprite):

    # Initialize explode tile
    def __init__(self, image, xpos, ypos):

        pygame.sprite.Sprite.__init__(self)
        self.image=image
        self.rect=image.get_rect()
        self.rect.left=xpos
        self.rect.top=ypos
        self.xpos=xpos
        self.ypos=ypos
        self.xdelta=random.uniform(-1, 1)
        self.ydelta=random.uniform(-1, 1)
        self.rotation=random.randint(-3,3)

    # Update explode tile settings
    def update(self):
        self.xpos=self.xpos+self.xdelta
        self.ypos=self.ypos+self.ydelta
        self.rect.left=int(self.xpos)
        self.rect.top=int(self.ypos)

# Fuel tank
class FuelTank(pygame.sprite.Sprite):

    # Init fuel tankeinstance
    def __init__(self, xpos=800, ypos=300, fuelGroup=None, gameState=None):

        global _fuelImage
        pygame.sprite.Sprite.__init__(self) #call Sprite initializer
        self.image, self.rect=_fuelImage
        self.rect.top=ypos
        self.rect.left=xpos
        self.xmove=-1
        self.ymove=0
        self.fuelGroup=fuelGroup
        self.gameState=gameState
        self.fuel=250

    # Update fuel tank settings
    def update(self):

        # Adjust fuel tank position
        newpos = self.rect.move((self.xmove, self.ymove))
        self.rect=newpos

        # Remove fuel tank leaving screen
        if self.rect.left==-30:
            self.gameState.fuelCnt=self.gameState.fuelCnt-1
            self.fuelGroup.remove(self)

# Ammo
class Ammo(pygame.sprite.Sprite):

    # Init fuel tankeinstance
    def __init__(self, xpos=800, ypos=300, ammoGroup=None, gameState=None):

        global _ammoImage
        pygame.sprite.Sprite.__init__(self) #call Sprite initializer
        self.image, self.rect=_ammoImage
        self.rect.top=ypos
        self.rect.left=xpos
        self.xmove=-1
        self.ymove=0
        self.ammoGroup=ammoGroup
        self.gameState=gameState

    # Update fuel tank settings
    def update(self):

        # Adjust ammo position
        newpos = self.rect.move((self.xmove, self.ymove))
        self.rect=newpos

        # Remove fuel tank leaving screen
        if self.rect.left==-30:
            self.gameState.ammoCnt=self.gameState.ammoCnt-1
            self.ammoGroup.remove(self)

# Rocket
class Rocket(pygame.sprite.Sprite):

    # Init fuel tankeinstance
    def __init__(self, xpos=800, ypos=300, rocketGroup=None, gameState=None):

        global _rocketImage
        pygame.sprite.Sprite.__init__(self) #call Sprite initializer
        self.image, self.rect=_rocketImage
        self.rect.top=ypos
        self.rect.left=xpos
        self.xmove=5
        self.ymove=0
        self.rocketGroup=rocketGroup
        self.gameState=gameState

    # Update fuel tank settings
    def update(self):
        global _backgroundWidth

        # Adjust rocket position
        newpos = self.rect.move((self.xmove, self.ymove))
        self.rect=newpos

        # Remove rocket leaving screen
        if self.rect.left>=_backgroundWidth-self.rect.width:
            self.gameState.rocketCnt=self.gameState.rocketCnt-1
            self.rocketGroup.remove(self)

    # Rocket has collided with background
    def collidedBackground(self):

        self.gameState.rocketCnt=self.gameState.rocketCnt-1
        self.rocketGroup.remove(self)

# Mines are dropped by Ufos
class Mine(pygame.sprite.Sprite):

    # Init fuel tankeinstance
    def __init__(self, xpos=800, ypos=300, mineGroup=None, gameState=None):

        global _rocketImage
        pygame.sprite.Sprite.__init__(self) #call Sprite initializer
        self.image, self.rect=_mineImage
        self.rect.top=ypos
        self.rect.left=xpos
        self.xmove=-1
        self.ymove=0
        self.gameState=gameState
        self.mineGroup=mineGroup

    # Update fuel tank settings
    def update(self):
        global _backgroundWidth

        # Adjust rocket position
        newpos = self.rect.move((self.xmove, self.ymove))
        self.rect=newpos

        # Remove mine leaving screen
        if self.rect.left<=0:
            self.gameState.mineCnt=self.gameState.mineCnt-1
            self.mineGroup.remove(self)

#  Ufo Shot
class UFOShot(pygame.sprite.Sprite):

    # Init fuel tankeinstance
    def __init__(self, xpos=-1, ypos=-1, xmove=0, ymove=0, \
                 ufoShotGroup=None, gameState=None):

        global _rocketImage
        pygame.sprite.Sprite.__init__(self) #call Sprite initializer
        self.image, self.rect=_ufoShotImage
        self.rect.top=ypos
        self.rect.left=xpos
        self.xmove=xmove
        self.ymove=ymove
        self.gameState=gameState
        self.ufoShotGroup=ufoShotGroup

    # Update Ufo shot settings
    def update(self):
        global _backgroundWidth

        # Adjust shot position
        newpos = self.rect.move((self.xmove, self.ymove))
        self.rect=newpos

        # Remove shot leaving screen
        if self.rect.left<=0 or self.rect.left>=_backgroundWidth-self.rect.width:
            self.gameState.ufoShotCnt=self.gameState.ufoShotCnt-1
            self.ufoShotGroup.remove(self)

    # Ufo shot has collided with background
    def collidedBackground(self):

        self.gameState.ufoShotCnt=self.gameState.ufoShotCnt-1
        self.ufoShotGroup.remove(self)


# Enemy UFO
class Ufo(pygame.sprite.Sprite):

    # Init UFO instance
    def __init__(self, xpos=800, ypos=300, ufoGroup=None, gameState=None):

        global _ufoImage
        pygame.sprite.Sprite.__init__(self) #call Sprite initializer
        self.image, self.rect=_ufoImage
        self.rect.top=ypos
        self.rect.left=xpos
        self.xmove=-2
        self.ymove=0
        self.ufoGroup=ufoGroup
        self.gameState=gameState
        self.lastReverseCnt=0
        self.killCnt=25

    # Update UFO settings
    def update(self):

        # Adjust UFO position
        newpos = self.rect.move((self.xmove, self.ymove))
        self.rect=newpos

        # Remove UFO leaving screen
        if self.rect.left==-30:
            self.gameState.ufoCnt=self.gameState.ufoCnt-1
            self.ufoGroup.remove(self)

        # Increase last reverse counter
        self.lastReverseCnt=self.lastReverseCnt+1

    # Ufo has collided with background
    def collidedBackground(self):

        # Revert movement direction
        if self.lastReverseCnt > 30:
            self.ymove=-self.ymove
            self.lastReverseCnt=0

# Manages a sprite explosion
class SpriteExplosion():

    # Init sprite explosion
    def __init__(self, background=None, toExplode=None, xtiles=0, ytiles=0):

        # Set input parameter
        self.imageToExplode=toExplode.image
        self.xtiles=xtiles
        self.ytiles=ytiles

        # Calculate number of tiles for explosion
        self.tileWidth=toExplode.get_rect().width/self.xtiles
        self.tileHeigh=toExplode.get_rect().height/self.ytiles

# Player's helicopter
class Copter(pygame.sprite.Sprite):

    # Init helicopter instance
    def __init__(self, xpos=50, ypos=280, state=None):

        global _copterImage
        pygame.sprite.Sprite.__init__(self) #call Sprite initializer
        self.image, self.rect=_copterImage
        self.imageNormal=self.image
        self.imageBackward=pygame.transform.rotate(self.image, 10)
        self.imageForward=pygame.transform.rotate(self.image, -10)
        self.rect.top=ypos
        self.rect.left=xpos
        self.xmove=0
        self.ymove=0
        self.xdelta=2
        self.ydelta=2
        self.xpos=xpos
        self.ypos=ypos
        self.state=state
        self.area = pygame.display.get_surface().get_rect()

    # Update helicopter settings
    def update(self):

        # Drop copter if no fuel left
        if self.state.copterFuel<=0:
            self.ymove=2

        # Set helicopter angle
        if self.xmove < 0:
            self.image=self.imageBackward
        elif self.xmove > 0:
            self.image=self.imageForward
        else:
            self.image=self.imageNormal

        # Adjust helicopter position
        newpos = self.rect.move((self.xmove, self.ymove))
        if newpos.left<=0:
            newpos.left=0
        elif newpos.left+newpos.width>=800:
            newpos.left=newpos.left-self.xdelta

        self.rect = newpos

    # Helicopter has collided with background
    def collidedBackground(self):

        self.kill()
        print ">>>> collided"

# Player's helicopter
class StateData():

    # Initialize state data instance
    def __init__(self):

        # Ufo create parameter
        self.ufoMax=1
        self.ufoCnt=0
        self.lastUfoCnt=-200
        self.doUfoCnt=50
        self.maxYDelta=1

        # Ufo shot create parameter
        self.ufoShotMax=1
        self.ufoShotCnt=0
        self.ufoShotRnd=1000
        self.doUfoShot=25

        # Mine create parameter
        self.mineMax=5
        self.mineCnt=0
        self.mineRnd=1000
        self.lastMineCnt=0
        self.doMine=25

        # Fuel create parameter
        self.fuelMax=1
        self.fuelCnt=0
        self.lastFuelCnt=0
        self.doFuelCnt=1200

        # Ammo create parameter
        self.ammoMax=1
        self.ammoCnt=0
        self.lastAmmoCnt=-600
        self.doAmmoCnt=500

        # Copter state
        self.copterFuel=500
        self.copterRockets=3
        self.copterScore=0

        # Rocket create parameter
        self.rocketMax=3
        self.rocketCnt=0

        # Level parameter
        self.sectorColors=['orange', 'darkgoldenrod4', 'red3', 'turquoise3',
                          'orchid2', 'violetred', 'cornsilk2', 'honeydew3']
        self.sectorColorCnt=0
        self.sectorColor=self.sectorColors[self.sectorColorCnt]
        self.sector=1
        self.sectorCnt=0
        self.nextSectorCnt=2500

    # Adjusts state data to next sector
    def nextSector(self, tile):

        # Check if new sector reached
        self.sectorCnt=self.sectorCnt+1
        if self.sectorCnt >= self.nextSectorCnt:
            self.sector=self.sector+1
            self.sectorCnt=0

            # Set new cave color for sector
            self.sectorColorCnt=self.sectorColorCnt+1
            if self.sectorColorCnt >= len(self.sectorColors):
                self.sectorColorCnt=0
            self.sectorColor=self.sectorColors[self.sectorColorCnt]

            # Increase game difficulty
            if self.sector%4 == 0:
                self.mineMax=self.mineMax+1
            elif self.sector%3 == 0:
                self.ufoMax=self.ufoMax+1
            elif self.sector%2 == 0:
                self.ufoShotMax=self.ufoShotMax+1

            if tile.minSpace>100:
                tile.minSpace=tile.minSpace-25

            if self.sector == 3 or self.sector == 5:
                self.maxYDelta=self.maxYDelta+1


#############################################################
### Main functions
#############################################################

# Process game entry loop
def doEntryLoop(screen,background):

    global _backgroundWidth
    global _titleImage
    global _highScore

    # Draw static background
    tile=CaveTile()
    tile.topSpace=0
    for x in range(_backgroundWidth):
        cave=tile.fetchTile()
        background.blit(cave, (x,tile.topSpace))
    addText("Highscore: " + str(_highScore), background, 310, 300, \
            THECOLORS['lightgreen'], THECOLORS['black'], 20, True)
    addText("[SPACE] to continue", background, 310, 560, \
            THECOLORS['black'], THECOLORS['orange'], 20, True)

    background.blit(_titleImage[0], (130,50))
    screen.blit(background, (0,0))
    pygame.display.flip()

    doLoop=True
    clock=pygame.time.Clock()
    while doLoop:
        clock.tick(100) # fps

        # Catch input event
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit(0)
            elif event.type == KEYDOWN:
                if event.key == 32:
                    doLoop=False


    tile.topSpace=40
    for x in range(_backgroundWidth):
        cave=tile.fetchTile()
        background.blit(cave, (x,tile.topSpace))
    screen.blit(background, (0,0))
    pygame.display.flip()

    return tile

# Process main game loop
def doMainLoop(screen,background, tile):

    global _heliSound
    global _fuelSound
    global _fuelDownSound
    global _enemyKillSound
    global _ufoKillImage

    _heliSound.play()

    # Game state data
    state=StateData()

    # Create helicopter
    copter=Copter(50, 280, state)

    # Create sprite groups
    copterGroup = pygame.sprite.RenderPlain((copter))
    ufoGroup = pygame.sprite.RenderPlain()
    ufoShotGroup = pygame.sprite.RenderPlain()
    killedGroup = pygame.sprite.RenderPlain()
    fuelGroup = pygame.sprite.RenderPlain()
    rocketGroup = pygame.sprite.RenderPlain()
    ammoGroup = pygame.sprite.RenderPlain()
    mineGroup = pygame.sprite.RenderPlain()

    # Main Loop
    clock=pygame.time.Clock()
    delta=1
    doContinue=True
    topSpace=40
    fuelReductionCnt=0
    while doContinue:
        clock.tick(100) # fps

        # Catch input event
        for event in pygame.event.get():
            if event.type == QUIT:
                return
            elif event.type == KEYDOWN:
                if event.key == 273: # up
                    copter.ymove=-copter.ydelta
                if event.key == 274: # down
                    copter.ymove=copter.ydelta
                if event.key == 275: # right
                    copter.xmove=copter.xdelta
                if event.key == 276: # left
                    copter.xmove=-copter.xdelta
                if event.key == 32: # space
                    fireRocket(rocketGroup, copter, state)
            elif event.type == KEYUP:
                copter.xmove=0
                copter.ymove=0

        # Scroll landsape
        tile.color=THECOLORS[state.sectorColor]
        newBackground=scrollLandscape(background, delta, tile, topSpace)
        background.blit(newBackground, (0,0))

        # Add objects to sprite groups
        addUfo(tile, ufoGroup, state, topSpace)
        addUfoShot(copter, ufoGroup, ufoShotGroup, state)
        addMine(ufoGroup, mineGroup, state)
        addFuel(tile, fuelGroup, state, topSpace)
        addAmmo(tile, ammoGroup, state, topSpace)

        # Check object collisions
        checkUfoCollisions(ufoGroup, rocketGroup, killedGroup, state, background)
        doContinue=checkBackgroundCollision(background, copter, copterGroup)
        checkCopterCollisions(copter, ufoGroup, fuelGroup, ammoGroup, \
                              mineGroup, ufoShotGroup, state)
        checkRocketCollisions(rocketGroup, mineGroup, state, background)
        checkUfoShotCollisions(ufoShotGroup, state, background)

        # Check rocket collisions with cave
        rockets=rocketGroup.sprites()
        for ndx in range(len(rockets)):
            rocket=rockets[ndx]
            checkBackgroundCollision(background,rocket,rocketGroup)

        # Update game state data
        if state.copterFuel<0:
            state.copterFuel=0
        updateCopterInfo(background, state)

        # Reduce copter fuel
        if fuelReductionCnt>10 and state.copterFuel>0:
            state.copterFuel=state.copterFuel-1
            fuelReductionCnt=0
            state.copterScore=state.copterScore+1
        fuelReductionCnt=fuelReductionCnt+1

        # Update sprites
        copterGroup.update()
        mineGroup.update()
        ufoGroup.update()
        ufoShotGroup.update()
        killedGroup.update()
        fuelGroup.update()
        ammoGroup.update()
        rocketGroup.update()

        # Update screen
        screen.blit(background, (0,0))
        fuelGroup.draw(screen)
        copterGroup.draw(screen)
        rocketGroup.draw(screen)
        ammoGroup.draw(screen)
        mineGroup.draw(screen)
        ufoShotGroup.draw(screen)
        ufoGroup.draw(screen)
        killedGroup.draw(screen)
        pygame.display.flip()

        # Change to next sectory
        state.nextSector(tile)

    # Copter explodes
    explodeGroup=explodeSprite(copter,10, 4)
    copterGroup.remove(copter)

    global _copterKillSound
    cnt=0
    _copterKillSound.play()
    while cnt<100:

        clock.tick(100) # fps
        cnt=cnt+1

        # Update explosion sprites
        explodeGroup.update()

        # Update screen
        screen.blit(background, (0,0))
        fuelGroup.draw(screen)
        explodeGroup.draw(screen)
        rocketGroup.draw(screen)
        ammoGroup.draw(screen)
        mineGroup.draw(screen)
        ufoGroup.draw(screen)
        killedGroup.draw(screen)
        pygame.display.flip()
        pygame.time.wait(25)

    # New highscore?
    global _highScore
    if state.copterScore > _highScore:
        _highScore=state.copterScore
        addText("New Highscore!", background, 270, 330, \
                THECOLORS['lightgreen'], (0,0,0), 30, True)
    # Show GAME OVER
    addText("GAME OVER", background, 270, 270, \
            THECOLORS['lightgreen'], (0,0,0), 50, True)
    addText("[SPACE] to continue", background, 310, 560, \
            (0,0,0), THECOLORS[state.sectorColor], 20, True)
    screen.blit(background, (0,0))
    pygame.display.flip()
    doLoop=True
    while doLoop:
        clock.tick(100) # fps

        # Catch input event
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit(0)
            elif event.type == KEYDOWN:
                if event.key == 32:
                    doLoop=False


# Entrypoint
def main():

    # Main window dimension
    global backgroundWidth
    mainWindowWidth=_backgroundWidth
    mainWindowHeight=_backgroundHeight

    # Initialize window
    screen=initWindow(mainWindowWidth, mainWindowHeight)

    # Load images for sprites
    loadImages()

    # Load sounds
    loadSounds()

    # Create empty background
    background=createEmptySurface(screen, screen.get_size())

    while True:
        # Enter entry loop
        caveTile=doEntryLoop(screen, background)

        # Enter main loop
        doMainLoop(screen, background, caveTile)

#this calls the 'main' function when this script is executed
if __name__ == '__main__': main()