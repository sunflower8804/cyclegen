from typing import Dict

import pygame
import pygame_gui

from scripts.cat.cats import Cat
from scripts.event_class import Single_Event
from scripts.events import events_class
from scripts.game_structure import image_cache
from scripts.game_structure.game_essentials import game
from scripts.game_structure.screen_settings import MANAGER
from scripts.game_structure.ui_elements import (
    UIModifiedScrollingContainer,
    IDImageButton,
    UISurfaceImageButton,
    CatButton,
)
from scripts.game_structure.windows import GameOver
from scripts.screens.Screens import Screens
from scripts.ui.generate_box import BoxStyles, get_box
from scripts.ui.generate_button import get_button_dict, ButtonStyles
from scripts.ui.icon import Icon
from scripts.utility import (
    ui_scale,
    clan_symbol_sprite,
    get_text_box_theme,
    shorten_text_to_fit,
    get_living_clan_cat_count,
    ui_scale_dimensions,
    ui_scale_value,
    ui_scale_offset,
)
 
# LG
from scripts.game_structure.ui_elements import UIImageButton, UIModifiedScrollingContainer, IDImageButton, UISpriteButton
import random
from scripts.game_structure.windows import GameOver, DeathScreen, PickPath


class EventsScreen(Screens):
    current_display = "all events"
    selected_display = "all events"

    all_events = ""
    ceremony_events = ""
    birth_death_events = ""
    relation_events = ""
    health_events = ""
    other_clans_events = ""
    misc_events = ""
    display_text = (
        "<center>See which events are currently happening in the Clan.</center>"
    )
    display_events = []
    tabs = [
        "all events",
        "ceremonies",
        "births & deaths",
        "relationships",
        "health",
        "other clans",
        "miscellaneous",
    ]

    def __init__(self, name):
        super().__init__(name)

        self.events_thread = None
        self.event_screen_container = None
        self.clan_info = {}
        self.timeskip_button = None

        self.full_event_display_container = None
        self.events_frame = None
        self.event_buttons = {}
        self.alert = {}

        self.event_display = None
        self.event_display_containers = []
        self.event_display_boxes = []
        self.cat_profile_buttons = []
        self.involved_cat_container = None
        self.involved_cat_buttons = []

        # LIFEGEN -----------------------
        self.fave_filter_elements = {}
        self.selected_fave_filter = []
        self.you = None
        self.death_button = None

        self.filters_open = False

        # i dont wanna split them into different dicts or anything
        self.all_filters = [
            "yourcat_filter",
            "fave_group_1",
            "fave_group_2",
            "fave_group_3",
            "yourcat_filter_selected",
            "fave_group_1_selected",
            "fave_group_2_selected",
            "fave_group_3_selected"
        ]
        self.selected_filters = ["yourcat_filter_selected", "fave_group_1_selected", "fave_group_2_selected", "fave_group_3_selected"]
        self.unselected_filters = ["yourcat_filter", "fave_group_1", "fave_group_2", "fave_group_3"]

        self.faves_1 = []
        self.faves_2 = []
        self.faves_3 = []
        # -------------------------------

        # Stores the involved cat button that currently has its cat profile buttons open
        self.open_involved_cat_button = None

        self.first_opened = False

    def handle_event(self, event):
        # ON HOVER
        if event.type == pygame_gui.UI_BUTTON_ON_HOVERED:
            element = event.ui_element
            if element in self.event_buttons.values():
                for ele in self.event_buttons:
                    if self.event_buttons[ele] == element:
                        x_pos = int(self.alert[ele].get_relative_rect()[0] - 10)
                        y_pos = self.alert[ele].get_relative_rect()[1]
                        self.alert[ele].set_relative_position((x_pos, y_pos))

        # ON UNHOVER
        elif event.type == pygame_gui.UI_BUTTON_ON_UNHOVERED:
            element = event.ui_element
            if element in self.event_buttons.values():
                for ele in self.event_buttons:
                    if self.event_buttons[ele] == element:
                        x_pos = int(self.alert[ele].get_relative_rect()[0] + 10)
                        y_pos = self.alert[ele].get_relative_rect()[1]
                        self.alert[ele].set_relative_position((x_pos, y_pos))

        # ON START BUTTON PRESS
        elif (
            event.type == pygame_gui.UI_BUTTON_START_PRESS
        ):  # this happens on start press to prevent alert movement
            element = event.ui_element
            if element in self.event_buttons.values():
                for ele, val in self.event_buttons.items():
                    if val == element:
                        self.handle_tab_switch(ele)
                        break

            self.mute_button_pressed(event)

        # ON FULL BUTTON PRESS
        elif (
            event.type == pygame_gui.UI_BUTTON_PRESSED
        ):  # everything else on button press to prevent blinking
            element = event.ui_element
            if element == self.timeskip_button:
                # ensure we can't run the same timeskip multiple times
                if self.events_thread is not None and self.events_thread.is_alive():
                    return
                if game.clan.your_cat.dead_for >= 2 and not game.switches['continue_after_death']:
                    DeathScreen('events screen')
                    return
                elif (game.clan.your_cat.moons == 5
                        and not game.clan.your_cat.outside
                        and not game.clan.your_cat.dead
                        and game.clan.your_cat.status == "kitten"
                        ) or not game.clan.your_cat.status:
                    PickPath('events screen')
                elif game.clan.your_cat.status:
                    self.events_thread = self.loading_screen_start_work(
                        events_class.one_moon
                    )
            elif self.death_button and event.ui_element == self.death_button:
                DeathScreen('events screen')
                return
            elif element == self.you:
                game.switches['cat'] = game.clan.your_cat.ID
                self.change_screen("profile screen")

            elif "cat_icon" in self.fave_filter_elements and element == self.fave_filter_elements["cat_icon"]:
                if self.filters_open is True:
                    self.filters_open = False
                else:
                    self.filters_open = True
                
                self.place_fave_filters()

            elif (
                "yourcat_filter" in self.fave_filter_elements and
                element == self.fave_filter_elements["yourcat_filter"]
                ):
                self.fave_filter_elements["yourcat_filter"].hide()
                self.fave_filter_elements["yourcat_filter_selected"].show()
                self.selected_fave_filter.append("yourcat_filter")
                self.place_fave_filters()
            elif (
                "yourcat_filter_selected" in self.fave_filter_elements and
                element == self.fave_filter_elements["yourcat_filter_selected"]
                ):
                self.fave_filter_elements["yourcat_filter"].show()
                self.fave_filter_elements["yourcat_filter_selected"].hide()
                self.selected_fave_filter.remove("yourcat_filter")
                self.place_fave_filters()

            elif (
                "fave_group_1" in self.fave_filter_elements and
                element == self.fave_filter_elements["fave_group_1"]
                ):
                self.fave_filter_elements["fave_group_1"].hide()
                self.fave_filter_elements["fave_group_1_selected"].show()
                self.selected_fave_filter.append("fave_group_1")
                self.place_fave_filters()
            elif (
                "fave_group_1_selected" in self.fave_filter_elements and
                element == self.fave_filter_elements["fave_group_1_selected"]
                ):
                self.fave_filter_elements["fave_group_1"].show()
                self.fave_filter_elements["fave_group_1_selected"].hide()
                self.selected_fave_filter.remove("fave_group_1")
                self.place_fave_filters()

            elif (
                "fave_group_2" in self.fave_filter_elements and
                element == self.fave_filter_elements["fave_group_2"]
                ):
                self.fave_filter_elements["fave_group_2"].hide()
                self.fave_filter_elements["fave_group_2_selected"].show()
                self.selected_fave_filter.append("fave_group_2")
                self.place_fave_filters()
            elif (
                "fave_group_2_selected" in self.fave_filter_elements and
                element == self.fave_filter_elements["fave_group_2_selected"]
                ):
                self.fave_filter_elements["fave_group_2"].show()
                self.fave_filter_elements["fave_group_2_selected"].hide()
                self.selected_fave_filter.remove("fave_group_2")
                self.place_fave_filters()

            elif (
                "fave_group_3" in self.fave_filter_elements and
                element == self.fave_filter_elements["fave_group_3"]
                ):
                self.fave_filter_elements["fave_group_3"].hide()
                self.fave_filter_elements["fave_group_3_selected"].show()
                self.selected_fave_filter.append("fave_group_3")
                self.place_fave_filters()
            elif (
                "fave_group_3_selected" in self.fave_filter_elements and
                element == self.fave_filter_elements["fave_group_3_selected"]
                ):
                self.fave_filter_elements["fave_group_3"].show()
                self.fave_filter_elements["fave_group_3_selected"].hide()
                self.selected_fave_filter.remove("fave_group_3")
                self.place_fave_filters()

            elif element in self.involved_cat_buttons:
                self.make_cat_buttons(element)
            
            elif element in self.cat_profile_buttons:
                self.save_scroll_position()
                game.switches["cat"] = element.cat_id
                self.change_screen("profile screen")
            else:
                self.save_scroll_position()
                self.menu_button_pressed(event)

        # KEYBIND CONTROLS
        elif game.settings["keybinds"]:
            # ON PRESSING A KEY
            if event.type == pygame.KEYDOWN:
                # LEFT ARROW
                if event.key == pygame.K_LEFT:
                    self.change_screen("patrol screen")
                # RIGHT ARROW
                elif event.key == pygame.K_RIGHT:
                    self.change_screen("camp screen")
                # DOWN AND UP ARROW
                elif event.key == pygame.K_DOWN or event.key == pygame.K_UP:
                    self.handle_tab_select(event.key)
                elif event.key == pygame.K_RETURN:
                    self.handle_tab_switch(self.selected_display)

    def save_scroll_position(self):
        """
        adds current event display vert scroll bar position to game.switches["saved_scroll_positions"] dict
        """
        if self.event_display.vert_scroll_bar:
            game.switches["saved_scroll_positions"][self.current_display] = (
                self.event_display.vert_scroll_bar.scroll_position
                / self.event_display.vert_scroll_bar.scrollable_height
            )

    def handle_tab_select(self, event):
        # find next tab based on current tab
        current_index = self.tabs.index(self.selected_display)
        if event == pygame.K_DOWN:
            next_index = current_index + 1
            wrap_index = 0
        else:
            next_index = current_index - 1
            wrap_index = -1

        # unselect the currently selected display
        # unless it matches the current display, we don't want to mess with the state of that button
        if self.current_display != self.selected_display:
            self.event_buttons[self.selected_display].unselect()
            x_pos = int(self.alert[self.selected_display].get_relative_rect()[0] + 10)
            y_pos = self.alert[self.selected_display].get_relative_rect()[1]
            self.alert[self.selected_display].set_relative_position((x_pos, y_pos))

        # find the new selected display
        try:
            self.selected_display = self.tabs[next_index]
        except IndexError:
            self.selected_display = self.tabs[wrap_index]

        # select the new selected display
        # unless it matches the current display, we don't want to mess with the state of that button
        if self.current_display != self.selected_display:
            self.event_buttons[self.selected_display].select()
            x_pos = int(self.alert[self.selected_display].get_relative_rect()[0] - 10)
            y_pos = self.alert[self.selected_display].get_relative_rect()[1]
            self.alert[self.selected_display].set_relative_position((x_pos, y_pos))

    def handle_tab_switch(self, display_type, is_rescale=False):
        """
        saves current tab scroll position, removes alert, and then switches to the new tab
        """
        if not is_rescale:
            self.save_scroll_position()

        self.current_display = display_type
        self.update_list_buttons()

        if display_type == "all events":
            self.display_events = self.all_events
        elif display_type == "ceremonies":
            self.display_events = self.ceremony_events
        elif display_type == "births & deaths":
            self.display_events = self.birth_death_events
        elif display_type == "relationships":
            self.display_events = self.relation_events
        elif display_type == "health":
            self.display_events = self.health_events
        elif display_type == "other clans":
            self.display_events = self.other_clans_events
        elif display_type == "miscellaneous":
            self.display_events = self.misc_events

        self.alert[display_type].hide()

        self.place_fave_filters()
        self.update_events_display()

    def screen_switches(self):
        super().screen_switches()
        # On first open, update display events list
        self.show_mute_buttons()
        if not self.first_opened:
            self.first_opened = True
            self.update_display_events_lists()
            self.display_events = self.all_events

        self.event_screen_container = pygame_gui.core.UIContainer(
            ui_scale(pygame.Rect((0, 0), (800, 700))),
            starting_height=1,
            manager=MANAGER,
        )

        self.clan_info["symbol"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((137, 105), (100, 100))),
            pygame.transform.scale(
                clan_symbol_sprite(game.clan), ui_scale_dimensions((100, 100))
            ),
            object_id=f"clan_symbol",
            starting_height=1,
            container=self.event_screen_container,
            manager=MANAGER,
        )

        self.clan_info["heading"] = pygame_gui.elements.UITextBox(
            "",
            ui_scale(pygame.Rect((272, 112), (250, -1))),
            object_id=get_text_box_theme("#text_box_30_horizcenter"),
            starting_height=1,
            container=self.event_screen_container,
            manager=MANAGER,
        )

        self.clan_info["season"] = pygame_gui.elements.UITextBox(
            "",
            ui_scale(pygame.Rect((252, 172), (290, -1))),
            object_id=get_text_box_theme("#text_box_30_horizcenter"),
            starting_height=1,
            container=self.event_screen_container,
            manager=MANAGER,
        )
        self.clan_info["age"] = pygame_gui.elements.UITextBox(
            "",
            ui_scale(pygame.Rect((252, 142), (290, -1))),
            object_id=get_text_box_theme("#text_box_30_horizcenter"),
            starting_height=1,
            container=self.event_screen_container,
            manager=MANAGER,
        )

        # Set text for Clan age
        if game.clan.age == 1:
            self.clan_info["age"].set_text(f"Clan age: {game.clan.age} moon")
        if game.clan.age != 1:
            self.clan_info["age"].set_text(f"Clan age: {game.clan.age} moons")

        self.timeskip_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((310, 218), (180, 30))),
            "Timeskip One Moon",
            get_button_dict(ButtonStyles.SQUOVAL, (180, 30)),
            object_id="@buttonstyles_squoval",
            starting_height=1,
            container=self.event_screen_container,
            manager=MANAGER,
            sound_id="timeskip",
        )

        height = 32
        
        self.fave_filter_elements["cat_icon"] = UIImageButton(
            ui_scale(pygame.Rect((30, 287), (25, 25))),
            "",
            object_id="#faves_dropdown",
            container=self.event_screen_container,
            manager=MANAGER,
            )

        self.fave_filter_elements["yourcat_filter"] = UIImageButton(
            ui_scale(pygame.Rect((30, 287 - height), (25, height))),
            "",
            object_id="#yourcat_filter",
            manager=MANAGER,
            container=self.event_screen_container
            )
        self.fave_filter_elements["fave_group_1"] = UIImageButton(
            ui_scale(pygame.Rect((30, 287 + height - 5), (25, height))),
            "", # dont ask me whats going on with the math here ^^ idfk
            object_id="#fave_filter_1",
            manager=MANAGER,
            container=self.event_screen_container
            )
        self.fave_filter_elements["fave_group_2"] = UIImageButton(
            ui_scale(pygame.Rect((30, 287 + height * 2 - 5), (25, height))),
            "",
            object_id="#fave_filter_2",
            manager=MANAGER,
            container=self.event_screen_container
            )
        self.fave_filter_elements["fave_group_3"] = UIImageButton(
            ui_scale(pygame.Rect((30, 287 + height * 3 - 5), (25, height))),
            "",
            object_id="#fave_filter_3",
            manager=MANAGER,
            container=self.event_screen_container
            )
        self.fave_filter_elements["yourcat_filter_selected"] = UIImageButton(
            ui_scale(pygame.Rect((30, 287 - height), (25, height))),
            "",
            object_id="#yourcat_filter_selected",
            manager=MANAGER,
            container=self.event_screen_container
            )
        self.fave_filter_elements["fave_group_1_selected"] = UIImageButton(
            ui_scale(pygame.Rect((30, 287 + height - 5), (25, height))),
            "",
            object_id="#fave_filter_1_selected",
            manager=MANAGER,
            container=self.event_screen_container
            )
        self.fave_filter_elements["fave_group_2_selected"] = UIImageButton(
            ui_scale(pygame.Rect((30, 287 + height * 2 - 5), (25, height))),
            "",
            object_id="#fave_filter_2_selected",
            manager=MANAGER,
            container=self.event_screen_container
            )
        self.fave_filter_elements["fave_group_3_selected"] = UIImageButton(
            ui_scale(pygame.Rect((30, 287 + height * 3 - 5), (25, height))),
            "",
            object_id="#fave_filter_3_selected",
            manager=MANAGER,
            container=self.event_screen_container
            )
        

        # lifegen continue after death button
        self.death_button = UIImageButton(
            ui_scale(pygame.Rect((500, 218), (34, 34))),
            "",
            object_id="#warrior",
            tool_tip_text="Revive",
            manager=MANAGER
        )
        self.death_button.hide()

        if game.switches['continue_after_death']:
            self.death_button.show()

        self.full_event_display_container = pygame_gui.core.UIContainer(
            ui_scale(pygame.Rect((45, 266), (700, 700))),
            starting_height=1,
            container=self.event_screen_container,
            manager=MANAGER,
        )
        self.events_frame = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((161, 0), (534, 370))),
            get_box(BoxStyles.FRAME, (534, 370)),
            starting_height=8,
            container=self.full_event_display_container,
            manager=MANAGER,
        )

        y_pos = 0
        for event_type in self.tabs:
            self.event_buttons[f"{event_type}"] = UISurfaceImageButton(
                ui_scale(pygame.Rect((16, 19 + y_pos), (150, 30))),
                event_type,
                get_button_dict(ButtonStyles.VERTICAL_TAB, (150, 30)),
                object_id="@buttonstyles_vertical_tab",
                starting_height=1,
                container=self.full_event_display_container,
                manager=MANAGER,
                anchors={"right_target": self.events_frame},
            )

            if event_type:
                self.alert[f"{event_type}"] = pygame_gui.elements.UIImage(
                    ui_scale(pygame.Rect((10, 24 + y_pos), (4, 22))),
                    pygame.transform.scale(
                        image_cache.load_image("resources/images/alert_mark.png"),
                        ui_scale_dimensions((4, 22)),
                    ),
                    container=self.full_event_display_container,
                    object_id=f"alert_mark_{event_type.replace(' ', '_')}",
                    manager=MANAGER,
                    visible=False,
                )

            y_pos += 50

        self.place_fave_filters()
        self.event_buttons[self.current_display].disable()

        self.make_event_scrolling_container()
        self.open_involved_cat_button = None
        self.update_events_display()

        # Draw and disable the correct menu buttons.
        self.set_disabled_menu_buttons(["events_screen"])
        self.update_heading_text(f"{game.clan.name}Clan")
        self.show_menu_buttons()

    def display_change_save(self) -> Dict:
        self.save_scroll_position()
        variable_dict = super().display_change_save()

        variable_dict["current_display"] = self.current_display

        return variable_dict

    def display_change_load(self, variable_dict: Dict):
        super().display_change_load(variable_dict)

        for key, value in variable_dict.items():
            try:
                setattr(self, key, value)
            except KeyError:
                continue

        self.handle_tab_switch(self.current_display, is_rescale=True)
        MANAGER.update(1)

        if game.switches["saved_scroll_positions"].get(self.current_display):
            self.event_display.vert_scroll_bar.set_scroll_from_start_percentage(
                game.switches["saved_scroll_positions"][self.current_display]
            )

    def make_event_scrolling_container(self):
        """
        kills and recreates the self.event_display container
        """
        if self.event_display:
            self.event_display.kill()

        rect = pygame.Rect(
            ui_scale_offset((211, 275)),
            (
                self.events_frame.rect[2] + ui_scale_value(13),
                self.events_frame.rect[3] - ui_scale_value(19),
            ),
        )
        self.event_display = UIModifiedScrollingContainer(
            rect,
            starting_height=1,
            manager=MANAGER,
            allow_scroll_y=True,
        )
        self.events_frame.join_focus_sets(self.event_display)

    def make_cat_buttons(self, button_pressed):
        """Makes the buttons that take you to the profile."""

        # How much to increase the panel box size by in order to fit the catbuttons
        size_increase = 26

        # determine whether we need a scrollbar
        scrollbar_needed = len(button_pressed.ids) > 2

        # Check if the button you pressed doesn't have its cat profile buttons currently displayed.
        # if it does, clear the cat profile buttons
        if self.open_involved_cat_button == button_pressed:
            self.open_involved_cat_button = None
            if len(self.cat_profile_buttons) > 2:
                button_pressed.parent_element.set_dimensions(
                    (
                        button_pressed.parent_element.get_relative_rect()[2],
                        button_pressed.parent_element.get_relative_rect()[3]
                        - ui_scale_value(size_increase),
                    ),
                )
            for ele in self.cat_profile_buttons:
                ele.kill()
            self.cat_profile_buttons = []
            return
        # now check if the involved cat display is already open somewhere
        # if so, shrink that back to original size
        elif (
            self.open_involved_cat_button is not None
            and len(self.cat_profile_buttons) > 2
        ):
            self.open_involved_cat_button.parent_element.set_dimensions(
                (
                    self.open_involved_cat_button.parent_element.get_relative_rect()[2],
                    self.open_involved_cat_button.parent_element.get_relative_rect()[3]
                    - ui_scale_value(size_increase),
                ),
            )

        # If it doesn't have its buttons displayed, set the current open involved_cat_button to the pressed button,
        # clear all other buttons, and open the cat profile buttons.
        self.open_involved_cat_button = button_pressed
        if self.involved_cat_container:
            self.involved_cat_container.kill()
        for ele in self.cat_profile_buttons:
            ele.kill()
        self.cat_profile_buttons = []

        container = button_pressed.parent_element

        # if a scrollbar is required, update the container to be bigge enough
        if scrollbar_needed:
            container.set_dimensions(
                (
                    container.relative_rect[2],
                    container.relative_rect[3] + ui_scale_value(size_increase),
                )
            )

        involved_cat_rect = ui_scale(
            pygame.Rect((0, 0), (455, 56 if scrollbar_needed else 36))
        )
        involved_cat_rect.topleft = (
            ui_scale_value(5),
            -button_pressed.get_relative_rect()[3],
        )

        self.involved_cat_container = UIModifiedScrollingContainer(
            involved_cat_rect,
            container=container,
            manager=MANAGER,
            starting_height=3,
            allow_scroll_x=True,
            allow_scroll_y=False,
            should_grow_automatically=scrollbar_needed,  # true if we need a scrollbar, false otherwise
            anchors={"top_target": button_pressed},
        )
        del involved_cat_rect

        # make the cat profiles
        if scrollbar_needed:
            anchor = {"left": "left"}
            for i, cat_id in enumerate(button_pressed.ids):
                rect = ui_scale(pygame.Rect((0 if i == 0 else 5, 0), (120, 34)))
                cat_ob = Cat.fetch_cat(cat_id)
                if cat_ob:
                    # Shorten name if needed
                    name = str(cat_ob.name)
                    short_name = shorten_text_to_fit(name, 80, 13, "clangen")

                    cat_profile_button = CatButton(
                        rect,
                        text=short_name,
                        cat_id=cat_id,
                        container=self.involved_cat_container,
                        object_id="#events_cat_profile_button",
                        starting_height=1,
                        manager=MANAGER,
                        anchors=anchor
                    )
                    self.cat_profile_buttons.append(cat_profile_button)
                anchor = { "left_target": cat_profile_button }
        else:
            anchor = {"right": "right"}
            rect = ui_scale(pygame.Rect((0, 0), (120, 34)))
            for i, cat_id in enumerate(reversed(button_pressed.ids)):
                rect.topright = ui_scale_offset((0 if i == 0 else -125, 0))
                cat_ob = Cat.fetch_cat(cat_id)
                if cat_ob:
                    # Shorten name if needed
                    name = str(cat_ob.name)
                    short_name = shorten_text_to_fit(name, 80, 13, "clangen")

                    cat_profile_button = CatButton(
                        rect,
                        text=short_name,
                        cat_id=cat_id,
                        container=self.involved_cat_container,
                        object_id="#events_cat_profile_button",
                        starting_height=1,
                        manager=MANAGER,
                        anchors=anchor,
                    )
                    self.cat_profile_buttons.append(cat_profile_button)
                anchor = { "left_target": cat_profile_button }
        del rect
        self.involved_cat_container.set_view_container_dimensions(
            (
                self.involved_cat_container.get_relative_rect()[2],
                self.event_display.get_relative_rect()[3],
            )
        )

    def exit_screen(self):
        self.event_display.kill()  # event display isn't put in the screen container due to lag issues
        self.event_screen_container.kill()
        if self.you:
            self.you.kill()
        
        if self.death_button:
            self.death_button.kill()

        for ele in self.fave_filter_elements:
            self.fave_filter_elements[ele].kill()
        self.fave_filter_elements = {}

    def place_fave_filters(self):
        for ele in self.fave_filter_elements:
            self.fave_filter_elements[ele].kill()
        self.fave_filter_elements = {}

        # fave filters
        height = 32
        
        self.fave_filter_elements["cat_icon"] = UIImageButton(
            ui_scale(pygame.Rect((30, 287), (25, 25))),
            "",
            object_id="#faves_dropdown",
            container=self.event_screen_container,
            manager=MANAGER,
            )

        self.fave_filter_elements["yourcat_filter"] = UIImageButton(
            ui_scale(pygame.Rect((30, 287 - height), (25, height))),
            "",
            object_id="#yourcat_filter",
            manager=MANAGER,
            container=self.event_screen_container
            )
        self.fave_filter_elements["fave_group_1"] = UIImageButton(
            ui_scale(pygame.Rect((30, 287 + height - 5), (25, height))),
            "",
            object_id="#fave_filter_1",
            manager=MANAGER,
            container=self.event_screen_container
            )
        self.fave_filter_elements["fave_group_2"] = UIImageButton(
            ui_scale(pygame.Rect((30, 287 + height * 2 - 5), (25, height))),
            "",
            object_id="#fave_filter_2",
            manager=MANAGER,
            container=self.event_screen_container
            )
        self.fave_filter_elements["fave_group_3"] = UIImageButton(
            ui_scale(pygame.Rect((30, 287 + height * 3 - 5), (25, height))),
            "",
            object_id="#fave_filter_3",
            manager=MANAGER,
            container=self.event_screen_container
            )
        self.fave_filter_elements["yourcat_filter_selected"] = UIImageButton(
            ui_scale(pygame.Rect((30, 287 - height), (25, height))),
            "",
            object_id="#yourcat_filter_selected",
            manager=MANAGER,
            container=self.event_screen_container
            )
        self.fave_filter_elements["fave_group_1_selected"] = UIImageButton(
            ui_scale(pygame.Rect((30, 287 + height - 5), (25, height))),
            "",
            object_id="#fave_filter_1_selected",
            manager=MANAGER,
            container=self.event_screen_container
            )
        self.fave_filter_elements["fave_group_2_selected"] = UIImageButton(
            ui_scale(pygame.Rect((30, 287 + height * 2 - 5), (25, height))),
            "",
            object_id="#fave_filter_2_selected",
            manager=MANAGER,
            container=self.event_screen_container
            )
        self.fave_filter_elements["fave_group_3_selected"] = UIImageButton(
            ui_scale(pygame.Rect((30, 287 + height * 3 - 5), (25, height))),
            "",
            object_id="#fave_filter_3_selected",
            manager=MANAGER,
            container=self.event_screen_container
            )

        if "yourcat_filter" not in self.selected_fave_filter:
            self.fave_filter_elements["yourcat_filter"].show()
            self.fave_filter_elements["yourcat_filter_selected"].hide()
        else:
            self.fave_filter_elements["yourcat_filter"].hide()
            self.fave_filter_elements["yourcat_filter_selected"].show()
        
        if "fave_group_1" not in self.selected_fave_filter:
            self.fave_filter_elements["fave_group_1"].show()
            self.fave_filter_elements["fave_group_1_selected"].hide()
        else:
            self.fave_filter_elements["fave_group_1"].hide()
            self.fave_filter_elements["fave_group_1_selected"].show()
        
        if "fave_group_2" not in self.selected_fave_filter:
            self.fave_filter_elements["fave_group_2"].show()
            self.fave_filter_elements["fave_group_2_selected"].hide()
        else:
            self.fave_filter_elements["fave_group_2"].hide()
            self.fave_filter_elements["fave_group_2_selected"].show()
        
        if "fave_group_3" not in self.selected_fave_filter:
            self.fave_filter_elements["fave_group_3"].show()
            self.fave_filter_elements["fave_group_3_selected"].hide()
        else:
            self.fave_filter_elements["fave_group_3"].hide()
            self.fave_filter_elements["fave_group_3_selected"].show()

        if self.filters_open is False:
            for item in self.fave_filter_elements:
                if item == "cat_icon":
                    continue
                self.fave_filter_elements[item].hide()

        if self.current_display == "all events":
            self.fave_filter_elements["cat_icon"].show()
        else:
            for btn in self.fave_filter_elements:
                self.fave_filter_elements[btn].hide()

        self.update_display_events_lists()
        self.update_events_display()

    def update_display_events_lists(self):
        """
        Categorize events from game.cur_events_list into display categories for screen
        """

        self.all_events = [
            x for x in game.cur_events_list if "interaction" not in x.types
        ]

         # LIFEGEN: changing all events based on fave filters
        if self.selected_fave_filter:
            fnumlist = []
            for item in self.selected_fave_filter:
                if "yourcat" in item:
                    continue
                num = item.split("_")[2]
                fnumlist.append(int(num))

            fav_cats = []
            fav_events = []

            for kitty in Cat.all_cats_list:
                for num in fnumlist:
                    if kitty.favourite == num:
                        fav_cats.append(kitty)
                if kitty.ID == game.clan.your_cat.ID:
                    if "yourcat_filter" in self.selected_fave_filter and kitty not in fav_cats:
                        fav_cats.append(kitty)

            for kitty in fav_cats:
                for ev in self.all_events + self.relation_events:
                    if kitty.ID in ev.cats_involved:
                        fav_events.append(ev)

            self.all_events = [
                x for x in fav_events
            ]

        self.event_display_type = self.current_display

        # ----------------------------------------------------------------

        self.ceremony_events = [
            x for x in game.cur_events_list if "ceremony" in x.types
        ]
        self.birth_death_events = [
            x for x in game.cur_events_list if "birth_death" in x.types
        ]
        self.relation_events = [
            x for x in game.cur_events_list if "relation" in x.types
        ]
        self.health_events = [x for x in game.cur_events_list if "health" in x.types]
        self.other_clans_events = [
            x for x in game.cur_events_list if "other_clans" in x.types
        ]
        self.misc_events = [x for x in game.cur_events_list if "misc" in x.types]

    def update_events_display(self):
        """
        Kills and recreates the event display, updates the clan info, sets the event display scroll position if it was
        previously saved
        """

        if not game.clan.your_cat:
            print(
                "Are you playing a normal ClanGen save? Switch to a LifeGen save or create a new cat!")
            print("Choosing random cat to play...")
            game.clan.your_cat = Cat.all_cats[random.choice(game.clan.clan_cats)]
            print("Chose " + str(game.clan.your_cat.name))
        # UPDATE CLAN INFO
        # self.clan_info["season"].set_text(f"Current season: {game.clan.current_season}")
        self.clan_info["heading"].set_text(str(game.clan.your_cat.name))
        self.clan_info["season"].set_text(f'Season: {game.clan.current_season} - Clan Age: {game.clan.age}')
        if game.clan.your_cat.moons == -1:
            self.clan_info["age"].set_text('Your age: Unborn')
        elif game.clan.your_cat.moons != 1:
            self.clan_info["age"].set_text(f'Your age: {game.clan.your_cat.moons} moons')
        elif game.clan.your_cat.moons == 1:
            self.clan_info["age"].set_text(f'Your age: {game.clan.your_cat.moons} moon')

        self.make_event_scrolling_container()

        for ele in self.event_display_containers:
            ele.kill()
        self.event_display_containers = []

        for ele in self.event_display_boxes:
            ele.kill()
        self.event_display_boxes = []

        for ele in self.cat_profile_buttons:
            ele.kill()
        self.cat_profile_buttons = []

        for ele in self.involved_cat_buttons:
            ele.kill()
        self.involved_cat_buttons = []

        # Stop if Clan is new, so that events from previously loaded Clan don't show up
        if game.clan.age == 0:
            return
        
        # LIFEGEN: This has to be here to update fave filtered events
        if self.current_display == "all events":
            self.display_events = self.all_events
        # -----------------------------------------------------------

        default_rect = pygame.Rect(
            ui_scale_offset((5, 0)),
            (
                self.event_display.get_relative_rect()[2]
                - ui_scale_value(10)
                - self.event_display.scroll_bar_width,
                ui_scale_value(300),
            ),
        )

        catbutton_rect = ui_scale(pygame.Rect((0, 0), (34, 34)))
        catbutton_rect.topright = ui_scale_offset((-10, 5))

        anchor = {"top": "top"}

        alternate_color = (pygame.Color(87, 76, 55)
                    if game.settings["dark mode"]
                    else pygame.Color(167, 148, 111))

        for i, event_object in enumerate(self.display_events):
            if not isinstance(event_object.text, str):
                print(
                    f"Incorrectly Formatted Event: {event_object.text}, {type(event_object)}"
                )
                self.display_events.remove(event_object)
                continue

            display_element_container = pygame_gui.elements.UIPanel(
                default_rect,
                5,
                MANAGER,
                container=self.event_display,
                element_id="event_panel",
                object_id="#dark" if game.settings["dark mode"] else None,
                margins={"top": 0, "bottom": 0, "left": 0, "right": 0},
                anchors=anchor,
            )

            self.event_display_containers.append(display_element_container)

            if i % 2 == 0:
                display_element_container.background_colour = alternate_color
                display_element_container.rebuild()

            # TEXT BOX
            display_element_event = pygame_gui.elements.UITextBox(
                event_object.text,
                ui_scale(pygame.Rect((0, 0), (509, -1))),
                object_id=get_text_box_theme("#text_box_30_horizleft"),
                starting_height=1,
                container=display_element_container,
                manager=MANAGER,
                anchors={"left": "left", "right": "right"},
            )

            self.event_display_boxes.append(display_element_event)

            if event_object.cats_involved:
                involved_cat_button = IDImageButton(
                    catbutton_rect,
                    Icon.CAT_HEAD,
                    get_button_dict(ButtonStyles.ICON, (34, 34)),
                    ids=event_object.cats_involved,
                    layer_starting_height=3,
                    object_id="@buttonstyles_icon",
                    parent_element=display_element_container,
                    container=display_element_container,
                    manager=MANAGER,
                    anchors={
                        "right": "right",
                        "top_target": display_element_event,
                    },
                )
                self.involved_cat_buttons.append(involved_cat_button)

            display_element_container.set_dimensions(
                (
                    default_rect[2],
                    (
                        display_element_event.get_relative_rect()[3]
                        + (
                            involved_cat_button.get_relative_rect()[3]
                            + ui_scale_value(10)
                        )
                        if event_object.cats_involved
                        else display_element_event.get_relative_rect()[3]
                    ),
                )
            )

            anchor = {"top_target": display_element_container}

        del catbutton_rect

        # this HAS TO UPDATE before saved scroll position can be set
        self.event_display.scrollable_container.update(1)

        # don't ask me why we have to redefine these dimensions, we just do
        # otherwise the scroll position save will break
        self.event_display.set_dimensions(
            (
                self.event_display.get_relative_rect()[2],
                self.event_display.get_relative_rect()[3],
            )
        )

        # set saved scroll position
        if game.switches["saved_scroll_positions"].get(self.current_display):
            self.event_display.vert_scroll_bar.set_scroll_from_start_percentage(
                game.switches["saved_scroll_positions"][self.current_display]
            )

        if self.you:
            self.you.kill()
        if game.clan.your_cat.moons != -1:
            self.you = UISpriteButton(
                ui_scale(pygame.Rect((570, 100), (120, 120))),
                game.clan.your_cat.sprite,
                cat_id=game.clan.your_cat.ID,
                manager=MANAGER
                )
        if game.switches['continue_after_death'] and game.clan.your_cat.moons >= 0:
            self.death_button.show()
        else:
            self.death_button.hide()

    def update_list_buttons(self):
        """
        re-enable all event tab buttons, then disable the currently selected tab
        """
        for ele in self.event_buttons:
            self.event_buttons[ele].enable()

        self.event_buttons[self.current_display].disable()

    def on_use(self):
        super().on_use()
        self.loading_screen_on_use(self.events_thread, self.timeskip_done)

    def timeskip_done(self):
        """Various sorting and other tasks that must be done with the timeskip is over."""

        game.switches["saved_scroll_positions"] = {}

        if get_living_clan_cat_count(Cat) == 0:
            GameOver("events screen")

        self.update_display_events_lists()

        self.current_display = "all events"
        self.event_buttons["all events"].disable()

        for tab in self.event_buttons:
            if tab != "all events":
                self.event_buttons[tab].enable()

        if not self.all_events:
            self.all_events.append(
                Single_Event("Nothing interesting happened this moon.")
            )

        self.display_events = self.all_events

        if self.ceremony_events:
            self.alert["ceremonies"].show()
        else:
            self.alert["ceremonies"].hide()

        if self.birth_death_events:
            self.alert["births & deaths"].show()
        else:
            self.alert["births & deaths"].hide()

        if self.relation_events:
            self.alert["relationships"].show()
        else:
            self.alert["relationships"].hide()

        if self.health_events:
            self.alert["health"].show()
        else:
            self.alert["health"].hide()

        if self.other_clans_events:
            self.alert["other clans"].show()
        else:
            self.alert["other clans"].hide()

        if self.misc_events:
            self.alert["miscellaneous"].show()
        else:
            self.alert["miscellaneous"].hide()

        # resets the alerts' x position to make sure they don't shift places over multiple moons.
        for item in self.alert.values():
            item.set_relative_position((10, item.get_relative_rect()[1]))

        
        self.update_events_display()
        self.timeskip_button.enable()
