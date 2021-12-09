import json
import subprocess
import time
from random import randrange

def get_raw_data(
    kol_id, 
    username, 
    password, 
    profile=True, 
    comments=True, 
    num_posts=1
):
    
    if profile:
        profile = "--profile-metadata"
    else:
        profile = ""
    if comments:
        comments = "--comments"
    else:
        comments = ""
    if num_posts:
        num_posts = "1"
    else:
        num_posts = str(num_posts)

    process = subprocess.Popen(
       [
            "instagram-scraper",
            kol_id,
            "-u", username,
            "-p", password, 
            "-t", "none", 
            comments, 
            profile,
            "-m", num_posts,
             "--destination", "big_data/" + kol_id
        ],
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE
    )
    stdout, stderr = process.communicate()
    print(stderr.decode("utf-8"))


if __name__ == "__main__":

    with open("src/configs/ig-config.json", "r") as file:
        ig_config = json.load(file)

    username = ig_config["username"]
    password = ig_config["password"]
    kol_list = ig_config["kol_id_list"]

    for kol in kol_list:
        get_raw_data(
            kol,
            username=username,
            password=password,
            profile=True,
            comments=True,
            num_posts=20
        )
        break
        time.sleep(randrange(1000, 5000))
    