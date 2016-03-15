import platform
import json
import requests
import sys
import csv


def set_file_path(file_from_onedrive):
    """
    :param file_from_onedrive: file path within onedrive (excluding OneDrive/ root)
    :return: returns system-contextual full file path
    """
    if platform.system() == "Windows":
        if "/" in file_from_onedrive:
            file_from_onedrive.replace("/", "\\")
        if file_from_onedrive[0:2] == "\\":
            file_from_onedrive = file_from_onedrive[2:]
        path_to_file = "C:\\Users\\Chris\\OneDrive\\Projects\\FPL_Tracker\\" + file_from_onedrive
        print(path_to_file)
    else:
        if file_from_onedrive[0:1] == "/":
            file_from_onedrive = file_from_onedrive[1:]
        path_to_file = '/Users/ChrisWatkins/OneDrive/Projects/FPL_Tracker/' + file_from_onedrive
        print(path_to_file)
    return path_to_file


def write_json_file(json_file_path, json_data):
    """
    writes any changes to existingData variable to JSON data file
    :param json_file_path: path to JSON data file
    :param json_data: pass dictionary to function
    """
    try:
        with open(json_file_path, 'w') as f:
                json.dump(json_data, f, ensure_ascii=True)
                f.close()
    except OSError:
        print("Damn!")
        with open(json_file_path, 'w+') as f:
            json.dump(json_data, f, ensure_ascii=True)
            f.close()
    print('JSON file written successfully.')
    print('\n')
    return json_data


def load_json_file(json_file_path):
    """
    loads JSON data from file
    :param json_file_path: path to JSON data file
    """
    try:
        with open(json_file_path, 'r') as f:
                json_data = json.load(f)
                f.close()
    except OSError:
        print("Damn!")
        with open(json_file_path, 'r+') as f:
            json_data = json.load(f)
            f.close()
    print('File read successfully.')
    print('\n')
    return json_data


def write_csv_file(csv_file_path, headers_to_write, data_to_write):
    """
    :param csv_file_path: pass in full_file_path var pointing to desired csv output
    :param headers_to_write: pass in list of headers
    :param data_to_write: pass in list of data
    :return:
    """
    csv.register_dialect('excel', delimiter=',', quoting=csv.QUOTE_ALL)

    # grab dict keys from data_to_write var as row iterator
    row_iterator = list(data_to_write)

    with open(csv_file_path, 'wt') as f:
        try:
            writer = csv.writer(f, dialect='excel')

            # write headers
            writer.writerow(headers_to_write)

            # write data
            for row in row_iterator:
                writer.writerow(data_to_write[row])
        finally:
            print('CSV file written successfully.')
            print('\n')
            f.close()


print('\n')
response = input("This script polls the FPL API for all player data. Please allow time to complete. Continue? ")

yes = {'y', 'Y', 'yes', 'Yes'}

while True:
    if response in yes:
        break
    else:
        sys.exit(0)

print('\n')

# begin API call
# set base null variables as dicts
all_data = {}
api_error = {}

# API logic: range adjustable depending on desired number of outputs
for i in range(650):
    player_url = "http://fantasy.premierleague.com/web/api/elements/{}/".format(i)
    print(player_url)
    r = requests.get(player_url)

    # skip non-existent players
    if r.status_code != 200:
        api_error[i] = r.status_code
        print('Not found.')
        print('\n')
        continue

    # assign player name to dict key, write all json data to key
    temp = r.json()
    player_name = temp['web_name']
    print(player_name)
    print('\n')
    all_data[player_name] = temp

print('\n')
print('API call over.')
print('\n')

print('Writing errors to file...')
full_file_path = set_file_path("Data/FPL_API_Dump_errors.log")
write_json_file(full_file_path, api_error)

print('Writing data to file...')
full_file_path = set_file_path("Data/FPL_API_Dump.json")
write_json_file(full_file_path, all_data)

# # load json encoded data to all_data var
# full_file_path = set_file_path("Data/FPL_API_Dump.json")
# all_data = load_json_file(full_file_path)

# collect all player names
all_keys = list(all_data)

# begin future fixture extraction
print('Data collection complete. Beginning future fixture extraction...')
print('\n')

# set state vars
fixtures_gw_val = []
fixtures_gw_headers = ["Player"]

# generate header row and current gameweek for future fixtures
for i in range(len(all_data["Terry"]["fixtures"]["all"])):
    val = int(str(all_data["Terry"]["fixtures"]["all"][i][1])[-2:])

    # append current gw val to list
    fixtures_gw_val.append(val)

    # write pretty 2-digit gw string
    if val < 10:
        fixtures_gw_headers.append("Gameweek 0" + str(val))
    else:
        fixtures_gw_headers.append("Gameweek " + str(val))

current_gw = min(fixtures_gw_val)
end_gw = max(fixtures_gw_val)
gws_remaining = (end_gw - current_gw) + 1

print("Current Gameweek: " + str(current_gw))
print('\n')

# set state vars
failures = 0
fixtures = {}

# grab rest of season fixtures for each player
for e in range(len(all_keys)):
    current_player = all_keys[e]
    fixtures[current_player] = [current_player]

    for i in range(gws_remaining):
        try:
            temp_fixture = all_data[current_player]['fixtures']['all'][i][2]
            fixtures[current_player].append(temp_fixture)
        except LookupError:
            fixtures[current_player].append("N/A")
            pass

    if "N/A" in fixtures[current_player]:
        failures += 1

    # print(fixtures[current_player])
    # print('\n')

print(str(failures) + " failures.")
print('\n')

print('Writing data to file.')
full_file_path = set_file_path("Data/FPL_Fixtures_Extract.json")
write_json_file(full_file_path, fixtures)
full_file_path = set_file_path("Data/FPL_Fixtures_Extract.csv")
write_csv_file(full_file_path, fixtures_gw_headers, fixtures)

print("Fixtures extract complete.")
print('\n')

# begin current season points history extract
print('Beginning current season points extract...')
print('\n')

# set state vars
points_gw_val = []
points_gw_headers = ["Player"]

# generate header row and current gameweek for current season's points
for i in range(len(all_data["Terry"]["fixture_history"]["all"])):

    val = all_data["Terry"]["fixture_history"]["all"][i][1]

    # append current gw val to list
    points_gw_val.append(val)

    # write pretty 2-digit gw string
    if val < 10:
        points_gw_headers.append("Gameweek 0" + str(val))
    else:
        points_gw_headers.append("Gameweek " + str(val))

# print(points_gw_headers)
# print('\n')

start_gw = min(points_gw_val)
end_gw = max(points_gw_val)
gws_played = (end_gw - start_gw) + 1

# set state vars
failures = 0
points_history = {}

# run through all players' current season points
for e in range(len(all_keys)):
    current_player = all_keys[e]
    points_history[current_player] = [current_player]
    player_gws = len(all_data[current_player]['fixture_history']['all'])

    # test to see how many gws played
    for i in range(gws_played):
        # test to see if player has played any weeks at all
        if player_gws == 0:
            break

        # test for played gws being fewer than total
        elif player_gws < gws_played:
            player_first_gw = all_data[current_player]['fixture_history']['all'][0][1]
            gw_enter_position = points_gw_val.index(player_first_gw) + 1

            for s in range(gws_played):
                # once it hits the start gw, run the full range of gws played then return to errors
                if len(points_history[current_player]) == gw_enter_position:
                    for p in range(player_gws):
                        temp_gw = all_data[current_player]['fixture_history']['all'][p][-1]
                        points_history[current_player].append(temp_gw)

                else:
                    if len(points_history[current_player]) == len(points_gw_headers):
                        break
                    else:
                        points_history[current_player].append("N/A")
            break

        else:
            if len(points_history[current_player]) == len(points_gw_headers):
                break
            else:
                temp_gw = all_data[current_player]['fixture_history']['all'][i][-1]
                points_history[current_player].append(temp_gw)

    if "N/A" in points_history[current_player]:
        failures += 1

    # print(points_history[current_player])
    # print('\n')

print(str(failures) + " failures.")
print('\n')

print('Writing data to file.')
full_file_path = set_file_path("Data/FPL_Points_Extract.json")
write_json_file(full_file_path, points_history)
full_file_path = set_file_path("Data/FPL_Points_Extract.csv")
write_csv_file(full_file_path, points_gw_headers, points_history)

print("Current season points extract complete.")
print('\n')

# begin season results extract using points_gw_headers from last extract
# set state vars
failures = 0
results_history = {}

# run through all players' current season points
for e in range(len(all_keys)):
    current_player = all_keys[e]
    results_history[current_player] = [current_player]
    player_gws = len(all_data[current_player]['fixture_history']['all'])

    # test to see how many gws played
    for i in range(gws_played):
        # test to see if player has played any weeks at all
        if player_gws == 0:
            break

        # test for played gws being fewer than total
        elif player_gws < gws_played:
            player_first_gw = all_data[current_player]['fixture_history']['all'][0][1]
            gw_enter_position = points_gw_val.index(player_first_gw) + 1

            for s in range(gws_played):
                # once it hits the start gw, run the full range of gws played then return to errors
                if len(results_history[current_player]) == gw_enter_position:
                    for p in range(player_gws):
                        temp_gw = all_data[current_player]['fixture_history']['all'][p][2]
                        results_history[current_player].append(temp_gw)

                else:
                    if len(results_history[current_player]) == len(points_gw_headers):
                        break
                    else:
                        results_history[current_player].append("N/A")
            break

        else:
            if len(results_history[current_player]) == len(points_gw_headers):
                break
            else:
                temp_gw = all_data[current_player]['fixture_history']['all'][i][2]
                results_history[current_player].append(temp_gw)

    if "N/A" in results_history[current_player]:
        failures += 1

    # print(results_history[current_player])
    # print('\n')

print(str(failures) + " failures.")
print('\n')

print('Writing data to file.')
full_file_path = set_file_path("Data/FPL_Results_Extract.json")
write_json_file(full_file_path, results_history)
full_file_path = set_file_path("Data/FPL_Results_Extract.csv")
write_csv_file(full_file_path, points_gw_headers, results_history)

print("Current season's results extract complete.")
print('\n')

# begin past season points history extract
print("Beginning previous season points extract...")
print('\n')

# set state vars
failures = 0
season_val = []
season_headers = ["Player"]
season_history = {}

# generate header row and current season by iterating through all
for i in range(len(all_data["Terry"]["season_history"])):

    v = all_data["Terry"]["season_history"][i][0]

    # write season val as int
    season_val.append(int(v[:4]))

    # write pretty season string to dict
    season_headers.append(v)

first_season = min(season_val)
last_season = max(season_val)
num_seasons = (last_season+1) - first_season

# print(season_headers)
# print('\n')

for e in range(len(all_keys)):
    current_player = all_keys[e]
    season_history[current_player] = [current_player]
    player_seasons = len(all_data[current_player]['season_history'])
    # print(current_player)
    # print(player_seasons)

    for i in range(num_seasons):
        # test to see which years player was in premier league
        if player_seasons == 0:
            break

        elif player_seasons < num_seasons:
            enter_league = all_data[current_player]['season_history'][0][0]
            enter_position = season_headers.index(enter_league)

            for s in range(num_seasons):
                # once it hits the start season, run the full range of seasons played then return to errors
                if len(season_history[current_player]) == enter_position:
                    for p in range(player_seasons):
                        temp_season = all_data[current_player]['season_history'][p][-1]
                        season_history[current_player].append(temp_season)

                else:
                    if len(season_history[current_player]) == len(season_headers):
                        break
                    else:
                        season_history[current_player].append("N/A")
            break

        else:
            if len(season_history[current_player]) == len(season_headers):
                break
            else:
                temp_season = all_data[current_player]['season_history'][i][-1]
                season_history[current_player].append(temp_season)

    if "N/A" in season_history[current_player]:
        failures += 1

    # print(season_history[current_player])
    # print('\n')

print(str(failures) + " failures.")
print('\n')

print('Writing data to file.')
full_file_path = set_file_path("Data/FPL_Season_History_Extract.json")
write_json_file(full_file_path, season_history)
full_file_path = set_file_path("Data/FPL_Season_History_Extract.csv")
write_csv_file(full_file_path, season_headers, season_history)

print('Past season points extract complete.')
print('\n')

# begin other information extract
print('Beginning misc info extraction...')
print('\n')

# set headers
misc_headers = ["Player", "Team Name", "TP", "PPG", "Chance this round", "Chance next round", "Form", "Selected By", "Status", "Position", "Cost"]

# set state vars
failures = 0
misc = {}

# grab rest of season fixtures for each player
for i in range(len(all_keys)):
    current_player = all_keys[i]
    misc[current_player] = [current_player]

    try:
        t_tn = all_data[current_player]['team_name']
        misc[current_player].append(t_tn)
    except LookupError:
        misc[current_player].append("N/A")
        pass
    try:
        t_tp = int(all_data[current_player]['total_points'])
        misc[current_player].append(t_tp)
    except LookupError:
        misc[current_player].append("N/A")
        pass
    try:
        t_ppg = float(all_data[current_player]['points_per_game'])
        misc[current_player].append(t_ppg)
    except LookupError:
        misc[current_player].append("N/A")
        pass
    try:
        t_this_round = all_data[current_player]['chance_of_playing_this_round']
        misc[current_player].append(t_this_round)
    except LookupError:
        misc[current_player].append("N/A")
        pass
    try:
        t_next_round = all_data[current_player]['chance_of_playing_next_round']
        misc[current_player].append(t_next_round)
    except LookupError:
        misc[current_player].append("N/A")
        pass
    try:
        t_form = float(all_data[current_player]['value_form'])
        misc[current_player].append(t_form)
    except LookupError:
        misc[current_player].append("N/A")
        pass
    try:
        t_sb = float(all_data[current_player]['selected_by_percent'])
        misc[current_player].append(t_sb)
    except LookupError:
        misc[current_player].append("N/A")
        pass
    try:
        t_s = all_data[current_player]['status']
        misc[current_player].append(t_s)
    except LookupError:
        misc[current_player].append("N/A")
        pass
    try:
        t_type = all_data[current_player]['type_name']
        misc[current_player].append(t_type)
    except LookupError:
        misc[current_player].append("N/A")
        pass
    try:
        t_cost = all_data[current_player]['now_cost']/10
        misc[current_player].append(t_cost)
    except LookupError:
        misc[current_player].append("N/A")
        pass
    if "N/A" in misc[current_player]:
        failures += 1

    # print(misc[current_player])
    # print('\n')

print(str(failures) + " failures.")
print('\n')

print('Writing data to file.')
full_file_path = set_file_path("Data/FPL_Misc_Extract.json")
write_json_file(full_file_path, misc)
full_file_path = set_file_path("Data/FPL_Misc_Extract.csv")
write_csv_file(full_file_path, misc_headers, misc)

print("Misc info extract complete.")
print('\n')

print("Programme complete.")

sys.exit(0)
