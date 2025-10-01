# B3 BEM

A wrapper around CCBlade for Blade Element Momentum (BEM) analysis of wind turbine rotors.

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