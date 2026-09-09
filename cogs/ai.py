import discord
from discord.ext import commands
import os
import asyncio
import gc
import time as _time

# Cache the models directory path once at module load
_MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'models')
# Detect CPU count once
_CPU_THREADS = max(1, (os.cpu_count() or 4) - 1)  # Leave 1 core free for the bot


class AI(commands.Cog):
    """Local AI via llama.cpp — zero external API calls."""

    __slots__ = ('bot', '_llm', '_model_path', '_loading', '_lock', '_history', '_auto_channels', '_auto_cooldowns')

    def __init__(self, bot):
        self.bot = bot
        self._llm = None
        self._model_path = None
        self._loading = False
        self._lock = asyncio.Lock()       # Serialize generation requests
        self._history: list[dict] = []    # Conversation memory (last N turns)
        # channel_id -> target_user_id | None
        # None means reply to ALL users in that channel
        self._auto_channels: dict[int, int | None] = {}
        self._auto_cooldowns: dict[int, float] = {}  # channel_id -> last reply timestamp

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    @staticmethod
    def _find_model() -> str | None:
        """Return the first .gguf file found in models/."""
        for f in os.scandir(_MODELS_DIR):
            if f.name.endswith('.gguf') and f.is_file():
                return f.path
        return None

    def _load_sync(self, path: str):
        """Blocking model load — runs in executor thread."""
        from llama_cpp import Llama
        self._llm = Llama(
            model_path=path,
            n_ctx=2048,
            n_batch=512,            # Bigger batch = faster prompt processing
            n_threads=_CPU_THREADS,
            n_threads_batch=_CPU_THREADS,
            n_gpu_layers=0,         # Pure CPU — change to 999 if you have GPU
            use_mmap=True,          # Memory-map the model file (fast load, low RAM)
            use_mlock=False,        # Don't pin to RAM (let OS manage)
            verbose=False,
        )

    def _generate_sync(self, messages: list[dict], max_tokens: int = 300) -> str:
        """Blocking generation — runs in executor thread."""
        resp = self._llm.create_chat_completion(
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.7,
            top_p=0.9,
            top_k=40,
            repeat_penalty=1.1,
            # Stop sequences to prevent rambling
            stop=["<|eot_id|>", "<|end|>", "\n\nUser:", "\n\nHuman:"],
        )
        return resp['choices'][0]['message']['content'].strip()

    def _build_messages(self, prompt: str) -> list[dict]:
        """Build the message list: system + recent history + current prompt."""
        sys_msg = {
            "role": "system",
            "content": (
                "You are a concise, helpful AI assistant in a Discord chat. "
                "Keep replies short and direct — under 1800 characters. "
                "Use markdown formatting sparingly. Don't repeat the question back."
            )
        }
        msgs = [sys_msg] + self._history[-6:]  # Last 3 exchanges (6 messages)
        msgs.append({"role": "user", "content": prompt})
        return msgs

    def _trim_for_discord(self, text: str) -> str:
        """Hard-cap at Discord's 2000 char limit."""
        if len(text) > 1900:
            # Try to cut at a sentence boundary
            cut = text[:1900].rfind('.')
            if cut > 1400:
                return text[:cut + 1]
            return text[:1897] + "..."
        return text

    # ------------------------------------------------------------------
    # Commands
    # ------------------------------------------------------------------

    @commands.group(invoke_without_command=True)
    async def ai(self, ctx, *, prompt: str = None):
        """Chat with local AI. Usage: |ai <prompt>"""
        if prompt is None:
            loaded = self._llm is not None
            name = os.path.basename(self._model_path) if self._model_path else "none"
            ch = ctx.channel.id
            if ch in self._auto_channels:
                target_id = self._auto_channels[ch]
                if target_id is None:
                    auto_str = "[ON] all users"
                else:
                    auto_str = f"[ON] <@{target_id}>"
            else:
                auto_str = "[OFF]"
            await ctx.send(
                f"**AI** {'[LOADED]' if loaded else '[NOT LOADED]'} `{name}` | Auto: {auto_str}\n"
                f"`{ctx.prefix}ai start` / `{ctx.prefix}ai stop` / `{ctx.prefix}ai auto` / `{ctx.prefix}ai clear` / `{ctx.prefix}ai <prompt>`"
            )
            return

        if not self._llm:
            await ctx.send(f"Model not loaded. Run `{ctx.prefix}ai start`")
            return

        async with self._lock:  # One generation at a time
            msg = await ctx.send("Generating...")
            t0 = _time.perf_counter()
            try:
                messages = self._build_messages(prompt)
                loop = asyncio.get_running_loop()
                response = await loop.run_in_executor(None, self._generate_sync, messages)
                elapsed = _time.perf_counter() - t0

                # Update history
                self._history.append({"role": "user", "content": prompt})
                self._history.append({"role": "assistant", "content": response})
                # Cap history at 10 messages
                if len(self._history) > 10:
                    self._history = self._history[-10:]

                response = self._trim_for_discord(response)
                await msg.edit(content=f"{response}\n-# {elapsed:.1f}s")
            except Exception as e:
                await msg.edit(content=f"[ERROR] `{type(e).__name__}: {e}`")

    @ai.command(name='start', aliases=['load', 'on'])
    async def ai_start(self, ctx):
        """Load model into RAM."""
        if self._llm:
            await ctx.send(f"Already loaded. `{ctx.prefix}ai stop` first.")
            return
        if self._loading:
            await ctx.send("Already loading...")
            return

        path = self._find_model()
        if not path:
            await ctx.send("[ERROR] No `.gguf` in `models/` folder.")
            return

        self._loading = True
        name = os.path.basename(path)
        msg = await ctx.send(f"Loading `{name}`...")

        try:
            loop = asyncio.get_running_loop()
            self._model_path = path
            t0 = _time.perf_counter()
            await loop.run_in_executor(None, self._load_sync, path)
            elapsed = _time.perf_counter() - t0
            self._history.clear()
            await msg.edit(content=f"[OK] `{name}` loaded in {elapsed:.1f}s -- {_CPU_THREADS} threads\nUse `{ctx.prefix}ai <prompt>` to chat")
        except Exception as e:
            self._llm = None
            self._model_path = None
            await msg.edit(content=f"[ERROR] Load failed: `{e}`")
        finally:
            self._loading = False

    @ai.command(name='stop', aliases=['unload', 'off'])
    async def ai_stop(self, ctx):
        """Free model from RAM."""
        if not self._llm:
            await ctx.send("Not loaded.")
            return

        name = os.path.basename(self._model_path)
        del self._llm
        self._llm = None
        self._model_path = None
        self._history.clear()
        gc.collect()
        await ctx.send(f"[OK] `{name}` unloaded -- RAM freed.")

    @ai.command(name='clear', aliases=['reset'])
    async def ai_clear(self, ctx):
        """Clear conversation history."""
        self._history.clear()
        await ctx.send("History cleared.")

    @ai.command(name='auto', aliases=['a'])
    async def ai_auto(self, ctx, user: discord.User = None):
        """Toggle auto-reply. No mention = reply to ALL. Mention = reply to that user only."""
        ch = ctx.channel.id
        # Toggle off if already active in this channel
        if ch in self._auto_channels:
            old = self._auto_channels.pop(ch)
            if old is None:
                await ctx.send("Auto-reply **OFF** (was: all users)")
            else:
                await ctx.send(f"Auto-reply **OFF** (was: <@{old}>)")
            return

        if not self._llm:
            await ctx.send(f"Load a model first with `{ctx.prefix}ai start`")
            return

        if user is None:
            # No user mentioned -> reply to ALL
            self._auto_channels[ch] = None
            await ctx.send("Auto-reply **ON** -- replying to **all users** in this channel.")
        else:
            if user.id == self.bot.user.id:
                await ctx.send("[ERROR] Can't target yourself.")
                return
            self._auto_channels[ch] = user.id
            await ctx.send(f"Auto-reply **ON** -- replying to **{user.display_name}** in this channel.")

    # ------------------------------------------------------------------
    # Auto-reply listener
    # ------------------------------------------------------------------

    @commands.Cog.listener()
    async def on_message(self, message):
        # Never reply to self
        if message.author.id == self.bot.user.id:
            return
        # Check if this channel has auto-reply
        ch = message.channel.id
        if ch not in self._auto_channels:
            return
        target_id = self._auto_channels[ch]
        # If target is a specific user, check it matches
        if target_id is not None and message.author.id != target_id:
            return
        # Model must be loaded
        if not self._llm:
            return
        # Ignore bot commands (messages starting with prefix)
        import json
        try:
            with open('config.json', 'r') as f:
                pfx = json.load(f).get('prefix', '.')
            if message.content.startswith(pfx):
                return
        except Exception:
            pass
        # Ignore empty messages
        if not message.content or not message.content.strip():
            return

        # Rate-limit: 5 second cooldown per channel to avoid ban
        now = _time.time()
        last = self._auto_cooldowns.get(ch, 0)
        if now - last < 5:
            return
        self._auto_cooldowns[ch] = now

        async with self._lock:
            try:
                prompt = f"{message.author.display_name}: {message.content}"
                messages = self._build_messages(prompt)
                loop = asyncio.get_running_loop()
                t0 = _time.perf_counter()
                response = await loop.run_in_executor(None, self._generate_sync, messages)
                elapsed = _time.perf_counter() - t0

                self._history.append({"role": "user", "content": prompt})
                self._history.append({"role": "assistant", "content": response})
                if len(self._history) > 10:
                    self._history = self._history[-10:]

                response = self._trim_for_discord(response)
                await message.reply(f"{response}\n-# {elapsed:.1f}s", mention_author=False)
            except Exception:
                pass  # Silently fail to avoid spam


async def setup(bot):
    await bot.add_cog(AI(bot))
