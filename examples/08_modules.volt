-- ⚡ Volt v2.0 - Modules (math, random, time, file)

use "math"
use "random"
use "time"

show "=== Math Module ==="
show f"pi = {math.pi}"
show f"e = {math.e}"
show f"sqrt(16) = {math.sqrt(16)}"
show f"pow(2, 10) = {math.pow(2, 10)}"
show f"floor(3.7) = {math.floor(3.7)}"
show f"ceil(3.2) = {math.ceil(3.2)}"
show f"abs(-42) = {math.abs(-42)}"
show f"sin(0) = {math.sin(0)}"
show f"log(100, 10) = {math.log(100, 10)}"
show f"gcd(12, 8) = {math.gcd(12, 8)}"

show ""
show "=== Random Module ==="
show f"Random int (1-10): {random.int(1, 10)}"
show f"Random float: {random.float()}"
show f"Random bool: {random.bool()}"

set colors = ["red", "blue", "green", "yellow"]
show f"Random choice: {random.choice(colors)}"
show f"Shuffled: {random.shuffle(colors)}"

show ""
show "=== Time Module ==="
show f"Date: {time.date()}"
show f"Year: {time.year()}"
show f"Month: {time.month()}"
show f"Timestamp: {time.now()}"

-- Measure execution time
set start = time.elapsed()
set sum = 0
for i in 1 to 100000 {
    set sum = sum + i
}
set elapsed = time.elapsed(start)
show f"Sum 1..100000 = {sum}"
show f"Time: {elapsed} seconds"

show ""
show "=== File Module ==="
use "file"

-- Write and read a file
file.write("test_output.txt", "Hello from Volt!\nLine 2\nLine 3")
set content = file.read("test_output.txt")
show f"File contents: {content}"

set lines = file.readlines("test_output.txt")
show f"Lines: {lines}"
show f"File exists? {file.exists('test_output.txt')}"
show f"File size: {file.size('test_output.txt')} bytes"

-- Clean up
file.delete("test_output.txt")
show f"Deleted. Exists? {file.exists('test_output.txt')}"
