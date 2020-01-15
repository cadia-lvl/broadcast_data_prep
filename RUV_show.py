#Author: Judy Fong <lvl@judyyfong.xyz.> Reykjavik University
#Description:
#a class called RUV show
#attributes: title, type (radio or tv), seasons (list of seasons, years and the kringlan number, and url), player(kringlan number, url)

class Season:
    def __init__(self, years, kringlan_number):
        self.years = years
        self.kringlan_number = kringlan_number

class Programme:
    def __init__(self, name, broadcast_method, player_url, approved, seasons):
            self.name = name
            self.broadcast_method = broadcast_method
            self.player_url = player_url
            self.seasons = seasons
            self.approved = approved;

    def add_season(self, season):
        self.seasons.append(season)
