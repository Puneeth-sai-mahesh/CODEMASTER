"""Question bank for Code Quest.

Each entry lists the CORRECT answer first, then three wrong ones.
The engine shuffles them at play time, so the order here never leaks.
Python snippets are executed and C snippets are compiled by tests/test_game.py,
so every "What does this print?" answer is machine-verified.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Question:
    track: str        # 'ds' | 'py' | 'c'
    diff: int         # 1 easy, 2 medium, 3 hard
    text: str
    correct: str
    wrong: tuple
    why: str
    code: str = ''
    lang: str = ''    # 'py' or 'c' when code is present


TRACKS = {
    'ds': {'name': 'Data Structures', 'tag': 'Stacks, queues, trees & hashing'},
    'py': {'name': 'Python', 'tag': 'Readable, powerful, everywhere'},
    'c': {'name': 'C Language', 'tag': 'Pointers, memory & speed'},
}


def Q(track, diff, text, correct, wrong, why, code='', lang=''):
    assert len(wrong) == 3, text
    if code and not lang:
        lang = track if track in ('py', 'c') else ''
    return Question(track, diff, text, correct, tuple(wrong), why, code, lang)


BANK = [
    # ------------------------------------------------------------ DS / EASY
    Q('ds', 1, "Which structure works Last-In, First-Out (LIFO)?",
      "Stack", ("Queue", "Array", "Tree"),
      "A stack removes the most recently added item first - like a pile of plates."),
    Q('ds', 1, "Which structure works First-In, First-Out (FIFO)?",
      "Queue", ("Stack", "Heap", "Set"),
      "A queue serves items in arrival order - like people waiting in a line."),
    Q('ds', 1, "In C and Python, what is the index of the FIRST element of an array or list?",
      "0", ("1", "-1", "It depends on the size"),
      "Indexing starts at 0, so a[0] is the first item."),
    Q('ds', 1, "How fast is reading arr[i] from an array?",
      "O(1) - constant time", ("O(n) - linear time", "O(log n)", "O(n^2)"),
      "Arrays sit in one block of memory, so the address of arr[i] is computed directly: base + i * size."),
    Q('ds', 1, "Which structure is built from nodes where each node points to the next one?",
      "Linked list", ("Array", "Matrix", "Hash table"),
      "Each node stores a value plus a pointer to the next node."),
    Q('ds', 1, "What is the operation that adds an item on top of a stack?",
      "push", ("pop", "peek", "dequeue"),
      "push adds to the top, pop removes the top, peek only looks at it."),
    Q('ds', 1, "A tree node that has no children is called a...",
      "leaf", ("root", "parent", "edge"),
      "Leaves sit at the bottom of the tree; the root is the single node at the top."),
    Q('ds', 1, "Which structure stores key -> value pairs with very fast lookup by key?",
      "Hash table", ("Linked list", "Stack", "Queue"),
      "A hash function turns the key into an array index, so lookup is O(1) on average."),

    # ---------------------------------------------------------- DS / MEDIUM
    Q('ds', 2, "You push 1, 2, 3 onto a stack and then pop once. What comes out?",
      "3", ("1", "2", "Nothing - the stack is empty"),
      "LIFO: the last item pushed (3) is the first one popped."),
    Q('ds', 2, "You enqueue A, B, C into a queue and then dequeue once. What comes out?",
      "A", ("C", "B", "Nothing"),
      "FIFO: A arrived first, so A leaves first."),
    Q('ds', 2, "Worst-case time to search an UNSORTED array of n items for a value?",
      "O(n)", ("O(1)", "O(log n)", "O(n log n)"),
      "You may have to look at every element, so the time grows linearly."),
    Q('ds', 2, "Binary search only works if the array is...",
      "Sorted", ("Full of positive numbers", "Stored in a linked list", "Of even length"),
      "Each step throws away half the data by comparing with the middle - that only makes sense when the data is in order."),
    Q('ds', 2, "An in-order traversal of a Binary Search Tree visits the keys in what order?",
      "Ascending (sorted) order", ("Descending order", "Insertion order", "Random order"),
      "In a BST: left subtree < node < right subtree. In-order (left, node, right) therefore prints sorted output."),
    Q('ds', 2, "Which structure does Breadth-First Search (BFS) use to remember what to visit next?",
      "Queue", ("Stack", "Heap", "Hash table"),
      "BFS explores level by level, and a FIFO queue keeps exactly that order. (DFS uses a stack.)"),
    Q('ds', 2, "Time to insert a new node at the HEAD of a singly linked list?",
      "O(1)", ("O(n)", "O(log n)", "O(n^2)"),
      "Point the new node at the old head and update head - nothing has to be shifted."),
    Q('ds', 2, "Two different keys landing in the same hash-table slot is called a...",
      "Collision", ("Overflow", "Underflow", "Rotation"),
      "Collisions are handled with chaining (a small list per slot) or open addressing (probe for another slot)."),

    # ------------------------------------------------------------ DS / HARD
    Q('ds', 3, "Time complexity of binary search on a sorted array of n items?",
      "O(log n)", ("O(n)", "O(1)", "O(n log n)"),
      "Every step halves the search range, so about log2(n) steps are needed."),
    Q('ds', 3, "Average-case lookup time in a hash table with a good hash function?",
      "O(1)", ("O(log n)", "O(n)", "O(n log n)"),
      "Good hashing spreads keys evenly, so each slot holds only a few items."),
    Q('ds', 3, "Worst-case height of a Binary Search Tree with n nodes?",
      "n - it degenerates into a list", ("log2(n)", "sqrt(n)", "2"),
      "Inserting already-sorted keys makes every node a right child. That is why self-balancing trees (AVL, Red-Black) exist."),
    Q('ds', 3, "Which structure is the standard way to build an efficient priority queue?",
      "Binary heap", ("Stack", "Singly linked list", "Circular queue"),
      "A heap gives O(log n) insert, O(log n) remove-min/max and O(1) peek."),
    Q('ds', 3, "Floyd's 'tortoise and hare' (slow and fast pointers) is used to...",
      "Detect a cycle in a linked list", ("Sort a linked list", "Reverse a linked list", "Balance a binary tree"),
      "The fast pointer moves 2 steps while the slow one moves 1. If there is a loop, they must eventually meet."),
    Q('ds', 3, "A tree has root 1, left child 2 and right child 3. What is its POST-order traversal?",
      "2 3 1", ("1 2 3", "2 1 3", "1 3 2"),
      "Post-order = left, right, then root: 2, 3, 1."),
    Q('ds', 3, "Worst-case total cost of inserting n items one by one into a binary heap?",
      "O(n log n)", ("O(n)", "O(log n)", "O(n^2)"),
      "Each insert may bubble up log n levels. (Building a heap from an existing array with 'heapify' is the famous O(n) trick.)"),
    Q('ds', 3, "How many edges does a tree with n nodes have?",
      "n - 1", ("n", "n + 1", "2n"),
      "Every node except the root owns exactly one edge to its parent, giving n - 1 edges."),

    # ------------------------------------------------------------ PY / EASY
    Q('py', 1, "What does this print?", "14", ("20", "24", "Error"),
      "* binds tighter than +, so 3 * 4 = 12 and then 2 + 12 = 14.",
      code='print(2 + 3 * 4)'),
    Q('py', 1, "What does this print?", "3", ("2", "4", "[1, 2, 3]"),
      "len() counts the items in the list.",
      code='print(len([1, 2, 3]))'),
    Q('py', 1, "Which keyword defines a function in Python?", "def", ("func", "function", "fn"),
      "def name(parameters): starts a function definition."),
    Q('py', 1, "What does this print?", "<class 'float'>", ("<class 'int'>", "<class 'str'>", "<class 'double'>"),
      "3.5 has a decimal point, so it is a float.",
      code='print(type(3.5))'),
    Q('py', 1, "What does this print?", "HiHi", ("Hi2", "Hi Hi", "Error"),
      "Multiplying a string repeats it.",
      code='print("Hi" * 2)'),
    Q('py', 1, "What does this print?", "[1, 2, 3, 4]", ("[1, 2, 3]", "[4]", "[1, 2, 3, [4]]"),
      "append() adds one item to the end of the list, in place.",
      code='x = [1, 2, 3]\nx.append(4)\nprint(x)'),
    Q('py', 1, "Which symbol starts a single-line comment in Python?", "#", ("//", "/*", "--"),
      "Everything after # on that line is ignored by Python."),
    Q('py', 1, "What does this print?", "3", ("3.33", "3.0", "4"),
      "// is floor division - it drops the fractional part.",
      code='print(10 // 3)'),

    # ---------------------------------------------------------- PY / MEDIUM
    Q('py', 2, "What does this print?", "[0, 2, 4]", ("[2, 4, 6]", "[0, 1, 2]", "[0, 2, 4, 6]"),
      "range(3) gives 0, 1, 2 and the comprehension doubles each one.",
      code='print([i * 2 for i in range(3)])'),
    Q('py', 2, "What does this print?", "2", ("1", "0", "KeyError"),
      "The dict starts with one key; assigning d['b'] adds a second.",
      code='d = {"a": 1}\nd["b"] = 2\nprint(len(d))'),
    Q('py', 2, "What does this print?", "yth", ("pyt", "ytho", "tho"),
      "Slicing [1:4] takes indexes 1, 2 and 3 - the end index is excluded.",
      code='print("python"[1:4])'),
    Q('py', 2, "Which of these Python types is IMMUTABLE?", "tuple", ("list", "dict", "set"),
      "A tuple cannot be changed after it is created; lists, dicts and sets can."),
    Q('py', 2, "What does this print?", "False", ("True", "[]", "None"),
      "Empty containers are 'falsy'.",
      code='print(bool([]))'),
    Q('py', 2, "What does this print?", "[3, 2, 1]", ("[1, 2, 3]", "[3, 1, 2]", "None"),
      "sorted() returns a NEW list; reverse=True puts the biggest value first.",
      code='nums = [3, 1, 2]\nprint(sorted(nums, reverse=True))'),
    Q('py', 2, "What does this print?", "['a', 'b', 'c']", ("a b c", "['a,b,c']", "('a', 'b', 'c')"),
      "split(',') cuts the string at every comma and returns a list.",
      code='print("a,b,c".split(","))'),
    Q('py', 2, "What does this print?", "3", ("5", "2", "{1, 2, 3, 1, 2}"),
      "A set keeps only unique values: {1, 2, 3}.",
      code='s = set([1, 1, 2, 2, 3])\nprint(len(s))'),

    # ------------------------------------------------------------ PY / HARD
    Q('py', 3, "What does this print?", "[1, 2]", ("[2]", "[1]", "[[], 2]"),
      "The default list [] is created ONCE, when the function is defined, and shared by every call - a famous Python gotcha.",
      code='def add(x, lst=[]):\n    lst.append(x)\n    return lst\n\nadd(1)\nprint(add(2))'),
    Q('py', 3, "What does this print?", "4", ("3", "1", "Error"),
      "b = a does NOT copy the list - both names point to the same object.",
      code='a = [1, 2, 3]\nb = a\nb.append(4)\nprint(len(a))'),
    Q('py', 3, "What does this print?", "[0, 3, 6, 9]", ("[3, 6, 9]", "[0, 3, 6]", "[1, 4, 7]"),
      "The condition keeps only the multiples of 3 from 0..9.",
      code='print([x for x in range(10)\n       if x % 3 == 0])'),
    Q('py', 3, "What does this print?", "3", ("2", "[1, 2]", "<generator object>"),
      "sum() consumes the generator: 1 + 2 = 3.",
      code='def gen():\n    yield 1\n    yield 2\n\nprint(sum(gen()))'),
    Q('py', 3, "What does this print?", "False", ("True", "0.3", "Error"),
      "Binary floating point cannot store 0.1 exactly, so 0.1 + 0.2 is really 0.30000000000000004.",
      code='print(0.1 + 0.2 == 0.3)'),
    Q('py', 3, "What does this print?", "1", ("99", "[99, 2, 3]", "Error"),
      "x[:] makes a (shallow) COPY, so changing y leaves x alone.",
      code='x = [1, 2, 3]\ny = x[:]\ny[0] = 99\nprint(x[0])'),
    Q('py', 3, "What does this print?", "cba", ("abc", "acb", "bca"),
      "[::-1] walks the string backwards.",
      code='print("abc"[::-1])'),
    Q('py', 3, "What does this print?", "120", ("24", "60", "5"),
      "Recursion: 5 * 4 * 3 * 2 * 1 = 120 (factorial).",
      code='def f(n):\n    if n <= 1:\n        return 1\n    return n * f(n - 1)\n\nprint(f(5))'),

    # ------------------------------------------------------------- C / EASY
    Q('c', 1, "Which header must you include to use printf?", "stdio.h", ("stdlib.h", "string.h", "math.h"),
      "stdio.h declares the standard input/output functions such as printf and scanf."),
    Q('c', 1, "Where does every C program start running?", "main()", ("start()", "run()", "init()"),
      "The operating system calls main() first."),
    Q('c', 1, "What does this print?", "3", ("3.5", "4", "2"),
      "Both operands are int, so C does integer division and drops the .5.",
      code='int x = 7 / 2;\nprintf("%d", x);'),
    Q('c', 1, "Which format specifier prints an int?", "%d", ("%s", "%f", "%c"),
      "%d = int, %f = float/double, %c = char, %s = string."),
    Q('c', 1, "Every C statement must end with a...", "semicolon ;", ("colon :", "period .", "comma ,"),
      "The semicolon marks the end of a statement."),
    Q('c', 1, "What does this print?", "2", ("1", "3", "0"),
      "a[1] is the SECOND element, because indexing starts at 0.",
      code='int a[3] = {1, 2, 3};\nprintf("%d", a[1]);'),
    Q('c', 1, "How many bytes is a char in C (by definition)?", "1", ("2", "4", "8"),
      "sizeof(char) is always 1 in C."),
    Q('c', 1, "Which operator gives the ADDRESS of a variable?", "&", ("*", "#", "@"),
      "&x is the address of x; *p follows a pointer to the value."),

    # --------------------------------------------------------- C / MEDIUM
    Q('c', 2, "What does this print?", "5", ("0", "An address", "Error"),
      "p holds the address of x; *p reads the value stored there.",
      code='int x = 5;\nint *p = &x;\nprintf("%d", *p);'),
    Q('c', 2, "What does this print?", "5", ("6", "4", "Error"),
      "strlen counts the characters before the '\\0' terminator.",
      code='char s[] = "hello";\nprintf("%d", (int)strlen(s));'),
    Q('c', 2, "What does malloc return when it cannot allocate memory?", "NULL",
      ("-1", "An empty block", "It crashes immediately"),
      "Always check the result: if (p == NULL) { handle the error }."),
    Q('c', 2, "What does this print?", "1", ("2", "3", "0"),
      "% is the remainder operator: 7 = 2 * 3 + 1.",
      code='printf("%d", 7 % 3);'),
    Q('c', 2, "What does this print?", "012", ("123", "0 1 2", "3"),
      "i takes the values 0, 1, 2 and each is printed with no separator.",
      code='for (int i = 0; i < 3; i++)\n    printf("%d", i);'),
    Q('c', 2, "Which function releases memory obtained with malloc?", "free", ("delete", "release", "dealloc"),
      "Every malloc needs a matching free, otherwise you leak memory."),
    Q('c', 2, "What does this print?", "4", ("16", "1", "8"),
      "Total bytes divided by bytes per element gives the element count.",
      code='int arr[4];\nint n = sizeof(arr) / sizeof(arr[0]);\nprintf("%d", n);'),
    Q('c', 2, "Which character marks the end of a C string?", "'\\0' (null terminator)",
      ("'\\n'", "'.'", "EOF"),
      "A string with n visible characters occupies n + 1 bytes."),

    # ----------------------------------------------------------- C / HARD
    Q('c', 3, "What does this print?", "20", ("10", "30", "Error"),
      "p++ moves the pointer forward by one int, so it now points at a[1].",
      code='int a[] = {10, 20, 30};\nint *p = a;\np++;\nprintf("%d", *p);'),
    Q('c', 3, "What does this print?", "7", ("5", "2", "An address"),
      "*p = *p + 2 writes through the pointer, so x itself becomes 7.",
      code='int x = 5;\nint *p = &x;\n*p = *p + 2;\nprintf("%d", x);'),
    Q('c', 3, "What does this print?", "8", ("3", "6", "16"),
      "Shifting left by 3 multiplies by 2^3 = 8.",
      code='printf("%d", 1 << 3);'),
    Q('c', 3, "What does this print?", "c", ("b", "a", "\\0"),
      "s + 2 points at the third character and * reads it.",
      code='char s[] = "abc";\nprintf("%c", *(s + 2));'),
    Q('c', 3, "What does this print?", "1", ("7", "8", "0"),
      "5 is 101 and 3 is 011 in binary. AND keeps only the matching 1-bits: 001.",
      code='printf("%d", 5 & 3);'),
    Q('c', 3, "Using memory after you have called free() on it is called a...",
      "Dangling pointer / use-after-free", ("Memory leak", "Buffer underflow", "Stack overflow"),
      "The pointer still holds the old address, but that memory is no longer yours - undefined behavior. Set the pointer to NULL after free."),
    Q('c', 3, "What does this print?", "30", ("10", "16", "14"),
      "1 + 4 + 9 + 16 = 30.",
      code='int i, s = 0;\nfor (i = 1; i <= 4; i++)\n    s += i * i;\nprintf("%d", s);'),
    Q('c', 3, "An int* p holds address 1000 and an int is 4 bytes. What address is p + 2?",
      "1008", ("1002", "1004", "1016"),
      "Pointer arithmetic scales by the element size: 1000 + 2 * 4 = 1008."),
]


def questions_for(track, diff):
    return [q for q in BANK if q.track == track and q.diff == diff]
