from PIL import Image
import os
from constants import *
from facenet_face_recognition import whoisit
from game.utils import *
import time
import imageio
from database import dbop

class PhotoLogic():

    def __init__(self, game_state_list, player_id_list):
        self.game_state_list = game_state_list
        self.player_id_list = player_id_list
        self.player_id_list[0] = INVALID_USER
        self.fr_who = whoisit.FRWhoIsIt()

    def set_game_state(self, state, desc):
        if self.game_state_list[0] != state:
            self.game_state_list[0] = state
            print("change game state to: ", state, "by ", desc)

    def resize_screenshot(self, source_path, dest_path):
        image = Image.open(source_path)
        # crop
        width, height = image.size   # Get dimensions

        left = (width - height)/2
        top = (height - height)/2
        right = (width + height)/2
        bottom = (height + height)/2

        image = image.crop((left, top, right, bottom))
        
        # resize
        size = (TARGET_IMAGE_WIDTH, TARGET_IMAGE_HEIGHT)
        image.thumbnail(size, Image.ANTIALIAS)
        image.save(dest_path, "JPEG")

    def save_and_resize(self, width, height, photo):
        # write to temporary folder
        photo_path = os.path.join(RESOURCE_TEMP_PATH, str(time.time()))
        photo = photo.reshape([height, width, 3])
        imageio.imsave(photo_path + ".jpg", photo)
        # resize image
        resized_photo_path = photo_path + "_resize"
        self.resize_screenshot(photo_path + ".jpg", resized_photo_path + ".jpg")
        return resized_photo_path + ".jpg"

    def move_to_user_folder(self, photo_path, id):
        if not os.path.exists(RESOURCE_USER_IMAGE_PATH + str(id)):
            os.makedirs(RESOURCE_USER_IMAGE_PATH + str(id))
        dest_path = os.path.join(RESOURCE_USER_IMAGE_PATH + str(id), str(time.time()) + ".jpg")
        os.rename(photo_path, dest_path)

    def face_recognition(self, width, height, photo, isfinish):
        if isfinish:
            self.set_game_state(STATE_PLAY, "face_recognition")

        print(len(photo))
        assert len(photo) == width * height * 3

        if photo is None:
            self.set_game_state(STATE_SHUTDOWN, "face_recognition")
            print("empty")
            return

        if self.player_id_list[0] != INVALID_USER:
            print("we already know")
            photo_path = self.save_and_resize(width, height, photo)
            self.move_to_user_folder(photo_path, self.player_id_list[0])
            return

        photo_path = self.save_and_resize(width, height, photo)

        all_users = dbop.get_all_user()

        min_dist, id, img_encoding = self.fr_who.who_is_it(photo_path, all_users)
        if id is None:
            # add new user
            id = dbop.add_user(img_encoding)
            print("add new user", id)
            
        self.player_id_list[0] = id
        # move to player folder
        self.move_to_user_folder(photo_path, id)
        print("player_id", self.player_id_list[0])

        
