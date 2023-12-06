# Import necessary modules
import os
import json
import pygame as pg
from random import randint
import eyed3

# Import custom module for IO methods
import ioMethods as io

# Define the version number
verTxt = "0.0.1"

# Define a class for color constants
class colours:
    BG1_C = (91,36,180)
    BG2_C = (171,0,255)
    PROG_C = (224,0,204)

    TEXT_COLOUR = (0, 0, 0)
    PROMPT_COLOUR = (30, 30, 30)

# Initialize global variables
initialised = None
playlistPath = None
shuffling = None
looping = None
songInfo = {
    "ID": 0,
    "SongName": "SongName",
    "SongArtist": "ArtistName",
    "Length": None
}
playlist = []
paused = False
currentPos = 1
msLen = 1

# Initialize Pygame
pg.init()

# Set the screen resolution
resolution = (400, 600)
sc = pg.display.set_mode(resolution)
pg.display.set_caption("Music Player")
pg.display.set_icon(pg.image.load("Icons/unpause.png"))

# Define constants for centering UI elements
CENTRE_X = resolution[0]//2
CENTRE_Y = resolution[1]//2

# Initialize Pygame clock
clock = pg.time.Clock()

# Function to unpack data from the configuration file
def dataUnpacker():
    with open(os.path.join("Data", "cfg.json"), "r") as cfgFile:
        rawData = cfgFile.read()
        data = json.loads(rawData)

    global initialised, playlistPath, shuffling, looping, songInfo, playlist
    initialised = data["Initialised"]
    playlistPath = data["PlaylistPath"]
    shuffling = data["Shuffling"]
    looping = data["Looping"]
    songInfo = data["SongInfo"]

    playlist = [os.path.join(playlistPath, item) for item in os.listdir(playlistPath)]

# Function to pack data into the configuration file
def dataPacker():
    data = {
        "Initialised": initialised,
        "PlaylistPath": playlistPath,
        "Shuffling": shuffling,
        "Looping": looping,
        "SongInfo": songInfo
    }

    with open(os.path.join("Data", "cfg.json"), "w") as cfgFile:
        json.dump(data, cfgFile, indent=4)

# Function to play a selected song by ID
def playSong(ID):
    if 0 <= ID < len(playlist):
        songPath = playlist[ID]
        print(songPath)

        if os.path.exists(songPath):
            pg.mixer.music.stop()

            pg.mixer.music.load(songPath)
            pg.mixer.music.play()

            if paused:
                pg.mixer.music.pause()

        global currentPos, msLen
        msLen = pg.mixer.Sound(songPath).get_length() * 1000
        currentPos = msLen - pg.mixer.music.get_pos()

        hours, remainder = divmod(int(msLen // 1000), 3600)
        minutes, seconds = divmod(remainder, 60)

        formatted_length = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        songInfo["Length"] = formatted_length

        song = eyed3.load(songPath)
        if song.tag:
            name = song.tag.artist
            if name:
                songInfo["SongArtist"] = name
            else:
                songInfo["SongArtist"] = "Unknown Artist"

        songInfo["SongName"] = os.listdir(playlistPath)[ID]
        songIDTxt.setText(f"ID: {songInfo['ID']}")
    else:
        print("Error: SongID not in Playlist")

# Function to play the next song
def nextSong(inc=1):
    if shuffling:
        oldID = songInfo["ID"]
        while songInfo["ID"] == oldID:
            songInfo["ID"] = randint(0, len(playlist) - 1)
    else:
        songInfo["ID"] += inc

        if songInfo["ID"] > len(playlist):
            if looping:
                songInfo["ID"] = 0
            else:
                paused = True
                songInfo["ID"] = len(playlist) - 1
        elif songInfo["ID"] < 0:
            if looping:
                songInfo["ID"] = len(playlist) - 1
            else:
                songInfo["ID"] = 0
    playSong(songInfo["ID"])

# Function to toggle pause/play
def togglePause():
    global paused
    if paused:
        pg.mixer.music.unpause()
        pause_icon.image = pg.transform.scale(pg.image.load("Icons/pause.png"), (16*5, 16*5))
        paused = False
    else:
        pg.mixer.music.pause()
        unpause_icon = pg.transform.scale(pg.image.load("Icons/unpause.png"), (16*5, 16*5))
        
        # Calculate the x-position to center the button
        pause_icon.rect.x = resolution[0] // 2 - unpause_icon.get_width() // 2
        
        pause_icon.image = unpause_icon
        paused = True

# ---- Shared UI ---- #
ver = io.text(0, 0, f"Music Player {verTxt}")
errorText = io.text(0, 20, "", colourOverride=(255, 0, 0))

# ---- Initialisation UI ---- #
fpPrompt = io.text(20, resolution[1]//2 - 32//2 - 20, "No playlist path found!")
fpBox = io.inputBox(20, resolution[1]//2 - 32//2, prompt="Input playlist directory")

initUI = [ver, fpBox, fpPrompt, errorText]

# ---- Music Player UI ---- #
progBar = io.progressBar(0, resolution[1] - resolution[1]//3, resolution[0], colour=colours.PROG_C)
minTime = io.text(2, resolution[1] - resolution[1]//3 + 22, "00:00:00")
maxTime = io.text(resolution[0] - 35, resolution[1] - resolution[1]//3 + 22, "0:00")
songNameTxt = io.text(0, 0, songInfo["SongName"], 2)
artistNameTxt = io.text(0, 0, songInfo["SongArtist"], 1)
songIDTxt = io.text(resolution[0] - 45, 110, f"ID: {songInfo['ID']}")

shufflingTxt = io.text(0, 24, f"Shuffling: {shuffling}")
loopingTxt = io.text(0, 48, f"Looping: {looping}")

# Load Icons
back_icon = io.button(resolution[0]//2 - 140, 480, "Icons/backSong.png", action=lambda: nextSong(-1))
forward_icon = io.button(resolution[0]//2 + 60, 480, "Icons/forwardSong.png", action=nextSong)
pause_icon = io.button(resolution[0]//2 - 40, 480, "Icons/pause.png", action=togglePause)

musicPlayerUI = [ver, errorText, progBar, minTime, maxTime, back_icon, forward_icon, pause_icon, songNameTxt, artistNameTxt, songIDTxt, loopingTxt, shufflingTxt]

dataUnpacker()

playSong(songInfo["ID"])
togglePause()

running = True
while running:
    # Draw regular UI
    if initialised:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            elif event.type == pg.KEYDOWN:
                oldID = songInfo["ID"]
                if event.key == pg.K_RIGHT:
                    try:
                        nextSong()
                    except Exception as e:
                        errorText.setText(str(e))
                        songInfo["ID"] = oldID + 1
                elif event.key == pg.K_LEFT and not songInfo["ID"]-1 < 0:
                    try:
                        nextSong(-1)
                    except Exception as e:
                        errorText.setText(str(e))
                        songInfo["ID"] = oldID - 1
                elif event.key == pg.K_SPACE:
                    togglePause()
                elif event.key == pg.K_F1:
                    shuffling = not shuffling
                elif event.key == pg.K_F2:
                    looping = not looping
        perc = (pg.mixer.music.get_pos() / msLen) * 100
        if perc < 0:
            nextSong()

        hours, remainder = divmod(int(pg.mixer.music.get_pos() // 1000), 3600)
        minutes, seconds = divmod(remainder, 60)
        formatted_length = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

        # Configure variable UI
        maxTime.x = sc.get_width() - maxTime.textSurface.get_width() - 2
        songNameTxt.centre(sc, yPos=100)
        artistNameTxt.centre(sc, yPos=350)
        pause_icon.centre(sc, yPos=520)
        
        songNameTxt.setText(songInfo["SongName"])
        artistNameTxt.setText(songInfo["SongArtist"])
        maxTime.setText(songInfo["Length"])
        minTime.setText(formatted_length)
        shufflingTxt.setText(f"Shuffling [F1 Toggle]: {shuffling}")
        loopingTxt.setText(f"Looping [F2 Toggle]: {looping}")

        percentage = (pg.mixer.music.get_pos() / msLen) * 100
        progBar.setValue(percentage)
        #print(progBar.current_value)

        # Background
        sc.fill(colours.BG1_C)
        pg.draw.rect(sc, colours.BG2_C, pg.Rect(0, resolution[1] - resolution[1]//3, resolution[0], resolution[1]//3))

        pg.draw.circle(sc, colours.BG1_C, (resolution[0]//2, 520), 50)
        pg.draw.circle(sc, (0, 0, 0), (resolution[0]//2, 520), 50, 2)
        for element in musicPlayerUI:
            element.draw(sc)

            if isinstance(element, io.button):
                element.handleEvent()

    # Draw initialisation UI
    else:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

            for obj in initUI:
                obj.handleEvent(event)
                if isinstance(obj, io.inputBox):
                    obj.update()

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_RETURN:
                    if os.path.exists(fpBox.finalText):
                        errorText.setText("")
                        playlistPath = fpBox.finalText
                        initialised = True
                        songInfo["ID"] = -1

                    else:
                        errorText.setText("Error: Folder not found.")

        sc.fill((20, 100, 20))

        for obj in initUI:
            obj.draw(sc)

    pg.display.flip()

dataPacker()
pg.quit()