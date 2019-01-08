from LoupGarou.Loading.role import *
ROLE_LIST = [Werewolf, Villager, Seer,
             Witch, Hunter, Werewolf,
             Villager, Cupidon, Villager,
             Werewolf, Villager, Villager,
             Villager, Villager, Werewolf]\
             + [Villager] * 5

ANN_GDOC_KEY = "1-JJZmP9SPJbzsRHXvBPbFTIDejwN2goqtHPv-Vdqtcg"
GOOGLE_TOKEN_PATH = "private/googlekey.json"

START_PL_TITLE = "Liste des Joueurs :"

OK_EMOJI = '✅'
NEXT_EMOJI = '➡'

OPTION = {
    "show_role_at_death": True,
    "server_mute_at_death": True,
    "point_alive": 2,
    "point_win": 1,
    "point_lose": -1,
}
