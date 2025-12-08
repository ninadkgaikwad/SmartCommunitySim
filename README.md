# Smart Community Simulator

The **Smart Community Simulator (SmartComSim)** is a **Gymnasium-compatible simulation and control environment** designed for research, analysis, and intelligent controller development for **single-house** and **multi-house residential communities** with distributed energy resources (DERs).

This simulator was published at **IEEE SmartGridComm 2025**:

```bibtex
@inproceedings{gaikwad2025smart,
  title={Smart Residential Community Simulator for Developing and Benchmarking Energy Management Systems},
  author={Gaikwad, Ninad and Dubey, Anamika},
  booktitle={2025 IEEE International Conference on Communications, Control, and Computing Technologies for Smart Grids (SmartGridComm)},
  pages={1--7},
  year={2025},
  organization={IEEE}
}
```

---

## Key Features

### 1. Heterogeneous Residential Communities
Create communities consisting of houses equipped with:
- **PV + Battery**
- **PV only**
- **Battery only**
- **No DERs**  
(Future versions will support EV integration and per-house DER diversity.)

---

### 2. Detailed House-Level Modeling

#### HVAC System
- Electric HVAC with ON/OFF control  
- Shared RC-network thermal model  
- Future support for per-house thermal parameters  

#### Photovoltaic System
- Controllable in **On-grid mode**  
- Automatic load-matching behavior in **Off-grid mode**

#### Battery Storage
- Scaled Tesla Powerwall model (13.5 kWh)  
- Supports constrained charging/discharging with round-trip efficiency  

#### Priority-Based Non-HVAC Loads
- 8 circuit-level loads per home  
- Supports prioritized load shedding  
- Default load profiles from the **Pecan Street Dataset**

---

### 3. Weather & Load Data Processing
- NSRDB weather data processed from 30-min resolution  
- Pecan Street load data processed from 15-min resolution  
- Flexible user-defined resampling to arbitrary simulation time steps  

---

### 4. Grid-Interaction Modes

#### On-Grid Mode
- Import/export with the grid  
- PV curtailment  
- Energy cost modeling  

#### Off-Grid Mode
- Load prioritization logic  
- PV load-matching  
- Battery-based resilience modeling  

---

### 5. Built-In Baseline Controllers
- Two Off-grid baseline EMS controllers  
- One On-grid baseline EMS controller  
- Plug-and-play support for custom RL and MPC controllers  

---

### 6. Flexible Observation & Action Spaces
- Default Gymnasium observation and action spaces  
- Full support for custom definitions  
- Integrates with RLlib, Stable Baselines3, or custom controllers  

---

## Requirements

### Python (64-bit)
Supported versions:
- 3.9  
- 3.10  
- 3.11  
- 3.12  

### Dependencies
- NumPy  
- SciPy  
- Matplotlib  
- MATLAB **R2025a**  
- `matlab.engine`

---

## MATLAB + Python Setup

1. Install **MATLAB R2025a (64-bit)**  
2. Use Python 3.9–3.12 (64-bit)  
3. Install the MATLAB Engine API:
   ```bash
   python -m pip install matlabengine
   ```  
4. Refer to MathWorks documentation:
   - https://www.mathworks.com/help/matlab/matlab_external/install-the-matlab-engine-for-python.html  
   - https://www.mathworks.com/support/requirements/python-compatibility.html  

---

## Project Structure

```
Smart_Community_Simulator/
├── code
│   ├── Examples
│   ├── Experiments
│   │   ├── Exp_MainScripts
│   │   ├── Exp_Modules
│   │   ├── Exp_Results
│   │   └── Exp_Test
│   ├── SmartComSim
│   └── Test
│
├── data
│   ├── LoadData
│   │   ├── ProcessedFiles
│   │   └── RawFiles
│   └── WeatherData
│       ├── ProcessedFiles
│       └── RawFiles
│
├── environment
│
└── LegacyCode
    ├── Matlab_Organized
    └── MatlabCode_Main
```

---

### New Folders

#### Experiments/
A complete research pipeline for experiments:
- `Exp_MainScripts` — master experiment scripts  
- `Exp_Modules` — reusable experiment utilities  
- `Exp_Results` — plots, logs, and result files  
- `Exp_Test` — minimal/debug experiments  

#### environment/
- Conda environment files  
- Dependency pins  
- Reproducibility helpers  

---

## Weather & Load Data (Dropbox Links)

1. **Processed NSRDB Weather Files**  
   https://www.dropbox.com/scl/fo/rv1ju1legnase4cfrx9zz  

2. **Raw NSRDB Weather Files**  
   https://www.dropbox.com/scl/fo/d73plxcwy3yxcf8v9vyby  

3. **Processed Pecan Street Load Data**  
   https://www.dropbox.com/scl/fo/xv9j7f28o6o6ghtrj7z4v  

4. **Raw Pecan Street Load Data**  
   https://www.dropbox.com/scl/fo/inuuaiq0wydx6ewmwkrop  

---

## Documentation

Example scripts in `code/Examples` demonstrate:
- Creating custom communities  
- Interfacing with MATLAB models  
- Running the simulator step-by-step  
- Using baseline controllers  
- On-grid vs Off-grid experiments  

More detailed documentation is coming soon.

---

## Citation

If you use this simulator in your research, please cite:

```bibtex
@inproceedings{gaikwad2025smart,
  title={Smart Residential Community Simulator for Developing and Benchmarking Energy Management Systems},
  author={Gaikwad, Ninad and Dubey, Anamika},
  booktitle={2025 IEEE International Conference on Communications, Control, and Computing Technologies for Smart Grids (SmartGridComm)},
  pages={1--7},
  year={2025},
  organization={IEEE}
}
```

---

## Authors & Contributors

- **Ninad Kiran Gaikwad**  
- **Shishir Lamichhane**

