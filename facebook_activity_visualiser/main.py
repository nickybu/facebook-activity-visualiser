from pathlib import Path

from facebook_activity_visualiser.load_and_prepare_data import load_data
from facebook_activity_visualiser.activity_data_model import ActivityData

if __name__ == '__main__':
    data = load_data(Path("data/facebook-nickybuttigieg"))
    data.print_overview()

    monthly_likes = data.get_monthly_count_likes()
    print(monthly_likes)
