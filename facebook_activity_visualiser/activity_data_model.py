import pandas as pd


class ActivityData:
    """
    Stores Facebook data, specifically likes, comments and posts as DataFrames.
    Has utility methods to retrieve counts and frequencies.
    """
    def __init__(self,
                 likes: pd.DataFrame = pd.DataFrame(),
                 comments: pd.DataFrame = pd.DataFrame(),
                 posts: pd.DataFrame = pd.DataFrame()):
        self.likes = likes
        self.comments = comments
        self.posts = posts

    def get_count_likes(self) -> int:
        return self.likes.shape[0]

    def get_count_comments(self) -> int:
        return self.comments.shape[0]

    def get_count_posts(self) -> int:
        return self.posts.shape[0]

    def get_monthly_count_likes(self) -> pd.Series:
        return self.likes.resample('M', on='datetime').sum()

    def print_overview(self):
        print(f"Total # Likes: {self.get_count_likes()}")
        print(f"Total # Comments: {self.get_count_comments()}")
        print(f"Total # Posts: {self.get_count_posts()}")
