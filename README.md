# Smart Community Simulator

The Smart Community Simulator is designed as a Gymnasium Environment for simulation/analysis/intelligent control design for single house or a community with the following features:

1. **Heterogenous Residential Community:** A community of houses can be created from a mixture of houses with different combinations of Distributed Energy Resources (DERs).
2. **DER Combinations:** Houses can have any combination of DERs in PV+Bat/Bat/PV/None (PV - Photovoltaic Panels, Bat - Battery Storage) (Future version will have EVs too).
3. **HVAC:** Every house is equipped with Electric HVAC system capable of both heating and cooling modes and control is on-off of the HVAC (Thermal characteristics for all houses are the same -> Future version will have the ability for having different thermal characteristics characteristics for each house).
3. **Photovoltaic Panels:** PV of desired size can be employed and its power output can be controlled in On-grid mode only (in Off-grid mode PV acts in load matching mode) (PV specifications are same for every house that has PV -> Future version will have the ability for having different PV specifications for every house with PV).
3. **Battery Storage:** Battery of desired size can be employed (through scaling of Tesla Powerwall 13.5kWh) and its charging/discharging power can be controlled (Battery storage specifications are the same for every house with a battery -> Future version will have the ability for having different battery storage specifications for every house with battery).
6. **Non-HVAC Load:** Every House load circuit is divided 8 circuits with different combination of loads so that a priority of loads can be developed and each load circuit can be individually turned on or off (currently the load data source is free PecanStreet Dataset).
7. **Weather Data:** Cuurently we support weather data from National Solar Radiation Database (NSRDB).
8. **Weather/Load Data Preprocessing:** We provide functionality for preprocessing NSRDB (original dataset 30 mins) and PecanStreet datasets (original dataset 15 mins) to any desired higher time resolution for custom time resolution simulation and control design applications. 
9. **Grid Interaction:** Supports simulations for both On-grid and Off-grid operational modes.
10. **Default Baseline Controllers:** We provide tow default controllers for Off-grid mode and one for On-grid mode.
11. **Flexible Observation And Action Spaces:** The simulator has default observation and action spaces; however, we provide interface for custom observation/action spaces so as to model custom control scenarios.

## Requirements
- Python
- NumPy
- SciPy
- Matplotlib
- MATLAB
- matlab.engine

## Project Structure

```
Smart_Community_Simulator/
├── code
│   ├── Examples
│   ├── SmartComSim
│   ├── Test
│
├── data
│   ├── LoadData
│   │   ├── ProcessedFiles
│   │   └── RawFiles
│   └── WeatherData
│       ├── ProcessedFiles
│       └── RawFiles
│
└── LegacyCode
    ├── Matlab_Organized
    └── MatlabCode_Main
```

The Examples folder has detailed explanation scripts for understanding the various aspects of this simulator environment and the default controllers.

More documentation will follow....

## Weather and Load Files

1. [Dropbox Link to Processed NSRDB Weather Files for major cities in US](https://www.dropbox.com/scl/fo/rv1ju1legnase4cfrx9zz/ACcbPML55FaOzVC4UYFuPv0?rlkey=g0c1younsdemmdhsoy0b3emjv&st=u0kt0h2q&dl=0)
2. [Dropbox Link to Raw NSRDB Weather Files for major cities in US](https://www.dropbox.com/scl/fo/d73plxcwy3yxcf8v9vyby/AHGXfNsgwUnQhY9DpA6ekmU?rlkey=yb5lptobeosrm00qd5fvjf9oa&st=5cysv7rw&dl=0)
3. [Dropbox Link to PecanStreet Processed Dataset](https://www.dropbox.com/scl/fo/xv9j7f28o6o6ghtrj7z4v/AP6sk6xp148zx3Nr42piAPA?rlkey=ha1hntpckghli443p8arieqhh&st=egug5d84&dl=0)
3. [Dropbox Link to PecanStreet Raw Dataset](https://www.dropbox.com/scl/fo/inuuaiq0wydx6ewmwkrop/ABcg9HjHGVgvcoDCq6OXxYo?rlkey=w1qg6xplj6hryjcjlvf7ij5we&st=1hlrira2&dl=0)

## Citation

Coming soon....

## Authors and Contributors
1. Ninad Kiran Gaikwad
2. Shishir Lamichhane

