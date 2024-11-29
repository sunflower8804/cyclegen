from random import choice, randrange
import pygame_gui
import random
from .Screens import Screens
from re import sub

import ujson

import pygame
import pygame_gui

from scripts.utility import get_text_box_theme, scale, generate_sprite
from scripts.housekeeping.version import get_version_info
from scripts.clan import Clan
from scripts.cat.cats import create_example_cats, Cat, Personality
from scripts.cat.skills import Skill, SkillPath
from scripts.cat.pelts import Pelt
from scripts.cat.cats import create_example_cats, create_cat, Cat
from scripts.cat.names import names
from scripts.clan import Clan
from scripts.game_structure import image_cache
from scripts.game_structure.game_essentials import game, screen, screen_x, screen_y, MANAGER
from scripts.patrol.patrol import Patrol
from scripts.cat.skills import SkillPath
from scripts.game_structure.game_essentials import (
    game,
    screen,
    screen_x,
    screen_y,
    MANAGER,
)
from scripts.game_structure.ui_elements import UIImageButton, UISpriteButton
from scripts.patrol.patrol import Patrol
from scripts.utility import get_text_box_theme, scale
from .Screens import Screens
from ..cat.sprites import sprites
from ..game_structure.windows import SymbolFilterWindow


class MakeClanScreen(Screens):
    # UI images
    clan_frame_img = pygame.transform.scale(pygame.image.load(
        'resources/images/pick_clan_screen/clan_name_frame.png').convert_alpha(), (432, 100))
    name_clan_img = pygame.transform.scale(pygame.image.load(
        'resources/images/pick_clan_screen/name_clan_light.png').convert_alpha(), (1600, 1400))
    leader_img = pygame.transform.scale(pygame.image.load(
        'resources/images/pick_clan_screen/choose cat.png').convert_alpha(), (1600, 1400))
    leader_img_dark = pygame.transform.scale(pygame.image.load(
        'resources/images/pick_clan_screen/choose cat dark.png').convert_alpha(), (1600, 1400))
    deputy_img = pygame.transform.scale(pygame.image.load(
        'resources/images/pick_clan_screen/deputy_light.png').convert_alpha(), (1600, 1400))
    medic_img = pygame.transform.scale(pygame.image.load(
        'resources/images/pick_clan_screen/med_light.png').convert_alpha(), (1600, 1400))
    clan_img = pygame.transform.scale(pygame.image.load(
        'resources/images/pick_clan_screen/clan_light.png').convert_alpha(), (1600, 1400))
    bg_preview_border = pygame.transform.scale(
        pygame.image.load("resources/images/bg_preview_border.png").convert_alpha(), (466, 416))
    
    your_name_img = pygame.transform.scale(pygame.image.load(
        'resources/images/pick_clan_screen/Your name screen.png').convert_alpha(), (1600, 1400))
    your_name_img_dark = pygame.transform.scale(pygame.image.load(
        'resources/images/pick_clan_screen/Your name screen darkmode.png').convert_alpha(), (1600, 1400))
    your_name_txt1 = pygame.transform.scale(pygame.image.load(
        'resources/images/pick_clan_screen/your name text1.png').convert_alpha(), (796, 52))
    your_name_txt2 = pygame.transform.scale(pygame.image.load(
        'resources/images/pick_clan_screen/your name text2.png').convert_alpha(), (536, 52))
    
    #images for the customizing screen
    sprite_preview_bg = pygame.transform.scale(pygame.image.load(
        'resources/images/sprite_preview.png').convert_alpha(), (1600, 1400))
    
    sprite_preview_bg_dark = pygame.transform.scale(pygame.image.load(
        'resources/images/sprite_preview_dark.png').convert_alpha(), (1600, 1400))
    
    poses_bg = pygame.transform.scale(pygame.image.load(
        'resources/images/poses_bg.png').convert_alpha(), (1600, 1400))
    
    poses_bg_dark = pygame.transform.scale(pygame.image.load(
        'resources/images/poses_bg_dark.png').convert_alpha(), (1600, 1400))
    
    choice_bg = pygame.transform.scale(pygame.image.load(
        'resources/images/custom_choice_bg.png').convert_alpha(), (1600, 1400))
    
    choice_bg_dark = pygame.transform.scale(pygame.image.load(
        'resources/images/custom_choice_bg_dark.png').convert_alpha(), (1600, 1400))
    

    with open(f"resources/dicts/acc_display.json", "r") as read_file:
        ACC_DISPLAY = ujson.loads(read_file.read())



    # This section holds all the information needed
    game_mode = 'expanded'  # To save the users selection before conformation.
    clan_name = ""  # To store the clan name before conformation
    leader = None  # To store the clan leader before conformation
    deputy = None
    med_cat = None
    members = []
    elected_camp = None
    your_cat = None

    # holds the symbol we have selected
    symbol_selected = None
    tag_list_len = 0
    # Holds biome we have selected
    biome_selected = None
    selected_camp_tab = 1
    selected_season = None
    # Camp number selected
    camp_num = "1"
    # Holds the cat we have currently selected.
    selected_cat = None
    # Hold which sub-screen we are on
    sub_screen = 'name clan'
    # Holds which ranks we are currently selecting.
    choosing_rank = None
    # To hold the images for the sections. Makes it easier to kill them
    elements = {}
    tabs = {}
    symbol_buttons = {}

    # used in symbol screen only - parent container is in element dict
    text = {}

    def __init__(self, name=None):
        super().__init__(name)
        # current page for symbol choosing
        self.current_page = 1

        self.rolls_left = game.config["clan_creation"]["rerolls"]
        self.menu_warning = None

    def screen_switches(self):
        # Reset variables
        self.game_mode = 'expanded'
        self.clan_name = ""
        self.selected_camp_tab = 1
        self.biome_selected = None
        self.selected_season = "Newleaf"
        self.symbol_selected = None
        self.leader = None  # To store the Clan leader before conformation
        self.deputy = None
        self.med_cat = None
        self.members = []
        self.clan_size = "medium"
        self.clan_age = "established"
        
        self.custom_cat = None
        self.elements = {}
        self.pname="SingleColour"
        self.length="short"
        self.colour="WHITE"
        self.white_patches=None
        self.eye_colour="BLUE"
        self.eye_colour2=None
        self.tortiebase=None
        self.tortiecolour=None
        self.pattern=None
        self.tortiepattern=None
        self.vitiligo=None
        self.points=None
        self.paralyzed=False
        self.opacity=100
        self.scars=[]
        self.tint="None"
        self.skin="BLACK"
        self.white_patches_tint="None"
        self.kitten_sprite=0
        self.reverse=False
        self.skill = "Random"
        self.accessories=[]
        self.inventory = []
        self.sex = "male"
        self.personality = "troublesome"
        self.permanent_condition = None
        self.preview_age = "kitten"
        self.page = 0
        self.adolescent_pose = 3
        self.adult_pose = 6
        self.elder_pose = 12
        self.faith = "flexible"
        game.choose_cats = {}
        self.skills = []
        self.current_members = []

        for skillpath in SkillPath:
            count = 0
            for skill in skillpath.value:
                count += 1
                if count == 1:
                    self.skills.append(skill)

        # NEW CUSTOMISER BUTTON DICTS

        self.current_selection = "pelt_pattern"
        self.customiser_sort = "default"
        self.search_text = ""
        self.previous_search_text = "search"

        self.tortie_enabled = False
        self.current_selection_buttons = {}
        # Page 0
        self.preview_age_buttons = {}
        self.kitten_pose_buttons = {}
        self.adolescent_pose_buttons = {}
        self.adult_pose_buttons = {}
        self.elder_pose_buttons = {}
        self.fur_length_buttons = {}
        self.reverse_buttons = {}
        # Page 1
        self.pelt_colour_buttons = {}
        self.pelt_pattern_buttons = {}
        self.tint_buttons = {}

        self.tortie_patches_buttons = {}
        self.tortie_colour_buttons = {}
        self.tortie_pattern_buttons = {}

        self.pelt_colour_names = {}
        self.pelt_pattern_names = {}

        self.white_patches_buttons = {}
        self.white_patches_names = {}

        self.points_buttons = {}
        self.points_names = {}

        self.vitiligo_buttons = {}
        self.vitiligo_names = {}

        self.white_patches_tint_buttons = {}

        self.tortie_patches_names = {}
        self.tortie_colour_names = {}
        self.tortie_pattern_names = {}
        

        # Page 2
        self.eye_colour_buttons = {}
        self.eye_colour_names = {}

        self.heterochromia_buttons = {}
        self.heterochromia_names = {}

        self.skin_buttons = {}
        self.skin_names = {}

        self.scar_buttons = {}
        self.scar_names = {}

        self.accessory_buttons = {}
        self.accessory_names = {}

        # Page 3
        self.condition_buttons = {}
        self.condition_names = {}

        self.trait_buttons = {}
        self.trait_names = {}

        self.skill_buttons = {}
        self.skill_names = {}

        self.faith_buttons = {}
        self.faith_names = {}

        self.sex_buttons = {}

        self.customiser_button_dicts = [
            self.current_selection_buttons,
            self.preview_age_buttons,
            self.kitten_pose_buttons,
            self.adolescent_pose_buttons,
            self.adult_pose_buttons,
            self.elder_pose_buttons,
            self.fur_length_buttons,
            self.reverse_buttons,

            self.pelt_colour_buttons,
            self.pelt_pattern_buttons,
            self.tint_buttons,

            self.white_patches_buttons,
            self.white_patches_names,
            self.points_buttons,
            self.points_names,

            self.vitiligo_buttons,
            self.vitiligo_names,

            self.white_patches_tint_buttons,

            self.tortie_patches_buttons,
            self.tortie_colour_buttons,
            self.tortie_pattern_buttons,

            self.pelt_colour_names,
            self.pelt_pattern_names,

            self.tortie_patches_names,
            self.tortie_colour_names,
            self.tortie_pattern_names,

            self.eye_colour_buttons,
            self.eye_colour_names,

            self.heterochromia_buttons,
            self.heterochromia_names,

            self.skin_buttons,
            self.skin_names,

            self.scar_buttons,
            self.scar_names,

            self.accessory_buttons,
            self.accessory_names,

            self.condition_buttons,
            self.condition_names,

            self.trait_buttons,
            self.trait_names,

            self.skill_buttons,
            self.skill_names,

            self.faith_buttons,
            self.faith_names,

            self.sex_buttons
            ]
        
        self.notail_accs = ['RED FEATHERS', 'BLUE FEATHERS', 'JAY FEATHERS', "SEAWEED",
                            "DAISY CORSAGE", "GULL FEATHERS", "SPARROW FEATHERS", "CLOVER", "DAISY",
                            "SPRINGFEATHERS", "CLOVER", "LAVENDERTAILWRAP", "CELESTIALCHIMES",
                            "LUNARCHIMES", "SILVERLUNARCHIMES", "FLOWER MOSS", "SANVITALIAFLOWERS",
                            "STARFLOWERS", "SHELL PACK", "MOSS2", "MUSHROOMS", "CLOVERS", "MUD", "LADYBUGS",
                            "FIRBRANCHES", "CHERRYBLOSSOM", "MISTLETOE", "BROWNMOSSPELT", "BLEEDINGVINES",
                            "BLEEDINGHEART", "MOREFERN", "GRAYMOSSPELT", "FERN"]
        # god damn we have a lot of tail accessories

        # Buttons that appear on every screen.
        self.menu_warning = pygame_gui.elements.UITextBox(
            '',
            scale(pygame.Rect((50, 50), (1200, -1))),
            object_id=get_text_box_theme("#text_box_22_horizleft"),
            manager=MANAGER,
        )
        self.main_menu = UIImageButton(
            scale(pygame.Rect((50, 100), (306, 60))),
            "",
            object_id="#main_menu_button",
            manager=MANAGER,
        )

        if game.switches["customise_new_life"] is True:
            for c in list(Cat.all_cats.keys()):
                self.current_members.append(c)
            create_example_cats()
            self.hide_menu_buttons()
            self.open_choose_leader()
        else:
            create_example_cats()
            self.open_name_clan()

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.main_menu:
                self.change_screen('start screen')
            if self.sub_screen == 'name clan':
                self.handle_name_clan_event(event)
            elif self.sub_screen == 'choose name':
                self.handle_choose_name_event(event)
            elif self.sub_screen == 'choose leader':
                self.handle_choose_leader_event(event)
            elif self.sub_screen == 'customize cat':
                self.handle_customize_cat_event(event)
            elif self.sub_screen == 'choose camp':
                self.handle_choose_background_event(event)
            elif self.sub_screen == "choose symbol":
                self.handle_choose_symbol_event(event)
            elif self.sub_screen == "saved screen":
                self.handle_saved_clan_event(event)
        
        elif event.type == pygame.KEYDOWN and game.settings['keybinds']:
            if self.sub_screen == 'name clan':
                self.handle_name_clan_key(event)
            elif self.sub_screen == "choose camp":
                self.handle_choose_background_key(event)
            elif self.sub_screen == "saved screen" and (
                event.key == pygame.K_RETURN or event.key == pygame.K_RIGHT
            ):
                self.change_screen("start screen")

    def handle_name_clan_event(self, event):
        if event.ui_element == self.elements["random"]:
            self.elements["name_entry"].set_text(self.random_clan_name())
        elif event.ui_element == self.elements["reset_name"]:
            self.elements["name_entry"].set_text("")
        elif event.ui_element == self.elements["next_step"]:
            new_name = sub(
                r"[^A-Za-z0-9 ]+", "", self.elements["name_entry"].get_text()
            ).strip()
            if not new_name:
                self.elements["error"].set_text("Your Clan's name cannot be empty")
                self.elements["error"].show()
                return
            if new_name.casefold() in [
                clan.casefold() for clan in game.switches["clan_list"]
            ]:
                self.elements["error"].set_text("A Clan with that name already exists.")
                self.elements["error"].show()
                return
            self.clan_name = new_name
            self.open_choose_leader()
        elif event.ui_element == self.elements["previous_step"]:
            self.clan_name = ""
            self.change_screen('start screen')
        elif event.ui_element == self.elements['small']:
            self.elements['small'].disable()
            self.elements['medium'].enable()
            self.elements['large'].enable()
            self.clan_size = "small"
        elif event.ui_element == self.elements['medium']:
            self.elements['small'].enable()
            self.elements['medium'].disable()
            self.elements['large'].enable()
            self.clan_size = "medium"
        elif event.ui_element == self.elements['large']:
            self.elements['small'].enable()
            self.elements['large'].disable()
            self.elements['medium'].enable()
            self.clan_size = "large"
        elif event.ui_element == self.elements["established"]:
            self.elements['established'].disable()
            self.elements['new'].enable()
            self.clan_age = "established"
        elif event.ui_element == self.elements["new"]:
            self.elements['established'].enable()
            self.elements['new'].disable()
            self.clan_age = "new"
    
    def random_clan_name(self):
        clan_names = names.names_dict["normal_prefixes"] + names.names_dict["clan_prefixes"]
        while True:
            chosen_name = choice(clan_names)
            if chosen_name.casefold() not in [clan.casefold() for clan in game.switches['clan_list']]:
                return chosen_name
            print("Generated clan name was already in use! Rerolling...")
    
    def handle_name_clan_key(self, event):
        if event.key == pygame.K_ESCAPE:
            self.change_screen("start screen")
        elif event.key == pygame.K_LEFT:
            if not self.elements["name_entry"].is_focused:
                self.clan_name = ""
        elif event.key == pygame.K_RIGHT:
            if not self.elements["name_entry"].is_focused:
                new_name = sub(
                    r"[^A-Za-z0-9 ]+", "", self.elements["name_entry"].get_text()
                ).strip()
                if not new_name:
                    self.elements["error"].set_text("Your Clan's name cannot be empty")
                    self.elements["error"].show()
                    return
                if new_name.casefold() in [
                    clan.casefold() for clan in game.switches["clan_list"]
                ]:
                    self.elements["error"].set_text(
                        "A Clan with that name already exists."
                    )
                    self.elements["error"].show()
                    return
                self.clan_name = new_name
                self.open_choose_leader()
        elif event.key == pygame.K_RETURN:
            new_name = sub(
                r"[^A-Za-z0-9 ]+", "", self.elements["name_entry"].get_text()
            ).strip()
            if not new_name:
                self.elements["error"].set_text("Your Clan's name cannot be empty")
                self.elements["error"].show()
                return
            if new_name.casefold() in [
                clan.casefold() for clan in game.switches["clan_list"]
            ]:
                self.elements["error"].set_text("A Clan with that name already exists.")
                self.elements["error"].show()
                return
            self.clan_name = new_name
            self.open_choose_leader()

    def handle_choose_leader_event(self, event):
        if event.ui_element in [
            self.elements["roll1"],
            self.elements["roll2"],
            self.elements["roll3"],
            self.elements["dice"],
        ]:
            self.elements["select_cat"].hide()
            game.choose_cats = {}
            create_example_cats()  # create new cats
            self.selected_cat = None  # Your selected cat now no longer exists. Sad. They go away.
            self.refresh_cat_images_and_info()  # Refresh all the images.
            self.rolls_left -= 1
            if game.config["clan_creation"]["rerolls"] == 3:
                event.ui_element.disable()
            else:
                self.elements["reroll_count"].set_text(str(self.rolls_left))
                if self.rolls_left == 0:
                    event.ui_element.disable()

        elif event.ui_element in [self.elements["cat" + str(u)] for u in range(0, 12)]:
            self.selected_cat = event.ui_element.return_cat_object()
            self.refresh_cat_images_and_info(self.selected_cat)
            self.refresh_text_and_buttons()
        elif event.ui_element == self.elements['select_cat']:
            self.your_cat = self.selected_cat
            self.selected_cat = None
            self.open_name_cat()
        elif event.ui_element == self.elements['previous_step']:
            self.clan_name = ""
            self.open_name_clan()
        elif event.ui_element == self.elements['customize']:
            self.open_customize_cat()
            
    def handle_choose_name_event(self, event):
        if event.ui_element == self.elements['next_step']:
            new_name = sub(r'[^A-Za-z0-9 ]+', "", self.elements["name_entry"].get_text()).strip()
            if not new_name:
                self.elements["error"].set_text("Your cat's name cannot be empty")
                self.elements["error"].show()
                return
            self.your_cat.name.prefix = new_name

            if game.switches["customise_new_life"] is True:
                self.open_clan_saved_screen()
            else:
                self.open_choose_background()

        elif event.ui_element == self.elements["random"]:
            self.elements["name_entry"].set_text(choice(names.names_dict["normal_prefixes"]))
        elif event.ui_element == self.elements['previous_step']:
            self.selected_cat = None
            self.open_choose_leader()
    
    def handle_create_other_cats(self):
        self.create_example_cats2()
        for cat in game.choose_cats.values():
            if cat.status == "warrior":
                if self.leader is None:
                    self.leader = cat
                elif self.deputy is None:
                    self.deputy = cat
                    cat.status = "deputy"
                elif self.med_cat is None:
                    self.med_cat = cat
                    cat.status = "medicine cat"
                else:
                    self.members.append(cat)
            else:
                self.members.append(cat)
        self.members.append(self.your_cat)
        
    def create_example_cats2(self):
        e = random.sample(range(12), 3)
        not_allowed = ['NOPAW', 'NOTAIL', 'HALFTAIL', 'NOEAR', 'BOTHBLIND', 'RIGHTBLIND', 'LEFTBLIND', 'BRIGHTHEART',
                    'NOLEFTEAR', 'NORIGHTEAR', 'MANLEG']
        c_size = 15
        backstories = ["clan_founder"]
        for i in range(1, 17):
            backstories.append(f"clan_founder{i}")
        if self.clan_age == "established":
            backstories = ['halfclan1', 'halfclan2', 'outsider_roots1', 'outsider_roots2', 'loner1', 'loner2', 'kittypet1', 'kittypet2', 'kittypet3', 'kittypet4', 'rogue1', 'rogue2', 'rogue3', 'rogue4', 'rogue5', 'rogue6', 'rogue7', 'rogue8', 'abandoned1', 'abandoned2', 'abandoned3', 'abandoned4', 'otherclan1', 'otherclan2', 'otherclan3', 'otherclan4', 'otherclan5', 'otherclan6', 'otherclan7', 'otherclan8', 'otherclan9', 'otherclan10', 'disgraced1', 'disgraced2', 'disgraced3', 'refugee1', 'refugee2', 'refugee3', 'refugee4', 'refugee5', 'tragedy_survivor1', 'tragedy_survivor2', 'tragedy_survivor3', 'tragedy_survivor4', 'tragedy_survivor5', 'tragedy_survivor6', 'guided1', 'guided2', 'guided3', 'guided4', 'orphaned1', 'orphaned2', 'orphaned3', 'orphaned4', 'orphaned5', 'orphaned6', 'outsider1', 'outsider2', 'outsider3', 'kittypet5', 'kittypet6', 'kittypet7', 'guided5', 'guided6', 'outsider4', 'outsider5', 'outsider6', 'orphaned7', 'halfclan4', 'halfclan5', 'halfclan6', 'halfclan7', 'halfclan8', 'halfclan9', 'halfclan10', 'outsider_roots3', 'outsider_roots4', 'outsider_roots5', 'outsider_roots6', 'outsider_roots7', 'outsider_roots8']

        if self.clan_size == "small":
            c_size = 10
        elif self.clan_size == 'large':
            c_size = 20
        for a in range(c_size):
            if a in e:
                game.choose_cats[a] = Cat(status='warrior', biome=None)
            else:
                r = random.randint(1,90)
                s = "warrior"
                if r > 85:
                    s = "medicine cat"
                elif r > 80:
                    s = "medicine cat apprentice"
                elif r > 40:
                    s = "warrior"
                elif r > 30:
                    s = "apprentice"
                elif r > 25:
                    s = "kitten"
                elif r > 20:
                    s = "elder"
                elif r > 15:
                    s = "mediator"
                elif r > 10:
                    s = "mediator apprentice"
                elif r > 5:
                    s = "queen"
                elif r >= 0:
                    s = "queen's apprentice"
                game.choose_cats[a] = Cat(status=s, biome=None)
            if game.choose_cats[a].moons >= 160:
                game.choose_cats[a].moons = choice(range(120, 155))
            elif game.choose_cats[a].moons == 0:
                game.choose_cats[a].moons = choice([1, 2, 3, 4, 5])

            # fucking inventory
            game.choose_cats[a].pelt.inventory = []

            if self.clan_age == "new":
                if game.choose_cats[a].status not in ['newborn', 'kitten']:
                    unique_backstories = ["clan_founder4", "clan_founder13", "clan_founder14", "clan_founder15"]
                    unique = choice(unique_backstories)
                    backstories = [story for story in backstories if story not in unique_backstories or story == unique]
                    game.choose_cats[a].backstory = choice(backstories)
                else:
                    game.choose_cats[a].backstory = 'clanborn'
            else:
                if random.randint(1,5) == 1 and game.choose_cats[a].status not in ['newborn', 'kitten']:
                    game.choose_cats[a].backstory = choice(backstories)
                else:
                    game.choose_cats[a].backstory = 'clanborn'
    
    def handle_choose_background_event(self, event):
        if event.ui_element == self.elements['previous_step']:
            self.open_name_cat()
        elif event.ui_element == self.elements['forest_biome']:
            self.biome_selected = "Forest"
            self.selected_camp_tab = 1
            self.refresh_text_and_buttons()
        elif event.ui_element == self.elements["mountain_biome"]:
            self.biome_selected = "Mountainous"
            self.selected_camp_tab = 1
            self.refresh_text_and_buttons()
        elif event.ui_element == self.elements["plains_biome"]:
            self.biome_selected = "Plains"
            self.selected_camp_tab = 1
            self.refresh_text_and_buttons()
        elif event.ui_element == self.elements["beach_biome"]:
            self.biome_selected = "Beach"
            self.selected_camp_tab = 1
            self.refresh_text_and_buttons()
        elif event.ui_element == self.tabs["tab1"]:
            self.selected_camp_tab = 1
            self.refresh_selected_camp()
        elif event.ui_element == self.tabs["tab2"]:
            self.selected_camp_tab = 2
            self.refresh_selected_camp()
        elif event.ui_element == self.tabs["tab3"]:
            self.selected_camp_tab = 3
            self.refresh_selected_camp()
        elif event.ui_element == self.tabs["tab4"]:
            self.selected_camp_tab = 4
            self.refresh_selected_camp()
        elif event.ui_element == self.tabs["tab5"]:
            self.selected_camp_tab = 5
            self.refresh_selected_camp()
        elif event.ui_element == self.tabs["tab6"]:
            self.selected_camp_tab = 6
            self.refresh_selected_camp()
        elif event.ui_element == self.tabs["newleaf_tab"]:
            self.selected_season = "Newleaf"
            self.refresh_text_and_buttons()
        elif event.ui_element == self.tabs["greenleaf_tab"]:
            self.selected_season = "Greenleaf"
            self.refresh_text_and_buttons()
        elif event.ui_element == self.tabs["leaffall_tab"]:
            self.selected_season = "Leaf-fall"
            self.refresh_text_and_buttons()
        elif event.ui_element == self.tabs["leafbare_tab"]:
            self.selected_season = "Leaf-bare"
            self.refresh_text_and_buttons()
        elif event.ui_element == self.elements["random_background"]:
            # Select a random biome and background
            old_biome = self.biome_selected
            possible_biomes = ['Forest', 'Mountainous', 'Plains', 'Beach']
            # ensuring that the new random camp will not be the same one
            if old_biome is not None:
                possible_biomes.remove(old_biome)
            self.biome_selected = choice(possible_biomes)
            if self.biome_selected == 'Forest':
                self.selected_camp_tab = randrange(1, 7)
            elif self.biome_selected == "Mountainous":
                self.selected_camp_tab = randrange(1, 7)
            elif self.biome_selected == "Plains":
                self.selected_camp_tab = randrange(1, 6)
            else:
                self.selected_camp_tab = randrange(1, 5)
            self.refresh_selected_camp()
            self.refresh_text_and_buttons()
        elif event.ui_element == self.elements["next_step"]:
            self.open_choose_symbol()

    def handle_choose_background_key(self, event):
        if event.key == pygame.K_RIGHT:
            if self.biome_selected is None:
                self.biome_selected = "Forest"
            elif self.biome_selected == "Forest":
                self.biome_selected = "Mountainous"
            elif self.biome_selected == "Mountainous":
                self.biome_selected = "Plains"
            elif self.biome_selected == "Plains":
                self.biome_selected = "Beach"
            self.selected_camp_tab = 1
            self.refresh_text_and_buttons()
        elif event.key == pygame.K_LEFT:
            if self.biome_selected is None:
                self.biome_selected = "Beach"
            elif self.biome_selected == "Beach":
                self.biome_selected = "Plains"
            elif self.biome_selected == "Plains":
                self.biome_selected = "Mountainous"
            elif self.biome_selected == "Mountainous":
                self.biome_selected = "Forest"
            self.selected_camp_tab = 1
            self.refresh_text_and_buttons()
        elif event.key == pygame.K_UP and self.biome_selected is not None:
            if self.selected_camp_tab > 1:
                self.selected_camp_tab -= 1
                self.refresh_selected_camp()
        elif event.key == pygame.K_DOWN and self.biome_selected is not None:
            if self.selected_camp_tab < 6:
                self.selected_camp_tab += 1
                self.refresh_selected_camp()
        elif event.key == pygame.K_RETURN:
            self.save_clan()
            self.open_clan_saved_screen()

    def handle_choose_symbol_event(self, event):
        if event.ui_element == self.elements["previous_step"]:
            self.open_choose_background()
        elif event.ui_element == self.elements["page_right"]:
            self.current_page += 1
            self.refresh_symbol_list()
        elif event.ui_element == self.elements["page_left"]:
            self.current_page -= 1
            self.refresh_symbol_list()
        elif event.ui_element == self.elements["done_button"]:
            self.save_clan()
            self.open_clan_saved_screen()
        elif event.ui_element == self.elements["random_symbol_button"]:
            if self.symbol_selected:
                if self.symbol_selected in self.symbol_buttons:
                    self.symbol_buttons[self.symbol_selected].enable()
            self.symbol_selected = choice(sprites.clan_symbols)
            self.refresh_text_and_buttons()
        elif event.ui_element == self.elements["filters_tab"]:
            SymbolFilterWindow()
        else:
            for symbol_id, element in self.symbol_buttons.items():
                if event.ui_element == element:
                    if self.symbol_selected:
                        if self.symbol_selected in self.symbol_buttons:
                            self.symbol_buttons[self.symbol_selected].enable()
                    self.symbol_selected = symbol_id
                    self.refresh_text_and_buttons()

    def handle_saved_clan_event(self, event):
        if event.ui_element == self.elements["continue"]:
            # redoing this here bc its usually done on the symbol screen
            # which we don't get with a new life
            if game.switches["customise_new_life"] is True:
                self.save_clan()
                self.open_clan_saved_screen()
                game.switches['customise_new_life'] = False
            self.change_screen("camp screen")

    def exit_screen(self):
        self.main_menu.kill()
        self.menu_warning.kill()
        self.clear_all_page()
        self.rolls_left = game.config["clan_creation"]["rerolls"]
        return super().exit_screen()

    def on_use(self):
        # Don't allow someone to enter no name for their clan
        if self.sub_screen == "name clan":
            if self.elements["name_entry"].get_text() == "":
                self.elements["next_step"].disable()
            elif self.elements["name_entry"].get_text().startswith(" "):
                self.elements["error"].set_text("Clan names cannot start with a space.")
                self.elements["error"].show()
                self.elements["next_step"].disable()
            elif self.elements["name_entry"].get_text().casefold() in [
                clan.casefold() for clan in game.switches["clan_list"]
            ]:
                self.elements["error"].set_text("A Clan with that name already exists.")
                self.elements["error"].show()
                self.elements["next_step"].disable()
            else:
                self.elements["error"].hide()
                self.elements['next_step'].enable()
            # Set the background for the name clan page - done here to avoid GUI layering issues
            screen.blit(pygame.transform.scale(MakeClanScreen.name_clan_img, (screen_x, screen_y)), (0,0))
            
        elif self.sub_screen == 'choose name':
            if self.elements["name_entry"].get_text() == "":
                self.elements['next_step'].disable()
            elif self.elements["name_entry"].get_text().startswith(" "):
                self.elements["error"].set_text("Your name cannot start with a space.")
                self.elements["error"].show()
                self.elements['next_step'].disable()
            else:
                self.elements["error"].hide()
                self.elements['next_step'].enable()
        elif self.sub_screen == "choose symbol":
            if len(game.switches["disallowed_symbol_tags"]) != self.tag_list_len:
                self.tag_list_len = len(game.switches["disallowed_symbol_tags"])
                self.refresh_symbol_list()

    def clear_all_page(self):
        """Clears the entire page, including layout images"""
        for image in self.elements:
            self.elements[image].kill()
        for tab in self.tabs:
            self.tabs[tab].kill()
        for button in self.symbol_buttons:
            self.symbol_buttons[button].kill()
        self.elements = {}

        for item in self.customiser_button_dicts:
            for ele in item:
                item[ele].kill()
            item = {}

    def refresh_text_and_buttons(self):
        """Refreshes the button states and text boxes"""
        if self.sub_screen == "game mode":
            # Set the mode explanation text
            if self.game_mode == "classic":
                display_text = self.classic_mode_text
                display_name = "Classic Mode"
            elif self.game_mode == "expanded":
                display_text = self.expanded_mode_text
                display_name = "Expanded Mode"
            elif self.game_mode == "cruel season":
                display_text = self.cruel_mode_text
                display_name = "Cruel Season"
            else:
                display_text = ""
                display_name = "ERROR"
            self.elements["mode_details"].set_text(display_text)
            self.elements["mode_name"].set_text(display_name)

            # Update the enabled buttons for the game selection to disable the
            # buttons for the mode currently selected. Mostly for aesthetics, and it
            # make it very clear which mode is selected.
            if self.game_mode == "classic":
                self.elements["classic_mode_button"].disable()
                self.elements["expanded_mode_button"].enable()
                self.elements["cruel_mode_button"].enable()
            elif self.game_mode == "expanded":
                self.elements["classic_mode_button"].enable()
                self.elements["expanded_mode_button"].disable()
                self.elements["cruel_mode_button"].enable()
            elif self.game_mode == "cruel season":
                self.elements["classic_mode_button"].enable()
                self.elements["expanded_mode_button"].enable()
                self.elements["cruel_mode_button"].disable()
            else:
                self.elements["classic_mode_button"].enable()
                self.elements["expanded_mode_button"].enable()
                self.elements["cruel_mode_button"].enable()

            # Don't let the player go forwards with cruel mode, it's not done yet.
            if self.game_mode == "cruel season":
                self.elements["next_step"].disable()
            else:
                self.elements["next_step"].enable()
        # Show the error message if you try to choose a child for leader, deputy, or med cat.
        elif self.sub_screen in ['choose leader', 'choose deputy', 'choose med cat']:
            self.elements['select_cat'].show()
        # Refresh the choose-members background to match number of cat's chosen.
        elif self.sub_screen == "choose members":
            if len(self.members) == 0:
                self.elements["background"].set_image(
                    pygame.transform.scale(
                        pygame.image.load(
                            "resources/images/pick_clan_screen/clan_none_light.png"
                        ).convert_alpha(),
                        (1600, 1400),
                    )
                )
                self.elements["next_step"].disable()
            elif len(self.members) == 1:
                self.elements["background"].set_image(
                    pygame.transform.scale(
                        pygame.image.load(
                            "resources/images/pick_clan_screen/clan_one_light.png"
                        ).convert_alpha(),
                        (1600, 1400),
                    )
                )
                self.elements["next_step"].disable()
            elif len(self.members) == 2:
                self.elements["background"].set_image(
                    pygame.transform.scale(
                        pygame.image.load(
                            "resources/images/pick_clan_screen/clan_two_light.png"
                        ).convert_alpha(),
                        (1600, 1400),
                    )
                )
                self.elements["next_step"].disable()
            elif len(self.members) == 3:
                self.elements["background"].set_image(
                    pygame.transform.scale(
                        pygame.image.load(
                            "resources/images/pick_clan_screen/clan_three_light.png"
                        ).convert_alpha(),
                        (1600, 1400),
                    )
                )
                self.elements["next_step"].disable()
            elif 4 <= len(self.members) <= 6:
                self.elements["background"].set_image(
                    pygame.transform.scale(
                        pygame.image.load(
                            "resources/images/pick_clan_screen/clan_four_light.png"
                        ).convert_alpha(),
                        (1600, 1400),
                    )
                )
                self.elements["next_step"].enable()
                # In order for the "previous step" to work properly, we must enable this button, just in case it
                # was disabled in the next step.
                self.elements["select_cat"].enable()
            elif len(self.members) == 7:
                self.elements["background"].set_image(
                    pygame.transform.scale(
                        pygame.image.load(
                            "resources/images/pick_clan_screen/clan_full_light.png"
                        ).convert_alpha(),
                        (1600, 1400),
                    )
                )
                self.elements["select_cat"].disable()
                self.elements["next_step"].enable()

            # Hide the recruit cat button if no cat is selected.
            if self.selected_cat is not None:
                self.elements["select_cat"].show()
            else:
                self.elements["select_cat"].hide()

        elif self.sub_screen == "choose camp":
            # Enable/disable biome buttons
            if self.biome_selected == "Forest":
                self.elements["forest_biome"].disable()
                self.elements["mountain_biome"].enable()
                self.elements["plains_biome"].enable()
                self.elements["beach_biome"].enable()
            elif self.biome_selected == "Mountainous":
                self.elements["forest_biome"].enable()
                self.elements["mountain_biome"].disable()
                self.elements["plains_biome"].enable()
                self.elements["beach_biome"].enable()
            elif self.biome_selected == "Plains":
                self.elements["forest_biome"].enable()
                self.elements["mountain_biome"].enable()
                self.elements["plains_biome"].disable()
                self.elements["beach_biome"].enable()
            elif self.biome_selected == "Beach":
                self.elements["forest_biome"].enable()
                self.elements["mountain_biome"].enable()
                self.elements["plains_biome"].enable()
                self.elements["beach_biome"].disable()

            if self.selected_season == "Newleaf":
                self.tabs["newleaf_tab"].disable()
                self.tabs["greenleaf_tab"].enable()
                self.tabs["leaffall_tab"].enable()
                self.tabs["leafbare_tab"].enable()
            elif self.selected_season == "Greenleaf":
                self.tabs["newleaf_tab"].enable()
                self.tabs["greenleaf_tab"].disable()
                self.tabs["leaffall_tab"].enable()
                self.tabs["leafbare_tab"].enable()
            elif self.selected_season == "Leaf-fall":
                self.tabs["newleaf_tab"].enable()
                self.tabs["greenleaf_tab"].enable()
                self.tabs["leaffall_tab"].disable()
                self.tabs["leafbare_tab"].enable()
            elif self.selected_season == "Leaf-bare":
                self.tabs["newleaf_tab"].enable()
                self.tabs["greenleaf_tab"].enable()
                self.tabs["leaffall_tab"].enable()
                self.tabs["leafbare_tab"].disable()

            if self.biome_selected and self.selected_camp_tab:
                self.elements["next_step"].enable()

            # Deal with tab and shown camp image:
            self.refresh_selected_camp()
        elif self.sub_screen == "choose symbol":
            if self.symbol_selected:
                if self.symbol_selected in self.symbol_buttons:
                    self.symbol_buttons[self.symbol_selected].disable()
                # refresh selected symbol image
                self.elements["selected_symbol"].set_image(
                    pygame.transform.scale(
                        sprites.sprites[self.symbol_selected], (200, 200)
                    ).convert_alpha()
                )
                symbol_name = self.symbol_selected.replace("symbol", "")
                self.text["selected"].set_text(f"Selected Symbol: {symbol_name}")
                self.elements["selected_symbol"].show()
                self.elements["done_button"].enable()

    def refresh_selected_camp(self):
        """Updates selected camp image and tabs"""

        self.tabs["tab1"].kill()
        self.tabs["tab2"].kill()
        self.tabs["tab3"].kill()
        self.tabs["tab4"].kill()
        self.tabs["tab5"].kill()
        self.tabs["tab6"].kill()

        if self.biome_selected == 'Forest':
            self.tabs["tab1"] = UIImageButton(scale(pygame.Rect((190, 360), (308, 60))), "", object_id="#classic_tab"
                                              , manager=MANAGER)
            self.tabs["tab2"] = UIImageButton(scale(pygame.Rect((216, 430), (308, 60))), "", object_id="#gully_tab"
                                              , manager=MANAGER)
            self.tabs["tab3"] = UIImageButton(scale(pygame.Rect((190, 500), (308, 60))), "", object_id="#grotto_tab"
                                              , manager=MANAGER)
            self.tabs["tab4"] = UIImageButton(scale(pygame.Rect((170, 570), (308, 60))), "", object_id="#lakeside_tab"
                                              , manager=MANAGER)
            self.tabs["tab5"] = UIImageButton(scale(pygame.Rect((170, 640), (308, 60))), "", object_id="#pine_tab"
                                              , manager=MANAGER)
            self.tabs["tab6"] = UIImageButton(scale(pygame.Rect((170, 710), (308, 60))), "", object_id="#birch_camp_tab"
                                              , manager=MANAGER)
        elif self.biome_selected == 'Mountainous':
            self.tabs["tab1"] = UIImageButton(scale(pygame.Rect((222, 360), (308, 60))), "", object_id="#cliff_tab"
                                              , manager=MANAGER)
            self.tabs["tab2"] = UIImageButton(scale(pygame.Rect((180, 430), (308, 60))), "", object_id="#cave_tab"
                                              , manager=MANAGER)
            self.tabs["tab3"] = UIImageButton(scale(pygame.Rect((85, 500), (358, 60))), "", object_id="#crystal_tab"
                                              , manager=MANAGER)
            self.tabs["tab4"] = UIImageButton(scale(pygame.Rect((85, 570), (308, 60))), "", object_id="#rocky_slope_tab"
                                              , manager=MANAGER)
            self.tabs["tab5"] = UIImageButton(scale(pygame.Rect((85, 640), (308, 60))), "", object_id="#quarry_tab"
                                              , manager=MANAGER)
            self.tabs["tab6"] = UIImageButton(
                scale(pygame.Rect((215, 710), (308, 60))),
                "",
                object_id="#ruins_tab",
                manager=MANAGER,
            )
        elif self.biome_selected == 'Plains':
            self.tabs["tab1"] = UIImageButton(scale(pygame.Rect((128, 360), (308, 60))), "", object_id="#grasslands_tab"
                                              , manager=MANAGER, )
            self.tabs["tab2"] = UIImageButton(scale(pygame.Rect((178, 430), (308, 60))), "", object_id="#tunnel_tab"
                                              , manager=MANAGER)
            self.tabs["tab3"] = UIImageButton(scale(pygame.Rect((128, 500), (308, 60))), "", object_id="#wasteland_tab"
                                              , manager=MANAGER)
            self.tabs["tab4"] = UIImageButton(scale(pygame.Rect((128, 570), (308, 60))), "", object_id="#taiga_camp_tab"
                                              , manager=MANAGER)
            self.tabs["tab5"] = UIImageButton(scale(pygame.Rect((118, 640), (308, 60))), "", object_id="#desert_tab"
                                              , manager=MANAGER)
        elif self.biome_selected == 'Beach':
            self.tabs["tab1"] = UIImageButton(scale(pygame.Rect((152, 360), (308, 60))), "", object_id="#tidepool_tab"
                                            , manager=MANAGER)
            self.tabs["tab2"] = UIImageButton(scale(pygame.Rect((130, 430), (308, 60))), "", object_id="#tidal_cave_tab"
                                                , manager=MANAGER)
            self.tabs["tab3"] = UIImageButton(scale(pygame.Rect((140, 500), (308, 60))), "", object_id="#shipwreck_tab"
                                                , manager=MANAGER)
            self.tabs["tab4"] = UIImageButton(scale(pygame.Rect((78, 570), (308, 60))), "", object_id="#tropical_island_tab"
                                                , manager=MANAGER)

        if self.selected_camp_tab == 1:
            self.tabs["tab1"].disable()
            self.tabs["tab2"].enable()
            self.tabs["tab3"].enable()
            self.tabs["tab4"].enable()
            self.tabs["tab5"].enable()
            self.tabs["tab6"].enable()
        elif self.selected_camp_tab == 2:
            self.tabs["tab1"].enable()
            self.tabs["tab2"].disable()
            self.tabs["tab3"].enable()
            self.tabs["tab4"].enable()
            self.tabs["tab5"].enable()
            self.tabs["tab6"].enable()
        elif self.selected_camp_tab == 3:
            self.tabs["tab1"].enable()
            self.tabs["tab2"].enable()
            self.tabs["tab3"].disable()
            self.tabs["tab4"].enable()
            self.tabs["tab5"].enable()
            self.tabs["tab6"].enable()
        elif self.selected_camp_tab == 4:
            self.tabs["tab1"].enable()
            self.tabs["tab2"].enable()
            self.tabs["tab3"].enable()
            self.tabs["tab4"].disable()
            self.tabs["tab5"].enable()
            self.tabs["tab6"].enable()
        elif self.selected_camp_tab == 5:
            self.tabs["tab1"].enable()
            self.tabs["tab2"].enable()
            self.tabs["tab3"].enable()
            self.tabs["tab4"].enable()
            self.tabs["tab5"].disable()
            self.tabs["tab6"].enable()
        elif self.selected_camp_tab == 6:
            self.tabs["tab1"].enable()
            self.tabs["tab2"].enable()
            self.tabs["tab3"].enable()
            self.tabs["tab4"].enable()
            self.tabs["tab5"].enable()
            self.tabs["tab6"].disable()
        else:
            self.tabs["tab1"].enable()
            self.tabs["tab2"].enable()
            self.tabs["tab3"].enable()
            self.tabs["tab4"].enable()
            self.tabs["tab5"].enable()
            self.tabs["tab6"].enable()

        # I have to do this for proper layering.
        if "camp_art" in self.elements:
            self.elements["camp_art"].kill()
        if self.biome_selected:
            self.elements["camp_art"] = pygame_gui.elements.UIImage(
                scale(pygame.Rect((350, 340), (900, 800))),
                pygame.transform.scale(
                    pygame.image.load(
                        self.get_camp_art_path(self.selected_camp_tab)
                    ).convert_alpha(),
                    (900, 800),
                ),
                manager=MANAGER,
            )
            self.elements["art_frame"].kill()
            self.elements["art_frame"] = pygame_gui.elements.UIImage(
                scale(pygame.Rect(((334, 324), (932, 832)))),
                pygame.transform.scale(
                    pygame.image.load(
                        "resources/images/bg_preview_border.png"
                    ).convert_alpha(),
                    (932, 832),
                ),
                manager=MANAGER,
            )

    def refresh_selected_cat_info(self, selected=None):
        # SELECTED CAT INFO
        if selected is not None:

            if self.sub_screen == 'choose leader':
                self.elements['cat_name'].set_text(str(selected.name))
            else:
                self.elements['cat_name'].set_text(str(selected.name))
            self.elements['cat_name'].show()
            self.elements['cat_info'].set_text(selected.gender + "\n" +
                                               "fur length: " + str(selected.pelt.length) + "\n" +
                                                   str(selected.personality.trait) + "\n" +
                                                   str(selected.skills.skill_string()))
            if selected.permanent_condition:

                self.elements['cat_info'].set_text(selected.gender + "\n" +
                                               "fur length: " + str(selected.pelt.length) + "\n" +
                                                   str(selected.personality.trait) + "\n" +
                                                   str(selected.skills.skill_string()) + "\n" +
                                                   "permanent condition: " + list(selected.permanent_condition.keys())[0])
            self.elements['cat_info'].show()


    def refresh_cat_images_and_info(self, selected=None):
        """Update the image of the cat selected in the middle. Info and image.
        Also updates the location of selected cats."""

        column_poss = [100, 200]

        # updates selected cat info
        self.refresh_selected_cat_info(selected)

        # CAT IMAGES
        for u in range(6):
            if "cat" + str(u) in self.elements:
                self.elements["cat" + str(u)].kill()
            if game.choose_cats[u] == selected:
                self.elements["cat" + str(u)] = self.elements[
                    "cat" + str(u)
                ] = UISpriteButton(
                    scale(pygame.Rect((540, 400), (300, 300))),
                    pygame.transform.scale(game.choose_cats[u].sprite, (300, 300)),
                    cat_object=game.choose_cats[u],
                )
            elif (
                game.choose_cats[u]
                in [self.leader, self.deputy, self.med_cat] + self.members
            ):
                self.elements["cat" + str(u)] = UISpriteButton(
                    scale(pygame.Rect((1300, 250 + 100 * u), (100, 100))),
                    game.choose_cats[u].sprite,
                    cat_object=game.choose_cats[u],
                    manager=MANAGER,
                )
                self.elements["cat" + str(u)].disable()
            else:
                self.elements["cat" + str(u)] = UISpriteButton(
                    scale(pygame.Rect((column_poss[0], 260 + 100 * u), (100, 100))),
                    game.choose_cats[u].sprite,
                    cat_object=game.choose_cats[u], manager=MANAGER)
        for u in range(6, 12):
            if "cat" + str(u) in self.elements:
                self.elements["cat" + str(u)].kill()
            if game.choose_cats[u] == selected:
                self.elements["cat" + str(u)] = self.elements["cat" + str(u)] = UISpriteButton(
                    scale(pygame.Rect((540, 400), (300, 300))),
                    pygame.transform.scale(game.choose_cats[u].sprite, (300, 300)),
                    cat_object=game.choose_cats[u], manager=MANAGER)
            elif game.choose_cats[u] in [self.leader, self.deputy, self.med_cat] + self.members:
                self.elements["cat" + str(u)] = self.elements["cat" + str(u)] = UISpriteButton(
                    scale(pygame.Rect((540, 400), (300, 300))),
                    pygame.transform.scale(game.choose_cats[u].sprite, (300, 300)),
                    cat_object=game.choose_cats[u], manager=MANAGER)
            else:
                self.elements["cat" + str(u)] = UISpriteButton(
                    scale(
                        pygame.Rect((column_poss[1], 260 + 100 * (u - 6)), (100, 100))
                    ),
                    game.choose_cats[u].sprite,
                    cat_object=game.choose_cats[u], manager=MANAGER)
                
    def refresh_cat_images_and_info2(self, selected=None):
        """Update the image of the cat selected in the middle. Info and image.
        Also updates the location of selected cats. """

        column_poss = [100, 200]

        # updates selected cat info
        self.refresh_selected_cat_info(selected)

        # CAT IMAGES
        for u in range(6):
            if game.choose_cats[u] in [self.leader, self.deputy, self.med_cat] + self.members:
                self.elements["cat" + str(u)] = self.elements["cat" + str(u)] = UISpriteButton(
                    scale(pygame.Rect((620, 400), (300, 300))),
                    pygame.transform.scale(game.choose_cats[u].sprite, (300, 300)),
                    cat_object=game.choose_cats[u])

        for u in range(6, 12):
            if game.choose_cats[u] in [self.leader, self.deputy, self.med_cat] + self.members:
                self.elements["cat" + str(u)] = self.elements["cat" + str(u)] = UISpriteButton(
                    scale(pygame.Rect((620, 400), (300, 300))),
                    pygame.transform.scale(game.choose_cats[u].sprite, (300, 300)),
                    cat_object=game.choose_cats[u])
        
    def open_name_cat(self):
        """Opens the name clan screen"""
        
        self.clear_all_page()
        
        self.elements["leader_image"] = pygame_gui.elements.UIImage(scale(pygame.Rect((580, 300), (400, 400))),
                                                                    pygame.transform.scale(
                                                                        self.your_cat.sprite,
                                                                        (200, 200)), manager=MANAGER)
        if game.settings["dark mode"]:
            self.elements['background'] = pygame_gui.elements.UIImage(scale(pygame.Rect((0, 0), (1600, 1400))),
                                                                    MakeClanScreen.your_name_img_dark, manager=MANAGER)
        else:
            self.elements['background'] = pygame_gui.elements.UIImage(scale(pygame.Rect((0, 0), (1600, 1400))),
                                                                    MakeClanScreen.your_name_img, manager=MANAGER)

        self.elements['text1'] = pygame_gui.elements.UIImage(scale(pygame.Rect((520, 730), (796, 52))),
                                                                  MakeClanScreen.your_name_txt1, manager=MANAGER)
        self.elements['text2'] = pygame_gui.elements.UIImage(scale(pygame.Rect((520, 790), (536, 52))),
                                                                  MakeClanScreen.your_name_txt2, manager=MANAGER)
        self.elements['background'].disable()

        self.elements["version_background"] = UIImageButton(scale(pygame.Rect((1450, 1344), (1400, 55))), "", object_id="blank_button", manager=MANAGER)
        self.elements["version_background"].disable()

        if game.settings['fullscreen']:
            version_number = pygame_gui.elements.UILabel(
                pygame.Rect((1500, 1350), (-1, -1)), get_version_info().version_number[0:8],
                object_id=get_text_box_theme())
            # Adjust position
            version_number.set_position(
                (1600 - version_number.get_relative_rect()[2] - 8,
                1400 - version_number.get_relative_rect()[3]))
        else:
            version_number = pygame_gui.elements.UILabel(
                pygame.Rect((700, 650), (-1, -1)), get_version_info().version_number[0:8],
                object_id=get_text_box_theme())
            # Adjust position
            version_number.set_position(
                (800 - version_number.get_relative_rect()[2] - 8,
                700 - version_number.get_relative_rect()[3]))

        self.refresh_cat_images_and_info2()
        
        self.sub_screen = 'choose name'
        
        self.elements["random"] = UIImageButton(scale(pygame.Rect((570, 895), (68, 68))), "",
                                                object_id="#random_dice_button"
                                                , manager=MANAGER)

        self.elements["error"] = pygame_gui.elements.UITextBox("", scale(pygame.Rect((506, 1310), (596, -1))),
                                                               manager=MANAGER,
                                                               object_id="#default_dark", visible=False)
        self.main_menu.kill()
        self.main_menu = UIImageButton(scale(pygame.Rect((100, 100), (306, 60))), "", object_id="#main_menu_button"
                                       , manager=MANAGER)

        self.elements['previous_step'] = UIImageButton(scale(pygame.Rect((506, 1290), (294, 60))), "",
                                                       object_id="#previous_step_button", manager=MANAGER)
        self.elements['next_step'] = UIImageButton(scale(pygame.Rect((800, 1290), (294, 60))), "",
                                                   object_id="#next_step_button", manager=MANAGER)
        self.elements["name_entry"] = pygame_gui.elements.UITextEntryLine(scale(pygame.Rect((650, 900), (280, 58)))
                                                                          , manager=MANAGER, initial_text=self.your_cat.name.prefix)
        self.elements["name_entry"].set_allowed_characters(
            list("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_- "))
        self.elements["name_entry"].set_text_length_limit(11)

        if game.settings['dark mode']:
            self.elements["clan"] = pygame_gui.elements.UITextBox("-kit",
                                                              scale(pygame.Rect((870, 905), (200, 50))),
                                                              object_id="#text_box_30_horizcenter_light",
                                                              manager=MANAGER)
        
        else:
            self.elements["clan"] = pygame_gui.elements.UITextBox("-kit",
                                                              scale(pygame.Rect((870, 905), (200, 50))),
                                                              object_id="#text_box_30_horizcenter",
                                                              manager=MANAGER)
        


    def open_name_clan(self):
        """Opens the name Clan screen"""
        self.clear_all_page()
        self.sub_screen = "name clan"

        # Create all the elements.
        self.elements["random"] = UIImageButton(
            scale(pygame.Rect((448, 1190), (68, 68))),
            "",
            object_id="#random_dice_button",
            manager=MANAGER,
        )

        self.elements["error"] = pygame_gui.elements.UITextBox("", scale(pygame.Rect((506, 1340), (596, -1))),
                                                               manager=MANAGER,
                                                               object_id="#default_dark", visible=False)

        self.elements['previous_step'] = UIImageButton(scale(pygame.Rect((506, 1290), (294, 60))), "",
                                                       object_id="#previous_step_button", manager=MANAGER)
        self.elements['next_step'] = UIImageButton(scale(pygame.Rect((800, 1290), (294, 60))), "",
                                                   object_id="#next_step_button", manager=MANAGER)
        self.elements['next_step'].disable()
        self.elements["name_entry"] = pygame_gui.elements.UITextEntryLine(scale(pygame.Rect((530, 1195), (280, 58)))
                                                                          , manager=MANAGER)
        self.elements["name_entry"].set_allowed_characters(
            list("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_- ")
        )
        self.elements["name_entry"].set_text_length_limit(11)
        self.elements["clan"] = pygame_gui.elements.UITextBox("-Clan",
                                                              scale(pygame.Rect((750, 1200), (200, 50))),
                                                              object_id="#text_box_30_horizcenter_light",
                                                              manager=MANAGER)
        self.elements["reset_name"] = UIImageButton(scale(pygame.Rect((910, 1190), (268, 60))), "",
                                                    object_id="#reset_name_button", manager=MANAGER)
        
        if game.settings['dark mode']:
            self.elements["clan_size"] = pygame_gui.elements.UITextBox("Clan Size: ",
                                                              scale(pygame.Rect((400, 110), (200, 50))),
                                                              object_id="#text_box_30_horizcenter_light",
                                                              manager=MANAGER)
        else:
            self.elements["clan_size"] = pygame_gui.elements.UITextBox("Clan Size: ",
                                                              scale(pygame.Rect((400, 110), (200, 50))),
                                                              object_id="#text_box_30_horizcenter",
                                                              manager=MANAGER)

        if game.settings['dark mode']:
            self.elements["clan_age"] = pygame_gui.elements.UITextBox("Clan Age: ",
                                                              scale(pygame.Rect((400, 195), (200, 60))),
                                                              object_id="#text_box_30_horizcenter_light",
                                                              manager=MANAGER)
        else:
            self.elements["clan_age"] = pygame_gui.elements.UITextBox("Clan Age: ",
                                                              scale(pygame.Rect((400, 195), (200, 60))),
                                                              object_id="#text_box_30_horizcenter",
                                                              manager=MANAGER)
        
        self.elements["small"] = UIImageButton(scale(pygame.Rect((600,100), (192, 60))), "Small", object_id="#clan_size_small", manager=MANAGER)

        self.elements["medium"] = UIImageButton(scale(pygame.Rect((850,100), (192, 60))), "Medium", object_id="#clan_size_medium", manager=MANAGER)
        
        self.elements["large"] = UIImageButton(scale(pygame.Rect((1100,100), (192, 60))), "Large", object_id="#clan_size_large", manager=MANAGER)

        self.elements["medium"].disable()

        self.elements["established"] = UIImageButton(scale(pygame.Rect((600,200), (192, 60))), "Old", object_id="#clan_age_old", tool_tip_text="The Clan has existed for many moons and cats' backstories will reflect this.",manager=MANAGER)
        self.elements["new"] = UIImageButton(scale(pygame.Rect((850,200), (192, 60))), "New", object_id="#clan_age_new", tool_tip_text="The Clan is newly established and cats' backstories will reflect this.", manager=MANAGER)
        self.elements["established"].disable()

    def clan_name_header(self):
        self.elements["name_backdrop"] = pygame_gui.elements.UIImage(
            scale(pygame.Rect((584, 200), (432, 100))),
            MakeClanScreen.clan_frame_img,
            manager=MANAGER,
        )
        self.elements["clan_name"] = pygame_gui.elements.UITextBox(
            self.clan_name + "Clan",
            scale(pygame.Rect((585, 212), (432, 100))),
            object_id="#text_box_30_horizcenter_light",
            manager=MANAGER,
        )

    def open_choose_leader(self):
        """Set up the screen for the choose leader phase."""
        self.clear_all_page()
        self.sub_screen = "choose leader"

        if game.settings['dark mode']:
            self.elements['background'] = pygame_gui.elements.UIImage(scale(pygame.Rect((500, 1000), (600, 70))),
                                                                  MakeClanScreen.leader_img_dark, manager=MANAGER)
        else:
            self.elements['background'] = pygame_gui.elements.UIImage(scale(pygame.Rect((500, 1000), (600, 70))),
                                                                  MakeClanScreen.leader_img, manager=MANAGER)

        self.elements["background"].disable()
        self.clan_name_header()

        # Roll_buttons
        x_pos = 310
        y_pos = 470
        self.elements["roll1"] = UIImageButton(
            scale(pygame.Rect((x_pos, y_pos), (68, 68))),
            "",
            object_id="#random_dice_button",
            manager=MANAGER,
        )
        y_pos += 80
        self.elements["roll2"] = UIImageButton(
            scale(pygame.Rect((x_pos, y_pos), (68, 68))),
            "",
            object_id="#random_dice_button",
            manager=MANAGER,
        )
        y_pos += 80
        self.elements["roll3"] = UIImageButton(
            scale(pygame.Rect((x_pos, y_pos), (68, 68))),
            "",
            object_id="#random_dice_button",
            manager=MANAGER,
        )

        _tmp = 160
        if self.rolls_left == -1:
            _tmp += 5
        self.elements["dice"] = UIImageButton(
            scale(pygame.Rect((_tmp, 870), (68, 68))),
            "",
            object_id="#random_dice_button",
            manager=MANAGER,
        )
        del _tmp
        self.elements["reroll_count"] = pygame_gui.elements.UILabel(
            scale(pygame.Rect((200, 880), (100, 50))),
            str(self.rolls_left),
            object_id=get_text_box_theme(""),
            manager=MANAGER,
        )

        if game.config["clan_creation"]["rerolls"] == 3:
            if self.rolls_left <= 2:
                self.elements["roll1"].disable()
            if self.rolls_left <= 1:
                self.elements["roll2"].disable()
            if self.rolls_left == 0:
                self.elements["roll3"].disable()
            self.elements["dice"].hide()
            self.elements["reroll_count"].hide()
        else:
            if self.rolls_left == 0:
                self.elements["dice"].disable()
            elif self.rolls_left == -1:
                self.elements["reroll_count"].hide()
            self.elements["roll1"].hide()
            self.elements["roll2"].hide()
            self.elements["roll3"].hide()

        # info for chosen cats:
        if game.settings['dark mode']:
            self.elements['cat_info'] = pygame_gui.elements.UITextBox("", scale(pygame.Rect((880, 450), (230, 300))),
                                                                    visible=False, object_id="#text_box_22_horizleft_spacing_95_dark",
                                                                    manager=MANAGER)
        else:
            self.elements['cat_info'] = pygame_gui.elements.UITextBox("", scale(pygame.Rect((880, 450), (230, 300))),
                                                                    visible=False, object_id=get_text_box_theme("#text_box_22_horizleft_spacing_95"),
                                                                    manager=MANAGER)
        self.elements['cat_name'] = pygame_gui.elements.UITextBox("", scale(pygame.Rect((300, 350), (1000, 110))),
                                                                  visible=False,
                                                                  object_id=get_text_box_theme(
                                                                      "#text_box_30_horizcenter"),
                                                                  manager=MANAGER)

        self.elements['select_cat'] = UIImageButton(scale(pygame.Rect((706, 720), (190, 60))),
                                                    "",
                                                    object_id="#recruit_button",
                                                    visible=False,
                                                    manager=MANAGER)
        

        # Next and previous buttons
        self.elements['previous_step'] = UIImageButton(scale(pygame.Rect((506, 1290), (294, 60))), "",
                                                       object_id="#previous_step_button", manager=MANAGER)
        self.elements['next_step'] = UIImageButton(scale(pygame.Rect((800, 1290), (294, 60))), "",
                                                   object_id="#next_step_button", manager=MANAGER)
        self.elements['next_step'].disable()

        self.elements['customize'] = UIImageButton(scale(pygame.Rect((100,200),(236,60))), "", object_id="#customize_button", manager=MANAGER,  tool_tip_text = "Customize your own cat")

        # draw cats to choose from
        self.refresh_cat_images_and_info()
    
    def randomize_custom_cat(self):
        pelts = list(Pelt.sprites_names.keys())
        pelts.remove("Tortie")
        pelts.remove("Calico")
        pelts.remove("TwoColour")
        pelts_tortie = pelts.copy()
        pelts_tortie.remove("SingleColour")
        # pelts_tortie.remove("TwoColour")
        # pelts_tortie.append("Single")
        permanent_conditions = ['born without a leg', 'weak leg', 'twisted leg', 'born without a tail', 'paralyzed', 'raspy lungs', 'wasting disease', 'blind', 'one bad eye', 'failing eyesight', 'partial hearing loss', 'deaf', 'constant joint pain', 'seizure prone', 'allergies', 'persistent headaches']

        white_patches = ["FULLWHITE"] + Pelt.little_white + Pelt.mid_white + Pelt.high_white + Pelt.mostly_white
        self.pname= random.choice(pelts) if random.randint(1,3) == 1 else "Tortie"
        self.length=random.choice(["short", "medium", "long"])
        self.colour=random.choice(Pelt.pelt_colours)
        self.white_patches= choice(white_patches) if random.randint(1,2) == 1 else None
        self.eye_colour=choice(Pelt.eye_colours)
        self.eye_colour2=choice(Pelt.eye_colours) if random.randint(1,10) == 1 else None
        self.tortiebase=choice(Pelt.tortiebases)
        self.tortiecolour=choice(Pelt.pelt_colours)
        self.pattern=choice(Pelt.tortiepatterns)
        self.tortiepattern=choice(pelts_tortie)
        self.vitiligo=choice(Pelt.vit) if random.randint(1,20) == 1 else None
        self.points=choice(Pelt.point_markings) if random.randint(1,5) == 1 else None
        self.scars=[choice(Pelt.scars1 + Pelt.scars2 + Pelt.scars3)] if random.randint(1,10) == 1 else []
        self.tint=choice(["pink", "gray", "red", "orange", "black", "yellow", "purple", "blue","dilute","warmdilute","cooldilute"]) if random.randint(1,5) == 1 else None
        self.skin=choice(Pelt.skin_sprites)
        self.white_patches_tint=choice(["offwhite", "cream", "darkcream", "gray", "pink"]) if random.randint(1,5) == 1 else None
        self.reverse= False if random.randint(1,2) == 1 else True
        self.skill = "Random"
        self.sex = random.choice(["male", "female"])
        self.personality = choice(['troublesome', 'lonesome', 'impulsive', 'bullying', 'attention-seeker', 'charming', 'daring', 'noisy', 'nervous', 'quiet', 'insecure', 'daydreamer', 'sweet', 'polite', 'know-it-all', 'bossy', 'disciplined', 'patient', 'manipulative', 'secretive', 'rebellious', 'grumpy', 'passionate', 'honest', 'leader-like', 'smug'])

        self.accessories = [choice(Pelt.plant_accessories + Pelt.wild_accessories + Pelt.collars + Pelt.flower_accessories + Pelt.plant2_accessories + Pelt.snake_accessories + Pelt.smallAnimal_accessories + Pelt.deadInsect_accessories + Pelt.aliveInsect_accessories + Pelt.fruit_accessories + Pelt.crafted_accessories + Pelt.tail2_accessories)] if random.randint(1,5) == 1 else []

        self.accessories = [choice(Pelt.plant_accessories + Pelt.wild_accessories + Pelt.collars + Pelt.flower_accessories + Pelt.plant2_accessories + Pelt.snake_accessories + Pelt.smallAnimal_accessories + Pelt.deadInsect_accessories + Pelt.aliveInsect_accessories + Pelt.fruit_accessories + Pelt.crafted_accessories + Pelt.tail2_accessories)] if random.randint(1,5) == 1 else []
        self.permanent_condition = choice(permanent_conditions) if random.randint(1,30) == 1 else None

        if self.permanent_condition == "born without a tail":
            for i in self.notail_accs:
                if i in self.accessories:
                    self.accessories = []
                    self.inventory = []

        # scars for conditions
        self.paralyzed = True if self.permanent_condition == "paralyzed" else False
        if self.permanent_condition == "born without a tail":
            self.scars = ["NOTAIL"]
        elif self.permanent_condition == "born without a leg":
            self.scars = ["NOPAW"]
        elif self.permanent_condition == "blind":
            if random.randint(0,10) == 1:
                self.scars = ["BOTHBLIND"]
        elif self.permanent_condition == "one bad eye":
            if random.randint(0,10) == 1:
                self.scars = [random.choice(["LEFTBLIND", "RIGHTBLIND", "BRIGHTHEART"])]
        elif self.permanent_condition in ["deaf", "partial hearing loss"]:
            if random.randint(0,10):
                self.scars = [random.choice(["LEFTEAR", "RIGHTEAR", "NOEAR"])]

        self.faith = random.choice(["flexible", "starclan", "dark forest", "neutral"])

        self.kitten_sprite=random.randint(0,2)
        self.adolescent_pose = random.randint(3,5)
        if self.length in ["short", "medium"]:
            self.adult_pose = random.randint(6,8)
        else:
            self.adult_pose = random.randint(9,11)
        self.elder_pose = random.randint(12,14)

        if self.pname == "Tortie":
            self.tortie_enabled = True
        else:
            self.tortie_enabled = False

    def open_customize_cat(self):

        self.clear_all_page()
        self.sub_screen = "customize cat"
        pelt2 = Pelt(
            name=self.pname,
            length=self.length,
            colour=self.colour,
            white_patches=self.white_patches,
            eye_color=self.eye_colour,
            eye_colour2=self.eye_colour2,
            tortiebase=self.tortiebase,
            tortiecolour=self.tortiecolour,
            pattern=self.pattern,
            tortiepattern=self.tortiepattern.lower() if self.tortiepattern else None,
            vitiligo=self.vitiligo,
            points=self.points,
            accessory=None,
            paralyzed=self.paralyzed,
            scars=self.scars,
            tint=self.tint,
            skin=self.skin,
            white_patches_tint=self.white_patches_tint,
            kitten_sprite=self.kitten_sprite if self.kitten_sprite else 0,
            adol_sprite=self.adolescent_pose if self.adolescent_pose else 3,
            adult_sprite=self.adult_pose if self.adult_pose else 6,
            senior_sprite=self.elder_pose if self.elder_pose else 12,
            reverse=self.reverse,
            accessories=self.accessories,
            inventory=self.accessories
        )
        if self.length == 'long' and self.adult_pose < 9:
            pelt2.cat_sprites['young adult'] = self.adult_pose + 9
            pelt2.cat_sprites['adult'] = self.adult_pose + 9
            pelt2.cat_sprites['senior adult'] = self.adult_pose + 9

        self.elements["left"] = UIImageButton(scale(pygame.Rect((35, 620), (102, 134))), "", object_id="#arrow_right_fancy",
                                                 starting_height=2)
        
        self.elements["right"] = UIImageButton(scale(pygame.Rect((1460, 620), (102, 134))), "", object_id="#arrow_left_fancy",
                                             starting_height=2)
        if self.page == 0:
            self.elements['left'].disable()
        else:
            self.elements['left'].enable()
        
        if self.page == 3:
            self.elements['right'].disable()
        else:
            self.elements['right'].enable()

       
        
        column1_x = 150  # x-coordinate for column 1
        column2_x = 450  # x-coordinate for column 2
        column3_x = 900  # x-coordinate for column 3
        column4_x = 1200
        x_align = 340
        x_align2 = 200
        x_align3 = 250
        y_pos = [80, 215, 280, 415, 480, 615, 680, 815, 880, 1015, 1080]


        self.elements['random_customize'] = UIImageButton(
            scale(pygame.Rect((80, 200), (68, 68))),
            "",
            object_id="#random_dice_button",
            starting_height=2
            )
        

        pelts = list(Pelt.sprites_names.keys())
        pelts.remove("Tortie")
        pelts.remove("Calico")
        pelts.remove("TwoColour")
        
        pelts_tortie = pelts.copy()
        # pelts_tortie.remove("SingleColour")
        # pelts_tortie.remove("TwoColour")
        
        permanent_conditions = ['born without a leg', 'weak leg', 'twisted leg', 'born without a tail', 'paralyzed', 'raspy lungs', 'wasting disease', 'blind', 'one bad eye', 'failing eyesight', 'partial hearing loss', 'deaf', 'constant joint pain', 'seizure prone', 'allergies', 'persistent headaches']

    # background images
    # values are ((x position, y position), (x width, y height))


        if game.settings['dark mode']:
            self.elements['spritebg'] = pygame_gui.elements.UIImage(scale(pygame.Rect((550, 250), (500, 570))),
                                                                  MakeClanScreen.sprite_preview_bg_dark, manager=MANAGER)
        else:
            self.elements['spritebg'] = pygame_gui.elements.UIImage(scale(pygame.Rect((550, 250), (500, 570))),
                                                                  MakeClanScreen.sprite_preview_bg, manager=MANAGER)

        c_moons = 1
        if self.preview_age == "adolescent":
            c_moons = 6
        elif self.preview_age == "adult":
            c_moons = 12
        elif self.preview_age == "elder":
            c_moons = 121
        self.custom_cat = Cat(moons = c_moons, pelt=pelt2, loading_cat=True)
        self.custom_cat.sprite = generate_sprite(self.custom_cat)
        self.elements["sprite"] = UISpriteButton(scale(pygame.Rect
                                         ((630,280), (350, 350))),
                                   self.custom_cat.sprite,
                                   self.custom_cat.ID,
                                   starting_height=0, manager=MANAGER)
        
        self.elements["randomise_selection"] = UIImageButton(
            scale(pygame.Rect((770, 700), (68, 68))),
            "",
            object_id="#random_dice_button",
            starting_height=2
            )

        self.elements["cycle_left"] = UIImageButton(
            scale(pygame.Rect((690, 700), (68, 68))),
            "",
            object_id="#arrow_left_button",
            starting_height=2
            )

        self.elements["cycle_right"] = UIImageButton(
            scale(pygame.Rect((850, 700), (68, 68))),
            "",
            object_id="#arrow_right_button",
            starting_height=2
            )
        
        if self.page == 0:
            # PAGE 0
            # poses

            # Preview age
            x_pos = 1100
            self.elements['preview text'] = pygame_gui.elements.UITextBox(
                    'Preview Age',
                    scale(pygame.Rect((x_pos, 250),(340, 68))),
                    object_id=get_text_box_theme("#text_box_30_horizcenter"), manager=MANAGER
                )
            button_count = 0
            age_y_pos = 350
            for i in ["kitten", "adolescent", "adult", "elder"]:
                self.preview_age_buttons[i] = UIImageButton(
                    scale(pygame.Rect((x_pos, age_y_pos), (150, 68))),
                    i,
                    object_id="",
                    manager=MANAGER
                    )
                x_pos += 190
                button_count += 1
                if button_count == 2:
                    age_y_pos += 80
                    x_pos = 1100
            # puts the last two buttons on the bottom so theyre not all in one line

            # fur length
            x_pos = 1100
            self.elements['fur_length_text'] = pygame_gui.elements.UITextBox(
                    'Fur Length',
                    scale(pygame.Rect((x_pos, 600),(340, 68))),
                    object_id=get_text_box_theme("#text_box_30_horizcenter"), manager=MANAGER
                )
            button_count = 0
            fur_y_pos = 700
            for i in ["short", "medium", "long"]:
                self.fur_length_buttons[i] = UIImageButton(
                    scale(pygame.Rect((x_pos, fur_y_pos), (150, 68))),
                    i,
                    object_id="",
                    manager=MANAGER
                    )
                x_pos += 190
                button_count += 1
                if button_count == 2:
                    fur_y_pos += 80
                    x_pos = 1200

            x_pos = 1200
            self.elements['reverse text'] = pygame_gui.elements.UITextBox(
                'Reverse',
                scale(pygame.Rect((1100, 890),(340, 68))),
                object_id=get_text_box_theme("#text_box_30_horizcenter"),
                manager=MANAGER
                )
            for i in [True, False]:
                self.reverse_buttons[str(i)] = UIImageButton(
                    scale(pygame.Rect((x_pos, 990), (68, 68))),
                    str(i)[0],
                    object_id="",
                    manager=MANAGER
                    )
                x_pos += 80

            # Kitten poses
            x_pos = 250
            self.elements['kitten_pose_text'] = pygame_gui.elements.UITextBox(
                    'Kitten',
                    scale(pygame.Rect((x_pos, 330), (230, 60))),
                    object_id=get_text_box_theme("#text_box_30_horizcenter"), manager=MANAGER
                )

            for pose in range(0,3):
                self.kitten_pose_buttons[str(pose)] = UIImageButton(
                    scale(pygame.Rect((x_pos, 400), (68, 68))),
                    str(pose),
                    object_id="",
                    manager=MANAGER
                    )
                x_pos += 80
                
            # Apprentice poses
            x_pos = 250
            self.elements['adolescent_pose_text'] = pygame_gui.elements.UITextBox(
                    'Apprentice',
                    scale(pygame.Rect((x_pos, 520),(230, 60))),
                    object_id=get_text_box_theme("#text_box_30_horizcenter"),
                    manager=MANAGER
                )
            for pose in range(3,6):
                self.adolescent_pose_buttons[str(pose)] = UIImageButton(
                    scale(pygame.Rect((x_pos, 590), (68, 68))),
                    str(pose),
                    object_id="",
                    manager=MANAGER
                    )
                x_pos += 80

            x_pos = 250
            if self.length in ["short", "medium"]:
                pose_range = range(6,9)
            else:
                pose_range = range(9,12)

            self.elements['adult_pose_text'] = pygame_gui.elements.UITextBox(
                'Adult',
                scale(pygame.Rect((x_pos, 720),(230, 60))),
                object_id=get_text_box_theme("#text_box_30_horizcenter"), manager=MANAGER
            )

            for pose in pose_range:
                self.adult_pose_buttons[str(pose)] = UIImageButton(
                    scale(pygame.Rect((x_pos, 790), (68, 68))),
                    str(pose),
                    object_id="",
                    manager=MANAGER
                    )
                x_pos += 80

            x_pos = 250
            self.elements['elder_pose_text'] = pygame_gui.elements.UITextBox(
                    'Elder',
                    scale(pygame.Rect((x_pos, 920),(230, 60))),
                    object_id=get_text_box_theme("#text_box_30_horizcenter"),
                    manager=MANAGER
                )
            for pose in range(12,15):
                self.elder_pose_buttons[str(pose)] = UIImageButton(
                    scale(pygame.Rect((x_pos, 990), (68, 68))),
                    str(pose),
                    object_id="",
                    manager=MANAGER
                    )
                x_pos += 80
        
        if self.page == 1:

            if self.current_selection not in [
                "pelt_pattern", "pelt_colour", "white_patches",
                "points", "vitiligo", "tortie_pattern",
                "tortie_colour", "tortie_patches"
                ]:
                self.current_selection = "pelt_pattern"

            self.elements["scroll_container"] = pygame_gui.elements.UIScrollingContainer(
                scale(pygame.Rect((1100, 170), (350, 960))),
                allow_scroll_x=False
                )
            
            x_pos = 265
            selection_y_pos = 200
            for i in ["pelt_pattern", "pelt_colour", "white_patches", "points", "vitiligo"]:
                self.current_selection_buttons[i] = UIImageButton(
                    scale(pygame.Rect((x_pos, selection_y_pos), (190, 80))),
                    i.replace("_", " ").capitalize(),
                    object_id="",
                    manager=MANAGER
                    )
                selection_y_pos += 100

            self.elements["tortie_text"] = pygame_gui.elements.UITextBox(
                        "Tortie",
                        scale(pygame.Rect((x_pos, selection_y_pos + 20),(130, 68))),
                        object_id=get_text_box_theme("#text_box_30_horizleft"),
                        manager=MANAGER
                    )
            if self.tortie_enabled is True:
                self.elements["tortie_checkbox"] = UIImageButton(
                    scale(pygame.Rect((x_pos + 120, selection_y_pos + 25), (60, 60))),
                    "",
                    object_id="#checked_checkbox",
                    manager=MANAGER
                    )
            else:
                self.elements["tortie_checkbox"] = UIImageButton(
                    scale(pygame.Rect((x_pos + 120, selection_y_pos + 25), (60, 60))),
                    "",
                    object_id="#unchecked_checkbox",
                    manager=MANAGER
                    )
            
            selection_y_pos += 150
            for i in ["tortie_pattern", "tortie_colour", "tortie_patches"]:
                self.current_selection_buttons[i] = UIImageButton(
                    scale(pygame.Rect((x_pos, selection_y_pos), (190, 80))),
                    i.replace("_", " ").capitalize(),
                    object_id="",
                    manager=MANAGER
                    )
                selection_y_pos += 100

                if self.tortie_enabled is False:
                    self.current_selection_buttons[i].disable()
                else:
                    self.current_selection_buttons[i].enable()

            x_pos = 0
            pelt_y_pos = 0
            if self.current_selection == "pelt_pattern":
                for pelt in pelts:
                    # pelt checkboxes
                    self.pelt_pattern_buttons[pelt] = UIImageButton(
                    scale(pygame.Rect((x_pos, pelt_y_pos + 8), (68, 68))),
                    "",
                    object_id="#unchecked_checkbox",
                    container=self.elements["scroll_container"],
                    manager=MANAGER
                    )
                    # now the labels
                    self.pelt_pattern_names[pelt] = pygame_gui.elements.UITextBox(
                        str(pelt),
                        scale(pygame.Rect((x_pos + 65, pelt_y_pos),(400, 68))),
                        object_id=get_text_box_theme("#text_box_30_horizleft"),
                        container=self.elements["scroll_container"],
                        manager=MANAGER
                    )
                    pelt_y_pos += 80
            elif self.current_selection == "pelt_colour":
                for colour in Pelt.pelt_colours:
                    self.pelt_colour_buttons[colour] = UIImageButton(
                    scale(pygame.Rect((x_pos, pelt_y_pos + 8), (68, 68))),
                    "",
                    object_id="#unchecked_checkbox",
                    container=self.elements["scroll_container"],
                    manager=MANAGER
                    )
                    self.pelt_colour_names[colour] = pygame_gui.elements.UITextBox(
                        str(colour).lower().capitalize(),
                        scale(pygame.Rect((x_pos + 65, pelt_y_pos),(400, 68))),
                        object_id=get_text_box_theme("#text_box_30_horizleft"),
                        container=self.elements["scroll_container"],
                        manager=MANAGER
                    )
                    pelt_y_pos += 80

                tint_x_pos = 512
                tint_y_pos = 900
                for tint in [
                    "none", "pink", "gray", "red", "orange", "black",
                    "yellow", "purple", "blue", "dilute", "warmdilute", "cooldilute"
                    ]:
                    self.tint_buttons[tint] = UIImageButton(
                        scale(pygame.Rect((tint_x_pos, tint_y_pos), (80, 80))),
                        tint,
                        object_id="",
                        manager=MANAGER
                        )
                    tint_x_pos += 100
                    if tint == "black":
                        tint_y_pos += 100
                        tint_x_pos = 512

            elif self.current_selection == "white_patches":
                # search bar first
                self.elements["search_button"] = UIImageButton(
                    scale(pygame.Rect((950, 1000), (68, 68))),
                    "",
                    object_id="#magnifying_glass_button",
                    manager=MANAGER
                    )
                self.elements["clear"] = UIImageButton(
                    scale(pygame.Rect((594, 1000), (68, 68))),
                    "",
                    object_id="#large_x_button",
                    manager=MANAGER
                    )
                self.elements["search_bar_image"] = pygame_gui.elements.UIImage(
                    scale(pygame.Rect((689, 1000), (236, 68))),
                    pygame.image.load("resources/images/search_bar.png").convert_alpha(),
                    manager=MANAGER
                    )
                self.elements["search_bar"] = pygame_gui.elements.UITextEntryLine(
                    scale(pygame.Rect((709, 1005), (205, 55))),
                    object_id="#search_entry_box",
                    initial_text=self.previous_search_text,
                    manager=MANAGER
                    )
                patch_list = Pelt.little_white + Pelt.mid_white + Pelt.high_white + Pelt.mostly_white + ["FULLWHITE"]
                if self.customiser_sort == "alphabetical":
                    patch_list.sort()

                new_patch_list = []
                searched = self.search_text
                if searched not in ["", "search"]:
                    for patch in patch_list:
                        if searched in patch.lower():
                            new_patch_list.append(patch)
                else:
                    new_patch_list = patch_list

                # now draw the buttons
                for patch in ["None"] + new_patch_list:
                    self.white_patches_buttons[patch] = UIImageButton(
                    scale(pygame.Rect((x_pos, pelt_y_pos + 8), (68, 68))),
                    "",
                    object_id="#unchecked_checkbox",
                    container=self.elements["scroll_container"],
                    manager=MANAGER
                    )
                    self.white_patches_names[patch] = pygame_gui.elements.UITextBox(
                        str(patch).lower().capitalize(),
                        scale(pygame.Rect((x_pos + 65, pelt_y_pos),(400, 68))),
                        object_id=get_text_box_theme("#text_box_30_horizleft"),
                        container=self.elements["scroll_container"],
                        manager=MANAGER
                    )
                    pelt_y_pos += 80
                filter_x_pos = 1125
                for sort in ["default", "alphabetical"]:
                    self.elements[sort] = UIImageButton(
                        scale(pygame.Rect((filter_x_pos, 100), (140, 60))),
                        "",
                        object_id=f"#{sort}_sort_button",
                        manager=MANAGER
                        )
                    filter_x_pos += 140

                tint_x_pos = 536
                tint_y_pos = 900
                for tint in [
                    "none", "offwhite", "cream", "darkcream", "gray", "pink"
                    ]:
                    self.white_patches_tint_buttons[tint] = UIImageButton(
                        scale(pygame.Rect((tint_x_pos, tint_y_pos), (80, 80))),
                        "",
                        object_id=f"#patches_tint_{tint}",
                        manager=MANAGER
                        )
                    tint_x_pos += 90
                    if tint == "pink":
                        tint_y_pos += 100
                        tint_x_pos = 512
                    # ^^ to make adding tint buttons a bit easier

            elif self.current_selection == "points":
                for point in ["None"] + Pelt.point_markings:
                    self.points_buttons[point] = UIImageButton(
                    scale(pygame.Rect((x_pos, pelt_y_pos + 8), (68, 68))),
                    "",
                    object_id="#unchecked_checkbox",
                    container=self.elements["scroll_container"],
                    manager=MANAGER
                    )
                    self.points_names[point] = pygame_gui.elements.UITextBox(
                        str(point).lower().capitalize(),
                        scale(pygame.Rect((x_pos + 65, pelt_y_pos),(400, 68))),
                        object_id=get_text_box_theme("#text_box_30_horizleft"),
                        container=self.elements["scroll_container"],
                        manager=MANAGER
                    )
                    pelt_y_pos += 80
            elif self.current_selection == "vitiligo":
                for patch in ["None"] + Pelt.vit:
                    self.vitiligo_buttons[patch] = UIImageButton(
                    scale(pygame.Rect((x_pos, pelt_y_pos + 8), (68, 68))),
                    "",
                    object_id="#unchecked_checkbox",
                    container=self.elements["scroll_container"],
                    manager=MANAGER
                    )
                    self.vitiligo_names[patch] = pygame_gui.elements.UITextBox(
                        str(patch).lower().capitalize(),
                        scale(pygame.Rect((x_pos + 65, pelt_y_pos),(400, 68))),
                        object_id=get_text_box_theme("#text_box_30_horizleft"),
                        container=self.elements["scroll_container"],
                        manager=MANAGER
                    )
                    pelt_y_pos += 80
            
            # TORTIES
            elif self.current_selection == "tortie_pattern":
                for pattern in pelts_tortie:
                    self.tortie_pattern_buttons[pattern] = UIImageButton(
                    scale(pygame.Rect((x_pos, pelt_y_pos + 8), (68, 68))),
                    "",
                    object_id="#unchecked_checkbox",
                    container=self.elements["scroll_container"],
                    manager=MANAGER
                    )
                    string = str(pattern).lower().capitalize()
                    if string == "Singlecolour":
                        string = "SingleColour"
                    self.tortie_pattern_names[pattern] = pygame_gui.elements.UITextBox(
                        string,
                        scale(pygame.Rect((x_pos + 65, pelt_y_pos),(400, 68))),
                        object_id=get_text_box_theme("#text_box_30_horizleft"),
                        container=self.elements["scroll_container"],
                        manager=MANAGER
                    )
                    pelt_y_pos += 80

                self.elements["match_base"] = UIImageButton(
                    scale(pygame.Rect((720, 930), (170, 68))),
                    "Match base",
                    object_id="",
                    manager=MANAGER
                    )

            elif self.current_selection == "tortie_colour":
                for colour in Pelt.pelt_colours:
                    self.tortie_colour_buttons[colour] = UIImageButton(
                    scale(pygame.Rect((x_pos, pelt_y_pos + 8), (68, 68))),
                    "",
                    object_id="#unchecked_checkbox",
                    container=self.elements["scroll_container"],
                    manager=MANAGER
                    )
                    self.tortie_colour_names[colour] = pygame_gui.elements.UITextBox(
                        str(colour).lower().capitalize(),
                        scale(pygame.Rect((x_pos + 65, pelt_y_pos),(400, 68))),
                        object_id=get_text_box_theme("#text_box_30_horizleft"),
                        container=self.elements["scroll_container"],
                        manager=MANAGER
                    )
                    pelt_y_pos += 80

            elif self.current_selection == "tortie_patches":
                for patch in Pelt.tortiepatterns:
                    self.tortie_patches_buttons[patch] = UIImageButton(
                    scale(pygame.Rect((x_pos, pelt_y_pos + 8), (68, 68))),
                    "",
                    object_id="#unchecked_checkbox",
                    container=self.elements["scroll_container"],
                    manager=MANAGER
                    )
                    self.tortie_patches_names[patch] = pygame_gui.elements.UITextBox(
                        str(patch).lower().capitalize(),
                        scale(pygame.Rect((x_pos + 65, pelt_y_pos),(400, 68))),
                        object_id=get_text_box_theme("#text_box_30_horizleft"),
                        container=self.elements["scroll_container"],
                        manager=MANAGER
                    )
                    pelt_y_pos += 80

        elif self.page == 2:

            if self.current_selection not in [
                "eye_colour", "heterochromia", "skin", "scar", "accessory"
                ]:
                self.current_selection = "eye_colour"

            self.elements["scroll_container"] = pygame_gui.elements.UIScrollingContainer(
                scale(pygame.Rect((1100, 170), (350, 960))),
                allow_scroll_x=False
                )

            x_pos = 265
            eye_y_pos = 0
            selection_y_pos = 300
            for i in ["eye_colour", "heterochromia", "skin", "scar", "accessory"]:
                self.current_selection_buttons[i] = UIImageButton(
                    scale(pygame.Rect((x_pos, selection_y_pos), (190, 80))),
                    i.replace("_", " ").capitalize(),
                    object_id="",
                    manager=MANAGER
                    )
                if i == "heterochromia":
                    selection_y_pos += 120
                if i == "skin":
                    selection_y_pos += 120
                selection_y_pos += 100

            if self.current_selection == "eye_colour":
                for colour in Pelt.eye_colours:
                    self.eye_colour_buttons[colour] = UIImageButton(
                    scale(pygame.Rect((0, eye_y_pos), (68, 68))),
                    "",
                    object_id="#unchecked_checkbox",
                    container=self.elements["scroll_container"],
                    manager=MANAGER
                    )
                    self.eye_colour_names[colour] = pygame_gui.elements.UITextBox(
                        str(colour).lower().capitalize(),
                        scale(pygame.Rect((0 + 65, eye_y_pos),(400, 68))),
                        object_id=get_text_box_theme("#text_box_30_horizleft"),
                        container=self.elements["scroll_container"],
                        manager=MANAGER
                    )
                    eye_y_pos += 80

            elif self.current_selection == "heterochromia":
                for colour in [None] + Pelt.eye_colours:
                    self.heterochromia_buttons[str(colour)] = UIImageButton(
                    scale(pygame.Rect((0, eye_y_pos), (68, 68))),
                    "",
                    object_id="#unchecked_checkbox",
                    container=self.elements["scroll_container"],
                    manager=MANAGER
                    )
                    self.heterochromia_names[str(colour)] = pygame_gui.elements.UITextBox(
                        str(colour).lower().capitalize(),
                        scale(pygame.Rect((0 + 65, eye_y_pos),(400, 68))),
                        object_id=get_text_box_theme("#text_box_30_horizleft"),
                        container=self.elements["scroll_container"],
                        manager=MANAGER
                    )
                    eye_y_pos += 80

            elif self.current_selection == "skin":
                for colour in Pelt.skin_sprites:
                    self.skin_buttons[str(colour)] = UIImageButton(
                    scale(pygame.Rect((0, eye_y_pos), (68, 68))),
                    "",
                    object_id="#unchecked_checkbox",
                    container=self.elements["scroll_container"],
                    manager=MANAGER
                    )
                    self.skin_names[str(colour)] = pygame_gui.elements.UITextBox(
                        str(colour).lower().capitalize(),
                        scale(pygame.Rect((0 + 65, eye_y_pos),(400, 68))),
                        object_id=get_text_box_theme("#text_box_30_horizleft"),
                        container=self.elements["scroll_container"],
                        manager=MANAGER
                    )
                    eye_y_pos += 80
            elif self.current_selection == "scar":
                for scar in ["None"] + Pelt.scars1 + Pelt.scars2 + Pelt.scars3:
                    self.scar_buttons[str(scar)] = UIImageButton(
                    scale(pygame.Rect((0, eye_y_pos), (68, 68))),
                    "",
                    object_id="#unchecked_checkbox",
                    container=self.elements["scroll_container"],
                    manager=MANAGER
                    )
                    self.scar_names[str(scar)] = pygame_gui.elements.UITextBox(
                        str(scar).lower().capitalize(),
                        scale(pygame.Rect((0 + 65, eye_y_pos),(400, 68))),
                        object_id=get_text_box_theme("#text_box_30_horizleft"),
                        container=self.elements["scroll_container"],
                        manager=MANAGER
                    )
                    eye_y_pos += 80
            elif self.current_selection == "accessory":

                self.elements["search_button"] = UIImageButton(
                    scale(pygame.Rect((950, 1000), (68, 68))),
                    "S",
                    object_id="#magnifying_glass_button",
                    manager=MANAGER
                    )
                self.elements["clear"] = UIImageButton(
                    scale(pygame.Rect((594, 1000), (68, 68))),
                    "C",
                    object_id="#large_x_button",
                    manager=MANAGER
                    )
                self.elements["search_bar_image"] = pygame_gui.elements.UIImage(
                    scale(pygame.Rect((689, 1000), (236, 68))),
                    pygame.image.load("resources/images/search_bar.png").convert_alpha(),
                    manager=MANAGER
                    )
                self.elements["search_bar"] = pygame_gui.elements.UITextEntryLine(
                    scale(pygame.Rect((709, 1005), (205, 55))),
                    object_id="#search_entry_box",
                    initial_text=self.previous_search_text,
                    manager=MANAGER
                    )
                acc_list = (Pelt.plant_accessories + Pelt.wild_accessories +
                    Pelt.collars + Pelt.flower_accessories +
                    Pelt.plant2_accessories + Pelt.snake_accessories +
                    Pelt.smallAnimal_accessories + Pelt.deadInsect_accessories +
                    Pelt.aliveInsect_accessories + Pelt.fruit_accessories +
                    Pelt.crafted_accessories + Pelt.tail2_accessories)
                if self.customiser_sort == "alphabetical":
                    acc_list.sort()

                new_acc_list = []
                searched = self.search_text
                if searched not in ["", "search"]:
                    for acc in acc_list:
                        if searched in str(self.ACC_DISPLAY[acc]["default"]).lower() or searched in acc.lower():
                            new_acc_list.append(acc)
                else:
                    new_acc_list = acc_list

                for acc in (
                    ["None"] + new_acc_list
                    ):
                    self.accessory_buttons[acc] = UIImageButton(
                    scale(pygame.Rect((0, eye_y_pos), (68, 68))),
                    "",
                    object_id="#unchecked_checkbox",
                    container=self.elements["scroll_container"],
                    manager=MANAGER
                    )

                    if acc != "None":
                        acc_name = str(acc)
                        if 15 <= len(acc_name):  # check name length
                            short_name = str(acc_name)[0:13]
                            acc_name = short_name + '...'
                    else:
                        acc_name = acc
                    self.accessory_names[str(acc)] = pygame_gui.elements.UITextBox(
                        acc_name.capitalize(),
                        scale(pygame.Rect((0 + 65, eye_y_pos),(400, 68))),
                        object_id=get_text_box_theme("#text_box_30_horizleft"),
                        container=self.elements["scroll_container"],
                        manager=MANAGER
                    )
                    eye_y_pos += 80

                filter_x_pos = 1125
                for sort in ["default", "alphabetical"]:
                    self.elements[sort] = UIImageButton(
                        scale(pygame.Rect((filter_x_pos, 100), (140, 60))),
                        "",
                        object_id=f"#{sort}_sort_button",
                        manager=MANAGER
                        )
                    filter_x_pos += 140

        elif self.page == 3:

            if self.current_selection not in [
                "condition", "trait", "skill", "faith", "sex"
                ]:
                self.current_selection = "condition"

            self.elements["scroll_container"] = pygame_gui.elements.UIScrollingContainer(
                scale(pygame.Rect((1100, 170), (350, 960))),
                allow_scroll_x=False
                )

            x_pos = 265
            selection_y_pos = 300
            for i in ["condition", "trait", "skill"]:
                self.current_selection_buttons[i] = UIImageButton(
                    scale(pygame.Rect((x_pos, selection_y_pos), (190, 80))),
                    i.replace("_", " ").capitalize(),
                    object_id="",
                    manager=MANAGER
                    )
                if i == "skill":
                    selection_y_pos += 120
                if i == "faith":
                    selection_y_pos += 120
                selection_y_pos += 100

            faith_x_pos = 217
            self.elements["faith_label"] = pygame_gui.elements.UITextBox(
                    "Faith",
                    scale(pygame.Rect((220, 750),(262, 50))),
                    object_id=get_text_box_theme("#text_box_30_horizcenter"),
                    manager=MANAGER
                )
            for faith in ["starclan", "neutral", "dark forest", "flexible"]:
                if faith == "starclan":
                    faith_text = "StarClan"
                elif faith == "dark forest":
                    faith_text = "Dark Forest"
                else:
                    faith_text = faith.capitalize()
                self.faith_buttons[faith] = UIImageButton(
                scale(pygame.Rect((faith_x_pos, 800), (68, 68))),
                "",
                object_id=f"#faith_{faith.replace(' ', '')}_button",
                tool_tip_text=faith_text,
                manager=MANAGER
                )
                faith_x_pos += 68

            sex_x_pos = 274
            self.elements["sex_label"] = pygame_gui.elements.UITextBox(
                    "Sex",
                    scale(pygame.Rect((220, 940),(262, 50))),
                    object_id=get_text_box_theme("#text_box_30_horizcenter"),
                    manager=MANAGER
                )
            for gender in ["male", "female"]:
                self.sex_buttons[gender] = UIImageButton(
                scale(pygame.Rect((sex_x_pos, 1000), (68, 68))),
                gender[0].upper(),
                object_id="",
                tool_tip_text=faith_text,
                manager=MANAGER
                )
                sex_x_pos += 80

            y_pos = 0
            if self.current_selection == "condition":
                for condition in ["None"] + permanent_conditions:
                    if condition != "None":
                        if 15 <= len(condition):
                            short_name = str(condition)[0:13]
                            condition_name = short_name + '...'
                        else:
                            condition_name = condition
                    else:
                        condition_name = "None"

                    self.condition_buttons[condition] = UIImageButton(
                    scale(pygame.Rect((0, y_pos), (68, 68))),
                    "",
                    object_id="#unchecked_checkbox",
                    container=self.elements["scroll_container"],
                    manager=MANAGER
                    )
                    self.condition_names[condition] = pygame_gui.elements.UITextBox(
                        condition_name.capitalize(),
                        scale(pygame.Rect((0 + 65, y_pos),(400, 68))),
                        object_id=get_text_box_theme("#text_box_30_horizleft"),
                        container=self.elements["scroll_container"],
                        manager=MANAGER
                    )
                    y_pos += 80

            y_pos = 0
            traits = ['troublesome', 'lonesome', 'impulsive', 'bullying', 'attention-seeker', 'charming', 'daring', 'noisy', 'nervous', 'quiet', 'insecure', 'daydreamer', 'sweet', 'polite', 'know-it-all', 'bossy', 'disciplined', 'patient', 'manipulative', 'secretive', 'rebellious', 'grumpy', 'passionate', 'honest', 'leader-like', 'smug']
            if self.current_selection == "trait":
                for trait in traits:
                    if 15 <= len(trait):
                        short_name = str(trait)[0:13]
                        trait_name = short_name + '...'
                    else:
                        trait_name = trait

                    self.trait_buttons[trait] = UIImageButton(
                    scale(pygame.Rect((0, y_pos), (68, 68))),
                    "",
                    object_id="#unchecked_checkbox",
                    container=self.elements["scroll_container"],
                    manager=MANAGER
                    )
                    self.trait_names[trait] = pygame_gui.elements.UITextBox(
                        trait_name.capitalize(),
                        scale(pygame.Rect((0 + 65, y_pos),(400, 68))),
                        object_id=get_text_box_theme("#text_box_30_horizleft"),
                        container=self.elements["scroll_container"],
                        manager=MANAGER
                    )
                    y_pos += 80

            if self.current_selection == "skill":
                for skill in ["Random"] + self.skills:
                    if 15 <= len(skill):
                        short_name = str(skill)[0:13]
                        skill_name = short_name + '...'
                    else:
                        skill_name = skill

                    self.skill_buttons[skill] = UIImageButton(
                    scale(pygame.Rect((0, y_pos), (68, 68))),
                    "",
                    object_id="#unchecked_checkbox",
                    container=self.elements["scroll_container"],
                    manager=MANAGER
                    )
                    self.skill_names[skill] = pygame_gui.elements.UITextBox(
                        skill_name.capitalize(),
                        scale(pygame.Rect((0 + 65, y_pos),(400, 68))),
                        object_id=get_text_box_theme("#text_box_30_horizleft"),
                        container=self.elements["scroll_container"],
                        manager=MANAGER
                    )
                    y_pos += 80
        
        self.elements['previous_step'] = UIImageButton(scale(pygame.Rect((506, 1250), (294, 60))), "",
                                                    object_id="#previous_step_button", manager=MANAGER)
        self.elements['next_step'] = UIImageButton(scale(pygame.Rect((800, 1250), (294, 60))), "",
                                                    object_id="#next_step_button", manager=MANAGER)
        
        self.update_disabled_buttons()
        

                
    def handle_customize_cat_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            pelts = list(Pelt.sprites_names.keys())
            pelts.remove("Tortie")
            pelts.remove("Calico")
            pelts.remove("TwoColour")
            pelts_tortie = pelts.copy()
            # pelts_tortie.remove("SingleColour")
            # pelts_tortie.remove("TwoColour")

            # cycle buttons. oh god
            if event.ui_element == self.elements["cycle_right"] or event.ui_element == self.elements["cycle_left"]:
                if event.ui_element == self.elements["cycle_right"]:
                    num = 1
                    if self.page == 0:
                        if self.preview_age == "kitten":
                            if self.kitten_sprite < 2:
                                self.kitten_sprite += 1
                            else:
                                self.kitten_sprite = 0
                        elif self.preview_age == "adolescent":
                            if self.adolescent_pose < 5:
                                self.adolescent_pose += 1
                            else:
                                self.adolescent_pose = 3
                        elif self.preview_age == "adult":
                            if self.length in ["short", "medium"]:
                                if self.adult_pose < 8:
                                    self.adult_pose += 1
                                else:
                                    self.adult_pose = 6
                            else:
                                if self.adult_pose < 11:
                                    self.adult_pose += 1
                                else:
                                    self.adult_pose = 9
                        elif self.preview_age == "elder":
                            if self.elder_pose < 14:
                                self.elder_pose += 1
                            else:
                                self.elder_pose = 12
                elif event.ui_element == self.elements["cycle_left"]:
                    num = -1
                    if self.page == 0:
                        if self.preview_age == "kitten":
                            if self.kitten_sprite > 0:
                                self.kitten_sprite -= 1
                            else:
                                self.kitten_sprite = 2
                        elif self.preview_age == "adolescent":
                            if self.adolescent_pose > 3:
                                self.adolescent_pose -= 1
                            else:
                                self.adolescent_pose = 5
                        elif self.preview_age == "adult":
                            if self.length in ["short", "medium"]:
                                if self.adult_pose > 6:
                                    self.adult_pose -= 1
                                else:
                                    self.adult_pose = 8
                            else:
                                if self.adult_pose > 9:
                                    self.adult_pose -= 1
                                else:
                                    self.adult_pose = 11
                        elif self.preview_age == "elder":
                            if self.elder_pose > 12:
                                self.elder_pose -= 1
                            else:
                                self.elder_pose = 14
                if self.page == 1:
                    if self.current_selection == "pelt_colour":
                        colours = Pelt.pelt_colours
                        current_index = colours.index(self.colour)
                        next_index = (current_index + num) % len(colours)
                        self.colour = colours[next_index]
                    elif self.current_selection == "white_patches":
                        patch_list = Pelt.little_white + Pelt.mid_white + Pelt.high_white + Pelt.mostly_white + ["FULLWHITE"]
                        if self.customiser_sort == "alphabetical":
                            patch_list.sort()

                        # grabbing search results
                        new_patch_list = []
                        searched = self.search_text
                        if searched not in ["", "search"]:
                            for patch in patch_list:
                                if searched in patch.lower():
                                    new_patch_list.append(patch)
                        else:
                            new_patch_list = patch_list

                        patches = ["None"] + new_patch_list
                        current_index = patches.index(str(self.white_patches))
                        next_index = (current_index + num) % len(patches)
                        if patches[next_index] == "None":
                            self.white_patches = None
                        else:
                            self.white_patches = patches[next_index]
                    elif self.current_selection == "points":
                        points = ["None"] + Pelt.point_markings
                        current_index = points.index(str(self.points))
                        next_index = (current_index + num) % len(points)
                        if points[next_index] == "None":
                            self.points = None
                        else:
                            self.points = points[next_index]
                    elif self.current_selection == "vitiligo":
                        vitiligo = ["None"] + Pelt.vit
                        current_index = vitiligo.index(str(self.vitiligo))
                        next_index = (current_index + num) % len(vitiligo)
                        if vitiligo[next_index] == "None":
                            self.vitiligo = None
                        else:
                            self.vitiligo = vitiligo[next_index]
                    elif self.current_selection == "pelt_pattern":
                        if self.pname in ["Tortie", "Calico"]:
                            if self.tortiebase == "single":
                                basename = "SingleColour"
                            else:
                                basename = self.tortiebase.capitalize()
                            current_index = pelts.index(basename)
                        else:
                            current_index = pelts.index(self.pname)
                        next_index = (current_index + num) % len(pelts)
                        if pelts[next_index] in ["SingleColour", "TwoColour", "Singlecolour"] and self.pname in ["Tortie", "Calico"]:
                            next_pelt = "single"
                        else:
                            next_pelt = pelts[next_index]
                        if self.pname in ["Tortie", "Calico"]:
                            self.tortiebase = next_pelt.lower()
                        else:
                            if next_pelt != "SingleColour":
                                self.pname = next_pelt.capitalize()
                            else:
                                self.pname = next_pelt
                    elif self.current_selection == "tortie_colour":
                        colours = Pelt.pelt_colours
                        current_index = colours.index(str(self.tortiecolour))
                        next_index = (current_index + num) % len(colours)
                        self.tortiecolour = colours[next_index]
                    elif self.current_selection == "tortie_patches":
                        pelts = Pelt.tortiepatterns
                        current_index = pelts.index(str(self.pattern))
                        next_index = (current_index + num) % len(pelts)
                        self.pattern = pelts[next_index]
                    elif self.current_selection == "tortie_pattern":
                        pelts = pelts_tortie
                        if self.tortiepattern == "single":
                            next_pelt = "SingleColour"
                        else:
                            next_pelt = str(self.tortiepattern).capitalize()
                        current_index = pelts.index(next_pelt)
                        next_index = (current_index + num) % len(pelts)

                        if pelts[next_index] == "SingleColour":
                            self.tortiepattern = "single"
                        else:
                            self.tortiepattern = pelts[next_index].lower()
                elif self.page == 2:
                    if self.current_selection == "eye_colour":
                        colours = Pelt.eye_colours
                        current_index = colours.index(self.eye_colour)
                        next_index = (current_index + num) % len(colours)
                        self.eye_colour = colours[next_index]
                    elif self.current_selection == "heterochromia":
                        colours = ["None"] + Pelt.eye_colours
                        current_index = colours.index(str(self.eye_colour2))
                        next_index = (current_index + num) % len(colours)
                        if colours[next_index] == "None":
                            next_eye = None
                        else:
                            next_eye = colours[next_index]
                        self.eye_colour2 = next_eye
                    elif self.current_selection == "skin":
                        colours = Pelt.skin_sprites
                        current_index = colours.index(self.skin)
                        next_index = (current_index + num) % len(colours)
                        self.skin = colours[next_index]
                    elif self.current_selection == "scar":
                        scars = ["None"] + Pelt.scars1 + Pelt.scars2 + Pelt.scars3
                        current_index = scars.index(self.scars[-1]) if self.scars else 0
                        next_index = (current_index + num) % len(scars)
                        if not self.scar_buttons[scars[next_index]].is_enabled:
                            next_index += num
                        try:
                            # im such a hack
                            test = scars[next_index]
                        except IndexError:
                            next_index = 0
                        if scars[next_index] == "None":
                            next_scar = []
                        else:
                            next_scar = [scars[next_index]]
                        self.scars = next_scar
                    elif self.current_selection == "accessory":
                        acc_list = (Pelt.plant_accessories + Pelt.wild_accessories +
                            Pelt.collars + Pelt.flower_accessories +
                            Pelt.plant2_accessories + Pelt.snake_accessories +
                            Pelt.smallAnimal_accessories + Pelt.deadInsect_accessories +
                            Pelt.aliveInsect_accessories + Pelt.fruit_accessories +
                            Pelt.crafted_accessories + Pelt.tail2_accessories)
                        if self.customiser_sort == "alphabetical":
                            acc_list.sort()

                        new_acc_list = []
                        searched = self.search_text
                        if searched not in ["", "search"]:
                            for acc in acc_list:
                                if searched in acc.lower():
                                    new_acc_list.append(acc)
                        else:
                            new_acc_list = acc_list

                        for i in self.accessory_buttons.items():
                            if not self.accessory_buttons[i[0]].is_enabled and i[0] not in self.accessories:
                                if i[0] in new_acc_list or i[0] in self.accessories:
                                    new_acc_list.remove(i[0])
                        accs = ["None"] + new_acc_list
                        current_index = accs.index(self.accessories[0]) if self.accessories else 0
                        next_index = (current_index + num) % len(accs)
                        if accs[next_index] == "None":
                            next_acc = []
                        else:
                            next_acc = [accs[next_index]]
                        self.accessories = next_acc
                elif self.page == 3:
                    if self.current_selection == "condition":
                        permanent_conditions = ['None', 'born without a leg', 'weak leg', 'twisted leg', 'born without a tail', 'paralyzed', 'raspy lungs', 'wasting disease', 'blind', 'one bad eye', 'failing eyesight', 'partial hearing loss', 'deaf', 'constant joint pain', 'seizure prone', 'allergies', 'persistent headaches']
                        current_index = permanent_conditions.index(str(self.permanent_condition))
                        next_index = (current_index + num) % len(permanent_conditions)
                        if permanent_conditions[next_index] == "None":
                            self.permanent_condition = None
                        else:
                            self.permanent_condition = permanent_conditions[next_index]
                            if self.permanent_condition == "None":
                                self.permanent_condition = None

                        if self.permanent_condition != "paralyzed":
                            self.paralyzed = False
                        else:
                            self.paralyzed = True

                        if self.permanent_condition == "born without a leg":
                            self.scars = ["NOPAW"]
                        else:
                            if "NOPAW" in self.scars:
                                self.scars.remove("NOPAW")

                        if self.permanent_condition == "born without a tail":
                            self.scars = ["NOTAIL"]
                        else:
                            if "NOTAIL" in self.scars:
                                self.scars.remove("NOTAIL")
                        
                        if self.permanent_condition != "blind":
                            if "BOTHBLIND" in self.scars:
                                self.scars.remove("BOTHBLIND")
                        if self.permanent_condition != "one bad eye":
                            if any(scar in ["LEFTBLIND", "RIGHTBLIND", "BRIGHTHEART"] for scar in self.scars):
                                self.scars = []
                    elif self.current_selection == "trait":
                        traits = ['troublesome', 'lonesome', 'impulsive', 'bullying', 'attention-seeker', 'charming', 'daring', 'noisy', 'nervous', 'quiet', 'insecure', 'daydreamer', 'sweet', 'polite', 'know-it-all', 'bossy', 'disciplined', 'patient', 'manipulative', 'secretive', 'rebellious', 'grumpy', 'passionate', 'honest', 'leader-like', 'smug']
                        current_index = traits.index(self.personality)
                        next_index = (current_index + num) % len(traits)
                        self.personality = traits[next_index]
                    elif self.current_selection == "skill":
                        current_index = self.skills.index(self.skill)
                        next_index = (current_index + num) % len(self.skills)
                        self.skill = self.skills[next_index]

                self.update_sprite()
                self.update_disabled_buttons()
            elif event.ui_element == self.elements["randomise_selection"]:
                if self.page == 0:
                    if self.preview_age == "kitten":
                        self.kitten_sprite=random.randint(0,2)
                    elif self.preview_age == "adolescent":
                        self.adolescent_pose = random.randint(3,5)
                    elif self.preview_age == "adult":
                        if self.length in ["short", "medium"]:
                            self.adult_pose = random.randint(6,8)
                        else:
                            self.adult_pose = random.randint(9,11)
                    else:
                        self.elder_pose = random.randint(12,14)
                if self.page == 1:
                    if self.current_selection == "pelt_pattern":
                        if self.pname in ["Tortie", "Calico"]:
                            new_pattern = random.choice(pelts)
                            if new_pattern == "SingleColour":
                                new_pattern = "single"
                            self.tortiebase = new_pattern.lower()
                        else:
                            self.pname = random.choice(pelts)
                    elif self.current_selection == "pelt_colour":
                        self.colour = random.choice(Pelt.pelt_colours)
                    elif self.current_selection == "white_patches":
                        self.white_patches = random.choice(["FULLWHITE"] + Pelt.little_white + Pelt.mid_white + Pelt.high_white + Pelt.mostly_white + [None])
                    elif self.current_selection == "points":
                        self.points = random.choice(Pelt.point_markings + ["None"])
                    elif self.current_selection == "vitiligo":
                        self.points = random.choice(Pelt.vit + ["None"])
                    elif self.current_selection == "tortie_pattern":
                        new_pattern = random.choice(pelts)
                        if new_pattern == "SingleColour":
                            new_pattern = "single"
                        self.tortiepattern = new_pattern.lower()
                    elif self.current_selection == "tortie_colour":
                        self.tortiecolour = random.choice(Pelt.pelt_colours)
                    elif self.current_selection == "tortie_patches":
                        self.pattern = random.choice(Pelt.tortiepatterns)
                elif self.page == 2:
                    if self.current_selection == "eye_colour":
                        self.eye_colour = random.choice(Pelt.eye_colours)
                    elif self.current_selection == "heterochromia":
                        self.eye_colour2 = random.choice(Pelt.eye_colours)
                    elif self.current_selection == "skin":
                        self.skin = random.choice(Pelt.skin_sprites)
                    elif self.current_selection == "scar":
                        self.scars = [random.choice(Pelt.scars1 + Pelt.scars2 + Pelt.scars3)]
                    elif self.current_selection == "accessory":

                        acc_list = (
                            Pelt.plant_accessories + Pelt.wild_accessories +
                            Pelt.collars + Pelt.flower_accessories +
                            Pelt.plant2_accessories + Pelt.snake_accessories +
                            Pelt.smallAnimal_accessories + Pelt.deadInsect_accessories +
                            Pelt.aliveInsect_accessories + Pelt.fruit_accessories +
                            Pelt.crafted_accessories + Pelt.tail2_accessories
                            )
                        new_acc_list = []
                        searched = self.search_text
                        if searched not in ["", "search"]:
                            for acc in acc_list:
                                if searched in acc.lower():
                                    new_acc_list.append(acc)
                        else:
                            new_acc_list = acc_list

                        if self.permanent_condition == "born without a tail":
                            for i in self.notail_accs:
                                if i in new_acc_list:
                                    new_acc_list.remove(i)
                        
                        acc = choice(new_acc_list)

                        self.accessories = [acc]
                        self.inventory = [acc]

                elif self.page == 3:
                    if self.current_selection == "condition":
                        permanent_conditions = ['None', 'born without a leg', 'weak leg', 'twisted leg', 'born without a tail', 'paralyzed', 'raspy lungs', 'wasting disease', 'blind', 'one bad eye', 'failing eyesight', 'partial hearing loss', 'deaf', 'constant joint pain', 'seizure prone', 'allergies', 'persistent headaches']

                        self.permanent_condition = random.choice(permanent_conditions)
                        if self.permanent_condition == "born without a leg":
                            self.scars = ["NOPAW"]
                        else:
                            if "NOPAW" in self.scars:
                                self.scars.remove("NOPAW")
                        if self.permanent_condition == "born without a tail":
                            self.scars = ["NOTAIL"]
                        else:
                            if "NOTAIL" in self.scars:
                                self.scars.remove("NOTAIL")
                        if self.permanent_condition == "paralyzed":
                            self.paralyzed = True
                        else:
                            self.paralyzed = False
                    elif self.current_selection == "trait":
                        self.personality = random.choice(['troublesome', 'lonesome', 'impulsive', 'bullying', 'attention-seeker', 'charming', 'daring', 'noisy', 'nervous', 'quiet', 'insecure', 'daydreamer', 'sweet', 'polite', 'know-it-all', 'bossy', 'disciplined', 'patient', 'manipulative', 'secretive', 'rebellious', 'grumpy', 'passionate', 'honest', 'leader-like', 'smug'])
                    elif self.current_selection == "skill":
                        self.skill = random.choice(self.skills)

                self.update_sprite()
                self.update_disabled_buttons()

            if "search_button" in self.elements and event.ui_element == self.elements["search_button"]:
                self.search_text = self.elements["search_bar"].get_text()
                self.previous_search_text = self.search_text
                self.open_customize_cat()
            if "clear" in self.elements and event.ui_element == self.elements["clear"]:
                self.search_text = ""
                self.previous_search_text = self.search_text
                self.open_customize_cat()
            if "match_base" in self.elements and event.ui_element == self.elements["match_base"]:
                self.tortiepattern = self.tortiebase
                self.update_sprite()
                self.update_disabled_buttons()

            if self.page == 0:
                for i in self.preview_age_buttons.items():
                    if event.ui_element == self.preview_age_buttons[i[0]]:
                        self.preview_age = i[0]
                        self.open_customize_cat()
                for i in self.kitten_pose_buttons.items():
                    if event.ui_element == self.kitten_pose_buttons[i[0]]:
                        self.kitten_sprite = int(i[0])
                        self.open_customize_cat()
                for i in self.adolescent_pose_buttons.items():
                    if event.ui_element == self.adolescent_pose_buttons[i[0]]:
                        self.adolescent_pose = int(i[0])
                        self.open_customize_cat()
                for i in self.adult_pose_buttons.items():
                    if event.ui_element == self.adult_pose_buttons[i[0]]:
                        self.adult_pose = int(i[0])
                        self.open_customize_cat()
                for i in self.elder_pose_buttons.items():
                    if event.ui_element == self.elder_pose_buttons[i[0]]:
                        self.elder_pose = int(i[0])
                        self.open_customize_cat()
                for i in self.fur_length_buttons.items():
                    if event.ui_element == self.fur_length_buttons[i[0]]:
                        self.length = i[0]
                        # correct long/shorthaired poses
                        if self.adult_pose in range(9,12) and self.length in ["short", "medium"]:
                            self.adult_pose -= 3
                        elif self.adult_pose in range(6,9) and self.length == "long":
                            self.adult_pose += 3
                        self.open_customize_cat()
                for i in self.reverse_buttons.items():
                    if event.ui_element == self.reverse_buttons[i[0]]:
                        if i[0] == "False":
                            self.reverse = False
                        else:
                            self.reverse = True
                        self.open_customize_cat()
            elif self.page == 1:
                if event.ui_element == self.elements["tortie_checkbox"]:
                    if self.tortie_enabled is True:
                        self.tortie_enabled = False
                        self.pname = self.tortiebase.capitalize()
                        if self.pname == "Single":
                            self.pname = "SingleColour"
                        self.tortiebase = None
                        self.tortiecolour = None
                        self.tortiepattern = None
                        self.pattern = None
                    else:
                        self.tortie_enabled = True
                        self.tortiebase = self.pname.lower()
                        if self.tortiebase == "singlecolour":
                            self.tortiebase = "single"
                        self.pname = "Tortie"
                        self.tortiecolour = "GINGER"
                        self.tortiepattern = "classic"
                        self.pattern = "ONE"
                    self.open_customize_cat()
                for i in self.pelt_pattern_buttons.items():
                    if event.ui_element == self.pelt_pattern_buttons[i[0]]:
                        if self.pname == "Tortie":
                            self.tortiebase = i[0].lower()
                        else:
                            self.pname = i[0]
                        self.update_sprite()
                        self.update_disabled_buttons()
                for i in self.pelt_colour_buttons.items():
                    if event.ui_element == self.pelt_colour_buttons[i[0]]:
                        self.colour = i[0]
                        self.update_sprite()
                        self.update_disabled_buttons()
                for i in self.tint_buttons.items():
                    if event.ui_element == self.tint_buttons[i[0]]:
                        self.tint = i[0]
                        self.update_sprite()
                        self.update_disabled_buttons()
                for i in self.white_patches_tint_buttons.items():
                    if event.ui_element == self.white_patches_tint_buttons[i[0]]:
                        self.white_patches_tint = i[0]
                        self.update_sprite()
                        self.update_disabled_buttons()
                for i in self.white_patches_buttons.items():
                    if event.ui_element == self.white_patches_buttons[i[0]]:
                        if i[0] == "None":
                            self.white_patches = None
                        else:
                            self.white_patches = i[0]
                        self.update_sprite()
                        self.update_disabled_buttons()
                for i in self.points_buttons.items():
                    if event.ui_element == self.points_buttons[i[0]]:
                        if i[0] == "None":
                            self.points = None
                        else:
                            self.points = i[0]
                        self.open_customize_cat()
                for i in self.vitiligo_buttons.items():
                    if event.ui_element == self.vitiligo_buttons[i[0]]:
                        if i[0] == "None":
                            self.vitiligo = None
                        else:
                            self.vitiligo = i[0]
                        self.open_customize_cat()
                # TORTIE
                for i in self.tortie_pattern_buttons.items():
                    if event.ui_element == self.tortie_pattern_buttons[i[0]]:
                        self.tortiepattern = i[0].lower()
                        if self.tortiepattern == "singlecolour":
                            self.tortiepattern = "single"
                        self.update_sprite()
                        self.update_disabled_buttons()
                for i in self.tortie_colour_buttons.items():
                    if event.ui_element == self.tortie_colour_buttons[i[0]]:
                        self.tortiecolour = i[0].upper()
                        self.update_sprite()
                        self.update_disabled_buttons()
                for i in self.tortie_patches_buttons.items():
                    if event.ui_element == self.tortie_patches_buttons[i[0]]:
                        self.pattern = i[0].upper()
                        self.update_sprite()
                        self.update_disabled_buttons()
            elif self.page == 2:
                for i in self.eye_colour_buttons.items():
                    if event.ui_element == self.eye_colour_buttons[i[0]]:
                        self.eye_colour = i[0].upper()
                        self.update_sprite()
                        self.update_disabled_buttons()
                for i in self.heterochromia_buttons.items():
                    if event.ui_element == self.heterochromia_buttons[i[0]]:
                        self.eye_colour2 = i[0].upper() if i[0] != "None" else None
                        self.update_sprite()
                        self.update_disabled_buttons()
                for i in self.skin_buttons.items():
                    if event.ui_element == self.skin_buttons[i[0]]:
                        self.skin = i[0].upper()
                        self.update_sprite()
                        self.update_disabled_buttons()
                for i in self.scar_buttons.items():
                    if event.ui_element == self.scar_buttons[i[0]]:
                        if i[0] == "None":
                            self.scars = []
                        else:
                            self.scars = [i[0].upper()]
                            if i[0] == "NOPAW":
                                self.permanent_condition = "born without a leg"
                                self.paralyzed = False
                            else:
                                if self.permanent_condition == "born without a leg":
                                    self.permanent_condition = None
                            if i[0] == "NOTAIL":
                                self.permanent_condition = "born without a tail"
                            else:
                                if self.permanent_condition == "born without a tail":
                                    self.permanent_condition = None
                            if i[0] == "BOTHBLIND":
                                self.permanent_condition = "blind"
                                self.paralyzed = False
                            if i[0] in ["RIGHTBLIND", "LEFTBLIND", "BRIGHTHEART"]:
                                self.permanent_condition = "one bad eye"
                                self.paralyzed = False
                        self.update_sprite()
                        self.update_disabled_buttons()
                for i in self.accessory_buttons.items():
                    if event.ui_element == self.accessory_buttons[i[0]]:
                        if i[0] == "None":
                            self.accessories = []
                            self.inventory = []
                        else:
                            self.accessories = [i[0].upper()]
                            self.inventory = [i[0].upper()]
                        self.update_sprite()
                        self.update_disabled_buttons()
            elif self.page == 3:
                for i in self.condition_buttons.items():
                    if event.ui_element == self.condition_buttons[i[0]]:
                        if i[0] == "None":
                            self.permanent_condition = None
                            if "NOTAIL" in self.scars:
                                self.scars.remove("NOTAIL")
                            if "NOPAW" in self.scars:
                                self.scars.remove("NOPAW")
                            if "BRIGHTHEART" in self.scars:
                                self.scars.remove("BRIGHTHEART")
                            if "BOTHBLIND" in self.scars:
                                self.scars.remove("BOTHBLIND")
                            if "LEFTBLIND" in self.scars:
                                self.scars.remove("LEFTBLIND")
                            if "RIGHTBLIND" in self.scars:
                                self.scars.remove("RIGHTBLIND")
                            self.paralyzed = False
                        else:
                            if i[0] != "paralyzed":
                                self.paralyzed = False
                            else:
                                self.paralyzed = True

                            if i[0] == "born without a leg":
                                self.scars = ["NOPAW"]
                            else:
                                if "NOPAW" in self.scars:
                                    self.scars.remove("NOPAW")

                            if i[0] == "born without a tail":
                                self.scars = ["NOTAIL"]
                            else:
                                if "NOTAIL" in self.scars:
                                    self.scars.remove("NOTAIL")
                            
                            if i[0] != "blind":
                                if "BOTHBLIND" in self.scars:
                                    self.scars.remove("BOTHBLIND")
                            if i[0] != "one bad eye":
                                if any(scar in ["LEFTBLIND", "RIGHTBLIND", "BRIGHTHEART"] for scar in self.scars):
                                    self.scars = []

                            self.permanent_condition = i[0]
                        self.update_sprite()
                        self.update_disabled_buttons()
                for i in self.trait_buttons.items():
                    if event.ui_element == self.trait_buttons[i[0]]:
                        self.personality = i[0]
                        self.update_disabled_buttons()
                for i in self.skill_buttons.items():
                    if event.ui_element == self.skill_buttons[i[0]]:
                        self.skill = i[0]
                        self.update_disabled_buttons()
                for i in self.faith_buttons.items():
                    if event.ui_element == self.faith_buttons[i[0]]:
                        self.faith = i[0]
                        self.update_disabled_buttons()
                for i in self.sex_buttons.items():
                    if event.ui_element == self.sex_buttons[i[0]]:
                        self.sex = i[0]
                        self.update_disabled_buttons()

            for i in self.current_selection_buttons.items():
                if event.ui_element == self.current_selection_buttons[i[0]]:
                    self.current_selection = i[0]
                    self.open_customize_cat()
            for i in ["default", "alphabetical"]:
                if i in self.elements:
                    if event.ui_element == self.elements[i]:
                        self.customiser_sort = i
                        self.open_customize_cat()

            if event.ui_element == self.main_menu:
                self.change_screen('start screen')
            elif event.ui_element == self.elements['right']:
                if self.page < 5:
                    self.page += 1
                    self.open_customize_cat()
            elif event.ui_element == self.elements['left']:
                if self.page > 0:
                    self.page -= 1
                    self.open_customize_cat()
            elif event.ui_element == self.elements['random_customize']:
                self.randomize_custom_cat()
                self.open_customize_cat()
            elif event.ui_element == self.elements['next_step']:
                new_cat = Cat(moons = 1)
                new_cat.pelt = self.custom_cat.pelt
                new_cat.gender = self.sex
                new_cat.genderalign = self.sex

                if new_cat.genderalign == "male":
                    new_cat.pronouns = [Cat.default_pronouns[2].copy()]
                elif new_cat.genderalign == "female":
                    new_cat.pronouns = [Cat.default_pronouns[1].copy()]
                else:
                    new_cat.pronouns = [Cat.default_pronouns[0].copy()]
                    
                self.your_cat = new_cat
                if self.permanent_condition is not None and self.permanent_condition != 'paralyzed':
                    self.your_cat.get_permanent_condition(self.permanent_condition, born_with=True)
                    self.your_cat.permanent_condition[self.permanent_condition]["moons_until"] = 1
                    self.your_cat.permanent_condition[self.permanent_condition]["moons_with"] = -1
                    self.your_cat.permanent_condition[self.permanent_condition]['born_with'] = True
                if self.paralyzed and 'paralyzed' not in self.your_cat.permanent_condition:
                    self.your_cat.get_permanent_condition('paralyzed')
                    self.your_cat.permanent_condition['paralyzed']["moons_until"] = 1
                    self.your_cat.permanent_condition['paralyzed']["moons_with"] = -1
                    self.your_cat.permanent_condition['paralyzed']['born_with'] = True
                if self.permanent_condition is not None and self.permanent_condition == "born without a tail" and "NOTAIL" not in self.your_cat.pelt.scars:
                    self.your_cat.pelt.scars.append('NOTAIL')
                    self.your_cat.permanent_condition['born without a tail']["moons_until"] = 1
                    self.your_cat.permanent_condition['born without a tail']["moons_with"] = -1
                    self.your_cat.permanent_condition['born without a tail']['born_with'] = True
                elif self.permanent_condition is not None and self.permanent_condition == "born without a leg" and "NOPAW" not in self.your_cat.pelt.scars:
                    self.your_cat.pelt.scars.append('NOPAW')
                    self.your_cat.permanent_condition['born without a leg']["moons_until"] = 1
                    self.your_cat.permanent_condition['born without a leg']["moons_with"] = -1
                    self.your_cat.permanent_condition['born without a leg']['born_with'] = True
                self.your_cat.pelt.accessories = self.accessories
                self.your_cat.pelt.inventory = self.accessories
                self.your_cat.personality = Personality(trait=self.personality, kit_trait=True)
                if self.skill == "Random":
                    self.skill = random.choice(self.skills)
                self.your_cat.skills.primary = Skill.get_skill_from_string(Skill, self.skill)
                self.your_cat.lock_faith = self.faith
                self.selected_cat = None
                self.open_name_cat()
            elif event.ui_element == self.elements['previous_step']:
                self.open_choose_leader()

    def update_disabled_buttons(self):
        if self.page == 0:
            for i in range(0,3):
                if self.kitten_sprite != i:
                    self.kitten_pose_buttons[str(i)].enable()
                else:
                    self.kitten_pose_buttons[str(i)].disable()
            for i in range(3,6):
                if self.adolescent_pose != i:
                    self.adolescent_pose_buttons[str(i)].enable()
                else:
                    self.adolescent_pose_buttons[str(i)].disable()

            if self.length in ["short", "medium"]:
                pose_range = range(6,9)
            else:
                pose_range = range(9,12)

            for i in pose_range:
                if self.adult_pose != i:
                    self.adult_pose_buttons[str(i)].enable()
                else:
                    self.adult_pose_buttons[str(i)].disable()

            for i in range(12,15):
                if self.elder_pose != i:
                    self.elder_pose_buttons[str(i)].enable()
                else:
                    self.elder_pose_buttons[str(i)].disable()

            for i in ["kitten", "adolescent", "adult", "elder"]:
                if self.preview_age != i:
                    self.preview_age_buttons[i].enable()
                else:
                    self.preview_age_buttons[i].disable()

            for i in ["short", "medium", "long"]:
                if self.length != i:
                    self.fur_length_buttons[i].enable()
                else:
                    self.fur_length_buttons[i].disable()

            for i in [True, False]:
                if self.reverse != i:
                    self.reverse_buttons[str(i)].enable()
                else:
                    self.reverse_buttons[str(i)].disable()

        if self.page == 1:
            pelts = list(Pelt.sprites_names.keys())
            pelts.remove("Tortie")
            pelts.remove("Calico")
            pelts.remove("TwoColour")
            pelts_tortie = pelts.copy()
            # pelts_tortie.remove("SingleColour")
            # pelts_tortie.remove("TwoColour")
            
            for i in self.pelt_pattern_buttons.items():
                if self.pname in ["Tortie", "Calico"]:
                    pattern = self.tortiebase.capitalize()
                    if pattern == "Single":
                        pattern = "SingleColour"
                else:
                    pattern = self.pname
                if i[0] != pattern:
                    self.pelt_pattern_buttons[i[0]].enable()
                else:
                    self.pelt_pattern_buttons[i[0]].disable()
            
            for i in self.pelt_colour_buttons.items():
                if i[0] != self.colour:
                    self.pelt_colour_buttons[i[0]].enable()
                else:
                    self.pelt_colour_buttons[i[0]].disable()
            
            for i in self.tint_buttons.items():
                if i[0] != self.tint:
                    self.tint_buttons[i[0]].enable()
                else:
                    self.tint_buttons[i[0]].disable()
            
            for i in self.white_patches_tint_buttons.items():
                if i[0] != self.white_patches_tint:
                    self.white_patches_tint_buttons[i[0]].enable()
                else:
                    self.white_patches_tint_buttons[i[0]].disable()
            
            for i in self.white_patches_buttons.items():
                if i[0] != str(self.white_patches): # convert to string for the one None
                    self.white_patches_buttons[i[0]].enable()
                else:
                    self.white_patches_buttons[i[0]].disable()
            
            for i in self.points_buttons.items():
                if i[0] != str(self.points):
                    self.points_buttons[i[0]].enable()
                else:
                    self.points_buttons[i[0]].disable()
            
            for i in self.vitiligo_buttons.items():
                if i[0] != str(self.vitiligo):
                    self.vitiligo_buttons[i[0]].enable()
                else:
                    self.vitiligo_buttons[i[0]].disable()
            
            for i in self.tortie_pattern_buttons.items():
                pattern = i[0].lower()
                if pattern == "singlecolour":
                    pattern = "single"
                if pattern != self.tortiepattern: # not changing to string bc this isnt accessible when its None
                    self.tortie_pattern_buttons[i[0]].enable()
                else:
                    self.tortie_pattern_buttons[i[0]].disable()
            
            for i in self.tortie_colour_buttons.items():
                if i[0] != self.tortiecolour:
                    self.tortie_colour_buttons[i[0]].enable()
                else:
                    self.tortie_colour_buttons[i[0]].disable()
            
            for i in self.tortie_patches_buttons.items():
                if i[0] != self.pattern:
                    self.tortie_patches_buttons[i[0]].enable()
                else:
                    self.tortie_patches_buttons[i[0]].disable()

        elif self.page == 2:
            for i in self.eye_colour_buttons.items():
                if i[0] != self.eye_colour:
                    self.eye_colour_buttons[i[0]].enable()
                else:
                    self.eye_colour_buttons[i[0]].disable()
            for i in self.heterochromia_buttons.items():
                if i[0] != str(self.eye_colour2):
                    self.heterochromia_buttons[i[0]].enable()
                else:
                    self.heterochromia_buttons[i[0]].disable()
            for i in self.skin_buttons.items():
                if i[0] != str(self.skin):
                    self.skin_buttons[i[0]].enable()
                else:
                    self.skin_buttons[i[0]].disable()
            for i in self.scar_buttons.items():
                if i[0] == "None" and self.scars == []:
                    self.scar_buttons[i[0]].disable()
                else:
                    if i[0] not in self.scars:
                        self.scar_buttons[i[0]].enable()
                    else:
                        self.scar_buttons[i[0]].disable()
                if self.paralyzed is True:
                    for scar in ["BRIGHTHEART", "LEFTBLIND", "RIGHTBLIND", "BOTHBLIND", "NOPAW", "NOTAIL"]:
                        self.scar_buttons[scar].disable()
            for i in self.accessory_buttons.items():
                if i[0] == "None" and not self.accessories:
                    self.accessory_buttons[i[0]].disable()
                else:
                    if i[0] not in self.accessories:
                        self.accessory_buttons[i[0]].enable()
                    else:
                        self.accessory_buttons[i[0]].disable()
                if self.permanent_condition == "born without a tail":
                    for acc in self.notail_accs:
                        self.accessory_buttons[acc].disable()
                if self.permanent_condition == "born without a leg":
                    for acc in ["ASHY PAWS", "MUD PAWS"]:
                        self.accessory_buttons[acc].disable()

            if self.current_selection == "accessory":
                if "acc_name" in self.elements:
                    self.elements["acc_name"].kill()
                    del self.elements["acc_name"]

                if self.accessories:
                    self.elements["acc_name"] = pygame_gui.elements.UITextBox(
                        str(self.ACC_DISPLAY[self.accessories[0]]["default"]).capitalize(),
                        scale(pygame.Rect((538, 830),(525, 150))),
                        object_id=get_text_box_theme("#text_box_30_horizcenter"),
                        manager=MANAGER
                    )
        elif self.page == 3:
            if self.current_selection == "condition":
                if "condition_name" in self.elements:
                    self.elements["condition_name"].kill()
                    del self.elements["condition_name"]

                if self.permanent_condition:
                    self.elements["condition_name"] = pygame_gui.elements.UITextBox(
                        self.permanent_condition.capitalize(),
                        scale(pygame.Rect((600, 860),(400, 68))),
                        object_id=get_text_box_theme("#text_box_30_horizcenter"),
                        manager=MANAGER
                    )

            for i in self.condition_buttons.items():
                if i[0] == "None" and self.permanent_condition is None:
                    self.condition_buttons[i[0]].disable()
                else:
                    if i[0] != self.permanent_condition:
                        self.condition_buttons[i[0]].enable()
                    else:
                        self.condition_buttons[i[0]].disable()

            for i in self.trait_buttons.items():
                if i[0] != self.personality:
                    self.trait_buttons[i[0]].enable()
                else:
                    self.trait_buttons[i[0]].disable()

            if self.current_selection == "trait":
                if "trait_name" in self.elements:
                    self.elements["trait_name"].kill()
                    del self.elements["trait_name"]

                if self.skill:
                    self.elements["trait_name"] = pygame_gui.elements.UITextBox(
                        self.personality.capitalize(),
                        scale(pygame.Rect((552, 830),(495, 98))),
                        object_id=get_text_box_theme("#text_box_30_horizcenter"),
                        manager=MANAGER
                    )

            if self.current_selection == "skill":
                if "skill_name" in self.elements:
                    self.elements["skill_name"].kill()
                    del self.elements["skill_name"]

                if self.skill:
                    skillname = self.skill[0].upper() + self.skill[1:]
                    self.elements["skill_name"] = pygame_gui.elements.UITextBox(
                        skillname,
                        scale(pygame.Rect((552, 830),(495, 98))),
                        object_id=get_text_box_theme("#text_box_30_horizcenter"),
                        manager=MANAGER
                    )

            for i in self.skill_buttons.items():
                if i[0] != self.skill:
                    self.skill_buttons[i[0]].enable()
                else:
                    self.skill_buttons[i[0]].disable()

            for i in self.faith_buttons.items():
                if i[0] != self.faith:
                    self.faith_buttons[i[0]].enable()
                else:
                    self.faith_buttons[i[0]].disable()

            for i in self.sex_buttons.items():
                if i[0] != self.sex:
                    self.sex_buttons[i[0]].enable()
                else:
                    self.sex_buttons[i[0]].disable()
            
        for i in self.current_selection_buttons.items():
            if self.current_selection != i[0]:
                if i[0] in ["tortie_pattern", "tortie_colour", "tortie_patches"]:
                    if self.tortie_enabled is True:
                        self.current_selection_buttons[i[0]].enable()
                else:
                    self.current_selection_buttons[i[0]].enable()
            else:
                self.current_selection_buttons[i[0]].disable()
        # filter buttons
        for i in ["default", "alphabetical"]:
            if i in self.elements:
                if i == self.customiser_sort:
                    self.elements[i].disable()
                else:
                    self.elements[i].enable()

    def update_sprite(self):
        # this sucks
        if self.pname in ["Tortie", "Calico"]:
            if self.tortiepattern in ["Singlecolour", "SingleColour", "Twocolour", "TwoColour", "singlecolour", "twocolour"]:
                print("Correcting tortiepattern:", self.tortiepattern, "| Report as LifeGen bug!")
                self.tortiepattern = "single"
            if self.tortiebase in ["Singlecolour", "SingleColour", "Twocolour", "TwoColour", "singlecolour", "twocolour"]:
                print("Correcting tortiebase:", self.tortiebase, "| Report as LifeGen bug!")
                self.tortiebase = "single"
        else:
            if self.pname in ["single", "singlecolour", "Singlecolour"]:
                print("Correcting pname:", self.pname, "| Report as LifeGen bug!")
                self.pname = "SingleColour"

        pelt2 = Pelt(
            name=self.pname,
            length=self.length,
            colour=self.colour,
            white_patches=self.white_patches,
            eye_color=self.eye_colour,
            eye_colour2=self.eye_colour2,
            tortiebase=self.tortiebase,
            tortiecolour=self.tortiecolour,
            pattern=self.pattern,
            tortiepattern=self.tortiepattern.lower() if self.tortiepattern else None,
            vitiligo=self.vitiligo,
            points=self.points,
            accessory=None,
            paralyzed=self.paralyzed,
            scars=self.scars,
            tint=self.tint,
            skin=self.skin,
            white_patches_tint=self.white_patches_tint,
            kitten_sprite=self.kitten_sprite,
            adol_sprite=self.adolescent_pose if self.adolescent_pose > 2 else self.adolescent_pose + 3,
            adult_sprite=self.adult_pose if self.adult_pose > 2 else self.adult_pose + 6,
            senior_sprite=self.elder_pose if self.elder_pose > 2 else self.elder_pose + 12,
            reverse=self.reverse,
            accessories=self.accessories,
            inventory=self.accessories
        )


        if self.length == 'long' and self.adult_pose < 9:
            pelt2.cat_sprites['young adult'] = self.adult_pose + 9
            pelt2.cat_sprites['adult'] = self.adult_pose + 9
            pelt2.cat_sprites['senior adult'] = self.adult_pose + 9
        c_moons = 1
        if self.preview_age == "adolescent":
            c_moons = 6
        elif self.preview_age == "adult":
            c_moons = 12
        elif self.preview_age == "elder":
            c_moons = 121
        self.custom_cat = Cat(moons = c_moons, pelt=pelt2, loading_cat=True)

        self.custom_cat.sprite = generate_sprite(self.custom_cat)
        self.elements['sprite'].kill()
        self.elements["sprite"] = UISpriteButton(scale(pygame.Rect
                                         ((630,280), (350, 350))),
                                   self.custom_cat.sprite,
                                   self.custom_cat.ID,
                                   starting_height=0, manager=MANAGER)
    
    def open_choose_background(self):
        # clear screen
        self.clear_all_page()
        self.sub_screen = "choose camp"

        # Next and previous buttons
        self.elements["previous_step"] = UIImageButton(
            scale(pygame.Rect((506, 1290), (294, 60))),
            "",
            object_id="#previous_step_button",
            manager=MANAGER,
        )
        self.elements["next_step"] = UIImageButton(
            scale(pygame.Rect((800, 1290), (294, 60))),
            "",
            object_id="#next_step_button",
            manager=MANAGER,
        )
        self.elements["next_step"].disable()

        # Biome buttons
        self.elements["forest_biome"] = UIImageButton(
            scale(pygame.Rect((392, 200), (200, 92))),
            "",
            object_id="#forest_biome_button",
            manager=MANAGER,
        )
        self.elements["mountain_biome"] = UIImageButton(
            scale(pygame.Rect((608, 200), (212, 92))),
            "",
            object_id="#mountain_biome_button",
            manager=MANAGER,
        )
        self.elements["plains_biome"] = UIImageButton(
            scale(pygame.Rect((848, 200), (176, 92))),
            "",
            object_id="#plains_biome_button",
            manager=MANAGER,
        )
        self.elements["beach_biome"] = UIImageButton(
            scale(pygame.Rect((1040, 200), (164, 92))),
            "",
            object_id="#beach_biome_button",
            manager=MANAGER,
        )

        # Camp Art Choosing Tabs, Dummy buttons, will be overridden.
        self.tabs["tab1"] = UIImageButton(scale(pygame.Rect((0, 0), (0, 0))), "",
                                          visible=False, manager=MANAGER)
        self.tabs["tab2"] = UIImageButton(scale(pygame.Rect((0, 0), (0, 0))), "",
                                          visible=False, manager=MANAGER)
        self.tabs["tab3"] = UIImageButton(scale(pygame.Rect((0, 0), (0, 0))), "",
                                          visible=False, manager=MANAGER)
        self.tabs["tab4"] = UIImageButton(scale(pygame.Rect((0, 0), (0, 0))), "",
                                          visible=False, manager=MANAGER)
        self.tabs["tab5"] = UIImageButton(scale(pygame.Rect((0, 0), (0, 0))), "",
                                          visible=False, manager=MANAGER)
        self.tabs["tab6"] = UIImageButton(scale(pygame.Rect((0, 0), (0, 0))), "",
                                          visible=False, manager=MANAGER)
        y_pos = 550
        self.tabs["newleaf_tab"] = UIImageButton(scale(pygame.Rect((1255, y_pos), (78, 68))), "",
                                                 object_id="#newleaf_toggle_button",
                                                 manager=MANAGER,
                                                 tool_tip_text='Switch starting season to Newleaf.'
                                                 )
        y_pos += 100
        self.tabs["greenleaf_tab"] = UIImageButton(scale(pygame.Rect((1255, y_pos), (78, 68))), "",
                                                   object_id="#greenleaf_toggle_button",
                                                   manager=MANAGER,
                                                   tool_tip_text='Switch starting season to Greenleaf.'
                                                   )
        y_pos += 100
        self.tabs["leaffall_tab"] = UIImageButton(scale(pygame.Rect((1255, y_pos), (78, 68))), "",
                                                  object_id="#leaffall_toggle_button",
                                                  manager=MANAGER,
                                                  tool_tip_text='Switch starting season to Leaf-fall.'
                                                  )
        y_pos += 100
        self.tabs["leafbare_tab"] = UIImageButton(scale(pygame.Rect((1255, y_pos), (78, 68))), "",
                                                  object_id="#leafbare_toggle_button",
                                                  manager=MANAGER,
                                                  tool_tip_text='Switch starting season to Leaf-bare.'
                                                  )
        # Random background
        self.elements["random_background"] = UIImageButton(
            scale(pygame.Rect((510, 1190), (580, 60))),
            "",
            object_id="#random_background_button",
            manager=MANAGER,
        )

        # art frame
        self.elements["art_frame"] = pygame_gui.elements.UIImage(
            scale(pygame.Rect(((334, 324), (932, 832)))),
            pygame.transform.scale(
                pygame.image.load(
                    "resources/images/bg_preview_border.png"
                ).convert_alpha(),
                (932, 832),
            ),
            manager=MANAGER,
        )

        # camp art self.elements["camp_art"] = pygame_gui.elements.UIImage(scale(pygame.Rect((175,170),(450, 400))),
        # pygame.image.load(self.get_camp_art_path(1)).convert_alpha(), visible=False)

    def open_choose_symbol(self):
        # clear screen
        self.clear_all_page()

        # set basics
        self.sub_screen = "choose symbol"

        self.elements["previous_step"] = UIImageButton(
            scale(pygame.Rect((506, 1290), (294, 60))),
            "",
            object_id="#previous_step_button",
            manager=MANAGER,
        )
        self.elements["done_button"] = UIImageButton(
            scale(pygame.Rect((800, 1290), (294, 60))),
            "",
            object_id="#done_arrow_button",
            manager=MANAGER,
        )
        self.elements["done_button"].disable()

        # create screen specific elements
        self.elements["text_container"] = pygame_gui.elements.UIAutoResizingContainer(
            scale(pygame.Rect((170, 230), (0, 0))),
            object_id="text_container",
            starting_height=1,
            manager=MANAGER,
        )
        self.text["clan_name"] = pygame_gui.elements.UILabel(
            scale(pygame.Rect((0, 0), (-1, -1))),
            text=f"{self.clan_name}Clan",
            container=self.elements["text_container"],
            object_id=get_text_box_theme("#text_box_40"),
            manager=MANAGER,
        )
        self.text["biome"] = pygame_gui.elements.UILabel(
            scale(pygame.Rect((0, 50), (-1, -1))),
            text=f"{self.biome_selected}",
            container=self.elements["text_container"],
            object_id=get_text_box_theme("#text_box_30_horizleft"),
            manager=MANAGER,
        )
        self.text["leader"] = pygame_gui.elements.UILabel(
            scale(pygame.Rect((0, 90), (-1, -1))),
            text=f"Your name: {self.your_cat.name}",
            container=self.elements["text_container"],
            object_id=get_text_box_theme("#text_box_30_horizleft"),
            manager=MANAGER,
        )
        self.text["recommend"] = pygame_gui.elements.UILabel(
            scale(pygame.Rect((0, 160), (-1, -1))),
            text=f"Recommended Symbol: N/A",
            container=self.elements["text_container"],
            object_id=get_text_box_theme("#text_box_30_horizleft"),
            manager=MANAGER,
        )
        self.text["selected"] = pygame_gui.elements.UILabel(
            scale(pygame.Rect((0, 200), (-1, -1))),
            text=f"Selected Symbol: N/A",
            container=self.elements["text_container"],
            object_id=get_text_box_theme("#text_box_30_horizleft"),
            manager=MANAGER,
        )

        self.elements["random_symbol_button"] = UIImageButton(
            scale(pygame.Rect((993, 412), (68, 68))),
            "",
            object_id="#random_dice_button",
            starting_height=1,
            tool_tip_text="Select a random symbol!",
            manager=MANAGER,
        )

        self.elements["symbol_frame"] = pygame_gui.elements.UIImage(
            scale(pygame.Rect((1081, 181), (338, 332))),
            pygame.image.load(
                f"resources/images/symbol_choice_frame.png"
            ).convert_alpha(),
            object_id="#symbol_choice_frame",
            starting_height=1,
            manager=MANAGER,
        )

        self.elements["page_left"] = UIImageButton(
            scale(pygame.Rect((95, 829), (68, 68))),
            "",
            object_id="#arrow_left_button",
            starting_height=1,
            manager=MANAGER,
        )
        self.elements["page_right"] = UIImageButton(
            scale(pygame.Rect((1438, 829), (68, 68))),
            "",
            object_id="#arrow_right_button",
            starting_height=1,
            manager=MANAGER,
        )
        self.elements["filters_tab"] = UIImageButton(
            scale(pygame.Rect((200, 1239), (156, 60))),
            "",
            object_id="#filters_tab_button",
            starting_height=1,
            manager=MANAGER,
        )
        self.elements["symbol_list_frame"] = pygame_gui.elements.UIImage(
            scale(pygame.Rect((152, 500), (1300, 740))),
            pygame.image.load(
                f"resources/images/symbol_list_frame.png"
            ).convert_alpha(),
            object_id="#symbol_list_frame",
            starting_height=2,
            manager=MANAGER,
        )

        if f"symbol{self.clan_name.upper()}0" in sprites.clan_symbols:
            self.text["recommend"].set_text(
                f"Recommended Symbol: {self.clan_name.upper()}0"
            )

        if not self.symbol_selected:
            if f"symbol{self.clan_name.upper()}0" in sprites.clan_symbols:
                self.symbol_selected = f"symbol{self.clan_name.upper()}0"

                self.text["selected"].set_text(
                    f"Selected Symbol: {self.clan_name.upper()}0"
                )

        if self.symbol_selected:
            symbol_name = self.symbol_selected.replace("symbol", "")
            self.text["selected"].set_text(f"Selected Symbol: {symbol_name}")

            self.elements["selected_symbol"] = pygame_gui.elements.UIImage(
                scale(pygame.Rect((1147, 254), (200, 200))),
                pygame.transform.scale(
                    sprites.sprites[self.symbol_selected], (200, 200)
                ).convert_alpha(),
                object_id="#selected_symbol",
                starting_height=2,
                manager=MANAGER,
            )
            self.refresh_symbol_list()
            while self.symbol_selected not in self.symbol_buttons:
                self.current_page += 1
                self.refresh_symbol_list()
            self.elements["done_button"].enable()
        else:
            self.elements["selected_symbol"] = pygame_gui.elements.UIImage(
                scale(pygame.Rect((1147, 254), (200, 200))),
                pygame.transform.scale(
                    sprites.sprites["symbolADDER0"], (200, 200)
                ).convert_alpha(),
                object_id="#selected_symbol",
                starting_height=2,
                manager=MANAGER,
                visible=False,
            )
            self.refresh_symbol_list()
    
    def refresh_symbol_list(self):
        # get symbol list
        symbol_list = sprites.clan_symbols.copy()
        symbol_attributes = sprites.symbol_dict

        # filtering out tagged symbols
        for symbol in sprites.clan_symbols:
            index = symbol[-1]
            name = symbol.strip("symbol1234567890")
            tags = symbol_attributes[name.capitalize()][f"tags{index}"]
            for tag in tags:
                if tag in game.switches["disallowed_symbol_tags"]:
                    if symbol in symbol_list:
                        symbol_list.remove(symbol)

        # separate list into chunks for pages
        symbol_chunks = self.chunks(symbol_list, 45)

        # clamp current page to a valid page number
        self.current_page = max(1, min(self.current_page, len(symbol_chunks)))

        # handles which arrow buttons are clickable
        if len(symbol_chunks) <= 1:
            self.elements["page_left"].disable()
            self.elements["page_right"].disable()
        elif self.current_page >= len(symbol_chunks):
            self.elements["page_left"].enable()
            self.elements["page_right"].disable()
        elif self.current_page == 1 and len(symbol_chunks) > 1:
            self.elements["page_left"].disable()
            self.elements["page_right"].enable()
        else:
            self.elements["page_left"].enable()
            self.elements["page_right"].enable()

        display_symbols = []
        if symbol_chunks:
            display_symbols = symbol_chunks[self.current_page - 1]

        # Kill all currently displayed symbols
        symbol_images = [ele for ele in self.elements if ele in sprites.clan_symbols]
        for ele in symbol_images:
            self.elements[ele].kill()
            if self.symbol_buttons:
                self.symbol_buttons[ele].kill()

        x_pos = 192
        y_pos = 540
        for symbol in display_symbols:
            self.elements[f"{symbol}"] = pygame_gui.elements.UIImage(
                scale(pygame.Rect((x_pos, y_pos), (100, 100))),
                sprites.sprites[symbol],
                object_id=f"#{symbol}",
                starting_height=3,
                manager=MANAGER,
            )
            self.symbol_buttons[f"{symbol}"] = UIImageButton(
                scale(pygame.Rect((x_pos - 24, y_pos - 24), (148, 148))),
                "",
                object_id=f"#symbol_select_button",
                starting_height=4,
                manager=MANAGER,
            )
            x_pos += 140
            if x_pos >= 1431:
                x_pos = 192
                y_pos += 140

        if self.symbol_selected in self.symbol_buttons:
            self.symbol_buttons[self.symbol_selected].disable()


    def open_clan_saved_screen(self):
        self.clear_all_page()

        self.sub_screen = 'saved screen'

        if game.switches["customise_new_life"] is False:
            # no new clan symbol when youre just making a new mc
            self.elements["selected_symbol"] = pygame_gui.elements.UIImage(
                scale(pygame.Rect((700, 210), (200, 200))),
                pygame.transform.scale(
                    sprites.sprites[self.symbol_selected], (200, 200)
                ).convert_alpha(),
                object_id="#selected_symbol",
                starting_height=1,
                manager=MANAGER,
            )

        self.elements["leader_image"] = pygame_gui.elements.UIImage(scale(pygame.Rect((700, 240), (200, 200))),
                                                                    pygame.transform.scale(
                                                                        self.your_cat.sprite,
                                                                        (200, 200)), manager=MANAGER)
        self.elements["continue"] = UIImageButton(scale(pygame.Rect((692, 600), (204, 60))), "",
                                                  object_id="#continue_button_small")
        self.elements["save_confirm"] = pygame_gui.elements.UITextBox('Welcome to the world, ' + self.your_cat.name.prefix + 'kit!',
                                                                    scale(pygame.Rect((200, 470), (1200, 60))),
                                                                    object_id=get_text_box_theme(
                                                                        "#text_box_30_horizcenter"),
                                                                    manager=MANAGER)
    def delete_example_cats(self):
        """ Deletes the other generated kits so they don't also get added to the Clan """
        key_copy = tuple(Cat.all_cats.keys())
        for i in key_copy:  # Going through all currently existing cats
            # cat_class is a Cat-object
            if i not in [game.clan.your_cat.ID] + self.current_members:
                Cat.all_cats[i].example = True
                self.remove_cat(Cat.all_cats[i].ID)

    def remove_cat(self, ID):  # ID is cat.ID
        """
        This function is for completely removing the cat from the game,
        it's not meant for a cat that's simply dead
        """

        if Cat.all_cats[ID] in Cat.all_cats_list:
            Cat.all_cats_list.remove(Cat.all_cats[ID])

        if ID in Cat.all_cats:
            Cat.all_cats.pop(ID)

        if ID in game.clan.clan_cats:
            game.clan.clan_cats.remove(ID)
        if ID in game.clan.starclan_cats:
            game.clan.starclan_cats.remove(ID)
        if ID in game.clan.unknown_cats:
            game.clan.unknown_cats.remove(ID)
        if ID in game.clan.darkforest_cats:
            game.clan.darkforest_cats.remove(ID)

    def save_clan(self):
        if game.switches["customise_new_life"] is True:
            self.your_cat.create_inheritance_new_cat()
            game.clan.your_cat = self.your_cat
            game.clan.your_cat.moons = -1
            self.delete_example_cats()
        else:
            self.handle_create_other_cats()
            game.mediated.clear()
            game.patrolled.clear()
            game.cat_to_fade.clear()
            Cat.outside_cats.clear()
            Patrol.used_patrols.clear()
            convert_camp = {1: 'camp1', 2: 'camp2', 3: 'camp3', 4: 'camp4', 5: 'camp5', 6: 'camp6'}
            self.your_cat.create_inheritance_new_cat()
            game.clan = Clan(name = self.clan_name,
                            leader = self.leader,
                            deputy = self.deputy,
                            medicine_cat = self.med_cat,
                            biome = self.biome_selected,
                            camp_bg = convert_camp[self.selected_camp_tab],
                            symbol=self.symbol_selected,
                            game_mode="expanded",
                            starting_members=self.members,
                            starting_season=self.selected_season,
                            your_cat=self.your_cat,
                            clan_age=self.clan_age)
            game.clan.your_cat.moons = -1
            game.clan.create_clan()
            if self.clan_age == "established":
                game.clan.leader_lives = random.randint(1,9)
            game.cur_events_list.clear()
            game.herb_events_list.clear()
            Cat.grief_strings.clear()
            Cat.sort_cats()

    def get_camp_art_path(self, campnum):
        leaf = self.selected_season.replace("-", "")

        camp_bg_base_dir = "resources/images/camp_bg/"
        start_leave = leaf.casefold()
        light_dark = "light"
        if game.settings["dark mode"]:
            light_dark = "dark"

        biome = self.biome_selected.lower()

        if campnum:
            return f"{camp_bg_base_dir}/{biome}/{start_leave}_camp{campnum}_{light_dark}.png"
        else:
            return None

    def chunks(self, L, n):
        return [L[x : x + n] for x in range(0, len(L), n)]


make_clan_screen = MakeClanScreen()
