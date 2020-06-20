from PIL import Image


def scale_to_discord_icon(img: Image.Image):
    """
    Discord icons are recommended to be 512x512 pixel. This function will rescale them until at least one side is scaled to 512 pixel.
    The pictures aspect ratio will stay the same
    """
    maxpix = 512

    rawheight = img.height
    rawwidth = img.width

    if rawheight > rawwidth:
        ratio = float(maxpix) / float(rawheight)
        pass
    else:
        ratio = float(maxpix) / float(rawwidth)
        pass

    newheight = int(rawheight * ratio)
    newwidth = int(rawwidth * ratio)

    return img.resize((newwidth, newheight), Image.ANTIALIAS)
