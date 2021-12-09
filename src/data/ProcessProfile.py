import json
import pandas as pd


def get_profile(kol_name):
    with open(f"data/{kol_name}/{kol_name}.json") as file:
        data = json.load(file)

    profile = data["GraphProfileInfo"]
    kolusername_ls = []
    followers_ls = []
    externalurl_ls = []
    postscount_ls = []
    kolusername_ls.append(profile['username'])
    followers_ls.append(profile['info']['followers_count'])
    externalurl_ls.append(profile['info']['external_url'])
    postscount_ls.append(profile['info']["posts_count"])

    kolprofile_df = pd.DataFrame(
        data = {
            'kol_username': kolusername_ls,
            'followers_count': followers_ls, 
            'postss_count': postscount_ls,
            'external_url':externalurl_ls,
        }
    )
    return kolprofile_df


def get_and_save_profile_df(get_profile_func, kol_list, save_path):

    df = pd.DataFrame()
    for kol_name in kol_list:
        tmp_df = get_profile_func(kol_name)
        df = pd.concat([df, tmp_df], axis=0)
    df.to_csv(save_path, index=False)


if __name__ == "__main__":

    with open("src/configs/ig-config.json", "r") as file:
        ig_config = json.load(file)

    # Get profile Data
    get_and_save_profile_df(
        get_profile,
        kol_list=ig_config["kol_id_list"],
        save_path="data/processed/profiles.csv"
    )

