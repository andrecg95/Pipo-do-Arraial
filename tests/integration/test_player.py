import functools

import pytest

import pipo.player
import tests.constants


class TestPlayer:
    @pytest.fixture(scope="function", autouse=True)
    def player(self, mocker):
        player = pipo.player.Player(None)
        # disable music queue consumption
        mocker.patch.object(player, "_start_music_queue")
        return player

    @pytest.mark.parametrize("url", tests.constants.URL_SIMPLE_LIST)
    def test_get_youtube_audio(self, player, url):
        assert player.get_youtube_audio(url)

    @pytest.mark.parametrize(
        "url, queue_size",
        [
            ("", 0),
            (tests.constants.URL_1, 1),
            (tests.constants.URL_2, 1),
            (tests.constants.URL_3, 1),
            (tests.constants.URL_4, 1),
            (tests.constants.URL_5, 1),
        ],
    )
    def test_play_single_url(self, player, url, queue_size):
        player.play(url)
        assert player.queue_size() == queue_size

    @pytest.mark.parametrize(
        "url_list",
        [
            [],
            tests.constants.URL_SIMPLE_LIST,
            tests.constants.URL_COMPLEX_LIST,
        ],
    )
    def test_play_multiple_url(self, player, url_list):
        player.play(url_list)
        assert player.queue_size() == len(url_list)

    @pytest.mark.parametrize(
        "url_list",
        [
            "",
            [],
        ],
    )
    def test_empty_queue_shuffle(self, player, url_list):
        player.play(url_list)
        player.shuffle()
        assert player.queue_size() == 0

    @pytest.mark.parametrize(
        "url_list",
        [
            tests.constants.URL_1,
            tests.constants.URL_2,
            tests.constants.URL_3,
        ],
    )
    def test_single_item_queue_shuffle(self, helpers, player, url_list):
        music_urls = player.play(url_list)
        initial_music_queue = player._music_queue.get_all().copy()
        player.shuffle()
        assert helpers.compare_iterables(
            initial_music_queue, player._music_queue.get_all()
        )
        assert len(music_urls) == 1

    @pytest.mark.parametrize(
        "url_list",
        [
            tests.constants.URL_SIMPLE_LIST,
            tests.constants.URL_COMPLEX_LIST,
        ],
    )
    def test_multi_item_queue_shuffle(self, helpers, player, url_list):
        music_urls = player.play(url_list)
        initial_music_queue = player._music_queue.get_all().copy()
        player.shuffle()
        assert not helpers.compare_iterables(
            initial_music_queue, player._music_queue.get_all()
        )
        assert len(music_urls) >= 0