-- ⚡ Volt v2.0 - Match/Switch, Try/Catch, Error Handling

-- Match statement
func describe(value) {
    match value {
        case 1 {
            show "One"
        }
        case 2 {
            show "Two"
        }
        case 3 {
            show "Three"
        }
        default {
            show f"Something else: {value}"
        }
    }
}

show "=== Match Statement ==="
describe(1)
describe(2)
describe(3)
describe(42)

-- Match with strings
func getDayType(day) {
    match day {
        case "Saturday" { return "Weekend" }
        case "Sunday" { return "Weekend" }
        default { return "Weekday" }
    }
}

show ""
show "Monday is a " + getDayType("Monday")
show "Saturday is a " + getDayType("Saturday")

-- Try / Catch
show ""
show "=== Error Handling ==="

try {
    set x = 10 / 0
} catch err {
    show f"Caught error: {err}"
}

-- Throw custom errors
func divide(a, b) {
    if b == 0 {
        throw "Cannot divide by zero!"
    }
    return a / b
}

try {
    set result = divide(10, 0)
} catch err {
    show f"Caught: {err}"
}

show f"Safe division: {divide(10, 3)}"

-- Try/Catch/Finally
show ""
func riskyOperation() {
    throw "Something went wrong"
}

try {
    riskyOperation()
} catch err {
    show f"Error caught: {err}"
} finally {
    show "Cleanup: finally block always runs"
}

-- Nested try/catch
show ""
try {
    try {
        throw "inner error"
    } catch e {
        show f"Inner catch: {e}"
        throw "re-thrown"
    }
} catch e {
    show f"Outer catch: {e}"
}
