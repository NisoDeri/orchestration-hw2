"""Pre-scripted debate transcript — simulates a real 10-ping Messi vs Ronaldo debate."""
from __future__ import annotations

MESSI_ARGS: list[dict] = [
    {"arg": "Lionel Messi has won 8 Ballon d'Or awards — more than any footballer in history. This sustained individual "
     "recognition across nearly two decades proves a level of excellence no other player can claim.",
     "attack": ["No other player has maintained peak performance this long"],
     "defense": ["8 Ballon d'Ors is an objective, voter-verified metric"],
     "cite": "https://en.wikipedia.org/wiki/Ballon_d%27Or", "conf": 0.92},
    {"arg": "My opponent highlights Ronaldo's goal tally, but football is not solely about goals. Messi holds the "
     "record for most assists in La Liga history with 192 — he creates AND finishes. Ronaldo's assist numbers "
     "pale in comparison, exposing a one-dimensional attacker.",
     "attack": ["Ronaldo's goal record ignores playmaking entirely"],
     "defense": ["192 La Liga assists is an all-time record", "Goals + assists combined favours Messi"],
     "cite": "https://www.transfermarkt.com/lionel-messi/assists/spieler/28003", "conf": 0.88},
    {"arg": "Ronaldo claims league diversity proves greatness, yet Messi dominated the strongest league in the world "
     "for 17 consecutive seasons. He then moved to PSG and Inter Miami, proving adaptability — but staying at "
     "Barcelona was a choice to compete against the best, not a limitation.",
     "attack": ["Leaving for weaker leagues is not proof of versatility"],
     "defense": ["La Liga was the world's strongest league during Messi's tenure"],
     "cite": "https://en.wikipedia.org/wiki/La_Liga", "conf": 0.85},
    {"arg": "My opponent cites Champions League knockouts, but let me remind the court: Messi scored 4 goals against "
     "Arsenal in one UCL quarter-final, destroyed Bayern Munich in the 2015 semi-final with a masterclass, and has "
     "the most UCL goals in group stages. His 129 total UCL goals came with far fewer penalty kicks.",
     "attack": ["Ronaldo's UCL knockout stats are inflated by penalties"],
     "defense": ["Messi's 2015 semi-final vs Bayern is widely considered the greatest individual UCL performance"],
     "cite": "https://www.uefa.com/uefachampionsleague/history/rankings/players/goals_scored/", "conf": 0.87},
    {"arg": "Speaking as the 2009 version of myself — at just 22, I won the first-ever sextuple in football history "
     "with Barcelona. Six trophies in one calendar year. I scored 38 goals that season while Ronaldo, the same "
     "age, was still adjusting to Real Madrid after leaving Manchester United.",
     "attack": ["2009 Ronaldo had zero major trophies with Real Madrid yet"],
     "defense": ["The 2009 sextuple is unprecedented and unrepeated"],
     "cite": "https://en.wikipedia.org/wiki/2008%E2%80%9309_FC_Barcelona_season", "conf": 0.90},
    {"arg": "The 2022 FIFA World Cup settled this debate permanently. I scored 7 goals and gave 3 assists across the "
     "tournament, won the Golden Ball, and lifted the one trophy that had eluded me. Ronaldo's World Cup record? "
     "Zero finals, zero semi-final goals, and an exit in tears against Morocco.",
     "attack": ["Ronaldo has never reached a World Cup final"],
     "defense": ["World Cup 2022 Golden Ball + trophy is the ultimate individual + team achievement"],
     "cite": "https://en.wikipedia.org/wiki/2022_FIFA_World_Cup", "conf": 0.94},
    {"arg": "Messi's dribbling success rate of 68% with over 3,000 successful dribbles in La Liga alone represents "
     "an entire dimension of football that Ronaldo simply cannot replicate. Football is art and expression — not "
     "just crossing a ball and heading it in.",
     "attack": ["Ronaldo's playing style is mechanistic and lacks creative genius"],
     "defense": ["Dribbling is the purest individual skill metric in football"],
     "cite": "https://fbref.com/en/players/d70ce98e/Lionel-Messi", "conf": 0.86},
    {"arg": "My opponent boasts about Ronaldo's mentality, but Messi's humility IS his mentality. He let his football "
     "speak. Meanwhile, Messi has won 36 team trophies at club level — more than Ronaldo's 34. The quiet leader "
     "outperforms the loud one where it counts: in the trophy cabinet.",
     "attack": ["Ronaldo's theatrics distract from actual team success metrics"],
     "defense": ["36 club trophies vs 34 is an objective comparison"],
     "cite": "https://en.wikipedia.org/wiki/Lionel_Messi#Career_statistics", "conf": 0.83},
    {"arg": "Every advanced metric — expected assists, progressive passes, shot-creating actions, through balls — "
     "ranks Messi as the most complete attacker in football history. Ronaldo excels at finishing, but finishing is "
     "one skill. Messi excels at everything simultaneously.",
     "attack": ["Ronaldo is a specialist; Messi is a generalist who also specialises"],
     "defense": ["xA, progressive passes, and SCA data all favour Messi overwhelmingly"],
     "cite": "https://fbref.com/en/players/d70ce98e/Lionel-Messi#all_stats_standard", "conf": 0.89},
    {"arg": "In closing: 8 Ballon d'Ors, a World Cup, 36 club trophies, 192 La Liga assists, 3,000+ dribbles, and "
     "the respect of every opponent who ever faced him. Messi didn't just play football — he redefined what was "
     "possible with a ball at his feet. The debate is settled.",
     "attack": ["No statistical or narrative dimension favours Ronaldo over Messi"],
     "defense": ["The totality of evidence is overwhelming"],
     "cite": "https://en.wikipedia.org/wiki/Lionel_Messi", "conf": 0.95},
]

RONALDO_ARGS: list[dict] = [
    {"arg": "Cristiano Ronaldo holds the all-time men's international scoring record with 135 goals for Portugal — "
     "no player in history has scored more for their country. This transcends club loyalty and proves greatness on "
     "the world stage where there are no super-teams to hide behind.",
     "attack": ["International goals prove individual merit without club-level support systems"],
     "defense": ["135 international goals is an objective, FIFA-verified record"],
     "cite": "https://en.wikipedia.org/wiki/International_goals_scored_by_Cristiano_Ronaldo", "conf": 0.91},
    {"arg": "My opponent cites Ballon d'Or count, but awards are voted by journalists with well-documented biases. "
     "What cannot be disputed: Ronaldo won league titles in England, Spain, and Italy — three of the top five "
     "leagues. Messi spent 17 years at one club in one league. That is comfort, not courage.",
     "attack": ["Ballon d'Or voting is subjective and influenced by media narratives"],
     "defense": ["Titles in 3 different top leagues proves adaptability Messi never tested"],
     "cite": "https://en.wikipedia.org/wiki/Cristiano_Ronaldo#Honours", "conf": 0.87},
    {"arg": "Messi's opponent claims La Liga was the strongest league — yet Ronaldo dominated the Champions League "
     "knockout stage with 67 goals, including hat-tricks against Bayern, Atletico, and Juventus. When the entire "
     "continent watches, Ronaldo delivers. Messi's infamous no-shows against Roma and Liverpool say otherwise.",
     "attack": ["Messi disappeared in critical UCL knockout matches repeatedly"],
     "defense": ["67 UCL knockout goals is 20 more than Messi's tally in the same stages"],
     "cite": "https://www.uefa.com/uefachampionsleague/history/rankings/players/goals_scored/", "conf": 0.89},
    {"arg": "My opponent downplays penalties, but converting penalties under Champions League pressure is itself a "
     "skill. Ronaldo's 5 Champions League titles across two different clubs — Manchester United AND Real Madrid — "
     "prove he is the defining player of European football's premier competition.",
     "attack": ["Messi has only 4 UCL titles, all with one historically dominant club"],
     "defense": ["5 UCL titles with 2 clubs > 4 UCL titles with 1 superteam"],
     "cite": "https://en.wikipedia.org/wiki/UEFA_Champions_League_records_and_statistics", "conf": 0.88},
    {"arg": "As the 2013 version of myself — I scored 69 goals in a single calendar year for Real Madrid, won my "
     "second Ballon d'Or, and was the undisputed best player in the world. While 2009 Messi had Barcelona's "
     "tiki-taka system, I carried Real Madrid as the sole creative and finishing force.",
     "attack": ["2009 Messi benefited from Xavi, Iniesta, and Pep's system — not pure individual brilliance"],
     "defense": ["2013 Ronaldo was a one-man army; 69 goals with less midfield support than Messi ever had"],
     "cite": "https://en.wikipedia.org/wiki/2013_Ballon_d%27Or", "conf": 0.86},
    {"arg": "My opponent raises the 2022 World Cup — one tournament. Ronaldo led Portugal to the Euro 2016 title, "
     "the first major trophy in Portuguese history. He did it despite going off injured in the final. Leadership "
     "isn't just playing well — it's inspiring your team to win without you on the pitch.",
     "attack": ["One World Cup does not erase a career of Champions League dominance"],
     "defense": ["Euro 2016 was the first major title for Portugal — a historically smaller football nation"],
     "cite": "https://en.wikipedia.org/wiki/UEFA_Euro_2016_final", "conf": 0.84},
    {"arg": "Dribbling statistics are a nostalgia metric for fans who confuse entertainment with effectiveness. "
     "Ronaldo evolved from the flashiest dribbler at Manchester United into the most lethal striker in history. "
     "That transformation — winger to striker to target man — shows unmatched tactical intelligence.",
     "attack": ["Dribbling does not win matches; goals and trophies do"],
     "defense": ["Ronaldo's tactical evolution across 3 phases of his career is unprecedented"],
     "cite": "https://en.wikipedia.org/wiki/Cristiano_Ronaldo#Playing_style", "conf": 0.82},
    {"arg": "Messi claims 36 club trophies, but let me counter: Ronaldo has 34 trophies across FOUR different clubs "
     "in THREE countries. Messi's trophies came overwhelmingly from one era of Barcelona dominance with Xavi, "
     "Iniesta, Busquets, Neymar, and Suarez. Strip the supporting cast and what remains?",
     "attack": ["Messi's trophy count is inflated by Barcelona's golden generation, not individual merit"],
     "defense": ["Winning across 4 clubs in 3 countries proves Ronaldo elevates any team"],
     "cite": "https://en.wikipedia.org/wiki/Cristiano_Ronaldo#Club", "conf": 0.85},
    {"arg": "Advanced metrics favour whoever the metric-designer admires. Here is a metric that cannot be gamed: "
     "Ronaldo has scored 900+ career goals — the highest verified tally in football history. Goals are the "
     "currency of football. Everything else is commentary.",
     "attack": ["xA and progressive passes are designer metrics; goals are the universal truth"],
     "defense": ["900+ goals is the highest verified career total in football history"],
     "cite": "https://en.wikipedia.org/wiki/List_of_men%27s_footballers_with_500_or_more_goals", "conf": 0.90},
    {"arg": "In closing: 135 international goals, 900+ career goals, 5 Champions League titles, 5 Ballon d'Ors, "
     "titles in 3 countries, and an athletic longevity that defies biology. Cristiano Ronaldo didn't just play "
     "the game — he bent it to his will through sheer force of dedication. The GOAT wears number 7.",
     "attack": ["No player has matched Ronaldo's combined output across all dimensions of the game"],
     "defense": ["Career goals, international goals, and UCL titles are inarguable metrics"],
     "cite": "https://en.wikipedia.org/wiki/Cristiano_Ronaldo", "conf": 0.93},
]

SCORES_A = [
    (8.5, 7.5, 9.0, 7.0), (8.0, 8.0, 8.5, 7.5), (7.5, 7.0, 8.0, 8.0),
    (8.0, 7.5, 8.5, 8.0), (9.0, 8.0, 8.5, 7.5), (9.5, 8.5, 9.0, 8.0),
    (7.0, 6.5, 8.5, 7.0), (7.5, 7.0, 8.0, 8.5), (8.0, 7.5, 8.5, 7.5),
    (8.5, 8.0, 9.0, 8.0),
]
SCORES_B = [
    (8.0, 8.0, 7.5, 7.5), (7.5, 8.5, 7.0, 8.0), (8.5, 7.5, 8.0, 7.0),
    (8.0, 7.0, 7.5, 8.0), (8.0, 7.5, 7.5, 7.0), (7.5, 7.0, 7.5, 8.0),
    (7.0, 6.5, 7.0, 7.5), (8.0, 7.5, 7.5, 7.0), (8.5, 8.0, 7.0, 7.5),
    (8.0, 7.5, 8.0, 7.0),
]
