class Club:
    def __init__(self, club_id, club_name, club_country):
        self.club_id = club_id
        self.club_name = club_name
        self.club_country = club_country

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.club_id == other.club_id
        return False

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return self.club_id != other.club_id
        return False

    def __hash__(self):
        return hash(self.club_id)
