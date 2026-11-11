def log_action(func):
    def wrapper(self, *args, **kwargs):
        print(f"{self.name} → {func.__name__}")
        return func(self, *args, **kwargs)
    return wrapper


class Character:
    count = 0

    def __init__(self, name, hp=100, level=1):
        self.name = name
        self.hp = hp
        self.level = level
        # Character.count და არა self.count, რადგან self.count += 1
        # ობიექტზე ახალ ატრიბუტს შექმნიდა და საერთო მთვლელი არ გაიზრდებოდა
        Character.count += 1

    def __str__(self):
        return f"{self.name} (Lv {self.level}, HP {self.hp})"

    def __eq__(self, other):
        return self.name == other.name and self.level == other.level

    def take_damage(self, amount):
        self.hp = max(self.hp - amount, 0)

    @property
    def is_alive(self):
        return self.hp > 0

    @log_action
    def attack(self, target):
        target.take_damage(5)

    @classmethod
    def from_string(cls, text):
        name, hp = text.split(";")
        return cls(name, hp=int(hp))

    @staticmethod
    def is_valid_name(name):
        return 2 <= len(name) <= 20


class Warrior(Character):
    def __init__(self, name, hp=100, level=1, strength=10):
        super().__init__(name, hp, level)
        self.strength = strength

    @log_action
    def attack(self, target):
        target.take_damage(self.strength)


class Mage(Character):
    def __init__(self, name, hp=100, level=1, mana=50):
        super().__init__(name, hp, level)
        self.mana = mana

    def __str__(self):
        return super().__str__() + f" MP {self.mana}"

    @log_action
    def attack(self, target):
        if self.mana >= 10:
            self.mana -= 10
            target.take_damage(20)
        else:
            super().attack(target)


class HealerMixin:
    @log_action
    def heal(self, target, amount):
        target.hp += amount


# Priest.__mro__ -> Priest, HealerMixin, Mage, Character, object
# Python მეთოდს ამ რიგით ეძებს და იყენებს პირველს, რასაც იპოვის.
# heal-ს პოულობს HealerMixin-ში, attack-ს Mage-ში, take_damage-ს Character-ში.
class Priest(HealerMixin, Mage):
    pass


class Inventory:
    def __init__(self):
        self.items = []

    def add(self, **item):
        self.items.append(item)

    def find(self, **filters):
        return [item for item in self.items
                if all(item.get(key) == value for key, value in filters.items())]

    def __len__(self):
        return len(self.items)


def battle(a, b):
    attacker, defender = a, b
    while a.is_alive and b.is_alive:
        attacker.attack(defender)
        print(a, "|", b)
        attacker, defender = defender, attacker
    return a if a.is_alive else b


if __name__ == "__main__":
    # სავარჯიშო 1
    a = Character("Tariel")
    b = Character("Avtandil", hp=50)
    b.take_damage(70)

    print(a)                 # Tariel (Lv 1, HP 100)
    print(b)                 # Avtandil (Lv 1, HP 0)
    print(b.is_alive)        # False
    print(Character.count)   # 2

    # სავარჯიშო 2
    t = Warrior("Tariel", hp=120, strength=15)
    n = Mage("Nestan", hp=80, mana=15)

    t.attack(n)
    print(n)    # Nestan (Lv 1, HP 65) MP 15

    n.attack(t)   # 20 ზიანი, mana-ს 5 რჩება
    n.attack(t)   # mana არ ჰყოფნის: 5 ზიანი
    print(t)    # Tariel (Lv 1, HP 95)

    # სავარჯიშო 3
    print(Priest.__mro__)

    p = Priest("Nestan", hp=60)
    w = Warrior.from_string("Tariel;120")

    p.heal(w, 30)
    print(w)                                   # Tariel (Lv 1, HP 150)
    print(type(w).__name__)                    # Warrior
    print(Character.is_valid_name("T"))        # False
    print(Character("A") == Character("A"))    # True

    # სავარჯიშო 4
    inv = Inventory()
    inv.add(name="sword", kind="weapon", power=10)
    inv.add(name="potion", kind="heal", power=30)

    print(len(inv))                  # 2
    print(inv.find(kind="weapon"))   # [{'name': 'sword', 'kind': 'weapon', 'power': 10}]
    print(inv.find(kind="heal", power=30))   # [{'name': 'potion', 'kind': 'heal', 'power': 30}]

    t = Warrior("Tariel")
    n = Mage("Nestan")
    t.attack(n)                      # Tariel → attack

    # ბონუსი
    winner = battle(Warrior("Tariel", hp=120), Mage("Nestan", hp=80))
    print(f"გამარჯვებული: {winner.name}")

    # საბოლოო მიზანი
    Character.count = 0   # ზემოთ უკვე შეიქმნა პერსონაჟები, ამიტომ თავიდან ვითვლით
    tariel = Warrior("Tariel", hp=120, strength=15)
    nestan = Mage("Nestan", hp=80, mana=50)

    tariel.attack(nestan)
    print(nestan)            # Nestan (Lv 1, HP 65) MP 50
    print(nestan.is_alive)   # True
    print(Character.count)   # 2
