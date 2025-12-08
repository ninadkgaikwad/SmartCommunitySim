import casadi as ca

# -------------------------------
# Decision variables
# -------------------------------
x = ca.SX.sym("x", 2)  # x[0] = x, x[1] = y (now continuous)

obj = (x[0] - 3.0)**2 + x[1]

g = []
g.append(x[0] - 2*x[1])   # x >= 2*y

g = ca.vertcat(*g)

nlp = {"x": x, "f": obj, "g": g}

# -------------------------------
# IPOPT options (pure NLP)
# -------------------------------
opts = {
    "ipopt": {
        "print_level": 5,
        "tol": 1e-6,
    },
    "print_time": True,
}

""" opts = {
        "print_level": 5,
        "tol": 1e-6,
        #"print_time": True,
} """

solver = ca.nlpsol("solver", "ipopt", nlp, opts)

# Bounds: now y is continuous, but still [0,1]
lbx = [0.0, 0.0]
ubx = [10.0, 1.0]

# g(x) = x - 2*y >= 0
lbg = [0.0]
ubg = [ca.inf]

sol = solver(lbx=lbx, ubx=ubx, lbg=lbg, ubg=ubg)

x_opt = sol["x"].full().flatten()

print("=== IPOPT NLP Test ===")
print(f"x* = {x_opt[0]:.4f}")
print(f"y* = {x_opt[1]:.4f}  (continuous relaxation)")
print(f"f(x*,y*) = {(x_opt[0]-3.0)**2 + x_opt[1]:.4f}")
