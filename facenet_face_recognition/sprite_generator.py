"""
Ref: https://minzkraut.com/2016/11/23/making-a-simple-spritesheet-generator-in-python/
"""
from PIL import Image
import os, math
# import time

def make_sprite(filenames, destpath):
    number = len(filenames)
    max_frames_row = math.ceil(math.sqrt(number))
    frames = []
    tile_width = 0
    tile_height = 0

    spritesheet_width = 0
    spritesheet_height = 0


    for current_file in filenames :
        try:
            with Image.open(current_file) as im :
                frames.append(im.getdata())
        except:
            print(current_file + " is not a valid image")

    tile_width = frames[0].size[0]
    tile_height = frames[0].size[1]

    if len(frames) > max_frames_row :
        spritesheet_width = tile_width * max_frames_row
        # required_rows = math.ceil(len(frames)/max_frames_row)
        spritesheet_height = tile_height * max_frames_row
    else:
        spritesheet_width = tile_width*len(frames)
        spritesheet_height = tile_height
        
    print(spritesheet_height)
    print(spritesheet_width)

    spritesheet = Image.new("RGBA",(int(spritesheet_width), int(spritesheet_height)))

    for current_frame in frames :
        top = tile_height * math.floor((frames.index(current_frame))/max_frames_row)
        left = tile_width * (frames.index(current_frame) % max_frames_row)
        bottom = top + tile_height
        right = left + tile_width
        
        box = (left,top,right,bottom)
        box = [int(i) for i in box]
        cut_frame = current_frame.crop((0,0,tile_width,tile_height))
        
        spritesheet.paste(cut_frame, box)
        
    # time.strftime("%Y-%m-%dT%H-%M-%S")
    spritesheet.save(os.path.join(destpath, "casia_test_sprite.png"), "PNG")



# if __name__ == '__main__':
#     from model.input_fn import test_datas
#     filenames, filelabels = test_datas("./data/250x250_CASIA/")
#     make_sprite(filenames, "./experiments")