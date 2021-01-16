import os
import pickle
from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd
from bs4 import BeautifulSoup

from facebook_activity_visualiser.activity_data_model import ActivityData


def load_data(facebook_data_dir: Path) -> ActivityData:
    """
    Loads and parses likes, comments and posts from a Facebook archive.
    :param facebook_data_dir: path to uncompressed Facebook archive. Ex: data/facebook-johndoe
    :return: Data class storing DataFrames for likes, comments and posts
    """
    data = load_serialised_activity_data()
    if data:
        return data

    likes_on_pages = parse_file(facebook_data_dir/"likes_and_reactions/pages.html")
    likes_on_posts_comments = parse_file(facebook_data_dir/"likes_and_reactions/posts_and_comments.html")
    likes = pd.concat([likes_on_pages, likes_on_posts_comments], axis=0)
    likes = likes.reset_index()

    posts_and_comments_on_groups = parse_file(facebook_data_dir / "groups/your_posts_and_comments_in_groups.html")

    comments_public = parse_file(facebook_data_dir / "comments/comments.html")
    comments_on_groups = posts_and_comments_on_groups.loc[
        (posts_and_comments_on_groups['activity'].str.contains("replied|commented", na=False)) &
        (posts_and_comments_on_groups['text'].str.contains("Group:", na=False))]
    comments = pd.concat([comments_public, comments_on_groups], axis=0)
    comments = comments.reset_index()

    posts_public = parse_file(facebook_data_dir / "posts/your_posts_1.html")
    posts_on_groups = posts_and_comments_on_groups.loc[
        posts_and_comments_on_groups['text'].str.contains("posted", na=False)]
    posts = pd.concat([posts_public, posts_on_groups], axis=0)
    posts = posts.reset_index()

    data = ActivityData(likes=likes, comments=comments, posts=posts)
    serialise_activity_data(data)

    return data


def parse_file(filepath: Path) -> pd.DataFrame:
    """
    Parse a Facebook data archive HTML file. Supports files containing likes, comments and posts.
    :param filepath:
    :return:
    """
    items = []
    with filepath.open() as f:
        soup = BeautifulSoup(f, "html.parser")
    contents = soup.find("div", class_="_4t5n")
    contents_items = contents.find_all("div", class_="uiBoxWhite")

    for item in contents_items:
        activity = item.find("div", class_="_2lel")
        activity_text = item.find("div", class_="_2let")
        date_time = item.find("div", class_="_2lem")

        row = {
            'activity': activity.text if activity else None,
            'text': activity_text.text if activity_text else None,
            'datetime': datetime.strptime(date_time.get_text(), '%b %d, %Y, %I:%M %p') if date_time else None
        }
        if all(not item for item in row.values()):
            raise ValueError(f"This file cannot be parsed: {filepath}")
        items.append(row)
    return pd.DataFrame(items)


def serialise_activity_data(data: ActivityData) -> None:
    pickle.dump(data, open(Path("data/activity_data.pkl"), 'wb'))


def load_serialised_activity_data() -> Optional[ActivityData]:
    try:
        data = pickle.load(open(Path("data/activity_data.pkl"), 'rb'))

        if not (data.likes.empty and data.comments.empty and data.posts.empty):
            return data
        return None
    except OSError:
        pass
