This is a python project to access and analyse data for rugby matches. The data is pulled from espn rugby, for example [Exeter v Munster](http://www.espn.com/rugby/match?gameId=293566&league=271937) and stored locally in the "database" to avoid having to pull from online every time.

Feel free to clone or fork the repo and contribute what you can to the project. Make sure to run test.py before committing any major changes and add tests for any new features

# Current Leagues in database

|League |Season(s)|
|--- | --- |
|Six Nations|2013-2018|
|Rugby Championship|2017, 2018|
|Internationals|June 18, November 17|
|Champions Cup|17/18, 18/19|
|Challenge Cup|17/18, 18/19|
|Pro 14|17/18, 18/19|
|Top 14|17/18, 18/19|
|English Premiership|17/18, 18/19|
|Super Rugby|2017, 2018|

# Quick Sample Demo
```python
from python_rugby.league import League
# Load the champions cup from the database
championsCup = League.fromLeagueName('Champions Cup')

# get matches in the range of dates
# in this example these dates encompass Round 2 matches
startDate = datetime(2018,10,18)
endDate = datetime(2018,10,22)
roundTwoMatches = championsCup.getMatchesInDateRange(startDate, endDate)

# Get the number of tackles for each player
tackles = []
for match in roundTwoMatches:
  print match
  for team in match.players.keys():
    for player in match.players[team]:
      tackles.append((player.name, player.getStat('tackles'), team))
```
