from dataclasses import dataclass

from discord.ext.commands import Context as Dctx

from pipo.groovy import Groovy
from pipo.command.command import Command


@dataclass
class PlayList(Command):
    bot: Groovy
    ctx: Dctx
    query: str
    shuffle: bool

    async def execute(self) -> None:
        self.ctx.kwargs["_query_"] = " ".join(self.query)
        await self.bot.play_list(self.ctx, shuffle=self.shuffle)