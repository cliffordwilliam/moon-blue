# db of all existing enemies in the game, also parallax bg and everything else, just store the class in a dict, not the intsance
import json
from os import path
import pygame
from nodes.enemies.blue_bat import BlueBat
from nodes.enemies.orange_bat import OrangeBat


class SpritesheetDataMap:
    def __init__(self, base_dir):
        # list what each stage owns, like png, jsons, music, etc...
        self.spritesheet_data_map = {
            "forest_of_illusion_tile_sheet": {
                "BlueBat": {
                    "class_ref": BlueBat,
                    "png": path.join(
                        base_dir, "pngs", "blue_fly_attack_anim_srip_3.png"
                    ),
                    "json": path.join(
                        base_dir,
                        "jsons",
                        "blue_fly_idle_or_flying_anim_strip_3.json",
                    ),
                }
            },
            "forest_of_mist_tile_sheet": {
                "OrangeBat": {
                    "class_ref": OrangeBat,
                    "png": path.join(
                        base_dir, "pngs", "orange_fly_atack_anim_srip_3.png"
                    ),
                    "json": path.join(
                        base_dir,
                        "jsons",
                        "orange_fly_idle_or_flying_anim_strip_3.json",
                    ),
                }
            },
        }

    def load_spritesheet_data(self, spritesheet_data):
        """Load images and JSON data for the given spritesheet data map."""
        # the thing that does the actual loading, should take a long time, to be called when u switch stage
        for entity_name, entity_data in spritesheet_data.items():
            # Load PNG
            if "png" in entity_data:
                entity_data["png"] = pygame.image.load(
                    entity_data["png"]
                ).convert_alpha()

            # Load JSON
            if "json" in entity_data:
                with open(entity_data["json"]) as json_file:
                    entity_data["json"] = json.load(json_file)
