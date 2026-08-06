from datetime import datetime, timedelta
import pandas as pd
import holidays
import re

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import numpy as np
import textwrap

# ==============================
# USER SETTINGS
# ==============================

# Input lesson file
LESSON_FILE = r"C:\Users\SticksandStones\OneDrive\Documents\CS\Term Schedule\lessons.txt"

# Output file
OUTPUT_FILE = "TeachingSchedule.csv"
OUTPUT_FILE_IMAGE = "TeachingSchedule.jpg"

# Holiday file
HOLIDAY_FILE = r"C:\Users\SticksandStones\OneDrive\Documents\CS\Term Schedule\Holidays.txt"

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
# plt.rcParams['font.family'] = 'Handwriting'
# plt.rc('font', size=16)

settings = {
    "weekends" : False,
    "gap" : 50,
    "round" : 20,
    "rect_x" : 800,
    "rect_y" : 500,
    "stat_holiday_colour" : STAT_HOLIDAY_COLOUR,
    "school_holiday_colour" : SCHOOL_HOLIDAY_COLOUR,
    "default_day_colour" : DEFAULT_INSTR_DAY_COLOUR,
}

def load_misc_days(text):
    other_dates = {}
    for i in text.strip().split("\n"):
        tmp = i.split(" : ")

        tmp_date = datetime.strptime(tmp[0], r"%Y-%m-%d")
        
        other_dates[tmp_date.date()] = tmp[1]
    return other_dates
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


def load_lessons(text, settings):
    lessons = []

    for line in text.splitlines():

        title = None
        duration = 1
        colour = settings['default_day_colour']

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


def create_schedule(lessons, misc_dates, settings):

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
                    "Colour": settings["stat_holiday_colour"]
                })
            
            elif current_date in misc_dates:

                    schedule.append({
                    "Date": current_date,
                    "Lesson #": "",
                    "Lesson": misc_dates[current_date],
                    "Day": "",
                    "Notes": "",
                    "Colour": settings['school_holiday_colour']
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
        x = np.floor((config_settings["rect_x"] + config_settings["gap"]) * ind[0] + (config_settings["rect_x"]) * 0.5)
        y = np.floor((config_settings["rect_y"] + config_settings["gap"]) * (ind[1]) + (config_settings["rect_y"]) * 0.5)
        rect = FancyBboxPatch(
                (x, y),      # (x, y) bottom-left corner
                config_settings["rect_x"],              # width
                config_settings["rect_y"],           # height
                boxstyle=fr"round, pad=-0.05, rounding_size={config_settings["round"]}",
                edgecolor="black",
                facecolor=fr"{row.Colour}",
                linewidth=2
            )

        ax.add_patch(rect)
        ax.text(x + config_settings["gap"] * .5, y + config_settings["gap"]*2, f"{row.Date.day}", fontweight="bold")
        ax.text(x + config_settings["rect_x"]//2, 
                y + + config_settings["rect_y"]//2 + config_settings["gap"], 
                s=f"{textwrap.fill(row.Lesson,13)}",
                ha="center",
                va="center",)

    ax.set_xlim(xmax=(days + 1) * (config_settings["rect_x"] + config_settings["gap"]) - config_settings["gap"])
    ax.set_ylim(ymax=(weeks + 1) * (config_settings["rect_y"] + config_settings["gap"]))
    ax.set_aspect("equal")
    ax.axis("off")
    ax.invert_yaxis()

    plt.title("Schedule", fontweight="bold")
    plt.tight_layout()
    plt.show()

    return fig, ax

if __name__ == "__main__":
    with open(LESSON_FILE, "r", encoding="utf-8") as f:

        lessons = load_lessons(f.read())

    with open(HOLIDAY_FILE, "r", encoding="utf-8") as f:
        pd_days = load_misc_days(f.read())

    df = create_schedule(lessons, pd_days, settings)

    fig, ax = gen_calendar(df)

    df.to_csv(OUTPUT_FILE, index=False)

    print(df)
    print(f"\nSaved to {OUTPUT_FILE}")

    fig.savefig(OUTPUT_FILE_IMAGE)

    print(f"\nSaved to {OUTPUT_FILE_IMAGE}")
