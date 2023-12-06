import asyncio
import streamlit as st
from Utils import AsyncYoutube, Visualize, rewaitable

st.set_page_config(
    page_title="Youtube App",
    page_icon="https://emojipedia-us.s3.amazonaws.com/content/2020/04/05/yt.png",
    initial_sidebar_state="expanded",
    layout="wide",
)


@st.cache_resource(ttl=1800, max_entries=3, show_spinner=False)
@rewaitable
async def get_data(channel_name: str, api_key: str) -> tuple[Visualize, dict]:
    yt = AsyncYoutube()
    with st.spinner("Fetching data from YouTube Data API V3"):
        try:
            data = await yt.retrieve_channel_data(
                channel_name=channel_name, api_key=api_key
            )
            visualize_obj = Visualize(data.pop("data"))
            return (visualize_obj, data)
        except Exception as err:
            st.error(err)
            st.stop()


def whitespace(number_of_lines):
    for _ in range(number_of_lines):
        st.write("\n")


async def main():
    if "log_x" not in st.session_state:
        st.session_state.log_x = False
    if "log_y" not in st.session_state:
        st.session_state.log_y = False
    if "animate" not in st.session_state:
        st.session_state.animate = False

    with st.sidebar:
        st.markdown(
            """
                # ![image](https://emojipedia-us.s3.amazonaws.com/content/2020/04/05/yt.png)YouTube App
                """
        )
        with st.form("user-input"):
            submitted = False
            API_KEY = st.text_input(
                "Your API KEY",
                help="Get Key from https://console.cloud.google.com/apis/api/youtube.googleapis.com",
            )
            channel_name = st.text_input("Channel Name")
            submitted = st.form_submit_button("Run")
            file = None
            if (submitted) and (API_KEY == "") or (channel_name == ""):
                st.stop()
            else:
                try:
                    visualize_obj, channel_info = await get_data(
                        channel_name=channel_name, api_key=API_KEY
                    )
                    file = visualize_obj.save()
                except Exception as error:
                    st.warning(error)
                    st.stop()
        if file:
            st.download_button(
                "Download data as csv",
                data=file,
                key="download",
                file_name=f"{channel_name}.csv",
                mime="text/csv",
            )

    with st.container():
        snippets_col, stats_col, popular_col = st.columns(3)
        with snippets_col:
            st.markdown(
                f"""
                ## Snippet \n
                Channel Name - {channel_info.get('channel_name').title()}\n
                Creation date - {channel_info.get('creation_date')}\n
                subscriber count - {channel_info.get('video_count')}\n
                No of videos - {visualize_obj.df.shape[0]}/{channel_info.get('video_count')}\n
                """
            )
        with stats_col:
            st.markdown(
                f"""
                ## Stats\n
                Likes :heart: - {visualize_obj.total_likes()}\n
                Comments :speech_balloon: - {visualize_obj.total_comments()}\n
                Views :eyes: - {visualize_obj.total_views()}\n
                Content Length :hourglass: - {visualize_obj.get_content_length()}hrs\n
                """
            )
        with popular_col:
            st.markdown(
                f"""
                ## Most Popular\n
                :heart: - {visualize_obj.most_liked_video()[0]} :thumbsup: {int(visualize_obj.most_liked_video()[1])}\n
                :speech_balloon: - {visualize_obj.most_commented_video()[0]} :speech_balloon: {int(visualize_obj.most_commented_video()[1])}\n
                :eyes: - {visualize_obj.most_viewed_video()[0]} :man::woman::boy::girl: {int(visualize_obj.most_viewed_video()[1])}\n
                """
            )

        st.subheader(
            f"Top 10 viewed videos from {channel_info.get('channel_name').title()}"
        )
        top_ten_videos_plot = visualize_obj.top_ten_videos()
        st.plotly_chart(top_ten_videos_plot, True)

        st.subheader("Video Upload Frequency per Year")
        fre_plot_fig = visualize_obj.video_upload_freq()
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
        fig = visualize_obj.duration_vs_views(log_x, log_y, animate)
        with plot_col:
            st.plotly_chart(fig)

        fig_col, input_col = st.columns([8, 1])
        with input_col:
            whitespace(10)
            year = st.number_input(
                "Select Year",
                min_value=visualize_obj.years[0],
                max_value=visualize_obj.years[-1],
                step=1,
                help=f"{visualize_obj.years}",
                value=visualize_obj.years[-1],
                key="select_year",
            )
        views_per_year_plot = visualize_obj.views_per_year(year)
        with fig_col:
            st.plotly_chart(views_per_year_plot, True)

        last_fifty_plot = visualize_obj.last_fifty_uploads()
        st.plotly_chart(last_fifty_plot, True)


if __name__ == "__main__":
    asyncio.run(main())
