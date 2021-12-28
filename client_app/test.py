from utils import *
# images/Player - Among Us/Individual Sprites/Walk/walkcolor0005.png
image = Image.open('images/amogus.png')
i1 = color_to_alpha(image, (0, 0, 0, 255))
background = Image.new('RGBA', i1.size, (0, 255, 0, 0))
background.paste(image.convert('RGBA'), mask=i1)

# background.show()
# image.show()
i1.show()
# i2.show()
# i3.show()