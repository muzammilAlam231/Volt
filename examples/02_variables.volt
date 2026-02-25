-- ⚡ Volt v2.0 - Variables, Arithmetic, String Interpolation

set name = "Volt"
set version = 2.0

-- String interpolation with f-strings (like Python)
show f"Welcome to {name} v{version}!"

-- Arithmetic
set a = 10
set b = 3
show f"a = {a}, b = {b}"
show f"a + b = {a + b}"
show f"a * b = {a * b}"
show f"a / b = {a / b}"
show f"a % b = {a % b}"

-- Destructuring
set [x, y, z] = [100, 200, 300]
show f"Destructured: x={x}, y={y}, z={z}"

-- Dict destructuring
set user = {name: "Alice", age: 25, city: "NYC"}
set {name, age} = user
show f"Name: {name}, Age: {age}"
