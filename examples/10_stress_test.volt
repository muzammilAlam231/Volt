-- ⚡ Volt v2.0 - Capability Stress Test (single complex program)

use "math"
use "random"
use "time"
use "file"

show "=== Volt Capability Stress Test ==="
show f"Start timestamp: {time.now()}"

func classifyScore(score) {
    match score {
        case 0 { return "idle" }
        case 1 { return "low" }
        case 2 { return "medium" }
        case 3 { return "high" }
        default { return "extreme" }
    }
}

func fib(n, memo = {}) {
    if memo.has(n) {
        return memo[n]
    }
    if n <= 1 {
        return n
    }
    set value = fib(n - 1, memo) + fib(n - 2, memo)
    set memo[n] = value
    return value
}

func makeIdGenerator(prefix = "agent") {
    set index = 0
    func nextId() {
        set index = index + 1
        return f"{prefix}-{index}"
    }
    return nextId
}

class Agent {
    func init(id, role, energy = 100) {
        set this.id = id
        set this.role = role
        set this.energy = energy
        set this.history = []
    }

    func work(units) {
        if units < 0 {
            throw "units cannot be negative"
        }
        set cost = math.ceil(units * 1.2)
        if cost > this.energy {
            set cost = this.energy
        }
        set this.energy = this.energy - cost
        this.history.push({action: "work", units: units, cost: cost})
        return cost
    }

    func rest(units = 10) {
        if units < 0 {
            throw "rest cannot be negative"
        }
        set gain = math.floor(units * 0.8)
        set this.energy = math.min(100, this.energy + gain)
        this.history.push({action: "rest", units: units, gain: gain})
        return gain
    }

    func score() {
        set totalCost = this.history.filter((e) => e.action == "work").map((e) => e.cost).reduce((acc, x) => acc + x, 0)

        set totalGain = this.history.filter((e) => e.action == "rest").map((e) => e.gain).reduce((acc, x) => acc + x, 0)

        set base = totalCost - totalGain
        if base < 0 {
            set base = 0
        }
        return base
    }

    func toDict() {
        return {
            id: this.id,
            role: this.role,
            energy: this.energy,
            score: this.score(),
            events: this.history.length()
        }
    }

    func toString() {
        return f"Agent({this.id}, role={this.role}, energy={this.energy})"
    }
}

class Simulation {
    func init(seed = 42) {
        set this.seed = seed
        set this.rounds = []
        set this.agents = []
    }

    func addAgent(agent) {
        this.agents.push(agent)
    }

    func run(roundCount = 12) {
        if roundCount <= 0 {
            throw "roundCount must be > 0"
        }

        for round in 1 to roundCount {
            set roundLog = {round: round, actions: []}

            for agent in this.agents {
                set mode = random.int(0, 3)

                if mode <= 2 {
                    set units = random.int(5, 25)
                    set spent = agent.work(units)
                    roundLog.actions.push({
                        id: agent.id,
                        type: "work",
                        units: units,
                        delta: -spent,
                        energy: agent.energy
                    })
                } else {
                    set units = random.int(5, 20)
                    set recovered = agent.rest(units)
                    roundLog.actions.push({
                        id: agent.id,
                        type: "rest",
                        units: units,
                        delta: recovered,
                        energy: agent.energy
                    })
                }
            }

            this.rounds.push(roundLog)
        }
    }

    func leaderboard() {
        set rows = this.agents.map((a) => a.toDict())
        return rows.sort().reverse()
    }

    func analytics() {
        set rows = this.agents.map((a) => a.toDict())

        set avgEnergy = rows.map((r) => r.energy).reduce((acc, x) => acc + x, 0) / rows.length()

        set maxScore = rows.map((r) => r.score).reduce((acc, x) => math.max(acc, x), 0)

        set roleGroups = {builder: 0, analyst: 0, tester: 0}
        for row in rows {
            if roleGroups.has(row.role) {
                set roleGroups[row.role] = roleGroups[row.role] + 1
            }
        }

        return {
            agents: rows.length(),
            rounds: this.rounds.length(),
            avgEnergy: avgEnergy,
            maxScore: maxScore,
            roles: roleGroups
        }
    }
}

set nextId = makeIdGenerator("node")

set sim = new Simulation()
sim.addAgent(new Agent(nextId(), "builder", 100))
sim.addAgent(new Agent(nextId(), "analyst", 95))
sim.addAgent(new Agent(nextId(), "tester", 90))
sim.addAgent(new Agent(nextId(), "builder", 88))

try {
    sim.run(15)
} catch err {
    show f"Simulation failed: {err}"
}

show ""
show "=== Agents ==="
for a in sim.agents {
    show f"  {a}"
}

show ""
show "=== Analytics ==="
set report = sim.analytics()
show f"Total agents: {report.agents}"
show f"Total rounds: {report.rounds}"
show f"Average energy: {report.avgEnergy}"
show f"Max score: {report.maxScore}"
show f"Role distribution: {report.roles}"

show ""
show "=== Classification & Recursion ==="
set level = classifyScore(math.floor(report.maxScore / 40))
show f"System load level: {level}"
show f"fib(20) with memoization: {fib(20)}"

show ""
show "=== Round Sample (first 3 rounds) ==="
set firstRounds = sim.rounds.slice(0, 3)
for r in firstRounds {
    show f"Round {r.round} -> actions={r.actions.length()}"
}

show ""
show "=== Persistence Test ==="
set outPath = "stress_report.txt"
set lines = [
    "Volt Stress Test Report",
    f"Timestamp: {time.now()}",
    f"Agents: {report.agents}",
    f"Rounds: {report.rounds}",
    f"AvgEnergy: {report.avgEnergy}",
    f"MaxScore: {report.maxScore}",
    f"LoadLevel: {level}",
    f"Fib20: {fib(20)}"
]
file.write(outPath, lines.join("\n"))

if file.exists(outPath) {
    show f"Report saved: {outPath} ({file.size(outPath)} bytes)"
    set preview = file.readlines(outPath).slice(0, 4)
    show f"Preview: {preview}"
} else {
    show "Report was not created"
}

show ""
show "=== Error Handling Check ==="
try {
    sim.agents[0].work(-1)
} catch err {
    show f"Expected error captured: {err}"
} finally {
    show "Finalization complete"
}

show ""
show "Capability stress test completed."
