import discord
from discord.ext import commands
import asyncio
import json

# Using the free OMDb API (or TMDb) for movie/show search
# OMDb requires a free API key from https://www.omdbapi.com/apikey.aspx
# For zero-config, we use the free open API at https://www.omdbapi.com with a demo key
# OR we can scrape basic info. Let's use a lightweight approach with aiohttp.

try:
    import aiohttp
    HAS_AIOHTTP = True
except ImportError:
    HAS_AIOHTTP = False


class Media(commands.Cog):
    """Movie and TV show search."""

    def __init__(self, bot):
        self.bot = bot
        self._session = None

    async def _get_session(self):
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    def cog_unload(self):
        if self._session and not self._session.closed:
            asyncio.create_task(self._session.close())

    # ------------------------------------------------------------------
    # OMDb API helpers (free tier: 1000 requests/day)
    # Key "trilogy" is a known public demo key; users should get their own
    # ------------------------------------------------------------------

    async def _omdb_search(self, query: str, media_type: str = None) -> dict | None:
        """Search OMDb for a title."""
        if not HAS_AIOHTTP:
            return None
        session = await self._get_session()
        params = {'apikey': 'trilogy', 't': query}
        if media_type:
            params['type'] = media_type  # 'movie' or 'series'
        try:
            async with session.get('https://www.omdbapi.com/', params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get('Response') == 'True':
                        return data
        except Exception:
            pass
        return None

    async def _omdb_search_list(self, query: str, media_type: str = None) -> list:
        """Search OMDb for multiple results."""
        if not HAS_AIOHTTP:
            return []
        session = await self._get_session()
        params = {'apikey': 'trilogy', 's': query}
        if media_type:
            params['type'] = media_type
        try:
            async with session.get('https://www.omdbapi.com/', params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get('Response') == 'True':
                        return data.get('Search', [])[:5]
        except Exception:
            pass
        return []

    async def _omdb_by_id(self, imdb_id: str) -> dict | None:
        """Get detailed info by IMDb ID."""
        if not HAS_AIOHTTP:
            return None
        session = await self._get_session()
        params = {'apikey': 'trilogy', 'i': imdb_id, 'plot': 'short'}
        try:
            async with session.get('https://www.omdbapi.com/', params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get('Response') == 'True':
                        return data
        except Exception:
            pass
        return None

    def _format_result(self, data: dict) -> str:
        """Format a movie/show result into a clean text block."""
        title = data.get('Title', 'Unknown')
        year = data.get('Year', '?')
        rated = data.get('Rated', 'N/A')
        runtime = data.get('Runtime', 'N/A')
        genre = data.get('Genre', 'N/A')
        imdb = data.get('imdbRating', 'N/A')
        plot = data.get('Plot', 'No plot available.')
        director = data.get('Director', 'N/A')
        actors = data.get('Actors', 'N/A')
        media_type = data.get('Type', 'N/A').title()
        imdb_id = data.get('imdbID', '')
        seasons = data.get('totalSeasons', '')

        text = (
            f"**{title}** ({year}) -- {media_type}\n"
            f"```\n"
            f"Rating:   {rated} | IMDb: {imdb}/10\n"
            f"Runtime:  {runtime}\n"
            f"Genre:    {genre}\n"
            f"Director: {director}\n"
            f"Cast:     {actors}\n"
        )
        if seasons:
            text += f"Seasons:  {seasons}\n"
        text += f"```\n"
        text += f"**Plot:** {plot}\n"
        if imdb_id:
            text += f"**IMDb:** https://www.imdb.com/title/{imdb_id}/"

        return text

    # ------------------------------------------------------------------
    # Commands
    # ------------------------------------------------------------------

    @commands.command(aliases=['mov'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def movie(self, ctx, *, query: str):
        """Search for a movie. Example: |movie Inception"""
        if not HAS_AIOHTTP:
            await ctx.send("Install `aiohttp` to use this command: `pip install aiohttp`", delete_after=10)
            return

        msg = await ctx.send(f"Searching for movie: `{query}`...")
        data = await self._omdb_search(query, 'movie')

        if not data:
            # Try general search
            results = await self._omdb_search_list(query, 'movie')
            if results:
                # Get details for the first result
                data = await self._omdb_by_id(results[0]['imdbID'])

        if data:
            text = self._format_result(data)
            await msg.edit(content=text)
        else:
            await msg.edit(content=f"No movie found for: `{query}`")
            await asyncio.sleep(5)
            try:
                await msg.delete()
            except Exception:
                pass

    @commands.command(aliases=['tv', 'series'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def show(self, ctx, *, query: str):
        """Search for a TV show. Example: |show Breaking Bad"""
        if not HAS_AIOHTTP:
            await ctx.send("Install `aiohttp` to use this command: `pip install aiohttp`", delete_after=10)
            return

        msg = await ctx.send(f"Searching for show: `{query}`...")
        data = await self._omdb_search(query, 'series')

        if not data:
            results = await self._omdb_search_list(query, 'series')
            if results:
                data = await self._omdb_by_id(results[0]['imdbID'])

        if data:
            text = self._format_result(data)
            await msg.edit(content=text)
        else:
            await msg.edit(content=f"No show found for: `{query}`")
            await asyncio.sleep(5)
            try:
                await msg.delete()
            except Exception:
                pass

    @commands.command(aliases=['imdb'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def msearch(self, ctx, *, query: str):
        """Search movies and shows (lists top 5 results)."""
        if not HAS_AIOHTTP:
            await ctx.send("Install `aiohttp` to use this command: `pip install aiohttp`", delete_after=10)
            return

        msg = await ctx.send(f"Searching: `{query}`...")
        results = await self._omdb_search_list(query)

        if not results:
            await msg.edit(content=f"No results for: `{query}`")
            await asyncio.sleep(5)
            try:
                await msg.delete()
            except Exception:
                pass
            return

        text = f"**Search results for:** `{query}`\n\n"
        for i, r in enumerate(results, 1):
            title = r.get('Title', '?')
            year = r.get('Year', '?')
            mtype = r.get('Type', '?').title()
            imdb_id = r.get('imdbID', '')
            text += f"`{i}.` **{title}** ({year}) -- {mtype}"
            if imdb_id:
                text += f" | [IMDb](https://www.imdb.com/title/{imdb_id}/)"
            text += "\n"

        text += f"\n-# Use `{ctx.prefix}movie <title>` or `{ctx.prefix}show <title>` for full details"
        await msg.edit(content=text)


async def setup(bot):
    await bot.add_cog(Media(bot))
