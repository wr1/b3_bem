# B3 BEM

A wrapper around CCBlade for Blade Element Momentum (BEM) analysis of wind turbine rotors.
Optimizes turbine control in 4 regimes (min speed, opt speed, max speed, max power). 

## Installation

```bash
pip install -e .
```

## Usage

### CLI

```bash
b3-bem run --yml config.yml [--force]
```

### Programmatic

```python
from b3_bem.core.step import B3BemStep
step = B3BemStep('config.yml', force=True)
step.run()
```

Outputs: CSV tables and PNG plots in the workdir.


## Example Output

### Planform
![Planform](docs/assets/ccblade_planform.png)

### Rotor Performance
![Rotor Performance](docs/assets/ccblade_out.png)

### Blade Loads
![Blade Loads](docs/assets/ccblade_bladeloads.png)

### Moments
![Moments](docs/assets/ccblade_moments.png)

## License
MIT
