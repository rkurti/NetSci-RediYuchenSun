class League:
    def __init__(self, league_name):
        self.league_name = league_name
        self.transfers_for_year = {}
        self.clubs = set()
        self.all_transfers = set()

        self.front_transfers = set()  # all front transfers
        self.midfield_transfers = set()  # all midfield transfers
        self.back_transfers = set() # Defense transfers
        self.goalkeeper_transfers = set() # Goalkeeper transfers

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.league_name == other.league_name
        return False

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return self.league_name == other.league_name
        return False

    def __hash__(self):
        return hash(self.league_name)

    def show_transfers_for(self, start_year, end_year):
        for year in range(start_year, end_year + 1):
            print("=======showing the links for " + str(year))
            try:
                for link in self.transfers_for_year[year]:
                    link.get_transfer_link_info()
            except Exception as e:
                print(e)

    def show_all_teams_belonging_to_league(self):
        print("=====================showing " + str(
            len(self.clubs)) + " teams in" + self.league_name + "==================")
        for club in self.clubs:
            print(str(club.club_id) + "," + club.club_name)
        print("-----------done showing teams in " + self.league_name + "------------------")

