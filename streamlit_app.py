import streamlit as st
from term_schedule import load_lessons, load_misc_days, create_schedule, gen_calendar

# run command in cmd
# streamlit run "C:\Users\SticksandStones\OneDrive\Documents\CS\Term Schedule\streamlit_app.py"

st.set_page_config(layout="wide")

# md_file_path = r"README.md"

# with open(md_file_path) as f:
#     webpage_text = f.read()

sample_lessons = r"""Introduction
Diagnostic Quiz [#aa6767]
Polynomials [3]
Exponentials [2]
Polynomial Quiz + Introduction to Factoring [1]
Factoring by Grouping [2]
Factoring by axc + b [2]
Test
"""

sample_holidays = r"""2026-09-10 : PD Day 1
2026-09-14 : PD Day 2
2026-09-16 : PD Day 3"""

webpage_text = rf"""
# Term Planner
## What is this?
This is a tool that will automatically generate a calendar based on your inputted lessons, days required for each lesson, and will account for holidays / flex days based on the current calendar year.
## How to use
You will need two information groups. Your lesson titles, and school-board specific holidays

Simply provide a text form of your lesson plans in order, similar to the following.
```
{sample_lessons}
```
Note a couple different features above. Numbers in square brackets such as `[3]` indicate a lesson which spans more than one day. Hex-codes within square brackets such as `[#aa6767]` indicate a custom colour for the specific day. You can choose any colour provided that you know the hex-code for.

The second thing you need is a list of the PD days for your specific board.

I may implement a library of schoolboard days in another iteration.

It should look something like the following.

```
{sample_holidays}
```"""

side = st.sidebar

with side:
    st.markdown("# Advanced Settings")
    reset_button = st.button("Reset Settings")
    STAT_HOLIDAY_COLOUR = st.color_picker("Select the colour for statutory holidays", key = "1", value="#D3C7E6")
    SCHOOL_HOLIDAY_COLOUR = st.color_picker("Select the colour for school holidays", key = "2", value="#F1B598")
    DEFAULT_INSTR_DAY_COLOUR = st.color_picker("Select the colour for default instructional days", key = "3", value="#BEDAE3")

    if reset_button:
        del st.session_state["1"]
        del st.session_state["2"]
        del st.session_state["3"]
        st.session_state["1"] = "#D3C7E6"
        st.session_state["2"] = "#F1B598"
        st.session_state["3"] = "#BEDAE3"
        st.rerun()

settings = {
    "weekends" : False,
    "gap" : 50,
    "round" : 20,
    "rect_x" : 1000,
    "rect_y" : 600,
    "stat_holiday_colour" : STAT_HOLIDAY_COLOUR.capitalize(),
    "school_holiday_colour" : SCHOOL_HOLIDAY_COLOUR.capitalize(),
    "default_day_colour" : DEFAULT_INSTR_DAY_COLOUR.capitalize(),
}

import matplotlib.pyplot as plt
plt.rc('font', size=10)
plt.rc('axes', titlesize=20)

left_column, right_column  = st.columns(2, gap="medium")

with left_column:

    st.markdown(webpage_text)

# sidebar content

with right_column:

# main content - columns
    col1, col2 = st.columns(2)

    with col1:
        lessons_input = st.text_area("Input your lesson schedule here:",
                                    value=sample_lessons)

        loaded_lessons = load_lessons(lessons_input, settings)

    with col2:
        holidays = st.text_area("Input your school holidays / flex days here:",
                                value=sample_holidays)
        
        misc_days = None
        try:
            misc_days = load_misc_days(holidays)
        except ValueError:
            pass

    start_date = st.date_input("Select the starting date for the term.", value="2026-09-07")

# calendar generation
def main():
    df = create_schedule(loaded_lessons, misc_days, settings, start_date=str(start_date))

    fig, ax = gen_calendar(df, config_settings=settings)

    st.pyplot(fig,use_container_width=False)


if not loaded_lessons or not misc_days:
    pass

else:
    with right_column:
        main()

