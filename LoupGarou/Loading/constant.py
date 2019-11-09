START_PL_TITLE = "Liste des Joueurs :"

OK_EMOJI = '✅'
NEXT_EMOJI = '➡'

OPTION = {
    "show_role_at_death": True,
    "death_channel_id": 0,
    "point_alive": 2,
    "point_win": 1,
    "point_lose": -1,
}

from LoupGarou.Loading.role import Werewolf, Villager, Seer, Witch, Hunter, Cupidon

ROLE_LIST = [Werewolf, Villager, Seer,
             Witch, Hunter, Werewolf,
             Villager, Cupidon, Villager,
             Werewolf, Villager, Villager,
             Villager, Villager, Werewolf]\
             + [Villager] * 5