import os
from copy import copy

import pygame
import ujson

from scripts.game_structure.game_essentials import game


class Sprites:
    cat_tints = {}
    white_patches_tints = {}
    clan_symbols = []

    def __init__(self):
        """Class that handles and hold all spritesheets. 
        Size is normally automatically determined by the size
        of the lineart. If a size is passed, it will override 
        this value. """
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
            with open("sprites/dicts/tint.json", 'r') as read_file:
                self.cat_tints = ujson.loads(read_file.read())
        except IOError:
            print("ERROR: Reading Tints")

        try:
            with open("sprites/dicts/white_patches_tint.json", 'r') as read_file:
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

    def make_group(self,
                   spritesheet,
                   pos,
                   name,
                   sprites_x=3,
                   sprites_y=7,
                   no_index=False):  # pos = ex. (2, 3), no single pixels

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
                        self.size, self.size
                    )

                except ValueError:
                    # Fallback for non-existent sprites
                    print(f"WARNING: nonexistent sprite - {full_name}")
                    if not self.blank_sprite:
                        self.blank_sprite = pygame.Surface(
                            (self.size, self.size),
                            pygame.HWSURFACE | pygame.SRCALPHA
                        )
                    new_sprite = self.blank_sprite

                self.sprites[full_name] = new_sprite
                i += 1

    def load_all(self):
        # get the width and height of the spritesheet
        lineart = pygame.image.load('sprites/lineart.png')
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
            print(f"if you are a modder, please update scripts/cat/sprites.py and "
                  f"do a search for 'if width / 3 == height / 7:'")

        del width, height  # unneeded

        for x in [
            'lineart', 'lineartdf', 'lineartdead', "lineartur",
            'eyes', 'eyes2', 
            'skin', 'gilltongue', 'beagilltongue', 'horns', 'fancyskin', 'whiskers', 'orbitals', 'datagamesstuff',
            'scars', 'missingscars',
            'medcatherbs',
            'collars', 'bellcollars', 'bowcollars', 'nyloncollars', 'rwlizards', 'drones', 'muddypaws', 
            'herbs2', 'insectwings', 'buddies', 'newaccs', 'bodypaint', 'implant', 'magic', 'necklaces',
            'newaccs2', 'drapery', 'eyepatches', 'pridedrapery', 'larsaccs', 'harleyaccs', 'newaccs3',
            'floatyeyes',
            'featherboas', 'scarves', 'chains', 'neckbandanas',
            'singlecolours', 'speckledcolours', 'tabbycolours', 'bengalcolours', 'marbledcolours',
            'rosettecolours', 'smokecolours', 'tickedcolours', 'mackerelcolours', 'classiccolours',
            'sokokecolours', 'agouticolours', 'singlestripecolours', 'maskedcolours', 'bananacolours',
            'centipedecolours', 'collaredcolours', 'concolours', 'gravelcolours', 'cyanlizardcolours',
            'slimemoldcolours', 'lanterncolours', 'vulturecolours', 'lizardcolours', 'leviathancolours',
            'fluffycolours', 'amoebacolours', 'seaslugcolours', 'yeekcolours', 'rustedcolours',
            'envoycolours', 'drizzlecolours', 'solacecolours', 'leafycolours', 'scaledcolours', 
            'dragonfruitcolours', 'necklacecolours', 'dreamercolours', 'duskdawncolours', 
            'seercolours', 'rottencolours', 'firecolours', 'countershadedcolours', 'cherrycolours',
            'oldgrowthcolours', 'sparklecatcolours', 'wolfcolours', 'sunsetcolours', 'hypnotistcolours',
            'ringedcolours', 'skinnycolours', 'sparsecolours', 'impishcolours', 'sportycolours', 
            'fizzycolours', 'skeletoncolours', 'shredcolours', 'glowingcolours', 'moldcolours',
            'swingcolours', 'lovebirdcolours', 'budgiecolours', 'amazoncolours', 'applecolours', 'bobacolours',
            'glittercolours', 'icecolours', 'iggycolours', 'manedcolours', 'patchworkcolours', 'robotcolours',
            'sunkencolours', 'tomocolours', 'whalecolours', 'pidgeoncolours',
            'raineyes', 'raineyes2', 'multieyes', 'multiraineyes', 'larseyes', 'multilarseyes', 'larseyes2', 
            'rivuleteyes', 'rivuleteyes2', 'buttoneyes', 'buttoneyes2',
            'shadersnewwhite', 'lightingnew',
            'whitepatches', 'tortiepatchesmasks',
            'fademask', 'fadestarclan', 'fadedarkforest',
            'symbols',
            #'lineart', 'lineartdf', 'lineartdead', "lineartur",
            #'eyes', 'eyes2', 'skin',
            #'scars', 'missingscars',
            #'medcatherbs', 'wild',
            #'collars', 'bellcollars', 'bowcollars', 'nyloncollars',
            #'singlecolours', 'speckledcolours', 'tabbycolours', 'bengalcolours', 'marbledcolours',
            #'rosettecolours', 'smokecolours', 'tickedcolours', 'mackerelcolours', 'classiccolours',
            #'sokokecolours', 'agouticolours', 'singlestripecolours', 'maskedcolours',
            #'shadersnewwhite', 'lightingnew',
            #'whitepatches', 'tortiepatchesmasks',
            #'fademask', 'fadestarclan', 'fadedarkforest',
            #'symbols',

            #OHDANS
            #'flower_accessories', 'plant2_accessories', 'snake_accessories', 'smallAnimal_accessories', 'deadInsect_accessories',
            #'aliveInsect_accessories', 'fruit_accessories', 'crafted_accessories', 'tail2_accessories',
#
            ###WILDS
            #'wildaccs_1', 'wildaccs_2',
#
            ###SUPERARTSI
            #'superartsi',
#
            ###coffee
            #'coffee','eragona','crowns','springwinter','raincoats','chimes','moipa','moipa2','pocky1','misc_acc','reign1'

        ]:
            if 'lineart' in x and game.config['fun']['april_fools']:
                self.spritesheet(f"sprites/aprilfools{x}.png", x)
            else:
                self.spritesheet(f"sprites/{x}.png", x)

        # Line art
        self.make_group('lineart', (0, 0), 'lines')
        self.make_group('shadersnewwhite', (0, 0), 'shaders')
        self.make_group('lightingnew', (0, 0), 'lighting')

        self.make_group('lineartdead', (0, 0), 'lineartdead')
        self.make_group('lineartdf', (0, 0), 'lineartdf')
        self.make_group('lineartur', (0, 0), 'lineartur')
        # Fading Fog
        for i in range(0, 3):
            self.make_group('fademask', (i, 0), f'fademask{i}')
            self.make_group('fadestarclan', (i, 0), f'fadestarclan{i}')
            self.make_group('fadedarkforest', (i, 0), f'fadedf{i}')

        # Define eye colors
        eye_colors = [
            ['YELLOW', 'AMBER', 'HAZEL', 'PALEGREEN', 'GREEN', 'BLUE', 'DARKBLUE', 'GREY', 'CYAN', 'EMERALD',
             'HEATHERBLUE', 'SUNLITICE'],
            ['COPPER', 'SAGE', 'COBALT', 'PALEBLUE', 'BRONZE', 'SILVER', 'PALEYELLOW', 'GOLD', 'GREENYELLOW',
             'RED', 'PURPLE', 'MAUVE']
        ]

        for row, colors in enumerate(eye_colors):
            for col, color in enumerate(colors):
                self.make_group('eyes', (col, row), f'eyes{color}')
                self.make_group('eyes2', (col, row), f'eyes2{color}')

        #rain's eyes
        for a, i in enumerate(
                ['ELECTRICBLUE', 'VIOLET', 'PINK', 'SNOW', 'ORANGE', 'CREAM', 'SEAFOAM', 'CRIMSON', 'NAVY', 'VOIDGOLD', 'COOLBROWN', 'PLUM']):
            self.make_group('raineyes', (a, 0), f'eyes{i}')
            self.make_group('raineyes2', (a, 0), f'eyes2{i}')
        for a, i in enumerate(
                ['INDIGO', 'LILAC']):
            self.make_group('raineyes', (a, 1), f'eyes{i}')
            self.make_group('raineyes2', (a, 1), f'eyes2{i}')
        #multieyes
        for a, i in enumerate(
                ['MULTIYELLOW', 'MULTIAMBER', 'MULTIHAZEL', 'MULTIPALEGREEN', 'MULTIGREEN', 'MULTIBLUE', 
                'MULTIDARKBLUE', 'MULTIGREY', 'MULTICYAN', 'MULTIEMERALD', 'MULTIHEATHERBLUE', 'MULTISUNLITICE']):
            self.make_group('multieyes', (a, 0), f'eyes2{i}')
        for a, i in enumerate(
                ['MULTICOPPER', 'MULTISAGE', 'MULTICOBALT', 'MULTIPALEBLUE', 'MULTIBRONZE', 'MULTISILVER',
                'MULTIPALEYELLOW', 'MULTIGOLD', 'MULTIGREENYELLOW', 'MULTIRED', 'MULTIPURPLE', 'MULTIMAUVE']):
            self.make_group('multieyes', (a, 1), f'eyes2{i}')
        #multieyes rain's colors
        for a, i in enumerate(
                ['MULTIELECTRICBLUE', 'MULTIVIOLET', 'MULTIPINK', 'MULTISNOW', 'MULTIORANGE',
                 'MULTICREAM', 'MULTISEAFOAM', 'MULTICRIMSON', 'MULTINAVY', 'MULTIVOIDGOLD',
                 'MULTICOOLBROWN', 'MULTIPLUM']):
            self.make_group('multiraineyes', (a, 0), f'eyes2{i}')
        for a, i in enumerate(
                ['MULTIINDIGO', 'MULTILILAC']):
            self.make_group('multiraineyes', (a, 1), f'eyes2{i}')

        #lars' eyes
        for a, i in enumerate(
                ['ALBA', 'ALBINO', 'ANGEL', 'APPLE', 'AQUA', 'ARID', 'BANANA', 'BLOOD', 'CARNI', 'CHAIN']):
            self.make_group('larseyes', (a, 0), f'eyes{i}')
            self.make_group('larseyes2', (a, 0), f'eyes2{i}')
        for a, i in enumerate(
                ['CREAMY', 'DAWN', 'ESES', 'EXILE', 'FAE', 'FALLSTAR', 'FIELD', 'FOAM', 'HOT', 'IRID']):
            self.make_group('larseyes', (a, 1), f'eyes{i}')
            self.make_group('larseyes2', (a, 1), f'eyes2{i}')
        for a, i in enumerate(
                ['KARMA', 'KIND', 'MARTI', 'MEISTALT', 'MHUNT', 'MELON', 'MESS', 'MEISTER', 'MINT', 'MINV']):
            self.make_group('larseyes', (a, 2), f'eyes{i}')
            self.make_group('larseyes2', (a, 2), f'eyes2{i}')
        for a, i in enumerate(
                ['MOON', 'MRIV', 'PEACH', 'PEBB', 'PELA', 'PEPPER', 'RETRO', 'RUNT', 'RUST', 'SIG']):
            self.make_group('larseyes', (a, 3), f'eyes{i}')
            self.make_group('larseyes2', (a, 3), f'eyes2{i}')
        for a, i in enumerate(
                ['SIXER', 'SPLIT', 'SUN', 'SWEET', 'TIDE', 'VIVID', 'WAVE', 'WINKS', 'ZENI', 'BEAST']):
            self.make_group('larseyes', (a, 4), f'eyes{i}')
            self.make_group('larseyes2', (a, 4), f'eyes2{i}')
        for a, i in enumerate(
                ['BROWNTBOI', 'ORANGETBOI', 'BREDTBOI', 'REDTBOI']):
            self.make_group('larseyes', (a, 5), f'eyes{i}')
            self.make_group('larseyes2', (a, 5), f'eyes2{i}')

        #lars' multi eyes
        for a, i in enumerate(
                ['MULTIALBA', 'MULTIALBINO', 'MULTIANGEL', 'MULTIAPPLE', 'MULTIAQUA', 'MULTIARID', 'MULTIBANANA', 'MULTIBLOOD', 'MULTICARNI', 'MULTICHAIN']):
            self.make_group('multilarseyes', (a, 0), f'eyes2{i}')
        for a, i in enumerate(
                ['MULTICREAMY', 'MULTIDAWN', 'MULTIESES', 'MULTIEXILE', 'MULTIFAE', 'MULTIFALLSTAR', 'MULTIFIELD', 'MULTIFOAM', 'MULTIHOT', 'MULTIIRID']):
            self.make_group('multilarseyes', (a, 1), f'eyes2{i}')
        for a, i in enumerate(
                ['MULTIKARMA', 'MULTIKIND', 'MULTIMARTI', 'MULTIMEISTALT', 'MULTIMHUNT', 'MULTIMELON', 'MULTIMESS', 'MULTIMEISTER', 'MULTIMINT', 'MULTIMINV']):
            self.make_group('multilarseyes', (a, 2), f'eyes2{i}')
        for a, i in enumerate(
                ['MULTIMOON', 'MULTIMRIV', 'MULTIPEACH', 'MULTIPEBB', 'MULTIPELA', 'MULTIPEPPER', 'MULTIRETRO', 'MULTIRUNT', 'MULTIRUST', 'MULTISIG']):
            self.make_group('multilarseyes', (a, 3), f'eyes2{i}')
        for a, i in enumerate(
                ['MULTISIXER', 'MULTISPLIT', 'MULTISUN', 'MULTISWEET', 'MULTITIDE', 'MULTIVIVID', 'MULTIWAVE', 'MULTIWINKS', 'MULTIZENI', 'MULTIBEAST']):
            self.make_group('multilarseyes', (a, 4), f'eyes2{i}')
        for a, i in enumerate(
                ['MULTIBROWNTBOI', 'MUTIORANGETBOI', 'MULTIBREDTBOI', 'MULTIREDTBOI']):
            self.make_group('multilarseyes', (a, 5), f'eyes2{i}')
                    
        #rivulet eyes
        for a, i in enumerate(
                ['RIVYELLOW', 'RIVAMBER', 'RIVHAZEL', 'RIVPALEGREEN', 'RIVGREEN', 'RIVBLUE', 
                'RIVDARKBLUE', 'RIVGREY', 'RIVCYAN', 'RIVEMERALD', 'RIVHEATHERBLUE', 'RIVSUNLITICE']):
            self.make_group('rivuleteyes', (a, 0), f'eyes{i}')
            self.make_group('rivuleteyes2', (a, 0), f'eyes2{i}')
        for a, i in enumerate(
                ['RIVCOPPER', 'RIVSAGE', 'RIVCOBALT', 'RIVPALEBLUE', 'RIVBRONZE', 'RIVSILVER',
                'RIVPALEYELLOW', 'RIVGOLD', 'RIVGREENYELLOW']):
            self.make_group('rivuleteyes', (a, 1), f'eyes{i}')
            self.make_group('rivuleteyes2', (a, 1), f'eyes2{i}')

        #button eyes
        for a, i in enumerate(
                ['BUTTONYELLOW', 'BUTTONAMBER', 'BUTTONHAZEL', 'BUTTONPALEGREEN', 'BUTTONGREEN', 'BUTTONBLUE', 
                'BUTTONDARKBLUE', 'BUTTONGREY', 'BUTTONCYAN', 'BUTTONEMERALD', 'BUTTONHEATHERBLUE', 'BUTTONSUNLITICE']):
            self.make_group('buttoneyes', (a, 0), f'eyes{i}')
            self.make_group('buttoneyes2', (a, 0), f'eyes2{i}')
        for a, i in enumerate(
                ['BUTTONCOPPER', 'BUTTONSAGE', 'BUTTONCOBALT', 'BUTTONPALEBLUE', 'BUTTONBRONZE', 'BUTTONSILVER',
                'BUTTONPALEYELLOW', 'BUTTONGOLD', 'BUTTONGREENYELLOW', 'BUTTONIRED', 'BUTTONPURPLE', 'BUTTONMAUVE']):
            self.make_group('buttoneyes', (a, 1), f'eyes{i}')
            self.make_group('buttoneyes2', (a, 1), f'eyes2{i}')
        for a, i in enumerate(
                ['BUTTONINDIGO', 'BUTTONLILAC']):
            self.make_group('buttoneyes', (a, 2), f'eyes{i}')
            self.make_group('buttoneyes2', (a, 2), f'eyes2{i}')

        # Define white patches
        white_patches = [
            ['FULLWHITE', 'ANY', 'TUXEDO', 'LITTLE', 'COLOURPOINT', 'VAN', 'ANYTWO', 'MOON', 'PHANTOM', 'POWDER',
             'BLEACHED', 'SAVANNAH', 'FADESPOTS', 'PEBBLESHINE'],
            ['EXTRA', 'ONEEAR', 'BROKEN', 'LIGHTTUXEDO', 'BUZZARDFANG', 'RAGDOLL', 'LIGHTSONG', 'VITILIGO', 'BLACKSTAR',
             'PIEBALD', 'CURVED', 'PETAL', 'SHIBAINU', 'OWL'],
            ['TIP', 'FANCY', 'FRECKLES', 'RINGTAIL', 'HALFFACE', 'PANTSTWO', 'GOATEE', 'VITILIGOTWO', 'PAWS', 'MITAINE',
             'BROKENBLAZE', 'SCOURGE', 'DIVA', 'BEARD'],
            ['TAIL', 'BLAZE', 'PRINCE', 'BIB', 'VEE', 'UNDERS', 'HONEY', 'FAROFA', 'DAMIEN', 'MISTER', 'BELLY',
             'TAILTIP', 'TOES', 'TOPCOVER'],
            ['APRON', 'CAPSADDLE', 'MASKMANTLE', 'SQUEAKS', 'STAR', 'TOESTAIL', 'RAVENPAW', 'PANTS', 'REVERSEPANTS',
             'SKUNK', 'KARPATI', 'HALFWHITE', 'APPALOOSA', 'DAPPLEPAW'],
            ['HEART', 'LILTWO', 'GLASS', 'MOORISH', 'SEPIAPOINT', 'MINKPOINT', 'SEALPOINT', 'MAO', 'LUNA', 'CHESTSPECK',
             'WINGS', 'PAINTED', 'HEARTTWO', 'WOODPECKER'],
            ['BOOTS', 'MISS', 'COW', 'COWTWO', 'BUB', 'BOWTIE', 'MUSTACHE', 'REVERSEHEART', 'SPARROW', 'VEST',
             'LOVEBUG', 'TRIXIE', 'SAMMY', 'SPARKLE'],
            ['RIGHTEAR', 'LEFTEAR', 'ESTRELLA', 'SHOOTINGSTAR', 'EYESPOT', 'REVERSEEYE', 'FADEBELLY', 'FRONT',
             'BLOSSOMSTEP', 'PEBBLE', 'TAILTWO', 'BUDDY', 'BACKSPOT', 'EYEBAGS'],
            ['BULLSEYE', 'FINN', 'DIGIT', 'KROPKA', 'FCTWO', 'FCONE', 'MIA', 'SCAR', 'BUSTER', 'SMOKEY', 'HAWKBLAZE',
             'CAKE', 'ROSINA', 'PRINCESS'],
            ['LOCKET', 'BLAZEMASK', 'TEARS', 'DOUGIE', 'BALLER', 'PAINTSPLAT', 'REVERSETEARS', 'ELDER', 'TREFOIL',
             'MANUL', 'REVERSETEARSTWO', 'GLOVE', 'REVERSENECK', 'NECK'],
            ['REVERSEHEAD', 'HEAD', 'DOTS', 'SPARSE', 'BADGER', 'FIVEPEBBLE', 'BELLY', 'CHARCOAL', 'MASK', 'LIGHTNING',
             'SIAMESE', 'FROSTBITTEN', 'HEX', 'SNOWBELLY'],
            ['LIMBS', 'STRIPES', 'GLOWSTAR', 'STAR', 'SLICE', 'DEADPIXEL', 'ESCAPEE', 'INSPECTOR', 'FACEDOTS', 'TOONY',
             'ACROBAT', 'WPTEARS', 'ONEEARTIP', 'NOSETIP']
        ]

        for row, patches in enumerate(white_patches):
            for col, patch in enumerate(patches):
                self.make_group('whitepatches', (col, row), f'white{patch}')

        # Define colors and categories
        color_categories = [
            ['WHITE', 'PALEGREY', 'SILVER', 'GREY', 'DARKGREY', 'GHOST', 'BLACK'],
            ['CREAM', 'PALEGINGER', 'GOLDEN', 'GINGER', 'DARKGINGER', 'SIENNA'],
            ['LIGHTBROWN', 'LILAC', 'BROWN', 'GOLDEN-BROWN', 'DARKBROWN', 'CHOCOLATE']
        ]

        color_types = [
            'singlecolours', 'speckledcolours', 'tabbycolours', 'bengalcolours', 'marbledcolours',
            'rosettecolours', 'smokecolours', 'tickedcolours', 'mackerelcolours', 'classiccolours',
            'sokokecolours', 'agouticolours', 'singlestripecolours', 'maskedcolours', 'bananacolours',
            'centipedecolours', 'collaredcolours', 'concolours', 'gravelcolours', 'cyanlizardcolours',
            'slimemoldcolours', 'lanterncolours', 'vulturecolours', 'lizardcolours', 'leviathancolours',
            'fluffycolours', 'amoebacolours', 'seaslugcolours', 'yeekcolours', 'rustedcolours',
            'envoycolours', 'drizzlecolours', 'solacecolours', 'leafycolours', 'scaledcolours', 
            'dragonfruitcolours', 'necklacecolours', 'dreamercolours', 'duskdawncolours', 
            'seercolours', 'rottencolours', 'firecolours', 'countershadedcolours', 'cherrycolours',
            'oldgrowthcolours', 'sparklecatcolours', 'wolfcolours', 'sunsetcolours', 'hypnotistcolours',
            'ringedcolours', 'skinnycolours', 'sparsecolours', 'impishcolours', 'sportycolours', 
            'fizzycolours', 'skeletoncolours', 'shredcolours', 'glowingcolours', 'moldcolours',
            'swingcolours', 'lovebirdcolours', 'budgiecolours', 'amazoncolours', 'applecolours', 'bobacolours',
            'glittercolours', 'icecolours', 'iggycolours', 'manedcolours', 'patchworkcolours', 'robotcolours',
            'sunkencolours', 'tomocolours', 'whalecolours', 'pidgeoncolours',
        ]

        for row, colors in enumerate(color_categories):
            for col, color in enumerate(colors):
                for color_type in color_types:
                    self.make_group(color_type, (col, row), f'{color_type[:-7]}{color}')

        # tortiepatchesmasks
        tortiepatchesmasks = [
            ['ONE', 'TWO', 'THREE', 'FOUR', 'REDTAIL', 'DELILAH', 'HALF', 'STREAK', 'MASK', 'SMOKE'],
            ['MINIMALONE', 'MINIMALTWO', 'MINIMALTHREE', 'MINIMALFOUR', 'OREO', 'SWOOP', 'CHIMERA', 'CHEST', 'ARMTAIL',
             'GRUMPYFACE'],
            ['MOTTLED', 'SIDEMASK', 'EYEDOT', 'BANDANA', 'PACMAN', 'STREAMSTRIKE', 'SMUDGED', 'DAUB', 'EMBER', 'BRIE'],
            ['ORIOLE', 'ROBIN', 'BRINDLE', 'PAIGE', 'ROSETAIL', 'SAFI', 'DAPPLENIGHT', 'BLANKET', 'BELOVED', 'BODY'],
            ['SHILOH', 'FRECKLED', 'HEARTBEAT', 'SPECKLES', 'TIGER']
        ]

        for row, masks in enumerate(tortiepatchesmasks):
            for col, mask in enumerate(masks):
                self.make_group('tortiepatchesmasks', (col, row), f"tortiemask{mask}")

        # Empty skin
        for a, i in enumerate(['BLACK', 'PINK', 'DARKBROWN', 'BROWN', 'LIGHTBROWN', "RED"]):
            self.make_group('skin', (a, 0), f"skin{i}")
        for a, i in enumerate(['DARK', 'DARKGREY', 'GREY', 'DARKSALMON', 'SALMON', 'PEACH']):
            self.make_group('skin', (a, 1), f"skin{i}")
        for a, i in enumerate(['DARKMARBLED', 'MARBLED', 'LIGHTMARBLED', 'DARKBLUE', 'BLUE', 'LIGHTBLUE']):
            self.make_group('skin', (a, 2), f"skin{i}")

        # Gills, Tongues, Quills
        for a, i in enumerate(['PINKGILLS', 'BLUEGILLS', 'REDGILLS', 'LIMEGILLS', 'YELLOWGILLS', 'WHITEGILLS']):
            self.make_group('gilltongue', (a, 0), f"skin{i}")
        for a, i in enumerate(['RAINBOWGILLS', 'FUCHSIATONGUE', 'PASTELTONGUE', 'KOBITONGUE', 'REDTONGUE', 'GREYTONGUE']):
                self.make_group('gilltongue', (a, 1), f"skin{i}")
        for a, i in enumerate(['ORANGETONGUE', 'WHITESPOTS', 'BLACKSPOTS', 'MIXSPOTS', 'RAINBOWSPOTS', 'BLACKCLAWS']):
            self.make_group('gilltongue', (a, 2), f"skin{i}")
        if game.settings["bea_gilltongue"]:
            for a, i in enumerate(['WHITETENNA', 'REDTENNA', 'PINKTENNA', 'ORANGETENNA', 'YELLOWTENNA', 'BLUETENNA']):
                self.make_group('beagilltongue', (a, 3), f"skin{i}")
            for a, i in enumerate(['GREENTENNA', 'WHITEGLOWSPOTS', 'REDGLOWSPOTS', 'PINKGLOWSPOTS', 'ORANGEGLOWSPOTS', 'YELLOWGLOWSPOTS']):
                self.make_group('beagilltongue', (a, 4), f"skin{i}")
            for a, i in enumerate(['BLUEGLOWSPOTS', 'GREENGLOWSPOTS', 'GRAYGILLS', 'HOTGILLS', 'COLDGILLS']):
                self.make_group('beagilltongue', (a, 5), f"skin{i}")
        else:
            for a, i in enumerate(['WHITETENNA', 'REDTENNA', 'PINKTENNA', 'ORANGETENNA', 'YELLOWTENNA', 'BLUETENNA']):
                self.make_group('gilltongue', (a, 3), f"skin{i}")
            for a, i in enumerate(['GREENTENNA', 'WHITEGLOWSPOTS', 'REDGLOWSPOTS', 'PINKGLOWSPOTS', 'ORANGEGLOWSPOTS', 'YELLOWGLOWSPOTS']):
                self.make_group('gilltongue', (a, 4), f"skin{i}")
            for a, i in enumerate(['BLUEGLOWSPOTS', 'GREENGLOWSPOTS', 'GRAYGILLS', 'HOTGILLS', 'COLDGILLS']):
                self.make_group('gilltongue', (a, 5), f"skin{i}")

        # Horns
        for a, i in enumerate(['WHITEHORNSRAM', 'BLACKHORNSRAM', 'REDHORNSRAM', 'YELLOWHORNSRAM', 'GREENHORNSRAM', 'BLUEHORNSRAM', 'ORANGEHORNSRAM', 'BROWNHORNSRAM']):
            self.make_group('horns', (a, 0), f"skin{i}")
        for a, i in enumerate(['WHITEHORNSSCAV', 'BLACKHORNSSCAV', 'REDHORNSSCAV', 'YELLOWHORNSSCAV', 'GREENHORNSSCAV', 'BLUEHORNSSCAV', 'ORANGEHORNSSCAV', 'BROWNHORNSSCAV']):
            self.make_group('horns', (a, 1), f"skin{i}")
        for a, i in enumerate(['WHITEHORNSELITE', 'BLACKHORNSELITE', 'REDHORNSELITE', 'YELLOWHORNSELITE', 'GREENHORNSELITE', 'BLUEHORNSELITE', 'ORANGEHORNSELITE', 'BROWNHORNSELITE']):
            self.make_group('horns', (a, 2), f"skin{i}")
        for a, i in enumerate(['WHITEHORNSSHARP', 'BLACKHORNSSHARP', 'REDHORNSSHARP', 'YELLOWHORNSSHARP', 'GREENHORNSSHARP', 'BLUEHORNSSHARP', 'ORANGEHORNSSHARP', 'BROWNHORNSSHARP']):
            self.make_group('horns', (a, 3), f"skin{i}")
        for a, i in enumerate(['WHITEHORNSDRAGON', 'BLACKHORNSDRAGON', 'REDHORNSDRAGON', 'YELLOWHORNSDRAGON', 'GREENHORNSDRAGON', 'BLUEHORNSDRAGON', 'ORANGEHORNSDRAGON', 'BROWNHORNSDRAGON']):
            self.make_group('horns', (a, 4), f"skin{i}")
        for a, i in enumerate(['WHITEHORNSLANCER', 'BLACKHORNSLANCER', 'REDHORNSLANCER', 'YELLOWHORNSLANCER', 'GREENHORNSLANCER', 'BLUEHORNSLANCER', 'ORANGEHORNSLANCER', 'BROWNHORNSLANCER']):
            self.make_group('horns', (a, 5), f"skin{i}")
            
        # Whiskers
        for a, i in enumerate(['WHITECATFISHWHISKERS', 'PINKCATFISHWHISKERS', 'REDCATFISHWHISKERS', 'YELLOWCATFISHWHISKERS', 'GREENCATFISHWHISKERS', 'REDYELLOWCATFISHWHISKERS']):
            self.make_group('whiskers', (a, 0), f"skin{i}")
        for a, i in enumerate(['BLUECATFISHWHISKERS', 'PURPLECATFISHWHISKERS', 'BLACKCATFISHWHISKERS', 'BLUEGREENCATFISHWHISKERS', 'BLUEPINKCATFISHWHISKERS', 'BROWNCATFISHWHISKERS']):
            self.make_group('whiskers', (a, 1), f"skin{i}")
        for a, i in enumerate(['WHITEDRAGONWHISKERS', 'PINKDRAGONWHISKERS', 'REDDRAGONWHISKERS', 'YELLOWDRAGONWHISKERS', 'GREENDRAGONWHISKERS', 'REDYELLOWDRAGONWHISKERS']):
            self.make_group('whiskers', (a, 2), f"skin{i}")
        for a, i in enumerate(['BLUEDRAGONWHISKERS', 'PURPLEDRAGONWHISKERS', 'BLACKDRAGONWHISKERS', 'BLUEGREENDRAGONWHISKERS', 'BLUEPINKDRAGONWHISKERS', 'BROWNDRAGONWHISKERS']):
            self.make_group('whiskers', (a, 3), f"skin{i}")

        # fancyskin spritesheet
        for a, i in enumerate(['WHITEMOTH', 'BLACKMOTH', 'REDMOTH', 'YELLOWMOTH', 'GREENMOTH', 'BLUEMOTH', 'ORANGEMOTH', 'BROWNMOTH']):
            self.make_group('fancyskin', (a, 0), f"skin{i}")
        for a, i in enumerate(['WHITEWHISKERS', 'BLACKWHISKERS', 'REDWHISKERS', 'YELLOWWHISKERS', 'GREENWHISKERS', 'BLUEWHISKERS', 'ORANGEWHISKERS', 'BROWNWHISKERS']):
            self.make_group('fancyskin', (a, 1), f"skin{i}")
        for a, i in enumerate(['PINKFINS', 'BLUEFINS', 'REDFINS', 'GREENFINS', 'YELLOWFINS', 'WHITEFINS', 'BLACKNEEDLES', 'WHITENEEDLES']):
            self.make_group('fancyskin', (a, 2), f"skin{i}")
        for a, i in enumerate(['WHITECYAN', 'ORANGECYAN', 'BROWNCYAN', 'PINKCYAN', 'PINKERCYAN', 'TEALCYAN', 'GREENCYAN', 'BLOODYCYAN']):
            self.make_group('fancyskin', (a, 3), f"skin{i}")
        for a, i in enumerate(['LAVENDERCYAN', 'PURPLECYAN', 'CYANCYAN', 'BLUECYAN', 'DARKBLUECYAN', 'DARKPURPLECYAN', 'BLACKCYAN', 'EGGCYAN']):
            self.make_group('fancyskin', (a, 4), f"skin{i}")
        for a, i in enumerate(['YELLOWCYAN', 'RAINBOWNEEDLES', 'CYANWINGS', 'ANGLERFISH', 'FIREBUGPART', 'TEARS', 'BLACKTHORNS', 'WHITETHORNS']):
            self.make_group('fancyskin', (a, 5), f"skin{i}")
        for a, i in enumerate(['GLASSBACK', 'SEASLUGPAPILLAE', 'GRASSSHEEPBACK', 'SEAANGELWINGS', 'ACROTAIL']):
            self.make_group('fancyskin', (a, 6), f"skin{i}")

        # data games stuff spritesheet
        for a, i in enumerate(['FAMILIARMARK', 'BLUETAILFRILLS', 'ORANGETAILFRILLS', 'GREENTAILFRILLS', 'PURPLETAILFRILLS']):
            self.make_group('datagamesstuff', (a, 0), f"skin{i}")
        for a, i in enumerate(['PINKTAILFRILLS', 'REDTAILFRILLS', 'YELLOWTAILFRILLS', 'CYANTAILFRILLS', 'WHITEQUILLS']):
            self.make_group('datagamesstuff', (a, 1), f"skin{i}")
        for a, i in enumerate(['BLACKQUILLS', 'YELLOWSPIKES', 'GREENSPIKES', 'AQUASPIKES', 'CYANSPIKES']):
            self.make_group('datagamesstuff', (a, 2), f"skin{i}")
        for a, i in enumerate(['BLUESPIKES', 'PURPLESPIKES', 'PINKSPIKES', 'REDSPIKES', 'ORANGESPIKES']):
            self.make_group('datagamesstuff', (a, 3), f"skin{i}")

        self.load_scars()
        self.load_symbols()

    def load_scars(self):
        """
        Loads scar sprites and puts them into groups.
        """

            # ohdan's accessories
        #for a, i in enumerate([
        #    "DAISIES", "DIANTHUS", "BLEEDING HEARTS", "FRANGIPANI", "BLUE GLORY", "CATNIP FLOWER", "BLANKET FLOWER", "ALLIUM", "LACELEAF", "PURPLE GLORY"]):
        #    self.make_group('flower_accessories', (a, 0), f'acc_flower{i}')
        #for a, i in enumerate([
        #    "YELLOW PRIMROSE", "HESPERIS", "MARIGOLD", "WISTERIA"]):
        #    self.make_group('flower_accessories', (a, 1), f'acc_flower{i}')
        #
        #for a, i in enumerate([
        #    "SINGULARCLOVER", "STICK", "PUMPKIN", "MOSS", "IVY", "ACORN", "MOSS PELT", "REEDS", "BAMBOO"]):
        #    self.make_group('plant2_accessories', (a, 0), f'acc_plant2{i}')
#
        #for a, i in enumerate([
        #    "GRASS SNAKE", "BLUE RACER", "WESTERN COACHWHIP", "KINGSNAKE"]):
        #    self.make_group('snake_accessories', (a, 0), f'acc_snake{i}')
        #    
        #for a, i in enumerate([
        #    "GRAY SQUIRREL", "RED SQUIRREL", "CRAB", "WHITE RABBIT", "BLACK RABBIT", "BROWN RABBIT", "INDIAN GIANT SQUIRREL", "FAWN RABBIT", "BROWN AND WHITE RABBIT", "BLACK AND WHITE RABBIT"]):
        #    self.make_group('smallAnimal_accessories', (a, 0), f'acc_smallAnimal{i}')
        #for a, i in enumerate([
        #    "WHITE AND FAWN RABBIT", "BLACK VITILIGO RABBIT", "BROWN VITILIGO RABBIT", "FAWN VITILIGO RABBIT", "BLACKBIRD", "ROBIN", "JAY", "THRUSH", "CARDINAL", "MAGPIE"]):
        #    self.make_group('smallAnimal_accessories', (a, 1), f'acc_smallAnimal{i}')
        #for a, i in enumerate([
        #    "CUBAN TROGON", "TAN RABBIT", "TAN AND WHITE RABBIT", "TAN VITILIGO RABBIT", "RAT", "WHITE MOUSE", "BLACK MOUSE", "GRAY MOUSE", "BROWN MOUSE", "GRAY RABBIT"]):
        #    self.make_group('smallAnimal_accessories', (a, 2), f'acc_smallAnimal{i}')
        #for a, i in enumerate([
        #    "GRAY AND WHITE RABBIT", "GRAY VITILIGO RABBIT"]):
        #    self.make_group('smallAnimal_accessories', (a, 3), f'acc_smallAnimal{i}')
        #    
        #for a, i in enumerate([
        #    "LUNAR MOTH", "ROSY MAPLE MOTH", "MONARCH", "DAPPLED MONARCH", "POLYPHEMUS MOTH", "MINT MOTH"]):
        #    self.make_group('deadInsect_accessories', (a, 0), f'acc_deadInsect{i}')
        #    
        #for a, i in enumerate([
        #    "BROWN SNAIL", "RED SNAIL", "WORM", "BLUE SNAIL", "ZEBRA ISOPOD", "DUCKY ISOPOD", "DAIRY COW ISOPOD", "BEETLEJUICE ISOPOD", "BEE", "RED LADYBUG"]):
        #    self.make_group('aliveInsect_accessories', (a, 0), f'acc_aliveInsect{i}')
        #for a, i in enumerate([
        #    "ORANGE LADYBUG", "YELLOW LADYBUG"]):
        #    self.make_group('aliveInsect_accessories', (a, 1), f'acc_aliveInsect{i}')
        #
        #for a, i in enumerate([
        #    "RASPBERRY2", "BLACKBERRY", "GOLDEN RASPBERRY", "CHERRY", "YEW"]):
        #    self.make_group('fruit_accessories', (a, 0), f'acc_fruit{i}')
        #
        #for a, i in enumerate([
        #    "WILLOWBARK BAG", "CLAY DAISY POT", "CLAY AMANITA POT", "CLAY BROWNCAP POT", "BIRD SKULL", "LEAF BOW"]):
        #    self.make_group('crafted_accessories', (a, 0), f'acc_crafted{i}')
        #
        #for a, i in enumerate([
        #    "SEAWEED", "DAISY CORSAGE"]):
        #    self.make_group('tail2_accessories', (a, 0), f'acc_tail2{i}')
#
#
        ## wilds accessories redone sheets by moipa and jay
        #for a, i in enumerate([
        #    "LILYPAD", "LARGE DEATHBERRY", "SMALL DEATHBERRY", "ACORN2", "PINECONE", "VINE"]):
        #    self.make_group('wildaccs_1', (a, 0), f'acc_herbs{i}')
        #
        #for a, i in enumerate([
        #    "CHERRY2", "BLEEDING HEARTS2", "SHELL PACK", "FERNS", "GOLD FERNS"]):
        #    self.make_group('wildaccs_1', (a, 1), f'acc_herbs{i}')
#
        #for a, i in enumerate([
        #    "WHEAT", "BLACK WHEAT"]):
        #    self.make_group('wildaccs_1', (a, 2), f'acc_herbs{i}')
        #
        ## -------------------------------------------------------------------------
        #
        #for a, i in enumerate([
        #    "BERRIES", "CLOVERS", "CLOVER2", "MOSS2", "FLOWER MOSS", "MUSHROOMS"]):
        #    self.make_group('wildaccs_2', (a, 0), f'acc_herbs{i}')
#
        #for a, i in enumerate([
        #    "LARGE LUNA", "LARGE COMET", "SMALL LUNA", "SMALL COMET", "LADYBUG"]):
        #    self.make_group('wildaccs_2', (a, 1), f'acc_wild{i}')
#
        #for a, i in enumerate([
        #    "MUD PAWS", "ASHY PAWS"]):
        #    self.make_group('wildaccs_2', (a, 2), f'acc_wild{i}')
#
        ## superartsi's accessories
#
        #for a, i in enumerate([
        #    "ORANGEBUTTERFLY", "BLUEBUTTERFLY", "BROWNPELT", "GRAYPELT", "BROWNMOSSPELT", "GRAYMOSSPELT"]):
        #    self.make_group('superartsi', (a, 0), f'acc_wild{i}')
        #for a, i in enumerate([
        #    "FERN", "MOREFERN", "BLEEDINGVINES", "BLEEDINGHEART", "LILY"]):
        #    self.make_group('superartsi', (a, 1), f'acc_wild{i}')
#
        ## coffee's accessories
        #for a, i in enumerate([
        #    "PINKFLOWERCROWN", "YELLOWFLOWERCROWN", "BLUEFLOWERCROWN", "PURPLEFLOWERCROWN"]):
        #    self.make_group('coffee', (a, 0), f'acc_flower{i}')
#
        ## eragona rose's accessories
#
        #for a, i in enumerate([
        #    "REDHARNESS", "NAVYHARNESS", "YELLOWHARNESS", "TEALHARNESS", "ORANGEHARNESS", "GREENHARNESS"]):
        #    self.make_group('eragona', (a, 0), f'collars{i}')
        #for a, i in enumerate([
        #    "MOSSHARNESS", "RAINBOWHARNESS", "BLACKHARNESS", "BEEHARNESS", "CREAMHARNESS"]):
        #    self.make_group('eragona', (a, 1), f'collars{i}')
        #for a, i in enumerate([
        #    "PINKHARNESS", "MAGENTAHARNESS", "PEACHHARNESS", "VIOLETHARNESS"]):
        #    self.make_group('eragona', (a, 2), f'collars{i}')
#
        #for a, i in enumerate([
        #    "YELLOWCROWN", "REDCROWN", "LILYPADCROWN"]):
        #    self.make_group('crowns', (a, 0), f'acc_wild{i}')
#
#
        #for a, i in enumerate(["CHERRYBLOSSOM","TULIPPETALS","CLOVERFLOWER","PANSIES","BELLFLOWERS","SANVITALIAFLOWERS","EGGSHELLS","BLUEEGGSHELLS","EASTEREGG","FORSYTHIA"]):
        #    self.make_group('springwinter', (a, 0), f'acc_wild{i}')
        #for a, i in enumerate([
        #    "MINTLEAF","STICKS","SPRINGFEATHERS","SNAILSHELL","MUD","CHERRYPLUMLEAVES","CATKIN","HONEYCOMB","FLOWERCROWN","LILIESOFTHEVALLEY"]):
        #    self.make_group('springwinter', (a, 1), f'acc_wild{i}')
        #for a, i in enumerate([
        #    "STRAWMANE","MISTLETOE","REDPOINSETTIA","WHITEPOINSETTIA","COTONEASTERWREATH","YEWS","CALLUNA","TEETHCOLLAR","DRIEDORANGE","ROESKULL"]):
        #    self.make_group('springwinter', (a, 2), f'acc_wild{i}')
        #for a, i in enumerate([
        #    "WOODENOAKANTLERS","WOODENBIRCHANTLERS","DOGWOOD","GRAYWOOL","BLACKWOOL","CREAMWOOL","WHITEWOOL","FIRBRANCHES","CORALBELLS","SLIVERDUSTPLANT"]):
        #    self.make_group('springwinter', (a, 3), f'acc_wild{i}')
#
        ##Lifegen artist additions
        #for a, i in enumerate(
        #    ["PURPLERAINCOAT", "BLUERAINCOAT", "GREENRAINCOAT", "PINKRAINCOAT", "REDRAINCOAT", "LIMERAINCOAT", "ORANGERAINCOAT"]):
        #    self.make_group('raincoats', (a, 0), f'acc_crafted{i}')
        #for a, i in enumerate(
        #    ["YELLOWRAINCOAT"]):
        #    self.make_group('raincoats', (a, 1), f'acc_crafted{i}')
#
        #for a, i in enumerate(
        #    ["WATTLE", "CORKHAT", "RAINBOWLORIKEET", "BILBY", "ZOOKEEPER"]):
        #    self.make_group('pocky1', (a, 0), f'acc_wild{i}')
#
        #for a, i in enumerate(
        #    ["FAZBEAR","WHITEBEAR", "PANDA", "BEAR", "BROWNBEAR"]):
        #    self.make_group('misc_acc', (a, 0), f'acc_crafted{i}')
        #for a, i in enumerate(
        #    ["EGG","POPTABS","BATHARNESS"]):
        #    self.make_group('misc_acc', (a, 1), f'acc_crafted{i}')
#
        #for a, i in enumerate(
        #    ["TIDE","WOODDRAGON","TOAST", "TOASTBERRY", "TOASTGRAPE", "TOASTNUTELLA", "TOASTPB"]):
        #    self.make_group('reign1', (a, 0), f'acc_crafted{i}')
        #for a, i in enumerate([
        #    "WINTERSTOAT", "BROWNSTOAT"]):
        #    self.make_group('reign1', (a, 1), f'acc_wild{i}')
#
        #for a, i in enumerate([
        #    "CELESTIALCHIMES", "STARCHIMES", "LUNARCHIMES", "SILVERLUNARCHIMES"]):
        #    self.make_group('chimes', (a, 0), f'acc_crafted{i}')
#
        #for a, i in enumerate([
        #    "FIDDLEHEADS", "LANTERNS", "HEARTCHARMS"]):
        #    self.make_group('moipa', (a, 0), f'acc_crafted{i}')
#
        #for a, i in enumerate([
        #    "SPRINGFLOWERCORSAGE", "ORCHID", "SPRINGFLOWERS", "RADIO", "SWANFEATHER", "DRACULAPARROTFEATHER", "JAYFEATHER"]):
        #    self.make_group('moipa2', (a, 0), f'acc_flower{i}')
        #for a, i in enumerate([
        #    "EAGLEFEATHER", "STARFLOWERS", "HEARTLEAVES", "YELLOWWISTERIA", "HOLLY2", "HOLLYVINES"]):
        #    self.make_group('moipa2', (a, 1), f'acc_wild{i}')
        #for a, i in enumerate([
        #    "LAVENDERHEADPIECE", "LAVENDERTAILWRAP", "LAVENDERANKLET"]):
        #    self.make_group('moipa2', (a, 2), f'acc_wild{i}')
        
        # Define scars
        scars_data = [
            ["ONE", "TWO", "THREE", "MANLEG", "BRIGHTHEART", "MANTAIL", "BRIDGE", "RIGHTBLIND", "LEFTBLIND",
             "BOTHBLIND", "BURNPAWS", "BURNTAIL"],
            ["BURNBELLY", "BEAKCHEEK", "BEAKLOWER", "BURNRUMP", "CATBITE", "RATBITE", "FROSTFACE", "FROSTTAIL",
             "FROSTMITT", "FROSTSOCK", "QUILLCHUNK", "QUILLSCRATCH"],
            ["TAILSCAR", "SNOUT", "CHEEK", "SIDE", "THROAT", "TAILBASE", "BELLY", "TOETRAP", "SNAKE", "LEGBITE",
             "NECKBITE", "FACE"],
            ["HINDLEG", "BACK", "QUILLSIDE", "SCRATCHSIDE", "TOE", "BEAKSIDE", "CATBITETWO", "SNAKETWO", "FOUR", 
             "ROTMARKED", "ROTRIDDEN", "TOPSURGERY"],
            ["CUTOPEN", "LABRATFACE", "VIVISECTION", "LABRATCHEST", "LABRATLIMBS", "NEUTRINO", "MANGLEDARM", 
             "ENVOYCHEST", "HALFFACELEFT", "FULLBODYBURNS", "BESIEGED", "HALFFACERIGHT"],
            ["STARBURN", "ARMBURN", "DOUBLEBITE", "DANGEROUS", "SMOKINGFACE", "NIBBLEDIDIOT", "X-FACE",
             "NIBBEDAGAIN", "MESSIAH", "EXTRACTIONTWO", "RESTITCHEDUPPER", "RESTITCHEDLOWER"],
            ["STITCHEDHEAD", "BURNTLEG", "BURNTARM", "VULTURESHOULDER", "CHEEKCUT", "MIROSNOM", "ARTIRIGHT",
            "ARTIGLOWRIGHT", "ARTILEFT", "ARTIGLOWLEFT", "SPEARWOUND", "PATCHWORK"]
        ]

        # define missing parts
        missing_parts_data = [
            ["LEFTEAR", "RIGHTEAR", "NOTAIL", "NOLEFTEAR", "NORIGHTEAR", "NOEAR", "HALFTAIL", "NOPAW"]
        ]

        # scars 
        for row, scars in enumerate(scars_data):
            for col, scar in enumerate(scars):
                self.make_group('scars', (col, row), f'scars{scar}')

        # missing parts
        for row, missing_parts in enumerate(missing_parts_data):
            for col, missing_part in enumerate(missing_parts):
                self.make_group('missingscars', (col, row), f'scars{missing_part}')

        # accessories
        medcatherbs_data = [
            ["MAPLE LEAF", "HOLLY", "BLUE BERRIES", "FORGET ME NOTS", "RYE STALK", "LAUREL"],
            ["BLUEBELLS", "NETTLE", "POPPY", "LAVENDER", "HERBS", "PETALS"],
            [],  # Empty row because this is the wild data, except dry herbs.
            ["OAK LEAVES", "SCUGMINT", "MAPLE SEED", "JUNIPER", "SAKURA"]
        ]

        wild_data = [
            ["RED FEATHERS", "BLUE FEATHERS", "JAY FEATHERS", "MOTH WINGS", "CICADA WINGS"]
        ]

        collars_data = [
            ["CRIMSON", "BLUE", "YELLOW", "CYAN", "RED", "LIME"],
            ["GREEN", "RAINBOW", "BLACK", "SPIKES", "WHITE"],
            ["PINK", "PURPLE", "MULTI", "INDIGO"]
        ]

        bellcollars_data = [
            ["CRIMSONBELL", "BLUEBELL", "YELLOWBELL", "CYANBELL", "REDBELL", "LIMEBELL"],
            ["GREENBELL", "RAINBOWBELL", "BLACKBELL", "SPIKESBELL", "WHITEBELL"],
            ["PINKBELL", "PURPLEBELL", "MULTIBELL", "INDIGOBELL"]
        ]

        bowcollars_data = [
            ["CRIMSONBOW", "BLUEBOW", "YELLOWBOW", "CYANBOW", "REDBOW", "LIMEBOW"],
            ["GREENBOW", "RAINBOWBOW", "BLACKBOW", "SPIKESBOW", "WHITEBOW"],
            ["PINKBOW", "PURPLEBOW", "MULTIBOW", "INDIGOBOW"]
        ]

        nyloncollars_data = [
            ["CRIMSONNYLON", "BLUENYLON", "YELLOWNYLON", "CYANNYLON", "REDNYLON", "LIMENYLON"],
            ["GREENNYLON", "RAINBOWNYLON", "BLACKNYLON", "SPIKESNYLON", "WHITENYLON"],
            ["PINKNYLON", "PURPLENYLON", "MULTINYLON", "INDIGONYLON"]
        ]
        drones_data = [
            ["CRIMSONDRONE", "BLUEDRONE", "YELLOWDRONE", "CYANDRONE", "REDDRONE", "LIMEDRONE"],
            ["GREENDRONE", "RAINBOWDRONE", "BLACKDRONE", "SPIKESDRONE", "WHITEDRONE"],
            ["PINKDRONE", "PURPLEDRONE", "MULTIDRONE", "INDIGODRONE"]
        ]
        rwlizards_data = [
            ["BLUESKY", "BLUESEA", "PINKMAGENTA", "PINKPURPLE", "GREENEMERALD", "GREENLIME", "WHITEHIDDEN", "WHITEREVEALED"], 
            ["BLACKNEUTRAL", "BLACKALERT", "YELLOWORANGE", "YELLOWLEMON", "REDTOMATO", "CYANBLUE", "CYANGREEN"],
            ["ALBISALAFUSHIA", "ALBISALARED", "MELASALARED", "MELASALAFUSHIA", "MELASALAPURPLE"]
        ]
        muddypaws_data = [
            ["MUDDYPAWS"]
        ]
        herbs2_data = [
            ["SPEAR", "PEARLEAR", "KARMAFLOWER", "LILCENTI", "PEARLNECK", "REDBATNIP"], 
            ["LILFLY","BATNIP", "FLASHFRUIT", "REDFLASHFRUIT", "GREENKELP", "REDKELP"], 
            ["VULTMASK", "KINGMASK", "SCAVMASK", "TREESEED", "GLOWSTONE", "BROWNKELP"], 
            ["LILBEETLE", "EXPLOSPEAR", "GREENDRAGFLY", "BLUEDRAGFLY", "ELESPEAR"]
        ]
        insectwings_data = [
            ["DEATHSHEAD", "BLUEBORDERED", "BLOODVEIN", "LARGEEMERALD", "CINNABAR", "LUNA", "ROSYMAPLE"],
            ["ATLAS", "HERCULES", "SUNSET", "PURPLEEMPEROR", "WHITEADMIRAL", "SWALLOWTAIL"]
        ]
        drones_data = [
            ["CRIMSONDRONE", "BLUEDRONE", "YELLOWDRONE", "CYANDRONE", "REDDRONE", "LIMEDRONE"],
            ["GREENDRONE", "RAINBOWDRONE", "BLACKDRONE", "SPIKESDRONE", "WHITEDRONE"],
            ["PINKDRONE", "PURPLEDRONE", "MULTIDRONE", "INDIGODRONE"]
        ]
        buddies_data = [
            ["MOUSEBLUE", "MOUSEYEL", "MOUSEPINK", "MOUSERED", "YEEKRED", "YEEKBLUE"], 
            ["VULTGRUB", "GRAPPLE", "SNAILGREEN", "SNAILBLUE", "SNAILRED", "SNAILPURPLE"],
            ["NOODLERED", "NOODLEPURPLE", "NOODLEGREY", "NOODLEBLUE", "NOODLEWHITE", "NOODLEPINK"],
            ["IGGYYELLOW", "IGGYPURPLE", "IGGYWHITE", "IGGYGREEN", "IGGYRED", "IGGYBLUE"],
            ["SQUIDBLACK", "SQUIDWHITE", "BUBBLE", "WORMGRASSPOT", "POLEPLANTPOT"]
        ]
        newaccs_data = [
            ["BATFLY", "BLUEFRUIT", "EMPTYBAG", "HERBSBAG", "INVEGG", "VOIDSPAWN"],
            ["REDARMOR", "OVERSEEREYE", "SPIDEREAR", "NEURONBLUE", "NEURONRED", "NEURONGREEN"],
            ["NEURONWHITE", "KARMAONE", "KARMATWO", "KARMATHREE", "KARMAFOUR", "SCROLL"],
            ["NECKLACESILVER", "NECKLACEGOLD", "TAILWRAP", "RAINCOAT", "LACESCARF", "TOLLMASK"],
            ["FLOWEREDMOSS", "MOSS", "MUSHROOMS", "MUSHROOMHAT", "GRENADE", "SANTAHAT"],
            ["EYEPATCH", 'INVMOUTH', "MOUSEYELPLUSH", "MOUSEREDPLUSH", "MOUSEBLUEPLUSH", "MOUSEPINKPLUSH"]
        ]
        newaccs2_data = [
            ["GLITCHING", "ROBOTARM", "ROBOTLEG", "SCRAPARMOR", "BLINDFOLD"],
            ["BRONZEPOCKETWATCH", "SILVERPOCKETWATCH", "GOLDPOCKETWATCH", "MURDERPAINT", "BOGMOSSBLUE"],
            ["BOGMOSSGREEN", "BOGMOSSLIME"],
            ["ORANGEPLANTPELT", "LIMEPLANTPELT", "GREENPLANTPELT", "YELLOWPLANTPELT", "BLUEPLANTPELT"]
        ]
        bodypaint_data = [
            ["REDPAINT", "PINKPAINT", "VOIDPAINT", "YELLOWPAINT", "GREENPAINT", "PALEPAINT"],
            ["CYANPAINT", "BLUEPAINT", "PURPLEPAINT", "MAGENTAPAINT", "BLACKPAINT", "WHITEPAINT"]
        ]
        implant_data = [
            ["IMPLANTWHITE", "IMPLANTPURPLE", "IMPLANTGREEN", "IMPLANTYELLOW", "IMPLANTBLUE"],
            ["EYEIMPLANTWHITE", "EYEIMPLANTRED", "EYEIMPLANTGREEN", "EYEIMPLANTYELLOW", "EYEIMPLANTBLUE"],
            ["GLOWWHITE", "GLOWPURPLE", "GLOWGREEN", "GLOWYELLOW", "GLOWBLUE"],
            ["CELLIMPLANT"]
        ]
        magic_data = [
            ["ORANGEFIRE", "GREENFIRE", "BLUEFIRE", "YELLOWFIRE", "WHITEFIRE", "PINKFIRE", "REDFIRE"],
            ["GREENRING", "CYANRING", "SILVERRING", "WHITERING", "YELLOWRING", "VOIDRING", "GOLDRING"],
            ["PETPEBBLE", "PETCLAY", "PETLAPIS", "PETAMETHYST", "PETJADE", "PETGRANITE", "PETSANDSTONE"]
        ]
        necklaces_data = [
            ["NECKLACEWHITE", "NECKLACEPINK", "NECKLACEPURPLE", "NECKLACEYELLOW", "NECKLACECYAN"],
            ["NECKLACEGREEN", "NECKLACERED", "NECKLACEORANGE", "NECKLACEBLUE", "NECKLACEBLACK"]
        ]
        drapery_data = [
            ["DRAPERYWHITE", "DRAPERYORANGE", "DRAPERYTAN", "DRAPERYPALEYELLOW", "DRAPERYYELLOW", "DRAPERYLIGHTMINT", "DRAPERYMINT", "DRAPERYGREEN", "DRAPERYLIGHTAQUA"],
            ["DRAPERYAQUA", "DRAPERYCYAN", "DRAPERYLIGHTGRAY", "DRAPERYPURPLE", "DRAPERYLIGHTINDIGO", "DRAPERYBLUE", "DRAPERYLAVENDER", "DRAPERYLIGHTPINK", "DRAPERYPINK"],
            ["DRAPERYHOTPINK", "DRAPERYGRAY", "DRAPERYDARKGRAY", "DRAPERYPALEPINK", "DRAPERYLIGHTRED", "DRAPERYRED", "DRAPERYPEACH", "DRAPERYLIGHTORANGE"]
        ]
        pridedrapery_data = [
            ["ORIGINALGAYDRAPERY", "TRANSDRAPERY", "GENDERQUEERDRAPERY", "AGENDERDRAPERY", "NONBINARYDRAPERY", "POLYAMDRAPERY", "GENDERFLUIDDRAPERY"],
            ["GENDERFLUXDRAPERY", "GAYDRAPERY", "OMNISEXUALDRAPERY", "OBJECTUMDRAPERY", "RAINBOWDRAPERY", "PHILIDRAPERY", "BISEXUALDRAPERY"],
            ["PANSEXUALDRAPERY", "POLYSEXUALDRAPERY", "ASEXUALDRAPERY", "LESBIANDRAPERY", "INTERSEXDRAPERY", "AROACEDRAPERY", "DEMIGIRLDRAPERY"],
            ["DEMIBOYDRAPERY", "DEMIGENDERDRAPERY", "DEMIFLUIDDRAPERY", "DEMIFLUXDRAPERY", "ABRODRAPERY", "ARODRAPERY", "DEMISEXDRAPERY"],
            ["DEMIRODRAPERY", "ACHILLEANDRAPERY", "SAPPHICDRAPERY", "DIAMORICDRAPERY", "UNLABELEDDRAPERY", "TRANSFEMDRAPERY", "TRANSMASCDRAPERY"],
            ["BIGENDERDRAPERY", "MULTISEXDRAPERY", "ACESPECDRAPERY", "AROSPECDRAPERY"]
        ]
        eyepatch_data = [
            ["EYEPATCHWHITE", "EYEPATCHGREEN", "EYEPATCHAQUA", "EYEPATCHTURQUOISE", "EYEPATCHCYAN", "EYEPATCHBLUE", "EYEPATCHINDIGO"],
            ["EYEPATCHPURPLE", "EYEPATCHMAGENTA", "EYEPATCHPINK", "EYEPATCHROSE", "EYEPATCHLIGHTGRAY", "EYEPATCHDARKGRAY", "EYEPATCHBLACK"],
            ["EYEPATCHRED", "EYEPATCHORANGE", "EYEPATCHAMBER", "EYEPATCHYELLOW", "EYEPATCHLIME"]
        ]
        larsaccs_data = [
            ["ALLSEEINGGOLD", "ALLSEEINGSILVER", "BESIEGEDMASKOG", "BESIEGEDMASKBLUE", "BESIEGEDMASKCYAN"],
            ["BESIEGEDMASKGRAY", "BESIEGEDMASKGREEN", "BESIEGEDMASKINDIGO", "BESIEGEDMASKORANGE", "BESIEGEDMASKPINK"],
            ["BESIEGEDMASKPURPLE", "BESIEGEDMASKRED", "BESIEGEDMASKROSE", "BESIEGEDMASKAQUA", "BESIEGEDMASKYELLOW"],
            ["HANDPEARLBLANK", "HANDPEARLBLUE", "HANDPEARLGREEN", "HANDPEARLORANGE", "HANDPEARLPURPLE"],
            ["HANDPEARLRED", "HANDPEARLYELLOW", "PEARLDRAPERY", "STRAIGHTGOLD", "STRAIGHTSILVER"]
        ]
    
        harleyaccs_data = [
            ["FALLENSTARMASK", "TORNCLOAKFALL", "FALLENSTARPAWS", "TORNCLOAKWINTER"],
            ["TORNCLOAKNIGHT", "TORNCLOAKSHADOW", "TORNCLOAKSILVER", "FAUXMANE"]
        ]

        featherboas_data = [
            ["DPINKFEATHERBOA", "DREDFEATHERBOA", "DGREENFEATHERBOA", "DBLUEFEATHERBOA", "DGREENERFEATHERBOA"],
            ["DORANGEFEATHERBOA", "LWHITEFEATHERBOA", "LPURPLEFEATHERBOA", "LBLUEFEATHERBOA", "LPINKFEATHERBOA"],
            ["DMAGENTAFEATHERBOA", "DCRIMSONFEATHERBOA", "DPURPLEFEATHERBOA"]
        ]

        scarves_data = [
            ["REDSCARF", "ORANGESCARF", "YELLOWSCARF", "LIMESCARF", "GREENSCARF", "CYANSCARF", "WHITESCARF"],
            ["BLUESCARF", "DARKBLUESCARF", "PURPLESCARF", "MAGENTASCARF", "BLACKSCARF", "GRAYSCARF", "BROWNSCARF"],
            ["NSHSCARF", "SAWYERSCARF"]
        ]
        
        neckbandanas_data = [
            ["DICEYNBANDANA", "EOUSNBANDANA", "FLUIDNBANDANA", "GUILDNBANDANA", "SKULLNBANDANA", "SKYNBANDANA", "SPACENBANDANA", "SWEETIENBANDANA"],
            ["TCYANNBANDANA", "TIEDYEMUDDYNBANDANA", "TIEDYENBANDANA", "TSAVNBANDANA", "BLUEGRADNBANDANA", "ORANGEGRADNBANDANA",  "YELLOWGRADNBANDANA", "LIMEGRADNBANDANA"],
            ["TEALGRADNBANDANA", "MAGENTAGRADNBANDANA", "REDGRADNBANDANA", "WHITENBANDANA", "LIGHTGRAYNBANDANA", "DARKGRAYNBANDANA", "BLACKNBANDANA", "PEACHNBANDANA"],
            ["PALEREDNBANDANA", "REDNBANDANA", "MAROONNBANDANA", "PALEORANGENBANDANA", "LIGHTORANGENBANDANA", "ORANGENBANDANA", "BROWNNBANDANA", "PALEYELLOWNBANDANA"],
            ["LIGHTYELLOWNBANDANA", "YELLOWNBANDANA", "PALEGREENNBANDANA", "LIGHTGREENNBANDANA", "GREENNBANDANA", "DARKGREENNBANDANA", "PALETEALNBANDANA", "LIGHTTEALNBANDANA"],
            ["TEALNBANDANA", "DARKTEALNBANDANA", "PALEBLUENBANDANA", "LIGHTBLUENBANDANA", "DARKBLUENBANDANA", "BLUENBANDANA", "LAVENDERNBANDANA", "PURPLENBANDANA"],
            ["DARKPURPLENBANDANA", "PALEPINKNBANDANA", "LIGHTPINKNBANDANA", "PINKNBANDANA", "DARKPINKNBANDANA", "PATCHWORKREDNBANDANA", "PATCHWORKORANGENBANDANA", "PATCHWORKYELLOWNBANDANA"],
            ["PATCHWORKGREENNBANDANA", "PATCHWORKTEALNBANDANA", "PATCHWORKBLUENBANDANA", "PATCHWORKINDIGONBANDANA", "PATCHWORKPURPLENBANDANA", "PATCHWORKPINKNBANDANA"]
        ]
        
        chains_data = [
            ["AMBERCHAIN", "PINKCHAIN", "PURPLECHAIN", "YELLOWCHAIN", "TEALCHAIN"],
            ["GREENCHAIN", "REDCHAIN", "ORANGECHAIN", "BLUECHAIN", "BLACKCHAIN"]
        ]

        newaccs3_data = [
            ["FALLMPAINT", "SCAVMPAINT", "SPEARMPAINT", "BLUECLOUDS"],
            ["YELLOWCLOUDS", "PURPLECLOUDS", "PINKCLOUDS", "GOGGLES"],
            ["PINKPOLEPLANTBUDDY", "ORANGEPOLEPLANTBUDDY", "REDPOLEPLANTBUDDY"]
        ]

        floatyeyes_data = [
            ["YELLOWFLOATYEYES", "REDFLOATYEYES", "ORANGEFLOATYEYES"],
            ["LIMEFLOATYEYES", "GREENFLOATYEYES", "BLUEFLOATYEYES"],
            ["INDIGOFLOATYEYES"]
        ]

        orbitals_data = [
            ['ORANGEORBITAL', 'YELLOWORBITAL', 'EARTHORBITAL'],
            ['EARTHTWOORBITAL', 'PURPLEORBITAL', 'PINKORBITAL'], 
            ['REDORBITAL']
        ]

        # medcatherbs
        for row, herbs in enumerate(medcatherbs_data):
            for col, herb in enumerate(herbs):
                self.make_group('medcatherbs', (col, row), f'acc_herbs{herb}')
        self.make_group('medcatherbs', (5, 2), 'acc_herbsDRY HERBS')

        # wild
        for row, wilds in enumerate(wild_data):
            for col, wild in enumerate(wilds):
                self.make_group('medcatherbs', (col, 2), f'acc_wild{wild}')

        # collars
        for row, collars in enumerate(collars_data):
            for col, collar in enumerate(collars):
                self.make_group('collars', (col, row), f'collars{collar}')

        # bellcollars
        for row, bellcollars in enumerate(bellcollars_data):
            for col, bellcollar in enumerate(bellcollars):
                self.make_group('bellcollars', (col, row), f'collars{bellcollar}')

        # bowcollars
        for row, bowcollars in enumerate(bowcollars_data):
            for col, bowcollar in enumerate(bowcollars):
                self.make_group('bowcollars', (col, row), f'collars{bowcollar}')

        # nyloncollars
        for row, nyloncollars in enumerate(nyloncollars_data):
            for col, nyloncollar in enumerate(nyloncollars):
                self.make_group('nyloncollars', (col, row), f'collars{nyloncollar}')
        # rw lizards     
        for a, i in enumerate(
                ["BLUESKY", "BLUESEA", "PINKMAGENTA", "PINKPURPLE", "GREENEMERALD", "GREENLIME", "WHITEHIDDEN", "WHITEREVEALED", "BLACKNEUTRAL", "BLACKALERT"]):
            self.make_group('rwlizards', (a, 0), f'lizards{i}')
        for a, i in enumerate(["YELLOWORANGE", "YELLOWLEMON", "REDTOMATO", "CYANBLUE", "CYANGREEN", "ALBISALAFUSHIA", "ALBISALARED", "MELASALARED", "MELASALAFUSHIA", "MELASALAPURPLE"]):
            self.make_group('rwlizards', (a, 1), f'lizards{i}')

        # drones
        for row, drones in enumerate(drones_data):
            for col, drone in enumerate(drones):
                self.make_group('drones', (col, row), f'collars{drone}')

        #sey's accs
        for row, muddypaws in enumerate(muddypaws_data):
            for col, muddypaws in enumerate(muddypaws):
                self.make_group('muddypaws', (col, row), f'muddypaws{muddypaws}')
                
        for a, i in enumerate(
                ["DEATHSHEAD", "BLUEBORDERED", "BLOODVEIN", "LARGEEMERALD", "CINNABAR", "LUNA", "ROSYMAPLE"]):
            self.make_group('insectwings', (a, 0), f'insectwings{i}')
        for a, i in enumerate(["ATLAS", "HERCULES", "SUNSET", "PURPLEEMPEROR", "WHITEADMIRAL", "SWALLOWTAIL"]):
            self.make_group('insectwings', (a, 1), f'insectwings{i}')
            
        #herbs 2
        for row, herbs2 in enumerate(herbs2_data):
            for col, herbs2 in enumerate(herbs2):
                self.make_group('herbs2', (col, row), f'herbs2{herbs2}')
                
        #buddies
        for row, buddies in enumerate(buddies_data):
            for col, buddies in enumerate(buddies):
                self.make_group('buddies', (col, row), f'buddies{buddies}')
                
        #newaccs
        for row, newaccs in enumerate(newaccs_data):
            for col, newaccs in enumerate(newaccs):
                self.make_group('newaccs', (col, row), f'newaccs{newaccs}')
                
        #newaccs2
        for row, newaccs2 in enumerate(newaccs2_data):
            for col, newaccs2 in enumerate(newaccs2):
                self.make_group('newaccs2', (col, row), f'newaccs2{newaccs2}')

        #bodypaint
        for row, bodypaint in enumerate(bodypaint_data):
            for col, bodypaint in enumerate(bodypaint):
                self.make_group('bodypaint', (col, row), f'bodypaint{bodypaint}')

        #implant
        for row, implant in enumerate(implant_data):
            for col, implant in enumerate(implant):
                self.make_group('implant', (col, row), f'implant{implant}')

        #magic
        for row, magic in enumerate(magic_data):
            for col, magic in enumerate(magic):
                self.make_group('magic', (col, row), f'magic{magic}')

        #necklaces
        for row, necklaces in enumerate(necklaces_data):
            for col, necklaces in enumerate(necklaces):
                self.make_group('necklaces', (col, row), f'necklaces{necklaces}')
        #drapery
        for row, drapery in enumerate(drapery_data):
            for col, drapery in enumerate(drapery):
                self.make_group('drapery', (col, row), f'drapery{drapery}')
        #pridedrapery
        for row, pridedrapery in enumerate(pridedrapery_data):
            for col, pridedrapery in enumerate(pridedrapery):
                self.make_group('pridedrapery', (col, row), f'pridedrapery{pridedrapery}')
        #eyepatches
        for row, eyepatches in enumerate(eyepatch_data):
            for col, eyepatches in enumerate(eyepatches):
                self.make_group('eyepatches', (col, row), f'eyepatches{eyepatches}')
        #larsaccs
        for row, larsaccs in enumerate(larsaccs_data):
            for col, larsaccs in enumerate(larsaccs):
                self.make_group('larsaccs', (col, row), f'larsaccs{larsaccs}')
        #harleyaccs
        for row, harleyaccs in enumerate(harleyaccs_data):
            for col, harleyaccs in enumerate(harleyaccs):
                self.make_group('harleyaccs', (col, row), f'harleyaccs{harleyaccs}')
        #featherboas
        for row, featherboas in enumerate(featherboas_data):
            for col, featherboas in enumerate(featherboas):
                self.make_group('featherboas', (col, row), f'featherboas{featherboas}')
        #scarves
        for row, scarves in enumerate(scarves_data):
            for col, scarves in enumerate(scarves):
                self.make_group('scarves', (col, row), f'scarves{scarves}')
        #neckbandanas
        for row, neckbandanas in enumerate(neckbandanas_data):
            for col, neckbandanas in enumerate(neckbandanas):
                self.make_group('neckbandanas', (col, row), f'neckbandanas{neckbandanas}')
        #chains
        for row, chains in enumerate(chains_data):
            for col, chains in enumerate(chains):
                self.make_group('chains', (col, row), f'chains{chains}')
        #newaccs3
        for row, newaccs3 in enumerate(newaccs3_data):
            for col, newaccs3 in enumerate(newaccs3):
                self.make_group('newaccs3', (col, row), f'newaccs3{newaccs3}')
        #floatyeyes
        for row, floatyeyes in enumerate(floatyeyes_data):
            for col, floatyeyes in enumerate(floatyeyes):
                self.make_group('floatyeyes', (col, row), f'floatyeyes{floatyeyes}')
        #orbitals
        for row, orbitals in enumerate(orbitals_data):
            for col, orbitals in enumerate(orbitals):
                self.make_group('orbitals', (col, row), f'orbitals{orbitals}')

    def load_symbols(self):
        """
        loads clan symbols
        """

        if os.path.exists('resources/dicts/clan_symbols.json'):
            with open('resources/dicts/clan_symbols.json') as read_file:
                self.symbol_dict = ujson.loads(read_file.read())

        # U and X omitted from letter list due to having no prefixes
        letters = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T",
                   "V", "W", "Y", "Z"]

        # sprite names will format as "symbol{PREFIX}{INDEX}", ex. "symbolSPRING0"
        y_pos = 1
        for letter in letters:
            x_mod = 0
            for i, symbol in enumerate([symbol for symbol in self.symbol_dict if
                                        letter in symbol and self.symbol_dict[symbol]["variants"]]):
                if self.symbol_dict[symbol]["variants"] > 1 and x_mod > 0:
                    x_mod += -1
                for variant_index in range(self.symbol_dict[symbol]["variants"]):
                    x_pos = i + x_mod

                    if self.symbol_dict[symbol]["variants"] > 1:
                        x_mod += 1
                    elif x_mod > 0:
                        x_pos += - 1

                    self.clan_symbols.append(f"symbol{symbol.upper()}{variant_index}")
                    self.make_group('symbols',
                                    (x_pos, y_pos),
                                    f"symbol{symbol.upper()}{variant_index}",
                                    sprites_x=1, sprites_y=1, no_index=True)

            y_pos += 1

    def dark_mode_symbol(self, symbol):
        """Change the color of the symbol to dark mode, then return it
        :param Surface symbol: The clan symbol to convert"""
        dark_mode_symbol = copy(symbol)
        var = pygame.PixelArray(dark_mode_symbol)
        var.replace((87, 76, 45), (239, 229, 206))
        del var
        # dark mode color (239, 229, 206)
        # debug hot pink (255, 105, 180)

        return dark_mode_symbol

# CREATE INSTANCE
sprites = Sprites()
