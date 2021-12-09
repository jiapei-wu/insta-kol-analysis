import json
import time
import os

import pandas as pd 
import numpy as np
import datetime as dt


def counter(url_list):
    image_count = 0
    video_count = 0
    for url in url_list:
        if "mp4" in url:
            video_count += 1
        elif "mov" in url:
            video_count += 1
        elif "png" in url:
            image_count += 1
        elif "jpg" in url:
            image_count += 1
        elif "jpeg" in url:
            image_count += 1
        elif "svg" in url:
            image_count += 1
    return image_count, video_count


def get_post(kol_name):
    with open(f"data/{kol_name}/{kol_name}.json") as file:
        data = json.load(file)
    owner_ls = []
    like_ls = []
    comment_ls = []
    postid_ls = []
    tags_ls = []
    time_ls = []
    image_ls = []
    video_ls = []
    post = data["GraphImages"]
    for i in range(len(data["GraphImages"])):
        like_ls.append(post[i]["edge_media_preview_like"]["count"])
        comment_ls.append(post[i]["edge_media_to_comment"]["count"])
        postid_ls.append(post[i]["id"])
        tags_ls.append(post[i]["tags"])
        owner_ls.append(post[i]["username"])
        time_ls.append(dt.datetime.fromtimestamp(post[i]["taken_at_timestamp"]).strftime('%Y-%m-%d %H:%M:%S'))
        url_list = post[i]["urls"]
        image_count, video_count = counter(url_list)
        image_ls.append(image_count)
        video_ls.append(video_count)
        

    post_df = pd.DataFrame(
        data = {
            'kol_username':owner_ls,
            'post_id': postid_ls,
            'likes_count': like_ls, 
            'comments_count': comment_ls,
            'tags':tags_ls,
            'time':time_ls,
            'videos': video_ls,
            'images': image_ls
        }
    )
    
    return post_df


if __name__ == "__main__":

    with open("src/configs/ig-config.json", "r") as file:
        ig_config = json.load(file)
    kol_list=ig_config["kol_id_list"]

    posts = pd.DataFrame()
    for kol in kol_list:
        tmp_post = get_post(kol)
        posts = pd.concat([posts, tmp_post], axis=0)

    posts.to_csv("data/processed/posts.csv", index=False)

