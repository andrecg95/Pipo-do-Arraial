import pytest

import tests.constants

import pipo.player

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
