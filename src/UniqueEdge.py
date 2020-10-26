class UniqueEdge:
    def __init__(self, source_id, target_id):
        self.source_id = source_id
        self.target_id = target_id

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.source_id == other.source_id and self.target_id == other.target_id
        return False

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return self.source_id != other.source_id or self.target_id != other.target_id
        return False

    def __hash__(self):
        return hash((self.source_id, self.target_id))
