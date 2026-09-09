import discord
from discord.ext import commands
import asyncio
import random
import string
import re


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ------------------------------------------------------------------
    # .hack @user — fake hacking animation
    # ------------------------------------------------------------------
    @commands.command()
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def hack(self, ctx, user: discord.User = None):
        """Fake hack a user."""
        if not user:
            await ctx.send(f"Mention someone: `{ctx.prefix}hack @user`")
            return

        msg = await ctx.send(f"**Hacking {user.name}...**")
        steps = [
            f"```\n[>---------] 5%  -- Searching for {user.name}'s data...```",
            f"```\n[>>>-------] 20% -- Accessing Discord token...```",
            f"```\n[>>>>------] 35% -- Bypassing 2FA...```",
            f"```\n[>>>>>>----] 50% -- Stealing DMs...```",
            f"```\n[>>>>>>>---] 65% -- Downloading browser history...```",
            f"```\n[>>>>>>>>--] 80% -- Injecting payload...```",
            f"```\n[>>>>>>>>>-] 90% -- Uploading data to server...```",
            f"```\n[>>>>>>>>>>] 100% -- Complete!\n\nEmail: {user.name.lower()}@gmail.com\nPassword: ********\nIP: {random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}\nLocation: Your Mom's House```",
            f"**Successfully hacked {user.mention}!**\n\n||jk lol||"
        ]
        for step in steps:
            await asyncio.sleep(1.5)
            await msg.edit(content=step)

    # ------------------------------------------------------------------
    # .token @user — fake token grab
    # ------------------------------------------------------------------
    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def token(self, ctx, user: discord.User = None):
        """Generate a fake token for a user."""
        user = user or ctx.author
        fake = ''.join(random.choices(string.ascii_letters + string.digits + '_-', k=24))
        fake += '.' + ''.join(random.choices(string.ascii_letters + string.digits, k=6))
        fake += '.' + ''.join(random.choices(string.ascii_letters + string.digits + '_-', k=27))
        await ctx.send(f"**{user.name}**'s token:\n`{fake}`\n||this is fake lol||")

    # ------------------------------------------------------------------
    # .ip @user — fake IP lookup
    # ------------------------------------------------------------------
    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def ip(self, ctx, user: discord.User = None):
        """Fake IP grab."""
        user = user or ctx.author
        ip = f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}"
        isp_list = ["Comcast", "AT&T", "Verizon", "Spectrum", "Jio", "Airtel", "BT Group", "Vodafone", "T-Mobile"]
        city_list = ["Los Angeles", "Mumbai", "London", "Berlin", "Tokyo", "Sao Paulo", "Cairo", "Sydney", "Toronto"]
        await ctx.send(
            f"**IP Lookup for {user.name}:**\n"
            f"```\n"
            f"IP:       {ip}\n"
            f"ISP:      {random.choice(isp_list)}\n"
            f"City:     {random.choice(city_list)}\n"
            f"OS:       Windows 11\n"
            f"Browser:  Chrome 153\n"
            f"```\n||not real btw||"
        )

    # ------------------------------------------------------------------
    # .nitro — fake nitro link
    # ------------------------------------------------------------------
    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def nitro(self, ctx):
        """Send a fake nitro gift."""
        code = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        await ctx.send(
            f"**A wild gift appears!**\n"
            f"discord.gift/{code}\n"
            f"||gotcha||"
        )

    # ------------------------------------------------------------------
    # .8ball <question> — magic 8 ball
    # ------------------------------------------------------------------
    @commands.command(name='8ball', aliases=['ask', 'ball'])
    async def eightball(self, ctx, *, question: str):
        """Ask the magic 8 ball."""
        answers = [
            "[YES] Absolutely.", "[YES] Without a doubt.", "[YES] Most likely.",
            "[YES] Signs point to yes.", "[YES] Obviously.", "[YES] 100%.",
            "[MAYBE] Maybe...", "[MAYBE] Ask again later.", "[MAYBE] Can't tell right now.",
            "[MAYBE] Concentrate and ask again.", "[MAYBE] It's possible.",
            "[NO] No way.", "[NO] Don't count on it.", "[NO] Very doubtful.",
            "[NO] Absolutely not.", "[NO] Not in a million years."
        ]
        await ctx.send(f"**{random.choice(answers)}**")

    # ------------------------------------------------------------------
    # .roll <NdN> — dice roller
    # ------------------------------------------------------------------
    @commands.command(aliases=['dice'])
    async def roll(self, ctx, dice: str = "1d6"):
        """Roll dice. Example: |roll 2d20"""
        try:
            count, sides = map(int, dice.lower().split('d'))
            if count > 100 or sides > 1000:
                await ctx.send("Too many dice/sides.")
                return
            rolls = [random.randint(1, sides) for _ in range(count)]
            await ctx.send(f"**{dice}:** {', '.join(map(str, rolls))} = **{sum(rolls)}**")
        except Exception:
            await ctx.send(f"Format: `{ctx.prefix}roll 2d20`")

    # ------------------------------------------------------------------
    # .coinflip
    # ------------------------------------------------------------------
    @commands.command(aliases=['flip', 'coin'])
    async def coinflip(self, ctx):
        """Flip a coin."""
        result = random.choice(["**Heads!**", "**Tails!**"])
        msg = await ctx.send("Flipping...")
        await asyncio.sleep(1)
        await msg.edit(content=result)

    # ------------------------------------------------------------------
    # .rate <thing> — rate anything
    # ------------------------------------------------------------------
    @commands.command()
    async def rate(self, ctx, *, thing: str):
        """Rate something out of 10."""
        score = random.randint(0, 10)
        bar = "#" * score + "-" * (10 - score)
        await ctx.send(f"I rate **{thing}** a **{score}/10**\n`[{bar}]`")

    # ------------------------------------------------------------------
    # .pp @user — pp size
    # ------------------------------------------------------------------
    @commands.command()
    async def pp(self, ctx, user: discord.User = None):
        """Check pp size."""
        user = user or ctx.author
        size = random.randint(1, 12)
        dong = "8" + "=" * size + "D"
        await ctx.send(f"**{user.name}**'s pp:\n{dong}")

    # ------------------------------------------------------------------
    # .ship @user1 @user2 — love calculator
    # ------------------------------------------------------------------
    @commands.command(aliases=['love'])
    async def ship(self, ctx, user1: discord.User, user2: discord.User = None):
        """Ship two users together."""
        user2 = user2 or ctx.author
        score = random.randint(0, 100)
        if score < 20:
            comment = "Not happening..."
        elif score < 50:
            comment = "There's a chance..."
        elif score < 80:
            comment = "Looking good!"
        else:
            comment = "Perfect match!"
        bar = "#" * (score // 10) + "-" * (10 - score // 10)
        await ctx.send(
            f"**Love Calculator**\n"
            f"{user1.name} x {user2.name}\n"
            f"`[{bar}]` **{score}%**\n"
            f"*{comment}*"
        )

    # ------------------------------------------------------------------
    # .mock <text> — sPoNgEbOb mOcK
    # ------------------------------------------------------------------
    @commands.command()
    async def mock(self, ctx, *, text: str):
        """SpOnGeBoB mOcK tExT."""
        mocked = ''.join(c.upper() if i % 2 else c.lower() for i, c in enumerate(text))
        await ctx.send(mocked)

    # ------------------------------------------------------------------
    # .reverse <text>
    # ------------------------------------------------------------------
    @commands.command(aliases=['rev'])
    async def reverse(self, ctx, *, text: str):
        """Reverse text."""
        await ctx.send(text[::-1])

    # ------------------------------------------------------------------
    # .emojify <text> — turn text into emoji letters
    # ------------------------------------------------------------------
    @commands.command(aliases=['emoji'])
    async def emojify(self, ctx, *, text: str):
        """Convert text to regional indicator letters."""
        result = []
        for c in text.lower():
            if c.isalpha():
                result.append(f":regional_indicator_{c}:")
            elif c == ' ':
                result.append("   ")
            elif c.isdigit():
                num_words = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
                result.append(f":{num_words[int(c)]}:")
            else:
                result.append(c)
        output = ''.join(result)
        if len(output) > 1900:
            output = output[:1900]
        await ctx.send(output)

    # ------------------------------------------------------------------
    # .clap <text> — add clap between words
    # ------------------------------------------------------------------
    @commands.command()
    async def clap(self, ctx, *, text: str):
        """Add clap between words."""
        await ctx.send(text.replace(' ', ' :clap: '))

    # ------------------------------------------------------------------
    # .say / .dm — send message somewhere
    # ------------------------------------------------------------------
    @commands.command()
    async def say(self, ctx, *, text: str):
        """Make the bot say something (deletes your command)."""
        try:
            await ctx.message.delete()
        except Exception:
            pass
        await ctx.send(text)

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def dm(self, ctx, user: discord.User, *, text: str):
        """DM a user."""
        try:
            await user.send(text)
            await ctx.send(f"DM sent to **{user.name}**", delete_after=3)
        except Exception:
            await ctx.send(f"Couldn't DM **{user.name}**")

    # ------------------------------------------------------------------
    # .spam <count> <text> — repeat a message
    # ------------------------------------------------------------------
    @commands.command()
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def spam(self, ctx, count: int, *, text: str):
        """Spam a message (max 5)."""
        count = min(count, 5)
        try:
            await ctx.message.delete()
        except Exception:
            pass
        for _ in range(count):
            await ctx.send(text)
            await asyncio.sleep(1.2)

    # ------------------------------------------------------------------
    # .rps <choice> — rock paper scissors
    # ------------------------------------------------------------------
    @commands.command()
    async def rps(self, ctx, choice: str):
        """Rock Paper Scissors."""
        choice = choice.lower()
        if choice not in ('rock', 'paper', 'scissors'):
            await ctx.send("Pick `rock`, `paper`, or `scissors`")
            return
        bot_choice = random.choice(['rock', 'paper', 'scissors'])
        labels = {'rock': 'Rock', 'paper': 'Paper', 'scissors': 'Scissors'}

        if choice == bot_choice:
            result = "**Tie!**"
        elif (choice == 'rock' and bot_choice == 'scissors') or \
             (choice == 'paper' and bot_choice == 'rock') or \
             (choice == 'scissors' and bot_choice == 'paper'):
            result = "**You win!**"
        else:
            result = "**You lose!**"

        await ctx.send(f"{labels[choice]} vs {labels[bot_choice]} -- {result}")

    # ------------------------------------------------------------------
    # .qotd — question of the day
    # ------------------------------------------------------------------

    _QOTD_QUESTIONS = [
        # Deep / Thought-provoking
        "What's one thing you'd change about yourself if you could?",
        "What's the best advice you've ever been given?",
        "If you could relive one day of your life, which would it be?",
        "What's something you believe that most people don't?",
        "What would you do if you knew you couldn't fail?",
        "What's the most important lesson you've learned this year?",
        "If you could have dinner with anyone (dead or alive), who?",
        "What's a hill you're willing to die on?",
        "What's the scariest thing you've ever done willingly?",
        "What would your last meal be?",
        "What's a secret talent nobody knows about?",
        "If your life was a movie, what genre would it be?",
        "What's the most overrated thing in society?",
        "What do you think happens after death?",
        "What's a memory that always makes you smile?",
        # Fun / Lighthearted
        "What's the weirdest dream you've ever had?",
        "If you could be any animal for a day, which one?",
        "What's your most unpopular food opinion?",
        "What song do you have on repeat right now?",
        "What's the dumbest thing you've ever done?",
        "If you had to eat one food forever, what would it be?",
        "What's your comfort show/movie?",
        "What's the most useless skill you have?",
        "What fictional world would you live in?",
        "If you could have any superpower, what would you pick?",
        "What's your toxic trait?",
        "What's the worst haircut you've ever had?",
        "What's something you're irrationally afraid of?",
        "What's your go-to karaoke song?",
        "What's the most embarrassing thing in your search history?",
        # Hypothetical / Would you rather
        "Would you rather be invisible or be able to fly?",
        "Would you rather know how you die or when you die?",
        "Would you rather have unlimited money or unlimited knowledge?",
        "If you won the lottery tomorrow, what's the first thing you'd buy?",
        "Would you rather live 100 years in the past or 100 years in the future?",
        "If you could master any skill overnight, what would it be?",
        "Would you rather never use social media again or never watch a movie again?",
        "If you could teleport anywhere right now, where would you go?",
        "Would you rather be famous or be the best friend of someone famous?",
        "If you could only keep 3 apps on your phone, which ones?",
        # Gaming / Internet
        "What's the best video game you've ever played?",
        "What game has the best soundtrack?",
        "What's a game you've rage-quit the hardest?",
        "PC, console, or mobile -- pick one forever?",
        "What's the best anime you've watched?",
        "What's your most controversial gaming take?",
        "What's a game you think is overrated?",
        "If you could live inside any game, which one?",
        "What's the longest gaming session you've ever had?",
        "What game do you wish you could play for the first time again?",
        # Debate starters
        "Is a hotdog a sandwich?",
        "Is water wet?",
        "Does pineapple belong on pizza?",
        "Is cereal a soup?",
        "Cats or dogs?",
        "Is it GIF or JIF?",
        "Morning person or night owl?",
        "Summer or winter?",
        "Batman or Superman?",
        "Is it better to be feared or loved?",
        # Social
        "What's your biggest green flag in a person?",
        "What's an instant red flag for you?",
        "What's your love language?",
        "What trait do you value most in a friend?",
        "What's the nicest thing a stranger has done for you?",
        "What's a compliment you'll never forget?",
        "What's the best gift you've ever received?",
        "What's something that instantly makes your day better?",
        "What makes you feel the most alive?",
        "What are you most grateful for right now?",
        # Spicy
        "What's your most controversial opinion?",
        "What's a trend you absolutely can't stand?",
        "What's the worst take you've seen on the internet?",
        "What's something that's legal but feels illegal?",
        "What's something everyone loves but you hate?",
        "What's a rule you always break?",
        "What's the pettiest reason you've stopped talking to someone?",
        "What's the most unhinged thing you've done at 3 AM?",
    ]

    @commands.command(aliases=['question'])
    async def qotd(self, ctx):
        """Send a random Question of the Day."""
        question = random.choice(self._QOTD_QUESTIONS)
        await ctx.send(f"**Question of the Day**\n\n{question}")

    # ==================================================================
    # NEW FUN COMMANDS
    # ==================================================================

    # ------------------------------------------------------------------
    # .roast @user
    # ------------------------------------------------------------------
    _ROASTS = [
        "You bring everyone so much joy... when you leave.",
        "I'd agree with you but then we'd both be wrong.",
        "You're proof that even evolution makes mistakes.",
        "You're not stupid, you just have bad luck thinking.",
        "If laughter is the best medicine, your face must be curing the world.",
        "You're like a cloud. When you disappear, it's a beautiful day.",
        "I'd explain it to you, but I left my crayons at home.",
        "You're the reason they put instructions on shampoo.",
        "Somewhere out there is a tree, tirelessly producing oxygen for you. You owe it an apology.",
        "If you were any more inbred you'd be a sandwich.",
        "Your secrets are safe with me. I never even listen when you talk.",
        "You're like a software update. Every time I see you, I think 'not now.'",
        "I thought of you today. It reminded me to take out the trash.",
        "You're not useless. You can always serve as a bad example.",
        "Light travels faster than sound, which is why you seemed bright until you spoke.",
    ]

    @commands.command()
    async def roast(self, ctx, user: discord.User = None):
        """Roast someone."""
        user = user or ctx.author
        await ctx.send(f"**{user.name}**, {random.choice(self._ROASTS)}")

    # ------------------------------------------------------------------
    # .compliment @user
    # ------------------------------------------------------------------
    _COMPLIMENTS = [
        "you light up every room you walk into.",
        "your smile is contagious.",
        "you have an amazing sense of humor.",
        "you make the world a better place.",
        "you're more fun than bubble wrap.",
        "you're someone's reason to smile.",
        "you have impeccable taste.",
        "you could survive a zombie apocalypse.",
        "you're like a ray of sunshine on a rainy day.",
        "if you were a vegetable, you'd be a cute-cumber.",
        "you're proof that good things come in small packages.",
        "you're the human equivalent of a warm cup of coffee.",
        "you have the best laugh.",
        "the world is better because you're in it.",
        "you have great energy.",
    ]

    @commands.command()
    async def compliment(self, ctx, user: discord.User = None):
        """Compliment someone."""
        user = user or ctx.author
        await ctx.send(f"**{user.name}**, {random.choice(self._COMPLIMENTS)}")

    # ------------------------------------------------------------------
    # .howgay @user
    # ------------------------------------------------------------------
    @commands.command()
    async def howgay(self, ctx, user: discord.User = None):
        """How gay is someone?"""
        user = user or ctx.author
        pct = random.randint(0, 100)
        bar = "#" * (pct // 10) + "-" * (10 - pct // 10)
        await ctx.send(f"**{user.name}** is **{pct}%** gay\n`[{bar}]`")

    # ------------------------------------------------------------------
    # .iq @user
    # ------------------------------------------------------------------
    @commands.command()
    async def iq(self, ctx, user: discord.User = None):
        """Check someone's IQ."""
        user = user or ctx.author
        score = random.randint(1, 200)
        if score < 70:
            comment = "...yikes."
        elif score < 100:
            comment = "room temperature IQ."
        elif score < 130:
            comment = "above average, nice."
        elif score < 160:
            comment = "certified genius."
        else:
            comment = "literally Einstein."
        await ctx.send(f"**{user.name}**'s IQ: **{score}** -- {comment}")

    # ------------------------------------------------------------------
    # .slot — slot machine
    # ------------------------------------------------------------------
    @commands.command(aliases=['slots'])
    async def slot(self, ctx):
        """Play the slot machine."""
        symbols = ['7', 'X', 'O', '#', '$', '%', '&', '*']
        s1, s2, s3 = random.choice(symbols), random.choice(symbols), random.choice(symbols)

        msg = await ctx.send("**[ ? | ? | ? ]** -- Spinning...")
        await asyncio.sleep(1.5)

        if s1 == s2 == s3:
            result = "JACKPOT! All three match!"
        elif s1 == s2 or s2 == s3 or s1 == s3:
            result = "Two match -- close one!"
        else:
            result = "No match. Better luck next time."

        await msg.edit(content=f"**[ {s1} | {s2} | {s3} ]** -- {result}")

    # ------------------------------------------------------------------
    # .choose opt1 | opt2 | opt3
    # ------------------------------------------------------------------
    @commands.command(aliases=['pick'])
    async def choose(self, ctx, *, options: str):
        """Pick a random option. Separate with |"""
        choices = [o.strip() for o in options.split('|') if o.strip()]
        if len(choices) < 2:
            await ctx.send(f"Give at least 2 options separated by `|`")
            return
        await ctx.send(f"I choose: **{random.choice(choices)}**")

    # ------------------------------------------------------------------
    # .truth / .dare
    # ------------------------------------------------------------------
    _TRUTHS = [
        "What's the most embarrassing thing you've done in public?",
        "What's a secret you've never told anyone?",
        "Have you ever cheated on a test?",
        "What's the biggest lie you've ever told?",
        "Who in this server do you secretly find annoying?",
        "What's your most cringe memory?",
        "Have you ever stalked someone's social media?",
        "What's the weirdest thing you've searched online?",
        "What's a guilty pleasure you're ashamed of?",
        "Have you ever pretended to like someone you didn't?",
        "What's the most childish thing you still do?",
        "What's the worst date you've ever been on?",
        "Have you ever lied to get out of plans?",
        "What's the most embarrassing song on your playlist?",
        "What's something you pretend to understand but don't?",
    ]

    _DARES = [
        "Change your Discord status to something embarrassing for 10 minutes.",
        "Send a random message in a random server with no context.",
        "Use only caps lock for the next 5 minutes.",
        "Change your nickname to 'I lost a dare' for 10 minutes.",
        "Send the last photo in your camera roll (no cheating!).",
        "Type with your elbows for the next message.",
        "Let someone else send a message from your account.",
        "Post your screen time from today.",
        "Send a voice message of you singing.",
        "DM someone 'I know what you did' with no explanation.",
        "Use only one word responses for 5 minutes.",
        "Put your bio as 'I eat cereal with water' for 10 minutes.",
        "React to every message in this channel for 2 minutes.",
        "Send an embarrassing selfie.",
        "Let the group choose your profile picture for 1 hour.",
    ]

    @commands.command()
    async def truth(self, ctx):
        """Get a random truth question."""
        await ctx.send(f"**Truth:** {random.choice(self._TRUTHS)}")

    @commands.command()
    async def dare(self, ctx):
        """Get a random dare challenge."""
        await ctx.send(f"**Dare:** {random.choice(self._DARES)}")

    # ------------------------------------------------------------------
    # .fact — random fun fact
    # ------------------------------------------------------------------
    _FACTS = [
        "Honey never spoils. Archaeologists have found 3000-year-old honey in Egyptian tombs that was still edible.",
        "Octopuses have three hearts and blue blood.",
        "A group of flamingos is called a 'flamboyance'.",
        "Bananas are berries, but strawberries aren't.",
        "The shortest war in history was between Britain and Zanzibar in 1896. It lasted 38 minutes.",
        "A jiffy is an actual unit of time: 1/100th of a second.",
        "Cows have best friends and get stressed when separated.",
        "The inventor of the Pringles can is buried in one.",
        "There are more possible iterations of a game of chess than there are atoms in the known universe.",
        "Venus is the only planet that spins clockwise.",
        "A bolt of lightning is five times hotter than the surface of the sun.",
        "The total weight of all ants on Earth is roughly equal to the total weight of all humans.",
        "Scotland's national animal is the unicorn.",
        "You can't hum while holding your nose.",
        "A day on Venus is longer than a year on Venus.",
    ]

    @commands.command()
    async def fact(self, ctx):
        """Get a random fun fact."""
        await ctx.send(f"**Fun Fact:** {random.choice(self._FACTS)}")

    # ------------------------------------------------------------------
    # .joke — random joke
    # ------------------------------------------------------------------
    _JOKES = [
        ("Why don't scientists trust atoms?", "Because they make up everything!"),
        ("Why did the scarecrow win an award?", "He was outstanding in his field."),
        ("I told my wife she was drawing her eyebrows too high.", "She looked surprised."),
        ("What do you call a fake noodle?", "An impasta."),
        ("Why don't eggs tell jokes?", "They'd crack each other up."),
        ("I'm reading a book about anti-gravity.", "It's impossible to put down."),
        ("What did the ocean say to the beach?", "Nothing, it just waved."),
        ("Why do programmers prefer dark mode?", "Because light attracts bugs."),
        ("What's the best thing about Switzerland?", "I don't know, but the flag is a big plus."),
        ("I used to hate facial hair.", "But then it grew on me."),
        ("Why did the developer go broke?", "Because he used up all his cache."),
        ("Parallel lines have so much in common.", "It's a shame they'll never meet."),
        ("Why was the math book sad?", "Because it had too many problems."),
        ("What do you call a bear with no teeth?", "A gummy bear."),
        ("I told a chemistry joke.", "There was no reaction."),
    ]

    @commands.command()
    async def joke(self, ctx):
        """Tell a random joke."""
        setup, punchline = random.choice(self._JOKES)
        msg = await ctx.send(f"**{setup}**")
        await asyncio.sleep(2)
        await msg.edit(content=f"**{setup}**\n\n||{punchline}||")

    # ------------------------------------------------------------------
    # .quote — random inspirational quote
    # ------------------------------------------------------------------
    _QUOTES = [
        ("The only way to do great work is to love what you do.", "Steve Jobs"),
        ("In the middle of difficulty lies opportunity.", "Albert Einstein"),
        ("It does not matter how slowly you go as long as you do not stop.", "Confucius"),
        ("The best time to plant a tree was 20 years ago. The second best time is now.", "Chinese Proverb"),
        ("Be yourself; everyone else is already taken.", "Oscar Wilde"),
        ("The only limit to our realization of tomorrow is our doubts of today.", "Franklin D. Roosevelt"),
        ("Do what you can, with what you have, where you are.", "Theodore Roosevelt"),
        ("Everything you've ever wanted is on the other side of fear.", "George Addair"),
        ("Success is not final, failure is not fatal: it is the courage to continue that counts.", "Winston Churchill"),
        ("Believe you can and you're halfway there.", "Theodore Roosevelt"),
        ("Your time is limited, don't waste it living someone else's life.", "Steve Jobs"),
        ("The future belongs to those who believe in the beauty of their dreams.", "Eleanor Roosevelt"),
        ("It is during our darkest moments that we must focus to see the light.", "Aristotle"),
        ("Strive not to be a success, but rather to be of value.", "Albert Einstein"),
        ("The mind is everything. What you think you become.", "Buddha"),
    ]

    @commands.command()
    async def quote(self, ctx):
        """Get a random inspirational quote."""
        text, author = random.choice(self._QUOTES)
        await ctx.send(f"*\"{text}\"*\n-- {author}")

    # ------------------------------------------------------------------
    # .ascii <text> — simple ASCII art
    # ------------------------------------------------------------------
    @commands.command()
    async def ascii(self, ctx, *, text: str):
        """Convert text to ASCII block letters."""
        # Simple block letter font using 3-line height
        font = {
            'A': [" ## ", "#  #", "####", "#  #", "#  #"],
            'B': ["### ", "#  #", "### ", "#  #", "### "],
            'C': [" ###", "#   ", "#   ", "#   ", " ###"],
            'D': ["### ", "#  #", "#  #", "#  #", "### "],
            'E': ["####", "#   ", "### ", "#   ", "####"],
            'F': ["####", "#   ", "### ", "#   ", "#   "],
            'G': [" ###", "#   ", "# ##", "#  #", " ###"],
            'H': ["#  #", "#  #", "####", "#  #", "#  #"],
            'I': ["###", " # ", " # ", " # ", "###"],
            'J': ["  ##", "  # ", "  # ", "# # ", " #  "],
            'K': ["#  #", "## ", "#  ", "## ", "#  #"],
            'L': ["#   ", "#   ", "#   ", "#   ", "####"],
            'M': ["#   #", "## ##", "# # #", "#   #", "#   #"],
            'N': ["#   #", "##  #", "# # #", "#  ##", "#   #"],
            'O': [" ## ", "#  #", "#  #", "#  #", " ## "],
            'P': ["### ", "#  #", "### ", "#   ", "#   "],
            'Q': [" ## ", "#  #", "#  #", " ## ", "  ##"],
            'R': ["### ", "#  #", "### ", "## ", "#  #"],
            'S': [" ###", "#   ", " ## ", "   #", "### "],
            'T': ["#####", "  #  ", "  #  ", "  #  ", "  #  "],
            'U': ["#  #", "#  #", "#  #", "#  #", " ## "],
            'V': ["#   #", "#   #", " # # ", " # # ", "  #  "],
            'W': ["#   #", "#   #", "# # #", "## ##", "#   #"],
            'X': ["#  #", " ## ", " ## ", " ## ", "#  #"],
            'Y': ["#   #", " # # ", "  #  ", "  #  ", "  #  "],
            'Z': ["####", "  # ", " #  ", "#   ", "####"],
            ' ': ["  ", "  ", "  ", "  ", "  "],
        }
        text = text.upper()[:15]  # Limit length
        lines = ["", "", "", "", ""]
        for c in text:
            if c in font:
                for i in range(5):
                    lines[i] += font[c][i] + " "
            else:
                for i in range(5):
                    lines[i] += "  "

        output = "```\n" + "\n".join(lines) + "\n```"
        if len(output) > 1950:
            await ctx.send("Text too long for ASCII art.")
            return
        await ctx.send(output)

    # ------------------------------------------------------------------
    # .uwu <text> — uwuify text
    # ------------------------------------------------------------------
    @commands.command()
    async def uwu(self, ctx, *, text: str):
        """Uwuify text."""
        replacements = {
            'r': 'w', 'l': 'w', 'R': 'W', 'L': 'W',
            'no': 'nyo', 'No': 'Nyo', 'NO': 'NYO',
            'na': 'nya', 'Na': 'Nya', 'NA': 'NYA',
            'ne': 'nye', 'Ne': 'Nye', 'NE': 'NYE',
            'ni': 'nyi', 'Ni': 'Nyi', 'NI': 'NYI',
            'nu': 'nyu', 'Nu': 'Nyu', 'NU': 'NYU',
            'ove': 'uv', 'OVE': 'UV',
        }
        result = text
        for old, new in replacements.items():
            result = result.replace(old, new)
        faces = [' owo', ' uwu', ' >w<', ' ^w^', ' OwO', ' UwU']
        # Add a face at the end
        result += random.choice(faces)
        await ctx.send(result)

    # ------------------------------------------------------------------
    # .typeracer — typing speed test
    # ------------------------------------------------------------------
    _TYPERACER_SENTENCES = [
        "The quick brown fox jumps over the lazy dog.",
        "Pack my box with five dozen liquor jugs.",
        "How vexingly quick daft zebras jump.",
        "The five boxing wizards jump quickly.",
        "Sphinx of black quartz, judge my vow.",
        "Two driven jocks help fax my big quiz.",
        "Crazy Frederick bought many very exquisite opal jewels.",
        "We promptly judged antique ivory buckles for the next prize.",
        "A mad boxer shot a quick, gloved jab to the jaw of his dizzy opponent.",
        "The job requires extra pluck and zeal from every young wage earner.",
    ]

    @commands.command(aliases=['tr'])
    async def typeracer(self, ctx):
        """Typing speed test. Type the sentence as fast as you can!"""
        sentence = random.choice(self._TYPERACER_SENTENCES)
        await ctx.send(f"**Type this as fast as you can:**\n```\n{sentence}\n```")

        import time as _time
        start = _time.perf_counter()

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            response = await self.bot.wait_for('message', check=check, timeout=60)
        except asyncio.TimeoutError:
            await ctx.send("Time's up! You took too long.")
            return

        elapsed = _time.perf_counter() - start
        typed = response.content.strip()

        # Calculate accuracy
        correct = sum(1 for a, b in zip(typed, sentence) if a == b)
        total = max(len(sentence), len(typed))
        accuracy = (correct / total) * 100 if total > 0 else 0

        # Words per minute
        word_count = len(sentence.split())
        wpm = (word_count / elapsed) * 60

        if typed == sentence:
            result = "Perfect match!"
        else:
            result = f"Accuracy: {accuracy:.1f}%"

        await ctx.send(
            f"**Results:**\n"
            f"Time: {elapsed:.2f}s\n"
            f"Speed: {wpm:.1f} WPM\n"
            f"{result}"
        )

    # ==================================================================
    # TEXT MANIPULATION
    # ==================================================================

    # ------------------------------------------------------------------
    # .fancy <style> <text> — Unicode font styles
    # ------------------------------------------------------------------
    _FONT_MAPS = {
        'bold': {c: chr(0x1D400 + i) for i, c in enumerate('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz')},
        'italic': {c: chr(0x1D434 + i) for i, c in enumerate('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz')},
        'bolditalic': {c: chr(0x1D468 + i) for i, c in enumerate('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz')},
        'mono': {c: chr(0x1D670 + i) for i, c in enumerate('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz')},
        'gothic': {
            **{c: chr(0x1D504 + i) for i, c in enumerate('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz')},
            # Fix special gothic chars that aren't in sequence
            'C': '\u212D', 'H': '\u210C', 'I': '\u2111', 'R': '\u211C', 'Z': '\u2128',
        },
        'double': {c: chr(0x1D538 + i) for i, c in enumerate('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz')},
        'script': {c: chr(0x1D49C + i) for i, c in enumerate('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz')},
    }
    # Add digit mappings for bold
    for _style_name, _style_map in _FONT_MAPS.items():
        if _style_name == 'bold':
            _style_map.update({str(i): chr(0x1D7CE + i) for i in range(10)})
        elif _style_name == 'double':
            _style_map.update({str(i): chr(0x1D7D8 + i) for i in range(10)})
        elif _style_name == 'mono':
            _style_map.update({str(i): chr(0x1D7F6 + i) for i in range(10)})

    @commands.command()
    async def fancy(self, ctx, style: str = None, *, text: str = None):
        """Convert text to Unicode font. Styles: bold, italic, bolditalic, mono, gothic, double, script"""
        styles = list(self._FONT_MAPS.keys())
        if not style or style.lower() not in styles or not text:
            await ctx.send(
                f"**Available styles:** {', '.join(f'`{s}`' for s in styles)}\n"
                f"Usage: `{ctx.prefix}fancy <style> <text>`",
                delete_after=10
            )
            return

        font_map = self._FONT_MAPS[style.lower()]
        result = ''.join(font_map.get(c, c) for c in text)
        try:
            await ctx.message.delete()
        except Exception:
            pass
        await ctx.send(result)

    # ------------------------------------------------------------------
    # .spoilerify <text> — wrap every word in spoiler tags
    # ------------------------------------------------------------------
    @commands.command(aliases=['sp'])
    async def spoilerify(self, ctx, *, text: str):
        """Wrap every word in spoiler tags."""
        result = ' '.join(f'||{word}||' for word in text.split())
        try:
            await ctx.message.delete()
        except Exception:
            pass
        if len(result) > 1900:
            result = result[:1900]
        await ctx.send(result)

    # ------------------------------------------------------------------
    # .encrypt / .decrypt — Caesar cipher
    # ------------------------------------------------------------------
    @staticmethod
    def _caesar(text: str, shift: int) -> str:
        result = []
        for c in text:
            if c.isalpha():
                base = ord('A') if c.isupper() else ord('a')
                result.append(chr((ord(c) - base + shift) % 26 + base))
            else:
                result.append(c)
        return ''.join(result)

    @commands.command(aliases=['enc', 'cipher'])
    async def encrypt(self, ctx, shift: int = 13, *, text: str):
        """Encrypt text with Caesar cipher. Default shift: 13 (ROT13)."""
        if shift < 1 or shift > 25:
            await ctx.send("Shift must be between 1 and 25.", delete_after=5)
            return
        encrypted = self._caesar(text, shift)
        try:
            await ctx.message.delete()
        except Exception:
            pass
        await ctx.send(f"**[shift {shift}]** {encrypted}")

    @commands.command(aliases=['dec', 'decipher'])
    async def decrypt(self, ctx, shift: int = 13, *, text: str):
        """Decrypt Caesar cipher text. Default shift: 13 (ROT13)."""
        if shift < 1 or shift > 25:
            await ctx.send("Shift must be between 1 and 25.", delete_after=5)
            return
        decrypted = self._caesar(text, -shift)
        await ctx.send(f"**[decoded]** {decrypted}", delete_after=15)


async def setup(bot):
    await bot.add_cog(Fun(bot))

