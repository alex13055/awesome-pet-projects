import pandas as pd
from datetime import datetime
from config import msg_hist_file


def save_data(message, weather_id):
    saved_df = pd.DataFrame({
        "message_id": weather_id,
        "chat_id": message.chat.id,
        "username": message.chat.username,
        "datetime": datetime.fromtimestamp(message.date).isoformat(timespec='minutes'),
        "message": message.text
    }, index=[0])
    return saved_df


def get_user_history(username):
    try:
        df = pd.read_csv(msg_hist_file)
        df_username = df[df.username.isin(
            [username])].sort_values(by="datetime")
    except FileNotFoundError:
        return None
    else:
        if df_username.empty:
            return None
        return list(df_username.message.head())
