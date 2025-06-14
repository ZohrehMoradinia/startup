
# import streamlit as st
# import pandas as pd
# #import matplotlib.pyplot as plt
# import numpy as np
# import pickle
# import streamlit as st
# import pandas as pd
# import matplotlib.pyplot as plt
# import numpy as np

# import pymoo
# from pymoo.core.problem import Problem
# from pymoo.algorithms.moo.nsga2 import NSGA2
# #from pymoo.factory import get_sampling, get_crossover, get_mutation
# from pymoo.core.mixed import MixedVariableMating, MixedVariableGA, MixedVariableSampling, MixedVariableDuplicateElimination
# from pymoo.optimize import minimize
# from pymoo.core.variable import Real, Integer
# from pymoo.core.problem import ElementwiseProblem
# from pymoo.visualization.scatter import Scatter
# from pymoo.util.ref_dirs import get_reference_directions
# import matplotlib.pyplot as plt
# import warnings
# from pymoo.problems import get_problem
# warnings.filterwarnings("ignore")
# from pymoo.core.callback import Callback
# import numpy as np
# from scipy.interpolate import griddata
# from scipy.interpolate import interpn
# import pandas as pd
# import csv
# import os
# from pymoo.termination import get_termination
# from pymoo.termination.robust import RobustTermination
# from pymoo.termination.ftol import MultiObjectiveSpaceTermination
# import io



# st.set_page_config(layout="wide")
# st.title("Mooring System Design Optimization UI")
# st.markdown("""
# Welcome to the Mooring System Optimization Platform.

# To begin, please:
# 1. Define the ranges for your decision variables using the panel on the left.
# 2. Upload your dataset used to train the surrogate model.
# 3. Click 'Run Optimization' to execute the optimization and view results.
# """)

# # Sidebar - Parameter Ranges
# st.sidebar.header("Step 1: Define Decision Variable Ranges")
# param_ranges = {}
# param_ranges['chain_length_min'] = st.sidebar.number_input("Min Chain Length (m)", value=200)
# param_ranges['chain_length_max'] = st.sidebar.number_input("Max Chain Length (m)", value=350)
# param_ranges['chain_mass_min'] = st.sidebar.number_input("Min Chain Mass (kg/m)", value=107)
# param_ranges['chain_mass_max'] = st.sidebar.number_input("Max Chain Mass (kg/m)", value=285)
# param_ranges['pretension_min'] = st.sidebar.number_input("Min Pretension (kN)", value=75)
# param_ranges['pretension_max'] = st.sidebar.number_input("Max Pretension (kN)", value=225)
# param_ranges['buoy_dist_min'] = st.sidebar.number_input("Min Buoy-Hull Distance (m)", value=50)
# param_ranges['buoy_dist_max'] = st.sidebar.number_input("Max Buoy-Hull Distance (m)", value=100)

# # Upload Dataset
# st.subheader("Step 2: Upload Surrogate Model Training Dataset")
# uploaded_file = st.file_uploader("Upload CSV Dataset", type=["csv"], help="This dataset should be used to train or feed the surrogate model.")

# if uploaded_file is not None:
#     df = pd.read_csv(uploaded_file)
#     st.success("✅ Dataset uploaded successfully.")
#     st.write("Preview of Uploaded Dataset:")
#     st.dataframe(df.head())

#     # Define cost and constraint functions
#     chain_price = 23.80
#     rope_price = 15.24

#     def cost_function(Chain_lengths, PreTensions, chain_mass):
#         return np.sum((Chain_lengths * chain_mass * chain_price) + PreTensions * rope_price)

#     def constrsints(Chain_lengths, Chain_mass, PreTensions, Buoy_Hull_Distances):
#         X = df[['Chain_lengths', 'Chain_mass', 'PreTensions', 'Buoy_Hull_Distances']].values
#         y = df['Output_mean_X'].values
#         interp_value = griddata(X, y, [[Chain_lengths, Chain_mass, PreTensions, Buoy_Hull_Distances]], method='linear')
#         if interp_value is None or np.isnan(interp_value[0]):
#             interp_value = np.array([0.0])
#         return float(interp_value[0])

#     class FloatingWindTurbineProblem(ElementwiseProblem):
#         def __init__(self, **kwargs):
#             vars = {
#                 "Chain_lengths": Integer(bounds=(param_ranges['chain_length_min'], param_ranges['chain_length_max'])),
#                 "Chain_mass": Integer(bounds=(param_ranges['chain_mass_min'], param_ranges['chain_mass_max'])),
#                 "PreTensions": Integer(bounds=(param_ranges['pretension_min'], param_ranges['pretension_max'])),
#                 "Buoy_Hull_Distances": Integer(bounds=(param_ranges['buoy_dist_min'], param_ranges['buoy_dist_max'])),
#             }
#             super().__init__(vars=vars, n_obj=2, n_ieq_constr=1, **kwargs)

#         def _evaluate(self, x, out, *args, **kwargs):
#             Chain_lengths, Chain_mass, PreTensions, Buoy_Hull_Distances = x
#             cost = cost_function(Chain_lengths, PreTensions, Chain_mass)
#             cons = constrsints(Chain_lengths, Chain_mass, PreTensions, Buoy_Hull_Distances)
#             out["F"] = [cost, -cons]
#             out["G"] = -cons - 12

#     class MyCallback(Callback):
#         def __init__(self):
#             super().__init__()
#             self.data["F"] = []
#             self.data["x"] = []
#             self.data["G"] = []
#             self.data["best_offset_values"] = []
#             self.data["best_cost_values"] = []

#         def notify(self, algorithm):
#             self.data["F"].append(algorithm.pop.get("F"))
#             self.data["x"].append(algorithm.pop.get("X"))
#             self.data["G"].append(algorithm.pop.get("G"))
#             self.data["best_offset_values"].append(algorithm.pop.get("F")[:, 1].max())
#             self.data["best_cost_values"].append(algorithm.pop.get("F")[:, 0].min())

#     # Run Optimization
#     st.subheader("Step 3: Run Optimization")
#     if st.button("Run Optimization"):
#         with st.spinner("Running optimization using surrogate model..."):
#             ref_dirs = get_reference_directions("das-dennis", 3, n_partitions=30)
#             problem = FloatingWindTurbineProblem(return_as_dictionary=False)
#             algorithm = NSGA2(
#                 pop_size=10,
#                 sampling=MixedVariableSampling(),
#                 mating=MixedVariableMating(eliminate_duplicates=MixedVariableDuplicateElimination()),
#                 eliminate_duplicates=MixedVariableDuplicateElimination(),
#                 ref_dirs=ref_dirs
#             )
#             termination = RobustTermination(
#                 MultiObjectiveSpaceTermination(tol=0.05, n_skip=10), period=25
#             )
#             res = minimize(
#                 problem,
#                 algorithm,
#                 seed=1,
#                 callback=MyCallback(),
#                 save_history=True,
#                 termination=termination
#             )

#             F = res.F
#             df_results = pd.DataFrame(F, columns=['Cost', 'Negative X-Offset'])
#             df_results['X-Offset'] = -df_results['Negative X-Offset']
#             df_results = df_results.drop(columns='Negative X-Offset')

#         st.success("✅ Optimization completed successfully.")
#         st.subheader("Pareto Optimal Solutions")
#         st.dataframe(df_results.sort_values(by='Cost'))

#         fig, ax = plt.subplots()
#         ax.scatter(df_results['X-Offset'], df_results['Cost'], color='red')
#         ax.set_xlabel("X-Offset (m)")
#         ax.set_ylabel("Cost")
#         ax.set_title("Pareto Front")
#         st.pyplot(fig)

#         st.download_button("Download Results", data=df_results.to_csv(index=False), file_name="pareto_solutions.csv")



import streamlit as st
import pandas as pd
#import matplotlib.pyplot as plt
import numpy as np
import pickle
import pymoo
from pymoo.core.problem import Problem
from pymoo.algorithms.moo.nsga2 import NSGA2
#from pymoo.factory import get_sampling, get_crossover, get_mutation
from pymoo.core.mixed import MixedVariableMating, MixedVariableGA, MixedVariableSampling, MixedVariableDuplicateElimination
from pymoo.optimize import minimize
from pymoo.core.variable import Real, Integer
from pymoo.core.problem import ElementwiseProblem
from pymoo.visualization.scatter import Scatter
from pymoo.util.ref_dirs import get_reference_directions
import matplotlib.pyplot as plt
import warnings
from pymoo.problems import get_problem
warnings.filterwarnings("ignore")
from pymoo.core.callback import Callback
import numpy as np
from scipy.interpolate import griddata
from scipy.interpolate import interpn
import pandas as pd
import csv
import os
from pymoo.termination import get_termination
from pymoo.termination.robust import RobustTermination
from pymoo.termination.ftol import MultiObjectiveSpaceTermination
import io





st.set_page_config(layout="wide")
st.title("Mooring System Design Optimization UI")
st.markdown("""
Welcome to the Mooring System Optimization Platform.

To begin, please:
1. Define the ranges for your decision variables using the panel on the left.
2. Upload your dataset used to train the surrogate model.
3. Click 'Run Optimization' to execute the optimization and view results.
""")

# Sidebar - Parameter Ranges
st.sidebar.header("Step 1: Define Decision Variable Ranges")
param_ranges = {}
param_ranges['chain_length_min'] = int(st.sidebar.number_input("Min Chain Length (m)", value=200))
param_ranges['chain_length_max'] = int(st.sidebar.number_input("Max Chain Length (m)", value=350))
param_ranges['chain_mass_min'] =   int(st.sidebar.number_input("Min Chain Mass (kg/m)", value=107))
param_ranges['chain_mass_max'] =   int(st.sidebar.number_input("Max Chain Mass (kg/m)", value=285))
param_ranges['pretension_min'] =   int(st.sidebar.number_input("Min Pretension (kN)", value=75))
param_ranges['pretension_max'] =   int(st.sidebar.number_input("Max Pretension (kN)", value=225))
param_ranges['buoy_dist_min'] =    int(st.sidebar.number_input("Min Buoy-Hull Distance (m)", value=50))
param_ranges['buoy_dist_max'] =    int(st.sidebar.number_input("Max Buoy-Hull Distance (m)", value=100))


# Upload Dataset
st.subheader("Step 2: Upload Surrogate Model Training Dataset")
uploaded_file = st.file_uploader("Upload CSV Dataset", type=["csv"], help="This dataset should be used to train or feed the surrogate model.")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.success("✅ Dataset uploaded successfully.")
    st.write("Preview of Uploaded Dataset:")
    st.dataframe(df.head())

    # Define cost and constraint functions
    chain_price = 23.80
    rope_price = 15.24

    def cost_function(Chain_lengths, PreTensions, chain_mass):
         
        Chain_lengths = float(Chain_lengths)
        PreTensions = float(PreTensions)
        chain_mass = float(chain_mass)
        return (Chain_lengths * chain_mass * chain_price) + (PreTensions * rope_price)


        return np.sum((Chain_lengths * chain_mass * chain_price) + PreTensions * rope_price)

    def constrsints(Chain_lengths, Chain_mass, PreTensions, Buoy_Hull_Distances):
        X = df[['Chain_lengths', 'Chain_mass', 'PreTensions', 'Buoy_Hull_Distances']].values
        y = df['Output_mean_X'].values
        interp_value = griddata(X, y, [[Chain_lengths, Chain_mass, PreTensions, Buoy_Hull_Distances]], method='linear')
        if interp_value is None or np.isnan(interp_value[0]):
            interp_value = np.array([0.0])
        return float(interp_value[0])

    class FloatingWindTurbineProblem(ElementwiseProblem):
        def __init__(self, **kwargs):
    
            vars = {
                 "Chain_lengths": Integer(bounds=(param_ranges['chain_length_min'], param_ranges['chain_length_max'])),
                 "Chain_mass": Integer(bounds=(param_ranges['chain_mass_min'], param_ranges['chain_mass_max'])),
                 "PreTensions": Integer(bounds=(param_ranges['pretension_min'], param_ranges['pretension_max'])),
                 "Buoy_Hull_Distances": Integer(bounds=(param_ranges['buoy_dist_min'], param_ranges['buoy_dist_max'])),
            }

            super().__init__(vars=vars, n_obj=2, n_ieq_constr=1, **kwargs)

        def _evaluate(self, x, out, *args, **kwargs):
            Chain_lengths, Chain_mass, PreTensions, Buoy_Hull_Distances = x
        
            Chain_lengths = float(x["Chain_lengths"])
            Chain_mass = float(x["Chain_mass"])
            PreTensions = float(x["PreTensions"])
            Buoy_Hull_Distances = float(x["Buoy_Hull_Distances"])
            cost = cost_function(Chain_lengths, PreTensions, Chain_mass)
            cons = constrsints(Chain_lengths, Chain_mass, PreTensions, Buoy_Hull_Distances)
            out["F"] = [cost, -cons]
            out["G"] = -cons - 12

    class MyCallback(Callback):
        def __init__(self):
            super().__init__()
            self.data["F"] = []
            self.data["x"] = []
            self.data["G"] = []
            self.data["best_offset_values"] = []
            self.data["best_cost_values"] = []

        def notify(self, algorithm):
            self.data["F"].append(algorithm.pop.get("F"))
            self.data["x"].append(algorithm.pop.get("X"))
            self.data["G"].append(algorithm.pop.get("G"))
            self.data["best_offset_values"].append(algorithm.pop.get("F")[:, 1].max())
            self.data["best_cost_values"].append(algorithm.pop.get("F")[:, 0].min())

    # Run Optimization
    st.subheader("Step 3: Run Optimization")
    if st.button("Run Optimization"):
        with st.spinner("Running optimization using surrogate model..."):
            ref_dirs = get_reference_directions("das-dennis", 3, n_partitions=30)
            problem = FloatingWindTurbineProblem(return_as_dictionary=False)
            algorithm = NSGA2(
                pop_size=10,
                sampling=MixedVariableSampling(),
                mating=MixedVariableMating(eliminate_duplicates=MixedVariableDuplicateElimination()),
                eliminate_duplicates=MixedVariableDuplicateElimination(),
                ref_dirs=ref_dirs
            )
            termination = RobustTermination(
                MultiObjectiveSpaceTermination(tol=0.05, n_skip=10), period=25
            )
            res = minimize(
                problem,
                algorithm,
                seed=1,
                callback=MyCallback(),
                save_history=True,
                termination=termination
            )

            F = res.F
            val = res.algorithm.callback.data["F"]
            individuals =res.algorithm.callback.data["x"]
            G_const =res.algorithm.callback.data["G"]
            best_offset_values = res.algorithm.callback.data["best_offset_values"]
            best_cost_values = res.algorithm.callback.data["best_cost_values"]
            df_results = pd.DataFrame(F, columns=['Cost', 'Negative X-Offset'])
            df_results['X-Offset'] = -df_results['Negative X-Offset']
            df_results = df_results.drop(columns='Negative X-Offset')

            gen_n = res.algorithm.n_gen  # generation number
            X = res.X                    # list of dicts
            F = res.F                    # list/array of objective values
            G = res.G                    # list/array of constraints

            with open("optimization_results.csv", mode="w", newline="") as csvfile:
                writer = csv.writer(csvfile)

                # Write the header
                writer.writerow(["gen_n", "x", "F", "G"])

                # Write each row
                for i in range(len(X)):
                    x_str = str(X[i])           # dict to string
                    f_str = str(F[i])           # objective to string
                    g_str = str(G[i]) if G is not None else ""  # handle G being None
                    writer.writerow([gen_n, x_str, f_str, g_str])



        st.success("✅ Optimization completed successfully.")
        st.subheader("Pareto Optimal Solutions")
        st.dataframe(df_results.sort_values(by='Cost'))

        fig, ax = plt.subplots()
        ax.scatter(df_results['Cost'], df_results['X-Offset'], color='red')
        ax.set_xlabel(" Cost")
        ax.set_ylabel(" X-Offset (m)")
        ax.set_title("Pareto Front")
        st.pyplot(fig)

        # Create in-memory CSV buffer
        buffer = io.StringIO()
        writer = csv.writer(buffer)

        # Write header
        writer.writerow(["gen_n", "x", "F", "G"])

        # Write data
        for i in range(len(X)):
            x_str = str(X[i])
            f_str = str(F[i])
            g_str = str(G[i]) if G is not None else ""
            writer.writerow([gen_n, x_str, f_str, g_str])

        # Move to beginning of buffer
        buffer.seek(0)

        # Add Streamlit download button
        st.download_button(
            label="Download Optimization Results CSV",
            data=buffer.getvalue(),
            file_name="optimization_results.csv",
            mime="text/csv"
        )

        st.download_button("Download Solutions", data=df_results.to_csv(index=False), file_name="pareto_solutions.csv")
     

        




