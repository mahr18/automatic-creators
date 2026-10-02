type YouTubeItem = {
  id: string;
  title: string;
  channel: string;
  published_at: string;
  views: number;
  likes: number;
  url: string;
};

export async function optionalYouTubeSignals(
  env: Env,
  query: string,
  maxResults = 8
): Promise<{ items: YouTubeItem[]; sources: Array<{ title: string; url: string; note: string }> }> {
  if (!env.YOUTUBE_API_KEY) return { items: [], sources: [] };

  const searchUrl = new URL("https://www.googleapis.com/youtube/v3/search");
  searchUrl.searchParams.set("part", "snippet");
  searchUrl.searchParams.set("q", query.slice(0, 180));
  searchUrl.searchParams.set("type", "video");
  searchUrl.searchParams.set("order", "viewCount");
  searchUrl.searchParams.set("maxResults", String(Math.min(Math.max(maxResults, 1), 10)));
  searchUrl.searchParams.set("key", env.YOUTUBE_API_KEY);

  const searchResponse = await fetch(searchUrl);
  const searchPayload = (await searchResponse.json()) as {
    error?: { message?: string };
    items?: Array<{ id?: { videoId?: string }; snippet?: { title?: string; channelTitle?: string; publishedAt?: string } }>;
  };
  if (!searchResponse.ok) throw new Error(searchPayload.error?.message || `YouTube search HTTP ${searchResponse.status}`);

  const ids = (searchPayload.items || [])
    .map(x => x.id?.videoId)
    .filter((x): x is string => Boolean(x));

  if (!ids.length) return { items: [], sources: [] };

  const detailsUrl = new URL("https://www.googleapis.com/youtube/v3/videos");
  detailsUrl.searchParams.set("part", "snippet,statistics");
  detailsUrl.searchParams.set("id", ids.join(","));
  detailsUrl.searchParams.set("key", env.YOUTUBE_API_KEY);

  const detailsResponse = await fetch(detailsUrl);
  const detailsPayload = (await detailsResponse.json()) as {
    error?: { message?: string };
    items?: Array<{ id: string; snippet?: { title?: string; channelTitle?: string; publishedAt?: string }; statistics?: { viewCount?: string; likeCount?: string } }>;
  };
  if (!detailsResponse.ok) throw new Error(detailsPayload.error?.message || `YouTube details HTTP ${detailsResponse.status}`);

  const items = (detailsPayload.items || []).map(x => ({
    id: x.id,
    title: x.snippet?.title || "",
    channel: x.snippet?.channelTitle || "",
    published_at: x.snippet?.publishedAt || "",
    views: Number(x.statistics?.viewCount || 0),
    likes: Number(x.statistics?.likeCount || 0),
    url: `https://www.youtube.com/watch?v=${x.id}`
  }));

  return {
    items,
    sources: items.map(x => ({
      title: x.title,
      url: x.url,
      note: `Public YouTube signal: views=${x.views}, likes=${x.likes}, channel=${x.channel}`
    }))
  };
}
