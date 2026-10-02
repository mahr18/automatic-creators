type WatchItem = {
  channel_id: string;
  title: string;
  video_id: string;
  published_at: string;
  url: string;
};

export async function readWatchlist(env: Env): Promise<WatchItem[]> {
  const rows = await env.DB.prepare(
    "SELECT channel_id FROM watchlists WHERE enabled = 1 ORDER BY id DESC LIMIT 10"
  ).all<{ channel_id: string }>();

  const all: WatchItem[] = [];
  for (const row of rows.results || []) {
    const url = `https://www.youtube.com/feeds/videos.xml?channel_id=${encodeURIComponent(row.channel_id)}`;
    try {
      const response = await fetch(url, { headers: { "user-agent": "MAHER-CONTENT-BRAIN/0.3" } });
      if (!response.ok) continue;
      const xml = await response.text();
      const entries = [...xml.matchAll(/<entry>([\s\S]*?)<\/entry>/g)].slice(0, 5);
      for (const match of entries) {
        const block = match[1];
        const id = block.match(/<yt:videoId>([^<]+)<\/yt:videoId>/)?.[1] || "";
        const title = block.match(/<title>([\s\S]*?)<\/title>/)?.[1]?.replace(/<!\[CDATA\[|\]\]>/g, "").trim() || "";
        const published = block.match(/<published>([^<]+)<\/published>/)?.[1] || "";
        if (!id || !title) continue;
        all.push({
          channel_id: row.channel_id,
          title: title.replace(/&amp;/g, "&").replace(/&quot;/g, '"'),
          video_id: id,
          published_at: published,
          url: `https://www.youtube.com/watch?v=${id}`
        });
      }
    } catch {
      // One broken watch feed must never block the brain.
    }
  }

  return all.sort((a, b) => b.published_at.localeCompare(a.published_at));
}
