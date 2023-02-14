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
        request_url =  "https://www.googleapis.com/youtube/v3/search?"
        params = {
            "part":"id",
            "fields":"items(id(channelId))",
            "q":channel_name,
            "key":self.API_KEY,
            "type":"channel"
        }
        response_body = get(request_url, params=params)
        if response_body.status_code != 200:
            raise YouTubeException("", response_body.status_code)
        else:
            try:
                response_body = response_body.json()
                return response_body["items"][0]["id"]["channelId"]
            except (IndexError, KeyError) as err:
                print(err)
        return None

    def get_ids(self, items: list) -> str:
        def get_video_info(video_ids: str) -> list:
            """Returns list containing video information"""
            data = []
            request_url = "https://youtube.googleapis.com/youtube/v3/videos?"
            params = {
                "part":"snippet,statistics,contentDetails",
                "id":video_ids,
                "key":self.API_KEY,
                "fields":"items(contentDetails(duration),snippet(title,categoryId,publishedAt),statistics)",
            }
            response_body = get(request_url, params)
            if response_body.status_code == 200:
                try:
                    response_body = response_body.json()
                except Exception as err:
                    print(err)
                    return None
                for item in response_body["items"]:
                    item["statistics"]["Title"] = item.get("snippet").get("title")
                    item["statistics"]["categoryId"] = item.get("snippet").get("categoryId")
                    item["statistics"]["publishedAt"] = item.get("snippet").get("publishedAt")
                    item["statistics"]["duration"] = item.get("contentDetails").get("duration")
                    del item["statistics"]["favoriteCount"]
                    data.append(item["statistics"])
                return data
            else:
                raise YouTubeException("Error While Getting Video Information!")
        records = []
        for item in items:
            try:
                records.append(item['id']['videoId'])
            except KeyError:
                YouTubeException("Video Id Not Found")
        return get_video_info(','.join(records))

    def extract_details(self, channel_info):
        """Helper method for YouTube.get_channel_info()"""
        try:
            date = channel_info["snippet"]["publishedAt"].split("T")[0]
            sub_count = channel_info["statistics"]["subscriberCount"]
            video_count = channel_info["statistics"]["videoCount"]
            title = channel_info["snippet"]["title"]
        except KeyError:
            video_count, sub_count, date, title = 0, 0, 0, ""
        self.channel_name, self.creation_date, self.sub_count, self.video_count = title, date, sub_count, video_count

    def get_channel_info(self, chan_id):
        """Return Channel name, Channel creation date, Channel subscriber count, Channels total video upload count"""
        request_url = "https://www.googleapis.com/youtube/v3/channels"
        params = {
            "part":"snippet,statistics",
            "id":chan_id,
            "key":self.API_KEY,
            "fields":"items(snippet(title,publishedAt),statistics(subscriberCount,videoCount))"
        }
        response_body = get(request_url, params)
        if response_body.status_code == 200:
            try:
                response_body = response_body.json()
                channel_info = response_body["items"][0]
                return self.extract_details(channel_info)
            except:
                return None
        else:
            raise YouTubeException("", response_body.status_code)
        
    def main(self, channel_name: str, api_key:str) -> list:
        """Return Visualize object"""
        self.API_KEY = api_key
        data = []
        request_url = "https://www.googleapis.com/youtube/v3/search?"

        self.chan_id = self.get_channel_id(channel_name)

        params = {
            "order":"date",
            "channelId": self.chan_id,
            "maxResults":50,
            "key":self.API_KEY,
            "part":"id",
            "fields":"nextPageToken,items(id(videoId))"
        }

        if self.chan_id is None:
            return None
        response = get(request_url, params)
        if response.status_code != 200:
            return None
        try:
            response = response.json()
        except Exception:
            print("Json err") 
        self.get_channel_info(self.chan_id)
        while "nextPageToken" in response.keys():            
            data.extend(self.get_ids(response["items"]))
            next_token = response.get("nextPageToken", None)
            if next_token is not None:
                params.update({"pageToken":next_token})
                response = get(request_url, params).json()
        data.extend(self.get_ids(response["items"]))
        return data


class YouTubeException(Exception):
    def __init__(self, message: str, code: int=None) -> None:
        self.message = message
        if code:
            self.code = code
            self.throw_error()
        else:
            super().__init__(self.message)

    def throw_error(self) -> Exception:
        match self.code:
            case 400:
                super().__init__("The API request was malformed, Invalid API KEY")
            case 401:
                super().__init__("The request requires authentication and the API credentials provided are invalid or missing.")
            case 403:
                super().__init__("The API request is not authorized to access the requested resource or the API quota has been exceeded")
            case 404:
                super().__init__("The requested resource is not found.")
            case 429:
                super().__init__("The API quota has been exceeded")
            case 500:
                super().__init__("The server encountered an unexpected error while fulfilling the request. Retry the request")