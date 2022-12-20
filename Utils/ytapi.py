from requests import get

class YouTube:
    chan_id = None
    API_KEY = None
    creation_date = None
    channel_name = None
    video_uploads = 0
    sub_count = 0
    
    def get_channel_id(self, channel_name: str) -> str:
        """Returns channel id for given channel name"""
        request_url =  f"""https://www.googleapis.com/youtube/v3/search?part=id&fields=items(id(channelId))&q={channel_name}&type=channel&key={self.API_KEY}"""
        response_body = get(request_url)
        if response_body.status_code == 200:
            try:
                response_body = response_body.json()
                return response_body["items"][0]["id"]["channelId"]
            except Exception as err:
                print(err)
                return None 
        else:
            print("Error while getting channel id")
            return None
        
    def get_ids(self, items: list) -> str:
        """Returns String of video ids containing 50 ids"""
        records = []
        for item in items:
            try:
                records.append(item['id']['videoId'])
            except KeyError:
                print("Video id not found!!!!")
        return ','.join(records)

    def get_video_info(self, video_ids: str, data: list) -> list:
        """Returns list containing video information """
        res_body = get(f"""https://youtube.googleapis.com/youtube/v3/videos?part=snippet,statistics,contentDetails&id={video_ids}&key={self.API_KEY}&fields=items(contentDetails(duration),snippet(title,categoryId,publishedAt),statistics)""")
        if res_body.status_code == 200:
            try:
                res_body = res_body.json()
            except Exception as err:
                print(err)
            for item in res_body["items"]:
                item["statistics"]["Title"] = item.get("snippet").get("title")
                item["statistics"]["categoryId"] = item.get("snippet").get("categoryId")
                item["statistics"]["publishedAt"] = item.get("snippet").get("publishedAt")
                item["statistics"]["duration"] = item.get("contentDetails").get("duration")
                del item["statistics"]["favoriteCount"]
                data.append(item["statistics"])
            return data
        else:
            print("Error while getting video information")
            return None

    def extract_details(self, channel_info):
        """Helper method for YouTube.get_channel_info()"""
        try:
            date = channel_info["snippet"]["publishedAt"].split("T")[0]
            sub_count = channel_info["statistics"]["subscriberCount"]
            video_count = channel_info["statistics"]["videoCount"]
            title = channel_info["snippet"]["title"]
        except KeyError:
            video_count, sub_count, date = 0, 0, 0
        return (title, date, sub_count, video_count)

    def get_channel_info(self, chan_id):
        """Return Channel name, Channel creation date, Channel subscriber count, Channels total video upload count"""
        try:
            response = get(f"""https://www.googleapis.com/youtube/v3/channels?part=snippet,statistics&id={chan_id}&key={self.API_KEY}&fields=items(snippet(title,publishedAt),statistics(subscriberCount,videoCount))""").json()
            channel_info = response["items"][0]
            return self.extract_details(channel_info)
        except:
            return None
        
    def main(self, channel_name: str, api_key:str) -> list:
        """Return Visualize object"""
        if api_key is not None:
            self.API_KEY = api_key
        self.chan_id = self.get_channel_id(channel_name)
        # print(self.chan_id)
        if self.chan_id is not None:
            video_id_url = f"""https://www.googleapis.com/youtube/v3/search?order=date&channelId={self.chan_id}&maxResults=50&key={self.API_KEY}&part=id&fields=nextPageToken,items(id(videoId))"""
        else:
            return None
        response = get(video_id_url).json()
        data = []
        self.channel_name, self.creation_date, self.sub_count, self.video_count = self.get_channel_info(self.chan_id)
        while True:
            if "nextPageToken" in response.keys():
                video_ids = self.get_ids(response["items"])
                self.get_video_info(video_ids, data)
                next_token = response.get("nextPageToken", None)
                if next_token is not None:
                    response = get(f"{video_id_url}&pageToken={next_token}").json()
            else:
                video_ids = self.get_ids(response["items"])
                self.get_video_info(video_ids, data)
                return data