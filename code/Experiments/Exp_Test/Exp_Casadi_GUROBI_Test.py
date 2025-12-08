import casadi as ca
import os

gurobi_bin_path = r"C:\gurobi1300\win64\bin"
os.environ['PATH'] += os.pathsep + gurobi_bin_path


# -------------------------------
# Decision variables
# -------------------------------
# x[0] = x (continuous)
# x[1] = y (binary)
x = ca.SX.sym("x", 2)

# Objective
obj = (x[0] - 3.0)**2 + x[1]

# Constraint list: g(x) >= 0 / == 0 style
g = []

# Constraint: x >= 2*y  ->  x - 2*y >= 0
g.append(x[0] - 2*x[1])

g = ca.vertcat(*g)

nlp = {"x": x, "f": obj, "g": g}

# -------------------------------
# Gurobi options (MILP/MINLP)
# -------------------------------
# Mark x[1] as integer (binary with bounds [0,1])
int_vars = [1]

opts = {
    "gurobi": {
        "int_vars": int_vars,
        "OutputFlag": 1,     # Show Gurobi log
        "MIPGap": 0.0,       # Tight optimality tolerance
        "TimeLimit": 60.0,   # Just in case
    }
}

opts = {
        "int_vars": int_vars,
        "OutputFlag": 1,     # Show Gurobi log
        "MIPGap": 0.0,       # Tight optimality tolerance
        "TimeLimit": 60.0,   # Just in case
    
}

solver = ca.nlpsol("solver", "gurobi", nlp, opts)

# Bounds: x free in [0, 10], y binary (0 or 1)
lbx = [0.0, 0.0]
ubx = [10.0, 1.0]

# Constraint bounds: g[0] = x - 2*y >= 0
lbg = [0.0]    # lower bound
ubg = [ca.inf] # upper bound

sol = solver(lbx=lbx, ubx=ubx, lbg=lbg, ubg=ubg)

x_opt = sol["x"].full().flatten()

print("=== Gurobi MILP Test ===")
print(f"x* = {x_opt[0]:.4f}")
print(f"y* = {x_opt[1]:.4f}  (should be ~0 or 1, here binary)")
print(f"f(x*,y*) = {(x_opt[0]-3.0)**2 + x_opt[1]:.4f}")
