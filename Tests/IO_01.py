import pygame as pg
import sys

sys.path.append("../Music Player 2.1")
import ioMethods as io

pg.init()

sc = pg.display.set_mode((500, 500))
pg.display.set_caption("IO Test")

cap = io.inputBox(0, 0, prompt="Testing Testing 123")
noCap = io.inputBox(0, 40)
maxTest = io.inputBox(0, 80, max=20)
filledTest = io.inputBox(0, 118, filled=True)

slider = io.inputSlider(0, 200)
sliderText = io.text(0, 170)

progressBar = io.progressBar(0, 250, current_value=slider.value)

iBoxes = [noCap, cap, maxTest, filledTest, slider, sliderText, progressBar]

noCapText = io.text(300, 40)
capText = io.text(300, 0)
maxText = io.text(300, 80)
filledText = io.text(300, 118)
outputText = [noCapText, capText, maxText, filledText]

running = True
while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        
        for iBox in iBoxes:
            iBox.handleEvent(event)

    progressBar.setValue(slider.value)
    sliderText.setText(f"Value: {slider.value}")

    noCapText.setText(noCap.finalText)
    capText.setText(cap.finalText)
    maxText.setText(maxTest.finalText)
    filledText.setText(filledTest.finalText)

    for iBox in iBoxes:
        if isinstance(iBox, io.inputBox):
            iBox.update()
    
    sc.fill((192, 72, 72))

    for iBox in iBoxes:
        iBox.draw(sc)

    for oText in outputText:
        oText.draw(sc)

    pg.display.flip()