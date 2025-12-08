import gurobipy as gp
from gurobipy import GRB

# Create model
m = gp.Model("milp_test")

# ---------------------------
# Decision variables
# ---------------------------
# x[0] = continuous variable ∈ [0,10]
# x[1] = binary variable ∈ {0,1}
x = m.addVars(2, name="x")     # creates x[0], x[1]

# Set variable types explicitly
x[0].vtype = GRB.CONTINUOUS
x[0].lb = 0.0
x[0].ub = 10.0

x[1].vtype = GRB.BINARY       # automatically 0 or 1

# ---------------------------
# Objective: (x0 – 3)^2 + x1
# ---------------------------
obj = (x[0] - 3.0) * (x[0] - 3.0) + x[1]
m.setObjective(obj, GRB.MINIMIZE)

# ---------------------------
# Constraint: x0 >= 2*x1
# ---------------------------
m.addConstr(x[0] - 2 * x[1] >= 0.0, name="c_x_ge_2y")

# Solver params
m.setParam("OutputFlag", 1)
m.setParam("MIPGap", 0.0)
m.setParam("TimeLimit", 60.0)

# Optimize
m.optimize()

# ---------------------------
# Print solution
# ---------------------------
if m.status == GRB.OPTIMAL:
    x0 = x[0].X
    x1 = x[1].X
    fval = m.objVal

    print("\n=== Gurobi MILP Test (Vector x) ===")
    print(f"x[0]* = {x0:.4f}  (continuous)")
    print(f"x[1]* = {x1:.4f}  (binary)")
    print(f"Objective = {fval:.4f}")
else:
    print(f"Optimization ended with status {m.status}")
