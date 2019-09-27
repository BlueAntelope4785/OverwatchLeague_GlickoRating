# OWL_Glicko2
Rating teams in the Overwatch League using the glicko2 rating algorhithm.

Requirements:
python3.x
matplotlib

glicko website: www.glicko.net/glicko.html

glicko2 python implementation (files glicko2.py and glicko2_tests.py) from: https://code.google.com/archive/p/pyglicko2/downloads accessed 2019/04/07

Running OWL_Glicko.py extracts match results from  https://api.overwatchleague.com/schedule and rates teams using the glicko2 rating algorhithm.
For all teams, the initial team ratings and ratings deviations (RDs) are the default (rating = 1500, RD = 350).
Each week of open play and each stage playoff week is a ratig period.
A plot of the ratings after each week and of the latest rating with RDs as errorbars are created.
Additionally a .txt file with the latest ratings and rds is created.

The jupyter notebook Examples.ipynb provides examples for using the extracted and generated rating data including plotting the ratings over time with the option to highlight any team.
