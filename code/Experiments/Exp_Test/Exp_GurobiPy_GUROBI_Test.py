import gurobipy as gp
from gurobipy import GRB

# Create model
m = gp.Model("milp_test")

# Decision variables
# x: continuous in [0, 10]
# y: binary in {0,1}
x = m.addVar(lb=0.0, ub=10.0, vtype=GRB.CONTINUOUS, name="x")
y = m.addVar(vtype=GRB.BINARY, name="y")  # bounds 0/1 implied

# Objective: (x - 3)^2 + y
# Quadratic term is fine in Gurobi
obj = (x - 3.0) * (x - 3.0) + y
m.setObjective(obj, GRB.MINIMIZE)

# Constraint: x >= 2*y   <=>   x - 2y >= 0
m.addConstr(x - 2.0 * y >= 0.0, name="c_x_ge_2y")

# (Optional) Gurobi parameters
m.setParam("OutputFlag", 1)  # 1 = show log, 0 = silent
m.setParam("MIPGap", 0.0)
m.setParam("TimeLimit", 60.0)

# Optimize
m.optimize()

# Check solution status
if m.status == GRB.OPTIMAL:
    x_val = x.X
    y_val = y.X
    f_val = m.objVal

    print("=== Gurobi MILP Test (gurobipy) ===")
    print(f"x* = {x_val:.4f}")
    print(f"y* = {y_val:.4f}  (binary)")
    print(f"f(x*, y*) = {f_val:.4f}")
else:
    print(f"Optimization ended with status {m.status}")
