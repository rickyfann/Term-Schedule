import streamlit as st
from term_schedule import load_lessons, load_misc_days, create_schedule, gen_calendar

st.set_page_config(layout="wide")

sample_lessons = r"""Introduction
Diagnostic Quiz [#aa6767]
Polynomials [3]
Exponentials [2]
Polynomial Quiz [q]
Modeling Linear Equations
Solving Linear Systems
Linear Word Problems
Review
Linear Systems Test [t]
Introduction to Quadratics
Factoring by Grouping [2]
Factoring by axc + b [2]
Vertex Form
Quiz [q]
Factoring Word Problems [3]
Quadratics Test [t]
Introduction to Trigonometry
"""

sample_holidays = r"""2026-10-12 : PD Day 1
2026-12-21 : Christmas Break
2026-12-22 : Christmas Break
2026-12-23 : Christmas Break
2026-12-24 : Christmas Break
2026-12-28 : Christmas Break
2026-12-29 : Christmas Break
2026-12-30 : Christmas Break
2026-12-31 : Christmas Break
2027-01-01 : Christmas Break
"""

webpage_text = rf"""
# Term Planner
## What is this?
This is a tool that will automatically generate a calendar based on your inputted lessons, days required for each lesson, and will account for holidays / flex days based on the current calendar year.
## How to use
You will need two pieces of information. Your lesson titles, and school-board specific holidays

Simply provide a text form of your lesson plans in order, similar to the following.
```
{sample_lessons}
```
Note a couple different features above. Numbers in square brackets such as `[3]` indicate a lesson which spans more than one day. Hex-codes within square brackets such as `[#aa6767]` indicate a custom colour for the specific day. You can choose any colour provided that you know the hex-code for. You can also indicate if a day is a quiz or test day with `[q]` or `[t]`

The second thing you need is a list of the PD days for your specific board. I may implement a library of schoolboard days in another iteration.

It should look something like the following.

```
{sample_holidays}
```"""

side = st.sidebar

with side:
    st.markdown("# Advanced Settings")
    reset_button = st.button("Reset Settings")
    STAT_HOLIDAY_COLOUR = st.color_picker("Select the colour for statutory holidays", 
                                                key="1", value="#FFB6A6")
    SCHOOL_HOLIDAY_COLOUR = st.color_picker("Select the colour for school holidays", 
                                                key="2", value="#FFEBD3")
    DEFAULT_INSTR_DAY_COLOUR = st.color_picker("Select the colour for default instructional days", 
                                                key="3", value="#67A2C5")

    DEFAULT_TEST_COLOUR = st.color_picker("Select the colour for quiz days", 
                                                key="4", value="#9BCEC1")
    DEFAULT_QUIZ_COLOUR = st.color_picker("Select the colour for test days", 
                                                key="5", value="#FFC349")
    
    gap_size = st.number_input("Gap size",          key="6", value=50)
    round_size = st.number_input("Round size",      key="7", value=20)
    rect_x_size = st.number_input("Cell x-size",    key="8", value=1000,)
    rect_y_size = st.number_input("Cell y-size",    key="9", value=rect_x_size//2)

    if reset_button:
        del st.session_state["1"]
        del st.session_state["2"]
        del st.session_state["3"]
        st.session_state["1"] = "#FFB6A6"
        st.session_state["2"] = "#FFEBD3"
        st.session_state["3"] = "#9BCEC1"
        st.rerun()

settings = {
    "weekends" : False,
    "gap" : gap_size,
    "round" : round_size,
    "rect_x" : rect_x_size,
    "rect_y" : rect_y_size,
    "stat_holiday_colour" : STAT_HOLIDAY_COLOUR.capitalize(),
    "school_holiday_colour" : SCHOOL_HOLIDAY_COLOUR.capitalize(),
    "default_day_colour" : DEFAULT_INSTR_DAY_COLOUR.capitalize(),
    "default_quiz_colour" : DEFAULT_QUIZ_COLOUR.capitalize(),
    "default_test_colour" : DEFAULT_TEST_COLOUR.capitalize(),
}

import matplotlib.pyplot as plt
plt.rc('font', size=10)
plt.rc('axes', titlesize=20)

left_column, mid_column, right_column  = st.columns(3, gap="medium")

with left_column:

    st.markdown(webpage_text)

# sidebar content

with mid_column:

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

    df = create_schedule(loaded_lessons, misc_days, settings, start_date=str(start_date))

    st.markdown("Below is a table of your data.")
    st.dataframe(df)

# calendar generation
def main():
    fig, ax = gen_calendar(df, config_settings=settings)

    st.pyplot(fig,use_container_width=False)

if not loaded_lessons or not misc_days:
    pass

else:
    with right_column:
        main()

