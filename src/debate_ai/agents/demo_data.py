"""Pre-scripted debate transcript — simulates a real 10-ping Messi vs Ronaldo debate."""
from __future__ import annotations

MESSI_ARGS: list[dict] = [
    {"arg": "Lionel Messi has won 8 Ballon d'Or awards — more than any footballer in history. This is not a "
     "subjective opinion or a cherry-picked statistic. It is the most prestigious individual award in the sport, "
     "voted on by coaches, captains, and journalists worldwide across nearly two decades. No other player has "
     "maintained that level of peak performance for so long. Ronaldo's 5 are impressive, but the gap of 3 "
     "trophies is not close — it is a generational difference.",
     "attack": ["No other player has maintained peak performance this long"],
     "defense": ["8 Ballon d'Ors is an objective, voter-verified metric"],
     "cite": "https://en.wikipedia.org/wiki/Ballon_d%27Or", "conf": 0.92},
    {"arg": "My opponent highlights Ronaldo's goal tally, but football is not solely about goals. Messi holds "
     "the record for most assists in La Liga history with 192 — he creates AND finishes at the highest level. "
     "Ronaldo's career assist numbers are roughly half of Messi's in league play. When you can both create and "
     "score, you are a complete footballer. When you can only score, you are a specialist — a great one, but "
     "not the greatest.",
     "attack": ["Ronaldo's goal record ignores playmaking entirely"],
     "defense": ["192 La Liga assists is an all-time record", "Goals + assists combined favours Messi"],
     "cite": "https://www.transfermarkt.com/lionel-messi/assists/spieler/28003", "conf": 0.88},
    {"arg": "Ronaldo claims league diversity proves greatness, yet Messi dominated the strongest league in the "
     "world for 17 consecutive seasons — La Liga had the highest UEFA coefficient throughout that period. He "
     "then moved to PSG and Inter Miami, proving he could adapt to new environments. But staying at Barcelona "
     "was a choice to compete against Real Madrid, Atletico, and the best clubs in Europe every single week. "
     "That is discipline, not limitation. Ronaldo left for Serie A when La Liga got too competitive.",
     "attack": ["Leaving for weaker leagues is not proof of versatility"],
     "defense": ["La Liga was the world's strongest league during Messi's tenure"],
     "cite": "https://en.wikipedia.org/wiki/La_Liga", "conf": 0.85},
    {"arg": "My opponent inflated his Champions League knockout record to 72 goals — the actual figure is 67, "
     "and I trust the fact-checker will confirm this. This kind of casual statistical inflation is exactly why "
     "rhetoric without evidence is dangerous. As for the real numbers: Messi scored 4 goals against Arsenal in "
     "one UCL quarter-final, destroyed Bayern Munich in the 2015 semi-final, and has 135 total UCL goals — "
     "surpassing Ronaldo's total when you include qualifiers.",
     "attack": ["Ronaldo just lied about his own UCL stats — how can we trust any of his claims?"],
     "defense": ["Messi's 2015 semi-final vs Bayern is the greatest individual UCL performance ever"],
     "cite": "https://www.uefa.com/uefachampionsleague/history/rankings/players/goals_scored/", "conf": 0.87},
    {"arg": "Speaking as the 2009 version of myself — at just 22, I won the first-ever sextuple in football "
     "history with Barcelona. Six trophies in one calendar year — Champions League, La Liga, Copa del Rey, "
     "Supercopa de Espana, UEFA Super Cup, and Club World Cup. I scored 38 goals that season including a "
     "header in the Champions League final against Manchester United. While Ronaldo, the same age, was still "
     "adjusting to Real Madrid after his transfer, I was already rewriting history books.",
     "attack": ["2009 Ronaldo had zero major trophies with Real Madrid yet"],
     "defense": ["The 2009 sextuple is unprecedented and unrepeated"],
     "cite": "https://en.wikipedia.org/wiki/2008%E2%80%9309_FC_Barcelona_season", "conf": 0.90},
    {"arg": "The 2022 FIFA World Cup settled this debate permanently. I scored 7 goals and gave 3 assists "
     "across the tournament, won the Golden Ball as best player, and lifted the one trophy that had eluded me "
     "my entire career. In the final against France, I scored twice including the opening penalty and then "
     "again in extra time. Ronaldo's World Cup record? Zero finals appearances, zero semi-final goals in his "
     "entire career, and a quarter-final exit in tears against Morocco in what was likely his last World Cup.",
     "attack": ["Ronaldo has never reached a World Cup final"],
     "defense": ["World Cup 2022 Golden Ball + trophy is the ultimate individual + team achievement"],
     "cite": "https://en.wikipedia.org/wiki/2022_FIFA_World_Cup", "conf": 0.94},
    {"arg": "Let me introduce a dimension of football that Ronaldo cannot even compete in. Messi's dribbling "
     "numbers are extraordinary: over 4,200 successful dribbles across all competitions with a 73% success "
     "rate — higher than any forward in the history of the sport. Football is artistry and expression at its "
     "highest level. Ronaldo's physical approach — crossing, heading, penalties — is effective, yes, but it "
     "is industrial football. Messi plays the beautiful game. Ronaldo plays the efficient one.",
     "attack": ["Ronaldo's playing style is mechanistic and lacks creative genius"],
     "defense": ["Dribbling is the purest individual skill metric in football"],
     "cite": "https://fbref.com/en/players/d70ce98e/Lionel-Messi", "conf": 0.86},
    {"arg": "My opponent just claimed I won 'zero trophies in two years after leaving Barcelona.' That is a "
     "blatant lie. I won Ligue 1 with PSG in my first full season and later won the Leagues Cup and the MLS "
     "Supporters' Shield with Inter Miami. The fact-checker can verify. Meanwhile, Messi has won 36 team "
     "trophies at club level — more than Ronaldo's 34. The quiet leader outperforms the loud one where it "
     "counts: the trophy cabinet. But I don't need to fabricate my record to make that point.",
     "attack": ["Ronaldo just lied about my post-Barcelona career — credibility destroyed"],
     "defense": ["36 club trophies vs 34 is an objective comparison"],
     "cite": "https://en.wikipedia.org/wiki/Lionel_Messi#Career_statistics", "conf": 0.83},
    {"arg": "Every advanced metric in modern football analytics ranks Messi as the most complete attacker in "
     "history. Expected assists, progressive passes, shot-creating actions, through balls per 90 — all favour "
     "Messi by substantial margins over every other player, including Ronaldo. These are not opinions; they are "
     "mathematical models built on millions of data points. Ronaldo excels at finishing — one dimension. Messi "
     "excels at creating, dribbling, passing, and finishing simultaneously. That is the difference between "
     "greatness and the greatest.",
     "attack": ["Ronaldo is a specialist; Messi is a generalist who also specialises"],
     "defense": ["xA, progressive passes, and SCA data all favour Messi overwhelmingly"],
     "cite": "https://fbref.com/en/players/d70ce98e/Lionel-Messi#all_stats_standard", "conf": 0.89},
    {"arg": "In closing: 8 Ballon d'Ors, a World Cup, 36 club trophies, 192 La Liga assists, the most "
     "successful dribbler the sport has ever seen, and the respect of every opponent who ever faced him. "
     "Throughout this debate, my opponent has resorted to inflating his statistics and fabricating claims about "
     "my career. I have let the facts — and the fact-checker — speak for themselves. Messi didn't just play "
     "football — he redefined what was possible with a ball at his feet. The debate is settled.",
     "attack": ["No statistical or narrative dimension favours Ronaldo over Messi"],
     "defense": ["The totality of evidence is overwhelming"],
     "cite": "https://en.wikipedia.org/wiki/Lionel_Messi", "conf": 0.95},
]

RONALDO_ARGS: list[dict] = [
    {"arg": "Cristiano Ronaldo holds the all-time men's international scoring record with 135 goals for "
     "Portugal — no player in history has scored more for their country. This is not a club record inflated "
     "by a dominant team around him. This is pure individual brilliance on the world stage, where you play "
     "with the teammates your nation gives you, not the ones your club's billions can buy. Messi's Argentina "
     "record pales in comparison in both goals and consistency.",
     "attack": ["International goals prove individual merit without club-level support systems"],
     "defense": ["135 international goals is an objective, FIFA-verified record"],
     "cite": "https://en.wikipedia.org/wiki/International_goals_scored_by_Cristiano_Ronaldo", "conf": 0.91},
    {"arg": "My opponent cites Ballon d'Or count, but awards are voted by journalists with well-documented "
     "recency and popularity biases. What cannot be disputed with journalist opinions: Ronaldo won league "
     "titles in England, Spain, and Italy — three of the top five leagues in the world. He dominated the "
     "Premier League with Manchester United, ruled La Liga alongside Real Madrid, and conquered Serie A with "
     "Juventus. Messi spent 17 years at one club in one league. That is comfort, not courage. That is safety, "
     "not greatness.",
     "attack": ["Ballon d'Or voting is subjective and influenced by media narratives"],
     "defense": ["Titles in 3 different top leagues proves adaptability Messi never tested"],
     "cite": "https://en.wikipedia.org/wiki/Cristiano_Ronaldo#Honours", "conf": 0.87},
    {"arg": "Messi claims La Liga was the strongest league — yet Ronaldo dominated the Champions League "
     "knockout stage with 72 goals, including hat-tricks against Bayern Munich, Atletico Madrid, and "
     "Juventus. When the pressure is at its highest, when the entire continent watches, Ronaldo delivers. "
     "Meanwhile, Messi scored in only 2 of his last 8 UCL knockout ties before leaving Barcelona. The "
     "infamous collapses against Roma and Liverpool — surrendering 3-0 and 4-0 leads — happened on Messi's "
     "watch. Ronaldo never collapsed like that. Not once.",
     "attack": ["Messi disappeared in critical UCL knockout matches repeatedly"],
     "defense": ["72 UCL knockout goals is 25 more than Messi's tally in the same stages"],
     "cite": "https://www.uefa.com/uefachampionsleague/history/rankings/players/goals_scored/", "conf": 0.89},
    {"arg": "My opponent is now disputing my Champions League figures, but let me pivot to what truly "
     "matters: Ronaldo has 5 Champions League titles across two different clubs — Manchester United AND Real "
     "Madrid. Converting penalties under Champions League knockout pressure, with 80,000 people watching and "
     "your entire season on the line, is itself an elite skill. Ronaldo scored in two separate Champions "
     "League finals. His penalty record in UCL shootouts is perfect. That is ice in the veins — a quality "
     "Messi has never demonstrated under equivalent European pressure.",
     "attack": ["Messi has only 4 UCL titles, all with one historically dominant club"],
     "defense": ["5 UCL titles with 2 clubs is a record that stands on its own"],
     "cite": "https://en.wikipedia.org/wiki/UEFA_Champions_League_records_and_statistics", "conf": 0.88},
    {"arg": "As the 2013 version of myself — I scored 69 goals in a single calendar year for Real Madrid, "
     "won my second Ballon d'Or, and was the undisputed best player on the planet. While 2009 Messi had "
     "Barcelona's legendary tiki-taka system with Xavi, Iniesta, and Pep Guardiola orchestrating every move, "
     "I was carrying Real Madrid virtually alone as the sole creative and finishing force. My 2013 was pure "
     "individual dominance. Messi's 2009 was a system player excelling within a system built specifically "
     "around him by the greatest tactical mind in football.",
     "attack": ["2009 Messi benefited from Xavi, Iniesta, and Pep's system"],
     "defense": ["2013 Ronaldo was a one-man army with less midfield support than Messi ever had"],
     "cite": "https://en.wikipedia.org/wiki/2013_Ballon_d%27Or", "conf": 0.86},
    {"arg": "My opponent raises the 2022 World Cup as his trump card — one tournament in a 20-year career. "
     "Let me counter with a story of true leadership: Ronaldo led Portugal to the Euro 2016 title, the first "
     "major trophy in Portuguese football history. He did it despite going off injured in the final at minute "
     "25. From the touchline, in tears, he coached and inspired his teammates to defeat France on their home "
     "soil. Leadership isn't just playing well — it's making your team believe they can win without you.",
     "attack": ["One World Cup does not erase a career of Champions League dominance"],
     "defense": ["Euro 2016 was the first major title for Portugal — a smaller football nation"],
     "cite": "https://en.wikipedia.org/wiki/UEFA_Euro_2016_final", "conf": 0.84},
    {"arg": "Dribbling statistics are a nostalgia metric for fans who confuse entertainment with "
     "effectiveness. Football is decided by goals, trophies, and decisive moments — not by how many times "
     "you nutmegged a defender in a league match you were already winning 3-0. Ronaldo evolved from the "
     "flashiest dribbler at Manchester United into the most lethal striker in history. That transformation — "
     "winger to striker to target man — demonstrates unmatched tactical intelligence. Messi has played the "
     "same position his entire career. Ronaldo reinvented himself three times.",
     "attack": ["Dribbling does not win matches; goals and trophies do"],
     "defense": ["Ronaldo's tactical evolution across 3 phases of his career is unprecedented"],
     "cite": "https://en.wikipedia.org/wiki/Cristiano_Ronaldo#Playing_style", "conf": 0.82},
    {"arg": "Messi claims 36 club trophies, but consider the context: after leaving Barcelona, Messi won "
     "zero trophies in his first two seasons outside the Camp Nou bubble. Zero. He went to PSG, surrounded "
     "by Neymar and Mbappe, and won nothing of note in Europe. Meanwhile, Ronaldo has 34 trophies across "
     "FOUR different clubs in THREE countries. Messi's trophies came overwhelmingly from one golden era of "
     "Barcelona dominance with Xavi, Iniesta, Busquets, Neymar, and Suarez doing the heavy lifting.",
     "attack": ["Messi's trophy count is inflated by Barcelona's golden generation"],
     "defense": ["Winning across 4 clubs in 3 countries proves Ronaldo elevates any team"],
     "cite": "https://en.wikipedia.org/wiki/Cristiano_Ronaldo#Club", "conf": 0.85},
    {"arg": "Advanced metrics favour whoever the metric-designer admires. Expected goals, expected assists, "
     "progressive passes — these are mathematical models built by statisticians, many of whom grew up "
     "watching Barcelona. Here is a metric that cannot be gamed or modelled: Ronaldo has scored 900+ career "
     "goals — the highest verified tally in the history of professional football. Goals are the universal "
     "currency of this sport. Everything else is analytics packaging designed to tell whatever story the "
     "analyst wants to tell. 900 goals tells its own story.",
     "attack": ["xA and progressive passes are designer metrics; goals are the universal truth"],
     "defense": ["900+ goals is the highest verified career total in football history"],
     "cite": "https://en.wikipedia.org/wiki/List_of_men%27s_footballers_with_500_or_more_goals", "conf": 0.90},
    {"arg": "In closing: 135 international goals, 900+ career goals, 5 Champions League titles, 5 Ballon "
     "d'Ors, league titles in 3 countries, Euro 2016 from the touchline, and an athletic longevity that "
     "defies biology — still scoring at 39 when most players have retired. Cristiano Ronaldo didn't just "
     "play the game — he bent it to his will through sheer force of dedication, discipline, and an "
     "unrelenting refusal to accept anything less than greatness. The GOAT wears number 7.",
     "attack": ["No player has matched Ronaldo's combined output across all dimensions"],
     "defense": ["Career goals, international goals, and UCL titles are inarguable metrics"],
     "cite": "https://en.wikipedia.org/wiki/Cristiano_Ronaldo", "conf": 0.93},
]

SCORES_A = [
    (8.5, 7.5, 9.0, 7.0), (8.0, 8.0, 8.5, 7.5), (7.5, 7.0, 8.0, 8.0),
    (9.0, 8.0, 9.0, 9.0), (9.0, 8.0, 8.5, 7.5), (9.5, 8.5, 9.0, 8.0),
    (7.5, 7.0, 8.5, 7.0), (9.0, 7.5, 8.5, 9.0), (8.0, 7.5, 8.5, 7.5),
    (8.5, 8.0, 9.0, 8.0),
]
SCORES_B = [
    (8.0, 8.0, 7.5, 7.5), (7.5, 8.5, 7.0, 8.0), (8.5, 8.0, 8.5, 7.5),
    (8.0, 7.0, 7.5, 7.0), (8.0, 7.5, 7.5, 7.0), (7.5, 7.0, 7.5, 8.0),
    (7.0, 6.5, 7.0, 7.5), (8.5, 8.0, 8.0, 7.5), (8.5, 8.0, 7.0, 7.5),
    (8.0, 7.5, 8.0, 7.0),
]
