import logging
import os
from copy import copy

import pygame
import ujson

from scripts.game_structure.game_essentials import game

logger = logging.getLogger(__name__)


class Sprites:
    cat_tints = {}
    white_patches_tints = {}
    clan_symbols = []

    def __init__(self):
        """Class that handles and hold all spritesheets.
        Size is normally automatically determined by the size
        of the lineart. If a size is passed, it will override
        this value."""
        self.symbol_dict = None
        self.size = None
        self.spritesheets = {}
        self.images = {}
        self.sprites = {}

        # Shared empty sprite for placeholders
        self.blank_sprite = None

        self.load_tints()

    def load_tints(self):
        try:
            with open("sprites/dicts/tint.json", "r") as read_file:
                self.cat_tints = ujson.loads(read_file.read())
        except IOError:
            print("ERROR: Reading Tints")

        try:
            with open("sprites/dicts/white_patches_tint.json", "r") as read_file:
                self.white_patches_tints = ujson.loads(read_file.read())
        except IOError:
            print("ERROR: Reading White Patches Tints")

    def spritesheet(self, a_file, name):
        """
        Add spritesheet called name from a_file.

        Parameters:
        a_file -- Path to the file to create a spritesheet from.
        name -- Name to call the new spritesheet.
        """
        self.spritesheets[name] = pygame.image.load(a_file).convert_alpha()

    def make_group(
        self, spritesheet, pos, name, sprites_x=3, sprites_y=7, no_index=False
    ):  # pos = ex. (2, 3), no single pixels
        """
        Divide sprites on a spritesheet into groups of sprites that are easily accessible
        :param spritesheet: Name of spritesheet file
        :param pos: (x,y) tuple of offsets. NOT pixel offset, but offset of other sprites
        :param name: Name of group being made
        :param sprites_x: default 3, number of sprites horizontally
        :param sprites_y: default 3, number of sprites vertically
        :param no_index: default False, set True if sprite name does not require cat pose index
        """
        group_x_ofs = pos[0] * sprites_x * self.size
        group_y_ofs = pos[1] * sprites_y * self.size
        i = 0

        # splitting group into singular sprites and storing into self.sprites section
        for y in range(sprites_y):
            for x in range(sprites_x):
                if no_index:
                    full_name = f"{name}"
                else:
                    full_name = f"{name}{i}"

                try:
                    new_sprite = pygame.Surface.subsurface(
                        self.spritesheets[spritesheet],
                        group_x_ofs + x * self.size,
                        group_y_ofs + y * self.size,
                        self.size,
                        self.size,
                    )

                except ValueError:
                    # Fallback for non-existent sprites
                    print(f"WARNING: nonexistent sprite - {full_name}")
                    if not self.blank_sprite:
                        self.blank_sprite = pygame.Surface(
                            (self.size, self.size), pygame.HWSURFACE | pygame.SRCALPHA
                        )
                    new_sprite = self.blank_sprite

                self.sprites[full_name] = new_sprite
                i += 1

    def load_all(self):
        # get the width and height of the spritesheet
        lineart = pygame.image.load("sprites/lineart.png")
        width, height = lineart.get_size()
        del lineart  # unneeded

        # if anyone changes lineart for whatever reason update this
        if isinstance(self.size, int):
            pass
        elif width / 3 == height / 7:
            self.size = width / 3
        else:
            self.size = 50  # default, what base clangen uses
            print(f"lineart.png is not 3x7, falling back to {self.size}")
            print(
                "if you are a modder, please update scripts/cat/sprites.py and "
                "do a search for 'if width / 3 == height / 7:'"
            )

        del width, height  # unneeded

        for x in [
            "lineart",
            "lineartur",
            "lineartdf",
            "lineartdead",
            "eyes",
            "eyes2",
            "skin",
            "scars",
            "missingscars",
            "medcatherbs",
            "wild",
            "collars",
            "bellcollars",
            "bowcollars",
            "nyloncollars",
            "singlecolours",
            "speckledcolours",
            "tabbycolours",
            "bengalcolours",
            "marbledcolours",
            "rosettecolours",
            "smokecolours",
            "tickedcolours",
            "mackerelcolours",
            "classiccolours",
            "sokokecolours",
            "agouticolours",
            "singlestripecolours",
            "maskedcolours",
            "shadersnewwhite",
            "lightingnew",
            "whitepatches",
            "tortiepatchesmasks",
            "fademask",
            "fadestarclan",
            "fadedarkforest",
            "symbols",

            #OHDANS
            'flower_accessories', 'plant2_accessories', 'snake_accessories', 'smallAnimal_accessories', 'deadInsect_accessories',
            'aliveInsect_accessories', 'fruit_accessories', 'crafted_accessories', 'tail2_accessories',

            #WILDS
            'wildaccs_1', 'wildaccs_2',

            #SUPERARTSI
            'superartsi',

            #coffee
            'coffee','eragona','crowns','springwinter','raincoats','chimes','moipa','moipa2','pocky1','misc_acc','reign1'

        ]:
            if "lineart" in x and game.config["fun"]["april_fools"]:
                self.spritesheet(f"sprites/aprilfools{x}.png", x)
            else:
                self.spritesheet(f"sprites/{x}.png", x)

        # Line art
        self.make_group("lineart", (0, 0), "lines")
        self.make_group("shadersnewwhite", (0, 0), "shaders")
        self.make_group("lightingnew", (0, 0), "lighting")

        self.make_group('lineartdead', (0, 0), 'lineartdead')
        self.make_group('lineartdf', (0, 0), 'lineartdf')
        self.make_group('lineartur', (0, 0), 'lineartur')
        # Fading Fog
        for i in range(0, 3):
            self.make_group("fademask", (i, 0), f"fademask{i}")
            self.make_group("fadestarclan", (i, 0), f"fadestarclan{i}")
            self.make_group("fadedarkforest", (i, 0), f"fadedf{i}")

        # Define eye colors
        eye_colors = [
            [
                "YELLOW",
                "AMBER",
                "HAZEL",
                "PALEGREEN",
                "GREEN",
                "BLUE",
                "DARKBLUE",
                "GREY",
                "CYAN",
                "EMERALD",
                "HEATHERBLUE",
                "SUNLITICE",
            ],
            [
                "COPPER",
                "SAGE",
                "COBALT",
                "PALEBLUE",
                "BRONZE",
                "SILVER",
                "PALEYELLOW",
                "GOLD",
                "GREENYELLOW",
            ],
        ]

        for row, colors in enumerate(eye_colors):
            for col, color in enumerate(colors):
                self.make_group("eyes", (col, row), f"eyes{color}")
                self.make_group("eyes2", (col, row), f"eyes2{color}")

        # Define white patches
        white_patches = [
            [
                "FULLWHITE",
                "ANY",
                "TUXEDO",
                "LITTLE",
                "COLOURPOINT",
                "VAN",
                "ANYTWO",
                "MOON",
                "PHANTOM",
                "POWDER",
                "BLEACHED",
                "SAVANNAH",
                "FADESPOTS",
                "PEBBLESHINE",
            ],
            [
                "EXTRA",
                "ONEEAR",
                "BROKEN",
                "LIGHTTUXEDO",
                "BUZZARDFANG",
                "RAGDOLL",
                "LIGHTSONG",
                "VITILIGO",
                "BLACKSTAR",
                "PIEBALD",
                "CURVED",
                "PETAL",
                "SHIBAINU",
                "OWL",
            ],
            [
                "TIP",
                "FANCY",
                "FRECKLES",
                "RINGTAIL",
                "HALFFACE",
                "PANTSTWO",
                "GOATEE",
                "VITILIGOTWO",
                "PAWS",
                "MITAINE",
                "BROKENBLAZE",
                "SCOURGE",
                "DIVA",
                "BEARD",
            ],
            [
                "TAIL",
                "BLAZE",
                "PRINCE",
                "BIB",
                "VEE",
                "UNDERS",
                "HONEY",
                "FAROFA",
                "DAMIEN",
                "MISTER",
                "BELLY",
                "TAILTIP",
                "TOES",
                "TOPCOVER",
            ],
            [
                "APRON",
                "CAPSADDLE",
                "MASKMANTLE",
                "SQUEAKS",
                "STAR",
                "TOESTAIL",
                "RAVENPAW",
                "PANTS",
                "REVERSEPANTS",
                "SKUNK",
                "KARPATI",
                "HALFWHITE",
                "APPALOOSA",
                "DAPPLEPAW",
            ],
            [
                "HEART",
                "LILTWO",
                "GLASS",
                "MOORISH",
                "SEPIAPOINT",
                "MINKPOINT",
                "SEALPOINT",
                "MAO",
                "LUNA",
                "CHESTSPECK",
                "WINGS",
                "PAINTED",
                "HEARTTWO",
                "WOODPECKER",
            ],
            [
                "BOOTS",
                "MISS",
                "COW",
                "COWTWO",
                "BUB",
                "BOWTIE",
                "MUSTACHE",
                "REVERSEHEART",
                "SPARROW",
                "VEST",
                "LOVEBUG",
                "TRIXIE",
                "SAMMY",
                "SPARKLE",
            ],
            [
                "RIGHTEAR",
                "LEFTEAR",
                "ESTRELLA",
                "SHOOTINGSTAR",
                "EYESPOT",
                "REVERSEEYE",
                "FADEBELLY",
                "FRONT",
                "BLOSSOMSTEP",
                "PEBBLE",
                "TAILTWO",
                "BUDDY",
                "BACKSPOT",
                "EYEBAGS",
            ],
            [
                "BULLSEYE",
                "FINN",
                "DIGIT",
                "KROPKA",
                "FCTWO",
                "FCONE",
                "MIA",
                "SCAR",
                "BUSTER",
                "SMOKEY",
                "HAWKBLAZE",
                "CAKE",
                "ROSINA",
                "PRINCESS",
            ],
            ["LOCKET", "BLAZEMASK", "TEARS", "DOUGIE"],
        ]

        for row, patches in enumerate(white_patches):
            for col, patch in enumerate(patches):
                self.make_group("whitepatches", (col, row), f"white{patch}")

        # Define colors and categories
        color_categories = [
            ["WHITE", "PALEGREY", "SILVER", "GREY", "DARKGREY", "GHOST", "BLACK"],
            ["CREAM", "PALEGINGER", "GOLDEN", "GINGER", "DARKGINGER", "SIENNA"],
            ["LIGHTBROWN", "LILAC", "BROWN", "GOLDEN-BROWN", "DARKBROWN", "CHOCOLATE"],
        ]

        color_types = [
            "singlecolours",
            "tabbycolours",
            "marbledcolours",
            "rosettecolours",
            "smokecolours",
            "tickedcolours",
            "speckledcolours",
            "bengalcolours",
            "mackerelcolours",
            "classiccolours",
            "sokokecolours",
            "agouticolours",
            "singlestripecolours",
            "maskedcolours",
        ]

        for row, colors in enumerate(color_categories):
            for col, color in enumerate(colors):
                for color_type in color_types:
                    self.make_group(color_type, (col, row), f"{color_type[:-7]}{color}")

        # tortiepatchesmasks
        tortiepatchesmasks = [
            [
                "ONE",
                "TWO",
                "THREE",
                "FOUR",
                "REDTAIL",
                "DELILAH",
                "HALF",
                "STREAK",
                "MASK",
                "SMOKE",
            ],
            [
                "MINIMALONE",
                "MINIMALTWO",
                "MINIMALTHREE",
                "MINIMALFOUR",
                "OREO",
                "SWOOP",
                "CHIMERA",
                "CHEST",
                "ARMTAIL",
                "GRUMPYFACE",
            ],
            [
                "MOTTLED",
                "SIDEMASK",
                "EYEDOT",
                "BANDANA",
                "PACMAN",
                "STREAMSTRIKE",
                "SMUDGED",
                "DAUB",
                "EMBER",
                "BRIE",
            ],
            [
                "ORIOLE",
                "ROBIN",
                "BRINDLE",
                "PAIGE",
                "ROSETAIL",
                "SAFI",
                "DAPPLENIGHT",
                "BLANKET",
                "BELOVED",
                "BODY",
            ],
            ["SHILOH", "FRECKLED", "HEARTBEAT"],
        ]

        for row, masks in enumerate(tortiepatchesmasks):
            for col, mask in enumerate(masks):
                self.make_group("tortiepatchesmasks", (col, row), f"tortiemask{mask}")

        # Define skin colors
        skin_colors = [
            ["BLACK", "RED", "PINK", "DARKBROWN", "BROWN", "LIGHTBROWN"],
            ["DARK", "DARKGREY", "GREY", "DARKSALMON", "SALMON", "PEACH"],
            ["DARKMARBLED", "MARBLED", "LIGHTMARBLED", "DARKBLUE", "BLUE", "LIGHTBLUE"],
        ]

        for row, colors in enumerate(skin_colors):
            for col, color in enumerate(colors):
                self.make_group("skin", (col, row), f"skin{color}")

        self.load_scars()
        self.load_symbols()

    def load_scars(self):
        """
        Loads scar sprites and puts them into groups.
        """

            # ohdan's accessories
        for a, i in enumerate([
            "DAISIES", "DIANTHUS", "BLEEDING HEARTS", "FRANGIPANI", "BLUE GLORY", "CATNIP FLOWER", "BLANKET FLOWER", "ALLIUM", "LACELEAF", "PURPLE GLORY"]):
            self.make_group('flower_accessories', (a, 0), f'acc_flower{i}')
        for a, i in enumerate([
            "YELLOW PRIMROSE", "HESPERIS", "MARIGOLD", "WISTERIA"]):
            self.make_group('flower_accessories', (a, 1), f'acc_flower{i}')
        
        for a, i in enumerate([
            "SINGULARCLOVER", "STICK", "PUMPKIN", "MOSS", "IVY", "ACORN", "MOSS PELT", "REEDS", "BAMBOO"]):
            self.make_group('plant2_accessories', (a, 0), f'acc_plant2{i}')

        for a, i in enumerate([
            "GRASS SNAKE", "BLUE RACER", "WESTERN COACHWHIP", "KINGSNAKE"]):
            self.make_group('snake_accessories', (a, 0), f'acc_snake{i}')
            
        for a, i in enumerate([
            "GRAY SQUIRREL", "RED SQUIRREL", "CRAB", "WHITE RABBIT", "BLACK RABBIT", "BROWN RABBIT", "INDIAN GIANT SQUIRREL", "FAWN RABBIT", "BROWN AND WHITE RABBIT", "BLACK AND WHITE RABBIT"]):
            self.make_group('smallAnimal_accessories', (a, 0), f'acc_smallAnimal{i}')
        for a, i in enumerate([
            "WHITE AND FAWN RABBIT", "BLACK VITILIGO RABBIT", "BROWN VITILIGO RABBIT", "FAWN VITILIGO RABBIT", "BLACKBIRD", "ROBIN", "JAY", "THRUSH", "CARDINAL", "MAGPIE"]):
            self.make_group('smallAnimal_accessories', (a, 1), f'acc_smallAnimal{i}')
        for a, i in enumerate([
            "CUBAN TROGON", "TAN RABBIT", "TAN AND WHITE RABBIT", "TAN VITILIGO RABBIT", "RAT", "WHITE MOUSE", "BLACK MOUSE", "GRAY MOUSE", "BROWN MOUSE", "GRAY RABBIT"]):
            self.make_group('smallAnimal_accessories', (a, 2), f'acc_smallAnimal{i}')
        for a, i in enumerate([
            "GRAY AND WHITE RABBIT", "GRAY VITILIGO RABBIT"]):
            self.make_group('smallAnimal_accessories', (a, 3), f'acc_smallAnimal{i}')
            
        for a, i in enumerate([
            "LUNAR MOTH", "ROSY MAPLE MOTH", "MONARCH", "DAPPLED MONARCH", "POLYPHEMUS MOTH", "MINT MOTH"]):
            self.make_group('deadInsect_accessories', (a, 0), f'acc_deadInsect{i}')
            
        for a, i in enumerate([
            "BROWN SNAIL", "RED SNAIL", "WORM", "BLUE SNAIL", "ZEBRA ISOPOD", "DUCKY ISOPOD", "DAIRY COW ISOPOD", "BEETLEJUICE ISOPOD", "BEE", "RED LADYBUG"]):
            self.make_group('aliveInsect_accessories', (a, 0), f'acc_aliveInsect{i}')
        for a, i in enumerate([
            "ORANGE LADYBUG", "YELLOW LADYBUG"]):
            self.make_group('aliveInsect_accessories', (a, 1), f'acc_aliveInsect{i}')
        
        for a, i in enumerate([
            "RASPBERRY2", "BLACKBERRY", "GOLDEN RASPBERRY", "CHERRY", "YEW"]):
            self.make_group('fruit_accessories', (a, 0), f'acc_fruit{i}')
        
        for a, i in enumerate([
            "WILLOWBARK BAG", "CLAY DAISY POT", "CLAY AMANITA POT", "CLAY BROWNCAP POT", "BIRD SKULL", "LEAF BOW"]):
            self.make_group('crafted_accessories', (a, 0), f'acc_crafted{i}')
        
        for a, i in enumerate([
            "SEAWEED", "DAISY CORSAGE"]):
            self.make_group('tail2_accessories', (a, 0), f'acc_tail2{i}')


        # wilds accessories redone sheets by moipa and jay
        for a, i in enumerate([
            "LILYPAD", "LARGE DEATHBERRY", "SMALL DEATHBERRY", "ACORN2", "PINECONE", "VINE"]):
            self.make_group('wildaccs_1', (a, 0), f'acc_herbs{i}')
        
        for a, i in enumerate([
            "CHERRY2", "BLEEDING HEARTS2", "SHELL PACK", "FERNS", "GOLD FERNS"]):
            self.make_group('wildaccs_1', (a, 1), f'acc_herbs{i}')

        for a, i in enumerate([
            "WHEAT", "BLACK WHEAT"]):
            self.make_group('wildaccs_1', (a, 2), f'acc_herbs{i}')
        
        # -------------------------------------------------------------------------
        
        for a, i in enumerate([
            "BERRIES", "CLOVERS", "CLOVER2", "MOSS2", "FLOWER MOSS", "MUSHROOMS"]):
            self.make_group('wildaccs_2', (a, 0), f'acc_herbs{i}')

        for a, i in enumerate([
            "LARGE LUNA", "LARGE COMET", "SMALL LUNA", "SMALL COMET", "LADYBUGS"]):
            self.make_group('wildaccs_2', (a, 1), f'acc_wild{i}')

        for a, i in enumerate([
            "MUD PAWS", "ASHY PAWS"]):
            self.make_group('wildaccs_2', (a, 2), f'acc_wild{i}')

        # superartsi's accessories

        for a, i in enumerate([
            "ORANGEBUTTERFLY", "BLUEBUTTERFLY", "BROWNPELT", "GRAYPELT", "BROWNMOSSPELT", "GRAYMOSSPELT"]):
            self.make_group('superartsi', (a, 0), f'acc_wild{i}')
        for a, i in enumerate([
            "FERN", "MOREFERN", "BLEEDINGVINES", "BLEEDINGHEART", "LILY"]):
            self.make_group('superartsi', (a, 1), f'acc_wild{i}')

        # coffee's accessories
        for a, i in enumerate([
            "PINKFLOWERCROWN", "YELLOWFLOWERCROWN", "BLUEFLOWERCROWN", "PURPLEFLOWERCROWN"]):
            self.make_group('coffee', (a, 0), f'acc_flower{i}')

        # eragona rose's accessories

        for a, i in enumerate([
            "REDHARNESS", "NAVYHARNESS", "YELLOWHARNESS", "TEALHARNESS", "ORANGEHARNESS", "GREENHARNESS"]):
            self.make_group('eragona', (a, 0), f'collars{i}')
        for a, i in enumerate([
            "MOSSHARNESS", "RAINBOWHARNESS", "BLACKHARNESS", "BEEHARNESS", "CREAMHARNESS"]):
            self.make_group('eragona', (a, 1), f'collars{i}')
        for a, i in enumerate([
            "PINKHARNESS", "MAGENTAHARNESS", "PEACHHARNESS", "VIOLETHARNESS"]):
            self.make_group('eragona', (a, 2), f'collars{i}')

        for a, i in enumerate([
            "YELLOWCROWN", "REDCROWN", "LILYPADCROWN"]):
            self.make_group('crowns', (a, 0), f'acc_wild{i}')


        for a, i in enumerate(["CHERRYBLOSSOM","TULIPPETALS","CLOVERFLOWER","PANSIES","BELLFLOWERS","SANVITALIAFLOWERS","EGGSHELLS","BLUEEGGSHELLS","EASTEREGG","FORSYTHIA"]):
            self.make_group('springwinter', (a, 0), f'acc_wild{i}')
        for a, i in enumerate([
            "MINTLEAF","STICKS","SPRINGFEATHERS","SNAILSHELL","MUD","CHERRYPLUMLEAVES","CATKIN","HONEYCOMB","FLOWERCROWN","LILIESOFTHEVALLEY"]):
            self.make_group('springwinter', (a, 1), f'acc_wild{i}')
        for a, i in enumerate([
            "STRAWMANE","MISTLETOE","REDPOINSETTIA","WHITEPOINSETTIA","COTONEASTERWREATH","YEWS","CALLUNA","TEETHCOLLAR","DRIEDORANGE","ROESKULL"]):
            self.make_group('springwinter', (a, 2), f'acc_wild{i}')
        for a, i in enumerate([
            "WOODENOAKANTLERS","WOODENBIRCHANTLERS","DOGWOOD","GRAYWOOL","BLACKWOOL","CREAMWOOL","WHITEWOOL","FIRBRANCHES","CORALBELLS","SLIVERDUSTPLANT"]):
            self.make_group('springwinter', (a, 3), f'acc_wild{i}')

        #Lifegen artist additions
        for a, i in enumerate(
            ["PURPLERAINCOAT", "BLUERAINCOAT", "GREENRAINCOAT", "PINKRAINCOAT", "REDRAINCOAT", "LIMERAINCOAT", "ORANGERAINCOAT"]):
            self.make_group('raincoats', (a, 0), f'acc_crafted{i}')
        for a, i in enumerate(
            ["YELLOWRAINCOAT"]):
            self.make_group('raincoats', (a, 1), f'acc_crafted{i}')

        for a, i in enumerate(
            ["WATTLE", "CORKHAT", "RAINBOWLORIKEET", "BILBY", "ZOOKEEPER"]):
            self.make_group('pocky1', (a, 0), f'acc_wild{i}')

        for a, i in enumerate(
            ["FAZBEAR","WHITEBEAR", "PANDA", "BEAR", "BROWNBEAR"]):
            self.make_group('misc_acc', (a, 0), f'acc_crafted{i}')
        for a, i in enumerate(
            ["EGG","POPTABS","BATHARNESS"]):
            self.make_group('misc_acc', (a, 1), f'acc_crafted{i}')

        for a, i in enumerate(
            ["TIDE","WOODDRAGON","TOAST", "TOASTBERRY", "TOASTGRAPE", "TOASTNUTELLA", "TOASTPB"]):
            self.make_group('reign1', (a, 0), f'acc_crafted{i}')
        for a, i in enumerate([
            "WINTERSTOAT", "BROWNSTOAT"]):
            self.make_group('reign1', (a, 1), f'acc_wild{i}')

        for a, i in enumerate([
            "CELESTIALCHIMES", "STARCHIMES", "LUNARCHIMES", "SILVERLUNARCHIMES"]):
            self.make_group('chimes', (a, 0), f'acc_crafted{i}')

        for a, i in enumerate([
            "FIDDLEHEADS", "LANTERNS", "HEARTCHARMS"]):
            self.make_group('moipa', (a, 0), f'acc_crafted{i}')

        for a, i in enumerate([
            "SPRINGFLOWERCORSAGE", "ORCHID", "SPRINGFLOWERS", "RADIO", "SWANFEATHER", "DRACULAPARROTFEATHER", "JAYFEATHER"]):
            self.make_group('moipa2', (a, 0), f'acc_flower{i}')
        for a, i in enumerate([
            "EAGLEFEATHER", "STARFLOWERS", "HEARTLEAVES", "YELLOWWISTERIA", "HOLLY2", "HOLLYVINES"]):
            self.make_group('moipa2', (a, 1), f'acc_wild{i}')
        for a, i in enumerate([
            "LAVENDERHEADPIECE", "LAVENDERTAILWRAP", "LAVENDERANKLET"]):
            self.make_group('moipa2', (a, 2), f'acc_wild{i}')
        
        # Define scars
        scars_data = [
            [
                "ONE",
                "TWO",
                "THREE",
                "MANLEG",
                "BRIGHTHEART",
                "MANTAIL",
                "BRIDGE",
                "RIGHTBLIND",
                "LEFTBLIND",
                "BOTHBLIND",
                "BURNPAWS",
                "BURNTAIL",
            ],
            [
                "BURNBELLY",
                "BEAKCHEEK",
                "BEAKLOWER",
                "BURNRUMP",
                "CATBITE",
                "RATBITE",
                "FROSTFACE",
                "FROSTTAIL",
                "FROSTMITT",
                "FROSTSOCK",
                "QUILLCHUNK",
                "QUILLSCRATCH",
            ],
            [
                "TAILSCAR",
                "SNOUT",
                "CHEEK",
                "SIDE",
                "THROAT",
                "TAILBASE",
                "BELLY",
                "TOETRAP",
                "SNAKE",
                "LEGBITE",
                "NECKBITE",
                "FACE",
            ],
            [
                "HINDLEG",
                "BACK",
                "QUILLSIDE",
                "SCRATCHSIDE",
                "TOE",
                "BEAKSIDE",
                "CATBITETWO",
                "SNAKETWO",
                "FOUR",
            ],
        ]

        # define missing parts
        missing_parts_data = [
            [
                "LEFTEAR",
                "RIGHTEAR",
                "NOTAIL",
                "NOLEFTEAR",
                "NORIGHTEAR",
                "NOEAR",
                "HALFTAIL",
                "NOPAW",
            ]
        ]

        # scars
        for row, scars in enumerate(scars_data):
            for col, scar in enumerate(scars):
                self.make_group("scars", (col, row), f"scars{scar}")

        # missing parts
        for row, missing_parts in enumerate(missing_parts_data):
            for col, missing_part in enumerate(missing_parts):
                self.make_group("missingscars", (col, row), f"scars{missing_part}")

        # accessories
        # to my beloved modders, im very sorry for reordering everything <333 -clay
        medcatherbs_data = [
            [
                "MAPLE LEAF",
                "HOLLY",
                "BLUE BERRIES",
                "FORGET ME NOTS",
                "RYE STALK",
                "CATTAIL",
                "POPPY",
                "ORANGE POPPY",
                "CYAN POPPY",
                "WHITE POPPY",
                "PINK POPPY",
            ],
            [
                "BLUEBELLS",
                "LILY OF THE VALLEY",
                "SNAPDRAGON",
                "HERBS",
                "PETALS",
                "NETTLE",
                "HEATHER",
                "GORSE",
                "JUNIPER",
                "RASPBERRY",
                "LAVENDER",
            ],
            [
                "OAK LEAVES",
                "CATMINT",
                "MAPLE SEED",
                "LAUREL",
                "BULB WHITE",
                "BULB YELLOW",
                "BULB ORANGE",
                "BULB PINK",
                "BULB BLUE",
                "CLOVER",
                "DAISY",
            ],
        ]
        dryherbs_data = [["DRY HERBS", "DRY CATMINT", "DRY NETTLES", "DRY LAURELS"]]
        wild_data = [
            [
                "RED FEATHERS",
                "BLUE FEATHERS",
                "JAY FEATHERS",
                "GULL FEATHERS",
                "SPARROW FEATHERS",
                "MOTH WINGS",
                "ROSY MOTH WINGS",
                "MORPHO BUTTERFLY",
                "MONARCH BUTTERFLY",
                "CICADA WINGS",
                "BLACK CICADA",
            ]
        ]

        collars_data = [
            ["CRIMSON", "BLUE", "YELLOW", "CYAN", "RED", "LIME"],
            ["GREEN", "RAINBOW", "BLACK", "SPIKES", "WHITE"],
            ["PINK", "PURPLE", "MULTI", "INDIGO"],
        ]

        bellcollars_data = [
            [
                "CRIMSONBELL",
                "BLUEBELL",
                "YELLOWBELL",
                "CYANBELL",
                "REDBELL",
                "LIMEBELL",
            ],
            ["GREENBELL", "RAINBOWBELL", "BLACKBELL", "SPIKESBELL", "WHITEBELL"],
            ["PINKBELL", "PURPLEBELL", "MULTIBELL", "INDIGOBELL"],
        ]

        bowcollars_data = [
            ["CRIMSONBOW", "BLUEBOW", "YELLOWBOW", "CYANBOW", "REDBOW", "LIMEBOW"],
            ["GREENBOW", "RAINBOWBOW", "BLACKBOW", "SPIKESBOW", "WHITEBOW"],
            ["PINKBOW", "PURPLEBOW", "MULTIBOW", "INDIGOBOW"],
        ]

        nyloncollars_data = [
            [
                "CRIMSONNYLON",
                "BLUENYLON",
                "YELLOWNYLON",
                "CYANNYLON",
                "REDNYLON",
                "LIMENYLON",
            ],
            ["GREENNYLON", "RAINBOWNYLON", "BLACKNYLON", "SPIKESNYLON", "WHITENYLON"],
            ["PINKNYLON", "PURPLENYLON", "MULTINYLON", "INDIGONYLON"],
        ]

        # medcatherbs
        for row, herbs in enumerate(medcatherbs_data):
            for col, herb in enumerate(herbs):
                self.make_group("medcatherbs", (col, row), f"acc_herbs{herb}")
        # dryherbs
        for row, dry in enumerate(dryherbs_data):
            for col, dryherbs in enumerate(dry):
                self.make_group("medcatherbs", (col, 3), f"acc_herbs{dryherbs}")
        # wild
        for row, wilds in enumerate(wild_data):
            for col, wild in enumerate(wilds):
                self.make_group("wild", (col, 0), f"acc_wild{wild}")

        # collars
        for row, collars in enumerate(collars_data):
            for col, collar in enumerate(collars):
                self.make_group("collars", (col, row), f"collars{collar}")

        # bellcollars
        for row, bellcollars in enumerate(bellcollars_data):
            for col, bellcollar in enumerate(bellcollars):
                self.make_group("bellcollars", (col, row), f"collars{bellcollar}")

        # bowcollars
        for row, bowcollars in enumerate(bowcollars_data):
            for col, bowcollar in enumerate(bowcollars):
                self.make_group("bowcollars", (col, row), f"collars{bowcollar}")

        # nyloncollars
        for row, nyloncollars in enumerate(nyloncollars_data):
            for col, nyloncollar in enumerate(nyloncollars):
                self.make_group("nyloncollars", (col, row), f"collars{nyloncollar}")

    def load_symbols(self):
        """
        loads clan symbols
        """

        if os.path.exists("resources/dicts/clan_symbols.json"):
            with open(
                "resources/dicts/clan_symbols.json", encoding="utf-8"
            ) as read_file:
                self.symbol_dict = ujson.loads(read_file.read())

        # U and X omitted from letter list due to having no prefixes
        letters = [
            "A",
            "B",
            "C",
            "D",
            "E",
            "F",
            "G",
            "H",
            "I",
            "J",
            "K",
            "L",
            "M",
            "N",
            "O",
            "P",
            "Q",
            "R",
            "S",
            "T",
            "V",
            "W",
            "Y",
            "Z",
        ]

        # sprite names will format as "symbol{PREFIX}{INDEX}", ex. "symbolSPRING0"
        y_pos = 1
        for letter in letters:
            x_mod = 0
            for i, symbol in enumerate(
                [
                    symbol
                    for symbol in self.symbol_dict
                    if letter in symbol and self.symbol_dict[symbol]["variants"]
                ]
            ):
                if self.symbol_dict[symbol]["variants"] > 1 and x_mod > 0:
                    x_mod += -1
                for variant_index in range(self.symbol_dict[symbol]["variants"]):
                    x_pos = i + x_mod

                    if self.symbol_dict[symbol]["variants"] > 1:
                        x_mod += 1
                    elif x_mod > 0:
                        x_pos += -1

                    self.clan_symbols.append(f"symbol{symbol.upper()}{variant_index}")
                    self.make_group(
                        "symbols",
                        (x_pos, y_pos),
                        f"symbol{symbol.upper()}{variant_index}",
                        sprites_x=1,
                        sprites_y=1,
                        no_index=True,
                    )

            y_pos += 1

    def get_symbol(self, symbol: str, force_light=False):
        """Change the color of the symbol to match the requested theme, then return it
        :param Surface symbol: The clan symbol to convert
        :param force_light: Use to ignore dark mode and always display the light mode color
        """
        symbol = self.sprites.get(symbol)
        if symbol is None:
            logger.warning("%s is not a known Clan symbol! Using default.")
            symbol = self.sprites[self.clan_symbols[0]]

        recolored_symbol = copy(symbol)
        var = pygame.PixelArray(recolored_symbol)
        var.replace(
            (87, 76, 45),
            pygame.Color(game.config["theme"]["dark_mode_clan_symbols"])
            if not force_light and game.settings["dark mode"]
            else pygame.Color(game.config["theme"]["light_mode_clan_symbols"]),
            distance=0.2,
        )
        del var

        return recolored_symbol


# CREATE INSTANCE
sprites = Sprites()
