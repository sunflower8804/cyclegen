#!/usr/bin/env python3
# -*- coding: ascii -*-
import random
import re
from os.path import exists as path_exists
from random import choice, choices, gauss
from typing import List, Dict, Union, TYPE_CHECKING, Optional, Tuple

import pygame

from scripts.events_module.short.handle_short_events import INJURY_GROUPS

if TYPE_CHECKING:
    from scripts.events_module.patrol.patrol import Patrol

from scripts.cat.history import History
from scripts.clan import HERBS
from scripts.utility import (
    change_clan_relations,
    change_clan_reputation,
    change_relationship_values,
    create_new_cat,
    unpack_rel_block,
    event_text_adjust,
    gather_cat_objects,
    adjust_txt,
    create_new_cat_block
)
from scripts.game_structure.game_essentials import game
from scripts.cat.skills import SkillPath
from scripts.cat.cats import Cat, ILLNESSES, INJURIES, PERMANENT, BACKSTORIES
from scripts.cat.pelts import Pelt
from scripts.cat_relations.relationship import Relationship
from scripts.clan_resources.freshkill import (
    ADDITIONAL_PREY,
    PREY_REQUIREMENT,
    HUNTER_EXP_BONUS,
    HUNTER_BONUS,
    FRESHKILL_ACTIVE,
)


class PatrolOutcome:
    """Holds all info on patrol outcomes, and methods to handle that outcome"""

    def __init__(
        self,
        success: bool = True,
        antagonize: bool = False,
        text: str = None,
        weight: int = 20,
        exp: int = 0,
        stat_trait: List[str] = None,
        stat_skill: List[str] = None,
        can_have_stat: List[str] = None,
        dead_cats: List[str] = None,
        lost_cats: List[str] = None,
        injury: List[Dict] = None,
        murder: List[str] = None,
        convert: List[str] = None,
        faith_effects: List[str] = None,
        accessory: List[Dict] = None,
        history_reg_death: str = None,
        history_leader_death: str = None,
        history_scar: str = None,
        new_cat: List[List[str]] = None,
        herbs: List[str] = None,
        prey: List[str] = None,
        outsider_rep: Union[int, None] = None,
        other_clan_rep: Union[int, None] = None,
        relationship_effects: List[dict] = None,
        relationship_constraints: List[str] = None,
        outcome_art: Union[str, None] = None,
        outcome_art_clean: Union[str, None] = None,
        stat_cat: Cat = None
    ):
        self.success = success
        self.antagonize = antagonize
        self.text = text if text is not None else ""
        self.weight = weight
        self.exp = exp
        self.stat_trait = stat_trait if stat_trait is not None else []
        self.stat_skill = stat_skill if stat_skill is not None else []
        self.can_have_stat = can_have_stat if can_have_stat is not None else []
        self.dead_cats = dead_cats if dead_cats is not None else []
        self.lost_cats = lost_cats if lost_cats is not None else []
        self.injury = injury if injury is not None else []
        self.murder = murder if murder is not None else []
        self.convert = convert if convert is not None else []
        self.faith_effects = faith_effects if faith_effects is not None else []
        self.accessory = accessory if accessory is not None else []
        self.history_reg_death = (
            history_reg_death
            if history_reg_death is not None
            else "m_c died on patrol."
        )
        self.history_leader_death = (
            history_leader_death
            if history_leader_death is not None
            else "died on patrol."
        )
        self.history_scar = (
            history_scar if history_scar is not None else "m_c was scarred on patrol."
        )
        self.new_cat = new_cat if new_cat is not None else []
        self.herbs = herbs if herbs is not None else []
        self.prey = prey if prey is not None else []
        self.outsider_rep = outsider_rep
        self.other_clan_rep = other_clan_rep
        self.relationship_effects = (
            relationship_effects if relationship_effects is not None else []
        )
        self.relationship_constraints = (
            relationship_constraints if relationship_constraints is not None else []
        )
        self.outcome_art = outcome_art
        self.outcome_art_clean = outcome_art_clean

        # This will hold the stat cat, for filtering purposes
        self.stat_cat = stat_cat

    @staticmethod
    def prepare_allowed_outcomes(
        outcomes: List["PatrolOutcome"], patrol: "Patrol"
    ) -> List["PatrolOutcome"]:
        """Takes a list of patrol outcomes, and returns those which are possible. If "special" events, gated
        by stat cats or relationships, are possible, this function returns only those. Stat cats are also determined here.
        """

        # Determine which outcomes are possible
        reg_outcomes = []
        special_outcomes = []
        for out in outcomes:
            # We want to gather special (ie, gated with stat or relationship constaints)
            # outcomes seperatly, so we can ensure that those occur if possible.
            special = False

            if out.stat_skill or out.stat_trait:
                special = True
                out._get_stat_cat(patrol)
                if not isinstance(out.stat_cat, Cat):
                    continue

            # TODO: outcome relationship constraints
            # if not patrol._satify_relationship_constaints(patrol, out.relationship_constaints):
            #    continue
            # elif out.relationship_constaints:
            #    special = True

            if special:
                special_outcomes.append(out)
            else:
                reg_outcomes.append(out)

        # If there are somehow no possible outcomes, add a single default
        # outcome. Patrols should be written so this never has to occur
        if not (special_outcomes or reg_outcomes):
            reg_outcomes.append(
                PatrolOutcome(
                    text="There's nothing here, and that's a problem. Please report! ",
                )
            )

        return special_outcomes if special_outcomes else reg_outcomes

    @staticmethod
    def generate_from_info(
        info: List[dict], success: bool = True, antagonize: bool = False
    ) -> List["PatrolOutcome"]:
        """Factory method generates a list of PatrolOutcome objects based on the dicts"""

        outcome_list = []

        if not isinstance(info, list):
            return outcome_list

        for _d in info:
            outcome_list.append(
                PatrolOutcome(
                    success=success,
                    antagonize=antagonize,
                    text=_d.get("text"),
                    weight=_d.get("weight"),
                    exp=_d.get("exp"),
                    stat_skill=_d.get("stat_skill"),
                    stat_trait=_d.get("stat_trait"),
                    can_have_stat=_d.get("can_have_stat"),
                    dead_cats=_d.get("dead_cats"),
                    injury=_d.get("injury"),
                    murder=_d.get("murder"),
                    convert =_d.get("convert"),
                    faith_effects = _d.get("faith_effects"),
                    accessory=_d.get("accessory"),
                    lost_cats=_d.get("lost_cats"),
                    history_leader_death=(
                        _d["history_text"].get("lead_death")
                        if isinstance(_d.get("history_text"), dict)
                        else None
                    ),
                    history_reg_death=(
                        _d["history_text"].get("reg_death")
                        if isinstance(_d.get("history_text"), dict)
                        else None
                    ),
                    history_scar=(
                        _d["history_text"].get("scar")
                        if isinstance(_d.get("history_text"), dict)
                        else None
                    ),
                    new_cat=_d.get("new_cat"),
                    herbs=_d.get("herbs"),
                    prey=_d.get("prey"),
                    outsider_rep=_d.get("outsider_rep"),
                    other_clan_rep=_d.get("other_clan_rep"),
                    relationship_effects=_d.get("relationships"),
                    relationship_constraints=_d.get("relationship_constraint"),
                    outcome_art=_d.get("art"),
                    outcome_art_clean=_d.get("art_clean"),
                )
            )

        return outcome_list

    def execute_outcome(self, patrol: "Patrol") -> Tuple[str, str, Optional[str]]:
        """
        Excutes the outcome. Returns a tuple with the final outcome text, the results text, and any outcome art
        format: (Outcome text, results text, outcome art (might be None))
        """
        # This must be done before text processing so that the new cat's pronouns are generated first
        results = [self._handle_new_cats(patrol)]

        # lifegen random abbrev processing!
        lifegen_abbrev_text = adjust_txt(Cat, self.text, patrol.patrol_leader, patrol.patrol_cat_dict, r_c_allowed=False, o_c_allowed=False)

        text = lifegen_abbrev_text
        if lifegen_abbrev_text == "":
            print("Lifegen: No abbrevs to adjust")
            text = self.text

        # the text has to be processed before - otherwise leader might be referenced with their warrior name
        processed_text = event_text_adjust(Cat,
                                        text,
                                        patrol_leader=patrol.patrol_leader,
                                        # LIFEGEN ^^ pls don't remove
                                        patrol_cat_dict=patrol.patrol_cat_dict,
                                        random_cat=patrol.random_cat,
                                        stat_cat=self.stat_cat,
                                        patrol_cats=patrol.patrol_cats,
                                        patrol_apprentices=patrol.patrol_apprentices,
                                        new_cats=patrol.new_cats,
                                        clan=game.clan,
                                        other_clan=patrol.other_clan)

        # This order is important.
        results.append(self._handle_death(patrol))
        results.append(self._handle_lost(patrol))
        # LG
        results.append(self._handle_accessories(patrol))
        results.append(self._handle_df_convert(patrol))
        results.append(self._handle_murder(patrol))
        results.append(self._handle_faith_changes(patrol))
        # ---
        results.append(self._handle_condition_and_scars(patrol))

        # pronounify the relationship log
        for block in self.relationship_effects:
            if block.get("log"):
                log = block.get("log") + " "
                if isinstance(log, str):
                    block["log"] = event_text_adjust(
                        Cat,
                        log,
                        patrol_leader=patrol.patrol_leader,
                        random_cat=patrol.random_cat,
                        stat_cat=self.stat_cat,
                        patrol_cats=patrol.patrol_cats,
                        patrol_apprentices=patrol.patrol_apprentices,
                        new_cats=patrol.new_cats,
                        clan=game.clan,
                        other_clan=patrol.other_clan,
                    )
                elif isinstance(log, list):
                    for i in range(1, len(log)):
                        block["log"][i] = event_text_adjust(
                            Cat,
                            block["log"][i] + " ",
                            patrol_leader=patrol.patrol_leader,
                            random_cat=patrol.random_cat,
                            stat_cat=self.stat_cat,
                            patrol_cats=patrol.patrol_cats,
                            patrol_apprentices=patrol.patrol_apprentices,
                            new_cats=patrol.new_cats,
                            clan=game.clan,
                            other_clan=patrol.other_clan,
                        )

        results.append(
            unpack_rel_block(
                Cat, self.relationship_effects, patrol, stat_cat=self.stat_cat
            )
        )
        results.append(self._handle_rep_changes(patrol))
        results.append(self._handle_other_clan_relations(patrol))
        results.append(self._handle_prey(patrol))
        results.append(self._handle_herbs(patrol))
        results.append(self._handle_exp(patrol))
        results.append(self._handle_mentor_app(patrol))

        # Filter out empty results strings
        results = [x for x in results if x]

        print("PATROL END -----------------------------------------------------")

        return processed_text, " ".join(results), self.get_outcome_art()

    def _allowed_stat_cat_specific(
        self, kitty: Cat, patrol: "Patrol", allowed_specific
    ) -> bool:
        """Helper that handled specific stat cat requirements."""

        if "any" in allowed_specific:
            # Special allowed_specific that allows all.
            return True

        # With allowed_specific empty, that means the stat can can be anyone that's not patrol leader
        # or stat cat. This can
        if not allowed_specific or "not_pl_rc" in allowed_specific:
            if kitty in (patrol.patrol_leader, patrol.random_cat):
                return False
            return True

        # Code to allow anyone but p_l to be selected as stat cat
        if not allowed_specific or "not_pl" in allowed_specific:
            if kitty is patrol.patrol_leader:
                return False
            return True

        # Otherwise, check to see if the cat matched any of the specfic cats
        if "p_l" in allowed_specific and kitty == patrol.patrol_leader:
            return True
        if "r_c" in allowed_specific and kitty == patrol.random_cat:
            return True
        if "y_c" in allowed_specific and kitty == game.clan.your_cat:
            return True
        if (
            "app1" in allowed_specific
            and len(patrol.patrol_apprentices) >= 1
            and kitty == patrol.patrol_apprentices[0]
        ):
            return True
        if (
            "app2" in allowed_specific
            and len(patrol.patrol_apprentices) >= 2
            and kitty == patrol.patrol_apprentices[1]
        ):
            return True
        
        for item in patrol.patrol_cat_dict.items():
            abbrev = item[0]
            cat_object = item[1]

            if abbrev in allowed_specific and kitty == cat_object:
                return True


        return False

    def _get_stat_cat(self, patrol: "Patrol"):
        """Sets the stat cat. Returns true if a stat cat was found, and False if a stat cat was not found"""

        print("---")
        print(
            f"Finding stat cat. Outcome Type: Success = {self.success}, Antag = {self.antagonize}"
        )
        print(f"Can Have Stat: {self.can_have_stat}")

        # Grab any specfic stat cat requirements:
        allowed_specific = [
            x
            for x in self.can_have_stat
            if x in ("r_c", "p_l", "app1", "app2", "any", "not_pl_rc", "not_pl")
        ]
        for i in patrol.patrol_cat_dict.items():
            if i[0] in self.can_have_stat:
                allowed_specific.append(i[0])

        # Special default behavior for patrols less than two cats.
        # Patrol leader is the only one allowed to be stat_cat in patrols equal to or less than than two cats

        # LIFEGEN EDIT: only in clangen patrols buster
        if "patrol_category" in game.switches and game.switches["patrol_category"] == "clangen":
            if not allowed_specific and len(patrol.patrol_cats) <= 2:
                allowed_specific = ["p_l"]

            patrolcats = patrol.patrol_cats
        
        else:
            # this is lifegen stuff to add random abbrevs to the list for stat cat possibilities
            # so its not just cats in the patrol
            patrolcats = []
            for kitty in patrol.patrol_cat_dict.items():
                patrolcats.append(kitty[1])

        possible_stat_cats = []
        # for kitty in patrol.patrol_cats: # clangen
        for kitty in patrolcats:
            # First, the blanket requirements
            if "app" in self.can_have_stat and kitty.status not in [
                "apprentice",
                "medicine cat apprentice",
            ]:
                continue

            if "adult" in self.can_have_stat and kitty.status in [
                "apprentice",
                "medicine cat apprentice",
            ]:
                continue

            if "healer" in self.can_have_stat and kitty.status not in [
                "medicine cat",
                "medicine cat apprentice",
            ]:
                continue

            # Then, move on the specific requirements.
            if not self._allowed_stat_cat_specific(kitty, patrol, allowed_specific):
                continue

            possible_stat_cats.append(kitty)

        print("POSSIBLE STAT CATS", [str(i.name) for i in possible_stat_cats])

        actual_stat_cats = []
        for kitty in possible_stat_cats:
            if kitty.personality.trait in self.stat_trait:
                actual_stat_cats.append(kitty)

            if kitty.skills.check_skill_requirement_list(self.stat_skill):
                actual_stat_cats.append(kitty)

        if actual_stat_cats:
            self.stat_cat = choice(actual_stat_cats)
            print(f"Found stat cat: {self.stat_cat.name}")
        else:
            print("No Stat Cat Found")

        print("---")

        return

    def get_outcome_art(self):
        """Return outcome art, if not None. Return's None if there is no outcome art, or if outcome art can't be found."""
        root_dir = "resources/images/patrol_art/"

        if game.settings.get("gore") and self.outcome_art_clean:
            file_name = self.outcome_art_clean
        else:
            file_name = self.outcome_art

        if not isinstance(file_name, str) or not path_exists(
            f"{root_dir}{file_name}.png"
        ):
            return None

        return pygame.image.load(f"{root_dir}{file_name}.png")

    # ---------------------------------------------------------------------------- #
    #                                   HANDLERS                                   #
    # ---------------------------------------------------------------------------- #

    def _handle_exp(self, patrol: "Patrol") -> str:
        """Handle giving exp"""

        if game.clan.game_mode == "classic":
            gm_modifier = 1
        elif game.clan.game_mode == "expanded":
            gm_modifier = 3
        elif game.clan.game_mode == "cruel season":
            gm_modifier = 6
        else:
            gm_modifier = 1

        base_exp = 0
        if "master" in [x.experience_level for x in patrol.patrol_cats]:
            max_boost = 10
        else:
            max_boost = 0
        patrol_exp = 2 * self.exp
        gained_exp = patrol_exp + base_exp + max_boost
        gained_exp = max(
            gained_exp * (1 - 0.1 * len(patrol.patrol_cats)) / gm_modifier, 1
        )

        # Apprentice exp, does not depend on success
        if game.clan.game_mode != "classic":
            app_exp = max(random.randint(1, 7) * (1 - 0.1 * len(patrol.patrol_cats)), 1)
        else:
            app_exp = 0

        if gained_exp or app_exp:
            for cat in patrol.patrol_cats:
                if cat.status in ["apprentice", "medicine cat apprentice"]:
                    cat.experience = cat.experience + app_exp
                else:
                    cat.experience = cat.experience + gained_exp

        return ""

    def _handle_death(self, patrol: "Patrol") -> str:
        """Handle killing cats"""

        if not self.dead_cats:
            return ""

        # body_tags = ("body", "no_body")
        # leader_lives = ("all_lives", "some_lives")

        cats_to_kill = gather_cat_objects(
            Cat, self.dead_cats, patrol, stat_cat=self.stat_cat
        )

        if not cats_to_kill:
            print(
                f"Something was indicated in dead_cats, but no cats were indicated: {self.dead_cats}"
            )
            return ""

        body = True
        if "no_body" in self.dead_cats:
            body = False

        results = []
        for _cat in cats_to_kill:
            if _cat.status == "leader":
                if "all_lives" in self.dead_cats:
                    game.clan.leader_lives = 0
                    results.append(f"{_cat.name} lost all of their lives.")
                elif "some_lives" in self.dead_cats:
                    lives_lost = random.randint(1, max(1, game.clan.leader_lives - 1))
                    game.clan.leader_lives -= lives_lost
                    if lives_lost == 1:
                        results.append(f"{_cat.name} lost one life.")
                    else:
                        results.append(f"{_cat.name} lost {lives_lost} lives.")
                else:
                    game.clan.leader_lives -= 1
                    results.append(f"{_cat.name} lost one life.")
            else:
                results.append(f"{_cat.name} died.")

            # Kill Cat
            self.__handle_death_history(_cat, patrol)
            _cat.die(body)

        return " ".join(results)

    def _handle_lost(self, patrol: "Patrol") -> str:
        """Handle losing cats"""

        if not self.lost_cats:
            return ""

        cats_to_lose = gather_cat_objects(
            Cat, self.lost_cats, patrol, stat_cat=self.stat_cat
        )

        if not cats_to_lose:
            print(
                f"Something was indicated in lost_cats, but no cats were indicated: {self.lost_cats}"
            )
            return ""

        results = []
        for _cat in cats_to_lose:
            results.append(f"{_cat.name} has been lost.")
            _cat.gone()
            # _cat.greif(body=False)

        return " ".join(results)
    
    def _handle_df_convert(self, patrol:'Patrol') -> str:
        """ Handle converting cats to the DF in DF patrols """
        
        if not self.convert:
            return ""
        
        def gather_cat_objects(cat_list, patrol: 'Patrol') -> list: 
            out_set = set()
            
            for _cat in cat_list:
                if _cat == "r_c":
                    out_set.add(patrol.random_cat)
                elif _cat == "p_l":
                    out_set.add(patrol.patrol_leader)
                elif _cat == "s_c":
                    out_set.add(self.stat_cat)
                # lifegen ------------------
                elif _cat == "y_c":
                    out_set.add(game.clan.your_cat)
                elif _cat == "o_c1":
                    out_set.add(patrol.patrol_cats[2])
                # --------------------------
                elif _cat == "app1" and len(patrol.patrol_apprentices) >= 1:
                    out_set.add(patrol.patrol_apprentices[0])
                elif _cat == "app2" and len(patrol.patrol_apprentices) >= 2:
                    out_set.add(patrol.patrol_apprentices[1])
                elif _cat == "patrol":
                    out_set.update(patrol.patrol_cats)
                elif _cat == "multi":
                    cats_dying = random.randint(1, max(1, len(patrol.patrol_cats) - 1))
                    out_set.update(random.sample(patrol.patrol_cats, cats_dying))
                    
            return list(out_set)
        
        cats_to_convert = gather_cat_objects(self.convert, patrol)
        if not cats_to_convert:
            print(f"Something was indicated in convert, but no cats were indicated: {self.convert}")
            return ""
        
        
        results = []
        for _cat in cats_to_convert:
            results.append(f"{_cat.name} has joined the Dark Forest.")
            _cat.joined_df = True
            _cat.faith -= 1
            
        return " ".join(results)
    
    def _handle_faith_changes(self, patrol:'Patrol') -> str:
        """ Handle changing a cats faith in patrols """
        
        if not self.faith_effects:
            return ""
        
        def gather_cat_objects(cat_list, patrol: 'Patrol') -> list: 
            out_set = set()
            
            for _cat in cat_list:
                if _cat == "r_c":
                    out_set.add(patrol.random_cat)
                elif _cat == "p_l":
                    out_set.add(patrol.patrol_leader)
                elif _cat == "s_c":
                    out_set.add(self.stat_cat)
                elif _cat == "y_c":
                    out_set.add(game.clan.your_cat)
                elif _cat == "app1" and len(patrol.patrol_apprentices) >= 1:
                    out_set.add(patrol.patrol_apprentices[0])
                elif _cat == "app2" and len(patrol.patrol_apprentices) >= 2:
                    out_set.add(patrol.patrol_apprentices[1])
                elif _cat == "patrol":
                    out_set.update(patrol.patrol_cats)
                elif _cat == "multi":
                    cats_dying = random.randint(1, max(1, len(patrol.patrol_cats) - 1))
                    out_set.update(random.sample(patrol.patrol_cats, cats_dying))
                    
            return list(out_set)
        
        results = []
        for block in self.faith_effects:
            faith_cat = block.get("faith_cat", ())
            amount = block.get("amount")
            
            # Gather acual cat objects:
            faith_cat_ob = gather_cat_objects(faith_cat, patrol)
            
            # Remove any "None" that might have snuck in
            if None in faith_cat_ob:
                faith_cat_ob.remove(None)


            for _cat in faith_cat_ob:

                # results.append(f"{_cat.name}'s faith has changed.")
                _cat.faith = _cat.faith + amount

                # quick corrections if a cats faith passes the max amount from the patrol block
                if _cat.faith < -9:
                    _cat.faith = -9
                elif _cat.faith > 9:
                    _cat.faith = 9
        
        # return " ".join(results)
        return " "
        
    
    def _handle_murder(self, patrol:'Patrol') -> str:
        """ cat killin each other on patrol. just dark forest right now"""

        if not self.murder:
            return ""
        
        def gather_cat_objects(cat_list, patrol: 'Patrol') -> list:
            out_set = set()
            
            for _cat in cat_list:
                if _cat == "r_c":
                    out_set.add(patrol.random_cat)
                elif _cat == "p_l":
                    out_set.add(patrol.patrol_leader)
                elif _cat == "s_c":
                    out_set.add(self.stat_cat)
                elif _cat == "y_c":
                    out_set.add(game.clan.your_cat)
                elif _cat == "app1" and len(patrol.patrol_apprentices) >= 1:
                    out_set.add(patrol.patrol_apprentices[0])
                elif _cat == "app2" and len(patrol.patrol_apprentices) >= 2:
                    out_set.add(patrol.patrol_apprentices[1])
                elif _cat == "patrol":
                    out_set.update(patrol.patrol_cats)
                elif _cat == "multi":
                    cat_num = random.randint(1, max(1, len(patrol.patrol_cats) - 1))
                    out_set.update(random.sample(patrol.patrol_cats, cat_num))
                elif _cat == "some_clan":
                    clan_cats = [x for x in Cat.all_cats_list if not (x.dead or x.outside)]
                    out_set.update(random.sample(clan_cats, k=min(len(clan_cats), choice([2, 3, 4]))))
                elif re.match(r"n_c:[0-9]+", _cat):
                    index = re.match(r"n_c:([0-9]+)", _cat).group(1)
                    index = int(index)
                    if index < len(patrol.new_cats):
                        out_set.update(patrol.new_cats[index])
            return list(out_set)
        
        results = []
        for block in self.murder:
            murderer = block.get("murderer", ())
            victim = block.get("victim", ())
            
            # Gather acual cat objects:
            murderer_ob = gather_cat_objects(murderer, patrol)
            victim_ob = gather_cat_objects(victim, patrol)
            
            # Remove any "None" that might have snuck in
            if None in murderer_ob:
                murderer_ob.remove(None)
            if None in victim_ob:
                victim_ob.remove(None)

            results.append(f"{murderer_ob[-1].name} has murdered {victim_ob[-1].name}.")
            victim_ob[-1].die()

            # add the murder to their history!
            History.add_murders(victim_ob[-1], murderer_ob[-1], True, text=None, unrevealed_text=None)

        return " ".join(results)
          
    def _handle_condition_and_scars(self, patrol:'Patrol') -> str:
        """ Handle injuring cats, or giving scars """
        
        if not self.injury:
            return ""

        results = []
        condition_lists = INJURY_GROUPS

        for block in self.injury:
            cats = gather_cat_objects(Cat, block.get("cats", ()), patrol, self.stat_cat)
            injury = block.get("injuries", ())
            scars = block.get("scars", ())

            if not (cats and injury):
                print(f"something is wrong with injury - {block}")
                continue

            possible_injuries = []
            for _tag in injury:
                if _tag in condition_lists:
                    possible_injuries.extend(condition_lists[_tag])
                elif _tag in INJURIES or _tag in ILLNESSES or _tag in PERMANENT:
                    possible_injuries.append(_tag)

            lethal = True
            if "non_lethal" in injury:
                lethal = False

            # Injury or scar the cats
            results = []
            for _cat in cats:
                # give condition
                if not possible_injuries:
                    continue

                old_injuries = list(_cat.injuries.keys())
                old_illnesses = list(_cat.illnesses.keys())
                old_perm_cond = list(_cat.permanent_condition.keys())

                if set(possible_injuries).issubset(
                    old_injuries + old_illnesses + old_perm_cond
                ):
                    print(
                        "WARNING: All possible conditions are already on this cat! (poor kitty)"
                    )
                    continue

                give_injury = choice(possible_injuries)
                # If the cat already has this injury, reroll it to get something new
                while (
                    give_injury in old_injuries
                    or give_injury in old_illnesses
                    or give_injury in old_perm_cond
                ):
                    give_injury = choice(possible_injuries)

                if give_injury in INJURIES:
                    _cat.get_injured(give_injury, lethal=lethal)
                elif give_injury in ILLNESSES:
                    _cat.get_ill(give_injury, lethal=lethal)
                elif give_injury in PERMANENT:
                    _cat.get_permanent_condition(give_injury)
                else:
                    print("WARNING: No Conditions to Give")
                    continue

                given_conditions = []
                given_conditions.extend(
                    [x for x in _cat.injuries.keys() if x not in old_injuries]
                )
                given_conditions.extend(
                    [x for x in _cat.illnesses.keys() if x not in old_illnesses]
                )
                given_conditions.extend(
                    [
                        x
                        for x in _cat.permanent_condition.keys()
                        if x not in old_perm_cond
                    ]
                )
                # History is also ties to "no_results"
                if not block.get("no_results"):
                    for given_condition in given_conditions:
                        self.__handle_condition_history(_cat, given_condition, patrol)
                    combined_conditions = ", ".join(given_conditions)
                    results.append(f"{_cat.name} got: {combined_conditions}.")
                else:
                    # If no results are shown, assume the cat didn't get the patrol history. Default override.
                    self.__handle_condition_history(
                        _cat, give_injury, patrol, default_overide=True
                    )

        return " ".join(results)
    
    def _handle_accessories(self, patrol:'Patrol') -> str:
        """ cats getting accessories """
        
        if not self.accessory:
            return ""
        
        def gather_cat_objects(cat_list, patrol: 'Patrol') -> list:
            out_set = set()
            
            for _cat in cat_list:
                if _cat == "r_c":
                    out_set.add(patrol.random_cat)
                elif _cat == "p_l":
                    out_set.add(patrol.patrol_leader)
                elif _cat == "s_c":
                    out_set.add(self.stat_cat)
                # lifegen ------------------
                elif _cat == "y_c":
                    out_set.add(game.clan.your_cat)
                elif _cat == "o_c1":
                    out_set.add(patrol.patrol_cats[2])
                # --------------------------
                elif _cat == "app1" and len(patrol.patrol_apprentices) >= 1:
                    out_set.add(patrol.patrol_apprentices[0])
                elif _cat == "app2" and len(patrol.patrol_apprentices) >= 2:
                    out_set.add(patrol.patrol_apprentices[1])
                elif _cat == "patrol":
                    out_set.update(patrol.patrol_cats)
                elif _cat == "multi":
                    cat_num = random.randint(1, max(1, len(patrol.patrol_cats) - 1))
                    out_set.update(random.sample(patrol.patrol_cats, cat_num))
                elif _cat == "some_clan":
                    clan_cats = [x for x in Cat.all_cats_list if not (x.dead or x.outside)]
                    out_set.update(random.sample(clan_cats, k=min(len(clan_cats), choice([2, 3, 4]))))
                elif re.match(r"n_c:[0-9]+", _cat):
                    index = re.match(r"n_c:([0-9]+)", _cat).group(1)
                    index = int(index)
                    if index < len(patrol.new_cats):
                        out_set.update(patrol.new_cats[index])
                    
                    
            return list(out_set)
        
        results = []
       
        for block in self.accessory:
            cats = gather_cat_objects(block.get("cats", ()), patrol)
            accessory = block.get("accessory", ())
            
            if not (cats and accessory):
                print(f"something is wrong with accessory - {block}")
                continue

            for _cat in cats:
                if self.__handle_accs(_cat, accessory):
                    if not block.get("no_results"):
                        results.append(f"{_cat.name} got an accessory!")

        return " ".join(results)
            
    def _handle_rep_changes(self, patrol:'Patrol') -> str:
        """ Handles any changes in outsider rep"""

        if not isinstance(self.outsider_rep, int):
            return ""

        change_clan_reputation(self.outsider_rep)
        if self.outsider_rep > 0:
            insert = "improved"
        elif self.outsider_rep == 0:
            insert = "remained neutral"
        else:
            insert = "worsened"

        return f"Your Clan's reputation towards Outsiders has {insert}."

    def _handle_other_clan_relations(self, patrol: "Patrol") -> str:
        """Handles relations changes with other clans"""

        if not isinstance(self.other_clan_rep, int) or patrol.other_clan is None:
            return ""

        change_clan_relations(patrol.other_clan, self.other_clan_rep)
        if self.other_clan_rep > 0:
            insert = "improved"
        elif self.other_clan_rep == 0:
            insert = "remained neutral"
        else:
            insert = "worsened"

        return f"Relations with {patrol.other_clan} have {insert}."

    def _handle_herbs(self, patrol: "Patrol") -> str:
        """Handle giving herbs"""

        if not self.herbs or game.clan.game_mode == "classic":
            return ""

        large_bonus = False
        if "many_herbs" in self.herbs:
            large_bonus = True

        # Determine which herbs get picked
        specific_herbs = [x for x in self.herbs if x in HERBS]
        if "random_herbs" in self.herbs:
            specific_herbs += random.sample(
                HERBS, k=choices([1, 2, 3], [6, 5, 1], k=1)[0]
            )

        # Remove duplicates
        specific_herbs = list(set(specific_herbs))

        if not specific_herbs:
            print(f"{self.herbs} - gave no herbs to give")
            return ""

        patrol_size_modifier = int(len(patrol.patrol_cats) * 0.5)
        for _herb in specific_herbs:
            if large_bonus:
                amount_gotten = 6
            else:
                amount_gotten = choices([2, 4, 6], [2, 3, 1], k=1)[0]

            amount_gotten = int(amount_gotten * patrol_size_modifier)
            amount_gotten = max(1, amount_gotten)

            if _herb in game.clan.herbs:
                game.clan.herbs[_herb] += amount_gotten
            else:
                game.clan.herbs[_herb] = amount_gotten

        plural_herbs_list = ["cobwebs", "oak leaves"]

        if len(specific_herbs) == 1 and specific_herbs[0] not in plural_herbs_list:
            insert = f"{specific_herbs[0]} was"
        elif len(specific_herbs) == 1 and specific_herbs[0] in plural_herbs_list:
            insert = f"{specific_herbs[0]} were"
        elif len(specific_herbs) == 2:
            if str(specific_herbs[0]) == str(specific_herbs[1]):
                insert = f"{specific_herbs[0]} was"
            else:
                insert = f"{specific_herbs[0]} and {specific_herbs[1]} were"
        else:
            insert = f"{', '.join(specific_herbs[:-1])}, and {specific_herbs[-1]} were"

        insert = re.sub("[_]", " ", insert)

        game.herb_events_list.append(f"{insert.capitalize()} gathered on a patrol.")
        return f"{insert.capitalize()} gathered."

    def _handle_prey(self, patrol: "Patrol") -> str:
        """Handle giving prey"""

        if not FRESHKILL_ACTIVE:
            return ""

        if not self.prey or game.clan.game_mode == "classic":
            return ""

        basic_amount = PREY_REQUIREMENT["warrior"]
        if game.clan.game_mode == "expanded":
            basic_amount += ADDITIONAL_PREY
        prey_types = {
            "very_small": basic_amount / 2,
            "small": basic_amount,
            "medium": basic_amount * 1.8,
            "large": basic_amount * 2.4,
            "huge": basic_amount * 3.2,
        }

        used_tag = None
        for tag in self.prey:
            basic_amount = prey_types.get(tag)
            if basic_amount is not None:
                used_tag = tag
                break
        else:
            print(f"{self.prey} - no prey amount tags in prey property")
            return ""

        total_amount = 0
        highest_hunter_tier = 0
        for cat in patrol.patrol_cats:
            total_amount += basic_amount
            if (
                cat.skills.primary.path == SkillPath.HUNTER
                and cat.skills.primary.tier > 0
            ):
                level = cat.experience_level
                tier = cat.skills.primary.tier
                if tier > highest_hunter_tier:
                    highest_hunter_tier = tier
                total_amount += int(
                    HUNTER_EXP_BONUS[level] * (HUNTER_BONUS[str(tier)] / 10 + 1)
                )
            elif (
                cat.skills.secondary
                and cat.skills.secondary.path == SkillPath.HUNTER
                and cat.skills.secondary.tier > 0
            ):
                level = cat.experience_level
                tier = cat.skills.secondary.tier
                if tier > highest_hunter_tier:
                    highest_hunter_tier = tier
                total_amount += int(
                    HUNTER_EXP_BONUS[level] * (HUNTER_BONUS[str(tier)] / 10 + 1)
                )

        # additional hunter buff for expanded mode
        if game.clan.game_mode == "expanded" and highest_hunter_tier:
            total_amount = int(
                total_amount * (HUNTER_BONUS[str(highest_hunter_tier)] / 20 + 1)
            )

        results = ""
        if total_amount > 0:
            amount_text = used_tag
            if "_" in amount_text:
                amount_text = amount_text.replace("_", " ")

            total_amount = round(total_amount, 2)
            print(f"PREY ADDED: {total_amount}")
            game.freshkill_event_list.append(
                f"{total_amount} pieces of prey were caught on a patrol."
            )
            game.clan.freshkill_pile.add_freshkill(total_amount)
            results = f"A {amount_text} amount of prey is brought to camp."

        return results

    def _handle_new_cats(self, patrol: "Patrol") -> str:
        """Handles creating a new cat. Add any new cats to patrol.new_cats"""

        if not self.new_cat:
            return ""

        results = []
        in_event_cats  = {
            "p_l": patrol.patrol_leader,
            "r_c": patrol.random_cat,
        }
        if self.stat_cat:
            in_event_cats["s_c"] = self.stat_cat

        for i, attribute_list in enumerate(self.new_cat):
            patrol.new_cats.append(
                create_new_cat_block(
                    Cat, Relationship, patrol, in_event_cats, i, attribute_list
                )
            )

            for cat in patrol.new_cats[-1]:
                if cat.dead:
                    # LIFEGEN --------------------------------------------------------------------------
                    if (
                        cat.history and
                        cat.history.beginning and
                        "encountered" in cat.history.beginning and
                        cat.history.beginning["encountered"] is True
                        ):
                        if cat.ID in game.clan.your_cat.mate:
                            cat.thought = f"Is missing {game.clan.your_cat.name}"
                            results.append(f"You have spoken with {cat.name}.")
                        else:
                        # a different message for these guys so it doesnt imply they just died
                            results.append(f"You have met {cat.name}.")
                    # -----------------------------------------------------------------------------------
                    else:
                        results.append(f"{cat.name}'s ghost now wanders.")
                elif cat.outside:
                    results.append(f"The patrol met {cat.name}.")
                else:
                    results.append(f"{cat.name} joined the Clan.")

                cat.pelt.inventory = []
                # ^^ this stops the multi-cat inventory thing for kittypets joining from patrols!!
            
        # Check to see if any young litters joined with alive parents.
        # If so, see if recovering from birth condition is needed
        # and give the condition
        for sub in patrol.new_cats:
            if sub[0].moons < 3:
                # Search for parent
                for sub_sub in patrol.new_cats:
                    if (
                        sub_sub[0] != sub[0]
                        and (
                            sub_sub[0].gender == "female"
                            or game.clan.clan_settings["same sex birth"]
                        )
                        and sub_sub[0].ID in (sub[0].parent1, sub[0].parent2)
                        and not (sub_sub[0].dead or sub_sub[0].outside)
                    ):
                        sub_sub[0].get_injured("recovering from birth")
                        break  # Break - only one parent ever gives birth

        return " ".join(results)
            

    def _handle_mentor_app(self, patrol: "Patrol") -> str:
        """Handles mentor inflence on apprentices"""

        for cat in patrol.patrol_cats:
            if Cat.fetch_cat(cat.mentor) in patrol.patrol_cats:
                mentor = Cat.fetch_cat(cat.mentor)
                affect_personality = cat.personality.mentor_influence(
                    mentor.personality
                )
                affect_skills = cat.skills.mentor_influence(mentor)
                if affect_personality:
                    History.add_facet_mentor_influence(
                        cat, mentor.ID, affect_personality[0], affect_personality[1]
                    )
                    print(str(cat.name), affect_personality)
                if affect_skills:
                    History.add_skill_mentor_influence(
                        cat, affect_skills[0], affect_skills[1], affect_skills[2]
                    )
                    print(str(cat.name), affect_skills)

        return ""

    # ---------------------------------------------------------------------------- #
    #                                   HELPERS                                    #
    # ---------------------------------------------------------------------------- #

    def _add_death_history(self, cat: Cat):
        """Adds death history for a cat"""

    def _add_potential_history(self, cat: Cat, condition):
        """Add potential history for a condition"""

    def __handle_scarring(self, cat: Cat, scar_list: str, patrol: "Patrol"):
        """Add scar and scar history. Returns scar given"""

        if len(cat.pelt.scars) >= 4:
            return None

        scar_list = [
            x
            for x in scar_list
            if x in Pelt.scars1 + Pelt.scars2 + Pelt.scars3 and x not in cat.pelt.scars
        ]

        if not scar_list:
            return None

        chosen_scar = choice(scar_list)
        cat.pelt.scars.append(chosen_scar)

        history_text = self.history_scar
        if history_text and isinstance(history_text, str):
            # I'm not 100% sure which one is supposed to be which...
            history_text = (
                history_text
                if "m_c" not in history_text
                else history_text.replace("m_c", str(cat.name))
            )
            history_text = (
                history_text
                if "r_c" not in history_text
                else history_text.replace("r_c", str(patrol.random_cat.name))
            )
            history_text = (
                history_text
                if "o_c_n" not in history_text
                else history_text.replace("o_c_n", f"{str(patrol.other_clan.name)}Clan")
            )

            History.add_scar(cat, history_text)
        else:
            print("WARNING: Scar occured, but scar history is missing")

        return chosen_scar

    def __handle_condition_history(
        self, cat: Cat, condition: str, patrol: "Patrol", default_overide=False
    ) -> None:
        """Handles adding potentional history to a cat. default_overide will use the default text for the condition."""

        if not (
            self.history_leader_death and self.history_reg_death and self.history_scar
        ):
            print("WARNING: Injury occured, but some death or scar history is missing.")

        final_death_history = None
        if cat.status == "leader":
            if self.history_leader_death:
                final_death_history = self.history_leader_death
        else:
            final_death_history = self.history_reg_death

        history_scar = self.history_scar

        if default_overide:
            final_death_history = None
            history_scar = None

        if final_death_history and isinstance(final_death_history, str):
            final_death_history = (
                final_death_history
                if "o_c_n" not in final_death_history
                else final_death_history.replace(
                    "o_c_n", f"{str(patrol.other_clan.name)}Clan"
                )
            )

        if history_scar and isinstance(history_scar, str):
            history_scar = (
                history_scar
                if "o_c_n" not in history_scar
                else history_scar.replace("o_c_n", f"{str(patrol.other_clan.name)}Clan")
            )

        History.add_possible_history(
            cat,
            condition=condition,
            death_text=final_death_history,
            scar_text=history_scar,
        )

    def __handle_death_history(self, cat: Cat, patrol: "Patrol") -> None:
        """Handles adding death history, for dead cats."""

        if not (self.history_leader_death and self.history_reg_death):
            print("WARNING: Death occured, but some death history is missing.")

        final_death_history = None
        if cat.status == "leader":
            if self.history_leader_death:
                final_death_history = self.history_leader_death
        else:
            final_death_history = self.history_reg_death

        if not final_death_history:
            final_death_history = "m_c died on patrol."

        if final_death_history and isinstance(final_death_history, str):
            final_death_history = final_death_history.replace(
                "o_c_n", f"{str(patrol.other_clan.name)}Clan"
            )

        History.add_death(cat, death_text=final_death_history)
        if self.murder:
            for x in patrol.patrol_cats:
                if x.ID != cat.ID:
                    other_cat = x
            
            History.add_murders(cat, other_cat, True, f"{other_cat.name} killed this cat in the Dark Forest.")
    
    def __handle_accs(self, cat: Cat, acc_list: str) -> str:

        if "WILD" in acc_list:
            acc_list = Pelt.wild_accessories
        elif "COLLAR" in acc_list:
            acc_list = Pelt.collars
        elif "TAIL" in acc_list:
            acc_list = Pelt.tail_accessories + Pelt.tail2_accessories
        #elif "SNAKE" in acc_list:
        #    acc_list = Pelt.snake_accessories
        #elif "RABBIT" in acc_list:
        #    acc_list = ["WHITE RABBIT", "BLACK RABBIT",
        #                "BROWN RABBIT", "FAWN RABBIT",
        #                "BROWN AND WHITE RABBIT", "BLACK AND WHITE RABBIT", "WHITE AND FAWN RABBIT",
        #                "BLACK VITILIGO RABBIT", "BROWN VITILIGO RABBIT", "FAWN VITILIGO RABBIT",
        #                "TAN RABBIT", "TAN AND WHITE RABBIT", "TAN VITILIGO RABBIT",
        #                "GRAY RABBIT", "GRAY AND WHITE RABBIT", "GRAY VITILIGO RABBIT"]
        #elif "BIRD" in acc_list:
        #    acc_list = ["BLACKBIRD", "ROBIN", "JAY", "THRUSH", "CARDINAL", "MAGPIE", "CUBAN TROGON"]
        #elif "SQUIRREL" in acc_list:
        #    acc_list = ["GRAY SQUIRREL", "RED SQUIRREL", "CRAB", "INDIAN GIANT SQUIRREL"]
        #elif "MOUSE" in acc_list:
        #    acc_list = ["RAT", "WHITE MOUSE", "BLACK MOUSE", "GRAY MOUSE", "BROWN MOUSE"]
        #elif "SMALLANIMAL" in acc_list:
        #    acc_list = Pelt.smallAnimal_accessories
        #elif "DEADINSECT" in acc_list:
        #    acc_list = Pelt.deadInsect_accessories
        #elif "ALIVEINSECT" in acc_list:
        #    acc_list = Pelt.aliveInsect_accessories
        #elif "FRUIT" in acc_list:
        #    acc_list = Pelt.fruit_accessories + "BLUE BERRIES" + "BERRIES"
        #elif "CRAFTED" in acc_list:
        #    acc_list = Pelt.crafted_accessories + 'WOODDRAGON'
        #elif "LEAF" in acc_list:
        #    acc_list = ["MAPLE LEAF", "HOLLY", "HERBS", "DRY HERBS","OAK LEAVES", "CATMINT", "MAPLE SEED", "JUNIPER", "FERNS", "GOLD FERNS", "WHEAT", "BLACK WHEAT","CLOVERS", "CLOVER", "CHERRYPLUMLEAVES"]
        #elif "FLOWER" in acc_list:
        #    acc_list = Pelt.flower_accessories + ['REDCROWN', 'YELLOWCROWN', 'LILY', 'CLOVERFLOWER']
        #elif "FLOWERCROWN" in acc_list:
        #    acc_list = ['REDCROWN', 'YELLOWCROWN', "PINKFLOWERCROWN", "YELLOWFLOWERCROWN", "BLUEFLOWERCROWN", "PURPLEFLOWERCROWN", "FLOWERCROWN"]
        else:
            acc_list = [x for x in acc_list if x in Pelt.plant_accessories + Pelt.wild_accessories + Pelt.collars
        #+ Pelt.plant2_accessories +\
        #Pelt.tail_accessories + Pelt.flower_accessories + Pelt.snake_accessories + Pelt.smallAnimal_accessories + \
        #Pelt.deadInsect_accessories + Pelt.aliveInsect_accessories + Pelt.fruit_accessories + Pelt.crafted_accessories + \
        #Pelt.tail2_accessories
                            and x not in cat.pelt.inventory]

        if not acc_list:
            return None

        chosen_acc = choice(acc_list)
        if chosen_acc not in cat.pelt.inventory:
            cat.pelt.inventory.append(chosen_acc)
            cat.pelt.accessories.append(chosen_acc)

        return chosen_acc
