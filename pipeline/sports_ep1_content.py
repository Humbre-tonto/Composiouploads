# Sports Trivia Ep. 1 — 30 Questions across 8 sport categories
# Each entry: (question, [options], correct_index)

CATEGORIES = [
    {
        "name": "Football",
        "emoji": "⚽",
        "color_top": (10, 80, 20),
        "color_bot": (5, 140, 40),
        "questions": [
            ("Which country has won the most FIFA World Cup titles?",
             ["Germany", "Brazil", "Argentina", "Italy"], 1),
            ("How many players are on the field per team in football?",
             ["9", "10", "11", "12"], 2),
            ("What is the maximum number of substitutes allowed in a FIFA World Cup match?",
             ["3", "4", "5", "6"], 2),
            ("Which player has scored the most goals in World Cup history?",
             ["Pelé", "Ronaldo (Brazil)", "Just Fontaine", "Miroslav Klose"], 3),
            ("In what year was the first FIFA World Cup held?",
             ["1928", "1930", "1934", "1938"], 1),
            ("Which club has won the most UEFA Champions League titles?",
             ["Barcelona", "Bayern Munich", "AC Milan", "Real Madrid"], 3),
        ]
    },
    {
        "name": "Basketball",
        "emoji": "🏀",
        "color_top": (140, 40, 10),
        "color_bot": (200, 70, 0),
        "questions": [
            ("How high is an NBA basketball hoop from the ground?",
             ["9 feet", "10 feet", "11 feet", "12 feet"], 1),
            ("Which player has the most NBA championship rings?",
             ["LeBron James", "Bill Russell", "Michael Jordan", "Kareem Abdul-Jabbar"], 1),
            ("How many points is a three-pointer worth in basketball?",
             ["2", "3", "4", "5"], 1),
            ("Which country invented basketball?",
             ["USA", "Canada", "UK", "Australia"], 1),
            ("How long is an NBA game quarter?",
             ["10 minutes", "12 minutes", "15 minutes", "20 minutes"], 1),
        ]
    },
    {
        "name": "Tennis",
        "emoji": "🎾",
        "color_top": (100, 140, 0),
        "color_bot": (150, 200, 20),
        "questions": [
            ("Which Grand Slam tournament is played on clay courts?",
             ["Wimbledon", "US Open", "French Open", "Australian Open"], 2),
            ("How many Grand Slams did Roger Federer win in his career?",
             ["18", "20", "22", "24"], 1),
            ("What does 'love' mean in tennis scoring?",
             ["15 points", "Advantage", "Zero", "Game point"], 2),
            ("Which player has won the most Wimbledon singles titles (men)?",
             ["Pete Sampras", "Novak Djokovic", "Roger Federer", "Björn Borg"], 2),
        ]
    },
    {
        "name": "Swimming",
        "emoji": "🏊",
        "color_top": (0, 60, 140),
        "color_bot": (0, 100, 200),
        "questions": [
            ("Which swimmer holds the record for most Olympic gold medals of all time?",
             ["Mark Spitz", "Michael Phelps", "Ryan Lochte", "Ian Thorpe"], 1),
            ("How long is an Olympic swimming pool?",
             ["25 meters", "50 meters", "75 meters", "100 meters"], 1),
            ("Which swimming stroke is the fastest?",
             ["Breaststroke", "Backstroke", "Butterfly", "Freestyle (front crawl)"], 3),
        ]
    },
    {
        "name": "Baseball",
        "emoji": "⚾",
        "color_top": (20, 30, 100),
        "color_bot": (40, 60, 160),
        "questions": [
            ("How many strikes does a batter get before striking out?",
             ["2", "3", "4", "5"], 1),
            ("How many innings are in a standard MLB game?",
             ["7", "8", "9", "10"], 2),
            ("Which baseball team has won the most World Series titles?",
             ["Boston Red Sox", "Los Angeles Dodgers", "New York Yankees", "Chicago Cubs"], 2),
        ]
    },
    {
        "name": "Boxing",
        "emoji": "🥊",
        "color_top": (100, 10, 10),
        "color_bot": (160, 20, 20),
        "questions": [
            ("How many rounds are in a professional world championship boxing match?",
             ["10", "12", "15", "20"], 1),
            ("Which boxer was known as 'The Greatest'?",
             ["Joe Frazier", "Muhammad Ali", "Mike Tyson", "Sugar Ray Leonard"], 1),
            ("What does 'TKO' stand for in boxing?",
             ["Total Knockout", "Technical Knockout", "Timed Knockout", "Tactical Knockout"], 1),
        ]
    },
    {
        "name": "Athletics",
        "emoji": "🏃",
        "color_top": (60, 0, 120),
        "color_bot": (100, 20, 180),
        "questions": [
            ("What is the distance of a marathon?",
             ["26.2 miles", "25 miles", "30 km", "40 km"], 0),
            ("Who holds the world record for the 100m sprint?",
             ["Justin Gatlin", "Yohan Blake", "Usain Bolt", "Tyson Gay"], 2),
            ("How many hurdles are there in a 110m hurdles race?",
             ["8", "10", "12", "14"], 1),
        ]
    },
    {
        "name": "Olympics",
        "emoji": "🏆",
        "color_top": (80, 60, 0),
        "color_bot": (160, 120, 0),
        "questions": [
            ("How many rings are on the Olympic flag?",
             ["4", "5", "6", "7"], 1),
            ("In what year were the first modern Olympic Games held?",
             ["1892", "1896", "1900", "1904"], 1),
            ("Which country has won the most Olympic medals all-time?",
             ["China", "Russia", "Germany", "United States"], 3),
        ]
    },
]

# Flat question list with category info for chapters
def get_all_questions():
    qs = []
    for cat in CATEGORIES:
        for q, opts, ci in cat["questions"]:
            qs.append({
                "category": cat["name"],
                "emoji": cat["emoji"],
                "q": q, "opts": opts, "ci": ci,
                "color_top": cat["color_top"],
                "color_bot": cat["color_bot"],
            })
    return qs
