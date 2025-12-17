###############################################################################################################
## Import Desired Packages
###############################################################################################################

from pathlib import Path 
import contextlib

###############################################################################################################
## Import Desired Packages
###############################################################################################################


###############################################################################################################
## Main Functions
###############################################################################################################

def Exp_GurobiPy_Model_Diagnostic(m, filename, BASE_DIR=Path(
        r"C:\Users\ninad\Dropbox\NinadGaikwad_PhD\Gaikwad_Research\Gaikwad_Research_Work"
        r"\SmartCommunitySim\code\Experiments\Exp_Test"    )):
    # ---------------------------------------------------------
    # GUROBI MODEL FULL DUMP → TEXT FILE
    # ---------------------------------------------------------

    dump_file = BASE_DIR / filename

    # Ensure directory exists
    dump_file.parent.mkdir(parents=True, exist_ok=True)

    with open(dump_file, "w") as f:

        # -----------------------------------------------------
        # HEADER
        # -----------------------------------------------------
        f.write(
            "===========================================================\n"
            " GUROBI MODEL FULL DUMP\n"
            "   - VARIABLES (name, lb, ub, type)\n"
            "   - OBJECTIVE (sense + expression + term-by-term)\n"
            "   - CONSTRAINTS (name + LHS + sense + RHS + term-by-term LHS)\n"
            "   - OPTIONAL: write .lp / .mps\n"
            "===========================================================\n\n"
            "Notes:\n"
            "- In Gurobi, constraints are stored as:  LHS (<=,==,>=) RHS\n"
            "- LHS is a linear expression (variables + coefficients)\n"
            "- RHS is a constant (float)\n"
            "- Gurobi canonicalizes equations by moving variable terms to LHS,\n"
            "  so RHS is often 0.0 (this is normal).\n"
            "===========================================================\n\n"
        )

        # Ensure model is finalized
        m.update()

        # -----------------------------------------------------
        # 1) VARIABLES
        # -----------------------------------------------------
        f.write("================ VARIABLES ================\n\n")
        for v in m.getVars():
            f.write(
                f"{v.VarName}: lb={v.LB}, ub={v.UB}, type={v.VType}\n"
            )

        f.write(f"\nTotal Variables: {m.NumVars}\n\n")

        # -----------------------------------------------------
        # 2) OBJECTIVE
        # -----------------------------------------------------
        f.write("================ OBJECTIVE ================\n\n")
        f.write(
            "Objective sense: "
            + ("MINIMIZE\n" if m.ModelSense == 1 else "MAXIMIZE\n")
        )

        obj = m.getObjective()
        f.write("\nObjective expression:\n")
        f.write(str(obj) + "\n\n")

        f.write("Objective terms (coeff * var):\n")
        try:
            for i in range(obj.size()):
                var = obj.getVar(i)
                coeff = obj.getCoeff(i)
                f.write(f"{coeff:+.10g} * {var.VarName}\n")
        except Exception as e:
            f.write("Could not iterate objective term-by-term.\n")
            f.write(f"Error: {e}\n")

        f.write("\n")

        # -----------------------------------------------------
        # 3) CONSTRAINTS
        # -----------------------------------------------------
        f.write("================ CONSTRAINTS ================\n\n")

        sense_map = {'<': '<=', '>': '>=', '=': '=='}

        for c in m.getConstrs():
            lhs = m.getRow(c)
            rhs = c.RHS
            sense = sense_map.get(c.Sense, c.Sense)

            f.write(f"Constraint Name: {c.ConstrName}\n")
            f.write(f"  LHS:   {lhs}\n")
            f.write(f"  Sense: {sense}\n")
            f.write(f"  RHS:   {rhs}\n")
            f.write("  LHS terms:\n")

            for i in range(lhs.size()):
                var = lhs.getVar(i)
                coeff = lhs.getCoeff(i)
                f.write(f"    {coeff:+.10g} * {var.VarName}\n")

            f.write("-" * 70 + "\n")

        f.write(f"\nTotal Constraints: {m.NumConstrs}\n")
        f.write("\n===========================================================\n")

    print(f"Gurobi model dump written to '{dump_file}'")

    return None


def Exp_Casadi_Model_Diagnostic(
    NLP_Problem,
    NLP_Solver,
    filename,
    BASE_DIR=Path(
        r"C:\Users\ninad\Dropbox\NinadGaikwad_PhD\Gaikwad_Research\Gaikwad_Research_Work"
        r"\SmartCommunitySim\code\Experiments\Exp_Test"
    ),
):
    """
    Writes a CasADi NLP diagnostic dump to a text file, similar in spirit to the
    Gurobi full dump. Includes:
      - NLP dimensions (nx, ng)
      - symbolic variable names present in f and g
      - sparsity patterns for grad(f) and jac(g)
      - solver IO signature (inputs/outputs + sparsity)
      - (optional) solver stats if solver has been run
    """

    dump_file = BASE_DIR / filename
    dump_file.parent.mkdir(parents=True, exist_ok=True)

    x = NLP_Problem.get("x", None)
    g = NLP_Problem.get("g", None)
    f_obj = NLP_Problem.get("f", None)

    with open(dump_file, "w") as f:

        # -----------------------------------------------------
        # HEADER
        # -----------------------------------------------------
        f.write(
            "===========================================================\n"
            " CASADI NLP MODEL FULL DUMP\n"
            "   - NLP DIMENSIONS (x, g, f)\n"
            "   - SYMBOLIC VARIABLES IN f AND g (symvar)\n"
            "   - SPARSITY (grad(f), jac(g))\n"
            "   - SOLVER SIGNATURE (name_in/name_out + sparsity)\n"
            "   - SOLVER STATS (if available)\n"
            "===========================================================\n\n"
            "Notes:\n"
            "- CasADi does not store constraint 'names' like Gurobi.\n"
            "- To get per-constraint names, you must store them yourself\n"
            "  when constructing g (e.g., g_terms + g_names).\n"
            "===========================================================\n\n"
        )

        # -----------------------------------------------------
        # 1) NLP DIMENSIONS
        # -----------------------------------------------------
        f.write("================ NLP DIMENSIONS ================\n\n")

        if x is None or g is None or f_obj is None:
            f.write("ERROR: NLP_Problem must contain keys {'f','x','g'}.\n")
        else:
            f.write(f"x shape: {x.shape}  -> n_x = {int(x.numel())}\n")
            f.write(f"g shape: {g.shape}  -> n_g = {int(g.numel())}\n")
            f.write(f"f shape: {f_obj.shape}  -> n_f = {int(f_obj.numel())}\n")

        f.write("\n")

        # -----------------------------------------------------
        # 2) SYMBOLIC VARIABLES PRESENT IN f AND g
        # -----------------------------------------------------
        f.write("================ SYMBOLIC VARIABLES (symvar) ================\n\n")

        if f_obj is not None:
            try:
                f_syms = [v.name() for v in ca.symvar(f_obj)]
                f.write("symvar(f): " + (", ".join(f_syms) if f_syms else "(none)") + "\n")
            except Exception as e:
                f.write(f"Could not compute symvar(f). Error: {e}\n")

        if g is not None:
            try:
                g_syms = [v.name() for v in ca.symvar(g)]
                f.write("symvar(g): " + (", ".join(g_syms) if g_syms else "(none)") + "\n")
            except Exception as e:
                f.write(f"Could not compute symvar(g). Error: {e}\n")

        f.write("\n")

        # -----------------------------------------------------
        # 3) SPARSITY PATTERNS
        # -----------------------------------------------------
        f.write("================ SPARSITY ================\n\n")

        if (x is not None) and (f_obj is not None):
            try:
                grad_f = ca.gradient(f_obj, x)
                f.write(f"grad(f) sparsity: {grad_f.sparsity()}  nnz={grad_f.sparsity().nnz()}\n")
            except Exception as e:
                f.write(f"Could not compute grad(f). Error: {e}\n")

        if (x is not None) and (g is not None):
            try:
                Jg = ca.jacobian(g, x)
                sp = Jg.sparsity()
                f.write(f"jac(g) sparsity: {sp}  nnz={sp.nnz()}\n")
            except Exception as e:
                f.write(f"Could not compute jac(g). Error: {e}\n")

        f.write("\n")

        # -----------------------------------------------------
        # 4) SOLVER SIGNATURE (inputs/outputs + sparsity)
        # -----------------------------------------------------
        f.write("================ SOLVER SIGNATURE ================\n\n")

        if NLP_Solver is None:
            f.write("No NLP_Solver provided.\n")
        else:
            try:
                f.write("Inputs : " + ", ".join(NLP_Solver.name_in()) + "\n")
                f.write("Outputs: " + ", ".join(NLP_Solver.name_out()) + "\n\n")

                f.write("Input sizes (sparsity):\n")
                for nm in NLP_Solver.name_in():
                    sp_in = NLP_Solver.sparsity_in(nm)
                    f.write(f"  {nm}: {sp_in.size1()} x {sp_in.size2()}  nnz={sp_in.nnz()}\n")

                f.write("\nOutput sizes (sparsity):\n")
                for nm in NLP_Solver.name_out():
                    sp_out = NLP_Solver.sparsity_out(nm)
                    f.write(f"  {nm}: {sp_out.size1()} x {sp_out.size2()}  nnz={sp_out.nnz()}\n")

            except Exception as e:
                f.write(f"Could not read solver signature. Error: {e}\n")

        f.write("\n")

        # -----------------------------------------------------
        # 5) SOLVER STATS (if available)
        # -----------------------------------------------------
        f.write("================ SOLVER STATS ================\n\n")
        if NLP_Solver is None:
            f.write("No NLP_Solver provided.\n")
        else:
            try:
                stats = NLP_Solver.stats()
                for k, v in stats.items():
                    f.write(f"{k}: {v}\n")
            except Exception as e:
                f.write(f"Could not read solver stats (solver may not have run yet). Error: {e}\n")

        f.write("\n===========================================================\n")

    print(f"CasADi model dump written to '{dump_file}'")
    return None