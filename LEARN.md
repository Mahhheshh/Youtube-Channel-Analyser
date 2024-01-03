### Motivation

While watching YouTube I got stumbled upon this [insightful video](https://youtu.be/oYVLxaxn3Dg?si=hfcy9qAgrBdSDhZR), which inspired me to build a web app that would allow users to analyze YouTube channels and gain insights. 

### Development Process

#### Data Collection

##### YouTube API Integration
To efficiently manage YouTube API calls, I have encapsulated these calls within the `AsyncYoutube` class.

##### Obtaining Channel ID
Recognizing that a channel's name isn't sufficient for data retrieval, I established a process to convert channel names into unique channel IDs. Utilizing the API endpoint `https://www.googleapis.com/youtube/v3/search`, YouTube provides a list of channels matching the name, allowing extraction of the channel ID from the first item in the list.

##### Retrieving Channel Information
A subsequent API call to `https://www.googleapis.com/youtube/v3/channels`, passing the channel ID as a parameter, facilitated the retrieval of channel data. The `YouTubeMetadata` class, nested within `AsyncYoutube`, dynamically assigned class attributes upon acquiring channel information such as Name, Public Video count, Subscribes etc.

##### Fetching Video Information
Making individual API calls for each video is both slow and API costly.
To adress This, We make a single API call to `https://www.googleapis.com/youtube/v3/search` with the channel ID, this will return a list of all videos uploaded. 
Concatenating video IDs as a comma-separated string enabled a single API call to `https://www.googleapis.com/youtube/v3/videos`, returning data for multiple videos. These data sets were then appended to a list for further processing. This way we can get information about 50 videos(YouTube Api limit) in a single API call.

#### Data Analysis

##### Utilizing the Pandas Library
The pandas library played a pivotal role in data analysis. Converting the acquired data into a pandas dataframe facilitated robust data cleaning and analysis. Ultimately, the processed data was transformed into a JSON string for seamless integration with the web app.

#### `Cleanup` and `Visualize` Classes

In the `Cleanup` class, data underwent various cleaning processes, including conversion of string values to integers and adaptation of YouTube date formats to Python date formats. Additional columns like `Uploadday`, `Uploadmonth`, and `Uploadyear` were created.

Meanwhile, within the `Visualize` class, interactive data visualizations were generated using the `plotly.express` library. These visual representations included:

- A scatter plot showcasing video duration versus views received.
- A bar plot illustrating video upload frequency.
- An area plot depicting data from the last 50 videos.
- Bar plots showcasing views per year and the top ten videos.

#### Web App Deployment

##### Leveraging the Streamlit Framework
To serve the web app seamlessly, the project leveraged the capabilities of the streamlit framework. The application was deployed using the `streamlit run main.py` command for user access and interaction.