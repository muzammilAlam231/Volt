-- ⚡ Volt v2.0 - Hello World


-- number guessing game
set secret = 42
set maxAttempts = 5
set attempts = 0
ask "Guess the secret number: " -> guess
set gameOver = false
while !gameOver {
    set attempts = attempts + 1
    if guess.toInt() == secret {
        show "Congratulations! You guessed it!"
        set gameOver = true
    } else if guess.toInt() < secret {
        show "Too low! Try again."
    } else {
        show "Too high! Try again."
    }
    if attempts >= maxAttempts {
        show f"Game over! The secret number was {secret}."
        set gameOver = true
    } else if not gameOver {
        ask "Guess the secret number: " -> guess
    }
}