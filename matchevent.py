class MatchEvent:

    @classmethod
    def from_dict(cls, match_event_dict):
        """
        Create a Match Event from the dictionary in a Match.

        ARGS:
            match_event_dict (dict) - dictionary for a single match event
                                      read from a match dictionary
        RETURNS:
            MatchEvent (obj) - new MatchEvent object
        """
        return cls(match_event_dict['type'],
                   match_event_dict['time'],
                   match_event_dict['text'],
                   match_event_dict['homeScore'],
                   match_event_dict['awayScore'])

    def __init__(self, type_, time, text="", home_score=None, away_score=None):
        """
        ARGS:
            type_ (int) - type of the event
            time (str) - minute of the time in the match
            text (str) - text of the event
            home_score (int) - score for the home team after the event
            away_score (int) - score for the away team after the event
        """
        self.type_map = {
            1: 'Try',
            2: 'Conversion',
            3: 'Penalty',
            4: 'Drop Goal',
            5: 'Yellow Card',
            6: 'Red Card',
            7: 'Sub Off',
            8: 'Sub On',
            9: 'Game Start',
            10: 'End of first half',
            11: 'Start of Second Half',
            12: 'End of game',
            9999: 'Text Event'
        }
        self.type = type_
        time = time.replace("'", "")
        if '+' in time:
            self.time = int(time.split('+')[0])
            self.added_time = int(time.split('+')[1])
        else:
            self.time = int(time)
            self.added_time = 0
        self.text = text
        self.home_score = home_score
        self.away_score = away_score

    def __str__(self):
        """
        String representation for a Match Event.
        """
        score = ", {}-{}".format(self.home_score, self.away_score) if self.home_score else ""
        return "{}: {}, {} {}".format(self.time, self.type_string, self.text, score)

    @property
    def type_string(self):
        """
        Return the string name for a match event type.
        """
        return self.type_map[self.type] if self.type in self.type_map else self.type

    def is_try(self):
        return self.type == 1

    def is_conversion(self):
        return self.type == 2

    def is_penalty(self):
        return self.type == 3

    def is_drop_goal(self):
        return self.type == 4

    def is_yellow_card(self):
        return self.type == 5

    def is_red_card(self):
        return self.type == 6

    def is_sub_off(self):
        return self.type == 7

    def is_sub_on(self):
        return self.type == 8

    def is_start_of_game(self):
        return self.type == 9

    def is_end_of_first_half(self):
        return self.type == 10

    def is_start_of_second_half(self):
        return self.type == 11

    def is_end_of_game(self):
        return self.type == 12

    def is_text_event(self):
        return self.type == 9999


class MatchEventList:

    @classmethod
    def from_dict(cls, player_event_dict):
        """
        Create a Match Event list for a player events in a match.

        ARGS:
            player_event_dict (dict) - dict of events for a player in the form
                                       {eventType: ["timeOne", "timeTwo"]}, e.g.
                                       {
                                         '1': ["59'"],
                                         '3': ["34'"],
                                         '2': ["50'", "77'"],
                                       }
        RETURNS
            MatchEventList (obj) - list of match events for a player
        """
        events = []
        for type_ in player_event_dict:
            events.extend([MatchEvent(int(type_), event)
                           for event in player_event_dict[type_]])
        return cls(events)

    def __init__(self, match_events=None):
        """
        ARGS:
            match_events ([MatchEvent]) - list of MatchEvents to store in the list
        """
        self.match_events = match_events or []
    
    def __len__(self):
        """
        len implementation for MatchEventList.
        """
        return len(self.match_events)

    def __iter__(self):
        """
        Iterator implementation for MatchEventList.
        """
        self.currentIndex = -1
        return self

    def __next__(self):
        """
        Iterator implementation for MatchEventList
        RETURNS:
            MatchEvent (obj) - returns next MatchEvent object in list
        """
        if self.currentIndex >= len(self.match_events) - 1:
            raise StopIteration
        else:
            self.currentIndex += 1
            return self.match_events[self.currentIndex]

    def add_match_event(self, match_event):
        """
        Add a new match event to the list.

        ARGS:
            match_event (obj) - new MatchEvent to add
        """
        self.match_events.append(match_event)

    def get_events_for_type(self, type_):
        """
        Return a new MatchEventList filtered by type.
        
        ARGS:
            type_ (int) - type to filter the list by
        RETURNS:
            MatchEventList - list with filtered MatchEvents
        """
        match_events = MatchEventList()
        for match_event in self.match_events:
            if match_event.type == type_:
                match_events.add_match_event(match_event)
        return match_events
