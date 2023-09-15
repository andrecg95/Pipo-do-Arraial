#!usr/bin/env python3
"""Music Player."""
import asyncio
import logging
from typing import List, Union

from pipo.config import settings
from pipo.player.music_queue.music_queue import MusicQueue
from pipo.player.music_queue.music_queue_factory import MusicQueueFactory


class Player:
    """Manage music and Discord voice channel interactions.

    Acts as facilitator to manage audio information while interacting with Discord.
    Maintains a music queue to which new audio sources are asynchronously added when
    calling :meth:`~Player.play`. A thread is used to stream audio to Discord
    until the music queue is exhausted. Whether such thread is allowed to continue
    consuming the queue is specified using :attr:`~Player.can_play`.

    Attributes
    ----------
    __bot : :class:`~pipo.bot.PipoBot`
        Client Discord bot.
    __logger : logging.Logger
        Class logger.
    __player_thread : asyncio.Task
        Obtains and plays music from :attr:`~Player._music_queue`.
    _music_queue : :class:`~pipo.player.music_queue.music_queue.MusicQueue`
        Stores music to play.
    can_play : asyncio.Event
        Whether new music from queue can be played.
    """

    __bot: None
    __logger: logging.Logger
    __player_thread: asyncio.Task
    _music_queue: MusicQueue
    can_play: asyncio.Event

    def __init__(self, bot) -> None:
        """Build music player.

        Parameters
        ----------
        bot : :class:`~pipo.bot.PipoBot`
            Client Discord bot.
        """
        self.__bot = bot
        self.__logger = logging.getLogger(__name__)
        self.__player_thread = None
        self.can_play = asyncio.Event()
        self._music_queue = MusicQueueFactory.get(settings.player.queue.type)

    def stop(self) -> None:
        """Reset music queue and halt currently playing audio."""
        self.__clear_queue()
        self.__player_thread.cancel()
        self.__bot.voice_client.stop()
        self.can_play.set()

    def skip(self) -> None:
        """Skip currently playing music."""
        self.__bot.voice_client.stop()

    def pause(self) -> None:
        """Pause currently playing music."""
        self.__bot.voice_client.pause()

    def resume(self) -> None:
        """Resume previously paused music."""
        self.__bot.voice_client.resume()

    async def leave(self) -> None:
        """Make bot leave the current server."""
        await self.__bot.voice_client.disconnect()

    def queue_size(self) -> int:
        """Get music queue size."""
        return self._music_queue.size()

    def play(self, queries: Union[str, List[str]], shuffle: bool = False) -> None:
        """Add music to play.

        Enqueues music to be played when player thread is free and broadcasts such
        availability. Music thread is initialized if not yet available.

        Parameters
        ----------
        queries : Union[str, List[str]]
            Single/list of music or playlist urls. If a query string is provided
            the best guess music is played.
        shuffle : bool, optional
            Randomize play order when multiple musics are provided, by default False.
        """
        if (not self.__player_thread) or (
            self.__player_thread
            and (self.__player_thread.done() or self.__player_thread.cancelled())
        ):
            self._start_music_queue()
        if not isinstance(queries, (list, tuple)):  # ensure an Iterable is used
            queries = [
                queries,
            ]
        self.__add_music(queries, shuffle)

    def __add_music(self, queries: List[str], shuffle: bool) -> None:
        """Add music to play queue.

        Enqueues music to be played when player thread is free and broadcasts such
        availability. Music thread is initialized if not yet available.

        Parameters
        ----------
        queries : List[str]
            List comprised of music, search query or playlist urls. If a query string is
            found the best guess music is played.
        shuffle : bool
            Randomize order by which queries are added to play queue.
        """
        self.__logger.info("Processing music query %s", queries)
        self._music_queue.add(
            queries,
            shuffle,
        )  # source_type) TODO decide how to use

    def _start_music_queue(self) -> None:
        """Initialize music thread.

        Initializes music thread and allows music queue consumption.
        """
        self.can_play.set()
        self.__player_thread = asyncio.create_task(self.__play_music_queue())

    def __clear_queue(self) -> None:
        """Clear music queue."""
        self._music_queue.clear()

    async def _submit_music(self, url: str) -> None:
        # TODO consider raised exceptions
        await self.__bot.submit_music(url)

    async def __play_music_queue(self) -> None:
        """Play music task.

        Obtains a music from :attr:`~pipo.play.player.Player._music_queue` and creates
        a task to submit to the Discord bot to be played.
        """
        self.__logger.info("Entering music play loop")
        while await self.can_play.wait():
            if not self.queue_size():
                break
            self.can_play.clear()
            self.__logger.debug("Entered music play loop %s", self.queue_size())
            url = self._music_queue.get()
            if url:
                try:
                    await self.__bot.submit_music(url)
                except asyncio.CancelledError:
                    self.__logger.info("Play music task cancelled", exc_info=True)
                except Exception:
                    self.__logger.warning("Unable to play next music", exc_info=True)
                    await self.__bot.send_message(settings.player.messages.play_error)
            else:
                self.__logger.info(
                    "Unable to play next music, obtained invalid url %s", url
                )
                await self.__bot.send_message(settings.player.messages.play_error)
        self.can_play.set()
        self.__logger.info("Exiting play music queue loop")
        self.__bot.become_idle()