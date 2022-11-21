from pipo.groovy import Groovy
from .command import Command

class Join(Command):

    def __init__(self, bot: Groovy, ctx) -> None:
        self._bot = bot
        self._ctx = ctx

    async def execute(self) -> None:
        await self._bot.join(self._ctx)
