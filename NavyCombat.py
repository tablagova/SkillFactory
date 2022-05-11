from random import randint, choice


class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return "Вы пытаетесь выстрелить за доску!"


class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку"


class BoardWrongShipException(BoardException):
    pass


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f'Dot({self.x}, {self.y})'


class Ship:
    def __init__(self, length, bow, direction):
        self.length = length
        self.bow = bow
        self.direction = direction
        self.lives = length

    @property
    def dots(self):
        ship_dots = [self.bow]
        if self.length > 1:
            if self.direction == 'v':
                for i in range(1, self.length):
                    ship_dots.append(Dot(self.bow.x + i, self.bow.y))
            if self.direction == 'h':
                for i in range(1, self.length):
                    ship_dots.append(Dot(self.bow.x, self.bow.y + i))
        return ship_dots

    def hit(self, target):
        return target in self.dots


class Board:
    def __init__(self, hid=False, size=6):
        self.field = [['O'] * size for _ in range(size)]
        self.ships = []
        self.busy = []
        self.hid = hid
        self.count = 0
        self.size = size

    def add_ship(self, ship):
        for dot in ship.dots:
            if dot in self.busy or self.out(dot):
                raise BoardWrongShipException
        for dot in ship.dots:
            self.field[dot.x][dot.y] = '■'
            self.busy.append(dot)
        self.ships.append(ship)
        self.contour(ship)

    def contour(self, ship, verb=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1),
        ]
        for dot in ship.dots:
            for dx, dy in near:
                candidate = Dot(dot.x + dx, dot.y + dy)
                if candidate not in self.busy and not (self.out(candidate)):
                    if verb:
                        self.field[candidate.x][candidate.y] = '.'
                    self.busy.append(candidate)

    def show_board(self):
        res = ' ' * 3
        for i in range(self.size):
            res += "\033[32m{} \033[0m".format(i + 1)
        for j, row in enumerate(self.field):
            res += '\n' + "\033[32m{:2} \033[0m".format(j + 1) + ' '.join(row)
        if self.hid is True:
            res = res.replace('■', 'O')
        return res

    def __str__(self):
        return self.show_board()

    def out(self, dot):
        return not ((0 <= dot.x < self.size) and (0 <= dot.y < self.size))

    def shot(self, target):
        if self.out(target):
            raise BoardOutException
        elif target in self.busy:
            raise BoardUsedException
        else:
            self.busy.append(target)
            for ship in self.ships:
                if ship.hit(target):
                    ship.lives -= 1
                    self.field[target.x][target.y] = 'X'
                    if ship.lives == 0:
                        self.count += 1
                        self.contour(ship, verb=True)
                        print('Корабль уничтожен!')
                        return False
                    else:
                        print('Корабль ранен!')
                        return True
            self.field[target.x][target.y] = '.'
            print("Мимо!")
            return False

    def begin(self):
        self.busy = []


class Player:
    def __init__(self, player_board, enemy_board):
        self.board = player_board
        self.enemy_board = enemy_board

    def ask(self):
        raise NotImplementedError

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy_board.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):
    def ask(self):
        target = Dot(randint(0, SIZE - 1), randint(0, SIZE - 1))
        print(f'Ход компьютера: {target.x + 1} {target.y + 1}')
        return target


class User(Player):
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()
            if len(cords) != 2:
                print(" Введите 2 координаты! ")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print(" Введите числа! ")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)


class Game:
    def __init__(self, size=6):
        self.size = size
        pl_board = self.user_board()
        comp_board = self.random_board()
        pl_board.hid = False
        comp_board.hid = True

        self.ai = AI(comp_board, pl_board)
        self.us = User(pl_board, comp_board)

    @property
    def fleet(self):
        if 5 < self.size < 10:
            fleet = [3, 2, 2, 1, 1, 1, 1]
        elif self.size == 10:
            fleet = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]
        else:
            raise BoardException
        return fleet

    def try_board(self):
        board = Board(size=self.size)
        attempts = 0
        for i in self.fleet:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(i, Dot(randint(0, self.size), randint(0, self.size)), choice(['v', 'h']))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def random_board(self):
        board = None
        while board is None:
            board = self.try_board()
        return board

    def try_user_board(self):
        self_construct = input("Вы хотите разместить корабои самостоятельно? (введите YES или NO): ")[0].upper()
        while self_construct not in ['Y', 'N']:
            self_construct = input("Введите YES или NO: ")[0].upper()
        if self_construct == 'Y':
            board = Board(size=self.size)
            self.self_construct_info()
            for i in self.fleet:
                print(board)
                if len(board.busy) == SIZE ** 2:
                    print("Не осталось места для размещения корабля, начните расстановку заново.")
                    return None
                print("Размещаем корабль длины", i)
                while True:
                    if i > 1:
                        x, y, d = self.put_long_ship()
                    else:
                        x, y, d = self.put_short_ship()
                    ship = Ship(i, Dot(x - 1, y - 1), d)
                    try:
                        board.add_ship(ship)
                        break
                    except BoardWrongShipException:
                        print("Так разместить корабль нельзя.")
            board.begin()
            return board
        else:
            return self.random_board()

    def put_long_ship(self):
        while True:
            cords = input("Укажите координаты носа и направление корабля(): ").split()
            if len(cords) != 3:
                print(" Введите 2 координаты и направление! ")
                continue
            x, y, d = cords
            if not (x.isdigit()) or not (y.isdigit()) or not (d in ['h', 'v']):
                print(" Введите 2 числа и букву 'v' или 'h'! ")
                continue
            x, y = int(x), int(y)
            break
        return x, y, d

    def put_short_ship(self):
        while True:
            cords = input("Укажите координаты корабля(): ").split()
            if len(cords) != 2:
                print(" Введите 2 координаты! ")
                continue
            x, y = cords
            if not (x.isdigit()) or not (y.isdigit()):
                print(" Введите 2 числа! ")
                continue
            d = choice(['h', 'v'])
            x, y = int(x), int(y)
            break
        return x, y, d

    def user_board(self):
        board = None
        while board is None:
            board = self.try_user_board()
        return board

    def self_construct_info(self):
        print("Укажите коордитнаты носа корабля и его направление (по вертикали или по горизонтали)")
        print(" формат ввода: x y dir")
        print(" x - номер строки  ")
        print(" y - номер столбца ")
        print(" dir - направление: v или h")
        print(" v - для размещения по вертикали, h - по горизонлали")
        print(" Пример: 1 2 v   или  1 4 h")
        print(" Для корабля длиной 1 направление указывать не нужно, только две координаты. Например: 3 4")

    def greet(self):
        print("-" * 20)
        print(" Начинаем сражение")
        print("-" * 20)
        print(" для выстрела вводите: x y ")
        print(" x - номер строки  ")
        print(" y - номер столбца ")

    def loop(self):
        num = 0
        while True:
            print("-" * 20)
            print("Доска пользователя:")
            print(self.us.board)
            print("-" * 20)
            print("Доска компьютера:")
            print(self.ai.board)
            if num % 2 == 0:
                print("-" * 20)
                print("Ходит пользователь!")
                repeat = self.us.move()
            else:
                print("-" * 20)
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.count == len(self.ai.board.ships):
                print("-" * 20)
                print("Доска пользователя:")
                print(self.us.board)
                print("-" * 20)
                print("Доска компьютера:")
                print(self.ai.board)
                print("-" * 20)
                print("\033[31m Пользователь выиграл! \033[0m ")
                break

            if self.us.board.count == len(self.us.board.ships):
                print("-" * 20)
                print("Доска пользователя:")
                print(self.us.board)
                print("-" * 20)
                print("Доска компьютера:")
                print(self.ai.board)
                print("-" * 20)
                print("\033[31m Компьютер выиграл! \033[0m")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()


class Start:
    def __init__(self):
        self.size = self.def_size()

    def def_size(self):
        print("-------------------------------------------")
        print("Выберите размер поля для игры в морской бой")
        print("Возможные варианты: 6x6, 7x7, 8x8, 9x9, 10x10")
        while True:
            try:
                size = int(input("Введите число от 6 до 10: "))
            except ValueError:
                continue
            else:
                if 5 < size < 11:
                    break
        print("-------------------------------------------")
        return size


SIZE = Start().size
game = Game(SIZE)
game.start()
