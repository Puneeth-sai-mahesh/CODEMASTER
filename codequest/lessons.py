"""Short, friendly lessons shown in the Learn section."""

LESSONS = {
    'ds': [
        {
            'title': 'Arrays & Big-O',
            'body': (
                "An array keeps its items side by side in memory, so jumping to any index is instant: O(1).\n\n"
                "Searching an unsorted array means checking items one by one: O(n).\n\n"
                "Big-O describes how the work grows when the data grows. O(1) stays flat, "
                "O(log n) grows slowly, O(n) grows in step with the data, O(n^2) explodes."),
            'code': "nums = [4, 8, 15, 16]\nprint(nums[2])      # O(1)  -> 15\nprint(15 in nums)   # O(n) scan",
        },
        {
            'title': 'Stack (LIFO)',
            'body': (
                "Last In, First Out - like a pile of plates.\n\n"
                "push adds on top, pop removes the top, peek looks without removing.\n\n"
                "Stacks power undo/redo, the browser Back button, expression evaluation and every function call you make."),
            'code': "stack = []\nstack.append(1)     # push\nstack.append(2)     # push\nprint(stack.pop())  # 2 (LIFO)",
        },
        {
            'title': 'Queue (FIFO)',
            'body': (
                "First In, First Out - like a ticket line.\n\n"
                "enqueue adds at the back, dequeue removes from the front.\n\n"
                "Queues drive print jobs, task schedulers and Breadth-First Search. "
                "In Python use collections.deque - popping from the front of a plain list is slow."),
            'code': "from collections import deque\n\nq = deque()\nq.append('A')       # enqueue\nq.append('B')\nprint(q.popleft())  # A (FIFO)",
        },
        {
            'title': 'Linked List',
            'body': (
                "A chain of nodes. Each node stores a value and a pointer to the next node.\n\n"
                "Insert at the head: O(1). Reach the k-th item: O(k), because you must walk the chain.\n\n"
                "Unlike arrays, nodes can live anywhere in memory and the list can grow one node at a time."),
            'code': "class Node:\n    def __init__(self, v, nxt=None):\n        self.val = v\n        self.next = nxt\n\nhead = Node(1, Node(2, Node(3)))\nprint(head.next.val)   # 2",
        },
        {
            'title': 'Trees & BST',
            'body': (
                "A tree is a root node with children, which have children, and so on. Nodes without children are leaves.\n\n"
                "In a Binary Search Tree: left < node < right. Search, insert and delete take O(log n) when the tree is balanced.\n\n"
                "An in-order walk (left, node, right) prints the keys in sorted order."),
            'code': "def inorder(node):\n    if node:\n        inorder(node.left)\n        print(node.key)\n        inorder(node.right)",
        },
        {
            'title': 'Hash Tables',
            'body': (
                "A hash function turns a key into an array index, so you can jump straight to the value: O(1) on average.\n\n"
                "When two keys land on the same slot that is a collision. Chaining (a small list per slot) is the common fix.\n\n"
                "Python's dict and set are hash tables."),
            'code': "ages = {'asha': 21, 'ravi': 25}\nprint(ages['ravi'])  # 25, O(1)\nages['mina'] = 19    # insert, O(1)",
        },
    ],
    'py': [
        {
            'title': 'Variables & Types',
            'body': (
                "Python figures out the type for you. A name just points at a value.\n\n"
                "Core types: int (whole numbers), float (decimals), str (text), bool (True / False).\n\n"
                "Use type(x) to check, and int(), float(), str() to convert."),
            'code': "age = 20          # int\npi = 3.14         # float\nname = 'Code'     # str\nok = True         # bool\nprint(type(age))  # <class 'int'>",
        },
        {
            'title': 'Lists & Dicts',
            'body': (
                "A list is an ordered, changeable collection: [1, 2, 3].\n\n"
                "A dict maps keys to values: {'a': 1}. Lookup by key is fast.\n\n"
                "Slicing: nums[1:3] takes indexes 1 and 2 - the end is excluded."),
            'code': "nums = [10, 20, 30]\nnums.append(40)\nprint(nums[1:3])      # [20, 30]\n\nscore = {'ana': 90}\nscore['raj'] = 85\nprint(len(score))     # 2",
        },
        {
            'title': 'Functions',
            'body': (
                "def creates a function. return sends a value back.\n\n"
                "Parameters can have defaults. Never use a mutable default like [] - it is shared between calls!\n\n"
                "Small functions that do one thing are easier to test and reuse."),
            'code': "def greet(name, punct='!'):\n    return 'Hello, ' + name + punct\n\nprint(greet('Sai'))  # Hello, Sai!",
        },
        {
            'title': 'Loops & Comprehensions',
            'body': (
                "for walks over a sequence, while repeats until a condition fails.\n\n"
                "range(n) gives 0 .. n-1.\n\n"
                "A list comprehension builds a list in one readable line."),
            'code': "for i in range(3):\n    print(i)   # 0 1 2\n\nsquares = [n * n for n in range(5)]\nprint(squares)  # [0, 1, 4, 9, 16]",
        },
    ],
    'c': [
        {
            'title': 'Hello, C',
            'body': (
                "C is compiled: you write source code, a compiler turns it into a program, then you run it.\n\n"
                "Every program starts at main(). Statements end with a semicolon.\n\n"
                "Build it: gcc hello.c -o hello   then run: ./hello"),
            'code': "#include <stdio.h>\n\nint main(void) {\n    printf(\"Hello, C!\\n\");\n    return 0;\n}",
        },
        {
            'title': 'Pointers',
            'body': (
                "A pointer stores the ADDRESS of another variable.\n\n"
                "&x gives the address of x. *p follows the pointer to the value.\n\n"
                "Pointers let functions change the caller's variables and are the key to arrays, strings and dynamic memory."),
            'code': "int x = 5;\nint *p = &x;   // p = address of x\n*p = 9;        // write via pointer\nprintf(\"%d\", x); // 9",
        },
        {
            'title': 'Arrays & Strings',
            'body': (
                "An array has a fixed size and its elements sit side by side.\n\n"
                "a[i] is the same as *(a + i). Going past the end is undefined behavior - C will not stop you!\n\n"
                "A string is a char array that ends with the '\\0' terminator, so it needs one extra byte."),
            'code': "int a[3] = {1, 2, 3};\nchar s[] = \"hi\";  // 3 bytes\nprintf(\"%d %c\", a[2], s[0]);",
        },
        {
            'title': 'malloc & free',
            'body': (
                "malloc asks the system for memory at run time (the heap). It returns NULL if it fails.\n\n"
                "You own that memory until you call free(). Forgetting is a leak; using it afterwards is a bug.\n\n"
                "Good habit: check for NULL, free once, then set the pointer to NULL."),
            'code': "int *p = malloc(3 * sizeof(int));\nif (p == NULL) return 1;\np[0] = 7;\nfree(p);\np = NULL;",
        },
    ],
}


def all_lessons():
    """Flat list of (track, index, lesson) tuples."""
    out = []
    for track, items in LESSONS.items():
        for i, lesson in enumerate(items):
            out.append((track, i, lesson))
    return out
