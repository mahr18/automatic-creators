from __future__ import annotations

import httpx

from ..config import settings


YOUTUBE_SEARCH = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEOS = "https://www.googleapis.com/youtube/v3/videos"


async def search_youtube(
    query: str,
    max_results: int = 10,
    order: str = "viewCount",
    region_code: str | None = None,
) -> list[dict]:
    """Return structured public YouTube signals when an API key is configured."""
    if not settings.youtube_api_key:
        return []

    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": max(1, min(max_results, 50)),
        "order": order,
        "key": settings.youtube_api_key,
    }
    if region_code:
        params["regionCode"] = region_code

    async with httpx.AsyncClient(timeout=20) as client:
        search = (await client.get(YOUTUBE_SEARCH, params=params)).raise_for_status()
        items = search.json().get("items", [])
        ids = [x.get("id", {}).get("videoId") for x in items if x.get("id", {}).get("videoId")]
        if not ids:
            return []

        detail_params = {
            "part": "snippet,statistics,contentDetails",
            "id": ",".join(ids),
            "key": settings.youtube_api_key,
        }
        details = (await client.get(YOUTUBE_VIDEOS, params=detail_params)).raise_for_status()
        by_id = {x["id"]: x for x in details.json().get("items", [])}

    results=[]
    for item in items:
        vid=item.get("id",{}).get("videoId")
        detail=by_id.get(vid,{})
        snippet=detail.get("snippet", item.get("snippet",{}))
        stats=detail.get("statistics",{})
        results.append({
            "video_id": vid,
            "title": snippet.get("title"),
            "channel": snippet.get("channelTitle"),
            "published_at": snippet.get("publishedAt"),
            "views": int(stats.get("viewCount",0) or 0),
            "likes": int(stats.get("likeCount",0) or 0),
            "duration": detail.get("contentDetails",{}).get("duration"),
            "url": f"https://www.youtube.com/watch?v={vid}",
        })
    return results
