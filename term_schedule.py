from datetime import datetime, timedelta
import pandas as pd
import holidays
import re

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import numpy as np

# ==============================
# USER SETTINGS
# ==============================

# Input lesson file
LESSON_FILE = "lessons.txt"

# Output file
OUTPUT_FILE = "TeachingSchedule.csv"

# Holiday file
HOLIDAY_FILE = "Holidays.txt"

other_dates = {}
with open(HOLIDAY_FILE, 'r', encoding="utf-8") as f:
    text = f.read()
    tmp_text = text.split(r'\n')
    for i in text.split("\n"):
        tmp = i.split(" : ")
        tmp2 = tmp[0].split('-')

        tmp_date = datetime.strptime(tmp[0], "%Y-%m-%d")
        other_dates[tmp_date.date()] = tmp[1]

# Country for holidays
COUNTRY = "CA"          # Canada
PROVINCE = "ON"         # Ontario

# Schedule
START_DATE = "2026-09-07"
END_DATE = None         # Example: "2027-01-30" or None

# Teaching weekdays
# Monday=0 ... Sunday=6
TEACHING_DAYS = [0,1,2,3,4]     # Monday-Friday

# Calendar Settings
STAT_HOLIDAY_COLOUR = "#D3C7E6"
SCHOOL_HOLIDAY_COLOUR = "#F1B598"
DEFAULT_INSTR_DAY_COLOUR = "#BEDAE3"

settings = {
    "weekends" : False,
    "gap" : 50,
    "round" : 20,
    "rect_x" : 400,
    "rect_y" : 350,
}

# ==============================
# function for parsing text lines from lessons, regex is a nightmare and i will never use regex ever again
def groupings(text):

    out = []

    start, end = 0, 0

    if "[" and "]" in text:
        out.append(text[:text.find("[")])
    
    else:
        out.append(text)
        return out

    while True:
        window = text[start:]

        if "[" and "]" in window:

            start = text.find('[')
            end = text.find(']') + 1

            out.append(text[start:end])

            text = text[end + 1:]

        else:
            break
    
    return out


def load_lessons(filename):
    lessons = []

    with open(filename, "r", encoding="utf-8") as f:
        for line in f:

            title = None
            duration = 1
            colour = DEFAULT_INSTR_DAY_COLOUR

            line = line.strip()

            if not line:
                continue
            
            items = groupings(line)

            for i in items:
                if "[" and "]" not in i:
                    title = i.strip()
                
                elif i[1:-1].isnumeric():
                    duration = int(i[1:-1])
                
                elif len(i[1:-1]) > 5 or "#" in i[1:-1]:

                    colour = "#" + i[1:-1].strip("#").upper()

            lessons.append({
                "title": title,
                "duration": duration,
                "colour" : colour
            })

    return lessons


def create_schedule(lessons):

    start = datetime.strptime(START_DATE, "%Y-%m-%d").date()

    if END_DATE:
        end = datetime.strptime(END_DATE, "%Y-%m-%d").date()
    else:
        end = None

    ca_holidays = holidays.country_holidays(
        COUNTRY,
        subdiv=PROVINCE,
        years=range(start.year, start.year + 5)
    )

    schedule = []

    current_date = start

    lesson_number = 1
    lesson_index = 0

    remaining_days = 0
    current_lesson = None

    while lesson_index < len(lessons) or remaining_days > 0:

        if end and current_date > end:
            print("Reached end date.")
            break

        if current_date.weekday() in TEACHING_DAYS:

            if current_date in ca_holidays:

                schedule.append({
                    "Date": current_date,
                    "Lesson #": "",
                    "Lesson": ca_holidays[current_date],
                    "Day": "",
                    "Notes": "",
                    "Colour": STAT_HOLIDAY_COLOUR
                })
            
            elif current_date in other_dates:

                    schedule.append({
                    "Date": current_date,
                    "Lesson #": "",
                    "Lesson": other_dates[current_date],
                    "Day": "",
                    "Notes": "",
                    "Colour": SCHOOL_HOLIDAY_COLOUR
                })
            else:

                if remaining_days == 0:

                    current_lesson = lessons[lesson_index]
                    remaining_days = current_lesson["duration"]
                    lesson_day = 1

                else:

                    lesson_day = current_lesson["duration"] - remaining_days + 1

                schedule.append({
                    "Date": current_date,
                    "Lesson #": lesson_number,
                    "Lesson": current_lesson["title"],
                    "Day": f"{lesson_day}/{current_lesson["duration"]}",
                    "Notes": "",
                    "Colour": current_lesson["colour"]
                })

                remaining_days -= 1

                if remaining_days == 0:
                    lesson_number += 1
                    lesson_index += 1

        current_date += timedelta(days=1)

    return pd.DataFrame(schedule)


def gen_calendar(df, fig=None, ax=None, config_settings=settings):

    if fig is None or ax is None:
        fig, ax  = plt.subplots(figsize=[10,7], dpi=300)

    plt.sca(ax)

    days = 7 if config_settings["weekends"] else 5
    school_days = len(df["Date"])

    weeks = int(np.ceil(school_days / 5))

    start_day = datetime.strptime(str(df["Date"][0]), r"%Y-%m-%d").date()
    start_day_of_week = start_day.weekday()

    day_week_index = [(i, r) for r in range(weeks) for i in range(5)][start_day_of_week:school_days]

    for ind, (i, row) in zip(day_week_index, df.iterrows()):
        print(ind)
        x = np.floor((config_settings["rect_x"] + config_settings["gap"]) * ind[0] + (config_settings["rect_x"]) * 0.5)
        y = np.floor((config_settings["rect_y"] + config_settings["gap"]) * (ind[1]) + (config_settings["rect_y"]) * 0.5)
        print(x,y)
        rect = FancyBboxPatch(
                (x, y),      # (x, y) bottom-left corner
                config_settings["rect_x"],              # width
                config_settings["rect_y"],              # height
                boxstyle=fr"round, pad=-0.05, rounding_size={config_settings["round"]}",
                edgecolor="black",
                facecolor=fr"{row.Colour}",
                linewidth=2
            )

        ax.add_patch(rect)
        ax.text(x + 10, y + 4 + 50, f"{row.Date.day}")

    ax.set_xlim(xmax=(days + 1) * (config_settings["rect_x"] + config_settings["gap"]) - config_settings["gap"])
    ax.set_ylim(ymax=(weeks + 1) * (config_settings["rect_y"] + config_settings["gap"]))
    ax.set_aspect("equal")
    ax.axis("off")
    ax.invert_yaxis()

    plt.title("Schedule")
    plt.show()

    return fig, ax

if __name__ == "__main__":

    lessons = load_lessons(LESSON_FILE)

    df = create_schedule(lessons)

    gen_calendar(df)

    df.to_csv(OUTPUT_FILE, index=False)

    print(df)
    print(f"\nSaved to {OUTPUT_FILE}")