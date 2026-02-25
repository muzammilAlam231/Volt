-- ⚡ Volt v2.0 - Functions, Lambdas, Default Params

-- Default parameters
func greet(name = "World", greeting = "Hello") {
    show f"{greeting}, {name}!"
}

greet()
greet("Alice")
greet("Bob", "Hey")

-- Lambda functions
set double = (x) => x * 2
set add = (a, b) => a + b
set identity = (x) => x

show f"double(5) = {double(5)}"
show f"add(3, 7) = {add(3, 7)}"

-- Higher-order function
func apply(fn, value) {
    return fn(value)
}

show f"apply(double, 21) = {apply(double, 21)}"

-- Closures
func makeCounter() {
    set count = 0
    func increment() {
        set count = count + 1
        return count
    }
    return increment
}

set counter = makeCounter()
show f"Counter: {counter()}"
show f"Counter: {counter()}"
show f"Counter: {counter()}"

-- Recursive function
func fibonacci(n) {
    if n <= 1 { return n }
    return fibonacci(n - 1) + fibonacci(n - 2)
}

show ""
show "Fibonacci sequence:"
for i in 0 to 10 {
    show f"  fib({i}) = {fibonacci(i)}"
}

-- Function returning function
func multiplier(factor) {
    return (x) => x * factor
}

set triple = multiplier(3)
set quadruple = multiplier(4)
show ""
show f"triple(5) = {triple(5)}"
show f"quadruple(5) = {quadruple(5)}"
