from typing import Callable

from endstone.event import PlayerJoinEvent
from endstone.event import event_handler
from endstone.plugin import Plugin
from endstone import Player
from endstone.scoreboard import *

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
            self, self.update_sidebar,
            delay=0, period=self.update_period
        )

    @event_handler
    def on_player_join(self, event: PlayerJoinEvent) -> None:
        event.player.scoreboard = self.server.get_new_scoreboard()

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

        objective = player.scoreboard.add_objective(CUSTOM_OBJECTIVE_NAME, Criteria.DUMMY, t)

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
        # Populate the dict
        d = {}
        for name, provider in self.placeholders.items():
            d[name] = provider(player)

        # Magic!!!
        return string.format(**d)

    def register_default_placeholders(self):
        def x(p: Player) -> str:
            return f"{p.location.x:.0f}"

        self.register_placeholder("x", x)

        def y(p: Player) -> str:
            return f"{p.location.y:.0f}"

        self.register_placeholder("y", y)

        def z(p: Player) -> str:
            return f"{p.location.z:.0f}"

        self.register_placeholder("z", z)

        def player_name(p: Player) -> str:
            return p.name

        self.register_placeholder("player_name", player_name)

        def dimension(p: Player) -> str:
            return p.location.dimension.type.name.lower()

        self.register_placeholder("dimension", dimension)

        def dimension_id(p: Player) -> str:
            return str(p.location.dimension.type.value)

        self.register_placeholder("dimension_id", dimension_id)

        def ping(p: Player) -> str:
            return str(p.ping)

        self.register_placeholder("ping", ping)

        def mc_version(p) -> str:
            return self.server.minecraft_version

        self.register_placeholder("mc_version", mc_version)

        def online(p) -> str:
            return str(len(self.server.online_players))

        self.register_placeholder("online", online)

        def max_online(p) -> str:
            return str(self.server.max_players)

        self.register_placeholder("max_online", max_online)

    def register_placeholder(self, name: str, provider: Callable[[Player], str]) -> None:
        self.placeholders[name] = provider
