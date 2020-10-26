class EdgeWeight:
    def __init__(self, num_players=1, amount=0, total_normalized_amount=0, num_young_players=0,
                 num_middle_aged_players=0, num_old_players=0, 
                 total_amount_for_young_players=0, total_amount_for_middle_aged_players=0, 
                 total_amount_for_old_players=0, total_normalized_amount_for_young_players=0, 
                 total_normalized_amount_for_middle_aged_players=0, total_normalized_amount_for_old_players=0):
        self.num_players = num_players
        self.total_amount = amount
        self.total_normalized_amount = total_normalized_amount
        self.total_amount_for_young_players = total_amount_for_young_players
        self.total_amount_for_middle_aged_players = total_amount_for_middle_aged_players
        self.total_amount_for_old_players = total_amount_for_old_players
        self.num_young_players = num_young_players
        self.num_middle_aged_players = num_middle_aged_players
        self.num_old_players = num_old_players
        self.total_normalized_amount_for_young_players = total_normalized_amount_for_young_players
        self.total_normalized_amount_for_middle_aged_players = total_normalized_amount_for_middle_aged_players
        self.total_normalized_amount_for_old_players = total_normalized_amount_for_old_players

    def increase_num_players(self):
        self.num_players += 1

    def increase_amount(self, new_amount):
        self.total_amount += new_amount

    def increase_amount_for_young_players(self, new_amount):
        self.total_amount_for_young_players += new_amount
        
    def increase_amount_for_middle_aged_players(self, new_amount):
        self.total_amount_for_middle_aged_players += new_amount

    def increase_amount_for_old_players(self, new_amount):
        self.total_amount_for_old_players += new_amount
    
    def increase_normalized_amount(self, new_normalized_amount):
        self.total_normalized_amount += new_normalized_amount

    def increase_num_young_players(self):
        self.num_young_players += 1

    def increase_num_old_players(self):
        self.num_old_players += 1

    def increase_num_middle_aged_players(self):
        self.num_middle_aged_players += 1

    def increase_normalized_amount_for_young_players(self, new_normalized_amount):
        self.total_normalized_amount_for_young_players += new_normalized_amount

    def increase_normalized_amount_for_middle_aged_players(self, new_normalized_amount):
        self.total_normalized_amount_for_middle_aged_players += new_normalized_amount
        
    def increase_normalized_amount_for_old_players(self, new_normalized_amount):
        self.total_normalized_amount_for_old_players += new_normalized_amount
