-- ⚡ Volt v2.0 - Dictionaries

set user = {
    name: "Alice",
    age: 25,
    email: "alice@volt.dev",
    active: true
}

show f"User: {user}"
show f"Name: {user.name}"
show "Age: " + user["age"]

-- Dict methods
show "Keys: " + user.keys()
show "Values: " + user.values()
show "Has email? " + user.has("email")
show "Has phone? " + user.has("phone")
show "Size: " + user.size()

-- Modify
set user.age = 26
set user["city"] = "New York"
show f"Updated: {user}"

-- Merge dicts
set defaults = {theme: "dark", lang: "en"}
set prefs = {theme: "light", fontSize: 14}
set config = defaults.merge(prefs)
show f"Config: {config}"

-- Iterate over dict
show ""
show "=== Iterating ==="
for key, value in user {
    show f"  {key} -> {value}"
}

-- Dict with higher-order methods
set scores = {alice: 90, bob: 75, charlie: 88, dave: 62}
set passed = scores.filter((k, v) => v >= 80)
show f"Passed: {passed}"
