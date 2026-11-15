"""Pure-Python logic for the three mini-games (no Kivy imports)."""
import math
import random


# --------------------------------------------------------------------------
# 1. Stack Stacker - teaches LIFO
# --------------------------------------------------------------------------
class StackPuzzle:
    """Push 1..n in order and pop to produce the target output sequence."""

    def __init__(self, n=4, rng=None):
        self.rng = rng or random.Random()
        self.n = n
        self.target = self._make_target()
        self.reset(count_reset=False)

    def _make_target(self):
        for _ in range(50):
            inp, st, out = list(range(1, self.n + 1)), [], []
            while len(out) < self.n:
                if inp and (not st or self.rng.random() < 0.55):
                    st.append(inp.pop(0))
                else:
                    out.append(st.pop())
            if out != sorted(out):          # avoid the boring identity case
                return out
        return out

    def reset(self, count_reset=True):
        self.inp = list(range(1, self.n + 1))
        self.stack = []
        self.out = []
        self.moves = 0
        if count_reset:
            self.resets += 1
        else:
            self.resets = 0
            self.mistakes = 0

    @property
    def solved(self):
        return self.out == self.target

    def push(self):
        if not self.inp or self.solved:
            return False
        self.stack.append(self.inp.pop(0))
        self.moves += 1
        return True

    def pop(self):
        """Returns 'ok', 'wrong' (rejected) or 'empty'."""
        if not self.stack:
            return 'empty'
        if self.stack[-1] != self.target[len(self.out)]:
            self.mistakes += 1
            return 'wrong'
        self.out.append(self.stack.pop())
        self.moves += 1
        return 'ok'

    def next_move(self):
        """Greedy solver: 'push', 'pop' or None when stuck/finished."""
        inp, st, out = list(self.inp), list(self.stack), list(self.out)
        if len(out) == len(self.target):
            return None
        want = self.target[len(out)]
        if st and st[-1] == want:
            return 'pop'
        if want in inp:
            return 'push'
        return None

    @property
    def dead(self):
        """True when no sequence of moves can finish the puzzle any more."""
        inp, st, out = list(self.inp), list(self.stack), list(self.out)
        for want in self.target[len(out):]:
            if st and st[-1] == want:
                st.pop()
            elif want in inp:
                while inp[0] != want:
                    st.append(inp.pop(0))
                inp.pop(0)
            else:
                return True
        return False

    @property
    def stars(self):
        if not self.solved:
            return 0
        slips = self.mistakes + self.resets
        return 3 if slips == 0 else 2 if slips <= 2 else 1


# --------------------------------------------------------------------------
# 2. Binary Hunt - teaches binary search
# --------------------------------------------------------------------------
class BinaryHunt:
    def __init__(self, size=15, extra=2, rng=None):
        self.rng = rng or random.Random()
        self.size = size
        self.values = sorted(self.rng.sample(range(1, 100), size))
        self.idx = self.rng.randrange(size)
        self.target = self.values[self.idx]
        self.optimal = math.ceil(math.log2(size + 1))
        self.max_guesses = self.optimal + extra
        self.guesses = []
        self.lo, self.hi = 0, size - 1
        self.won = False

    @property
    def left(self):
        return self.max_guesses - len(self.guesses)

    @property
    def over(self):
        return self.won or self.left <= 0

    def guess(self, i):
        """Returns 'found', 'low' (target is to the RIGHT), 'high' (LEFT), 'repeat' or 'over'."""
        if self.over:
            return 'over'
        if i in self.guesses:
            return 'repeat'
        self.guesses.append(i)
        v = self.values[i]
        if v == self.target:
            self.won = True
            return 'found'
        if v < self.target:
            self.lo = max(self.lo, i + 1)
            return 'low'
        self.hi = min(self.hi, i - 1)
        return 'high'

    def in_range(self, i):
        return self.lo <= i <= self.hi

    @property
    def stars(self):
        if not self.won:
            return 0
        used = len(self.guesses)
        return 3 if used <= self.optimal else 2 if used <= self.optimal + 1 else 1

    def best_guess(self):
        """Index a perfect binary search would try next."""
        return (self.lo + self.hi) // 2


# --------------------------------------------------------------------------
# 3. Bug Hunter - spot the broken line
# --------------------------------------------------------------------------
BUG_SNIPPETS = [
    {'lang': 'py', 'goal': 'Add up every number in the list.',
     'lines': ['def total(nums):', '    s = 0', '    for n in nums:', '        s = n', '    return s'],
     'bug': 3, 'why': "s = n overwrites the running total every time. Use s += n to accumulate."},
    {'lang': 'py', 'goal': 'Print the numbers 0 to 4.',
     'lines': ['for i in range(5)', '    print(i)'],
     'bug': 0, 'why': "A for statement must end with a colon ( : )."},
    {'lang': 'py', 'goal': 'Return True when n is even.',
     'lines': ['def is_even(n):', '    return n % 2 = 0'],
     'bug': 1, 'why': "A single = assigns. Use == to compare."},
    {'lang': 'py', 'goal': 'Print every item in the list.',
     'lines': ['items = ["a", "b", "c"]', 'for i in range(1, len(items)):', '    print(items[i])'],
     'bug': 1, 'why': "range(1, ...) starts at index 1 and skips the first item. Start at 0."},
    {'lang': 'py', 'goal': 'Print 0, 1, 2 and then stop.',
     'lines': ['count = 0', 'while count < 3:', '    print(count)', '    count -= 1'],
     'bug': 3, 'why': "count goes DOWN, so the loop never ends. Use count += 1."},
    {'lang': 'py', 'goal': 'Take the most recently pushed item off the stack.',
     'lines': ['stack = []', 'stack.append(1)', 'stack.append(2)', 'top = stack.pop(0)'],
     'bug': 3, 'why': "pop(0) removes the FIRST item (queue behavior). A stack pops from the end: pop()."},
    {'lang': 'py', 'goal': 'Get the last character of the word.',
     'lines': ['word = "code"', 'last = word[len(word)]', 'print(last)'],
     'bug': 1, 'why': "Valid indexes are 0 .. len-1, so word[len(word)] is out of range. Use word[-1]."},
    {'lang': 'c', 'goal': 'Print all 5 numbers.',
     'lines': ['int a[5] = {1, 2, 3, 4, 5};', 'for (int i = 0; i <= 5; i++) {', '    printf("%d ", a[i]);', '}'],
     'bug': 1, 'why': "i <= 5 reads a[5], one past the end. Use i < 5."},
    {'lang': 'c', 'goal': 'Print the text stored in name.',
     'lines': ['char name[3] = "Bob";', 'printf("%s", name);'],
     'bug': 0, 'why': "A string needs one extra byte for the '\\0' terminator, so the array must be at least 4 chars."},
    {'lang': 'c', 'goal': 'Read an integer typed by the user and print it.',
     'lines': ['int n;', 'printf("Enter a number: ");', 'scanf("%d", n);', 'printf("%d", n);'],
     'bug': 2, 'why': "scanf needs the ADDRESS of the variable: scanf(\"%d\", &n)."},
    {'lang': 'c', 'goal': "Print 'five' only when x equals 5.",
     'lines': ['int x = 10;', 'if (x = 5) {', '    printf("five");', '}'],
     'bug': 1, 'why': "x = 5 ASSIGNS 5 (and is always true). Compare with x == 5."},
    {'lang': 'c', 'goal': 'Print the value of n through the pointer p.',
     'lines': ['int n = 42;', 'int *p = &n;', 'printf("%d", p);'],
     'bug': 2, 'why': "p is the address. Dereference it with *p to get the value."},
    {'lang': 'c', 'goal': 'Compute the average of a and b as a decimal.',
     'lines': ['int a = 3, b = 4;', 'float avg = (a + b) / 2;', 'printf("%.1f", avg);'],
     'bug': 1, 'why': "(a + b) / 2 is INTEGER division (7 / 2 = 3). Divide by 2.0 instead."},
]


class BugHunt:
    def __init__(self, diff=1, rounds=5, rng=None):
        self.rng = rng or random.Random()
        self.max_lives = {1: 4, 2: 3, 3: 2}[diff]
        self.lives = self.max_lives
        self.items = self.rng.sample(BUG_SNIPPETS, rounds)
        self.index = 0
        self.found = 0
        self.mistakes = 0
        self.answered = False

    @property
    def current(self):
        return self.items[self.index]

    @property
    def total(self):
        return len(self.items)

    def tap(self, line):
        if self.answered:
            return None
        self.answered = True
        ok = line == self.current['bug']
        if ok:
            self.found += 1
        else:
            self.mistakes += 1
            self.lives -= 1
        return ok

    def advance(self):
        self.index += 1
        self.answered = False

    @property
    def over(self):
        return self.lives <= 0 or (self.answered and self.index >= self.total - 1)

    @property
    def won(self):
        return self.lives > 0 and self.answered and self.index >= self.total - 1

    @property
    def stars(self):
        if not self.won:
            return 0
        return 3 if self.mistakes == 0 else 2 if self.mistakes == 1 else 1
