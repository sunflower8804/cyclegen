import pygame.transform
import pygame_gui.elements
from random import choice, randint
import ujson
import math

from scripts.cat.history import History
from scripts.event_class import Single_Event

from .Screens import Screens
from scripts.utility import get_personality_compatibility, get_text_box_theme, scale, scale_dimentions, shorten_text_to_fit
from scripts.cat.cats import Cat
from scripts.game_structure import image_cache
from scripts.cat.pelts import Pelt
from scripts.game_structure.windows import GameOver, PickPath, DeathScreen
from scripts.game_structure.game_essentials import game, screen, screen_x, screen_y, MANAGER
from scripts.game_structure.windows import RelationshipLog
from scripts.game_structure.propagating_thread import PropagatingThread
from scripts.game_structure.ui_elements import UIImageButton, UITextBoxTweaked, UISpriteButton
from scripts.cat.sprites import sprites

with open(f"resources/dicts/acc_display.json", "r") as read_file:
    ACC_DISPLAY = ujson.loads(read_file.read())

class GiftScreen(Screens):
    selected_cat = None
    current_page = 1
    list_frame = pygame.transform.scale(image_cache.load_image("resources/images/choosing_frame.png").convert_alpha(),
                                        (1300 / 1600 * screen_x, 452 / 1400 * screen_y))
    apprentice_details = {}
    selected_details = {}
    cat_list_buttons = {}
    stage = 'choose murder cat'

    def __init__(self, name=None):
        super().__init__(name)
        self.list_page = None
        self.next_cat = None
        self.previous_cat = None
        self.next_page_button = None
        self.previous_page_button = None
        self.current_mentor_warning = None
        self.confirm_mentor = None
        self.back_button = None
        self.next_cat_button = None
        self.previous_cat_button = None
        self.mentor_icon = None
        self.app_frame = None
        self.mentor_frame = None
        self.current_mentor_text = None
        self.info = None
        self.heading = None
        self.mentor = None
        self.the_cat = None
        self.murder_cat = None
        self.next = None
        self.murderimg = None
        self.page = 0
        self.max_pages = 1
        self.search_bar_image = None
        self.search_bar = None
        self.previous_page_button = None
        self.next_page_button = None
        self.accessory_tab_button = None
        self.previous_search_text = "search"
        self.cat_list_buttons = {}
        self.search_inventory = []
        self.accessory_buttons = {}
        self.selected_accessory = None
        self.cat_sprite = None
        
    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element in self.cat_list_buttons.values():
                self.selected_cat = event.ui_element.return_cat_object()
                self.update_selected_cat()
            
            elif event.ui_element in self.accessory_buttons.values():
                self.selected_accessory = event.ui_element
                self.update_selected_cat2()

            elif event.ui_element == self.confirm_mentor and self.selected_cat and self.stage == 'choose murder cat':
                if not self.selected_cat.dead:
                    self.exit_screen()
                    self.update_selected_cat()
                    self.stage = 'choose accomplice'
                    self.screen_switches()
            
            elif event.ui_element == self.confirm_mentor and self.selected_accessory:             
                    self.change_cat(self.murder_cat, self.selected_cat)
                    self.stage = 'choose murder cat'

            elif event.ui_element == self.back_button:
                self.change_screen('profile screen')
                self.stage = 'choose murder cat'

            elif event.ui_element == self.next_cat_button:
                if isinstance(Cat.fetch_cat(self.next_cat), Cat):
                    game.switches['cat'] = self.next_cat
                    self.update_cat_list()
                    self.update_selected_cat()
                else:
                    print("invalid next cat", self.next_cat)
            elif event.ui_element == self.previous_cat_button:
                if isinstance(Cat.fetch_cat(self.previous_cat), Cat):
                    game.switches['cat'] = self.previous_cat
                    self.update_cat_list()
                    self.update_selected_cat()
                else:
                    print("invalid previous cat", self.previous_cat)
            elif event.ui_element == self.next_page_button:
                if self.stage == "choose murder cat":
                    self.current_page += 1
                    self.update_cat_list()
                elif self.stage == "choose accomplice":
                    self.page += 1
                    
                    if self.page == 0 and self.max_pages in [0, 1]:
                        self.previous_page_button.disable()
                        self.next_page_button.disable()
                    elif self.page == 0:
                        self.previous_page_button.disable()
                        self.next_page_button.enable()
                    elif self.page == self.max_pages - 1:
                        self.previous_page_button.enable()
                        self.next_page_button.disable()
                    else:
                        self.previous_page_button.enable()
                        self.next_page_button.enable()
                    for i in self.cat_list_buttons:
                        self.cat_list_buttons[i].kill()
                    for i in self.accessory_buttons:
                        self.accessory_buttons[i].kill()
                    self.update_cat_list2()
            elif event.ui_element == self.previous_page_button:
                if self.stage == "choose murder cat":
                    self.current_page -= 1
                    self.update_cat_list()

                elif self.stage == "choose accomplice":
                    self.page -= 1
                    if self.page == 0 and self.max_pages in [0, 1]:
                        self.previous_page_button.disable()
                        self.next_page_button.disable()
                    elif self.page == 0:
                        self.previous_page_button.disable()
                        self.next_page_button.enable()
                    elif self.page == self.max_pages - 1:
                        self.previous_page_button.enable()
                        self.next_page_button.disable()
                    else:
                        self.previous_page_button.enable()
                        self.next_page_button.enable()
                    for i in self.cat_list_buttons:
                        self.cat_list_buttons[i].kill()
                    for i in self.accessory_buttons:
                        self.accessory_buttons[i].kill()
                    self.update_cat_list2()

    def screen_switches(self):

        if self.stage == 'choose murder cat':
            self.the_cat = game.clan.your_cat
            self.selected_cat = None
            self.selected_accessory = None

            self.heading = pygame_gui.elements.UITextBox("Choose who to gift",
                                                        scale(pygame.Rect((300, 50), (1000, 80))),
                                                        object_id=get_text_box_theme("#text_box_34_horizcenter"),
                                                        manager=MANAGER)
            
            # Layout Images:
            self.mentor_frame = pygame_gui.elements.UIImage(scale(pygame.Rect((200, 226), (569, 399))),
                                                            pygame.transform.scale(
                                                                image_cache.load_image(
                                                                "resources/images/choosing_cat1_frame_ment.png").convert_alpha(),
                                                                (569, 399)), manager=MANAGER)
            self.murderimg = pygame_gui.elements.UIImage(scale(pygame.Rect((850, 150), (446, 494))),
                                                            pygame.transform.scale(
                                                                image_cache.load_image(
                                                                    "resources/images/choose_victim.png").convert_alpha(),
                                                                (446, 494)), manager=MANAGER)
    
            
            self.back_button = UIImageButton(scale(pygame.Rect((50, 1290), (210, 60))), "", object_id="#back_button")
            self.confirm_mentor = UIImageButton(scale(pygame.Rect((270, 610), (208, 52))), "",
                                                object_id="#patrol_select_button")
        
            self.previous_page_button = UIImageButton(scale(pygame.Rect((630, 1155), (68, 68))), "",
                                                    object_id="#relation_list_previous", manager=MANAGER)
            self.next_page_button = UIImageButton(scale(pygame.Rect((902, 1155), (68, 68))), "",
                                                object_id="#relation_list_next", manager=MANAGER)

            self.update_selected_cat()  # Updates the image and details of selected cat
            self.update_cat_list()
        else:
            self.the_cat = game.clan.your_cat

            self.heading = pygame_gui.elements.UITextBox("Choose what to gift",
                                                        scale(pygame.Rect((300, 50), (1000, 80))),
                                                        object_id=get_text_box_theme("#text_box_34_horizcenter"),
                                                        manager=MANAGER)
            
            # Layout Images:
            self.mentor_frame = pygame_gui.elements.UIImage(scale(pygame.Rect((200, 226), (569, 399))),
                                                            pygame.transform.scale(
                                                                image_cache.load_image(
                                                                    "resources/images/choosing_cat1_frame_ment.png").convert_alpha(),
                                                                (569, 399)), manager=MANAGER)

            
            self.murderimg = pygame_gui.elements.UIImage(scale(pygame.Rect((850, 150), (446, 494))),
                                                            pygame.transform.scale(
                                                                image_cache.load_image(
                                                                    "resources/images/proceed_accomplice.png").convert_alpha(),
                                                                (446, 494)), manager=MANAGER)

            self.back_button = UIImageButton(scale(pygame.Rect((50, 1290), (210, 60))), "", object_id="#back_button")
            self.confirm_mentor = UIImageButton(scale(pygame.Rect((270, 610), (208, 52))), "",
                                                object_id="#patrol_select_button")
        
            self.previous_page_button = UIImageButton(scale(pygame.Rect((630, 1155), (68, 68))), "",
                                                    object_id="#relation_list_previous", manager=MANAGER)
            self.next_page_button = UIImageButton(scale(pygame.Rect((902, 1155), (68, 68))), "",
                                                object_id="#relation_list_next", manager=MANAGER)


            self.search_bar_image = pygame_gui.elements.UIImage(scale(pygame.Rect((219, 680), (236, 68))),
                                                            pygame.image.load(
                                                                "resources/images/search_bar.png").convert_alpha(),
                                                            manager=MANAGER)
            self.search_bar = pygame_gui.elements.UITextEntryLine(scale(pygame.Rect((239, 685), (205, 55))),
                                                            object_id="#search_entry_box",
                                                            initial_text="search",
                                                            manager=MANAGER)

            self.update_selected_cat2()  # Updates the image and details of selected cat
            self.update_cat_list2()


    def exit_screen(self):
        self.selected_accessory = None
        self.previous_search_text = "search"
        self.cat_sprite = None

        for ele in self.cat_list_buttons:
            self.cat_list_buttons[ele].kill()
        self.cat_list_buttons = {}

        for ele in self.apprentice_details:
            self.apprentice_details[ele].kill()
        self.apprentice_details = {}

        for ele in self.selected_details:
            self.selected_details[ele].kill()
        self.selected_details = {}

        for ele in self.accessory_buttons:
            self.accessory_buttons[ele].kill()
        self.accessory_buttons = {}
        
        if self.heading:
            self.heading.kill()
            del self.heading
        
        if self.murderimg:
            self.murderimg.kill()
            del self.murderimg

        if self.mentor_frame:
            self.mentor_frame.kill()
            del self.mentor_frame

        if self.back_button:
            self.back_button.kill()
            del self.back_button
        if self.confirm_mentor:
            self.confirm_mentor.kill()
            del self.confirm_mentor
        if self.previous_page_button:
            self.previous_page_button.kill()
            del self.previous_page_button
            
        if self.next_page_button:
            self.next_page_button.kill()
            del self.next_page_button
        
        if self.search_bar_image:
            self.search_bar_image.kill()
        
        if self.search_bar:
            self.search_bar.kill()

        if self.next:
            self.next.kill()
            del self.next

    def find_next_previous_cats(self):
        """Determines where the previous and next buttons lead"""
        is_instructor = False
        if self.the_cat.dead and game.clan.instructor.ID == self.the_cat.ID:
            is_instructor = True

        self.previous_cat = 0
        self.next_cat = 0
        if self.the_cat.dead and not is_instructor and not self.the_cat.df:
            self.previous_cat = game.clan.instructor.ID

        if is_instructor:
            self.next_cat = 1

        for check_cat in Cat.all_cats_list:
            if check_cat.ID == self.the_cat.ID:
                self.next_cat = 1

            if self.next_cat == 0 and check_cat.ID != self.the_cat.ID and check_cat.dead == self.the_cat.dead and \
                    check_cat.ID != game.clan.instructor.ID and not check_cat.exiled and check_cat.status in \
                    ["apprentice", "medicine cat apprentice", "mediator apprentice", "queen's apprentice"] \
                    and check_cat.df == self.the_cat.df:
                self.previous_cat = check_cat.ID

            elif self.next_cat == 1 and check_cat.ID != self.the_cat.ID and check_cat.dead == self.the_cat.dead and \
                    check_cat.ID != game.clan.instructor.ID and not check_cat.exiled and check_cat.status in \
                    ["apprentice", "medicine cat apprentice", "mediator apprentice", "queen's apprentice"] \
                    and check_cat.df == self.the_cat.df:
                self.next_cat = check_cat.ID

            elif int(self.next_cat) > 1:
                break

        if self.next_cat == 1:
            self.next_cat = 0

    def change_cat(self, new_mentor=None, accomplice=None, accompliced=None):
        game.clan.your_cat.pelt.inventory.remove(self.selected_accessory.tool_tip_text)
        if self.selected_accessory.tool_tip_text in game.clan.your_cat.pelt.accessories:
            game.clan.your_cat.pelt.accessories.remove(self.selected_accessory.tool_tip_text)
        if self.selected_accessory.tool_tip_text == game.clan.your_cat.pelt.accessory:
            game.clan.your_cat.pelt.accessory = None
        self.selected_cat.pelt.inventory.append(self.selected_accessory.tool_tip_text)
        
        self.exit_screen()
        game.switches['cur_screen'] = "events screen"
    
    
    def update_selected_cat(self):
        """Updates the image and information on the currently selected mentor"""
        for ele in self.selected_details:
            self.selected_details[ele].kill()
        self.selected_details = {}
        if self.selected_cat:

            self.selected_details["selected_image"] = pygame_gui.elements.UIImage(
                scale(pygame.Rect((233, 310), (270, 270))),
                pygame.transform.scale(
                    self.selected_cat.sprite,
                    (270, 270)), manager=MANAGER)

            info = self.selected_cat.status + "\n" + \
                self.selected_cat.genderalign + "\n" + self.selected_cat.personality.trait + "\n"

            if self.selected_cat.moons < 1:
                info += "???"
            else:
                info += self.selected_cat.skills.skill_string(short=True)
            
            self.selected_details["selected_info"] = pygame_gui.elements.UITextBox(info,
                                                                                scale(pygame.Rect((540, 325),
                                                                                                    (210, 250))),
                                                                                object_id="#text_box_22_horizcenter_vertcenter_spacing_95",
                                                                                manager=MANAGER)

            name = str(self.selected_cat.name)  # get name
            if 11 <= len(name):  # check name length
                short_name = str(name)[0:9]
                name = short_name + '...'
            self.selected_details["victim_name"] = pygame_gui.elements.ui_label.UILabel(
                scale(pygame.Rect((260, 230), (220, 60))),
                name,
                object_id="#text_box_34_horizcenter", manager=MANAGER)
            
                    
    def update_selected_cat2(self):
        """Updates the image and information on the currently selected mentor"""
        for ele in self.selected_details:
            self.selected_details[ele].kill()

        self.selected_details = {}
        if self.selected_accessory:
            cat = game.clan.your_cat
            accessory = self.selected_accessory.tool_tip_text
            
            if accessory in cat.pelt.plant_accessories:
                self.selected_details["selected_image"] = pygame_gui.elements.UIImage(scale(pygame.Rect((240, 250), (300, 300))), pygame.transform.scale(sprites.sprites['acc_herbs' + accessory + self.cat_sprite], (300,300)), manager=MANAGER)
            elif accessory in cat.pelt.wild_accessories:
                self.selected_details["selected_image"] = pygame_gui.elements.UIImage(scale(pygame.Rect((240, 250), (300, 300))), pygame.transform.scale(sprites.sprites['acc_wild' + accessory + self.cat_sprite], (300,300)), manager=MANAGER)
            elif accessory in cat.pelt.collars:
                self.selected_details["selected_image"] = pygame_gui.elements.UIImage(scale(pygame.Rect((240, 250), (300, 300))), pygame.transform.scale(sprites.sprites['collars' + accessory + self.cat_sprite], (300,300)), manager=MANAGER)
            elif accessory in cat.pelt.flower_accessories:
                self.selected_details["selected_image"] = pygame_gui.elements.UIImage(scale(pygame.Rect((240, 250), (300, 300))), pygame.transform.scale(sprites.sprites['acc_flower' + accessory + self.cat_sprite], (300,300)), manager=MANAGER)
            elif accessory in cat.pelt.plant2_accessories:
                self.selected_details["selected_image"] = pygame_gui.elements.UIImage(scale(pygame.Rect((240, 250), (300, 300))), pygame.transform.scale(sprites.sprites['acc_plant2' + accessory + self.cat_sprite], (300,300)), manager=MANAGER)
            elif accessory in cat.pelt.snake_accessories:
                self.selected_details["selected_image"] = pygame_gui.elements.UIImage(scale(pygame.Rect((240, 250), (300, 300))), pygame.transform.scale(sprites.sprites['acc_snake' + accessory + self.cat_sprite], (300,300)), manager=MANAGER)
            elif accessory in cat.pelt.smallAnimal_accessories:
                self.selected_details["selected_image"] = pygame_gui.elements.UIImage(scale(pygame.Rect((240, 250), (300, 300))), pygame.transform.scale(sprites.sprites['acc_smallAnimal' + accessory + self.cat_sprite], (300,300)), manager=MANAGER)
            elif accessory in cat.pelt.deadInsect_accessories:
                self.selected_details["selected_image"] = pygame_gui.elements.UIImage(scale(pygame.Rect((240, 250), (300, 300))), pygame.transform.scale(sprites.sprites['acc_deadInsect' + accessory + self.cat_sprite], (300,300)), manager=MANAGER)
            elif accessory in cat.pelt.aliveInsect_accessories:
                self.selected_details["selected_image"] = pygame_gui.elements.UIImage(scale(pygame.Rect((240, 250), (300, 300))), pygame.transform.scale(sprites.sprites['acc_aliveInsect' + accessory + self.cat_sprite], (300,300)), manager=MANAGER)
            elif accessory in cat.pelt.fruit_accessories:
                self.selected_details["selected_image"] = pygame_gui.elements.UIImage(scale(pygame.Rect((240, 250), (300, 300))), pygame.transform.scale(sprites.sprites['acc_fruit' + accessory + self.cat_sprite], (300,300)), manager=MANAGER)
            elif accessory in cat.pelt.crafted_accessories:
                self.selected_details["selected_image"] = pygame_gui.elements.UIImage(scale(pygame.Rect((240, 250), (300, 300))), pygame.transform.scale(sprites.sprites['acc_crafted' + accessory + self.cat_sprite], (300,300)), manager=MANAGER)
            elif accessory in cat.pelt.tail2_accessories:
                self.selected_details["selected_image"] = pygame_gui.elements.UIImage(scale(pygame.Rect((240, 250), (300, 300))), pygame.transform.scale(sprites.sprites['acc_tail2' + accessory + self.cat_sprite], (300,300)), manager=MANAGER)

            info = ACC_DISPLAY[self.selected_accessory.tool_tip_text]["default"]

            if self.selected_accessory.tool_tip_text in game.clan.your_cat.pelt.accessories:
                info += "\nCurrently worn"
            
            self.selected_details["selected_info"] = pygame_gui.elements.UITextBox(info,
                                                                                scale(pygame.Rect((540, 325),
                                                                                                    (210, 250))),
                                                                                object_id="#text_box_22_horizcenter_vertcenter_spacing_95",
                                                                                manager=MANAGER)

            self.selected_details["mentor_name"] = pygame_gui.elements.ui_label.UILabel(
                scale(pygame.Rect((260, 230), (220, 60))),
                "Gift",
                object_id="#text_box_34_horizcenter", manager=MANAGER)
            

    def update_cat_list(self):
        """Updates the cat sprite buttons. """
        valid_mentors = self.chunks(self.get_valid_cats(), 30)

        # If the number of pages becomes smaller than the number of our current page, set
        #   the current page to the last page
        if self.current_page > len(valid_mentors):
            self.list_page = len(valid_mentors)

        # Handle which next buttons are clickable.
        if len(valid_mentors) <= 1:
            self.previous_page_button.disable()
            self.next_page_button.disable()
        elif self.current_page >= len(valid_mentors):
            self.previous_page_button.enable()
            self.next_page_button.disable()
        elif self.current_page == 1 and len(valid_mentors) > 1:
            self.previous_page_button.disable()
            self.next_page_button.enable()
        else:
            self.previous_page_button.enable()
            self.next_page_button.enable()
        display_cats = []
        if valid_mentors:
            display_cats = valid_mentors[self.current_page - 1]

        # Kill all the currently displayed cats.
        for ele in self.cat_list_buttons:
            self.cat_list_buttons[ele].kill()
        self.cat_list_buttons = {}

        pos_x = 0
        pos_y = 40
        i = 0
        for cat in display_cats:
            self.cat_list_buttons["cat" + str(i)] = UISpriteButton(
                scale(pygame.Rect((200 + pos_x, 730 + pos_y), (100, 100))),
                cat.sprite, cat_object=cat, manager=MANAGER)
            pos_x += 120
            if pos_x >= 1100:
                pos_x = 0
                pos_y += 120
            i += 1
            
    def update_cat_list2(self):
        """Updates the cat sprite buttons. """
        cat = self.the_cat
        age = cat.age
        self.cat_sprite = str(cat.pelt.cat_sprites[cat.age])

        # setting the cat_sprite (bc this makes things much easier)
        if cat.not_working() and age != 'newborn' and game.config['cat_sprites']['sick_sprites']:
            if age in ['kitten', 'adolescent']:
                self.cat_sprite = str(19)
            else:
                self.cat_sprite = str(18)
        elif cat.pelt.paralyzed and age != 'newborn':
            if age in ['kitten', 'adolescent']:
                self.cat_sprite = str(17)
            else:
                if cat.pelt.length == 'long':
                    self.cat_sprite = str(16)
                else:
                    self.cat_sprite = str(15)
        else:
            if age == 'elder' and not game.config['fun']['all_cats_are_newborn']:
                age = 'senior'

            if game.config['fun']['all_cats_are_newborn']:
                self.cat_sprite = str(cat.pelt.cat_sprites['newborn'])
            else:
                self.cat_sprite = str(cat.pelt.cat_sprites[age])

        pos_x = 20
        pos_y = 250
        i = 0

        self.cat_list_buttons = {}
        self.accessory_buttons = {}
        self.accessories_list = []
        start_index = self.page * 30
        end_index = start_index + 30

        if cat.pelt.accessory:
            if cat.pelt.accessory not in cat.pelt.inventory:
                cat.pelt.inventory.append(cat.pelt.accessory)

        for acc in cat.pelt.accessories:
            if acc not in cat.pelt.inventory:
                cat.pelt.inventory.append(acc)

        inventory_len = 0
        new_inv = []
        if self.search_bar.get_text() in ["", "search"]:
            inventory_len = len(cat.pelt.inventory)
            new_inv = cat.pelt.inventory
        else:
            for ac in cat.pelt.inventory:
                if self.search_bar.get_text().lower() in ac.lower():
                    inventory_len+=1
                    new_inv.append(ac)
        self.max_pages = math.ceil(inventory_len/30)
        
        if (self.max_pages == 1 or self.max_pages == 0):
            self.previous_page_button.disable()
            self.next_page_button.disable()
        if self.page == 0:
            self.previous_page_button.disable()
        if cat.pelt.inventory:
            for a, accessory in enumerate(new_inv[start_index:min(end_index, inventory_len)], start = start_index):
                try:
                    if self.search_bar.get_text() in ["", "search"] or self.search_bar.get_text().lower() in accessory.lower():
                        self.accessory_buttons[str(i)] = UIImageButton(scale(pygame.Rect((200 + pos_x, 500 + pos_y), (100, 100))), "", tool_tip_text=accessory, object_id="#blank_button")
                        if accessory in cat.pelt.plant_accessories:
                            self.cat_list_buttons["cat" + str(i)] = pygame_gui.elements.UIImage(scale(pygame.Rect((200 + pos_x, 500 + pos_y), (100, 100))), sprites.sprites['acc_herbs' + accessory + self.cat_sprite], manager=MANAGER)
                        elif accessory in cat.pelt.wild_accessories:
                            self.cat_list_buttons["cat" + str(i)] = pygame_gui.elements.UIImage(scale(pygame.Rect((200 + pos_x, 500 + pos_y), (100, 100))), sprites.sprites['acc_wild' + accessory + self.cat_sprite], manager=MANAGER)
                        elif accessory in cat.pelt.collars:
                            self.cat_list_buttons["cat" + str(i)] = pygame_gui.elements.UIImage(scale(pygame.Rect((200 + pos_x, 500 + pos_y), (100, 100))), sprites.sprites['collars' + accessory + self.cat_sprite], manager=MANAGER)
                        elif accessory in cat.pelt.flower_accessories:
                            self.cat_list_buttons["cat" + str(i)] = pygame_gui.elements.UIImage(scale(pygame.Rect((200 + pos_x, 500 + pos_y), (100, 100))), sprites.sprites['acc_flower' + accessory + self.cat_sprite], manager=MANAGER)
                        elif accessory in cat.pelt.plant2_accessories:
                            self.cat_list_buttons["cat" + str(i)] = pygame_gui.elements.UIImage(scale(pygame.Rect((200 + pos_x, 500 + pos_y), (100, 100))), sprites.sprites['acc_plant2' + accessory + self.cat_sprite], manager=MANAGER)
                        elif accessory in cat.pelt.snake_accessories:
                            self.cat_list_buttons["cat" + str(i)] = pygame_gui.elements.UIImage(scale(pygame.Rect((200 + pos_x, 500 + pos_y), (100, 100))), sprites.sprites['acc_snake' + accessory + self.cat_sprite], manager=MANAGER)
                        elif accessory in cat.pelt.smallAnimal_accessories:
                            self.cat_list_buttons["cat" + str(i)] = pygame_gui.elements.UIImage(scale(pygame.Rect((200 + pos_x, 500 + pos_y), (100, 100))), sprites.sprites['acc_smallAnimal' + accessory + self.cat_sprite], manager=MANAGER)
                        elif accessory in cat.pelt.deadInsect_accessories:
                            self.cat_list_buttons["cat" + str(i)] = pygame_gui.elements.UIImage(scale(pygame.Rect((200 + pos_x, 500 + pos_y), (100, 100))), sprites.sprites['acc_deadInsect' + accessory + self.cat_sprite], manager=MANAGER)
                        elif accessory in cat.pelt.aliveInsect_accessories:
                            self.cat_list_buttons["cat" + str(i)] = pygame_gui.elements.UIImage(scale(pygame.Rect((200 + pos_x, 500 + pos_y), (100, 100))), sprites.sprites['acc_aliveInsect' + accessory + self.cat_sprite], manager=MANAGER)
                        elif accessory in cat.pelt.fruit_accessories:
                            self.cat_list_buttons["cat" + str(i)] = pygame_gui.elements.UIImage(scale(pygame.Rect((200 + pos_x, 500 + pos_y), (100, 100))), sprites.sprites['acc_fruit' + accessory + self.cat_sprite], manager=MANAGER)
                        elif accessory in cat.pelt.crafted_accessories:
                            self.cat_list_buttons["cat" + str(i)] = pygame_gui.elements.UIImage(scale(pygame.Rect((200 + pos_x, 500 + pos_y), (100, 100))), sprites.sprites['acc_crafted' + accessory + self.cat_sprite], manager=MANAGER)
                        elif accessory in cat.pelt.tail2_accessories:
                            self.cat_list_buttons["cat" + str(i)] = pygame_gui.elements.UIImage(scale(pygame.Rect((200 + pos_x, 500 + pos_y), (100, 100))), sprites.sprites['acc_tail2' + accessory + self.cat_sprite], manager=MANAGER)
                        self.accessories_list.append(accessory)
                        pos_x += 120
                        if pos_x >= 1200:
                            pos_x = 0
                            pos_y += 120
                        i += 1
                except:
                    continue

    def get_valid_cats(self):
        valid_mentors = []

        for cat in Cat.all_cats_list:
            if not cat.dead and not cat.outside and not cat.ID == game.clan.your_cat.ID and not cat.moons == 0:
                valid_mentors.append(cat)
        
        return valid_mentors

    def on_use(self):
        # Due to a bug in pygame, any image with buttons over it must be blited
        screen.blit(self.list_frame, (150 / 1600 * screen_x, 720 / 1400 * screen_y))
        if self.search_bar:
            if self.search_bar.is_focused and self.search_bar.get_text() == "search":
                self.search_bar.set_text("")
                self.page = 0
                if self.page == 0 and (self.max_pages == 1 or self.max_pages == 0):
                    self.previous_page_button.disable()
                    self.next_page_button.disable()
                elif self.page == 0:
                    self.previous_page_button.disable()
                    self.next_page_button.enable()
                elif self.page == self.max_pages - 1:
                    self.previous_page_button.enable()
                    self.next_page_button.disable()
                else:
                    self.previous_page_button.enable()
                    self.next_page_button.enable()
            elif self.search_bar.get_text() != self.previous_search_text:
                self.page = 0
                if self.cat_list_buttons:
                    for i in self.cat_list_buttons:
                        self.cat_list_buttons[i].kill()
                    for i in self.accessory_buttons:
                        self.accessory_buttons[i].kill()
                
                self.update_cat_list2()

                if self.page == 0 and self.max_pages in [0, 1]:
                    self.previous_page_button.disable()
                    self.next_page_button.disable()
                elif self.page == 0:
                    self.previous_page_button.disable()
                    self.next_page_button.enable()
                elif self.page == self.max_pages - 1:
                    self.previous_page_button.enable()
                    self.next_page_button.disable()
                else:
                    self.previous_page_button.enable()
                    self.next_page_button.enable()
                self.previous_search_text = self.search_bar.get_text()

    def chunks(self, L, n):
        return [L[x: x + n] for x in range(0, len(L), n)]
