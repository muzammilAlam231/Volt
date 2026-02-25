-- ⚡ Volt v2.0 - Quadratic Equation Solver

use "math"

show "Quadratic Equation Solver: ax^2 + bx + c = 0"

ask "Enter coefficient a: " -> aInput
ask "Enter coefficient b: " -> bInput
ask "Enter coefficient c: " -> cInput

set a = 0
set b = 0
set c = 0
set valid = true

try {
    set a = aInput.toInt()
    set b = bInput.toInt()
    set c = cInput.toInt()
} catch err {
    show "Invalid input. Please enter numbers only."
    set valid = false
}

if valid {
    if a == 0 {
        if b != 0 {
            show f"Linear equation detected. Root: {-c / b}"
        } else {
            show "Invalid equation (0 = 0 or 0 = c)."
        }
    } else {
        set dValue = math.pow(b, 2) - (4 * a * c)
        show f""
        show f"Discriminant |b^2 - 4ac|: {math.abs(dValue)}"

        if dValue >= 0 {
            set x1 = (-b + math.sqrt(dValue)) / (2 * a)
            set x2 = (-b - math.sqrt(dValue)) / (2 * a)
            show f"Real Roots: x1 = {x1}, x2 = {x2}"
        } else {
            set realPart = -b / (2 * a)
            set imagPart = math.sqrt(-dValue) / (2 * a)
            show f"Complex Roots: {realPart} ± {imagPart}i"
        }
    }
}
