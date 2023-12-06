import pandas as pd
from datetime import timedelta
import plotly.express as px


class Cleanup:
    df = None

    def to_int(self, int_string: str) -> int:
        try:
            return int(int_string)
        except ValueError:
            return 0

    def apply_int(self) -> None:
        self.df[["Viewcount", "Likecount", "Commentcount"]] = self.df[
            ["Viewcount", "Likecount", "Commentcount"]
        ].map(self.to_int)

    def dates_cleanup(self) -> None:
        # taking published date only
        self.df["Publishedat"] = self.df["Publishedat"].apply(
            lambda string: string.split()[0]
        )
        self.df["Publishedat"] = pd.to_datetime(self.df["Publishedat"])
        self.df["Uploadmonth"] = self.df["Publishedat"].dt.month_name()
        self.df["Uploadday"] = self.df["Publishedat"].dt.day_name()
        self.df["Uploadyear"] = self.df["Publishedat"].dt.year

    def to_sec(slef, time_string: str) -> float | int | None:
        try:
            val = pd.to_datetime(time_string, format="PT%HH%MM%SS")
            return timedelta(
                hours=val.hour, minutes=val.minute, seconds=val.second
            ).total_seconds()
        except Exception:
            pass
        try:
            val = pd.to_datetime(time_string, format="PT%MM%SS")
            return timedelta(minutes=val.minute, seconds=val.second).total_seconds()
        except Exception:
            pass
        try:
            val = pd.to_datetime(time_string, format="PT%HH%MM")
            return timedelta(hours=val.hour, minutes=val.minute).total_seconds()
        except Exception:
            pass
        try:
            val = pd.to_datetime(time_string, format="PT%MM")
            return timedelta(minutes=val.minute).total_seconds()
        except Exception:
            pass
        try:
            val = pd.to_datetime(time_string, format="PT%SS")
            return val.second
        except Exception:
            pass
        try:
            val = pd.to_datetime(time_string, format="PT%HH")
            return timedelta(hours=val.hour).total_seconds()
        except Exception:
            pass

    def apply_sec(self) -> None:
        self.df["Duration"] = self.df["Duration"].apply(self.to_sec)

    def calculate_like_percent(self) -> None:
        self.df["Likepercentage"] = (
            (self.df["Likecount"] / self.df["Viewcount"]) * 100
        ).round(2)

    def calculate_comment_percent(self) -> None:
        self.df["Commentpercentage"] = (
            (self.df["Commentcount"] / self.df["Viewcount"]) * 100
        ).round(2)

    def clean(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        self.df = pd.DataFrame(dataframe)
        self.df.columns = self.df.columns.str.capitalize()
        self.df.fillna(
            value={"Viewcount": 0, "Likecount": 0, "Commentcount": 0}, inplace=True
        )
        self.apply_int()
        self.apply_sec()
        self.dates_cleanup()
        self.calculate_like_percent()
        self.calculate_comment_percent()
        return self.df


class Visualize(Cleanup):
    order = {
        "Uploadmonth": [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ],
        "Uploadday": [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
        ],
    }

    def __init__(self, dataframe: list):
        self.df = self.clean(dataframe)
        self.years = sorted(self.df["Uploadyear"].unique())

    def save(self):
        return self.df.to_csv(encoding="utf-8", index=False)

    def most_viewed_video(self) -> list:
        """Returns most viewed video"""
        return self.df.nlargest(1, "Viewcount")[["Title", "Viewcount"]].values[0]

    def most_liked_video(self) -> list:
        """Returns most liked video"""
        return self.df.nlargest(1, "Likecount")[["Title", "Likecount"]].values[0]

    def most_commented_video(self) -> list:
        """Returns most commented video"""
        return self.df.nlargest(1, "Commentcount")[["Title", "Commentcount"]].values[0]

    def get_content_length(self) -> str:
        """Returns total content length of the given channel"""
        try:
            return f"{self.df['Duration'].sum()/3600:.2f}"
        except TypeError:
            return None

    def total_comments(self) -> int:
        """Returns total number of comments of given channel"""
        try:
            return int(self.df["Commentcount"].sum())
        except TypeError:
            return 0

    def total_likes(self) -> int:
        """Returns total number of likes of given channel"""
        try:
            return int(self.df["Likecount"].sum())
        except TypeError:
            return 0

    def total_views(self) -> int:
        """Returns Total number of views"""
        try:
            return int(self.df["Viewcount"].sum())
        except TypeError:
            return 0

    def duration_vs_views(self, log_x=False, log_y=False, animation=False):
        if not animation:
            fig = px.scatter(
                self.df,
                x="Duration",
                y="Viewcount",
                color="Uploadyear",
                size="Likecount",
                hover_name="Title",
                log_x=log_x,
                log_y=log_y,
                labels={"Viewcount": "Number of Views"},
            )
            return fig
        else:
            fig = px.scatter(
                self.df.sort_values("Uploadyear"),
                x="Duration",
                y="Viewcount",
                color="Uploadyear",
                size="Likecount",
                hover_name="Title",
                title="Duration vs Views",
                animation_frame="Uploadyear",
                animation_group="Duration",
                range_x=[0, self.df["Duration"].nlargest(1).values[0]],
                log_y=True,
            )
            fig.update_layout(transition={"duration": 2000})
            return fig

    def video_upload_freq(self):
        data = self.df.groupby(["Uploadyear", "Uploadmonth"], as_index=False).size()
        fig = px.bar(
            data,
            x="Uploadyear",
            y="size",
            barmode="group",
            color="Uploadmonth",
            category_orders=self.order,
            labels={"size": "Upload Frequency", "Uploadyear": "Year"},
        )
        return fig

    def last_fifty_uploads(self):
        fig = px.area(
            self.df.iloc[:50],
            x="Publishedat",
            y=["Commentcount", "Likecount", "Viewcount"],
            markers="True",
            labels={"Publishedat": "Month"},
            range_x=[],
        )
        return fig

    def views_per_year(self, year: int):
        if year not in self.years:
            year = self.years[-1]
        data = (
            self.df[self.df["Uploadyear"] == year]
            .groupby("Uploadmonth", as_index=False)
            .agg({"Viewcount": "sum"})
        )
        fig = px.bar(
            data,
            x="Uploadmonth",
            y="Viewcount",
            title=f"Video views for year {year}",
            category_orders=self.order,
            labels={"Uploadmonth": "Month", "Viewcount": "Views"},
        )
        return fig

    def top_ten_videos(self):
        data = (
            self.df.nlargest(10, "Viewcount")
            .sort_values("Viewcount")
            .loc[:, ["Title", "Viewcount", "Likecount"]]
        )
        fig = px.bar(
            data,
            x=["Likecount", "Viewcount"],
            y="Title",
            barmode="group",
        )
        fig.update_layout({"legend_title": ""}, yaxis={"title": ""})
        return fig
