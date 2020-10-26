class TransferLink:
    def __init__(self, source_team_id, target_team_id, amount=0, player_pos=None,
                 player_name=None, player_age=None, player_nationality=None,
                 source_team_league=None, target_team_league=None, source_team_name=None, target_team_name=None,
                 transfer_type=None, year=2000, normalized_amount=0):
        self.source_team_id = source_team_id
        self.target_team_id = target_team_id
        self.amount = amount
        self.player_pos = player_pos
        self.player_name = player_name
        self.player_nationality = player_nationality
        self.player_age = player_age
        self.source_team_league = source_team_league
        self.target_team_league = target_team_league
        self.source_team_name = source_team_name
        self.target_team_name = target_team_name
        self.transfer_type = transfer_type
        self.year = year
        self.normalized_amount = normalized_amount

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.source_team_id == other.source_team_id and self.target_team_id == other.target_team_id and \
                   self.amount == other.amount and self.player_pos == other.player_pos and self.player_name == \
                   other.player_name and self.player_nationality == other.player_nationality and \
                   self.source_team_league == other.source_team_league and self.target_team_league == \
                   other.target_team_league and self.source_team_name == other.source_team_name and \
                   self.target_team_name == other.target_team_name and self.transfer_type == other.transfer_type and \
                   self.year == other.year
        return False

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return self.source_team_id != other.source_team_id or self.target_team_id != other.target_team_id or \
                   self.amount != other.amount or self.player_pos != other.player_pos or self.player_name != \
                   other.player_name or self.player_nationality != other.player_nationality or \
                   self.source_team_league != other.source_team_league or self.target_team_league != \
                   other.target_team_league or self.source_team_name != other.source_team_name or \
                   self.target_team_name != other.target_team_name or self.transfer_type != other.transfer_type or \
                   self.year != other.year
        return False

    def __hash__(self):
        return hash((
            self.source_team_id,
            self.target_team_id,
            self.amount,
            self.player_pos,
            self.player_name,
            self.player_age,
            self.player_nationality,
            self.source_team_league,
            self.target_team_league,
            self.source_team_name,
            self.target_team_name,
            self.transfer_type,
            self.year
        ))

    def get_transfer_link_info(self):
        return self.player_name + ", " + self.player_pos + ", " + self.source_team_id + ", " + self.source_team_name \
               + ", " + self.target_team_id + ", " + self.target_team_name + ", " + self.player_age + ", " +\
                str(self.amount) + ", " + self.transfer_type + ", " + self.year

