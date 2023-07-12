from pyomo.environ import *
import pandas as pd
import numpy as np

days = [0, 1, 2, 3, 4, 5, 6]
shifts = [0, 1, 2, 3, 4, 5, 6]
# Given demand by day
demand = [16, 12, 18, 13, 15, 9, 7]

# 7 shift types for employees in a week (3 consequtive days and 4 days off)
num_shifts = len(days)
num_days = len(shifts)

# creating a shift pattern table with 0
np_shift = np.empty(shape=(num_shifts,num_days))
np_shift.fill(0)

# Initializing the first 3 days with 1
for j in range(3):
    np_shift[0][j] = 1

# Roll the 3 days shifts
for j in range(1,num_shifts):
    np_shift[j] = np.array(np.roll(np_shift[j-1],1,0))

# Shift matrix
print("Shift matrix\n",np_shift)

# model formulation
model = ConcreteModel()

# variables (employees across each shift)
model.emp = Var(shifts, domain=NonNegativeIntegers)

# Calculate daily totals of employees based on the variable
daily = []

for i in shifts:
    tot = 0
    for j in days:
        tot += model.emp[j]*np_shift[j][i]
    daily.append(tot)

total_shift_staff = sum(daily)/3

# objective minimize total shift staff
model.objective = Objective(expr = total_shift_staff, sense=minimize)

# constraints
model.constraints = ConstraintList()

# demand constraint based on daily employee totals
for j in days:
    model.constraints.add(daily[j] >= demand[j])

# Employees in first 3 shifts
fir_three = sum(model.emp[i] for i in range(3))

# Employees in last 4 shifts
last_four = sum(model.emp[i] for i in range(3,num_shifts))

# Add constraint that atleast half of employees to be off on Sat and Sun
# Only Shifts 1, 2 and 3 does not have weekend overlap 
model.constraints.add(last_four <= fir_three)

solver = SolverFactory('glpk')
solver.solve(model)

print("Optimized employees:",total_shift_staff())
