"""discord bot runnable script"""
import os

import discord
from dotenv import load_dotenv

from googlesheets.googlesheets import VALORANT_WORKSHEET, VALORANT_WORKSHEET
from ranks.valorantRanks import VALORANT_RANKS, RANKS_URL


logChannelId = 1000040420807548949

def load_environment():
    """loads envrionment variables"""
    load_dotenv()
    TOKEN = os.getenv("DISCORD_TOKEN")  # pylint: disable=invalid-name
    GUILDS = os.getenv("GUILD_ID").split(",")  # pylint: disable=invalid-name
    for i in range(len(GUILDS)):  # pylint: disable=consider-using-enumerate
        GUILDS[i] = int(GUILDS[i])

    return TOKEN, GUILDS


def instantiate():
    bot = discord.Bot()

    return bot


def main():
    print("Libraries successfully imported...")
    print("Loading environment variables...")
    TOKEN, GUILDS = load_environment()  # pylint: disable=invalid-name
    print("Environment variables successfully loaded...")


    print("Instantiating bot...")
    bot = instantiate()

    @bot.event
    async def on_ready():
        """on ready function"""
        print(f"{bot.user} has successfully connected to discord...")

    valorant = bot.create_group(
        "valorant", "commands related to valorant accounts", GUILDS
    )

    @valorant.command(
        name="use", description="use a valorant account", guild_ids=GUILDS
    )
    async def use(ctx, ign: discord.Option(str, "in-game name", required=True)):
        """use function"""
        await ctx.defer(ephemeral=True)

        result = VALORANT_WORKSHEET.find(ign, in_column=1)
        print('PRINT RESULT')
        print(result)

        if not result:
            await ctx.respond("Account not found", ephemeral=True)
            return

        row = VALORANT_WORKSHEET.row_values(result.row)
        using = row[9]

        try:
            using_user = row[10]
        except IndexError:
            using_user = ""

        tagline = row[1]
        username = row[2]
        password = row[3]
        competitive = "Unlocked" if row[4] == "TRUE" else "Locked"
        current_rank = row[5]
        peak_rank = row[6]
        skins = "Present" if row[7] == "TRUE" else "None"

        if using == "TRUE":
            await ctx.respond(f"{using_user} is using the account", ephemeral=True)
            print("valorant account in use")
            return

        discord_user = ctx.user

        VALORANT_WORKSHEET.update(
            f"J{result.row}:K{result.row}", [[True, str(discord_user)]]
        )

        embed = discord.Embed(
            title=f"{ign}#{tagline}",
            description="\n",
            colour=discord.Colour.from_rgb(80, 146, 223),
        )
        embed.set_thumbnail(url=RANKS_URL.get(current_rank))
        embed.add_field(name="Competitive", value=competitive, inline=True)

        if competitive == "Unlocked":
            embed.add_field(name="Current Rank", value=current_rank, inline=True)
            embed.add_field(name="Peak Rank", value=peak_rank, inline=True)

        embed.add_field(name="Skins", value=skins, inline=False)
        embed.add_field(name="Username", value=username, inline=True)
        embed.add_field(name="Password", value=password, inline=True)

        await ctx.respond(embed=embed, ephemeral=True)


        # Admin logs
        embed = discord.Embed(
            title="Valorant Account Used",
            description="\n",
            colour=discord.Colour.from_rgb(80, 146, 223),
        )
        embed.add_field(name="Discord Username", value=str(discord_user), inline=False)
        embed.add_field(name="Valorant IGN", value=ign, inline=False)

        log_channel = bot.get_channel(logChannelId)
        await log_channel.send(embed=embed)
        print('complete command in use')

    @valorant.command(
        name="abandon", description="abandon a valorant account", guild_ids=GUILDS
    )
    async def abandon(
        ctx,
        ign: discord.Option(str, "in-game name", required=True),
        new_rank: discord.Option(
            str,
            name="new-rank",
            description="new rank",
            choices=VALORANT_RANKS,
            required=False,
        ),
        all: discord.Option(
            str,
            name="all",
            description="abandon all",
            required=False,
        )
    ):
        """abandon function"""

        await ctx.defer(ephemeral=True)
        result = VALORANT_WORKSHEET.find(ign, in_column=1)

        if not result:
            await ctx.respond("Account not found", ephemeral=True)
            return

        row = result.row

        using, tagline = VALORANT_WORKSHEET.batch_get([f"J{row}", f"B{row}"])
        using, tagline = using[0][0], tagline[0][0]

        if using == "FALSE":
            await ctx.respond("Account not in use", ephemeral=True)
            return

        if all:
            ign = VALORANT_WORKSHEET.col_values(1)
            rows = len(ign)

            in_use = VALORANT_WORKSHEET.batch_get([f"J2:K{rows}"])

            for i in range(1, rows):
                if in_use[i - 1][0] == "TRUE":
                    pass
                else:
                    reply += f"{ranks[i - 1][0]} - {ign[i]}\n"

            updates = [{"range": f"J{row}:K{row}", "values": [[False, ""]]}]

        updates = [{"range": f"J{row}:K{row}", "values": [[False, ""]]}]

        if new_rank:
            updates.append({"range": f"F{row}", "values": [[new_rank]]})

        VALORANT_WORKSHEET.batch_update(updates)

        embed = discord.Embed(
            title=f"{ign}#{tagline}",
            description="Abandoned",
            colour=discord.Colour.from_rgb(80, 146, 223),
        )

        await ctx.respond(embed=embed, ephemeral=True)

        #admin logs
        embed = discord.Embed(
            title="Valorant Account Abandoned",
            description="\n",
            colour=discord.Colour.from_rgb(80, 146, 223),
        )
        embed.add_field(name="Discord Username", value=str(ctx.user), inline=False)
        embed.add_field(name="Valorant IGN", value=ign, inline=False)

        log_channel = bot.get_channel(logChannelId)
        await log_channel.send(embed=embed)

    @valorant.command(
        name="accounts",
        description="view unused accounts from the valorant account bank",
        guild_ids=GUILDS,
    )
    async def accounts(ctx):
        """accounts function"""
        ign = VALORANT_WORKSHEET.col_values(1)
        rows = len(ign)

        if rows < 2:
            await ctx.respond("No accounts available", ephemeral=True)
            return

        result = VALORANT_WORKSHEET.batch_get([f"F2:F{rows}", f"J2:K{rows}"])
        ranks = result[0]
        use_status = result[1]

        reply = ""

        for i in range(1, rows):
            if use_status[i - 1][0] == "TRUE":
                pass
            else:
                reply += f"{ranks[i - 1][0]} - {ign[i]}\n"

        await ctx.respond(reply, ephemeral=True)

        #admin logs
        embed = discord.Embed(
            title="Valorant Account Bank Viewed",
            description="\n",
            colour=discord.Colour.from_rgb(80, 146, 223),
        )
        embed.add_field(name="Discord Username", value=str(ctx.user), inline=False)

        log_channel = bot.get_channel(logChannelId)
        await log_channel.send(embed=embed)

    # run bot
    bot.run(TOKEN)


if __name__ == "__main__":
    main()
