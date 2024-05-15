import os
from enum import Enum
from random import randint, choice
from time import sleep


def print_col(text: str, custom_sep: str = '&', end="\n"):
    message = text + end
    new_message = list(message)
    for index, letter in enumerate(message):
        if letter == custom_sep:
            dictionary = {
                'r': '0',  # сброс
                'l': '1',  # жирный
                'n': '4',  # подчёркнутый
                'm': '9',  # зачёркнутый
                'o': '3',  # курсив
                'N': '21',  # хорошо подчёркнутый
                '19': '34',  # синий
                '0': '30',  # чёрный
                '4c': '31',  # красный
                '2a': '32',  # зелёный
                '6e': '33',  # жёлтый
                '5d': '35',  # фиолетовый
                '3b': '36',  # бирюзовый
                '78': '37'  # серый
            }
            after = False
            try:
                next_letter = message[index + 1]
                after = True
                code = [v for k, v in dictionary.items() if next_letter in k][0]
            except IndexError as ex:
                nonewline = message.replace("\n", "\033[4Nm\033[0m")
                ex.args = (f'"{next_letter}" is not a valid code. Valid codes: {", ".join(dictionary.keys())}',)\
                    if after else (f'Excepted a valid code after "{custom_sep}" at index {index}:\n'
                                   f'{nonewline}\n{" " * index} ↑ THERE',)
                raise ex
            else:
                new_message[index] = '\033[' + code
                new_message[index + 1] = 'm'
    print(''.join(new_message), end="")


def get_all(super_: type):
    return [
        e() for e in globals().values()
        if e not in (super_, UserInput) and type(e) == type and issubclass(e, super_)
    ]


def safe_input(maximum):
    while True:
        try:
            a = int(input())
            assert 1 <= a <= maximum
            return a
        except:
            pass


class Steps(Enum):
    BETRAY    = False
    COOPERATE = True


class Game:
    def __init__(self, player1, player2, max_steps=100, both_betray=1, both_cooperate=3, betrayer=5, victim=0):
        self.step  = 0
        self.steps = []  # [(True, False), (False, False)]
        self._max_steps = max_steps  # Кол-во ходов не должно быть известно агентам!

        self.player1: BaseAgent = player1
        self.player2: BaseAgent = player2
        self.score1 = self.score2 = 0

        self.name_hidden = False  # Скрывает второго игрока, он будет раскрыт только в конце игры

        self.both_betray    = both_betray
        self.both_cooperate = both_cooperate
        self.betrayer       = betrayer
        self.victim         = victim

    def is_vs_player(self):
        return type(self.player1) == UserInput

    def get_opponents_steps(self, target) -> list[bool]:
        match target:
            case self.player1: index = 1
            case self.player2: index = 0
            case _: raise ValueError(f"Target must be an Agent (got {type(target)})")
        return [entry[index] for entry in self.steps]

    def get_opponent(self, target):
        return self.player1 if target == self.player2 else self.player2

    def get_opponents_step(self, target) -> bool:
        return self.get_current_state()[int(target == self.player1)]

    def get_current_state(self):
        return self.steps[self.step - 1] if self.step != 0 else (None, None)

    def perform_single(self):
        play = self.player1.on_turn(self), self.player2.on_turn(self)
        if play == (Steps.BETRAY, Steps.BETRAY):
            self.score1 += self.both_betray
            self.score2 += self.both_betray

        elif play == (Steps.COOPERATE, Steps.COOPERATE):
            self.score1 += self.both_cooperate
            self.score2 += self.both_cooperate

        elif play[0] == Steps.BETRAY:
            self.score1 += self.betrayer
            self.score2 += self.victim

        else:
            self.score1 += self.victim
            self.score2 += self.betrayer

        self.steps.append(play)

    def simulate(self):
        for _ in range(self.step, self._max_steps):
            self.perform_single()
            self.step += 1

        self.player1.scores.append(self.score1)
        self.player2.scores.append(self.score2)

        if self.is_vs_player():
            os.system("cls")
            self.print()

            if self.name_hidden:
                print_col("&7")
                if self.score1 > self.score2:
                    print("Хмм... Хоть тебе это и не надо, но могу предложить доп. очки, согласен? (Ничего не вводи для скипа)")
                    if input() != "": self.offer_deal()
                else:
                    print("Хмм...")
                    sleep(1)
                    self.offer_deal()

            if self.score1 > self.score2:
                print("\033[0m"
                    "#   #  #####  #####  #####  #####  ####   #   #",
                    "#   #    #    #        #    #   #  #   #  #   #",
                    "#   #    #    #        #    #   #  ####    ### ",
                    " # #     #    #        #    #   #  #  #      # ",
                    "  #    #####  #####    #    #####  #   #  ###  ", sep="\n"  # victory
                )
                print_col(f"Счёт: &a{self.score1}&7/&c{self.score2}&7 (разница {self.score1 - self.score2})")
            elif self.score1 < self.score2:
                print("\033[0m"
                      "####   #####  #####  #####    #    #####",
                      "#   #  #      #      #       # #     #  ",
                      "#   #  #####  #####  #####  #   #    #  ",
                      "#   #  #      #      #      #####    #  ",
                      "####   #####  #      #####  #   #    #  ", sep="\n"  # defeat
                      )
                print_col(f"Счёт: &a{self.score1}&7/&c{self.score2}&7 (разница {self.score2 - self.score1})")
            else:
                print("\033[0m"
                      "####   ####     #    #   #",
                      "#   #  #   #   # #   #   #",
                      "#   #  ####   #   #  #   #",
                      "#   #  #  #   #####  # # #",
                      "####   #   #  #   #  #   #", sep="\n"  # draw
                      )
                print_col(f"Счёт: &9{self.score1}&7/&9{self.score2}")

            if self.name_hidden:
                print_col(f"&rВторым игроком был: {self.player2.get_name_in_leader_board()}")

            os.system("pause")

    def offer_deal(self):
        add_score = 15

        if self.score1 + add_score < self.score2:
            print("Боюсь даже доп. очки тебе не помогут")
            sleep(1)
        else:
            print(
                f"Предлагаю сделку: если ты угадаешь кто твой соперник, то я дам тебе {add_score} очков, "
                f"тебе как раз до {'ничей' if self.score1 + add_score == self.score2 else 'победы'} хватит!\n"
            )
            print("Выбирай:")

            valid_players = [player for player in players if player.evil == self.player2.evil]
            for i, player in enumerate(valid_players, start=1):
                print_col(f'&7{i}. {player.get_name_in_leader_board()}&7 - &r"{player.bio}"')

            print_col("&7")
            lifes = randint(1, 3)
            while True:
                selected = safe_input(len(valid_players))
                if valid_players[selected - 1] == self.player2:
                    print(f"Угадал! Получай бонус в виде +{add_score} очков")
                    self.score1 += add_score
                    sleep(1)
                else:
                    lifes -= 1
                    print(["Не угадал, не дам тебе очков", "Не тот, может ещё раз?", "Не попал, ещё раз?"][lifes])
                    sleep(.5)
                    if lifes > 0: continue
                break

    def print(self):
        p1, p2 = self.player1.name, self.player2.name
        l1, l2 = map(len, (p1, p2))

        if self.name_hidden:
            p2 = "&oПротивник&r"
            l2 = len("Противник")
        print_col(f'&7"&5{p1} &{self.player1.get_col_code()}{self.player1.logo}&7"'
                   ' &b&eVS '
                  f'&7"&3{p2} &{self.player2.get_col_code()}{self.player2.logo}&7"')

        if l1 > l2: p2 += " " * (l1 - l2)
        if l2 > l1: p1 += " " * (l2 - l1)

        getter = lambda step: {Steps.BETRAY: "&c◉", Steps.COOPERATE: "&9◉"}.get(step, "&5?")
        print_col(f"&5{p1}&7 : " + '&r '.join([getter(step) for step in self.get_opponents_steps(self.player2)]))
        print_col(f"&3{p2}&7 : " + '&r '.join([getter(step) for step in self.get_opponents_steps(self.player1)]))

        print_col(f"&7Счёт: &5{self.score1}&7|&3{self.score2}", end="&7 ")
        if self.is_vs_player():
            print_col(f"; Ход: &r#{self.step+1}")
        elif self.step > 0:
            print_col(f"; Ход: &r{self.step+1}&7/&r{self._max_steps}")
        else:
            print_col(f"; Ходов: &r{self._max_steps}")


class BaseAgent:
    def __init__(self, name, bio=None, evil=False, by_chat_gpt=False):
        self.logo = "😇🔪"[int(evil)] if evil is not None else "💬"
        self.name = name
        self.bio  = bio if bio else "..."
        self.scores = []
        self.evil = evil
        self.by_chat_gpt = by_chat_gpt

    def __eq__(self, other):
        return self.name == other.name if isinstance(other, BaseAgent) else False

    def __repr__(self):
        return f'Prisoner "{self.name}" ({self.get_aver_score()} points)'

    def get_col_code(self):
        return {True: "c", False: "a", None: "9"}[self.evil]

    def get_name_in_leader_board(self):
        return f'&{self.get_col_code()}{self.logo} {self.name} {"🤖" if self.by_chat_gpt else ""}'

    def get_desc(self):
        return f'Агент "{self.name}" ({self.get_aver_score()} очков)' + (f"\n - Описание: {self.bio}" if self.bio else "")

    def on_turn(self, game: Game) -> Steps:
        """
        Метод, вызываемый при опросе агента, он должен вернуть или True (сотрудничает), или False (предаёт)
        """
        return True

    def get_aver_score(self):
        return sum(self.scores) / len(self.scores)


class AlwaysBetray(BaseAgent):
    def __init__(self):
        super().__init__("Предатель", "Неизменный враг", evil=True)

    def on_turn(self, game: Game) -> Steps:
        return Steps.BETRAY


class AlwaysCooperate(BaseAgent):
    def __init__(self):
        super().__init__("Верный союзник", "Доверяю всем!")

    def on_turn(self, game: Game) -> Steps:
        return Steps.COOPERATE


class Fridman(BaseAgent):
    def __init__(self):
        super().__init__("Фридман", "Не терпит предательства")
        self.was_betrayed = False

    def on_turn(self, game: Game) -> Steps:
        if game.get_opponents_step(self) == Steps.BETRAY:
            self.was_betrayed = True

        return Steps.BETRAY if self.was_betrayed else Steps.COOPERATE

class Sneaky(BaseAgent):
    def __init__(self):
        super().__init__("Хитрый", "Может предать, когда-нибудь", evil=True)

    def on_turn(self, game: Game) -> Steps:
        if game.get_opponents_step(self) == Steps.BETRAY:
            return Steps.BETRAY
        else:
            return Steps.BETRAY if randint(1, 7) == 1 else Steps.COOPERATE

class Imposter(BaseAgent):
    def __init__(self):
        super().__init__("Обманщик", "Будет предавать всегда, когда-нибудь...", evil=True)
        self.freak_out = False

    def on_turn(self, game: Game) -> Steps:
        if randint(1, 15) == 1 or game.get_opponents_step(self) == Steps.BETRAY: self.freak_out = True

        return Steps.BETRAY if self.freak_out else Steps.COOPERATE


class TitForTat(BaseAgent):
    def __init__(self):
        super().__init__("Око за око", "Да будет возмездие!")

    def on_turn(self, game: Game) -> Steps:
        return game.get_opponents_step(self) or Steps.COOPERATE


class TitForTwoTats(BaseAgent):
    def __init__(self):
        super().__init__("Око за два ока", "Терпит дважды, но не больше")

    def on_turn(self, game: Game) -> Steps:
        if game.step > 2:
            last_steps = game.get_opponents_steps(self)
            return Steps.BETRAY if last_steps[0] == Steps.BETRAY and last_steps[1] == Steps.BETRAY else Steps.COOPERATE
        return Steps.COOPERATE


class Tester(BaseAgent):
    def __init__(self):
        super().__init__("Тестер", "Первый ход скажет мне кто ты", evil=True)
        self.is_opponent_nice = False

    def on_turn(self, game: Game) -> Steps:
        if game.step == 0:
            return Steps.BETRAY
        if game.step == 1:
            self.is_opponent_nice = game.get_opponents_step(self) == Steps.COOPERATE

        if self.is_opponent_nice:
            return Steps.COOPERATE if game.step % 2 else Steps.BETRAY
        else:
            return game.get_opponents_step(self)

class AdaptiveAgent(BaseAgent):
    def __init__(self):
        super().__init__("Адаптивный", "Меняет свое поведение, если часто предаёшь", by_chat_gpt=True)

    def on_turn(self, game: Game) -> Steps:
        if game.step > 0:
            # Получаем шаги оппонента
            opponent_steps = game.get_opponents_steps(self)
            betray_count = opponent_steps.count(Steps.BETRAY)
            betray_ratio = betray_count / game.step

            # Если более 50% ходов оппонент предавал, то агент тоже начинает предавать
            if betray_ratio > 0.5:
                return Steps.BETRAY

        # По умолчанию сотрудничает
        return Steps.COOPERATE

class ForgivingAgent(BaseAgent):
    def __init__(self):
        super().__init__("Прощающий агент", "Прощает один раз, потом наказывает!",
                         evil=True, by_chat_gpt=True)
        self.was_betrayed_last_turn = False

    def on_turn(self, game: Game) -> Steps:
        if game.step > 0:
            opponent_last_step = game.get_opponents_step(self)
            if opponent_last_step == Steps.BETRAY:
                if self.was_betrayed_last_turn:
                    self.was_betrayed_last_turn = False
                    return Steps.COOPERATE
                else:
                    self.was_betrayed_last_turn = True
                    return Steps.BETRAY
            else:
                self.was_betrayed_last_turn = False
                return Steps.COOPERATE
        else:
            return Steps.COOPERATE

class OpportunistAgent(BaseAgent):
    def __init__(self):
        super().__init__("Оппортунист", "Всегда ищет выгоду", evil=True, by_chat_gpt=True)

    def on_turn(self, game: Game) -> Steps:
        if game.step > 0:
            return\
                Steps.BETRAY\
                    if game.betrayer > game.both_cooperate or\
                    self.scores[-1] < game.get_opponent(self).scores[-1] else\
                Steps.COOPERATE

        return Steps.COOPERATE

class SpitefulAgent(BaseAgent):
    def __init__(self):
        super().__init__("Мститель", "Запомнит твоё предательство и отплатит сполна!",
                         evil=True, by_chat_gpt=True)
        self.spiting = False

    def on_turn(self, game: Game) -> Steps:
        if game.step > 0:
            if game.get_opponents_step(self) == Steps.BETRAY:
                self.spiting = True
            elif self.spiting and game.get_opponents_step(self) == Steps.COOPERATE:
                self.spiting = False

            if self.spiting:
                return Steps.BETRAY
        return Steps.COOPERATE

class CooperativeStrategist(BaseAgent):
    def __init__(self):
        super().__init__("Стратег-сотрудник", "Сотрудничает сначала, затем адаптируется", evil=False, by_chat_gpt=True)
        self.initial_cooperate_steps = 3

    def on_turn(self, game: Game) -> Steps:
        if game.step < self.initial_cooperate_steps:
            return Steps.COOPERATE
        else:
            return game.get_opponents_step(self)

class PeacefulAgent(BaseAgent):
    def __init__(self):
        super().__init__("Миролюбивый агент", "Сотрудничает, если оппонент сотрудничал хотя бы раз за последние два хода", evil=False, by_chat_gpt=True)

    def on_turn(self, game: Game) -> Steps:
        if game.step > 0:
            last_steps = game.get_opponents_steps(self)
            if len(last_steps) > 1:
                return Steps.COOPERATE if last_steps[-1] == Steps.COOPERATE or last_steps[-2] == Steps.COOPERATE else Steps.BETRAY
            else:
                return Steps.COOPERATE if last_steps[-1] == Steps.COOPERATE else Steps.BETRAY
        return Steps.COOPERATE

class UserInput(BaseAgent):
    def __init__(self):
        super().__init__("Пользователь", 'Берёт ввод у пользователя, не может быть выбран при режиме "Все против всех"', evil=None)

    def on_turn(self, game: Game) -> Steps:
        os.system("cls")
        game.print()
        while True:
            print_col('&rПредать: &c"-"&7, &rСотрудничать: &9"+"')
            in_ = input()
            if in_ == "-": return Steps.BETRAY
            if in_ == "+": return Steps.COOPERATE


players: list[BaseAgent] = get_all(BaseAgent)

print("Выбери режим:")
print("1. Все против всех")
print("2. Я против кого-то")
mode = input()
if mode == "1":

    for p1 in players:
        for p2 in players:
            game = Game(p1, p2)
            game.simulate()

    for i, player in enumerate(sorted(players, key=BaseAgent.get_aver_score, reverse=True), start=1):
        player: BaseAgent
        print_col(f'&7#{i} {player.get_name_in_leader_board()}&7 - &r{player.get_aver_score():.1f}&8 ; "{player.bio}"')

elif mode == "2":

    print("Теперь выбери против кого:")
    for i, player in enumerate(players, start=1):
        print_col(f'&7{i}. {player.get_name_in_leader_board()}')
    print_col(f'&7{len(players)+1}. &eСлучайный соперник (+10 очков сопернику)')
    select = safe_input(len(players) + 1)

    game = Game(UserInput(), None, max_steps=10 + randint(-2, 2))

    if select == len(players) + 1:
        opponent = choice(players)
        game.name_hidden = True
        game.score2 = 10
    else:
        opponent = players[select - 1]

    game.player2 = opponent
    game.simulate()
