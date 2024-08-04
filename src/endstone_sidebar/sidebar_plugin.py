import datetime
import uuid
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

        def year(p) -> str:
            return str(datetime.datetime.today().year)

        self.register_placeholder("year", year)

        def month(p) -> str:
            return str(datetime.datetime.today().month)

        self.register_placeholder("month", month)

        def day(p) -> str:
            return str(datetime.datetime.today().day)

        self.register_placeholder("day", day)

        def hour(p) -> str:
            return str(datetime.datetime.today().hour)

        self.register_placeholder("hour", hour)

        def minute(p) -> str:
            return str(datetime.datetime.today().minute)

        self.register_placeholder("minute", minute)

        def second(p) -> str:
            return str(datetime.datetime.today().second)

        self.register_placeholder("second", second)

        def address(p: Player) -> str:
            return str(p.address)

        self.register_placeholder("address", address)

        def runtime_id(p: Player) -> str:
            return str(p.runtime_id)

        self.register_placeholder("runtime_id", runtime_id)

        def exp_level(p: Player) -> str:
            return str(p.exp_level)

        self.register_placeholder("exp_level", exp_level)

        def total_exp(p: Player) -> str:
            return str(p.total_exp)

        self.register_placeholder("total_exp", total_exp)

        def exp_progress(p: Player) -> str:
            return str(p.exp_progress)

        self.register_placeholder("exp_progress", exp_progress)

        def gamemode(p: Player) -> str:
            return p.game_mode.name.lower()

        self.register_placeholder("gamemode", gamemode)

        def xuid(p: Player) -> str:
            return str(p.xuid)

        self.register_placeholder("xuid", xuid)

        def uuid(p: Player) -> str:
            return str(p.unique_id)

        self.register_placeholder("uuid", uuid)

        def device_os(p: Player) -> str:
            return p.device_os

        self.register_placeholder("device_os", device_os)

        def locale(p: Player) -> str:
            return p.locale

        self.register_placeholder("locale", locale)

    def register_placeholder(self, name: str, provider: Callable[[Player], str]) -> None:
        self.placeholders[name] = provider
