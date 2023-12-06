# Initialize Pygame
import pygame as pg
import textwrap
pg.init()

# Define a font and color palette using a class
FONT = pg.font.Font(None, 24)
class colours:
    COLOUR_ACTIVE = (91,36,180)
    COLOUR_HOVER = (171,0,255)
    COLOUR_INACTIVE = (224,0,204)

    TEXT_COLOUR = (0, 0, 0)
    PROMPT_COLOUR = (30, 30, 30)

# Define an input box class for text input
class inputBox:
    def __init__(self, x, y, w=140, h=32, max = 0, prompt="", filled=False, text=""):
        # Initialize input box attributes
        self.rect = pg.Rect(x, y, w, h)
        self.colour = colours.COLOUR_INACTIVE
        self.max = max
        self.prompt = prompt
        self.text = text
        self.textSurface = FONT.render(text, True, self.colour)
        self.active = False
        self.hover = False
        self.filled = filled
        self.finalText = "placeholder"

    # Handle events such as mouse clicks and key presses
    def handleEvent(self, event):
        # Mouse events
        if event.type == pg.MOUSEBUTTONDOWN:
            # Check if mouse clicked inside the input box
            if self.rect.collidepoint(event.pos):
                self.active = True
            else:
                self.active = False
            # Change color based on activity
            self.colour = colours.COLOUR_ACTIVE if self.active else colours.COLOUR_INACTIVE
        # Keyboard events
        if event.type == pg.KEYDOWN:
            if self.active:
                # Handle Enter, Backspace, and Ctrl+V for paste
                if event.key == pg.K_RETURN:
                    self.finalText = self.text
                    self.text = ""
                    self.active = False
                    self.colour = colours.COLOUR_INACTIVE
                elif event.key == pg.K_BACKSPACE:
                    self.text = self.text[:-1]
                elif (event.key == pg.K_v) and (event.mod & pg.KMOD_CTRL):
                    try:
                        # Try to get text from the clipboard and append it to the input
                        pg.scrap.init()
                        pg.scrap.set_mode(pg.SCRAP_CLIPBOARD)
                        clipboard = pg.scrap.get("text/plain;charset=utf-8").decode()
                        clipboard = ''.join(char for char in clipboard if char.isprintable())
                        self.text += clipboard
                    except:
                        pass
                else:
                    # Handle regular text input
                    if len(self.text) < self.max or self.max == 0:
                        self.text += event.unicode
                # Update the rendered text surface
                self.textSurface = FONT.render(self.text, True, colours.TEXT_COLOUR)
        # Mouse motion events for hover effect
        elif event.type == pg.MOUSEMOTION and not self.active:
            self.hover = self.rect.collidepoint(event.pos)
            self.colour = colours.COLOUR_HOVER if self.hover else colours.COLOUR_INACTIVE

    # Update the input box width based on text width
    def update(self):
        if not self.rect.w > self.max or self.max == 0:
            width = max(200, self.textSurface.get_width() + 10)
            self.rect.w = width

    # Draw the input box on the screen
    def draw(self, screen):
        # Display prompt if there's no text and a prompt is provided
        if not self.text and self.prompt:
            screen.blit(FONT.render(self.prompt, True, colours.PROMPT_COLOUR), (self.rect.x + 5, self.rect.y + 8))

        # Draw filled or unfilled input box and text
        if self.filled:
            pg.draw.rect(screen, self.colour, self.rect)
            screen.blit(self.textSurface, (self.rect.x + 5, self.rect.y + 8))
        else:
            screen.blit(self.textSurface, (self.rect.x + 5, self.rect.y + 8))
            pg.draw.rect(screen, self.colour, self.rect, 2)

# Define a class for an input slider
class inputSlider:
    def __init__(self, x, y, length=200, height=10, min_value=0, max_value=100, default_value=100):
        # Initialize input slider attributes
        self.rect = pg.Rect(x, y, length, height)
        self.colour = colours.COLOUR_INACTIVE
        self.value = default_value
        self.min_value = min_value
        self.max_value = max_value
        self.knob_radius = height
        self.held = False

    # Handle mouse events for the input slider
    def handleEvent(self, event):
        # Mouse button down event
        if event.type == pg.MOUSEBUTTONDOWN:
            # Check if mouse clicked inside the slider
            if self.rect.collidepoint(event.pos):
                self.held = True
                self.colour = colours.COLOUR_ACTIVE
            else:
                self.held = False
                self.colour = colours.COLOUR_INACTIVE

        # Mouse motion event
        if event.type == pg.MOUSEMOTION:
            # If slider is being held, update the value based on mouse position
            if self.held:
                mouse_x, _ = event.pos
                mouse_x = max(self.rect.x, min(mouse_x, self.rect.x + self.rect.width))
                percent = (mouse_x - self.rect.x) / self.rect.width
                self.value = int(self.min_value + percent * (self.max_value - self.min_value))

        # Mouse button up event
        if event.type == pg.MOUSEBUTTONUP:
            self.held = False
            self.colour = colours.COLOUR_INACTIVE

    # Draw the input slider on the screen
    def draw(self, screen):
        pg.draw.rect(screen, self.colour, self.rect, 2)

        # Calculate knob position based on the value
        knob_x = int(self.rect.x + (self.value - self.min_value) / (self.max_value - self.min_value) * self.rect.width)
        knob_rect = pg.Rect(knob_x - self.knob_radius, self.rect.y - self.knob_radius / 2, 2 * self.knob_radius, 2 * self.knob_radius)
        pg.draw.circle(screen, self.colour, knob_rect.center, self.knob_radius)

    # String representation of the input slider for debugging
    def __str__(self):
        return f"An input slider. Length = {self.rect.width}, height = {self.rect.height}. @({self.rect.x},{self.rect.y})"


# Define a class for a button with an image
class button:
    def __init__(self, x, y, texturePath, action, delay=500):
        # Initialize button attributes
        original_image = pg.image.load(texturePath)
        width, height = original_image.get_width(), original_image.get_height()

        # Scale the image based on the provided scale factor
        scaled_width = int(width * 5)
        scaled_height = int(height * 5)
        self.image = pg.transform.scale(original_image, (scaled_width, scaled_height))

        self.rect = self.image.get_rect(topleft=(x, y))
        self.action = action
        self.delay = delay
        self.last_press_time = 0

    def handleEvent(self):
        # Mouse events
        mouse_pos = pg.mouse.get_pos()
        if pg.mouse.get_pressed()[0]:  # Check if left mouse button is pressed
            # Check if the mouse clicked inside the button and if enough time has passed
            current_time = pg.time.get_ticks()
            if current_time - self.last_press_time > self.delay and self.rect.collidepoint(mouse_pos):
                # Call the action function without arguments
                self.action()
                self.last_press_time = current_time  # Update the last press time

    def draw(self, sc):
        sc.blit(self.image, self.rect)

    def centre(self, screen, xPos=-1, yPos=-1):
        if xPos != -1:
            self.rect.x = xPos - self.rect.width // 2
        elif yPos != -1:
            self.rect.y = yPos - self.rect.height // 2
        else:
            self.rect.x = (screen.get_width() - self.rect.width) // 2
            self.rect.y = (screen.get_height() - self.rect.height) // 2

# ---------- OUTPUT ---------- #
class text:
    def __init__(self, x, y, text="", scale=1, colourOverride = colours.TEXT_COLOUR):
        self.x = x
        self.y = y
        self.text = text
        self.colour = colourOverride
        self.fontSize = 24 * scale

        self.font = pg.font.Font(None, self.fontSize)

        self.textSurface = self.font.render(str(self.text), True, self.colour)

    def updateSurface(self):
        try:
            wrappedText = textwrap.fill(self.text, width=20)
            self.textSurface = self.font.render(wrappedText, True, self.colour)
        except Exception as e:
            print(e)

    def setText(self, text):
        self.text = text
        self.updateSurface()

    def setColour(self, colour):
        self.colour = colour
        self.updateSurface()

    def handleEvent(self, event):
        # Text output doesn't handle any events
        pass

    def draw(self, screen):
        lines = self.wrapTextToFit(self.text, self.font, screen.get_width())

        for i, line in enumerate(lines):
            text_surface = self.font.render(line, True, self.colour)
            y_offset = i * self.font.get_linesize()
            screen.blit(text_surface, (self.x, self.y + y_offset))

    def centre(self, screen, xPos=-1, yPos=-1):
        if xPos != -1:
            self.x = xPos
        elif yPos != -1:
            self.y = yPos
        else:
            self.x = (screen.get_width() - self.textSurface.get_width()) // 2
            self.y = (screen.get_height() - self.textSurface.get_height()) // 2

    @staticmethod
    def wrapTextToFit(text, font, max_width):
        words = text.split(' ')
        lines = []
        current_line = []

        for word in words:
            test_line = ' '.join(current_line + [word])
            width, _ = font.size(test_line)

            if width <= max_width:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]

        lines.append(' '.join(current_line))
        return lines

    def __str__(self):
        return f"A text output. Text: {self.text}. Font size: {self.font_size}. @({self.x},{self.y})"

class progressBar:
    def __init__(self, x, y, width=200, height=20, min_value=0, max_value=100, current_value=50, colour=colours.COLOUR_INACTIVE):
        self.rect = pg.Rect(x, y, width, height)
        self.colour = colour
        self.min_value = min_value
        self.max_value = max_value
        self.current_value = current_value

    def setValue(self, value):
        self.current_value = max(self.min_value, min(value, self.max_value))

    def handleEvent(self, event):
        # No events
        pass

    def draw(self, screen):
        # Draw the progress bar background
        pg.draw.rect(screen, (50, 50, 50), self.rect)
        
        # Calculate the width of the filled portion based on the current value
        fill_width = int((self.current_value - self.min_value) / (self.max_value - self.min_value) * self.rect.width)
        fill_rect = pg.Rect(self.rect.x, self.rect.y, fill_width, self.rect.height)
        
        # Draw the filled portion
        pg.draw.rect(screen, self.colour, fill_rect)

        # Draw the border
        pg.draw.rect(screen, colours.COLOUR_ACTIVE, self.rect, 2)

    def __str__(self):
        return f"A progress bar. Width = {self.rect.width}, height = {self.rect.height}. @({self.rect.x},{self.rect.y})"