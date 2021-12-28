import pygame
from PIL import Image, ImageMath


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


def difference1(source, color):
    """When source is bigger than color"""
    return (source - color) / (255.0 - color)


def difference2(source, color):
    """When color is bigger than source"""
    return (color - source) / color


def color_to_alpha(image: Image, color=None):
    image = image.convert('RGBA')
    width, height = image.size

    color = list(map(float, color))
    # new_color = list(map(float, new_color))
    img_bands = [band.convert("F") for band in image.split()]

    # Find the maximum difference rate between source and color. I had to use two
    # difference functions because ImageMath.eval only evaluates the expression
    # once.
    alpha = ImageMath.eval(
        """float(
            max(
                max(
                    max(
                        difference1(red_band, cred_band),
                        difference1(green_band, cgreen_band)
                    ),
                    difference1(blue_band, cblue_band)
                ),
                max(
                    max(
                        difference2(red_band, cred_band),
                        difference2(green_band, cgreen_band)
                    ),
                    difference2(blue_band, cblue_band)
                )
            )
        )""",
        difference1=difference1,
        difference2=difference2,
        red_band=img_bands[0],
        green_band=img_bands[1],
        blue_band=img_bands[2],
        cred_band=color[0],
        cgreen_band=color[1],
        cblue_band=color[2]
    )

    # Calculate the new image colors after the removal of the selected color
    new_bands1 = [
        ImageMath.eval(
            "convert((image - color) / alpha + color, 'L')",
            image=img_bands[i],
            color=color[i],
            alpha=alpha
        )
        for i in range(3)
    ]
    # new_bands2 = [
    #     ImageMath.eval(
    #         "convert((image - color) / alpha + new_color, 'L')",
    #         image=img_bands[i],
    #         color=color[i],
    #         alpha=alpha,
    #         new_color=new_color[i]
    #     )
    #     for i in range(3)
    # ]
    # new_bands3 = [
    #     ImageMath.eval(
    #         "convert(image, 'L')",
    #         image=img_bands[i],
    #         color=color[i],
    #         alpha=alpha
    #     )
    #     for i in range(3)
    # ]
    # # my code
    # new_bands1[1] = ImageMath.eval(
    #     "convert(image - ), 'L')",
    #     image=img_bands[0],
    #     color=new_color[0],
    #     alpha=alpha
    # )
    # Add the new alpha band
    new_bands1.append(ImageMath.eval(
        "convert(alpha_band, 'L')",
        alpha=alpha,
        alpha_band=img_bands[3]
    ))
    # new_bands2.append(ImageMath.eval(
    #     "convert(alpha_band, 'L')",
    #     alpha=alpha,
    #     alpha_band=img_bands[3]
    # ))
    # new_bands3.append(ImageMath.eval(
    #     "convert(alpha_band * alpha, 'L')",
    #     alpha=alpha,
    #     alpha_band=img_bands[3]
    # ))

    return Image.merge('RGBA', new_bands1)
