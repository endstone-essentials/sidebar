import datetime
import typing
from typing import Callable

from endstone.event import PlayerJoinEvent
from endstone.event import event_handler
from endstone.plugin import Plugin
from endstone import Player
from endstone.scoreboard import Objective, DisplaySlot, Criteria

CUSTOM_OBJECTIVE_NAME = "__CUSTOM_SIDEBAR_OBJECTIVE__"


class SidebarPlugin(Plugin):
    api_version = "0.5"

    def __init__(self):
        super().__init__()
        self.update_period: int = 20
        self.sidebar_title: str = ""
        self.sidebar_content: list[str] = []
        self.placeholders: dict[str, Callable[[Player], str]] = {}

    def on_enable(self) -> None:
        self.save_default_config()
        self.load_config()
        self.register_events(self)
        self.register_default_placeholders()
        self.server.scheduler.run_task(
            self, self.update_sidebar, delay=0, period=self.update_period
        )

    @event_handler
    def on_player_join(self, event: PlayerJoinEvent) -> None:
        event.player.scoreboard = self.server.create_scoreboard()

    def update_sidebar(self) -> None:
        for player in self.server.online_players:
            self.update_sidebar_for(player)

    def update_sidebar_for(self, player: Player) -> None:
        if player.scoreboard is self.server.scoreboard:
            return

        t = self.replace_placeholder(self.sidebar_title, player)

        c: list[str] = []
        for line in self.sidebar_content:
            c.append(self.replace_placeholder(line, player))

        objective: Objective = player.scoreboard.get_objective(CUSTOM_OBJECTIVE_NAME)

        if objective is not None:
            objective.unregister()

        objective = player.scoreboard.add_objective(
            CUSTOM_OBJECTIVE_NAME, Criteria.DUMMY, t
        )

        counter = 0
        for line in c:
            objective.get_score(line).value = counter
            counter += 1

        objective.set_display(DisplaySlot.SIDE_BAR)

    def load_config(self) -> None:
        self.update_period = self.config["update_period"]
        self.sidebar_title = self.config["sidebar"]["title"]
        self.sidebar_content = self.config["sidebar"]["content"]

    def replace_placeholder(self, string: str, player: Player) -> str:
        args = {}
        for key, provider in self.placeholders.items():
            args[key] = str(provider(player))

        return string.format(**args)

    def register_default_placeholders(self):
        self.register_placeholder("x", lambda p: int(p.location.x))
        self.register_placeholder("y", lambda p: int(p.location.y))
        self.register_placeholder("z", lambda p: int(p.location.z))
        self.register_placeholder("player_name", lambda p: p.name)
        self.register_placeholder("dimension", lambda p: p.location.dimension.type.name.lower())
        self.register_placeholder("dimension_id", lambda p: p.location.dimension.type.value)
        self.register_placeholder("ping", lambda p: p.ping)
        self.register_placeholder("mc_version", lambda _: self.server.minecraft_version)
        self.register_placeholder("online", lambda _: len(self.server.online_players))
        self.register_placeholder("max_online", lambda _: self.server.max_players)
        self.register_placeholder("year", lambda _: datetime.datetime.today().year)
        self.register_placeholder("month", lambda _: datetime.datetime.today().month)
        self.register_placeholder("day", lambda _: datetime.datetime.today().day)
        self.register_placeholder("hour", lambda _: datetime.datetime.today().hour)
        self.register_placeholder("minute", lambda _: datetime.datetime.today().minute)
        self.register_placeholder("second", lambda _: datetime.datetime.today().second)
        self.register_placeholder("address", lambda p: p.address)
        self.register_placeholder("runtime_id", lambda p: p.runtime_id)
        self.register_placeholder("exp_level", lambda p: p.exp_level)
        self.register_placeholder("total_exp", lambda p: p.total_exp)
        self.register_placeholder("exp_progress", lambda p: p.exp_progress)
        self.register_placeholder("gamemode", lambda p: p.gamemode.name.lower())
        self.register_placeholder("xuid", lambda p: p.xuid)
        self.register_placeholder("uuid", lambda p: p.unique_id)
        self.register_placeholder("device_os", lambda p: p.device_os)
        self.register_placeholder("locale", lambda p: p.locale)

    def register_placeholder(
            self, name: str, provider: Callable[[Player], typing.Any]
    ) -> None:
        self.placeholders[name] = provider
