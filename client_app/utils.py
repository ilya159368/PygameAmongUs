import pygame


def colorize(image, newColor):
    image = image.copy()
    image = image.convert_alpha()
    image.fill((0, 0, 0, 255), None, pygame.BLEND_RGBA_MULT)
    image.fill(newColor[0:3] + (0,), None, pygame.BLEND_RGBA_ADD)
    return image


def changeColor(image, color):
    colouredImage = pygame.Surface(image.get_size())
    colouredImage.fill(color)

    finalImage = image.copy()
    finalImage.blit(colouredImage, (0, 0), special_flags=pygame.BLEND_MULT)
    return finalImage
