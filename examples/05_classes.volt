-- ⚡ Volt v2.0 - Classes & OOP

-- Basic class
class Animal {
    func init(name, sound) {
        set this.name = name
        set this.sound = sound
    }

    func speak() {
        show f"{this.name} says {this.sound}!"
    }

    func toString() {
        return f"Animal({this.name})"
    }
}

-- Inheritance
class Dog extends Animal {
    func init(name, breed) {
        super.init(name, "Woof")
        set this.breed = breed
    }

    func fetch(item) {
        show f"{this.name} fetches the {item}!"
    }

    func toString() {
        return f"Dog({this.name}, {this.breed})"
    }
}

class Cat extends Animal {
    func init(name) {
        super.init(name, "Meow")
        set this.lives = 9
    }

    func scratch() {
        show f"{this.name} scratches!"
    }
}

-- Create instances
set dog = new Dog("Rex", "Labrador")
set cat = new Cat("Whiskers")

dog.speak()
dog.fetch("ball")
show dog

cat.speak()
cat.scratch()
show f"Lives: {cat.lives}"

-- Check types
show "dog is Animal? " + isinstance(dog, Animal)
show "cat is Dog? " + isinstance(cat, Dog)

show ""
show "=== A More Complex Example ==="

class Vector {
    func init(x, y) {
        set this.x = x
        set this.y = y
    }

    func add(other) {
        return new Vector(this.x + other.x, this.y + other.y)
    }

    func scale(factor) {
        return new Vector(this.x * factor, this.y * factor)
    }

    func magnitude() {
        return (this.x * this.x + this.y * this.y)
    }

    func toString() {
        return f"({this.x}, {this.y})"
    }
}

set v1 = new Vector(3, 4)
set v2 = new Vector(1, 2)
set v3 = v1.add(v2)
set v4 = v1.scale(2)

show f"v1 = {v1}"
show f"v2 = {v2}"
show f"v1 + v2 = {v3}"
show f"v1 * 2 = {v4}"
