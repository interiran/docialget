import requests
from .exceptions import (TooManyRequests, TwitterException, HTTPException, BadRequest, Unauthorized, Forbidden, NotFound, TwitterServerError)
from operator import itemgetter

#class for twitter api without registering an app
class TwitterAPI:
    def __init__(self, access_token=None, proxies=None):
        if access_token is None:
            access_token = "AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"
        else:
            access_token = access_token
        
        self.access_token = access_token
        self.session = requests.Session()
        self.base_url = "https://api.twitter.com/1.1/"
        self.headers = {
            "Authorization": "Bearer " + self.access_token,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36"
        }
        self.proxies = {}
        if proxies is not None:
            self.proxies = proxies
            self.session.proxies.update(self.proxies)
        
        self.params = {
            "cards_platform": "Web-12",
            "include_cards": 1,
            "include_reply_count": 1,
            "include_user_entities": 0,
            "tweet_mode": "extended"
        }
    
    def request(self, url, method, params=None, headers=None):
        try:

            if params is None:
                params = {}
            
            if headers is None:
                headers = {}
            
            try:
                response = self.session.request(url=url, method=method, headers=headers, params=params, timeout=10)
            except:
                raise TwitterException("Failed to send request")
            
            if response.status_code == 200:
                return response
            elif response.status_code == 400:
                raise BadRequest(response)
            elif response.status_code == 401:
                raise Unauthorized(response)
            elif response.status_code == 403:
                raise Forbidden(response)
            elif response.status_code == 404:
                raise NotFound(response)
            elif response.status_code == 429:
                raise TooManyRequests(response)
            elif response.status_code >= 500:
                raise TwitterServerError(response)
            elif response.status_code and 200 >= response.status_code >= 300:
                raise HTTPException(response)
        finally:
            self.session.close()
    
    def get_token(self):
        url = self.base_url + "guest/activate.json"
        print("Getting Public Token...")
        try:
            response = self.request(url, method="POST", headers=self.headers).json()
        except Exception as e:
            raise TwitterException(e)

        return response["guest_token"]

    
    def media_parser(self, media):
        if media["type"] == "photo":
            return {
                "type": "photo",
                "url": media["media_url_https"],
            }
        elif media["type"] == "video" or media["type"] == "animated_gif":
            #get biggest bitraite url from list of variants
            if "video_info" in media:
                try:
                    variants = media["video_info"]["variants"]
                    #Delete variants that do not have a bitraite
                    variants = [variant for variant in variants if "bitrate" in variant]
                    #sort varints by bitrait if content_type is video/mp4 and has bitrate
                    video_url = max(variants, key=itemgetter("bitrate"))["url"]
                    thumbnail_url = media["media_url_https"]
                    return {
                        "type": media["type"],
                        "url": video_url,
                        "thumbnail_url": thumbnail_url
                    }
                except:
                    return {
                        "type": "video",
                        "url": media["media_url_https"],
                    }
                    
        

    def get_status(self, tweet_id):
        try:
            url = self.base_url + "statuses/show.json"
            params = self.params
            params["id"] = tweet_id
            params["x_guest_token"] = self.get_token()
            response = self.request(url, method="GET", params=params, headers=self.headers).json()
            full_text = response["full_text"]
            data = {
                "full_text": full_text,
                "reply_count": response["reply_count"],
                "retweet_count": response["retweet_count"],
                "favorite_count": response["favorite_count"],
                "has_media": "extended_entities" in response,
                "media_count": len(response["extended_entities"]["media"]) if "extended_entities" in response else 0,
                "medias": [self.media_parser(media_sec) for media_sec in response["extended_entities"]["media"]] if "extended_entities" in response else [],
                "user": {
                    "name": response["user"]["name"],
                    "user_name": response["user"]["screen_name"],
                    "verified": response["user"]["verified"],
                }
            }
            return data
        except Exception as e:
            raise e
