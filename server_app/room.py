class Room:
    def __init__(self, token, name, max_players):
        self.name, self.max_players = name, max_players
        self.token = token
        self.players_list = []
        self.available = True

    def delete_client(self, client):
        self.players_list.remove(client)
