import streamlit as st
from term_schedule import load_lessons, load_misc_days, create_schedule, gen_calendar

# run command in cmd
# streamlit run "C:\Users\SticksandStones\OneDrive\Documents\CS\Term Schedule\streamlit_app.py"

md_file_path = r"C:\Users\SticksandStones\OneDrive\Documents\CS\Term Schedule\README.md"

with open(md_file_path) as f:
    webpage_text = f.read()

st.markdown(webpage_text)

# sidebar content

side = st.sidebar

with side:
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
    "rect_x" : 800,
    "rect_y" : 500,
    "stat_holiday_colour" : STAT_HOLIDAY_COLOUR.capitalize(),
    "school_holiday_colour" : SCHOOL_HOLIDAY_COLOUR.capitalize(),
    "default_day_colour" : DEFAULT_INSTR_DAY_COLOUR.capitalize(),
}

# 
# main content - columns
col1, col2 = st.columns(2)

with col1:
    lessons_input = st.text_area("Input your lesson schedule here:")

    loaded_lessons = load_lessons(lessons_input, settings)

with col2:
    holidays = st.text_area("Input your school holidays / flex days here:")
    misc_days = None
    try:
        misc_days = load_misc_days(holidays)
    except ValueError:
        pass

# calendar generation

def main():
    df = create_schedule(loaded_lessons, misc_days, settings)

    fig, ax = gen_calendar(df, config_settings=settings)

    st.pyplot(fig)


if not loaded_lessons or not misc_days:
    pass

else:
    main()

