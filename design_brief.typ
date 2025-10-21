
= Technical Brief: B3 BEM Codebase

== Introduction

The `b3_bem` project implements a Blade Element Momentum (BEM) analysis tool for wind turbine rotor performance, leveraging the CCBlade library for aerodynamic computations. It supports configuration via YAML files, optimization of control parameters (e.g., tip-speed ratio, pitch), and generation of performance metrics, blade loads, and visualizations. The codebase integrates with Statesman for workflow management and provides a CLI for execution.


This is a major refactor, the plotting, planform and thickness interpolation from the code remains intact (adjusted to the new inputs), but the running and optimization of operation points is drastically changed, using the gradient based approach using CCBlade gradient features as demonstrated in grad6.py 

Also implement the 4 regime optimization, multiprocessing, and use of initial optimized solutions as initial points for further set points. 