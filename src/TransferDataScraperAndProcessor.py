import os
import csv
from bs4 import BeautifulSoup
from TransferLink import *
from LeagueURLConstants import *
from Club import *
from EdgeWeight import *
from League import *
from UniqueEdge import *
from decimal import Decimal

front_pos = {"Centre-Forward","Second Striker","Striker", "Left Winger", "Right Winger"}
midfield_pos = {"Defensive Midfield", "Attacking Midfield","Central Midfield","Right Midfield","Left Midfield"}
back_pos = {"Sweeper", "Centre-Back", "Right-Back", "Left-Back"}
goalkeeper_pos = {"Goalkeeper"}

class TransferDataScraperAndProcessor:

    def __init__(self, start_year, end_year, should_include_loans=False):
        self.start_year = start_year
        self.end_year = end_year
        self.should_include_loans = should_include_loans
        self.headers = {'User-Agent':
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}

        self.url_start = "https://www.transfermarkt.us/"
        self.url_string_after_league_data = "/plus/?saison_id="
        self.url_end = "&s_w=&leihe=0&leihe=1&intern=0&intern=0"  # Include Loans and no club internal transfers(ChelseaU23 to Chelsea)
        
        # self.all_player_names = []
        # self.all_player_names_dup = []

        self.all_transfers = set()  # all transfer links

        self.all_front_transfers = set()  # all front transfers
        self.all_midfield_transfers = set()  # all midfield transfers
        self.all_back_transfers = set() # Defense transfers
        self.all_goalkeeper_transfers = set() # Goalkeeper transfers

        self.all_leagues = set()  # all leagues
        self.all_clubs = set()  # all clubs. Each club object has a club id and name
        self.all_countries_and_clubs = {}
        self.most_expensive_transfer_for_each_year = {}
        self.get_most_expensive_transfers_for_all_years(self.start_year, self.end_year)
        self.process_all_data(self.start_year, self.end_year)
        
        self.all_unique_edges = self.generate_unique_edges(self.all_transfers)
        self.all_unique_front_edges = self.generate_unique_edges(self.all_front_transfers)
        self.all_unique_midfield_edges = self.generate_unique_edges(self.all_midfield_transfers)
        self.all_unique_back_edges = self.generate_unique_edges(self.all_back_transfers)
        self.all_unique_goalkeeper_edges = self.generate_unique_edges(self.all_goalkeeper_transfers)

        self.put_all_clubs_in_a_league()

    def get_most_expensive_transfers_for_all_years(self, start_year, end_year):
        for year in range(start_year, end_year + 1):
            year_as_string = str(year)
            print("Finding most expensive Transfer for " + year_as_string)

            source_file = "../html/" + year_as_string + "MostExpensiveTransfer.html"
            with open(source_file, "rb") as fetched_content:
                page_soup = BeautifulSoup(fetched_content, 'html.parser')

            amount = page_soup.find("td", {"class": "rechts hauptlink"}).find("a").get_text()
            processed_amount = self.process_amount(amount)
            self.most_expensive_transfer_for_each_year[year] = processed_amount

    def process_all_data(self, start_year, end_year):
        for league_name in LeagueURLConstants.league_names_with_urls:
            print("=================================working on " + league_name + "=========================")
            league = League(league_name)
            # league_edges = []
            for year in range(start_year, end_year + 1):
                max_amount_for_year = self.most_expensive_transfer_for_each_year[year]
                league.transfers_for_year[year] = set()
                year_as_string = str(year)
                print("calculating data for " + year_as_string + "..........")
                source_file = "../html/" + year_as_string + league_name + ".html"
                with open(source_file, "rb") as fetched_content:
                    page_soup = BeautifulSoup(fetched_content, 'html.parser')

                boxes = page_soup.findAll("div", {"class": "box"})
                club_boxes = [box for box in boxes if box]

                country_header_box = club_boxes[0]
                # Remove the First 3 Box elements that are at the top of each page.
                club_boxes = club_boxes[3:]

                tuples_out = []
                tuples_in = []
                for box in club_boxes:
                    table_headers = box.find_all("div", {"class": "table-header"})

                    # Get only the Transfer out Boxes from Each Box.
                    responsive_table_out_transfers = box.find_all("div", {"class": "responsive-table"})[1::2]
                    responsive_table_in_transfers = box.find_all("div", {"class": "responsive-table"})[0::1]
                    header_div_tuple_out = (table_headers, responsive_table_out_transfers)
                    tuples_out.append(header_div_tuple_out)

                    header_div_tuple_in = (table_headers, responsive_table_in_transfers)
                    tuples_in.append(header_div_tuple_in)

                header_team_country = self.get_header_country(country_header_box)
                if header_team_country not in self.all_countries_and_clubs:
                    self.all_countries_and_clubs[header_team_country] = set()
                for t in tuples_out:
                    if t[0] and t[1]:
                        # print("=====================================================================================")
                        source_team_details = self.get_header_team_details(t)
                        source_team_name = self.get_header_team_name(source_team_details)
                        source_team_id = self.get_header_team_id(source_team_details)
                        transfers_out = t[1][0]
                        trs = self.get_all_trs(transfers_out)
                        if "No departures" in trs[1].find("td").get_text():
                            continue
                        else:
                            source_team_club = Club(source_team_id, source_team_name, header_team_country)
                            self.all_countries_and_clubs[header_team_country].add(source_team_club)
                            if source_team_club not in self.all_clubs:
                                self.all_clubs.add(source_team_club)
                            for i in range(1, len(trs)):
                                tr = trs[i]
                                player_name = self.get_player_name(tr)
                                player_amount = self.get_player_amount(tr)
                                player_pos = self.get_player_position(tr)
                                player_age = self.get_player_age(tr)
                                player_nationality = self.get_player_nationality(tr)
                                target_team_details = self.get_tr_team_details(tr)
                                target_team = self.get_tr_team(target_team_details)
                                target_team_name = self.get_tr_team_name(tr)
                                transfer_type = self.get_transfer_type(player_amount)
                                processed_amount = self.process_amount(player_amount)
                                calculated_normalized_amount = self.get_normalized_amount(processed_amount, max_amount_for_year)
                                if target_team:
                                    target_team_id = self.get_tr_team_id(target_team)
                                    if self.valid_football_club(target_team_id):
                                        target_team_country = self.get_tr_team_country(target_team_details)
                                        link = TransferLink(source_team_id=source_team_id,
                                                            target_team_id=target_team_id,
                                                            amount=processed_amount,
                                                            player_pos=player_pos,
                                                            source_team_name=source_team_name,
                                                            target_team_name=target_team_name,
                                                            player_name=player_name,
                                                            player_nationality=player_nationality,
                                                            player_age=player_age,
                                                            transfer_type=transfer_type,
                                                            year=year, normalized_amount=calculated_normalized_amount)
                                        league.transfers_for_year[year].add(link)
                                        league.all_transfers.add(link)
                                        self.all_transfers.add(link)
                                        target_club = Club(target_team_id, target_team_name, target_team_country)
                                        if target_team_country not in self.all_countries_and_clubs:
                                            self.all_countries_and_clubs[target_team_country] = set()
                                        self.all_countries_and_clubs[target_team_country].add(target_club)
                                        if target_club not in self.all_clubs:
                                            self.all_clubs.add(target_club)
                                        # Change in filtering
                                        if transfer_type != "Loan":
                                            if player_pos in front_pos:
                                                self.all_front_transfers.add(link)
                                                league.front_transfers.add(link)
                                                # print("Add front position")
                                                # print("Total front position ", len(league.front_transfers))
                                            elif player_pos in midfield_pos:
                                                self.all_midfield_transfers.add(link)
                                                league.midfield_transfers.add(link)
                                                # print("Add Midfield position")
                                                # print("Total Midfield position ",len(league.midfield_transfers))
                                            elif player_pos in back_pos:
                                                self.all_back_transfers.add(link)
                                                league.back_transfers.add(link)
                                                # print("Add Back position")
                                                # print("Total Back position ", len(league.back_transfers))
                                            elif player_pos in goalkeeper_pos:
                                                self.all_goalkeeper_transfers.add(link)
                                                league.goalkeeper_transfers.add(link)
                                                # print("Add Goalkeeper position")
                                                # print("Total Goalkeeper position ", len(league.goalkeeper_transfers))

                                        if source_team_club not in league.clubs:
                                            league.clubs.add(source_team_club)
                self.all_player_names=[]
                self.all_player_names_dup=[]
                # -----------------Transfers IN ------------------------------------------------------------------------

                for t in tuples_in:
                    if t[0] and t[1]:
                        # print("=====================================================================================")
                        target_team_details = self.get_header_team_details(t)
                        target_team_name = self.get_header_team_name(target_team_details)
                        target_team_id = self.get_header_team_id(target_team_details)
                        transfers_in = t[1][0]
                        trs = self.get_all_trs(transfers_in)
                        if "No arrivals" in trs[1].find("td").get_text():
                            continue
                        else:
                            target_team_club = Club(target_team_id, target_team_name, header_team_country)
                            self.all_countries_and_clubs[header_team_country].add(target_team_club)
                            if target_team_club not in self.all_clubs:
                                self.all_clubs.add(target_team_club)
                            for i in range(1, len(trs)):
                                tr = trs[i]
                                player_name = self.get_player_name(tr)
                                player_amount = self.get_player_amount(tr)
                                player_pos = self.get_player_position(tr)
                                player_age = self.get_player_age(tr)
                                player_nationality = self.get_player_nationality(tr)
                                source_team_details = self.get_tr_team_details(tr)
                                source_team = self.get_tr_team(source_team_details)
                                source_team_name = self.get_tr_team_name(tr)
                                transfer_type = self.get_transfer_type(player_amount)
                                processed_amount = self.process_amount(player_amount)
                                calculated_normalized_amount = self.get_normalized_amount(processed_amount, max_amount_for_year)
                                if source_team:
                                    source_team_id = self.get_tr_team_id(source_team)
                                    if self.valid_football_club(source_team_id):
                                        source_team_country = self.get_tr_team_country(source_team_details)
                                        link = TransferLink(source_team_id=source_team_id,
                                                            target_team_id=target_team_id,
                                                            amount=processed_amount,
                                                            player_pos=player_pos,
                                                            player_age=player_age,
                                                            player_nationality=player_nationality,
                                                            source_team_name=source_team_name,
                                                            target_team_name=target_team_name,
                                                            player_name=player_name,
                                                            transfer_type=transfer_type,
                                                            year=year, normalized_amount=calculated_normalized_amount)
                                        league.transfers_for_year[year].add(link)
                                        league.all_transfers.add(link)
                                        self.all_transfers.add(link)
                                        source_club = Club(source_team_id, source_team_name, source_team_country)
                                        if source_team_country not in self.all_countries_and_clubs:
                                            self.all_countries_and_clubs[source_team_country] = set()
                                        self.all_countries_and_clubs[source_team_country].add(source_club)
                                        if source_club not in self.all_clubs:
                                            self.all_clubs.add(source_club)
                                        # Change in filtering
                                        if transfer_type != "Loan":
                                            if player_pos in front_pos:
                                                self.all_front_transfers.add(link)
                                                league.front_transfers.add(link)
                                                # print("Add front position")
                                                # print("Total front position ", len(league.front_transfers))
                                            elif player_pos in midfield_pos:
                                                self.all_midfield_transfers.add(link)
                                                league.midfield_transfers.add(link)
                                                # print("Add Midfield position")
                                                # print("Total Midfield position ",len(league.midfield_transfers))
                                            elif player_pos in back_pos:
                                                self.all_back_transfers.add(link)
                                                league.back_transfers.add(link)
                                                # print("Add Back position")
                                                # print("Total Back position ", len(league.back_transfers))
                                            elif player_pos in goalkeeper_pos:
                                                self.all_goalkeeper_transfers.add(link)
                                                league.goalkeeper_transfers.add(link)
                                                # print("Add Goalkeeper position")
                                                # print("Total Goalkeeper position ", len(league.goalkeeper_transfers))

                                        if target_team_club not in league.clubs:
                                            league.clubs.add(target_team_club)

                print("------Finished calculating data for " + year_as_string + "----------")
            self.all_leagues.add(league)

    def get_expenditure_per_year(self, league_total_transaction_data):
        return league_total_transaction_data[1].find("span").get_text()

    def get_income_per_year(self, league_total_transaction_data):
        return league_total_transaction_data[0].find("span").get_text()

    def get_income_expenditure_per_year_data(self, page_soup):
        return page_soup.find("div", {"class": "transferbilanz"}).findAll("div", {"class": "text"})

    def get_header_country(self, box):
        return box.find("div", {"class": "box-header"}).find("img").get("alt")

    def get_header_team_details(self, t):
        return t[0][0].select("a", {"class": "vereinprofil_tooltip"})

    def get_header_team_name(self, team_details):
        return team_details[0].find("img").get("alt")

    def get_header_team_id(self, team_details):
        return team_details[1].get("id")

    def get_all_trs(self, transfers):
        return transfers.find_all("tr")

    def get_player_name(self, tr):
        return tr.find("span", {"class": "hide-for-small"}).get_text()

    def get_player_amount(self, tr):
        # Index 0 has market Value. Index 1 has Transfer Fee
        return tr.find_all("td", {"class": "rechts"})[1].get_text()

    def get_player_position(self, tr):
        return tr.find_all("td", {"class": "pos-transfer-cell"})[0].get_text()

    def get_player_age(self, tr):
        age_data = tr.find("td", {"class": "zentriert alter-transfer-cell"}).get_text()
        AVERAGE_AGE = 25
        if age_data.isdigit():
            return int(tr.find("td", {"class": "zentriert alter-transfer-cell"}).get_text())
        else:
            return AVERAGE_AGE

    def get_player_nationality(self, tr):
        nationality_td = (tr.find("td", {"class": "zentriert nat-transfer-cell"})).find("img")
        if nationality_td:
            return nationality_td.find("alt")
        else:
            return "Unknown"

    def get_tr_team_details(self, tr):
        return tr.find("td", {"class": "no-border-links verein-flagge-transfer-cell"})

    def get_tr_team(self, team_details):
        return team_details.find("a", {"class": "vereinprofil_tooltip"})

    def get_tr_team_name(self, tr):
        return tr.find("td", {"class": "no-border-rechts zentriert"}).find("img").get("alt")

    def get_tr_team_id(self, team):
        return team.get("id")

    def get_tr_team_country(self, team_details):
        return team_details.find("img").get("alt")

    def process_amount(self, amount):
        if '$' not in amount:
            return Decimal(0)
        else:
            wo_currency_amount = amount[amount.index('$') + 1:]
            multiplier_symbol = wo_currency_amount[len(wo_currency_amount) - 1]
            wo_currency_and_multiplier_amount = Decimal(wo_currency_amount[0:len(wo_currency_amount) - 1])
            if multiplier_symbol == 'm':
                amount = wo_currency_and_multiplier_amount * 1000000
            elif multiplier_symbol == 'k':
                amount = wo_currency_and_multiplier_amount * 1000
            else:
                amount = Decimal(wo_currency_amount)
            # Remove Trailing Zeros after Decimal Point
            return amount.quantize(Decimal(1)) if amount == amount.to_integral() else amount.normalize()

    def get_normalized_amount(self, amount, total):
        return amount/Decimal(total)

    def get_transfer_type(self, amount):
        if ("loan" in amount or "Loan" in amount) and "end of" not in amount.lower():
            return "Loan"
        elif "Free Transfer" in amount:
            return "Free Transfer"
        else:
            return "Transfer"

    def valid_football_club(self, team_id):
        retired_id = 123
        without_club_id = 515
        career_break_id = 2113
        if team_id != retired_id or team_id != without_club_id or team_id != career_break_id:
            return True
        return False

    def show_all_transfers_per_league(self, start_year, end_year):
        for league in self.all_leagues:
            print("printing " + league.league_name + "......")
            league.show_transfers_for(start_year, end_year)

    def show_all_teams(self):
        for league in self.all_leagues:
            league.show_all_teams_belonging_to_league()

    def generate_unique_edges(self, set_links):
        unique_edges = {}
        for link in set_links:
            unique_edge = UniqueEdge(link.source_team_id, link.target_team_id)
            
            if unique_edge in unique_edges:
                unique_edges[unique_edge].increase_num_players()
                unique_edges[unique_edge].increase_amount(link.amount)
                unique_edges[unique_edge].increase_normalized_amount(link.normalized_amount)
                if link.player_age <= 24:
                    unique_edges[unique_edge].increase_num_young_players()
                    unique_edges[unique_edge].increase_amount_for_young_players(link.amount)
                    unique_edges[unique_edge].increase_normalized_amount_for_young_players(link.normalized_amount)
                elif link.player_age > 24 and link.player_age < 30:
                    unique_edges[unique_edge].increase_num_middle_aged_players()
                    unique_edges[unique_edge].increase_amount_for_middle_aged_players(link.amount)
                    unique_edges[unique_edge].increase_normalized_amount_for_middle_aged_players(link.normalized_amount)
                else:
                    unique_edges[unique_edge].increase_num_old_players()
                    unique_edges[unique_edge].increase_amount_for_old_players(link.amount)
                    unique_edges[unique_edge].increase_normalized_amount_for_old_players(link.normalized_amount)
            else:
                unique_edge = UniqueEdge(link.source_team_id, link.target_team_id)
                if link.player_age <= 24:
                    unique_edges[unique_edge] = EdgeWeight(1, link.amount, link.normalized_amount, num_young_players=1,
                                                           total_amount_for_young_players=link.amount,
                                                           total_normalized_amount_for_young_players=link.normalized_amount)
                elif link.player_age > 24 and link.player_age < 30:
                    unique_edges[unique_edge] = EdgeWeight(1, link.amount, link.normalized_amount,
                                                           num_middle_aged_players=1,
                                                           total_amount_for_middle_aged_players=link.amount,
                                                           total_normalized_amount_for_middle_aged_players=link.normalized_amount)
                else:
                    unique_edges[unique_edge] = EdgeWeight(1, link.amount, link.normalized_amount, num_old_players=1,
                                                           total_amount_for_old_players=link.amount,
                                                           total_normalized_amount_for_old_players=link.normalized_amount)
        return unique_edges
    
    # Added more cases to create files for each of the positions (and the overall as well).
    def write_output_file_with_weights(self, pos):
        file_path_start = "../data/all_edges_weight_"+pos
        if pos == "":
            edges_to_write = self.all_unique_edges
            file_path_start = "../data/all_edges_all_pos_"
            print("Total edges with weights: ", len(edges_to_write))
        elif pos == "front":
            edges_to_write = self.all_unique_front_edges
            print("Total front position with weights: ", len(edges_to_write))
        elif pos == "midfield":
            edges_to_write = self.all_unique_midfield_edges
            print("Total midfield position with weights: ", len(edges_to_write))
        elif pos == "back":
            edges_to_write = self.all_unique_back_edges
            print("Total back position with weights: ", len(edges_to_write))
        elif pos == "goalkeeper":
            edges_to_write = self.all_unique_goalkeeper_edges
            print("Total goalkeeper position with weights: ", len(edges_to_write))

        file_path = file_path_start + str(self.start_year) + "_" + str(self.end_year) + ".csv"
        if os.path.exists(file_path):
            os.remove(file_path)
        with open(file_path, 'w', newline='\n', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter=',')
            writer.writerow(["source", "target", "num_players", "total_amount", "total_normalized_amount",
                             "num_young_players", "num_middle_aged_players", "num_old_players",
                             "total_amount_for_young_players",
                             "total_amount_for_middle_aged_players",
                             "total_amount_for_old_players",
                             "total_normalized_amount_for_young_players",
                             "total_normalized_amount_for_middle_aged_players",
                             "total_normalized_amount_for_old_players"])
            for edge in edges_to_write:
                num_players_as_string = str(edges_to_write[edge].num_players)
                total_amount_as_string = str(edges_to_write[edge].total_amount/100000000)
                total_normalized_amount_as_string = str(edges_to_write[edge].total_normalized_amount*10)
                num_young_players_as_string = str(edges_to_write[edge].num_young_players)
                num_middle_aged_players_as_string = str(edges_to_write[edge].num_middle_aged_players)
                num_old_players_as_string = str(edges_to_write[edge].num_old_players)
                total_amount_for_young_players_as_string = str(edges_to_write[edge].total_amount_for_young_players/100000000)
                total_amount_for_middle_aged_players_as_string = str(edges_to_write[edge].total_amount_for_middle_aged_players/100000000)
                total_amount_for_old_players_as_string = str(edges_to_write[edge].total_amount_for_old_players/100000000)
                total_normalized_amount_for_young_players_as_string = str(edges_to_write[
                                                                              edge].total_normalized_amount_for_young_players*10)
                total_normalized_amount_for_middle_aged_players_as_string = str(edges_to_write[
                                                                                    edge].total_normalized_amount_for_middle_aged_players*10)
                total_normalized_amount_for_old_players_as_string = str(edges_to_write[
                                                                            edge].total_normalized_amount_for_old_players*10)

                writer.writerow([edge.source_id, edge.target_id, num_players_as_string,
                                 total_amount_as_string, total_normalized_amount_as_string,
                                 num_young_players_as_string, num_middle_aged_players_as_string,
                                 num_old_players_as_string, total_amount_for_young_players_as_string,
                                 total_amount_for_middle_aged_players_as_string,
                                 total_amount_for_old_players_as_string,
                                 total_normalized_amount_for_young_players_as_string,
                                 total_normalized_amount_for_middle_aged_players_as_string,
                                 total_normalized_amount_for_old_players_as_string])

    # Writes the number of players as edges in the csv depending on what position given.
    def write_output_file_for_pos(self, pos):
        file_path = "../data/num_players_"+pos+"_network_" + str(self.start_year) + "_" + str(self.end_year) + ".csv"
        if pos == "":
            edges_to_write = self.all_unique_edges
            print("Total", len(edges_to_write))
            print("All duplicate players: ", self.all_player_names_dup)
        elif pos == "front":
            edges_to_write = self.all_unique_front_edges
            print("Total front position ", len(edges_to_write))
        elif pos == "midfield":
            edges_to_write = self.all_unique_midfield_edges
            print("Total midfield position ", len(edges_to_write))
        elif pos == "back":
            edges_to_write = self.all_unique_back_edges
            print("Total back position ", len(edges_to_write))
        elif pos == "goalkeeper":
            edges_to_write = self.all_unique_goalkeeper_edges
            print("Total goalkeeper position ", len(edges_to_write))

        if os.path.exists(file_path):
            os.remove(file_path)
        with open(file_path, 'w', newline='\n', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter=',')
            writer.writerow(["source", "target", "weight"])
            for edge in edges_to_write:
                writer.writerow([edge.source_id, edge.target_id, str(edges_to_write[edge].num_players)])


    def put_all_clubs_in_a_league(self):
        other_league = League("Other")
        for club in self.all_clubs:
            belongs_to_known_leagues = False
            for league in self.all_leagues:
                if club in league.clubs:
                    belongs_to_known_leagues = True
                    break
            if not belongs_to_known_leagues:
                other_league.clubs.add(club)
        self.all_leagues.add(other_league)

    def write_out_all_clubs_and_leagues(self):
        file_path = "../data/all_nodes_leagues_" + str(self.start_year) + "_" + str(self.end_year) + ".csv"
        if os.path.exists(file_path):
            os.remove(file_path)
        with open(file_path, 'w', newline='\n', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter=',')
            writer.writerow(["Id", "Label", "League"])
            for league in self.all_leagues:
                for club in league.clubs:
                    writer.writerow([str(club.club_id), club.club_name, league.league_name])

    def write_out_clubs_and_countries(self):
        file_path = "../data/all_nodes_countries_" + str(self.start_year) + "_" + str(self.end_year) + ".csv"
        if os.path.exists(file_path):
            os.remove(file_path)
        with open(file_path, 'w', newline='\n', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter=',')
            writer.writerow(["Id", "Label", "Country"])
            for country in self.all_countries_and_clubs:
                clubs = self.all_countries_and_clubs[country]
                for club in clubs:
                    writer.writerow([str(club.club_id), club.club_name, club.club_country])
