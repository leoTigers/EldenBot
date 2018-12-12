from LoupGarou.constant import ANN_GDOC_KEY, GOOGLE_TOKEN_PATH
from LoupGarou.object import Announce
import gspread
from oauth2client.service_account import ServiceAccountCredentials as sac

def load_announce(game):
    credentials = sac.from_json_keyfile_name(GOOGLE_TOKEN_PATH,
                                             ["https://spreadsheets.google.com/feeds"])
    gc = gspread.authorize(credentials)
    wb = gc.open_by_key(ANN_GDOC_KEY).get_worksheet(0)
    data = wb.get_all_values()[1:]
    result = []
    return {line[0]: Announce(game, line) for line in data if any(line)}


def load_images():
    credentials = sac.from_json_keyfile_name(GOOGLE_TOKEN_PATH,
                                             ["https://spreadsheets.google.com/feeds"])
    gc = gspread.authorize(credentials)
    wb = gc.open_by_key(ANN_GDOC_KEY).get_worksheet(1)
    data = wb.get_all_values()[1:]
    result = []
    return {line[0]: Announce(game, line) for line in data if any(line)}
