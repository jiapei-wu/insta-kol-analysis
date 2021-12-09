import emoji
import json
import pandas as pd
import datetime as dt
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


analyser = SentimentIntensityAnalyzer()


def get_comment(kol_name):
    with open(f"data/{kol_name}/{kol_name}.json") as file:
        data = json.load(file)
    postid_ls = []
    date_ls = []
    id_ls = []
    username_ls = []
    text_ls = []
    for i in range(len(data["GraphImages"])):
        comment = data["GraphImages"][i]["comments"]
        for j in range(len(comment["data"])):
            postid_ls.append(data["GraphImages"][i]['id'])
            date_ls.append(dt.datetime.fromtimestamp(comment["data"][j]["created_at"]).strftime('%Y-%m-%d %H:%M:%S'))
            id_ls.append(comment["data"][j]['id'])
            text_ls.append(comment["data"][j]["text"])
            username_ls.append(comment["data"][j]["owner"]["username"])

    comments = pd.DataFrame(
        data = {
            'post_id':postid_ls,
            'date': date_ls, 
            'id': id_ls,
            'username':username_ls,
            'text': text_ls
        }
    )
    return comments


def extract_emojis(s):
    return ''.join(c for c in s if c in emoji.UNICODE_EMOJI['en'])


def emoji_flag(s):
    if len(s) == 0:
        return 0
    else:
        return 1


def sentiment_analyzer_scores(sentence):
    score = analyser.polarity_scores(sentence)
    return score


def emoji_sentiment_df(comments):
    neg_list = []
    pos_list = []
    neu_list = []
    com_list = []
    emotion_list = comments["emoji"].apply(lambda x: sentiment_analyzer_scores(x))
    for emotion in emotion_list:
        pos_list.append(emotion["pos"])
        neg_list.append(emotion["neg"])
        neu_list.append(emotion["neu"])
        com_list.append(emotion["compound"])
    comments["pos"] = pos_list
    comments["neg"] = neg_list
    comments["neu"] = neu_list
    comments["compound"] = com_list
    return comments


if __name__ == "__main__":

    with open("src/configs/ig-config.json", "r") as file:
        ig_config = json.load(file)
    kol_list=ig_config["kol_id_list"]

    comments = pd.DataFrame()
    for kol in kol_list:
        tmp_comment = get_comment(kol)
        comments = pd.concat([comments, tmp_comment], axis=0)

    comments.loc[:, "emoji"] = comments["text"].apply(lambda x: extract_emojis(x))
    comments.loc[:, "emoji_flag"] = comments["emoji"].apply(lambda x: emoji_flag(x))
    comments = emoji_sentiment_df(comments)
    comments.to_csv("data/processed/comments.csv", index=False)

