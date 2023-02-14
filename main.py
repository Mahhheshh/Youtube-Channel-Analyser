import streamlit as st
from Utils.Youtube import YouTube, YouTubeException
from Utils.dataframe import Visualize


st.set_page_config(
    page_title="Youtube App",
    page_icon="https://emojipedia-us.s3.amazonaws.com/content/2020/04/05/yt.png",
    initial_sidebar_state="expanded",
    layout="wide",
)

@st.experimental_memo(
    ttl=6000,
    suppress_st_warning=True,
    max_entries=3,
    show_spinner=False
)
def get_data(api_key, c_name):
    yt = YouTube()    
    with st.spinner("Fetching data from YouTube Data API V3"):
        try:
            data = yt.main(c_name, api_key)
        except YouTubeException as e:
            st.warning(e)
            st.stop()
    if data is not None:
        try:
            data = Visualize(data)
        except Exception as e:
            st.warning("Error while creating Pandas Dataframe")
        date = yt.creation_date
        sub_count =  yt.sub_count
        video_count = yt.video_count
        c_name = yt.channel_name
        return data, date, sub_count, video_count, c_name
    else:
        st.warning("Error while creating data")

def whitespace(number_of_lines):
    for _ in range(number_of_lines):
        st.write("\n")

if "log_x" not in st.session_state:
    st.session_state.log_x = False
if "log_y" not in st.session_state:
    st.session_state.log_y = False
if "animate" not in st.session_state:
    st.session_state.animate = False


with st.sidebar:
    st.markdown("""
            # ![image](https://emojipedia-us.s3.amazonaws.com/content/2020/04/05/yt.png)YouTube App
            """)
    with st.form("user-input"):
        API_KEY = st.text_input("Your API KEY", help="Get Key from https://console.cloud.google.com/apis/api/youtube.googleapis.com")
        channel_name = st.text_input("Channel Name")
        submitted = st.form_submit_button("Run")
        if (not submitted) and (API_KEY == "") and (channel_name == ""):
            st.stop()
        else:
            data, date, sub_count, video_count, c_name = get_data(api_key=API_KEY, c_name=channel_name)
            try:
                file = data.save()
            except Exception as e:
                file = None
                st.warning(e)
    st.download_button("Download data as csv", data=file, key="download", file_name=f"{channel_name}.csv", mime="text/csv")

with st.container():
    snippets_col, stats_col, popular_col = st.columns(3)
    with snippets_col:
        st.markdown(
            f"""
            ## Snippet \n
            Channel Name - {c_name.title()}\n
            Creation date - {date}\n
            subscriber count - {sub_count}\n
            No of videos - {data.df.shape[0]}/{video_count}\n
            """
        )
    with stats_col:
        st.markdown(
            f"""
            ## Stats\n
            Likes :heart: - {data.total_likes()}\n
            Comments :speech_balloon: - {data.total_comments()}\n
            Views :eyes: - {data.total_views()}\n
            Content Length :hourglass: - {data.get_content_length()}hrs\n
            """
        )
    with popular_col:
        st.markdown(
            f"""
            ## Most Popular\n
            :heart: - {data.most_liked_video()[0]} :thumbsup: {int(data.most_liked_video()[1])}\n
            :speech_balloon: - {data.most_commented_video()[0]} :speech_balloon: {int(data.most_commented_video()[1])}\n
            :eyes: - {data.most_viewed_video()[0]} :man::woman::boy::girl: {int(data.most_viewed_video()[1])}\n
            """
        )

    st.subheader(f"Top 10 viewed videos from {c_name.title()}")
    top_ten_videos_plot = data.top_ten_videos()
    st.plotly_chart(top_ten_videos_plot, True)

    st.subheader("Video Upload Frequency per Year")
    fre_plot_fig = data.video_upload_freq()
    st.plotly_chart(fre_plot_fig, True)

    st.subheader("Video Duration Vs Number of Views")
    plot_col, seetings_col = st.columns([8, 1]) 
    with seetings_col:
        whitespace(10)
        log_x = st.checkbox("Enable Log_X", value=False, key="Enable_logx")
        log_y = st.checkbox("Enable Log_Y", value=False, key="Enable_logy")
        animate = st.checkbox("Animate Plot", value=False, key="animate_plots")
    if log_x:
        st.session_state.log_x = True
    if log_y:
        st.session_state.log_y = True
    if animate:
        st.session_state.animate = True
    fig = data.duration_vs_views(log_x, log_y, animate)
    with plot_col:  
        st.plotly_chart(fig)

    fig_col, input_col = st.columns([8, 1])
    with input_col:
        whitespace(10)
        year = st.number_input("Select Year", min_value=data.years[0], max_value=data.years[-1],step=1,help=f"{data.years}", value=data.years[-1], key="select_year")
    views_per_year_plot = data.views_per_year(year)
    with fig_col:
        st.plotly_chart(views_per_year_plot, True)

    last_fifty_plot = data.last_fifty_uploads()
    st.plotly_chart(last_fifty_plot, True)