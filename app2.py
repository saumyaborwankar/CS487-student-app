import streamlit as st
import streamlit_authenticator as stauth
import yaml
import time
from db_funcs import *
import streamlit as st
import datetime as dt
import plotly.express as px
from modules import data
import os,calendar  # Core Python Module
from datetime import datetime  # Core Python Module
import plotly.graph_objects as go  # pip install plotly
import streamlit as st  # pip install streamlit
from streamlit_option_menu import option_menu  # pip3 install streamlit-option-menu
import database as db  # local import
from deta import Deta  # pip3 install deta
from dotenv import load_dotenv
# hashed_passwords = stauth.Hasher(['123', '456']).generate()
# print(hashed_passwords)
import pandas as pd
app_name="Hello"
def read_tasks():
    df=pd.read_csv("tasks.csv")
    tasks=df['task']
    value=df['value']
    return tasks,value

# tasks =["I agree"]
t=[]
def color_df(val):
	if val == "Done":
		color = "green"
	elif val == "Doing":
		color = "orange"
	else:
		color = "red"

	return f'background-color: {color}'

def count_down(ts):
    with st.empty():
        while ts:
            mins, secs = divmod(ts, 60)
            time_now = '{:02d}:{:02d}'.format(mins, secs)
            st.header(f"{time_now}")
            time.sleep(1)
            ts -= 1
    st.header("Time Up!")
def health_managment():
    global app_name
    st.title(app_name)
    dt_now = dt.datetime.now()
    dt_str = dt_now.strftime("%Y-%m-%d")
    dt_weekday = dt_now.strftime("%A")
    dt_day = dt_now.strftime("%-d")
    dt_month = dt_now.strftime("%b")

    st.markdown(f" Today is {dt_weekday} - {dt_day} of {dt_month}.")


    #########
    # SIDEBAR
    st.sidebar.title("Track Control")

    # LOAD/CREATE FILE
    sidebar_data_container = st.sidebar.expander(
        "💫 Load or Create a file", expanded=True
    )

    with sidebar_data_container:
        st.markdown("### 🗂 Load data")
        sidebar_uploaded_file = st.file_uploader(
            "Choose your .csv file"
        )

        st.markdown("### ✨ or create a new file")

        sidebar_create_file_name = st.text_input(
            "Choose a file name", value="habit_data.csv"
        )
        sidebar_create_file_button = st.button("* Create new file")


    # INPUT
    sidebar_input_container = st.sidebar.expander(
        "💪🏼 How did you do today?", expanded=False
    )

    with sidebar_input_container:
        # Choose Date
        sidebar_date = st.date_input(
            "📅 Which day you want to make an entry for?",
            max_value=dt_now
        )

        # Slider Metrics
        sidebar_sleep = st.slider(
            "😴 How much did you sleep?",
            min_value=0.0, max_value=12.0, value=8.0, step=0.1
        )
        sidebar_mood = st.slider(
            "🌈 What mood were you in?",
            min_value=1, max_value=7, value=5, step=1
        )
        sidebar_energy = st.slider(
            "⚡️ How energized did you feel?",
            min_value=1, max_value=7, value=5, step=1
        )

        # Radio Button Metrics
        sidebar_food = st.radio(
            "🥕 Did you eat healthy?", (0, 1)
        )
        sidebar_exercise = st.radio(
            "🏃‍♀️ Did you exercise?", (0, 1)
        )
        sidebar_meditation = st.radio(
            "🧘‍ Did you meditate?", (0, 1)
        )
        sidebar_reading = st.radio(
            "📖 Did you read?", (0, 1)
        )
        sidebar_journaling = st.radio(
            "✏️ Did you journal?", (0, 1)
        )
        sidebar_learning = st.radio(
            "🎓 Did you learn something new?", (0, 1)
        )
        sidebar_work = st.radio(
            "🏆 Did you work towards your goals?", (0, 1)
        )

        # "add data" button
        add_row = st.button("➕ Add values")


    ######
    # DATA
    @st.cache(allow_output_mutation=True)
    def get_file(input_file):
        HabitData = data.HabitData()
        HabitData.load(file=input_file)
        return HabitData


    @st.cache(allow_output_mutation=True)
    def create_file(filename):
        HabitData = data.HabitData()
        HabitData.create(filename=filename)
        return HabitData


    # LOAD/CREATE DATA
    if sidebar_uploaded_file is not None:
        st.markdown("🔄 Data loaded.")
        HabitData = get_file(sidebar_uploaded_file)

    elif sidebar_create_file_button:
        st.markdown("✨ File created.")
        HabitData = create_file(sidebar_create_file_name)

    else:
        st.markdown("### Create or load a file to continue.")
        st.stop()


    # ADD DATA
    if add_row:
        append_dict = {
            "date": sidebar_date,
            "sleep": sidebar_sleep,
            "mood": sidebar_mood,
            "energy": sidebar_energy,
            "food": sidebar_food,
            "exercise": sidebar_exercise,
            "meditation": sidebar_meditation,
            "reading": sidebar_reading,
            "journaling": sidebar_journaling,
            "learning": sidebar_learning,
            "work": sidebar_work,
        }

        HabitData.add(append_dict=append_dict)


    # REMOVE DATA
    # add function to sidebar
    sidebar_remove_data_container = st.sidebar.expander(
        "🗑 Delete data", expanded=False
    )

    with sidebar_remove_data_container:
        try:
            opt = HabitData.data.date.unique()
        except AttributeError:
            opt = [None]

        selectbox_remove_date = st.selectbox(
            "Remove data:", options=opt
        )
        drop_row = st.button("➖ Remove values")

    if drop_row:
        HabitData.drop(date_index=selectbox_remove_date)


    # DOWNLOAD DATA
    sidebar_download_data = st.sidebar.button("⬇️ Download data")

    if sidebar_download_data:
        st.sidebar.markdown(HabitData.download(), unsafe_allow_html=True)


    # ######
    # # KPIs

    # mean_container = st.beta_container()  # , current_container = st.columns([1, 1])
    # with mean_container:
    #     mean_dict = HabitData.data.mean().to_dict()
    #     for k, v in mean_dict.items():
    #         st.markdown(f"""### {k}:""")
    #         st.markdown(f"""# {v}""")

    # st.dataframe(pd.DataFrame(HabitData.data.mean().to_dict(), index=[0]))
    HabitData.data["avg_performance"] = HabitData.data.set_index("date").sum(axis=1).div(28).values


    #########
    # VISUALS
    # dataframe
    data_container = st.expander("Display your data", expanded=True)

    with data_container:
        dataframe = st.dataframe(HabitData.data)


    # line plot
    st.markdown("### Plot your habits over time")

    plot_container, info_container = st.columns([8, 2])

    with info_container:
        opt = HabitData.data.columns.to_list()
        opt.remove("date")
        selectbox_columns = st.selectbox(
            "Select which column to plot:",
            options=opt
        )

        m = round(HabitData.data[selectbox_columns].mean(), 2)

        metric_dict = {
            "mood": "lvl",
            "energy": "lvl",
            "sleep": "h",
            "food": "%",
            "exercise": "%",
            "meditation": "%",
            "reading": "%",
            "journaling": "%",
            "learning": "%",
            "work": "%",
        }

        # {metric_dict.get(selectbox_columns)}
        st.markdown(f"""# avg // {m}""")

    with plot_container:
        px_chart = px.bar(
            HabitData.data,
            x="date",
            y=selectbox_columns,
            # marginal="box", hover_data=HabitData.data.columns
        )
        st.plotly_chart(px_chart, use_container_width=True)
    
def timer():
    time_minutes = st.number_input('Enter the time in minutes ', min_value=1, value=25)
    time_in_seconds = time_minutes * 60
    if st.button("START"):
        count_down(int(time_in_seconds))
def time_managment():
    global app_name
    st.title(app_name)
    # col1, col2, col3 = st.columns([1,1,1])
    time_fin_hel =st.sidebar.selectbox("Select a page", ["Task","Timer", "Priority"])
    # with col1:
    # if st.button('Pomodoro Timer'):
    #     timer()
    if(time_fin_hel=="Task"):
        choice = st.sidebar.selectbox("Tasks", ["Create Task ✅","Update Task 👨‍💻","Delete Task ❌", "View Tasks' Status 👨‍💻"])
        create_table()
        
        if choice == "Create Task ✅":
            st.subheader("Add Item")
            col1,col2 = st.columns(2)

            with col1:
                task = st.text_area("Task To Do")

            with col2:
                task_status = st.selectbox("Status",["ToDo","Doing","Done"])
                task_due_date = st.date_input("Due Date")

            if st.button("Add Task"):
                add_data(task,task_status,task_due_date)
                st.success("Added Task \"{}\" ✅".format(task))
                st.balloons()

        elif choice == "Update Task 👨‍💻":
            st.subheader("Edit Items")
            with st.expander("Current Data"):
                result = view_all_data()
                clean_df = pd.DataFrame(result,columns=["Task","Status","Date"])
                st.dataframe(clean_df.style.applymap(color_df,subset=['Status']))

            list_of_tasks = [i[0] for i in view_all_task_names()]
            selected_task = st.selectbox("Task",list_of_tasks)
            task_result = get_task(selected_task)

            if task_result:
                task = task_result[0][0]
                task_status = task_result[0][1]
                task_due_date = task_result[0][2]

                col1,col2 = st.columns(2)

                with col1:
                    new_task = st.text_area("Task To Do",task)

                with col2:
                    new_task_status = st.selectbox(task_status,["To Do","Doing","Done"])
                    new_task_due_date = st.date_input(task_due_date)

                if st.button("Update Task 👨‍💻"):
                    edit_task_data(new_task,new_task_status,new_task_due_date,task,task_status,task_due_date)
                    st.success("Updated Task \"{}\" ✅".format(task,new_task))

                with st.expander("View Updated Data 💫"):
                    result = view_all_data()
                    # st.write(result)
                    clean_df = pd.DataFrame(result,columns=["Task","Status","Date"])
                    st.dataframe(clean_df.style.applymap(color_df,subset=['Status']))

        elif choice == "Delete Task ❌":
            st.subheader("Delete")
            with st.expander("View Data"):
                result = view_all_data()
                # st.write(result)
                clean_df = pd.DataFrame(result,columns=["Task","Status","Date"])
                st.dataframe(clean_df.style.applymap(color_df,subset=['Status']))

            unique_list = [i[0] for i in view_all_task_names()]
            delete_by_task_name =  st.selectbox("Select Task",unique_list)
            if st.button("Delete ❌"):
                delete_data(delete_by_task_name)
                st.warning("Deleted Task \"{}\" ✅".format(delete_by_task_name))

            with st.expander("View Updated Data 💫"):
                result = view_all_data()
                # st.write(result)
                clean_df = pd.DataFrame(result,columns=["Task","Status","Date"])
                st.dataframe(clean_df.style.applymap(color_df,subset=['Status']))

        else:
            with st.expander("View All 📝"):
                result = view_all_data()
                # st.write(result)
                clean_df = pd.DataFrame(result,columns=["Task","Status","Date"])
                st.dataframe(clean_df.style.applymap(color_df,subset=['Status']))

            with st.expander("Task Status 📝"):
                task_df = clean_df['Status'].value_counts().to_frame()
                task_df = task_df.reset_index()
                st.dataframe(task_df)

                p1 = px.pie(task_df,names='index',values='Status', color='index',
                    color_discrete_map={'ToDo':'red',
                                        'Done':'green',
                                        'Doing':'orange'})
                st.plotly_chart(p1,use_container_width=True)

    # st.markdown("<br><hr><center>Made with ❤️ by <a href='mailto:ralhanprateek@gmail.com?subject=ToDo WebApp!&body=Please specify the issue you are facing with the app.'><strong>Prateek Ralhan</strong></a></center><hr>", unsafe_allow_html=True)
    if(time_fin_hel=="Timer"):
        time_minutes = st.number_input('Enter the time in minutes ', min_value=1, value=25)
        time_in_seconds = time_minutes * 60
        if st.button("START"):
            count_down(int(time_in_seconds))

    if(time_fin_hel=="Priority"):
        st.checkbox('Submit financial documents')
        st.checkbox('Apply scholarship')

def finance_managment():
    global app_name
    st.title(app_name)
    incomes = ["Total Points"]
    expenses = ["Rent", "Utilities", "Groceries", "Transport", "Food"]
    currency = ""
    page_title = "Income and Expense Tracker"
    page_icon = ":dollar:"  # emojis: https://www.webfx.com/tools/emoji-cheat-sheet/
    layout = "centered"
    # --------------------------------------

    # st.set_page_config(page_title=page_title, page_icon=page_icon, layout=layout)
    # st.title(page_title + " " + page_icon)

    # --- DROP DOWN VALUES FOR SELECTING THE PERIOD ---
    years = [datetime.today().year-1, datetime.today().year, datetime.today().year + 1]
    months = list(calendar.month_name[1:])


    # --- DATABASE INTERFACE ---
    def get_all_periods():
        items = db.fetch_all_periods()
        periods = [item["key"] for item in items]
        return periods

    # --- HIDE STREAMLIT STYLE ---
    hide_st_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                header {visibility: hidden;}
                </style>
                """
    st.markdown(hide_st_style, unsafe_allow_html=True)

    # --- NAVIGATION MENU ---
    selected = option_menu(
        menu_title=None,
        options=["Data Entry", "Data Visualization"],
        icons=["text-center", "bar-chart-steps"],  # https://icons.getbootstrap.com/
        orientation="horizontal",
    )


    # --- INPUT & SAVE PERIODS ---
    if selected == "Data Entry":
        st.header(f"Data Entry in {currency}")
        with st.form("entry_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            col1.selectbox("Select Month:", months, key="month")
            col2.selectbox("Select Year:", years, key="year")

            "---"
            with st.expander("Total Points"):
                for income in incomes:
                    st.number_input(f"{income}:", min_value=0, format="%i", step=10, key=income)
            with st.expander("Expenses"):
                for expense in expenses:
                    st.number_input(f"{expense}:", min_value=0, format="%i", step=10, key=expense)
            with st.expander("Comment"):
                comment = st.text_area("", placeholder="Enter a comment here ...")

            "---"
            submitted = st.form_submit_button("Save Data")
            if submitted:
                period = str(st.session_state["year"]) + "_" + str(st.session_state["month"])
                incomes = {income: st.session_state[income] for income in incomes}
                expenses = {expense: st.session_state[expense] for expense in expenses}
                db.insert_period(period, incomes, expenses, comment)
                #st.write(f"incomes: {incomes}")
                #st.write(f"expenses: {expenses}")
                st.success("Data saved!")


    # --- PLOT PERIODS ---
    if selected == "Data Visualization":
        st.header("Data Visualization")
        with st.form("saved_periods"):
            period = st.selectbox("Select Period:", get_all_periods())
            #period = st.selectbox("Select Period:" ,["2022_July"])
            submitted = st.form_submit_button("Plot Period")
            if submitted:
                # Get data from database
                # period_data = db.get_period(period)
                # comment = period_data.get("comment")
                # expenses = period_data.get("expenses")
                # incomes = period_data.get("incomes")
                comment = "Testing"
                incomes= {'Total Points': 7000}
                expenses= {'Rent': 1500, 'Utilities': 200, 'Groceries': 100, 'Transport': 90, 'Food': 350} 
                # Create metrics
                total_income = sum(incomes.values())
                total_expense = sum(expenses.values())
                remaining_budget = total_income - total_expense
                col1, col2, col3 = st.columns(3)
                col1.metric("Total Points", f"{total_income} {currency}")
                col2.metric("Points Used", f"{total_expense} {currency}")
                col3.metric("Remaining Points", f"{remaining_budget} {currency}")
                st.text(f"Comment: {comment}")

                # Create sankey chart
                label = list(incomes.keys()) + ["Total Points"] + list(expenses.keys())
                source = list(range(len(incomes))) + [len(incomes)] * len(expenses)
                target = [len(incomes)] * len(incomes) + [label.index(expense) for expense in expenses.keys()]
                value = list(incomes.values()) + list(expenses.values())

                # Data to dict, dict to sankey
                link = dict(source=source, target=target, value=value)
                node = dict(label=label, pad=20, thickness=30, color="#F4C430")
                data = go.Sankey(link=link, node=node)

                # Plot it!
                fig = go.Figure(data)
                fig.update_layout(margin=dict(l=0, r=0, t=5, b=5))
                st.plotly_chart(fig, use_container_width=True)
    
def main_page():
    global app_name
    st.write(f'Welcome *{st.session_state["name"]}*')
    st.sidebar.header('Select App')
    page = st.sidebar.selectbox("Select a page", ["Time Managment","Health Managment","Finance Managment"])
    if page == "Time Managment":
        app_name="Time Managment"
        time_managment()
    if page == "Health Managment":
        app_name="Health Managment"
        health_managment()
    if page == "Finance Managment":
        app_name="Finance Managment"
        finance_managment()


def login():
    with open('config.yaml') as file:
        config = yaml.load(file, Loader=yaml.SafeLoader)
    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
        config['preauthorized']
    )

    name, authentication_status, username = authenticator.login('Login', 'main')
    if authentication_status:
        authenticator.logout('Logout', 'main')
        main_page()
    elif authentication_status == False:
        st.error('Username/password is incorrect')
    elif authentication_status == None:
        st.warning('Please enter your username and password')



login()
