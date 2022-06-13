import logging
from re import search
from aiogram import Bot, Dispatcher, executor, types
from wget import download
from numerize import numerize as num
from requests import head
from twittic import TwitterAPI
from twittic.exceptions import (Forbidden, NotFound)


API_TOKEN = '5227234241:AAGyRM4oqaWjyPLzLmm3s7tq0NrZtvKpGPY'
PROXY_URL = 'socks5://127.0.0.1:7890'
INSTA_SESSION = "51209710385%3AGrtJvXtvzFwHDK%3A11"
INSTAGRAM_POST_PATTERN = "^(https?:\\/\\/(?:www\\.)?instagram\\.com(?:\\/(?!.*\\.\\.)(?!.*\\.$)[^\\W][\\w.]{2,29})?\\/(?:p|tv|reel)\\/([^/?#&]+)).*$"
INSTAGRAM_STORY_URL_PATTERN = "^(https?:\\/\\/(?:www\\.)?instagram\\.com(?:\\/(?!.*\\.\\.)(?!.*\\.$)[^\\W][\\w.]{2,29})?\\/stories\\/([^/?#&]+)).*$"
INSTAGRAM_PROFILE_URL_PATTERN = "^(https?:\\/\\/(?:www\\.)?instagram\\.com(?:\\/(?!.*\\.\\.)(?!.*\\.$)[^\\W][\\w.]{2,29})?\\/([^/?#&]+)).*$"
TWITTER_TWEET_PATTERN_WITH_ONE_ESCAPE = "^(https?:\/\/(?:www\.)?(?:mobile\.)?twitter\.com(?:\/(?!.*\.\.)(?!.*\\.$)[^\W][\w.]{2,29})?\/status(es)?\/([\d+]{16,19}))"

Cli = Bot(token=API_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(Cli)

"""@dp.message_handler(regexp=INSTAGRAM_POST_PATTERN)
async def download_post(message: types.Message):
    try:
        media_info = insta.media_info(
            insta.media_pk_from_url(
                message.text)).dict()
        media_type = media_info['media_type']
        caption = media_info['caption_text']
        media_type = media_info['media_type']
        comment_count = media_info['comment_count']
        like_count = media_info['like_count']
        user_info = media_info['user']
        full_caption = "{}\n 💬 {} 👍 {} | <a href='https://www.instagram.com/{}'>👤{}</a>".format(
            caption,
            num.numerize(comment_count),
            num.numerize(like_count),
            user_info["username"],
            user_info['full_name'])
        if media_type in [1, 2]:
            if media_type == 1:
                image_url = media_info["thumbnail_url"]
                await Cli.send_photo(message.chat.id, image_url, caption=full_caption, reply_to_message_id=message.message_id)
            elif media_type == 2:
                video_url = str(media_info["video_url"])
                size = int(head(video_url).headers["Content-Length"])
                if size >= 20971519:
                    status = "File size is too big please wait to download progress will be start"
                    status_message = await message.answer(status)
                    file = download(video_url)
                    await Cli.send_video(message.chat.id, types.InputFile(file), caption=full_caption, reply_to_message_id=message.message_id)
                    await status_message.delete()
                else:
                    await Cli.send_video(message.chat.id, video_url, caption=full_caption, reply_to_message_id=message.message_id)

    except Exception as e:
        logging.error(e)"""

#twitter post downloader by twitterapi
@dp.message_handler(regexp=TWITTER_TWEET_PATTERN_WITH_ONE_ESCAPE)
async def download_tweet(message: types.Message):
    try:
        tweet_url = message.text
        status_id = search(TWITTER_TWEET_PATTERN_WITH_ONE_ESCAPE, tweet_url).group(3)
        print(status_id)
        tweet = TwitterAPI()
        tweet_info = tweet.get_status(status_id)
        print(tweet_info)
        tweet_text = tweet_info['full_text']
        favorite_count = tweet_info['favorite_count']
        retweet_count = tweet_info['retweet_count']
        reply_count = tweet_info['reply_count']
        static_string = "❤️{} |🔁 {} |💬 {}".format(
            num.numerize(favorite_count),
            num.numerize(retweet_count),
            num.numerize(reply_count)
            )
        userinfo_string = "👤{} | <a href='https://twitter.com/{}'>@{}</a>".format(
            tweet_info['user']['name'],
            tweet_info['user']['user_name'],
            tweet_info['user']['user_name']
        )
        caption = "{}\n{}\n{}".format(tweet_text, static_string, userinfo_string)
        has_media = tweet_info['has_media']
        media_count = tweet_info['media_count']
        if has_media:
            if media_count == 1:
                media_type = tweet_info['medias'][0]['type']
                if media_type == "photo":
                    image_url = tweet_info['medias'][0]['url']
                    await Cli.send_photo(message.chat.id, image_url, caption=caption, reply_to_message_id=message.message_id)
                elif media_type == "video" or media_type == "animated_gif":
                    video_url = tweet_info['medias'][0]["url"]
                    size = int(head(video_url).headers["Content-Length"],)
                    if size >= 20971519:
                        status = "File size is too big please wait to download progress will be start"
                        status_message = await message.answer(status)
                        file = download(video_url)
                        await Cli.send_video(message.chat.id, types.InputFile(file), caption=caption, reply_to_message_id=message.message_id)
                        await status_message.delete()
                    else:
                        await Cli.send_video(message.chat.id, video_url, caption=caption, reply_to_message_id=message.message_id)
            elif media_count > 1:
                media_group = types.MediaGroup()
                for i, media in enumerate(tweet_info['medias']):
                    media_type = media['type']
                    image_url = media['url']
                    if i == 0:
                        media_group.attach_photo(image_url, caption=caption)
                        continue
                    media_group.attach_photo(image_url)

                await Cli.send_media_group(message.chat.id, media_group, reply_to_message_id=message.message_id)
    except NotFound:
        await message.reply("Tweet not found")
    except Forbidden:
        await message.reply("Forbidden")
    except Exception as e:
        logging.error(e)
        await message.reply("Something went wrong")
    finally:
        pass

executor.start_polling(dp, skip_updates=True)
