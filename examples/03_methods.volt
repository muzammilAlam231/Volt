-- ⚡ Volt v2.0 - String & List Methods (Chaining)

show "=== String Methods ==="
set msg = "  Hello, Volt World!  "
show msg.trim()
show msg.trim().upper()
show msg.trim().lower()
show "hello".replace("l", "r")
show "hello world".split(" ")
show "hello".startsWith("he")
show "hello".endsWith("lo")
show "hello".indexOf("ll")
show "hello".slice(1, 4)
show "hello".repeat(3)
show "hello".reverse()
show "hello".contains("ell")
show "hello".length()
show "42".toInt()
show "abc".toList()
show "hello".padStart(10, "-")
show "hello".padEnd(10, "-")

show ""
show "=== List Methods ==="
set nums = [3, 1, 4, 1, 5, 9, 2, 6]
show f"Original: {nums}"
show "Sorted: " + nums.sort()
show "Reversed: " + nums.reverse()
show "First: " + nums.first()
show "Last: " + nums.last()
show "Unique: " + nums.unique()
show "Sum: " + nums.sum()
show "Includes 5? " + nums.includes(5)
show "Index of 4: " + nums.indexOf(4)
show "Slice(2, 5): " + nums.slice(2, 5)

-- Higher-order methods with lambdas
set doubled = nums.map((x) => x * 2)
show f"Doubled: {doubled}"

set evens = nums.filter((x) => x % 2 == 0)
show f"Evens: {evens}"

set total = nums.reduce((acc, x) => acc + x, 0)
show f"Reduce sum: {total}"

set found = nums.find((x) => x > 4)
show f"First > 4: {found}"

show "All > 0? " + nums.every((x) => x > 0)
show "Any > 8? " + nums.some((x) => x > 8)

show ""
show "=== Chaining ==="
set result = [5, 3, 8, 1, 9, 2].sort().reverse().slice(0, 3)
show f"Top 3: {result}"
