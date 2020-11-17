#!/usr/bin/python3

import random

# Number of monopoles.
m = 23
# Number of rooms.
n = 3

# Size of population. Should be even.
npop = 1000
# Mutation rate.
mut = 0.01
# Retention rate.
retained = 0.8
# Maximum number of generations to run the simulation.
# (Will stop early on a perfect score.)
ngen = 500
# Show progress iff True.
trace = True

# A candidate solution is represented as a function
# from monopole to room.
def random_assignment():
    return { i : random.randrange(n) for i in range(1, m + 1) }

# Score of a proposed solution. Number of constraint
# violations: smaller is better, 0 is perfect.
def score(s, show_violations=False):
    fails = 0
    for r in range(n):
        contents = { m for m in s if s[m] == r }
        scontents = sorted(list(contents))
        ncontents = len(contents)
        for i in range(ncontents):
            for j in range(i + 1, ncontents):
                si = scontents[i]
                sj = scontents[j]
                if si + sj in contents:
                    if show_violations:
                        print(f"{si}+{sj}={si + sj}")
                    fails += m + 1 - min(si, sj)
    return fails
    
# Given two solutions s1 and s2, return the index of the one
# that should be deleted.
def tourney(i1, f1, i2, f2):
    if score(f1) < score(f2):
        return i2
    else:
        return i1

# Pick a random "split point" in the genome. Construct a new
# function by picking genes from s1 up to the splitpoint,
# and genes from s2 after.
def recombine_crossover(s1, s2):
    if random.randrange(2) == 1:
        s2, s1 = s1, s2
    c = 1 + random.randrange(m)
    s = dict()
    for i in range(1, c):
        s[i] = s1[i]
    for i in range(c, m + 1):
        s[i] = s2[i]
    return s

# Pick assignments randomly from s1 and s2.
def recombine_shuffle(s1, s2):
    s = dict()
    for i in s1:
        if random.randrange(2) == 1:
            s[i] = s1[i]
        else:
            s[i] = s2[i]
    return s

# For each gene in s, change it to a new random value with
# probability mut.
def mutate(s):
    for i in s:
        if random.random() < mut:
            s[i] = random.randrange(n)

# Construct an initial random population.
pop = [random_assignment() for _ in range(npop)]

# Best individual score ever found.
best_ever = None

# Run the GA loop.
for g in range(ngen):
    # Shuffle the population up.
    random.shuffle(pop)

    # Run the tournament.
    split = int(npop * retained)
    surviving = npop
    while surviving > split:
        i = random.randrange(surviving)
        j = random.randrange(surviving)
        if i == j:
            continue
        remove = tourney(i, pop[i], j, pop[j])
        del pop[remove]
        surviving -= 1
        
    # Replace the losers with combinations
    # of random pairs of winners.
    for i in range(split, npop):
        left = random.randrange(split)
        right = random.randrange(split)
        pop.append(recombine_shuffle(pop[left], pop[right]))
        # This test is strictly an efficiency hack.
        if mut > 0:
            mutate(pop[-1])
    assert len(pop) == npop

    # Find the best score achieved and stop if it is
    # perfect.
    best_index = min(range(npop), key=lambda i: score(pop[i]))
    if best_ever == None or score(pop[best_index]) < score(best_ever):
        best_ever = pop[best_index]

    # Found a perfect solution.
    if score(best_ever) == 0:
        break

    # If tracing, show best and worst scores for this
    # generation.
    if trace:
        worst = score(max(*pop, key=score))
        print(
            "gen", g,
            "best", score(pop[best_index]),
            "best_ever", "none" if best_ever == None else score(best_ever),
            "worst", worst,
        )

def format(s):
    score(s, show_violations=True)
    for r in range(n):
        contents = sorted([ m for m in s if s[m] == r ])
        print(*contents)

# Show final results.
best = min(*pop, key=score)
print(f"best {score(best)}")
format(best)
print(f"best_ever {score(best_ever)}")
format(best_ever)
