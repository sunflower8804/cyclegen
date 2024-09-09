from random import choice, choices, randint
import pygame
import ujson
import re

from scripts.utility import scale

from .Screens import Screens

from scripts.utility import generate_sprite, get_cluster, get_alive_cats, get_alive_status_cats, pronoun_repl, adjust_txt
from scripts.cat.cats import Cat
from scripts.game_structure import image_cache
import pygame_gui
from scripts.game_structure.game_essentials import game, screen_x, screen_y, MANAGER, screen
from scripts.game_structure.ui_elements import IDImageButton, UIImageButton, UISpriteButton
from enum import Enum  # pylint: disable=no-name-in-module
from scripts.housekeeping.version import VERSION_NAME


class RelationType(Enum):
    """An enum representing the possible age groups of a cat"""

    BLOOD = ''                      # direct blood related - do not need a special print
    ADOPTIVE = 'adoptive'       	# not blood related but close (parents, kits, siblings)
    HALF_BLOOD = 'half sibling'   	# only one blood parent is the same (siblings only)
    NOT_BLOOD = 'not blood related'	# not blood related for parent siblings
    RELATED = 'blood related'   	# related by blood (different mates only)

BLOOD_RELATIVE_TYPES = [RelationType.BLOOD, RelationType.HALF_BLOOD, RelationType.RELATED]

class InsultScreen(Screens):

    def __init__(self, name=None):
        super().__init__(name)
        self.back_button = None
        self.resource_dir = "resources/dicts/lifegen_talk/"
        self.texts = ""
        self.text_frames = [[text[:i+1] for i in range(len(text))] for text in self.texts]
        self.scroll_container = None
        self.life_text = None
        self.header = None
        self.the_cat = None
        self.text_index = 0
        self.frame_index = 0
        self.typing_delay = 20
        self.next_frame_time = pygame.time.get_ticks() + self.typing_delay
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 32)
        self.text = None
        self.profile_elements = {}
        self.talk_box_img = None
        self.possible_texts = {}
        self.chosen_text_key = ""
        self.choice_buttons = {}
        self.text_choices = {}
        self.option_bgs = {}
        self.current_scene = ""
        self.created_choice_buttons = False
        self.choicepanel = False
        self.textbox_graphic = None
        self.cat_dict = {}
        self.other_dict = {}

    def screen_switches(self):
        self.the_cat = Cat.all_cats.get(game.switches['cat'])
        self.cat_dict.clear()
        self.update_camp_bg()
        self.hide_menu_buttons()
        self.text_index = 0
        self.frame_index = 0
        self.choicepanel = False
        self.created_choice_buttons = False
        self.profile_elements = {}
        self.clan_name_bg = pygame_gui.elements.UIImage(
            scale(pygame.Rect((230, 875), (380, 70))),
            pygame.transform.scale(
                image_cache.load_image(
                    "resources/images/clan_name_bg.png").convert_alpha(),
                (500, 870)),
            manager=MANAGER)
        self.profile_elements["cat_name"] = pygame_gui.elements.UITextBox(str(self.the_cat.name),
                                                                       scale(pygame.Rect((300, 870), (-1, 80))),
                                                                          object_id="#text_box_34_horizcenter_light",
                                                                          manager=MANAGER)

        self.text_type = ""
        self.texts = self.load_texts(self.the_cat)
        self.text_frames = [[text[:i+1] for i in range(len(text))] for text in self.texts]
        self.talk_box_img = image_cache.load_image("resources/images/talk_box.png").convert_alpha()

        self.talk_box = pygame_gui.elements.UIImage(
                scale(pygame.Rect((178, 942), (1248, 302))),
                self.talk_box_img
            )

        self.back_button = UIImageButton(scale(pygame.Rect((50, 50), (210, 60))), "",
                                        object_id="#back_button", manager=MANAGER)
        self.scroll_container = pygame_gui.elements.UIScrollingContainer(scale(pygame.Rect((500, 970), (900, 300))))
        self.text = pygame_gui.elements.UITextBox("",
                                                  scale(pygame.Rect((0, 0), (900, -100))),
                                                  object_id="#text_box_30_horizleft",
                                                  container=self.scroll_container,
                                                manager=MANAGER)

        self.textbox_graphic = pygame_gui.elements.UIImage(
                scale(pygame.Rect((170, 942), (346, 302))),
                image_cache.load_image("resources/images/textbox_graphic.png").convert_alpha()
            )
        # self.textbox_graphic.hide()

        self.profile_elements["cat_image"] = pygame_gui.elements.UIImage(scale(pygame.Rect((70, 900), (400, 400))),
                                                                         pygame.transform.scale(
                                                                             generate_sprite(self.the_cat),
                                                                             (400, 400)), manager=MANAGER)
        self.paw = pygame_gui.elements.UIImage(
                scale(pygame.Rect((1370, 1180), (30, 30))),
                image_cache.load_image("resources/images/cursor.png").convert_alpha()
            )
        self.paw.visible = False


    def exit_screen(self):
        self.text.kill()
        del self.text
        self.scroll_container.kill()
        del self.scroll_container
        self.back_button.kill()
        del self.back_button
        self.profile_elements["cat_image"].kill()
        self.profile_elements["cat_name"].kill()
        del self.profile_elements
        self.clan_name_bg.kill()
        del self.clan_name_bg
        self.talk_box.kill()
        del self.talk_box
        self.textbox_graphic.kill()
        del self.textbox_graphic
        self.paw.kill()
        del self.paw
        for button in self.choice_buttons:
            self.choice_buttons[button].kill()
        self.choice_buttons = {}
        for option in self.text_choices:
            self.text_choices[option].kill()
        self.text_choices = {}
        for option_bg in self.option_bgs:
            self.option_bgs[option_bg].kill()
        self.option_bgs = {}

    def update_camp_bg(self):
        light_dark = "light"
        if game.settings["dark mode"]:
            light_dark = "dark"

        camp_bg_base_dir = 'resources/images/camp_bg/'
        leaves = ["newleaf", "greenleaf", "leafbare", "leaffall"]
        camp_nr = game.clan.camp_bg

        if camp_nr is None:
            camp_nr = 'camp1'
            game.clan.camp_bg = camp_nr

        available_biome = ['Forest', 'Mountainous', 'Plains', 'Beach']
        biome = game.clan.biome
        if biome not in available_biome:
            biome = available_biome[0]
            game.clan.biome = biome
        biome = biome.lower()

        all_backgrounds = []
        for leaf in leaves:

            platform_dir = ""
            if self.the_cat.dead and not self.the_cat.df:
                platform_dir = "resources/images/starclanbg.png"
            elif self.the_cat.dead and self.the_cat.df:
                platform_dir = "resources/images/darkforestbg.png"
            else:
                platform_dir = f'{camp_bg_base_dir}/{biome}/{leaf}_{camp_nr}_{light_dark}.png'
            all_backgrounds.append(platform_dir)

        self.newleaf_bg = pygame.transform.scale(
            pygame.image.load(all_backgrounds[0]).convert(), (screen_x, screen_y))
        self.greenleaf_bg = pygame.transform.scale(
            pygame.image.load(all_backgrounds[1]).convert(), (screen_x, screen_y))
        self.leafbare_bg = pygame.transform.scale(
            pygame.image.load(all_backgrounds[2]).convert(), (screen_x, screen_y))
        self.leaffall_bg = pygame.transform.scale(
            pygame.image.load(all_backgrounds[3]).convert(), (screen_x, screen_y))

    def on_use(self):
        if game.clan.clan_settings['backgrounds']:
            if game.clan.current_season == 'Newleaf':
                screen.blit(self.newleaf_bg, (0, 0))
            elif game.clan.current_season == 'Greenleaf':
                screen.blit(self.greenleaf_bg, (0, 0))
            elif game.clan.current_season == 'Leaf-bare':
                screen.blit(self.leafbare_bg, (0, 0))
            elif game.clan.current_season == 'Leaf-fall':
                screen.blit(self.leaffall_bg, (0, 0))
        now = pygame.time.get_ticks()
        if self.texts:
            if self.texts[self.text_index][0] == "[" and self.texts[self.text_index][-1] == "]":
                self.profile_elements["cat_image"].hide()
                # self.textbox_graphic.show()
            else:
                self.profile_elements["cat_image"].show()
                # self.textbox_graphic.hide()

        if self.text_index < len(self.text_frames):
            if now >= self.next_frame_time and self.frame_index < len(self.text_frames[self.text_index]) - 1:
                self.frame_index += 1
                self.next_frame_time = now + self.typing_delay
        if self.text_index == len(self.text_frames) - 1:
            if self.frame_index == len(self.text_frames[self.text_index]) - 1:
                if self.text_type != "choices":
                    self.paw.visible = True
                if not self.created_choice_buttons and self.text_type == "choices":
                    self.create_choice_buttons()
                    self.created_choice_buttons = True


        # Always render the current frame
        if self.text_frames:
            self.text.html_text = self.text_frames[self.text_index][self.frame_index]

        self.text.rebuild()
        self.clock.tick(60)

    def handle_event(self, event):
        if game.switches['window_open']:
            pass
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.back_button:
                self.change_screen('profile screen')
            else:
                for key, button in self.choice_buttons.items():
                    if event.ui_element == button and self.chosen_text_key:
                        self.current_scene = self.possible_texts[self.chosen_text_key][f"{self.current_scene}_choices"][key]["next_scene"]
                        self.handle_choice(self.the_cat)
        elif event.type == pygame.KEYDOWN and game.settings['keybinds']:
            if event.key == pygame.K_ESCAPE:
                self.change_screen('profile screen')
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.text_frames:
                if self.frame_index == len(self.text_frames[self.text_index]) - 1:
                    if self.text_index < len(self.texts) - 1:
                        self.text_index += 1
                        self.frame_index = 0
                else:
                    self.frame_index = len(self.text_frames[self.text_index]) - 1  # Go to the last frame
            
        return

    def get_cluster_list(self):
        return ["assertive", "brooding", "cool", "upstanding", "introspective", "neurotic", "silly", "stable", "sweet", "unabashed", "unlawful"]

    def get_cluster_list_they(self):
        return ["they_assertive", "they_brooding", "they_cool", "they_upstanding", "they_introspective", "they_neurotic", "they_silly", "they_stable", "they_sweet", "they_unabashed", "they_unlawful"]

    def get_cluster_list_you(self):
        return ["you_assertive", "you_brooding", "you_cool", "you_upstanding", "you_introspective", "you_neurotic", "you_silly", "you_stable", "you_sweet", "you_unabashed", "you_unlawful"]


    def relationship_check(self, talk, cat_relationship):
        relationship_conditions = {
            'hate': 50,
            'romantic_like': 30,
            'platonic_like': 30,
            'jealousy': 30,
            'dislike': 30,
            'comfort': 30,
            'respect': 30,
            'trust': 30
        }
        tags = talk["intro"] if "intro" in talk else talk[0]
        for key, value in relationship_conditions.items():
            if key in tags and cat_relationship < value:
                return True
        return False

    def handle_random_cat(self, cat):
        random_cat = Cat.all_cats.get(choice(game.clan.clan_cats))
        counter = 0
        while random_cat.outside or random_cat.dead or random_cat.ID in [game.clan.your_cat.ID, cat.ID]:
            counter += 1
            if counter == 15:
                break
            random_cat = Cat.all_cats.get(choice(game.clan.clan_cats))
        return random_cat

    def display_intro(self, cat, texts_list, texts_chosen_key):
        chosen_text_intro = texts_list[texts_chosen_key]["intro"]
        chosen_text_intro = self.get_adjusted_txt(chosen_text_intro, cat)
        self.current_scene = "intro"
        self.possible_texts = texts_list
        self.chosen_text_key = texts_chosen_key
        return chosen_text_intro

    def create_choice_buttons(self):


        y_pos = 0
        if f"{self.current_scene}_choices" not in self.possible_texts[self.chosen_text_key]:
            self.paw.visible = True

            return
        for c in self.possible_texts[self.chosen_text_key][f"{self.current_scene}_choices"]:
            text = self.possible_texts[self.chosen_text_key][f"{self.current_scene}_choices"][c]['text']
            text = self.get_adjusted_txt([text], self.the_cat)
            text = text[0]

            #the background image for the text
            option_bg = pygame_gui.elements.UIImage(scale(pygame.Rect((860, 855 + y_pos), (540, 70))),
                                                            pygame.transform.scale(
                                                                image_cache.load_image(
                                                                    "resources/images/option_bg.png").convert_alpha(),
                                                                (540, 60)), manager=MANAGER)
            self.option_bgs[c] = option_bg

            #the button for dialogue choices
            button = UIImageButton(scale(pygame.Rect((780, 855 + y_pos), (68, 68))),
                                        text = "",
                                        object_id="#dialogue_choice_button", manager=MANAGER)
            self.choice_buttons[c] = button


            #the text for dialogue choices
            option = pygame_gui.elements.UITextBox(str(text),
                                                            scale(pygame.Rect((870, 860 + y_pos), (540, 60))),
                                                            object_id="#text_box_30_horizleft",
                                                            manager=MANAGER)
            self.text_choices[c] = option

            y_pos -= 80

    def handle_choice(self, cat):
        for b in self.choice_buttons:
            self.choice_buttons[b].kill()
        for b in self.text_choices:
            self.text_choices[b].kill()
        for b in self.option_bgs:
            self.option_bgs[b].kill()

        self.choice_buttons = {}
        chosen_text = self.possible_texts[self.chosen_text_key][self.current_scene]
        chosen_text2 = self.get_adjusted_txt(chosen_text, cat)
        self.texts = chosen_text2
        self.text_frames = [[text[:i+1] for i in range(len(text))] for text in chosen_text2]
        self.text_index = 0
        self.frame_index = 0
        self.created_choice_buttons = False


    def load_texts(self, cat):
        you = game.clan.your_cat
        resource_dir = "resources/dicts/lifegen_talk/"
        possible_texts = {}

        with open(f"{resource_dir}insults.json", 'r') as read_file:
            possible_texts = ujson.loads(read_file.read())

        return self.filter_texts(cat, possible_texts)


    def filter_texts(self, cat, possible_texts):
        text = ""
        texts_list = {}
        you = game.clan.your_cat

        cluster1, cluster2 = get_cluster(cat.personality.trait)
        cluster3, cluster4 = get_cluster(you.personality.trait)

        their_trait_list = ['adventurous', 'aloof', 'ambitious', 'arrogant', 'bloodthirsty', 'bold', 'bouncy', 'calm', 'careful', 'confident', 'competitive', 'cold', 'charismatic', 'cunning', 'cowardly', 'childish', 'compassionate', 'daring', 'emotional', 'energetic', 'fierce', 'flexible', 'faithful', 'flamboyant', 'grumpy', 'gloomy', 'humble', 'insecure', 'justified', 'loyal', 'lonesome', 'loving', 'meek', 'mellow', 'methodical', 'nervous', 'oblivious', 'obsessive', 'playful', 'reserved', 'righteous', 'responsible', 'rebellious', 'strict', 'stoic', 'sneaky', 'strange', 'sincere', 'shameless', 'spontaneous', 'thoughtful', 'troublesome', 'trusting', 'vengeful', 'witty', 'wise', 'impulsive', 'bullying', 'attention-seeker', 'charming', 'daring', 'noisy', 'daydreamer', 'sweet', 'polite', 'know-it-all', 'bossy', 'disciplined', 'patient', 'manipulative', 'secretive', 'rebellious', 'grumpy', 'passionate', 'honest', 'leader-like', 'smug']
        you_trait_list = ['you_adventurous', 'you_aloof', 'you_ambitious', 'you_arrogant', 'you_bloodthirsty', 'you_bold', 'you_bouncy', 'you_calm', 'you_careful', 'you_confident', 'you_competitive', 'you_cold', 'you_charismatic', 'you_cunning', 'you_cowardly', 'you_childish', 'you_compassionate', 'you_daring', 'you_emotional', 'you_energetic', 'you_fierce', 'you_flexible', 'you_faithful', 'you_flamboyant', 'you_grumpy', 'you_gloomy', 'you_humble', 'you_insecure', 'you_justified', 'you_loyal', 'you_lonesome', 'you_loving', 'you_meek', 'you_mellow', 'you_methodical', 'you_nervous', 'you_oblivious', 'you_obsessive', 'you_playful', 'you_reserved', 'you_righteous', 'you_responsible', 'you_rebellious', 'you_strict', 'you_stoic', 'you_sneaky', 'you_strange', 'you_sincere', 'you_shameless', 'you_spontaneous', 'you_thoughtful', 'you_troublesome', 'you_trusting', 'you_vengeful', 'you_witty', 'you_wise', 'you_impulsive', 'you_bullying', 'you_attention-seeker', 'you_charming', 'you_daring', 'you_noisy', 'you_daydreamer', 'you_sweet', 'you_polite', 'you_know-it-all', 'you_bossy', 'you_disciplined', 'you_patient', 'you_manipulative', 'you_secretive', 'you_rebellious', 'you_passionate', 'you_honest', 'you_leader-like', 'you_smug']
        you_backstory_list = [
            "you_clanfounder",
            "you_clanborn",
            "you_outsiderroots",
            "you_half-Clan",
            "you_formerlyaloner",
            "you_formerlyarogue",
            "you_formerlyakittypet",
            "you_formerlyaoutsider",
            "you_originallyfromanotherclan",
            "you_orphaned",
            "you_abandoned"
        ]
        they_backstory_list = [
            "they_clanfounder",
            "they_clanborn",
            "they_outsiderroots",
            "they_half-Clan",
            "they_formerlyaloner",
            "they_formerlyarogue",
            "they_formerlyakittypet",
            "they_formerlyaoutsider",
            "they_originallyfromanotherclan",
            "they_orphaned",
            "they_abandoned"
        ]
        skill_list = ['teacher', 'hunter', 'fighter', 'runner', 'climber', 'swimmer', 'speaker', 'mediator1', 'clever', 'insightful', 'sense', 'kit', 'story', 'lore', 'camp', 'healer', 'star', 'omen', 'dream', 'clairvoyant', 'prophet', 'ghost', 'explorer', 'tracker', 'artistan', 'guardian', 'tunneler', 'navigator', 'song', 'grace', 'clean', 'innovator', 'comforter', 'matchmaker', 'thinker', 'cooperative', 'scholar', 'time', 'treasure', 'fisher', 'language', 'sleeper']
        you_skill_list = ['you_teacher', 'you_hunter', 'you_fighter', 'you_runner', 'you_climber', 'you_swimmer', 'you_speaker', 'you_mediator1', 'you_clever', 'you_insightful', 'you_sense', 'you_kit', 'you_story', 'you_lore', 'you_camp', 'you_healer', 'you_star', 'you_omen', 'you_dream', 'you_clairvoyant', 'you_prophet', 'you_ghost', 'you_explorer', 'you_tracker', 'you_artistan', 'you_guardian', 'you_tunneler', 'you_navigator', 'you_song', 'you_grace', 'you_clean', 'you_innovator', 'you_comforter', 'you_matchmaker', 'you_thinker', 'you_cooperative', 'you_scholar', 'you_time', 'you_treasure', 'you_fisher', 'you_language', 'you_sleeper']

        for talk_key, talk in possible_texts.items():
            tags = talk["tags"] if "tags" in talk else talk[0]
            for i in range(len(tags)):
                tags[i] = tags[i].lower()

            if "insult" not in tags:
                continue

            if you.moons == 0 and "newborn" not in tags and "you_newborn" not in tags:
                continue

            if cat.moons == 0 and "they_newborn" not in tags:
                continue


            if "deaf" in cat.permanent_condition and "they_deaf" not in tags:
                continue

            if "blind" in cat.permanent_condition and "they_blind" not in tags:
                continue

            if "deaf" in you.permanent_condition and "you_deaf" not in tags:
                continue

            if "blind" in you.permanent_condition and "you_blind" not in tags:
                continue

            # Status tags
            if you.status not in tags and f"you_{you.status}" not in tags and "any" not in tags and "young elder" not in tags and "no_kit" not in tags and "you_any" not in tags:
                continue
            elif "young elder" in tags and cat.status == 'elder' and cat.moons >= 100:
                continue
            elif "no_kit" in tags and (you.status in ['kitten', 'newborn'] or cat.status in ['kitten', 'newborn']):
                continue
            elif "newborn" in tags and "kitten" not in tags and you.moons != 0:
                continue

            if "they_adult" in tags and cat.status in ['apprentice', 'medicine cat apprentice', 'mediator apprentice', "queen's apprentice", "kitten", "newborn"]:
                continue
            if "they_app" in tags and cat.status not in ['apprentice', 'medicine cat apprentice', 'mediator apprentice', "queen's apprentice"]:
                continue
            
            if not any(t in tags for t in ["they_sc", "they_df"]) and cat.dead:
                continue
            if not any(t in tags for t in ["you_sc", "you_df"]) and you.dead:
                continue

            if any(t in tags for t in ["they_sc", "they_df"]) and not cat.dead:
                continue
            if any(t in tags for t in ["you_sc", "you_df"]) and not you.dead:
                continue

            if "you_dftrainee" in tags and not you.joined_df:
                continue

            if "they_dftrainee" in tags and not cat.joined_df:
                continue

            if "you_not_dftrainee" in tags and cat.joined_df:
                continue
                
            if "they_not_dftrainee" in tags and cat.joined_df:
                continue

            if "they_df" in tags and not cat.df:
                continue
            if "you_df" in tags and not you.df:
                continue
            if "they_sc" in tags and cat.df:
                continue
            if "you_sc" in tags and you.df:
                continue

            murdered_them = False
            if you.history:
                if you.history.murder:
                    if "is_murderer" in you.history.murder:
                        for murder_event in you.history.murder["is_murderer"]:
                            if cat.ID == murder_event.get("victim"):
                                murdered_them = True
                                break

            # if murdered_them and "murderedthem" not in tags:
            #     continue

            if "murderedthem" in tags and not murdered_them:
                continue

            murdered_you = False
            if cat.history:
                if cat.history.murder:
                    if "is_murderer" in cat.history.murder:
                        for murder_event in cat.history.murder["is_murderer"]:
                            if you.ID == murder_event.get("victim"):
                                murdered_you = True
                                break

            # if murdered_you and "murderedyou" not in tags:
            #     continue

            if "murderedyou" in tags and not murdered_you:
                continue

            if "grief stricken" in cat.illnesses:
                dead_cat = Cat.all_cats.get(cat.illnesses['grief stricken'].get("grief_cat"))
                if dead_cat:
                    if "grievingyou" in tags:
                        # if not game.clan.your_cat.dead:
                        #     cat.illnesses.remove('grief stricken')
                        if dead_cat.name != game.clan.your_cat.name:
                            continue
                    else:
                        if dead_cat.name == game.clan.your_cat.name:
                            continue

            if "grief stricken" in you.illnesses:
                dead_cat = Cat.all_cats.get(you.illnesses['grief stricken'].get("grief_cat"))
                if dead_cat:
                    if "grievingthem" in tags:
                        if dead_cat.name != cat.name:
                            continue
                    else:
                        if dead_cat.name == cat.name:
                            continue
            
            # FORGIVEN TAGS

            youreforgiven = False
            theyreforgiven = False

            if you.forgiven < 11 and you.forgiven > 0: 
                youreforgiven = True
                                
            if cat.forgiven < 11 and cat.forgiven > 0:
                theyreforgiven = True
            
            if "you_forgiven" in tags and (you.shunned > 0 or not youreforgiven):
                continue

            if "they_forgiven" in tags and (cat.shunned > 0 or not theyreforgiven):
                continue


            roles = ["they_kitten", "they_apprentice", "they_medicine_cat_apprentice", "they_mediator_apprentice", "they_queen's_apprentice", "they_warrior", "they_mediator", "they_medicine_cat", "they_queen", "they_deputy", "they_leader", "they_elder", "they_newborn"]
            if any(r in roles for r in tags):
                has_role = False
                if "they_kitten" in tags and cat.status == "kitten":
                    has_role = True
                elif "they_apprentice" in tags and cat.status == "apprentice":
                    has_role = True
                elif "they_medicine_cat_apprentice" in tags and cat.status == "medicine cat apprentice":
                    has_role = True
                elif "they_mediator_apprentice" in tags and cat.status == "mediator apprentice":
                    has_role = True
                elif "they_queen's_apprentice" in tags and cat.status == "queen's apprentice":
                    has_role = True
                elif "they_warrior" in tags and cat.status == "warrior":
                    has_role = True
                elif "they_mediator" in tags and cat.status == "mediator":
                    has_role = True
                elif "they_medicine_cat" in tags and cat.status == "medicine cat":
                    has_role = True
                elif "they_queen" in tags and cat.status == "queen":
                    has_role = True
                elif "they_deputy" in tags and cat.status == "deputy":
                    has_role = True
                elif "they_leader" in tags and cat.status == "leader":
                    has_role = True
                elif "they_elder" in tags and cat.status == "elder":
                    has_role = True
                elif "they_newborn" in tags and cat.status == "newborn":
                    has_role = True
                if not has_role:
                    continue

            if "they_grieving" not in tags and "grief stricken" in cat.illnesses and not cat.dead:
                continue
            if "they_grieving" in tags and "grief stricken" not in cat.illnesses and not cat.dead:
                continue

            # Cluster tags
            if any(i in self.get_cluster_list() for i in tags) or any(i in self.get_cluster_list_they() for i in tags):
                if cluster1 not in tags and cluster2 not in tags and (("they_"+cluster1) not in tags) and (("they_"+cluster2) not in tags):
                    continue
            if any(i in self.get_cluster_list_you() for i in tags):
                if ("you_"+cluster3) not in tags and ("you_"+cluster4) not in tags:
                    continue

            # Trait tags
            if any(i in you_trait_list for i in tags):
                ts = you_trait_list
                for j in range(len(ts)):
                    ts[j] = ts[j][3:]
                if you.personality.trait not in ts:
                    continue
            if any(i in their_trait_list for i in tags):
                if cat.personality.trait not in tags:
                    continue

            # Backstory tags
            if any(i in you_backstory_list for i in tags):
                ts = you_backstory_list
                for j in range(len(ts)):
                    ts[j] = ts[j][3:]
                if you.backstory not in ts:
                    continue
            if any(i in they_backstory_list for i in tags):
                ts = they_backstory_list
                for j in range(len(ts)):
                    ts[j] = ts[j][4:]
                if cat.backstory not in ts:
                    continue

            # Skill tags
            if any(i in you_skill_list for i in tags):
                ts = you_skill_list
                for j in range(len(ts)):
                    ts[j] = ts[j][3:]
                    ts[j] = ''.join([q for q in ts[j] if not q.isdigit()])
                if (you.skills.primary.path not in ts) or (you.skills.secondary.path not in ts):
                    continue
            if any(i in skill_list for i in tags):
                ts = skill_list
                for j in range(len(ts)):
                    ts[j] = ''.join([q for q in ts[j] if not q.isdigit()])
                if (cat.skills.primary.path not in ts) or (cat.skills.secondary.path not in ts):
                    continue

            # Season tags
            if ('leafbare' in tags and game.clan.current_season != 'Leaf-bare') or ('newleaf' in tags and game.clan.current_season != 'Newleaf') or ('leaffall' in tags and game.clan.current_season != 'Leaf-fall') or ('greenleaf' in tags and game.clan.current_season != 'Greenleaf'):
                continue

            # Biome tags
            if any(i in ['beach', 'forest', 'plains', 'mountainous', 'wetlands', 'desert'] for i in tags):
                if game.clan.biome.lower() not in tags:
                    continue

            # Injuries, grieving and illnesses tags

            if "you_pregnant" in tags and "pregnant" not in you.injuries:
                continue
            if "they_pregnant" in tags and "pregnant" not in cat.injuries:
                continue

            if "grief stricken" not in you.illnesses and "you_grieving" in tags and not you.dead:
                continue

            if "starving" not in you.illnesses and "you_starving" in tags:
                continue
            if "starving" not in cat.illnesses and "they_starving" in tags:
                continue


            if any(i in ["you_ill", "you_injured"] for i in tags):
                ill_injured = False

                if you.is_ill() and "you_ill" in tags and "grief stricken" not in you.illnesses:
                    for illness in you.illnesses:
                        if you.illnesses[illness]['severity'] != 'minor':
                            ill_injured = True
                if you.is_injured() and "you_injured" in tags and "pregnant" not in you.injuries and "recovering from birth" not in you.injuries and "sprain" not in you.injuries:
                    for injury in you.injuries:
                        if you.injuries[injury]['severity'] != 'minor':
                            ill_injured = True

                if not ill_injured:
                    continue

            if any(i in ["they_ill", "they_injured"] for i in tags):
                ill_injured = False

                if cat.is_ill() and "they_ill" in tags and "grief stricken" not in cat.illnesses and "guilty" not in cat.illnesses:
                    for illness in cat.illnesses:
                        if cat.illnesses[illness]['severity'] != 'minor':
                            ill_injured = True
                if cat.is_injured() and "they_injured" in tags and "pregnant" not in cat.injuries and "recovering from birth" not in cat.injuries and "sprain" not in cat.injuries:
                    for injury in cat.injuries:
                        if cat.injuries[injury]['severity'] != 'minor':
                            ill_injured = True

                if not ill_injured:
                    continue


            # Relationships
            # Family tags:
            if any(i in ["from_your_parent", "from_adopted_parent", "adopted_parent", "half sibling", "littermate", "siblings_mate", "cousin", "adopted_sibling", "parents_siblings", "from_mentor", "from_your_kit", "from_your_apprentice", "from_mate", "from_parent", "adopted_parent", "from_kit", "sibling", "from_adopted_kit"] for i in tags):

                fam = False
                if "from_mentor" in tags:
                    if you.mentor == cat.ID:
                        fam = True
                if "from_df_mentor" in tags:
                    if you.df_mentor == cat.ID:
                        fam = True
                if "from_your_apprentice" in tags:
                    if cat.mentor == you.ID:
                        fam = True
                if "from_df_apprentice" in tags:
                    if cat.df_mentor == you.ID:
                        fam = True
                if "from_mate" in tags:
                    if cat.ID in you.mate:
                        fam = True
                if "from_parent" in tags or "from_your_parent" in tags:
                    if you.parent1:
                        if you.parent1 == cat.ID:
                            fam = True
                    if you.parent2:
                        if you.parent2 == cat.ID:
                            fam = True
                if "adopted_parent" in tags or "from adopted_parent" in tags or "from_adopted_parent" in tags:
                    if cat.ID in you.inheritance.get_no_blood_parents():
                        fam = True
                if "from_kit" in tags or "from_your_kit" in tags:
                    if cat.ID in you.inheritance.get_blood_kits():
                        fam = True
                if "from_adopted_kit" in tags:
                    if cat.ID in you.inheritance.get_not_blood_kits():
                        fam = True
                if "littermate" in tags:
                    if cat.ID in you.inheritance.get_siblings() and cat.moons == you.moons:
                        fam = True
                if "sibling" in tags:
                    if cat.ID in you.inheritance.get_siblings():
                        fam = True
                if "half sibling" in tags:
                    c_p1 = cat.parent1
                    if not c_p1:
                        c_p1 = "no_parent1_cat"
                    c_p2 = cat.parent2
                    if not c_p2:
                        c_p2 = "no_parent2_cat"
                    y_p1 = you.parent1
                    if not y_p1:
                        y_p1 = "no_parent1_you"
                    y_p2 = you.parent2
                    if not y_p2:
                        y_p2 = "no_parent2_you"
                    if ((c_p1 == y_p1 or c_p1 == y_p2) or (c_p2 == y_p1 or c_p2 == y_p2)) and not (c_p1 == y_p1 and c_p2 == y_p2) and not (c_p2 == y_p1 and c_p1 == y_p2) and not (c_p1 == y_p2 and c_p2 == y_p1):
                        fam = True
                if "adopted_sibling" in tags:
                    if cat.ID in you.inheritance.get_no_blood_siblings():
                        fam = True
                if "parents_siblings" in tags:
                    if cat.ID in you.inheritance.get_parents_siblings():
                        fam = True
                if "cousin" in tags:
                    if cat.ID in you.inheritance.get_cousins():
                        fam = True
                if "siblings_mate" in tags:
                    if cat.ID in you.inheritance.get_siblings_mates():
                        fam = True
                if not fam:
                    continue


            if "non-related" in tags:
                if you.inheritance.get_exact_rel_type(cat.ID) == RelationType.RELATED:
                    continue
            
            if "they_not_kit" in tags and cat.moons < 6:
                continue

            # If you have murdered someone and have been revealed

            # if "murder" in tags and you.shunned == 1: # "murder" tag is gone, shunned is dealt with elsewhere
            #     if game.clan.your_cat.revealed:
            #         if game.clan.your_cat.history:
            #             if "is_murderer" in game.clan.your_cat.history.murder:
            #                 if len(game.clan.your_cat.history.murder["is_murderer"]) == 0:
            #                     continue
            #                 if 'accomplices' in game.switches:
            #                     if cat.ID in game.switches['accomplices']:
            #                         continue
            #             else:
            #                 continue
            #         else:
            #             continue
            #     else:
            #         continue

            if "war" in tags:
                if game.clan.war.get("at_war", False):
                    continue

            if "non-mates" in tags:
                if you.ID in cat.mate:
                    continue

            if "clan_has_kits" in tags:
                clan_has_kits = False
                for c in Cat.all_cats_list:
                    if c.status == "kitten" and not c.dead and not c.outside:
                        clan_has_kits = True
                if not clan_has_kits:
                    continue

            if "they_older" in tags:
                if you.age == cat.age or cat.moons < you.moons:
                    continue

            if "they_sameage" in tags:
                if you.age != cat.age:
                    continue

            if "they_younger" in tags:
                if you.age == cat.age or cat.moons > you.moons:
                    continue

            if "they_shunned" in tags:
                if cat.shunned == 0:
                    continue

            if "you_shunned" in tags:
                if you.shunned == 0:
                    continue
            
            if "both_shunned" in tags:
                if cat.shunned == 0 or you.shunned == 0:
                    continue

            if cat.shunned > 0 and you.shunned == 0 and "they_shunned" not in tags:
                continue

            if you.shunned > 0 and cat.shunned == 0 and "you_shunned" not in tags:
                continue

            if you.shunned > 0 and cat.shunned > 0 and "both_shunned" not in tags:
                continue

            if "guilty" in tags and "guilt" not in cat.illnesses:
                continue

            # PERMANENT CONDITIONS
            # the exclusive deaf/blind ones

            if "only_they_born_deaf" in tags:
                if "deaf" not in cat.permanent_condition:
                    continue
                if "deaf" in cat.permanent_condition and cat.permanent_condition["deaf"]["born_with"] is False:
                    continue
            if "only_they_went_deaf" in tags:
                if "deaf" not in cat.permanent_condition:
                    continue
                if "deaf" in cat.permanent_condition and cat.permanent_condition["deaf"]["born_with"] is True:
                    continue
            if "only_they_deaf" in tags and "deaf" not in cat.permanent_condition:
                continue

            if "only_they_born_blind" in tags:
                if "blind" not in cat.permanent_condition:
                    continue
                if "blind" in cat.illnesses and cat.permanent_condition["blind"]["born_with"] is False:
                    continue

            if "only_they_went_blind" in tags:
                if "blind" not in cat.permanent_condition:
                    continue
                if "blind" in cat.permanent_condition and cat.permanent_condition["blind"]["born_with"] is True:
                    continue

            if "only_they_blind" in tags and "blind" not in cat.permanent_condition:
                continue

            if "only_you_born_deaf" in tags:
                if "deaf" not in you.permanent_condition:
                    continue
                if "deaf" in you.permanent_condition and you.permanent_condition["deaf"]["born_with"] is False:
                    continue
            if "only_you_went_deaf" in tags:
                if "deaf" not in you.permanent_condition:
                    continue
                if "deaf" in you.permanent_condition and you.permanent_condition["deaf"]["born_with"] is True:
                    continue
            if "only_you_deaf" in tags and "deaf" not in you.permanent_condition:
                continue

            if "only_you_born_blind" in tags:
                if "blind" not in you.permanent_condition:
                    continue
                if "blind" in you.permanent_condition and you.permanent_condition["blind"]["born_with"] is False:
                    continue
            if "only_you_went_blind" in tags:
                if "blind" not in you.permanent_condition:
                    continue
                if "blind" in you.permanent_condition and you.permanent_condition["blind"]["born_with"] is True:
                    continue
            if "only_you_blind" in tags and "blind" not in you.permanent_condition:
                continue

            # non-exclusive deaf/blind
            if "deaf" in cat.permanent_condition:
                if cat.permanent_condition["deaf"]["born_with"] is True:
                    if "they_born_deaf" not in tags and "only_they_born_deaf" not in tags:
                        if "they_deaf" not in tags:
                            continue
                else:
                    if "they_born_deaf" in tags or "only_they_born_deaf" not in tags:
                        if "they_deaf" not in tags:
                            continue
                if "they_hearing" in tags:
                    continue
                # cats who went deaf later in life can get pretty much all normal dialogue, as they're able to talk regularly.
                # they_hearing is for dialogue that explicitly mentions that t_c can hear, so it can be filtered out for cats who went deaf.
                # "did you hear that?" "i just heard..." "r_k is so loud!" yanno

            if "deaf" in you.permanent_condition:
                if you.permanent_condition["deaf"]["born_with"] is True:
                    if "you_born_deaf" not in tags and "only_you_born_deaf" not in tags:
                        if "you_deaf" not in tags and "only_you_deaf" not in tags:
                            continue
                else:
                    if "you_born_deaf" in tags or "only_you_born_deaf" in tags:
                        continue
                    if "you_went_deaf" not in tags and "only_you_went_deaf" not in tags:
                        if "you_deaf" not in tags and "only_you_deaf" not in tags:
                            continue
            
            # blind
            if "blind" in cat.permanent_condition:
                if cat.permanent_condition["blind"]["born_with"] is True:
                    if "they_born_blind" not in tags and "only_they_born_blind" not in tags:
                        if "they_blind" not in tags and "only_they_blind" not in tags:
                            continue
                else:
                    if "they_born_blind" in tags or "only_they_born_blind" in tags:
                        continue
                    if "they_went_blind" not in tags and "only_they_went_blind" not in tags:
                        if "they_blind" not in tags and "only_they_blind" not in tags:
                            continue

            if "blind" in you.permanent_condition:
                if you.permanent_condition["blind"]["born_with"] is True:
                    if "you_born_blind" not in tags and "only_you_born_blind" not in tags:
                        if "you_blind" not in tags and "only_you_blind" not in tags:
                            continue
                else:
                    if "you_born_blind" in tags or "only_you_born_blind" in tags:
                        continue
                    if "you_went_blind" not in tags and "only_you_went_blind" not in tags:
                        if "you_blind" not in tags and "only_you_blind" not in tags:
                            continue


            if "you_allergies" in tags and "allergies" not in you.illnesses:
                continue
            if "they_allergies" in tags and "allergies" not in cat.illnesses:
                continue

            if "you_jointpain" in tags and "constant joint pain" not in you.illnesses:
                continue
            if "they_jointpain" in tags and "constant join pain" not in cat.illnesses:
                continue

            if "you_dizzy" in tags and "constantly dizzy" not in you.illnesses:
                continue
            if "they_dizzy" in tags and "constantly dizzy" not in cat.illnesses:
                continue

            if "you_nightmares" in tags and "constant nightmares" not in you.illnesses:
                continue
            if "they_nightmares" in tags and "constant nightmares" not in cat.illnesses:
                continue

            if "you_crookedjaw" in tags and "crooked jaw" not in you.illnesses:
                continue
            if "they_crookedjaw" in tags and "crooked jaw" not in cat.illnesses:
                continue

            if "you_failingeyesight" in tags and "failing eyesight" not in you.illnesses:
                continue
            if "they_failingeyesight" in tags and "failing eyesight" not in cat.illnesses:
                continue

            if "you_lastinggrief" in tags and "lasting grief" not in you.illnesses:
                continue
            if "they_lastinggrief" in tags and "lasting grief" not in cat.illnesses:
                continue

            # if "you_missingleg" in tags and "lost a leg" not in you.illnesses and "born without a leg" not in you.illnesses:
            #     continue
            # if "they_missingleg" in tags and "lost a leg" not in cat.illnesses and "born without a leg" not in cat.illnesses:
            #     continue

            # if "you_missingtail" in tags and "lost their tail" not in you.illnesses and "born without a tail" not in you.illnesses:
            #     continue
            # if "they_missingtail" in tags and "lost their tail" not in cat.illnesses and "born without a tail" not in cat.illnesses:
            #     continue

            if "you_paralyzed" in tags and "paralyzed" not in you.illnesses:
                continue
            if "they_paralyzed" in tags and "paralyzed" not in cat.illnesses:
                continue

            if "you_hearingloss" in tags and "partial hearing loss" not in you.illnesses:
                continue
            if "they_hearingloss" in tags and "partial hearing loss" not in cat.illnesses:
                continue

            if "you_headaches" in tags and "persistent headaches" not in you.illnesses:
                continue
            if "they_headaches" in tags and "persistent headaches" not in cat.illnesses:
                continue

            if "you_raspylungs" in tags and "raspy lungs" not in you.illnesses:
                continue
            if "they_raspylungs" in tags and "raspy lungs" not in cat.illnesses:
                continue

            if "you_recurringshock" in tags and "recurring shock" not in you.illnesses:
                continue
            if "they_recurringshock" in tags and "recurring shock" not in cat.illnesses:
                continue

            if "you_seizureprone" in tags and "seizure prone" not in you.illnesses:
                continue
            if "they_seizureprone" in tags and "seizure prone" not in cat.illnesses:
                continue

            if "you_wastingdisease" in tags and "wasting disease" not in you.illnesses:
                continue
            if "they_wastingdisease" in tags and "wasting disease" not in cat.illnesses:
                continue

            # Relationship conditions
            if you.ID in cat.relationships:
                if cat.relationships[you.ID].dislike < 30 and 'hate' in tags:
                    continue
                if cat.relationships[you.ID].romantic_love < 15 and 'romantic_like' in tags:
                    continue
                if cat.relationships[you.ID].platonic_like < 15 and 'platonic_like' in tags:
                    continue
                if cat.relationships[you.ID].platonic_like < 40 and 'platonic_love' in tags:
                    continue
                if cat.relationships[you.ID].jealousy < 5 and 'jealousy' in tags:
                    continue
                if cat.relationships[you.ID].dislike < 20 and 'dislike' in tags:
                    continue
                if cat.relationships[you.ID].comfortable < 5 and 'comfort' in tags:
                    continue
                if cat.relationships[you.ID].admiration < 5 and 'respect' in tags:
                    continue
                if cat.relationships[you.ID].trust < 5 and 'trust' in tags:
                    continue
                if (cat.relationships[you.ID].platonic_like > 10 or cat.relationships[you.ID].dislike > 10) and "neutral" in tags:
                    continue
            else:
                if any(i in ["hate","romantic_like","platonic_like","jealousy","dislike","comfort","respect","trust"] for i in tags):
                    continue

            texts_list[talk_key] = talk

        return self.choose_text(cat, texts_list)


    def choose_text(self, cat, texts_list):
        you = game.clan.your_cat
        resource_dir = "resources/dicts/lifegen_talk/"
        if not texts_list:
            cluster1, cluster2 = get_cluster(cat.personality.trait)
            cluster3, cluster4 = get_cluster(you.personality.trait)
            possible_texts = None
            with open(f"{resource_dir}general.json", 'r') as read_file:
                possible_texts = ujson.loads(read_file.read())
                clusters_1 = f"{cluster1} "
                if cluster2:
                    clusters_1 += f"and {cluster2}"
                clusters_2 = f"{cluster3} "
                if cluster4:
                    clusters_2 += f"and {cluster4}"
                try:
                    add_on = ""
                    add_on2 = ""
                    if you.dead and you.df:
                        add_on = " df"
                    elif you.dead and not you.df:
                        add_on = " sc"
                    if "grief stricken" in you.illnesses:
                        add_on += " g"
                    if you.shunned > 0:
                        add_on += " sh"
                    if cat.dead and cat.df:
                        add_on2 = " df"
                    elif cat.dead and not cat.df:
                        add_on2 = " sc"
                    if "grief stricken" in cat.illnesses:
                        add_on2 += " g"
                    if cat.shunned > 0:
                        add_on2 += " sh"
                    try:
                        add_on2 += " " + VERSION_NAME
                    except:
                        print("failed to add on version name")
                    add_on2 += " INSULTING"
                    possible_texts['general'][1][0] = possible_texts['general'][1][0].replace("c_1", clusters_1)
                    possible_texts['general'][1][0] = possible_texts['general'][1][0].replace("c_2", clusters_2)
                    possible_texts['general'][1][0] = possible_texts['general'][1][0].replace("r_1", you.status + add_on)
                    possible_texts['general'][1][0] = possible_texts['general'][1][0].replace("r_2", cat.status + add_on2)
                except Exception as e:
                    print(e)
            texts_list['general'] = possible_texts['general']

        max_retries = 30
        counter = 0
        if len(game.clan.talks) > 50:
            game.clan.talks.clear()

        weights2 = []
        weighted_tags = ["you_pregnant", "they_pregnant", "from_mentor", "from_your_parent", "from_adopted_parent", "adopted_parent", "half sibling", "littermate", "siblings_mate", "cousin", "adopted_sibling", "parents_siblings", "from_mentor", "from_your_kit", "from_your_apprentice", "from_mate", "from_parent", "adopted_parent", "from_kit", "sibling", "from_adopted_kit", "they_injured", "they_ill", "you_injured", "you_ill", "you_grieving", "you_forgiven", "they_forgiven", "murderedyou", "murderedthem"]
        for item in texts_list.values():
            tags = item["tags"] if "tags" in item else item[0]
            num_fam_mentor_tags = 1
            if any(i in weighted_tags for i in tags):
                num_fam_mentor_tags+=3
            weights2.append(num_fam_mentor_tags)

        if "debug_ensure_dialogue" in game.config and game.config["debug_ensure_dialogue"]:
            if game.config["debug_ensure_dialogue"] in list(texts_list.keys()):
                text_chosen_key = game.config["debug_ensure_dialogue"]
                text = texts_list[text_chosen_key]["intro"] if "intro" in texts_list[text_chosen_key] else texts_list[text_chosen_key][1]
                new_text = self.get_adjusted_txt(text, cat)
                if new_text:
                    if "intro" in texts_list[text_chosen_key]:
                        self.text_type = "choices"
                        self.display_intro(cat, texts_list, text_chosen_key)
                    return new_text
            else:
                print("Could not find debug dialogue in possible insults")

        while counter < max_retries:
            text_chosen_key = choices(list(texts_list.keys()), weights=weights2, k=1)[0]
            text = texts_list[text_chosen_key]["intro"] if "intro" in texts_list[text_chosen_key] else texts_list[text_chosen_key][1]
            new_text = self.get_adjusted_txt(text, cat)

            if "intro" in texts_list[text_chosen_key]:
                for choice_key in texts_list[text_chosen_key].keys():
                    choice_text = texts_list[text_chosen_key][choice_key]
                    if isinstance(choice_text, list) and choice_key != "tags":
                        choice_text = self.get_adjusted_txt(choice_text, cat)
                        if not choice_text:
                            new_text = ""
                            break


            if text_chosen_key not in game.clan.talks and new_text:
                game.clan.talks.append(text_chosen_key)
                if "intro" in texts_list[text_chosen_key]:
                    self.text_type = "choices"
                    self.display_intro(cat, texts_list, text_chosen_key)
                return new_text

            counter += 1

        weights = []
        for item in texts_list.values():
            tags = item["tags"] if "tags" in item else item[0]
            weights.append(len(tags))
        text_chosen_key = choices(list(texts_list.keys()), weights=weights, k=1)[0]
        while text_chosen_key not in texts_list.keys():
            text_chosen_key = choices(list(texts_list.keys()), weights=weights, k=1)[0]
        try:
            text = texts_list[text_chosen_key][1]
        except:
            possible_texts = None
            cluster1, cluster2 = get_cluster(cat.personality.trait)
            cluster3, cluster4 = get_cluster(you.personality.trait)
            with open(f"{resource_dir}general.json", 'r') as read_file:
                possible_texts = ujson.loads(read_file.read())
                clusters_1 = f"{cluster1} "
                if cluster2:
                    clusters_1 += f"and {cluster2}"
                clusters_2 = f"{cluster3} "
                if cluster4:
                    clusters_2 += f"and {cluster4}"
                try:
                    possible_texts['general'][1][0].replace("c_1", clusters_1)
                    possible_texts['general'][1][0].replace("c_2", clusters_2)
                    possible_texts['general'][1][0].replace("r_1", game.clan.your_cat.status)
                    possible_texts['general'][1][0].replace("r_2", cat.status)
                except Exception as e:
                    print(e)

            return possible_texts['general'][1]
        new_text = self.get_adjusted_txt(text, cat)
        counter = 0
        while not new_text:
            text_chosen_key = choices(list(texts_list.keys()), weights=weights, k=1)[0]
            text = texts_list[text_chosen_key][1]
            new_text = self.get_adjusted_txt(text, cat)
            counter +=1
            if counter == 30:
                possible_texts = None
                cluster1, cluster2 = get_cluster(cat.personality.trait)
                cluster3, cluster4 = get_cluster(you.personality.trait)
                with open(f"{resource_dir}general.json", 'r') as read_file:
                    possible_texts = ujson.loads(read_file.read())
                    clusters_1 = f"{cluster1} "
                    if cluster2:
                        clusters_1 += f"and {cluster2}"
                    clusters_2 = f"{cluster3} "
                    if cluster4:
                        clusters_2 += f"and {cluster4}"
                    try:
                        possible_texts['general'][1][0].replace("c_1", clusters_1)
                        possible_texts['general'][1][0].replace("c_2", clusters_2)
                        possible_texts['general'][1][0].replace("r_1", game.clan.your_cat.status)
                        possible_texts['general'][1][0].replace("r_2", cat.status)
                    except Exception as e:
                        print(e)

                return possible_texts['general'][1]
        return new_text

    def get_adjusted_txt(self, text, cat):

        you = game.clan.your_cat

        process_text_dict = self.cat_dict.copy()
    
        for abbrev in process_text_dict.keys():
            abbrev_cat = process_text_dict[abbrev]
            process_text_dict[abbrev] = (abbrev_cat, choice(abbrev_cat.pronouns))
        
        process_text_dict["y_c"] = (game.clan.your_cat, choice(game.clan.your_cat.pronouns))
        process_text_dict["t_c"] = (cat, choice(cat.pronouns))
        
        for i in range(len(text)):
            text[i] = re.sub(r"\{(.*?)\}", lambda x: pronoun_repl(x, process_text_dict, False), text[i])

        text = [t1.replace("c_n", game.clan.name) for t1 in text]
        text = [t1.replace("y_c", str(you.name)) for t1 in text]
        text = [t1.replace("t_c", str(cat.name)) for t1 in text]

        for i in range(len(text)):
            text[i] = adjust_txt(Cat, text[i], cat, self.cat_dict, r_c_allowed=True, o_c_allowed=True)
            if text[i] == "":
                return ""
            
        return text

    def get_living_cats(self):
        living_cats = []
        for the_cat in Cat.all_cats_list:
            if not the_cat.dead and not the_cat.outside and not the_cat.moons == -1:
                living_cats.append(the_cat)
        return living_cats