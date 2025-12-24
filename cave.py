import random
import os
import msvcrt


class SimpleCave:
    def __init__(self, width=30, height=15):
        os.system("")
        self.width = width
        self.height = height
        self.depth = 1
        self.health = 10
        self.max_health = 10
        self.slime_count = 0
        self.monster_damage = 1.0 + (self.depth // 5) * 0.1
        self.timer = 0
        self.monsters_activated = False
        self.message = ""
        self.enemies = []
        self.slimes = []
        self.traps = []
        self.artifacts_collected = 0
        self.px, self.py = 0, 0
        self.bonus_42 = False
        self.bonus_st = False
        self.bonus_deep = False
        self.bonus_slime = False
        self.bonus_view = False
        self.generate_level()

    def generate_level(self):
        self.message = ""
        self.enemies = []
        self.slimes = []
        self.traps = []
        self.map = [["#" for _ in range(self.width)] for _ in range(self.height)]
        x, y = random.randint(1, self.width - 2), random.randint(1, self.height - 2)
        self.px, self.py = x, y
        steps = (self.width * self.height) // 3
        floor_tiles = []
        while steps > 0:
            if self.map[y][x] == "#":
                self.map[y][x] = "."
                floor_tiles.append((x, y))
                steps -= 1
            dx, dy = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
            if 1 <= x + dx < self.width - 1 and 1 <= y + dy < self.height - 1:
                x, y = x + dx, y + dy

        if self.depth > 0 and self.depth % 10 == 0:
            self.map[y][x] = "A"
        elif self.depth == 4:
            self.map[y][x] = "F"
        else:
            self.map[y][x] = "E"

        if self.monsters_activated and self.depth >= 5:
            for _ in range(3):
                if not floor_tiles: break
                mx, my = random.choice(floor_tiles)
                if (mx, my) != (self.px, self.py):
                    self.enemies.append([mx, my])

        if self.depth % 15 == 0:
            self.timer = 40
            self.message = "\033[41m⚠️ НЕСТАБИЛЬНАЯ ЗОНА! УСПЕЙ ВЫЙТИ! ⚠️\033[0m"
        else:
            self.timer = -1

        if self.depth >= 5:
            self.monster_damage = round(1.0 + ((self.depth - 5) // 5) * 0.1, 1)
        else:
            self.monster_damage = 1.0

        if self.depth >= 3:
            for _ in range(random.randint(2, 4)):
                if not floor_tiles: break
                tx, ty = random.choice(floor_tiles)
                if (tx, ty) != (self.px, self.py) and self.map[ty][tx] == ".":
                    self.traps.append([tx, ty])

    def get_hp(self):
        percent = self.health / self.max_health
        display_hp = round(self.health, 1)
        if percent > 0.7:
            color = "\033[32m"
        elif percent > 0.3:
            color = "\033[33m"
        else:
            color = "\033[5;31m"
        return f"{color}{display_hp}/{self.max_health} HP\033[0m"

    def collect_artifact(self):
        self.max_health += 5
        self.health = self.max_health
        self.artifacts_collected += 1
        self.generate_level()
        self.message = f"\033[33m⭐ АРТЕФАКТ! Макс. HP увеличено до {self.max_health}!\033[0m"
        self.depth += 1

    def move_enemies(self):
        for i in range(len(self.enemies)):
            ex, ey = self.enemies[i]
            dx = 1 if ex < self.px else -1 if ex > self.px else 0
            dy = 1 if ey < self.py else -1 if ey > self.py else 0
            nx, ny = ex + dx, ey + dy

            if nx == self.px and ny == self.py:
                self.health -= self.monster_damage
                self.message = f"\033[31m💥 Монстр укусил вас! -{self.monster_damage} HP\033[0m"
            elif self.map[ny][nx] == "." and [nx, ny] not in self.enemies:
                self.enemies[i] = [nx, ny]

    def move(self, dx, dy):
        self.message = ""
        self.bonus_view = False

        if self.timer > 0:
            self.timer -= 1
            if self.timer == 0:
                self.health = 0
                self.message = "\033[31m💥 ОБВАЛ! Вы не успели!\033[0m"

        nx, ny = self.px + dx, self.py + dy
        if 0 <= nx < self.width and 0 <= ny < self.height:
            if [nx, ny] in self.enemies:
                self.enemies.remove([nx, ny])
                self.slimes.append([nx, ny])
                self.message = "\033[31m⚔️ Монстр убит!\033[0m \033[32mВыпала слизь.\033[0m"
                if random.random() > 0.4:
                    self.health -= self.monster_damage
            elif [nx, ny] in self.slimes:
                self.slimes.remove([nx, ny])
                self.slime_count += 1
                self.message = "\033[32m✨ Слизь собрана.\033[0m"
            elif self.map[ny][nx] != "#":
                self.px, self.py = nx, ny

                if [self.px, self.py] in self.traps:
                    self.health -= 2.0
                    self.traps.remove([self.px, self.py])
                    self.message = "\033[31m⚠️ КРАК! Вы наступили на шипы! -2.0 HP\033[0m"

                tile = self.map[self.py][self.px]
                if tile == "A":
                    self.collect_artifact()
                    return
                elif tile in ["F", "E"]:
                    if tile == "F": self.monsters_activated = True
                    self.depth += 1
                    self.generate_level()
                    return

        if self.monsters_activated: self.move_enemies()
        if self.health <= 0:
            if os.path.exists("savegame.json"):
                os.remove("savegame.json")

            print("\n\033[31m" + "Ы" * 50 + "\nВЫ ПОГИБЛИ!\033[0m")
            input()
            exit()

    def draw(self):
        print("\033[H\033[?25l", end="")
        hp_info = self.get_hp()

        time_info = ""
        if self.timer >= 0:
            t_color = "\033[32m" if self.timer > 15 else "\033[5;31m"
            time_info = f" | {t_color}⌛ {self.timer}\033[0m"

        if self.depth == 42:
            status = "\033[5;35m❓ Очень Странный Уровень...\033[0m"
        else:
            status = "\033[5;31mВРАТА ОТКРЫТЫ ☢️\033[0m" if self.monsters_activated else "Тихо..."

        print(
            f"--- \033[36mГлубина: {self.depth}\033[0m | "
            f"{hp_info}{time_info} | "
            f"\033[32mСлизь: {self.slime_count}\033[0m | "
            f"\033[35m{status}\033[0m ---")

        view_distance = 6

        for y in range(self.height):
            row = ""
            for x in range(self.width):
                dist = ((x - self.px) ** 2 + (y - self.py) ** 2) ** 0.5

                if not self.bonus_view and dist > view_distance:
                    row += " "
                    continue

                tile = self.map[y][x]
                if x == self.px and y == self.py:
                    row += "\033[35m@\033[0m"
                elif [x, y] in self.enemies:
                    row += "\033[31mX\033[0m"
                elif [x, y] in self.slimes:
                    row += "\033[32mo\033[0m"
                elif [x, y] in self.traps:
                    row += "\033[33m^\033[0m"
                elif self.map[y][x] == "A":
                    row += "\033[33mA\033[0m"
                elif tile in ["E", "F"]:
                    row += f"\033[34m{tile}\033[0m"
                elif tile == "#":
                    row += f"\033[90m#\033[0m"
                else:
                    row += self.map[y][x]
            print(row + "\033[K")

        if self.message:
            print(f"\n\033[90mЛОГ:\033[0m {self.message}\033[K")
            self.message = ""
        else:
            print("\n\033[K")

        print("\n\033[90mWASD - ход | B - сыр (3 слизи) | C - чит | Q - выход\033[J\033[0m")

    def run(self):
        while True:
            self.draw()
            try:
                cmd = msvcrt.getch().decode('utf-8').lower()

                if cmd in 'wasd':
                    d = {'w': (0, -1), 's': (0, 1), 'a': (-1, 0), 'd': (1, 0)}
                    self.move(*d[cmd])
                elif cmd == 'b':
                    if self.slime_count >= 3:
                        self.slime_count -= 3
                        self.health = min(self.max_health, self.health + 2)
                        self.message = "\033[33m🧀 Сыр восстановил +2 HP.\033[0m"
                elif cmd == 'c':
                    print("\033[?25h")
                    code = input("Код: ").lower()
                    if self.depth == 42 and code == "bee42" and self.bonus_42 == False:
                        self.health += 42
                        self.max_health += 42
                        self.bonus_42 = True
                        self.message = "⚡ Код принят! \033[35m+42 HP\033[0m"
                    elif code == "slimepack" and self.bonus_slime == False:
                        self.bonus_slime = True
                        self.slime_count += 15
                        self.message = "⚡ Код принят!\033[32m +15 Слизи!\033[0m"
                    elif code == "starterpack" and self.bonus_st == False:
                        self.bonus_st = True
                        self.max_health += 5
                        self.health = self.max_health
                        self.slime_count += 10
                        self.message = "⚡ Код принят! \033[35m+Full HP, +5 HP лимит и +10 Слизи!\033[0m"
                    elif code == "deep" and self.bonus_deep == False:
                        self.bonus_deep = True
                        self.monsters_activated = True
                        self.depth += 5
                        self.generate_level()
                        self.message = "⚡ Код принят! \033[35mПогружение вниз на 5 уровней!\033[0m"
                    elif code == "view" and self.bonus_view == False:
                        self.bonus_view = not self.bonus_view
                        self.message = "\033[35mНа 1 ход пещера освещена!\033[0m"
                    elif code == "list":
                        self.message = "\033[33mСписок читов: bee42, slimepack, starterpack, deep, view\033[0m"
                    else:
                        self.message = "\033[5;31mНеверный код...\033[0m \033[33mВведите list для списка читов\033[0m"
                    print("\033[2J", end="")
                elif cmd == 'q':
                    print("\033[?25h")
                    break
            except Exception:
                continue


if __name__ == "__main__":
    logo = "( /\ \/ [-   [- >< |^ |_ () /? [- /?"

    print("\033[2J\033[H", end="")
    print("\033[36m===============================")
    print(logo)
    print("      CAVE EXPLORER v2.0")
    print("===============================\033[0m")
    msvcrt.getch()
    game = SimpleCave()
    game.run()
