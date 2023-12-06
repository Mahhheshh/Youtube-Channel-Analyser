import asyncio
import aiohttp


class YoutubeMetaData:
    API_KEY = None
    channel_id = None
    creation_date = None
    channel_name = ""
    video_count = 0
    sub_count = 0


class AsyncYoutube(YoutubeMetaData):
    def __init__(self) -> None:
        self.session = aiohttp.ClientSession()

    async def fetch_data(self, url: str, params: dict) -> dict:
        async with self.session.get(url, params=params) as response:
            if response.status != 200:
                message = await response.json()
                raise Exception(
                    f" StatusCode: {message['error']['code']}, Message: {message['error']['message']}"
                )
            try:
                response = await response.json()
            except Exception as err:
                raise Exception(f"Encountered error while parsing response: {err}")
            return response

    async def fetch_channel_id(self, channel_name: str) -> str:
        base_url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            "part": "id",
            "fields": "items(id(channelId))",
            "q": channel_name,
            "key": self.API_KEY,
            "maxResults": 1,
            "type": "channel",
        }
        try:
            response = await self.fetch_data(base_url, params)
            return response["items"][0]["id"]["channelId"]
        except (IndexError, KeyError):
            raise Exception(
                f"Could not retrieve the channel id for given {channel_name}"
            )
        except Exception as e:
            raise Exception(e)

    async def fetch_channel_info(self, chan_id: str) -> str:
        base_url = "https://www.googleapis.com/youtube/v3/channels"
        params = {
            "part": "snippet,statistics",
            "id": chan_id,
            "key": self.API_KEY,
            "fields": "items(snippet(title,publishedAt),statistics(subscriberCount,videoCount))",
        }
        response = await self.fetch_data(base_url, params)
        try:
            channel_info = response["items"][0]
            self.channel_name = channel_info["snippet"]["title"]
            self.creation_date = channel_info["snippet"]["publishedAt"].split("T")[0]
            self.sub_count = channel_info["statistics"]["subscriberCount"]
            self.video_count = channel_info["statistics"]["videoCount"]
        except (IndexError, KeyError):
            raise Exception("Error while fetching channel information")

    async def fetch_video_ids(self, response_list: list) -> str:
        ids = ""
        for item in response_list:
            try:
                ids += item["id"]["videoId"] + ","
            except KeyError:
                continue
        return ids.removesuffix(",")

    async def fetch_video_details(self, video_ids: str) -> str:
        base_url = "https://www.googleapis.com/youtube/v3/videos?"
        params = {
            "part": "snippet,statistics,contentDetails",
            "id": video_ids,
            "key": self.API_KEY,
            "fields": "items(contentDetails(duration),snippet(title,publishedAt),statistics)",
        }
        response = await self.fetch_data(base_url, params)
        for item in response["items"]:
            del item["statistics"]["favoriteCount"]
            item["statistics"]["Title"] = item.get("snippet").get("title")
            item["statistics"]["publishedAt"] = item.get("snippet").get("publishedAt")
            item["statistics"]["duration"] = item.get("contentDetails").get("duration")
            yield item["statistics"]

    async def fetch_paginated_data(self, request_url: str, params: dict) -> dict:
        while True:
            response = await self.fetch_data(request_url, params)
            yield response

            if "nextPageToken" not in response:
                break

            params.update({"pageToken": response["nextPageToken"]})

    async def scrape_videos(self, channel_id: str, data: list) -> None:
        request_url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            "order": "date",
            "channelId": channel_id,
            "maxResults": 50,
            "key": self.API_KEY,
            "part": "id",
            "fields": "nextPageToken,items(id(videoId))",
        }
        async for response in self.fetch_paginated_data(request_url, params):
            video_ids = await self.fetch_video_ids(response["items"])
            async for video_detail in self.fetch_video_details(video_ids):
                data.append(video_detail)

    async def retrieve_channel_data(
        self, channel_name: str, api_key: str
    ) -> dict | None:
        video_data = []
        channel_data = {}
        self.API_KEY = api_key
        try:
            self.channel_id = await self.fetch_channel_id(channel_name)

            task = asyncio.create_task(self.fetch_channel_info(self.channel_id))
            await self.scrape_videos(self.channel_id, video_data)
            await task
            channel_data = {
                "channel_name": self.channel_name,
                "creation_date": self.creation_date,
                "sub_count": self.sub_count,
                "video_count": self.video_count,
                "data": video_data,
            }
            return channel_data

        except Exception as err:
            raise Exception(err)

        finally:
            await self.session.close()
