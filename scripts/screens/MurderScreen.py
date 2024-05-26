import pygame.transform
import pygame_gui.elements
from random import choice, randint
import ujson

from scripts.cat_relations.inheritance import Inheritance
from scripts.cat.history import History
from scripts.event_class import Single_Event
from scripts.events import events_class

from .Screens import Screens
from scripts.utility import get_personality_compatibility, get_text_box_theme, scale, scale_dimentions, shorten_text_to_fit
from scripts.cat.cats import Cat
from scripts.game_structure import image_cache
from scripts.cat.pelts import Pelt
from scripts.game_structure.windows import GameOver, PickPath, DeathScreen
from scripts.game_structure.image_button import UIImageButton, UISpriteButton, UIRelationStatusBar
from scripts.game_structure.game_essentials import game, screen, screen_x, screen_y, MANAGER
from scripts.game_structure.windows import RelationshipLog
from scripts.game_structure.propagating_thread import PropagatingThread
from scripts.cat.skills import SkillPath

class MurderScreen(Screens):
    selected_cat = None
    accomplice_cat = None
    current_page = 1
    list_frame = None
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
        self.accomplice_frame = None
        self.methodtext = None
        self.locationtext = None
        self.timetext = None
        self.attackmethod = None
        self.poisonmethod = None
        self.accidentmethod = None
        self.predatormethod = None
        self.camplocation = None
        self.territorylocation = None
        self.borderlocation = None
        self.dawntime = None
        self.daytime = None
        self.nighttime = None
        self.current_mentor_text = None
        self.info = None
        self.heading = None
        self.mentor = None
        self.the_cat = None
        self.murder_cat = None
        self.next = None
        self.method = "attack"
        self.location = "camp"
        self.time = "day"
        self.methodinfo = None
        self.methodheading = None
        self.locationinfo = None
        self.locationheading = None
        self.timeinfo = None
        self.timeheading = None
        self.your_sprite = None
        self.victim_sprite = None
        self.victim_info = None
        self.victim_name = None
        
    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element in self.cat_list_buttons.values():
                self.selected_cat = event.ui_element.return_cat_object()
                if self.stage == "choose murder cat":
                    self.update_selected_cat()
                elif self.stage == "choose accomplice":
                    self.update_selected_cat2()

            elif event.ui_element == self.confirm_mentor and self.selected_cat and self.stage == 'choose murder cat':
                if not self.selected_cat.dead:
                    self.exit_screen()
                    self.cat_to_murder = self.selected_cat
                    self.stage = 'choose murder method'
                    self.screen_switches()
            
            elif event.ui_element == self.confirm_mentor and self.method and self.location and self.time and self.stage == 'choose murder method':
                if not self.selected_cat.dead:
                    self.exit_screen()
                    self.stage = 'choose accomplice'
                    self.screen_switches()
                    self.selected_cat = None
            
            elif event.ui_element == self.confirm_mentor and self.selected_cat:
                r = randint(1,100)
                accompliced = False
                chance = self.get_accomplice_chance(game.clan.your_cat, self.selected_cat)
                if game.config["accomplice_chance"] != -1:
                    try:
                        chance = game.config["accomplice_chance"]
                    except:
                        pass
                if r < chance:
                    accompliced = True
                    if 'accomplices' in game.switches:
                        game.switches['accomplices'].append(self.selected_cat.ID)
                    else:
                        game.switches['accomplices'] = []
                        game.switches['accomplices'].append(self.selected_cat.ID)
                                            
                self.change_cat(self.murder_cat, self.selected_cat, accompliced)
                self.stage = 'choose murder cat'
                

            elif self.stage == 'choose murder method' and event.ui_element == self.next:
                self.change_cat(self.murder_cat, None, None)
                self.stage = 'choose murder cat'
            
            elif self.stage == 'choose accomplice' and event.ui_element == self.next:
                self.change_cat(self.murder_cat, None, None)
                self.stage = 'choose murder method'
            
            elif event.ui_element == self.back_button:
                self.change_screen('profile screen')
                self.stage = 'choose murder cat'

            # Method buttons
            elif event.ui_element == self.attackmethod:
                self.method = 'attack'
                self.attackmethod.disable()
                self.poisonmethod.enable()
                self.accidentmethod.enable()
                self.predatormethod.enable()
                self.update_selected_cat()
                chance = self.get_kill(game.clan.your_cat, self.cat_to_murder, accomplice=None, accompliced=None)
                risk_chance = self.get_risk_chance(self.cat_to_murder, accomplice=None, accompliced=None)
                discover_chance = self.get_discover_chance(game.clan.your_cat, self.cat_to_murder, accomplice=None, accompliced=None)
                self.update_method_info()
            elif event.ui_element == self.poisonmethod:
                self.method = 'poison'
                self.poisonmethod.disable()
                self.attackmethod.enable()
                self.accidentmethod.enable()
                self.predatormethod.enable()
                self.update_selected_cat()
                chance = self.get_kill(game.clan.your_cat, self.cat_to_murder, accomplice=None, accompliced=None)
                risk_chance = self.get_risk_chance(self.cat_to_murder, accomplice=None, accompliced=None)
                discover_chance = self.get_discover_chance(game.clan.your_cat, self.cat_to_murder, accomplice=None, accompliced=None)
                self.update_method_info()
            elif event.ui_element == self.accidentmethod:
                self.method = 'accident'
                self.accidentmethod.disable()
                self.poisonmethod.enable()
                self.attackmethod.enable()
                self.predatormethod.enable()
                self.update_selected_cat()
                chance = self.get_kill(game.clan.your_cat, self.cat_to_murder, accomplice=None, accompliced=None)
                risk_chance = self.get_risk_chance(self.cat_to_murder, accomplice=None, accompliced=None)
                discover_chance = self.get_discover_chance(game.clan.your_cat, self.cat_to_murder, accomplice=None, accompliced=None)
                self.update_method_info()
            elif event.ui_element == self.predatormethod:
                self.method = 'predator'
                self.predatormethod.disable()
                self.poisonmethod.enable()
                self.accidentmethod.enable()
                self.attackmethod.enable()
                self.update_selected_cat()
                chance = self.get_kill(game.clan.your_cat, self.cat_to_murder, accomplice=None, accompliced=None)
                risk_chance = self.get_risk_chance(self.cat_to_murder, accomplice=None, accompliced=None)
                discover_chance = self.get_discover_chance(game.clan.your_cat, self.cat_to_murder, accomplice=None, accompliced=None)
                self.update_method_info()

            # Location buttons
            elif event.ui_element == self.camplocation:
                self.location = 'camp'
                self.camplocation.disable()
                self.territorylocation.enable()
                self.borderlocation.enable()
                self.update_selected_cat()
                chance = self.get_kill(game.clan.your_cat, self.cat_to_murder, accomplice=None, accompliced=None)
                risk_chance = self.get_risk_chance(self.cat_to_murder, accomplice=None, accompliced=None)
                discover_chance = self.get_discover_chance(game.clan.your_cat, self.cat_to_murder, accomplice=None, accompliced=None)
                self.update_method_info()
            elif event.ui_element == self.territorylocation:
                self.location = 'territory'
                self.territorylocation.disable()
                self.camplocation.enable()
                self.borderlocation.enable()
                self.update_selected_cat()
                chance = self.get_kill(game.clan.your_cat, self.cat_to_murder, accomplice=None, accompliced=None)
                risk_chance = self.get_risk_chance(self.cat_to_murder, accomplice=None, accompliced=None)
                discover_chance = self.get_discover_chance(game.clan.your_cat, self.cat_to_murder, accomplice=None, accompliced=None)
                self.update_method_info()
            elif event.ui_element == self.borderlocation:
                self.location = 'border'
                self.borderlocation.disable()
                self.territorylocation.enable()
                self.camplocation.enable()
                self.update_selected_cat()
                chance = self.get_kill(game.clan.your_cat, self.cat_to_murder, accomplice=None, accompliced=None)
                risk_chance = self.get_risk_chance(self.cat_to_murder, accomplice=None, accompliced=None)
                discover_chance = self.get_discover_chance(game.clan.your_cat, self.cat_to_murder, accomplice=None, accompliced=None)
                self.update_method_info()

            # Time buttons
            elif event.ui_element == self.dawntime:
                self.time = 'dawn'
                self.dawntime.disable()
                self.daytime.enable()
                self.nighttime.enable()
                self.update_selected_cat()
                chance = self.get_kill(game.clan.your_cat, self.cat_to_murder, accomplice=None, accompliced=None)
                risk_chance = self.get_risk_chance(self.cat_to_murder, accomplice=None, accompliced=None)
                discover_chance = self.get_discover_chance(game.clan.your_cat, self.cat_to_murder, accomplice=None, accompliced=None)
                self.update_method_info()
            elif event.ui_element == self.daytime:
                self.time = 'day'
                self.daytime.disable()
                self.dawntime.enable()
                self.nighttime.enable()
                self.update_selected_cat()
                chance = self.get_kill(game.clan.your_cat, self.cat_to_murder, accomplice=None, accompliced=None)
                risk_chance = self.get_risk_chance(self.cat_to_murder, accomplice=None, accompliced=None)
                discover_chance = self.get_discover_chance(game.clan.your_cat, self.cat_to_murder, accomplice=None, accompliced=None)
                self.update_method_info()
            elif event.ui_element == self.nighttime:
                self.time = 'night'
                self.nighttime.disable()
                self.daytime.enable()
                self.dawntime.enable()
                self.update_selected_cat()
                chance = self.get_kill(game.clan.your_cat, self.cat_to_murder, accomplice=None, accompliced=None)
                risk_chance = self.get_risk_chance(self.cat_to_murder, accomplice=None, accompliced=None)
                discover_chance = self.get_discover_chance(game.clan.your_cat, self.cat_to_murder, accomplice=None, accompliced=None)
                self.update_method_info()

            elif event.ui_element == self.next_cat_button:
                if isinstance(Cat.fetch_cat(self.next_cat), Cat):
                    game.switches['cat'] = self.next_cat
                    self.update_cat_list()
                    self.update_selected_cat()
                    # self.update_buttons()
                else:
                    print("invalid next cat", self.next_cat)
            elif event.ui_element == self.previous_cat_button:
                if isinstance(Cat.fetch_cat(self.previous_cat), Cat):
                    game.switches['cat'] = self.previous_cat
                    self.update_cat_list()
                    self.update_selected_cat()
                    # self.update_buttons()
                else:
                    print("invalid previous cat", self.previous_cat)
            elif event.ui_element == self.next_page_button:
                self.current_page += 1
                self.update_cat_list()
            elif event.ui_element == self.previous_page_button:
                self.current_page -= 1
                self.update_cat_list()

    def screen_switches(self):

        if self.stage == 'choose murder cat':
            self.the_cat = game.clan.your_cat
            self.mentor = Cat.fetch_cat(self.the_cat.mentor)
            self.selected_cat = None
            self.next = None
            self.methodheading = None
            self.methodinfo = None
            self.locationinfo = None
            self.timeinfo = None
            self.timeheading = None
            self.locationheading = None
            self.accomplice_frame = None
            self.victim_sprite = None
            self.victim_info = None
            self.victim_name = None

            self.list_frame = pygame.transform.scale(image_cache.load_image("resources/images/choosing_frame.png").convert_alpha(),
                                        (1300 / 1600 * screen_x, 452 / 1400 * screen_y))
            
            self.heading = pygame_gui.elements.UITextBox("Choose your target",
                                                        scale(pygame.Rect((300, 50), (1000, 80))),
                                                        object_id=get_text_box_theme("#text_box_34_horizcenter"),
                                                        manager=MANAGER)
            
            # Layout Images:
            self.mentor_frame = pygame_gui.elements.UIImage(scale(pygame.Rect((130, 226), (569, 399))),
                                                            pygame.transform.scale(
                                                                image_cache.load_image(
                                                                    "resources/images/murder_select.png").convert_alpha(),
                                                                (569, 399)), manager=MANAGER)
            self.your_sprite = pygame_gui.elements.UIImage(
                                            scale(pygame.Rect((685, 285), (270, 270))),
                                            pygame.transform.scale(
                                                self.the_cat.sprite,
                                                (270, 270)), manager=MANAGER)
            
            self.methodtext = pygame_gui.elements.UITextBox("Method:",
                                                        scale(pygame.Rect((1090, 150), (200, 80))),
                                                        object_id=get_text_box_theme("#text_box_30_horizcenter"),
                                                        manager=MANAGER)
        
            self.attackmethod = UIImageButton(scale(pygame.Rect((1000, 220), (90, 90))), "A",
                                                tool_tip_text= "Attack", object_id="", manager=MANAGER)
            self.poisonmethod = UIImageButton(scale(pygame.Rect((1100, 220), (90, 90))), "P",
                                                tool_tip_text= "Poison", object_id="", manager=MANAGER)
            self.accidentmethod = UIImageButton(scale(pygame.Rect((1200, 220), (90, 90))), "AC",
                                                tool_tip_text= "Accident", object_id="", manager=MANAGER)
            self.predatormethod = UIImageButton(scale(pygame.Rect((1300, 220), (90, 90))), "PR",
                                                tool_tip_text= "Predator", object_id="", manager=MANAGER)
            
            self.attackmethod.disable()
            self.poisonmethod.disable()
            self.accidentmethod.disable()
            self.predatormethod.disable()

            self.locationtext = pygame_gui.elements.UITextBox("Location:",
                                                        scale(pygame.Rect((1090, 330), (200, 80))),
                                                        object_id=get_text_box_theme("#text_box_30_horizcenter"),
                                                        manager=MANAGER)

            self.camplocation = UIImageButton(scale(pygame.Rect((1040, 400), (90, 90))), "C",
                                                tool_tip_text= "Camp", object_id="", manager=MANAGER)
            self.territorylocation = UIImageButton(scale(pygame.Rect((1140, 400), (90, 90))), "T",
                                                tool_tip_text= "Territory", object_id="", manager=MANAGER)
            self.borderlocation = UIImageButton(scale(pygame.Rect((1240, 400), (90, 90))), "B",
                                                tool_tip_text= "Border", object_id="", manager=MANAGER)
            
            self.camplocation.disable()
            self.territorylocation.disable()
            self.borderlocation.disable()

            self.timetext = pygame_gui.elements.UITextBox("Time:",
                                                        scale(pygame.Rect((1090, 510), (200, 80))),
                                                        object_id=get_text_box_theme("#text_box_30_horizcenter"),
                                                        manager=MANAGER)

            self.dawntime = UIImageButton(scale(pygame.Rect((1040, 580), (90, 90))), "D",
                                                tool_tip_text= "Dawn", object_id="", manager=MANAGER)
            self.daytime = UIImageButton(scale(pygame.Rect((1140, 580), (90, 90))), "DY",
                                                tool_tip_text= "Day", object_id="", manager=MANAGER)
            self.nighttime = UIImageButton(scale(pygame.Rect((1240, 580), (90, 90))), "N",
                                                tool_tip_text= "Night", object_id="", manager=MANAGER)
            
            self.dawntime.disable()
            self.daytime.disable()
            self.nighttime.disable()
            
            self.back_button = UIImageButton(scale(pygame.Rect((50, 1290), (204, 60))), "", object_id="#back_button")
            self.confirm_mentor = UIImageButton(scale(pygame.Rect((700, 620), (208, 52))), "",
                                                object_id="#continue_button_small")
        
            self.previous_page_button = UIImageButton(scale(pygame.Rect((630, 1155), (68, 68))), "",
                                                    object_id="#relation_list_previous", manager=MANAGER)
            self.next_page_button = UIImageButton(scale(pygame.Rect((902, 1155), (68, 68))), "",
                                                object_id="#relation_list_next", manager=MANAGER)

            self.update_selected_cat()  # Updates the image and details of selected cat
            self.update_cat_list()

        elif self.stage == 'choose murder method':
            self.the_cat = game.clan.your_cat
            self.mentor = Cat.fetch_cat(self.the_cat.mentor)
            self.selected_cat = self.cat_to_murder
            self.next = None
            self.methodinfo = None
            self.locationinfo = None
            self.locationheading = None
            self.methodheading = None
            self.timeinfo = None
            self.timeheading = None
            self.accomplice_frame = None
            self.victim_sprite = None
            self.victim_info = None
            self.victim_name = None

            self.list_frame = None

            self.heading = pygame_gui.elements.UITextBox("Choose your plan",
                                                        scale(pygame.Rect((300, 50), (1000, 80))),
                                                        object_id=get_text_box_theme("#text_box_34_horizcenter"),
                                                        manager=MANAGER)
           
            # Layout Images:
            self.mentor_frame = pygame_gui.elements.UIImage(scale(pygame.Rect((130, 226), (569, 399))),
                                                            pygame.transform.scale(
                                                                image_cache.load_image(
                                                                    "resources/images/murder_select.png").convert_alpha(),
                                                                (569, 399)), manager=MANAGER)
            
            self.selected_details["selected_image"] = pygame_gui.elements.UIImage(
                                            scale(pygame.Rect((163, 310), (270, 270))),
                                            pygame.transform.scale(
                                                self.selected_cat.sprite,
                                                (270, 270)), manager=MANAGER)
            
            
            if game.settings['dark mode']:
                self.selected_details["chance"] = pygame_gui.elements.UITextBox("success chance: ...",
                                                                                        scale(pygame.Rect((228, 530),
                                                                                                            (210, 250))),
                                                                                        object_id="#text_box_22_horizcenter_vertcenter_spacing_95_dark",
                                                                                        manager=MANAGER)

            else:
                self.selected_details["chance"] = pygame_gui.elements.UITextBox("success chance: ...",
                                                                                    scale(pygame.Rect((228, 530),
                                                                                                        (210, 250))),
                                                                                    object_id="#text_box_22_horizcenter_vertcenter_spacing_95",
                                                                                    manager=MANAGER)
                
            if (game.clan.your_cat.skills.meets_skill_requirement(SkillPath.PROPHET) or\
                game.clan.your_cat.skills.meets_skill_requirement(SkillPath.CLEVER) or\
                game.clan.your_cat.skills.meets_skill_requirement(SkillPath.SENSE) or\
                game.clan.your_cat.skills.meets_skill_requirement(SkillPath.OMEN) or\
                game.clan.your_cat.skills.meets_skill_requirement(SkillPath.INSIGHTFUL)):
                self.selected_details["chance"].show()
            else:
                self.selected_details["chance"].hide()
           
            
            self.your_sprite = pygame_gui.elements.UIImage(
                                            scale(pygame.Rect((685, 285), (270, 270))),
                                            pygame.transform.scale(
                                                self.the_cat.sprite,
                                                (270, 270)), manager=MANAGER)
            

            self.methodtext = pygame_gui.elements.UITextBox("Method:",
                                                        scale(pygame.Rect((1090, 150), (200, 80))),
                                                        object_id=get_text_box_theme("#text_box_30_horizcenter"),
                                                        manager=MANAGER)
        
            self.attackmethod = UIImageButton(scale(pygame.Rect((1000, 220), (90, 90))), "A",
                                                tool_tip_text= "Attack", object_id="", manager=MANAGER)
            self.poisonmethod = UIImageButton(scale(pygame.Rect((1100, 220), (90, 90))), "P",
                                                tool_tip_text= "Poison", object_id="", manager=MANAGER)
            self.accidentmethod = UIImageButton(scale(pygame.Rect((1200, 220), (90, 90))), "AC",
                                                tool_tip_text= "Accident", object_id="", manager=MANAGER)
            self.predatormethod = UIImageButton(scale(pygame.Rect((1300, 220), (90, 90))), "PR",
                                                tool_tip_text= "Predator", object_id="", manager=MANAGER)
            
            self.attackmethod.disable()
            self.poisonmethod.enable()
            self.accidentmethod.enable()
            self.predatormethod.enable()

            self.locationtext = pygame_gui.elements.UITextBox("Location:",
                                                        scale(pygame.Rect((1090, 330), (200, 80))),
                                                        object_id=get_text_box_theme("#text_box_30_horizcenter"),
                                                        manager=MANAGER)

            self.camplocation = UIImageButton(scale(pygame.Rect((1040, 400), (90, 90))), "C",
                                                tool_tip_text= "Camp", object_id="", manager=MANAGER)
            self.territorylocation = UIImageButton(scale(pygame.Rect((1140, 400), (90, 90))), "T",
                                                tool_tip_text= "Territory", object_id="", manager=MANAGER)
            self.borderlocation = UIImageButton(scale(pygame.Rect((1240, 400), (90, 90))), "B",
                                                tool_tip_text= "Border", object_id="", manager=MANAGER)
            
            self.camplocation.disable()
            self.territorylocation.enable()
            self.borderlocation.enable()

            self.timetext = pygame_gui.elements.UITextBox("Time:",
                                                        scale(pygame.Rect((1090, 510), (200, 80))),
                                                        object_id=get_text_box_theme("#text_box_30_horizcenter"),
                                                        manager=MANAGER)

            self.dawntime = UIImageButton(scale(pygame.Rect((1040, 580), (90, 90))), "D",
                                                tool_tip_text= "Dawn", object_id="", manager=MANAGER)
            self.daytime = UIImageButton(scale(pygame.Rect((1140, 580), (90, 90))), "DY",
                                                tool_tip_text= "Day", object_id="", manager=MANAGER)
            self.nighttime = UIImageButton(scale(pygame.Rect((1240, 580), (90, 90))), "N",
                                                tool_tip_text= "Night", object_id="", manager=MANAGER)
            
            self.dawntime.enable()
            self.daytime.disable()
            self.nighttime.enable()

            # info = self.selected_cat.status + "\n" + \
            #        self.selected_cat.genderalign + "\n" + self.selected_cat.personality.trait + "\n"

            # if self.selected_cat.moons < 1:
            #     info += "???"
            # else:
            #     info += self.selected_cat.skills.skill_string(short=True)

            # self.victim_info = pygame_gui.elements.UITextBox(info,scale(pygame.Rect((470, 325),(210, 250))),
            #                                             object_id="#text_box_22_horizcenter_vertcenter_spacing_95",
            #                                             manager=MANAGER)
            
            # name = str(self.cat_to_murder.name)  # get name

            # if 11 <= len(name):  # check name length
            #     short_name = str(name)[0:9]
            #     name = short_name + '...'

            # self.victim_name = pygame_gui.elements.ui_label.UILabel(
            #     scale(pygame.Rect((190, 230), (220, 60))),
            #     name,
            #     object_id="#text_box_34_horizcenter", manager=MANAGER)
            
            self.back_button = UIImageButton(scale(pygame.Rect((50, 1290), (204, 60))), "", object_id="#back_button")
            self.confirm_mentor = UIImageButton(scale(pygame.Rect((700, 620), (208, 52))), "",
                                                object_id="#continue_button_small")
        
            self.previous_page_button = UIImageButton(scale(pygame.Rect((630, 1155), (68, 68))), "",
                                                    object_id="#relation_list_previous", manager=MANAGER)
            self.next_page_button = UIImageButton(scale(pygame.Rect((902, 1155), (68, 68))), "",
                                                object_id="#relation_list_next", manager=MANAGER)
            
            self.previous_page_button.hide()
            self.next_page_button.hide()

            self.update_method_info()

            self.update_selected_cat()  # Updates the image and details of selected cat
            # self.update_cat_list()
        else:
            self.the_cat = game.clan.your_cat
            self.mentor = Cat.fetch_cat(self.the_cat.mentor)
            # self.selected_cat = None
            self.next = None
            self.methodheading = None
            self.methodinfo = None
            self.locationinfo = None
            self.locationheading = None
            self.timeinfo = None
            self.timeheading = None

            self.methodtext = None

            self.attackmethod = None
            self.poisonmethod = None
            self.accidentmethod = None
            self.predatormethod = None

            self.camplocation = None
            self.territorylocation = None
            self.borderlocation = None

            self.dawntime = None
            self.daytime = None
            self.nighttime = None

            self.methodtext = None
            self.locationtext = None
            self.timetext = None

            self.list_frame = pygame.transform.scale(image_cache.load_image("resources/images/choosing_frame.png").convert_alpha(),
                                        (1300 / 1600 * screen_x, 452 / 1400 * screen_y))


            self.heading = pygame_gui.elements.UITextBox("Choose an accomplice",
                                                        scale(pygame.Rect((300, 50), (1000, 80))),
                                                        object_id=get_text_box_theme("#text_box_34_horizcenter"),
                                                        manager=MANAGER)
            
            # Layout Images:
            self.mentor_frame = pygame_gui.elements.UIImage(scale(pygame.Rect((130, 226), (569, 399))),
                                                            pygame.transform.scale(
                                                                image_cache.load_image(
                                                                    "resources/images/murder_select.png").convert_alpha(),
                                                                (569, 399)), manager=MANAGER)
            
            self.accomplice_frame = pygame_gui.elements.UIImage(scale(pygame.Rect((900, 226), (569, 399))),
                                                            pygame.transform.scale(
                                                                image_cache.load_image(
                                                                    "resources/images/choosing_cat2_frame_ment.png").convert_alpha(),
                                                                (569, 399)), manager=MANAGER)
            if game.settings['dark mode']:
                self.selected_details["chance2"] = pygame_gui.elements.UITextBox("success chance: ...",
                                                                                        scale(pygame.Rect((228, 530),
                                                                                                            (210, 250))),
                                                                                        object_id="#text_box_22_horizcenter_vertcenter_spacing_95_dark",
                                                                                        manager=MANAGER)

            else:
                self.selected_details["chance2"] = pygame_gui.elements.UITextBox("success chance: ...",
                                                                                    scale(pygame.Rect((228, 530),
                                                                                                        (210, 250))),
                                                                                    object_id="#text_box_22_horizcenter_vertcenter_spacing_95",
                                                                                    manager=MANAGER)
            if (game.clan.your_cat.skills.meets_skill_requirement(SkillPath.PROPHET) or\
                game.clan.your_cat.skills.meets_skill_requirement(SkillPath.CLEVER) or\
                game.clan.your_cat.skills.meets_skill_requirement(SkillPath.SENSE) or\
                game.clan.your_cat.skills.meets_skill_requirement(SkillPath.OMEN) or\
                game.clan.your_cat.skills.meets_skill_requirement(SkillPath.INSIGHTFUL)):
                self.selected_details["chance2"].show()
            else:
                self.selected_details["chance2"].hide()
            
            self.your_sprite = pygame_gui.elements.UIImage(
                                            scale(pygame.Rect((685, 285), (270, 270))),
                                            pygame.transform.scale(
                                                self.the_cat.sprite,
                                                (270, 270)), manager=MANAGER)
            
            self.victim_sprite = pygame_gui.elements.UIImage(
                                            scale(pygame.Rect((163, 310), (270, 270))),
                                            pygame.transform.scale(
                                                self.cat_to_murder.sprite,
                                                (270, 270)), manager=MANAGER)
            
            info = self.selected_cat.status + "\n" + \
                   self.selected_cat.genderalign + "\n" + self.selected_cat.personality.trait + "\n"

            if self.selected_cat.moons < 1:
                info += "???"
            else:
                info += self.selected_cat.skills.skill_string(short=True)

            self.victim_info = pygame_gui.elements.UITextBox(info,scale(pygame.Rect((470, 325),(210, 250))),
                                                        object_id="#text_box_22_horizcenter_vertcenter_spacing_95",
                                                        manager=MANAGER)
            
            name = str(self.cat_to_murder.name)  # get name

            if 11 <= len(name):  # check name length
                short_name = str(name)[0:9]
                name = short_name + '...'

            self.victim_name = pygame_gui.elements.ui_label.UILabel(
                scale(pygame.Rect((190, 230), (220, 60))),
                name,
                object_id="#text_box_34_horizcenter", manager=MANAGER)

            self.back_button = UIImageButton(scale(pygame.Rect((50, 1290), (204, 60))), "", object_id="#back_button")
            self.confirm_mentor = UIImageButton(scale(pygame.Rect((700, 620), (208, 52))), "",
                                                object_id="#continue_button_small")
        
            self.previous_page_button = UIImageButton(scale(pygame.Rect((630, 1155), (68, 68))), "",
                                                    object_id="#relation_list_previous", manager=MANAGER)
            self.next_page_button = UIImageButton(scale(pygame.Rect((902, 1155), (68, 68))), "",
                                                object_id="#relation_list_next", manager=MANAGER)
            
            self.next = UIImageButton(scale(pygame.Rect((950, 610), (68, 68))), "",
                                                tool_tip_text= "Proceed without an accomplice.",
                                                object_id="#arrow_right_button", manager=MANAGER)
            
            self.previous_page_button.show()
            self.next_page_button.show()

            selected_cat = None

            self.update_selected_cat2()  # Updates the image and details of selected cat
            self.update_cat_list2()


    def exit_screen(self):

       
        for ele in self.cat_list_buttons:
            self.cat_list_buttons[ele].kill()
        self.cat_list_buttons = {}

        for ele in self.apprentice_details:
            self.apprentice_details[ele].kill()
        self.apprentice_details = {}

        for ele in self.selected_details:
            self.selected_details[ele].kill()
        self.selected_details = {}
        
        if self.heading:
            self.heading.kill()
            del self.heading

        if self.mentor_frame:
            self.mentor_frame.kill()
            del self.mentor_frame

        if self.accomplice_frame:
            self.accomplice_frame.kill()
            del self.accomplice_frame

        if self.your_sprite:
            self.your_sprite.kill()
            del self.your_sprite

        if self.victim_sprite:
            self.victim_sprite.kill()
            del self.victim_sprite

        if self.victim_info:
            self.victim_info.kill()
            del self.victim_info

        if self.victim_name:
            self.victim_name.kill()
            del self.victim_name

        if self.methodinfo:
            self.methodinfo.kill()
            del self.methodinfo

        if self.locationinfo:
            self.locationinfo.kill()
            del self.locationinfo
        
        if self.timeinfo:
            self.timeinfo.kill()
            del self.timeinfo

        if self.methodheading:
            self.methodheading.kill()
            del self.methodheading

        if self.locationheading:
            self.locationheading.kill()
            del self.locationheading

        if self.timeheading:
            self.timeheading.kill()
            del self.timeheading
        
        if self.methodtext:
            self.methodtext.kill()
            del self.methodtext

        if self.locationtext:
            self.locationtext.kill()
            del self.locationtext
        
        if self.timetext:
            self.timetext.kill()
            del self.timetext
        
        if self.attackmethod:
            self.attackmethod.kill()
            del self.attackmethod

        if self.poisonmethod:
            self.poisonmethod.kill()
            del self.poisonmethod

        if self.accidentmethod:
            self.accidentmethod.kill()
            del self.accidentmethod

        if self.predatormethod:
            self.predatormethod.kill()
            del self.predatormethod

        if self.camplocation:
            self.camplocation.kill()
            del self.camplocation
        
        if self.territorylocation:
            self.territorylocation.kill()
            del self.territorylocation

        if self.borderlocation:
            self.borderlocation.kill()
            del self.borderlocation

        if self.dawntime:
            self.dawntime.kill()
            del self.dawntime
        
        if self.daytime:
            self.daytime.kill()
            del self.daytime

        if self.nighttime:
            self.nighttime.kill()
            del self.nighttime

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
        self.exit_screen()
        r = randint(0,100)
        r2 = randint(-10, 10)
        chance = self.get_kill(game.clan.your_cat, self.cat_to_murder, accomplice, accompliced)
        if game.config["murder_chance"] != -1:
            try:
                chance = game.config["murder_chance"]
            except:
                pass
        murdered = r < max(5, chance + r2)
        you = game.clan.your_cat
        cat_to_murder = self.cat_to_murder
        game.clan.murdered = True
        if murdered:
            self.choose_murder_text(you, cat_to_murder, accomplice, accompliced)
        else:
            self.handle_murder_fail(you, cat_to_murder, accomplice, accompliced)

        game.switches['cur_screen'] = "events screen"
    
    RESOURCE_DIR = "resources/dicts/events/lifegen_events/"

    def get_risk_chance(self, cat_to_murder, accomplice, accompliced):
        you = game.clan.your_cat
        chance = 0

        # GENERAL
        # lowers risk
        if you.joined_df:
            chance -= 4
        if you.age != cat_to_murder.age and you.moons > cat_to_murder.moons:
            chance -= 2
        if cat_to_murder.age == "senior":
            chance -= 2
        if you.status == cat_to_murder.status:
            chance -= 1
        if cat_to_murder.is_ill() or cat_to_murder.is_injured():
            chance -= 5
        if you.experience > cat_to_murder.experience:
            chance -= 2
        if accomplice and accompliced:
            chance -= 3

        # raises risk
        if cat_to_murder.joined_df:
            chance += 4
        if cat_to_murder.moons >= you.moons + 4:
            chance += 2
        if you.is_ill() or you.is_injured():
            chance += 2
        
        if cat_to_murder.status == "leader":
            if game.clan.leader_lives > 1:
                chance += 5
            else:
                chance += 2

        if cat_to_murder.experience > you.experience:
            chance += 2

        if cat_to_murder.skills.meets_skill_requirement(SkillPath.GUARDIAN):
            chance += 1
        if cat_to_murder.skills.meets_skill_requirement(SkillPath.COOPERATIVE):
            chance += 1
        if cat_to_murder.skills.meets_skill_requirement(SkillPath.OMEN):
            chance += 2
        if cat_to_murder.skills.meets_skill_requirement(SkillPath.PROPHET):
            chance += 2
        if cat_to_murder.skills.meets_skill_requirement(SkillPath.SENSE):
            chance += 2

        if self.method == "attack":
            if you.joined_df:
                chance -= 5
            if you.skills.meets_skill_requirement(SkillPath.HUNTER):
                chance -= 4
            if you.skills.meets_skill_requirement(SkillPath.FIGHTER):
                chance -= 4
            if you.skills.meets_skill_requirement(SkillPath.GRACE):
                chance -= 4
            if you.status == "warrior":
                chance -= 3
            if you.age != cat_to_murder.age and you.moons > cat_to_murder.moons:
                chance -= 2

            if self.location == "border":
                chance -= 1

            if you.personality.trait == "bloodthirsty":
                chance -= 4

            # lowers chances

            if cat_to_murder.status == "warrior":
                chance += 3
            if you.status in ["mediator", "mediator apprentice", "queen", "queen's apprentice", "medicine cat", "medicine cat apprentice", "kitten"]:
                chance += 4
            if cat_to_murder.skills.meets_skill_requirement(SkillPath.FIGHTER):
                chance += 5
            if self.location == "camp":
                chance += 1
            if cat_to_murder.personality.trait == "bloodthirsty":
                chance += 4

        if self.method == "poison":

         # raises chances
            if self.location == "camp":
                chance -= 3

        # lowers chances
            if self.location == "border":
                chance += 2

        if self.method == "accident":
            # raises chances
            if you.skills.meets_skill_requirement(SkillPath.EXPLORER):
                chance -= 4
            if you.skills.meets_skill_requirement(SkillPath.NAVIGATOR):
                chance -= 4
            if you.skills.meets_skill_requirement(SkillPath.CLIMBER):
                chance -= 4

            if self.location == "camp":
                chance -= 4

            # lowers chances

            if game.clan.biome == "Mountainous":
                chance += 4
            if cat_to_murder.status in ["warrior", "deputy", "leader"]:
                chance += 3

        if self.method == "predator":

        # raises chances
            if you.skills.meets_skill_requirement(SkillPath.LANGUAGE):
                chance -= 5
            if self.location == "camp":
                chance -= 4

            # lowers chances
            if cat_to_murder.status in ["warrior", "deputy", "leader"]:
                chance += 3
            if you.status in ["queen", "mediator", "kitten", "medicine cat", "queen's apprentice", "mediator apprentice", "medicine cat apprentice"]:
                chance += 3
            if cat_to_murder.skills.meets_skill_requirement(SkillPath.GUARDIAN):
                chance += 4
            if cat_to_murder.skills.meets_skill_requirement(SkillPath.FIGHTER):
                chance += 4
            if cat_to_murder.skills.meets_skill_requirement(SkillPath.LANGUAGE):
                chance += 2

        print("RISK CHANCE: ", chance)

        return chance
    

    def choose_murder_text(self, you, cat_to_murder, accomplice, accompliced):
        with open(f"{self.RESOURCE_DIR}murder.json",
                encoding="ascii") as read_file:
            self.m_txt = ujson.loads(read_file.read())
        with open(f"{self.RESOURCE_DIR}murder_unsuccessful.json",
                encoding="ascii") as read_file:
            self.mu_txt = ujson.loads(read_file.read())

        risk = randint(1,15)
        risk_chance = self.get_risk_chance(cat_to_murder, accomplice=None, accompliced=None)
        injury = False

        if risk < risk_chance + 1:
            injury = True
            you.get_injured("claw-wound")
        print("INJURY: ", injury)

      
        insert = f"{you.status} "
        insert2 = f"{cat_to_murder.status} "

        statuses = [
            f"{insert} {insert2} ",
            f"any {insert2} ",
            f"{insert} any ",
            "any any "]

        for status in statuses:
            try:
                if injury:
                    ceremony_txt = self.m_txt[status + "murder " + self.method.replace(" ", "") + " " + self.location.replace(" ", "") + " " + self.time.replace(" ", "") + " injury"]
                    ceremony_txt.extend(self.m_txt[status +  "murder " + self.method.replace(" ", "") + " " + self.location.replace(" ", "") + " injury"])
                else:
                    ceremony_txt = self.m_txt[status +  "murder " + self.method.replace(" ", "") + " " + self.location.replace(" ", "") + " " + self.time.replace(" ", "")]
                    ceremony_txt.extend(self.m_txt[status +  "murder " + self.method.replace(" ", "") + " " + self.location.replace(" ", "")])
                ceremony_txt = choice(ceremony_txt)
            except:
                try:
                    if injury:
                        ceremony_txt = self.m_txt[status +  "murder " + self.method.replace(" ", "") + " " + self.location.replace(" ", "") + " injury"]
                        ceremony_txt.extend(self.m_txt[status +  "murder " + self.method.replace(" ", "") + " injury"])
                    else:
                        ceremony_txt = self.m_txt[status +  "murder " + self.method.replace(" ", "") + " " + self.location.replace(" ", "")]
                        ceremony_txt.extend(self.m_txt[status +  "murder " + self.method.replace(" ", "")])
                    ceremony_txt = choice(ceremony_txt)
                except:
                    try:
                        if injury:
                            ceremony_txt = self.m_txt[status + "murder " + self.method.replace(" ", "") + " injury"]
                        else:
                            ceremony_txt = self.m_txt[status + "murder " + self.method.replace(" ", "")]
                        ceremony_txt = choice(ceremony_txt)
                    except:
                        ceremony_txt = choice(self.m_txt["murder general"])
                        print("Warning: No unique murder events found for ", insert, insert2, ".")
            
        other_clan = choice(game.clan.all_clans)
        ceremony_txt = ceremony_txt.replace('v_c', str(cat_to_murder.name))
        ceremony_txt = ceremony_txt.replace('c_n', game.clan.name)
        ceremony_txt = ceremony_txt.replace("o_c", str(other_clan.name))
        if cat_to_murder.status == 'leader':
            game.clan.leader_lives = 0
        cat_to_murder.die()
        game.cur_events_list.insert(0, Single_Event(ceremony_txt))

        discover_chance = self.get_discover_chance(you, cat_to_murder, accomplice, accompliced)
        discovery_num = randint(1,10)

        # discover_chance = 3
        # discovery_num = 1
        # ^^ shun debug

        discovered = False
        if discovery_num < (discover_chance + 1):
            discovered = True
        else:
            discovered = False
            
        if discovered:
            if accomplice and accompliced:
                game.cur_events_list.insert(1, Single_Event("You successfully murdered "+ str(cat_to_murder.name) + " with the help of " + str(accomplice.name) + "."))
                History.add_death(cat_to_murder, f"{you.name} and {accomplice.name} murdered this cat.")
                History.add_murders(cat_to_murder, accomplice, True, f"{you.name} murdered this cat along with {accomplice.name}.")
                History.add_murders(cat_to_murder, you, True, f"{you.name} murdered this cat with the help of {accomplice.name}.")
                
                accguiltchance = randint(1,2)
                if accguiltchance == 1:
                    accomplice.get_injured("guilt")

                youguiltchance = randint(1,4)
                if youguiltchance == 1:
                    accomplice.get_injured("guilt")

            else:
                game.cur_events_list.insert(1, Single_Event("You successfully murdered "+ str(cat_to_murder.name) + "."))
                History.add_death(cat_to_murder, f"{you.name} murdered this cat.")
                History.add_murders(cat_to_murder, you, True, f"{you.name} murdered this cat.")
            self.choose_discover_punishment(you, cat_to_murder, accomplice, accompliced)
        else:
            if accomplice:
                if accompliced:
                    History.add_death(cat_to_murder, f"{you.name} and {accomplice.name} murdered this cat.")
                    History.add_murders(cat_to_murder, you, True, f"{you.name} murdered this cat along with {accomplice.name}.")
                    History.add_murders(cat_to_murder, accomplice, True, f"{you.name} murdered this cat along with {accomplice.name}.")
                    game.cur_events_list.insert(1, Single_Event("You successfully murdered "+ str(cat_to_murder.name) + " along with " + str(accomplice.name) + ". It seems no one is aware of your actions."))

                    accguiltchance = randint(1,4)
                    if accguiltchance == 1:
                        accomplice.get_injured("guilt")

                    youguiltchance = randint(1,6)
                    if youguiltchance == 1:
                        accomplice.get_injured("guilt")


                else:
                    History.add_death(cat_to_murder, f"{you.name} murdered this cat.")
                    History.add_murders(cat_to_murder, you, True, f"{you.name} murdered this cat.")
                    game.cur_events_list.insert(1, Single_Event("You successfully murdered "+ str(cat_to_murder.name) + " but " + str(accomplice.name) + " chose not to help. It seems no one is aware of your actions."))
            else:
                History.add_death(cat_to_murder, f"{you.name} murdered this cat.")
                History.add_murders(cat_to_murder, you, True, f"{you.name} murdered this cat.")
                game.cur_events_list.insert(1, Single_Event("You successfully murdered "+ str(cat_to_murder.name) + ". It seems no one is aware of your actions."))
        
        
          
    def choose_discover_punishment(self, you, cat_to_murder, accomplice, accompliced):
        # 1 = you punished, 2 = accomplice punished, 3 = both punished
        punishment_chance = randint(1,3)
        if not accomplice or not accompliced:
            punishment_chance = 1
        if punishment_chance == 1:
            if accomplice and not accompliced:
                a_s = randint(1,2)
                if a_s == 1 and accomplice.status != "leader":
                    game.cur_events_list.insert(2, Single_Event(f"Shocked at your request to be an accomplice to murder, {accomplice.name} reports your actions to the Clan leader."))
                you.shunned = 1
            txt = ""
            if game.clan.your_cat.status in ['kitten', 'leader', 'deputy', 'medicine cat']:
                txt = choice(self.mu_txt["murder_discovered " + game.clan.your_cat.status])
            else:
                txt = choice(self.mu_txt["murder_discovered general"])
            txt = txt.replace('v_c', str(cat_to_murder.name))
            game.cur_events_list.insert(2, Single_Event(txt))
            you.shunned = 1
            you.faith -= 0.5
        elif punishment_chance == 2:
            txt = f"{accomplice.name} is blamed for the murder of v_c. However, you were not caught."
            txt = txt.replace('v_c', str(cat_to_murder.name))
            game.cur_events_list.insert(2, Single_Event(txt))
            accomplice.shunned = 1
            accomplice.faith -= 0.5
        else:
            txt = f"The unsettling truth of v_c's death is discovered, with you and {accomplice.name} responsible. The Clan decides both of your punishments."
            txt = txt.replace('v_c', str(cat_to_murder.name))
            game.cur_events_list.insert(2, Single_Event(txt))
            you.shunned = 1
            accomplice.shunned = 1
            accomplice.faith -= 0.5
        
        if punishment_chance == 1 or punishment_chance == 3:
            kit_punishment = ["You are assigned counseling by the Clan's medicine cat to help you understand the severity of your actions and to guide you to make better decisions in the future.",
                                "You are to be kept in the nursery under the watchful eye of the queens at all times until you become an apprentice."]
            gen_punishment = ["You are assigned counseling by the Clan's medicine cat to help you understand the severity of your actions and to guide you to make better decisions in the future.",
                                "You will be required to take meals last and are forced to sleep in a separate den away from your clanmates.",
                                "You are assigned to several moons of tasks that include cleaning out nests, checking elders for ticks, and other chores alongside your normal duties.",
                                "You are assigned a mentor who will better educate you about the Warrior Code and the sacredness of life."]
            # demote_leader = ["Your lives will be stripped away and you will be demoted to a warrior, no longer trusted to be the Clan's leader."]
            # demote_deputy = ["The Clan decides that you will be demoted to a warrior, no longer trusting you as their deputy."]
            # demote_medicine_cat = ["The Clan decides that you will be demoted to a warrior, no longer trusting you as their medicine cat."]
            # exiled = ["The Clan decides that they no longer feel safe with you as a Clanmate. You will be exiled from the Clan."]
            
            if you.status == 'kitten' or you.status == 'newborn':
                game.cur_events_list.insert(3, Single_Event(choice(kit_punishment)))
            elif you.status == 'leader':
                lead_choice = randint(1,3)
                if lead_choice == 1:
                    game.cur_events_list.insert(3, Single_Event(choice(gen_punishment)))
            elif you.status == 'deputy':
                lead_choice = randint(1,3)
                if lead_choice == 1:
                    game.cur_events_list.insert(3, Single_Event(choice(gen_punishment)))
            elif you.status == 'medicine cat':
                lead_choice = randint(1,3)
                if lead_choice == 1:
                    game.cur_events_list.insert(3, Single_Event(choice(gen_punishment)))
            else:
                lead_choice = randint(1,5)
                if lead_choice in [1, 2, 3, 4]:
                    game.cur_events_list.insert(3, Single_Event(choice(gen_punishment)))
        
        if accomplice and accompliced and (punishment_chance == 2 or punishment_chance == 3):
            a_n = str(accomplice.name)
            kit_punishment = [f"{a_n} is assigned counseling by the Clan's medicine cat to help them understand the severity of their actions and to guide them to make better decisions in the future.",
                            f"{a_n} is to be kept in the nursery under the watchful eye of the queens at all times until they become an apprentice."]
            gen_punishment = [f"{a_n} is assigned counseling by the Clan's medicine cat to help them understand the severity of their actions and to guide them to make better decisions in the future.",
                                f"{a_n} is required to take meals last and is forced to sleep in a separate den away from their clanmates.",
                                f"{a_n} is assigned to several moons of tasks that include cleaning out nests, checking elders for ticks, and other chores alongside their normal duties.",
                                f"{a_n} is assigned a mentor who will better educate them about the Warrior Code and the sacredness of life."]
            
            # demote_leader = [f"{a_n}'s lives will be stripped away and they will be demoted to a warrior, no longer trusted to be the Clan's leader."]
            # demote_deputy = [f"The Clan decides that {a_n} will be demoted to a warrior, no longer trusting them as their deputy."]
            # demote_medicine_cat = [f"The Clan decides that {a_n} will be demoted to a warrior, no longer trusting them as their medicine cat."]
            # exiled = [f"The Clan decides that they no longer feel safe with {a_n} as a Clanmate. They will be exiled from the Clan."]

            if accomplice.status == 'kitten' or accomplice.status == 'newborn':
                game.cur_events_list.insert(3, Single_Event(choice(kit_punishment)))
            elif accomplice.status == 'leader':
                lead_choice = randint(1,3)
                if lead_choice == 1:
                    game.cur_events_list.insert(3, Single_Event(choice(gen_punishment)))
                
            elif accomplice.status == 'deputy':
                lead_choice = randint(1,3)
                if lead_choice == 1:
                    game.cur_events_list.insert(3, Single_Event(choice(gen_punishment)))
               
            elif accomplice.status == 'medicine cat':
                lead_choice = randint(1,3)
                if lead_choice == 1:
                    game.cur_events_list.insert(3, Single_Event(choice(gen_punishment)))
                
            else:
                lead_choice = randint(1,5)
                if lead_choice in [1, 2, 3, 4]:
                    game.cur_events_list.insert(3, Single_Event(choice(gen_punishment)))
    
    def get_discover_chance(self, you, cat_to_murder, accomplice=None, accompliced=None):
        chance = 0
        # location chances
        if self.location == "camp":
            if self.method == "attack":
                chance += 5 
            if self.method == "poison":
                if game.clan.your_cat.status == "medicine cat":
                    chance += 0
                else:
                    chance += 2
            if self.method == "accident":
                chance += 3
            if self.method == "predator":
                chance += 3

            if self.time == "day":
                chance -= 1

        elif self.location == "territory":
            if self.method == "attack":
                chance += 2 
            if self.method == "poison":
                if game.clan.your_cat.status == "medicine cat":
                    chance += 2
                else:
                    chance += 3
            if self.method == "accident":
                chance += 2
            if self.method == "predator":
                chance += 1

        elif self.location == "border":
            if self.method == "attack":
                chance += 2 
            if self.method == "poison":
                chance += 3
            if self.method == "accident":
                chance += 3
            if self.method == "predator":
                chance += 2

            if game.clan.war.get("at_war", True):
                chance -= 1

        if self.time == "dawn":
            if self.method == "attack":
                chance += 4
            if self.method == "poison":
                if game.clan.your_cat.status == "medicine cat":
                    chance += 0
                else:
                    chance += 2
            if self.method == "accident":
                chance += 3
            if self.method == "predator":
                chance += 3

        if self.time == "day":
            if self.method == "attack":
                chance += 4
            if self.method == "poison":
                if game.clan.your_cat.status == "medicine cat":
                    chance += 2
                else:
                    chance += 3
            if self.method == "accident":
                chance += 1
            if self.method == "predator":
                chance += 2

        if self.time == "night":
            if self.method == "attack":
                chance += 1
            if self.method == "poison":
                chance += 2
            if self.method == "accident":
                chance += 4
            if self.method == "predator":
                chance += 1

        print("DISCOVERY CHANCE: ", chance)

        if chance < 0:
            chance = 0
        if chance > 10:
            chance = 10

        return chance

    def handle_murder_fail(self, you, cat_to_murder, accomplice, accompliced):
        c_m = str(cat_to_murder.name)
        discover_chance = randint(1,2)
        fail_texts = []
        if discover_chance == 1:
            fail_texts = ["You attempted to murder "+ c_m + ", but were unsuccessful. They were oblivious of your attempt.",
                            "You attempted to murder "+ c_m + ", but they sidestepped the peril you'd arranged. They remained oblivious to your intent.",
                            "You made an effort to end "+ c_m + "'s life, but fortune favored them. They were none the wiser of your deadly plot.",
                            "Your plot to murder "+ c_m + " fell through, and they went about their day, unaware of the fate you'd intended for them.",
                            "Despite your best efforts, "+ c_m + " remained unscathed. They continued on, blissfully ignorant of your lethal plan.",
                            "Your attempt to kill "+ c_m + " proved futile, and they stayed clueless about your ominous intentions."]
        else:
            if accomplice and accompliced:
                fail_texts = [f"You attempted to murder {c_m}, but your plot was unsuccessful. They appear to be slightly wary of you and {accomplice.name} now.",
                                f"Your effort to end {c_m}'s life was thwarted, and they now seem a bit more cautious around you and {accomplice.name}.",
                                f"Despite your intent to murder {c_m}, they remained unscathed. They now look at you and {accomplice.name} with a hint of suspicion.",
                                f"You and {accomplice.name} tried to kill {c_m}, but they survived. They now seem to watch you both with wary eyes.",
                                f"Your plot to murder {c_m} fell through, and they remain alive, now showing signs of mild suspicion towards you and {accomplice.name}."]
                cat_to_murder.relationships[you.ID].dislike += randint(1,20)
                cat_to_murder.relationships[you.ID].platonic_like -= randint(1,15)
                cat_to_murder.relationships[you.ID].comfortable -= randint(1,15)
                cat_to_murder.relationships[you.ID].trust -= randint(1,15)
                cat_to_murder.relationships[you.ID].admiration -= randint(1,15)
                cat_to_murder.relationships[accomplice.ID].dislike += randint(1,20)
                cat_to_murder.relationships[accomplice.ID].platonic_like -= randint(1,15)
                cat_to_murder.relationships[accomplice.ID].comfortable -= randint(1,15)
                cat_to_murder.relationships[accomplice.ID].trust -= randint(1,15)
                cat_to_murder.relationships[accomplice.ID].admiration -= randint(1,15)                
            else:
                fail_texts = ["You attempted to murder "+ c_m + ", but your plot was unsuccessful. They appear to be slightly wary now.",
                                "Your effort to end "+ c_m + "'s life was thwarted, and they now seem a bit more cautious around you.",
                                "Despite your intent to murder "+ c_m + ", they remained unscathed. They look at you now with a hint of suspicion.",
                                "You tried to kill "+ c_m + ", but they survived. They now seem to watch you with wary eyes.",
                                "Your plot to murder "+ c_m + " fell through, and they remain alive, now showing signs of mild suspicion towards you."]
                cat_to_murder.relationships[you.ID].dislike += randint(1,20)
                cat_to_murder.relationships[you.ID].platonic_like -= randint(1,15)
                cat_to_murder.relationships[you.ID].comfortable -= randint(1,15)
                cat_to_murder.relationships[you.ID].trust -= randint(1,15)
                cat_to_murder.relationships[you.ID].admiration -= randint(1,15)
        game.cur_events_list.insert(0, Single_Event(choice(fail_texts)))
        
    
    # status_chances = {
    #     'warrior': 40,
    #     'medicine cat': 40,
    #     'mediator': 35,
    #     'apprentice': 30,
    #     'medicine cat apprentice': 25,
    #     'mediator apprentice': 20,
    #     "queen": 25,
    #     "queen's apprentice": 20,
    #     'deputy': 50,
    #     'leader': 60,
    #     'elder': 25,
    #     'kitten': 10,
    # }

    # skill_chances = {
    #     'warrior': -5,
    #     'medicine cat': -5,
    #     'mediator': 0,
    #     'apprentice': 5,
    #     'medicine cat apprentice': 5,
    #     'mediator apprentice': 5,
    #     "queen's apprentice": 10,
    #     'queen': 5,
    #     'deputy': -10,
    #     'leader': -15,
    #     'elder': 5,
    #     'kitten': 30
    # }

    # murder_skills = ["quick witted", "avid play-fighter", "oddly observant","never sits still"]
    # good_murder_skills = ["clever", "good fighter", "natural intuition","fast runner"]
    # great_murder_skills = ["very clever", "formidable fighter", "keen eye","incredible runner"]
    # best_murder_skills = ["incredibly clever", "unusually strong fighter", "unnatural senses","fast as the wind"]


    def get_kill(self, you, cat_to_murder, accomplice, accompliced):
        chance = 30
        # GENERAL CHANCES
        # raises chances:
        if you.joined_df:
            chance += 15
        if you.age != cat_to_murder.age and you.moons > cat_to_murder.moons:
            chance += 10
        if cat_to_murder.age == "senior":
            chance += 10
        if you.status == cat_to_murder.status:
            chance += 10
        if cat_to_murder.is_ill() or cat_to_murder.is_injured():
            chance += 10
        if you.experience > cat_to_murder.experience:
            chance += 5
        if accomplice and accompliced:
            chance += 15

        if you.history:
            if you.history.murder:
                if "is_murderer" in you.history.murder:
                    if len(you.history.murder["is_murderer"]) > 0:
                        for i in range(len(you.history.murder["is_murderer"])):
                            chance += 5


        if cat_to_murder.relationships[you.ID].platonic_like > 20 and cat_to_murder.relationships[you.ID].platonic_like < 50:
            chance += 10
        elif cat_to_murder.relationships[you.ID].platonic_like >= 50:
            chance += 15

        # lowers chances:

        if cat_to_murder.joined_df:
            chance -= 10
        if cat_to_murder.moons >= you.moons + 4:
            chance -= 10
        if you.is_ill() or you.is_injured():
            chance -= 10

        if cat_to_murder.status == "leader" and cat_to_murder.shunned == 0:
            chance -= 10

        if cat_to_murder.moons < 6:
            for cat in Cat.all_cats_list:
                if cat.status == "queen":
                    chance -= 5
                if cat.ID == (cat_to_murder.parent1 or cat_to_murder.parent2) or cat.ID in cat_to_murder.adoptive_parents:
                    chance -= 5

        if cat_to_murder.experience > you.experience:
            chance -= 5

        if cat_to_murder.skills.meets_skill_requirement(SkillPath.GUARDIAN):
            chance -= 5
        if cat_to_murder.skills.meets_skill_requirement(SkillPath.COOPERATIVE):
            chance -= 5
        if cat_to_murder.skills.meets_skill_requirement(SkillPath.OMEN):
            chance -= 5
        if cat_to_murder.skills.meets_skill_requirement(SkillPath.PROPHET):
            chance -= 5
        if cat_to_murder.skills.meets_skill_requirement(SkillPath.SENSE):
            chance -= 5
        
        if cat_to_murder.skills.meets_skill_requirement(SkillPath.CAMP) and self.location != "camp":
            chance -= 5

        if cat_to_murder.status in ["queen", "queen's apprentice", "medicine cat", "medicine cat apprentice", "kitten"] and self.location != "camp":
            chance -= 10

        if cat_to_murder.history:
            if cat_to_murder.history.murder:
                if "is_murderer" in cat_to_murder.history.murder:
                    if len(cat_to_murder.history.murder["is_murderer"]) > 0:
                        for i in range(len(cat_to_murder.history.murder["is_murderer"])):
                            chance -= 5

        if cat_to_murder.relationships[you.ID].dislike > 20 and cat_to_murder.relationships[you.ID].platonic_like < 50:
            chance -= 10
        elif cat_to_murder.relationships[you.ID].dislike >= 50:
            chance -= 15

        # METHOD CHANCES
        # ATTACK
        if self.method == "attack":
            # raises chances
            if you.joined_df:
                chance += 15
            if you.skills.meets_skill_requirement(SkillPath.HUNTER):
                chance += 10
            if you.skills.meets_skill_requirement(SkillPath.FIGHTER):
                chance += 10
            if you.skills.meets_skill_requirement(SkillPath.GRACE):
                chance += 10
            if you.status == "warrior":
                chance += 10
            if you.age != cat_to_murder.age and you.moons > cat_to_murder.moons:
                chance += 10

            if self.location == "border":
                chance += 15

            if you.personality.trait == "bloodthirsty":
                chance += 10

            # lowers chances

            if cat_to_murder.status == "warrior":
                chance -= 10
            if you.status in ["mediator", "mediator apprentice", "queen", "queen's apprentice", "medicine cat", "medicine cat apprentice", "kitten"]:
                chance -= 10
            if cat_to_murder.skills.meets_skill_requirement(SkillPath.FIGHTER):
                chance -= 10
            if self.location == "camp":
                chance -= 15
            if cat_to_murder.personality.trait == "bloodthirsty":
                chance -= 10

        if self.method == "poison":
            # raises chances
            if you.status in ["medicine cat", "medicine cat apprentice"]:
                chance += 25
            if cat_to_murder.is_ill() or cat_to_murder.is_injured():
                chance += 15

            if self.location == "camp":
                chance += 10
            if self.location == "territory":
                chance += 15

            # lowers chances
            if cat_to_murder.status in ["medicine cat", "medicine cat apprentice"]:
                chance -= 15
            if cat_to_murder.skills.meets_skill_requirement(SkillPath.HEALER):
                chance -= 5
            if not cat_to_murder.is_ill() and not cat_to_murder.is_injured():
                chance -= 10
            if you.status not in ["medicine cat", "medicine cat apprentice"]:
                chance -= 20

            if self.location == "border":
                chance -= 10

        if self.method == "accident":
            # raises chances
            if you.skills.meets_skill_requirement(SkillPath.EXPLORER):
                chance += 15
            if you.skills.meets_skill_requirement(SkillPath.NAVIGATOR):
                chance += 15
            if you.skills.meets_skill_requirement(SkillPath.CLIMBER):
                chance += 15
            if cat_to_murder.status in ["kitten", "queen", "apprentice", "queen's apprentice", "medicine cat apprentice", "mediator apprentice"] and \
                not cat_to_murder.skills.meets_skill_requirement(SkillPath.EXPLORER) and\
                not cat_to_murder.skills.meets_skill_requirement(SkillPath.NAVIGATOR) and\
                not cat_to_murder.skills.meets_skill_requirement(SkillPath.CLIMBER):
                chance += 10
            if you.age == cat_to_murder.age and you.age in ["kitten", "adolescent"]:
                chance += 10

            if game.clan.biome == "Mountainous":
                chance += 10

            if self.location == "territory":
                chance += 15

            # lowers chances
            if cat_to_murder.skills.meets_skill_requirement(SkillPath.EXPLORER):
                chance -= 15
            if cat_to_murder.skills.meets_skill_requirement(SkillPath.NAVIGATOR):
                chance -= 15
            if cat_to_murder.skills.meets_skill_requirement(SkillPath.SENSE):
                chance -= 15
            
            if cat_to_murder.status in ["warrior", "deputy", "leader"]:
                chance -= 15
            if you.moons >= 12 and cat_to_murder.moons >= 12:
                chance -= 10

            if self.location == "camp":
                chance -= 15

        if self.method == "predator":
            # raises chances
            chance += 20
            if cat_to_murder.moons < 6:
                chance += 20
            if self.location in ["territory", "border"]:
                chance += 15
            if you.skills.meets_skill_requirement(SkillPath.LANGUAGE):
                chance += 20

            # lowers chances
            if cat_to_murder.moons >= 12:
                chance -= 10
            if cat_to_murder.status in ["warrior", "deputy", "leader"]:
                chance -= 10
            if you.status in ["queen", "mediator", "kitten", "medicine cat", "queen's apprentice", "mediator apprentice", "medicine cat apprentice"]:
                chance -= 15
            if cat_to_murder.skills.meets_skill_requirement(SkillPath.GUARDIAN):
                chance -= 15
            if cat_to_murder.skills.meets_skill_requirement(SkillPath.FIGHTER):
                chance -= 15
            if self.location == "camp":
                chance -= 10
            if cat_to_murder.skills.meets_skill_requirement(SkillPath.LANGUAGE):
                chance -= 15



        print("CHANCE: ", chance)
        if chance < 0:
            chance = 0

        if chance > 95:
            chance = 95

        return chance
    
    def update_method_info(self):

        if self.methodinfo:
            self.methodinfo.kill()
            del self.methodinfo

        if self.methodheading:
            self.methodheading.kill()
            del self.methodheading
        
        if self.locationinfo:
            self.locationinfo.kill()
            del self.locationinfo

        if self.locationheading:
            self.locationheading.kill()
            del self.locationheading

        if self.timeinfo:
            self.timeinfo.kill()
            del self.timeinfo

        if self.timeheading:
            self.timeheading.kill()
            del self.timeheading

        # METHOD INFO
        if self.method == "attack":
            self.methodheading = pygame_gui.elements.UITextBox("<b>An Attack</b>",
                                                scale(pygame.Rect((250, 750), (1100, 100))),
                                                object_id=get_text_box_theme("#text_box_34_horizcenter"),
                                                manager=MANAGER)
            self.methodinfo = pygame_gui.elements.UITextBox("For those who aren't afraid to use their claws.",
                                                scale(pygame.Rect((250, 820), (1100, 300))),
                                                object_id=get_text_box_theme("#text_box_30_horizcenter"),
                                                manager=MANAGER)
        elif self.method == "poison":
            self.methodheading = pygame_gui.elements.UITextBox("<b>A Poisoning</b>",
                                                scale(pygame.Rect((250, 750), (1100, 100))),
                                                object_id=get_text_box_theme("#text_box_34_horizcenter"),
                                                manager=MANAGER)
            self.methodinfo = pygame_gui.elements.UITextBox("Those familiar with medicine may want to consider using their skills for evil.",
                                                scale(pygame.Rect((250, 800), (1100, 300))),
                                                object_id=get_text_box_theme("#text_box_30_horizcenter"),
                                                manager=MANAGER)
    
        elif self.method == "accident":
            self.methodheading = pygame_gui.elements.UITextBox("<b>An \"Accident\"</b>",
                                                scale(pygame.Rect((250, 750), (1100, 100))),
                                                object_id=get_text_box_theme("#text_box_34_horizcenter"),
                                                manager=MANAGER)
            self.methodinfo = pygame_gui.elements.UITextBox("A strategy for those who are great at feigning innocence.",
                                                scale(pygame.Rect((250, 800), (1100, 300))),
                                                object_id=get_text_box_theme("#text_box_30_horizcenter"),
                                                manager=MANAGER)

        elif self.method == "predator":
            self.methodheading = pygame_gui.elements.UITextBox("<b>Lure a Predator</b>",
                                                scale(pygame.Rect((250, 750), (1100, 100))),
                                                object_id=get_text_box_theme("#text_box_34_horizcenter"),
                                                manager=MANAGER)
            self.methodinfo = pygame_gui.elements.UITextBox("A risky technique for those who don't want to get their own paws dirty.",
                                                scale(pygame.Rect((250, 800), (1100, 300))),
                                                object_id=get_text_box_theme("#text_box_30_horizcenter"),
                                                manager=MANAGER)
        # LOCATION INFO
        if self.location == "camp":
            if self.method == "predator":
                insert = "To"
            else:
                insert = "In"
                
            self.locationheading = pygame_gui.elements.UITextBox(f"<b>{insert} Camp</b>",
                                                scale(pygame.Rect((250, 900), (1100, 100))),
                                                object_id=get_text_box_theme("#text_box_34_horizcenter"),
                                                manager=MANAGER)
            self.locationinfo = pygame_gui.elements.UITextBox("For a kill closer to home.",
                                                scale(pygame.Rect((250, 950), (1100, 300))),
                                                object_id=get_text_box_theme("#text_box_30_horizcenter"),
                                                manager=MANAGER)
    
        elif self.location == "territory":
            if self.method == "predator":
                insert = "To"
            else:
                insert = "In"
            self.locationheading = pygame_gui.elements.UITextBox(f"<b>{insert} the Territory</b>",
                                                scale(pygame.Rect((250, 900), (1100, 100))),
                                                object_id=get_text_box_theme("#text_box_34_horizcenter"),
                                                manager=MANAGER)
            self.locationinfo = pygame_gui.elements.UITextBox("Who knows what could happen out there?",
                                                scale(pygame.Rect((250, 950), (1100, 300))),
                                                object_id=get_text_box_theme("#text_box_30_horizcenter"),
                                                manager=MANAGER)

        elif self.location == "border":
            if self.method == "predator":
                insert = "To"
            else:
                insert = "At"
                
            self.locationheading = pygame_gui.elements.UITextBox(f"<b>{insert} the Border</b>",
                                                scale(pygame.Rect((250, 900), (1100, 100))),
                                                object_id=get_text_box_theme("#text_box_34_horizcenter"),
                                                manager=MANAGER)
            self.locationinfo = pygame_gui.elements.UITextBox("The border is a dangerous place.",
                                                scale(pygame.Rect((250, 950), (1100, 300))),
                                                object_id=get_text_box_theme("#text_box_30_horizcenter"),
                                                manager=MANAGER)
        # TIME INFO 
        if self.time == "dawn":
            self.timeheading = pygame_gui.elements.UITextBox("<b>At Dawn</b>",
                                                scale(pygame.Rect((250, 1050), (1100, 100))),
                                                object_id=get_text_box_theme("#text_box_34_horizcenter"),
                                                manager=MANAGER)
            self.timeinfo = pygame_gui.elements.UITextBox("The early bird gets the worm!",
                                                scale(pygame.Rect((250, 1100), (1100, 300))),
                                                object_id=get_text_box_theme("#text_box_30_horizcenter"),
                                                manager=MANAGER)
    
        elif self.time == "day":
            self.timeheading = pygame_gui.elements.UITextBox("<b>During the Day</b>",
                                                scale(pygame.Rect((250, 1050), (1100, 100))),
                                                object_id=get_text_box_theme("#text_box_34_horizcenter"),
                                                manager=MANAGER)
            self.timeinfo = pygame_gui.elements.UITextBox("Want to strike in broad daylight?",
                                                scale(pygame.Rect((250, 1100), (1100, 300))),
                                                object_id=get_text_box_theme("#text_box_30_horizcenter"),
                                                manager=MANAGER)

        elif self.time == "night":
            self.timeheading = pygame_gui.elements.UITextBox("<b>At Night</b>",
                                                scale(pygame.Rect((250, 1050), (1100, 100))),
                                                object_id=get_text_box_theme("#text_box_34_horizcenter"),
                                                manager=MANAGER)
            self.timeinfo = pygame_gui.elements.UITextBox("Take advantage of the darkness.",
                                                scale(pygame.Rect((250, 1100), (1100, 300))),
                                                object_id=get_text_box_theme("#text_box_30_horizcenter"),
                                                manager=MANAGER)
            
    def update_chance_text(self):
        if self.selected_cat:
            if (not self.selected_cat.dead and not self.selected_cat.outside) or (not self.cat_to_murder.dead and not self.cat_to_murder.outside):
                if (game.clan.your_cat.skills.meets_skill_requirement(SkillPath.PROPHET) or\
                    game.clan.your_cat.skills.meets_skill_requirement(SkillPath.CLEVER) or\
                    game.clan.your_cat.skills.meets_skill_requirement(SkillPath.SENSE) or\
                    game.clan.your_cat.skills.meets_skill_requirement(SkillPath.OMEN) or\
                    game.clan.your_cat.skills.meets_skill_requirement(SkillPath.INSIGHTFUL)):
                
                    c_text = ""
                    chance = self.get_kill(game.clan.your_cat, self.selected_cat, None, False)
                    if chance < 20:
                        c_text = "very low"
                    elif chance < 30:
                        c_text = "low"
                    elif chance < 40:
                        c_text = "average"
                    elif chance < 70:
                        c_text = "high"
                    else:
                        c_text = "very high"
                    if game.settings['dark mode']:
                        self.selected_details["chance"] = pygame_gui.elements.UITextBox("success chance: " + c_text,
                                                                                                scale(pygame.Rect((228, 530),
                                                                                                                    (210, 250))),
                                                                                                object_id="#text_box_22_horizcenter_vertcenter_spacing_95_dark",
                                                                                                manager=MANAGER)

                    else:
                        self.selected_details["chance"] = pygame_gui.elements.UITextBox("success chance: " + c_text,
                                                                                            scale(pygame.Rect((228, 530),
                                                                                                                (210, 250))),
                                                                                            object_id="#text_box_22_horizcenter_vertcenter_spacing_95",
                                                                                            manager=MANAGER)
            if self.stage == "choose accomplice":
                if not self.selected_cat.dead and not self.selected_cat.outside:
                    c_text = ""
                    chance = self.get_accomplice_chance(game.clan.your_cat, self.selected_cat)
                    if game.config["accomplice_chance"] != -1:
                        try:
                            chance = game.config["accomplice_chance"]
                        except:
                            pass
                    if chance < 30:
                        c_text = "very low"
                    elif chance < 40:
                        c_text = "low"
                    elif chance < 50:
                        c_text = "average"
                    elif chance < 70:
                        c_text = "high"
                    else:
                        c_text = "very high"
                    if game.settings['dark mode']:
                        self.selected_details["willingness"] = pygame_gui.elements.UITextBox("willingness: " + c_text,
                                                                                                scale(pygame.Rect((1205, 530),
                                                                                                                    (210, 250))),
                                                                                                object_id="#text_box_22_horizcenter_vertcenter_spacing_95_dark",
                                                                                                manager=MANAGER)

                    else:
                        self.selected_details["willingness"] = pygame_gui.elements.UITextBox("willingness: " + c_text,
                                                                                            scale(pygame.Rect((1205, 530),
                                                                                                                (210, 250))),
                                                                                            object_id="#text_box_22_horizcenter_vertcenter_spacing_95",
                                                                                            manager=MANAGER)
    
    def update_selected_cat(self):
        """Updates the image and information on the currently selected mentor"""
        for ele in self.selected_details:
            self.selected_details[ele].kill()
        self.selected_details = {}
        if self.selected_cat:

            self.selected_details["selected_image"] = pygame_gui.elements.UIImage(
                scale(pygame.Rect((163, 310), (270, 270))),
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
                                                                                   scale(pygame.Rect((470, 325),
                                                                                                     (210, 250))),
                                                                                   object_id="#text_box_22_horizcenter_vertcenter_spacing_95",
                                                                                   manager=MANAGER)

            name = str(self.selected_cat.name)  # get name
            if 11 <= len(name):  # check name length
                short_name = str(name)[0:9]
                name = short_name + '...'
            self.selected_details["victim_name"] = pygame_gui.elements.ui_label.UILabel(
                scale(pygame.Rect((190, 230), (220, 60))),
                name,
                object_id="#text_box_34_horizcenter", manager=MANAGER)
            
            self.update_chance_text()
            

    def get_accomplice_chance(self, you, accomplice):
        chance = 10
        if accomplice.relationships[you.ID].platonic_like > 10:
            chance += 10
        if accomplice.relationships[you.ID].dislike < 10:
            chance += 10
        if accomplice.relationships[you.ID].romantic_love > 10:
            chance += 10
        if accomplice.relationships[you.ID].comfortable > 10:
            chance += 10
        if accomplice.relationships[you.ID].trust > 10:
            chance += 10
        if accomplice.relationships[you.ID].admiration > 10:
            chance += 10
        if you.status in ['medicine cat', 'mediator', 'deputy', 'leader']:
            chance += 10
        if accomplice.status in ['medicine cat', 'mediator', 'deputy', 'leader']:
            chance -= 20
        if accomplice.ID in game.clan.your_cat.mate:
            chance += 50
        if game.clan.your_cat.is_related(accomplice, False):
            chance += 30
        return chance
                    
    def update_selected_cat2(self):
        """Updates the image and information on the currently selected mentor"""
        for ele in self.selected_details:
            self.selected_details[ele].kill()
        self.selected_details = {}
        if self.selected_cat and self.selected_cat.ID != self.cat_to_murder.ID:
            self.selected_details["selected_image"] = pygame_gui.elements.UIImage(
                scale(pygame.Rect((1162, 310), (270, 270))),
                pygame.transform.scale(
                    self.selected_cat.sprite,
                    (300, 300)), manager=MANAGER)

            info = self.selected_cat.status + "\n" + \
                   self.selected_cat.genderalign + "\n" + self.selected_cat.personality.trait + "\n"
            
            if self.selected_cat.moons < 1:
                info += "???"
            else:
                info += self.selected_cat.skills.skill_string(short=True)
            
            self.selected_details["selected_info_acc"] = pygame_gui.elements.UITextBox(info,
                                                                                   scale(pygame.Rect((922, 325),
                                                                                                     (210, 250))),
                                                                                   object_id="#text_box_22_horizcenter_vertcenter_spacing_95",
                                                                                   manager=MANAGER)

            name = str(self.selected_cat.name)  # get name
            if 11 <= len(name):  # check name length
                short_name = str(name)[0:9]
                name = short_name + '...'
            self.selected_details["mentor_name"] = pygame_gui.elements.ui_label.UILabel(
                scale(pygame.Rect((1175, 230), (220, 60))),
                name,
                object_id="#text_box_34_horizcenter", manager=MANAGER)
            
        self.update_chance_text()
            
            

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
        valid_mentors = self.chunks(self.get_valid_cats2(), 30)

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
        if valid_mentors and len(valid_mentors) > self.current_page - 1:
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


    def get_valid_cats(self):
        valid_mentors = []

        for cat in Cat.all_cats_list:
            if not cat.dead and not cat.outside and not cat.ID == game.clan.your_cat.ID and not cat.moons == 0:
                valid_mentors.append(cat)
        
        return valid_mentors

    def get_valid_cats2(self):
        valid_mentors = []

        for cat in Cat.all_cats_list:
            if not cat.dead and not cat.outside and not cat.ID == game.clan.your_cat.ID and not cat.ID == self.cat_to_murder.ID and not cat.moons == 0:
                valid_mentors.append(cat)
        
        return valid_mentors

    def on_use(self):
        # Due to a bug in pygame, any image with buttons over it must be blited
        if self.list_frame:
            screen.blit(self.list_frame, (150 / 1600 * screen_x, 720 / 1400 * screen_y))

    def chunks(self, L, n):
        return [L[x: x + n] for x in range(0, len(L), n)]
