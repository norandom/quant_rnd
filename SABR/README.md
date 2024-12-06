# SABR Model Implementation with OpenBB Data

This project implements the SABR (Stochastic Alpha, Beta, Rho) volatility model using real market data fetched through OpenBB. The implementation focuses on analyzing options volatility smiles and calibrating the SABR model parameters.

## Overview

### SABR Model
The SABR model is a stochastic volatility model used extensively in financial mathematics, particularly in interest rate and equity derivatives markets. It was introduced by Hagan et al. in 2002 and has become an industry standard for modeling the volatility smile in options markets.

The model is defined by the following stochastic differential equations:
```
dF = α * F^β * dW₁
dα = v * α * dW₂
```
where:
- F is the forward price
- α is the volatility parameter
- β is the CEV (constant elasticity of variance) parameter
- v is the volatility of volatility
- ρ is the correlation between the two Brownian motions W₁ and W₂

### Understanding the Volatility Smile

The term "volatility smile" refers to the empirical pattern observed in options markets where implied volatilities vary across different strike prices for options with the same expiration date. This pattern typically forms a U-shaped or "smile" curve when plotted:

```
Implied
Volatility
    │     *        *
    │      *    *
    │       *  *
    │        *
    │
    └──────────────────
         Strike Price
```

Key aspects of the volatility smile:

1. **Market Reality vs. Black-Scholes**
   - The Black-Scholes model assumes constant volatility across all strikes
   - Real market data shows varying implied volatilities
   - Out-of-the-money puts and calls typically have higher implied volatilities

2. **Why it Matters**
   - Reflects market pricing of tail risks
   - Captures the skewness and kurtosis of returns
   - Essential for accurate options pricing and risk management

3. **SABR's Role**
   - SABR model was specifically designed to capture and model the volatility smile
   - Provides a mathematical framework to fit market-observed smiles
   - Allows for consistent pricing across different strikes and maturities

The SABR parameters affect the smile shape:
- β (beta): Controls the overall slope of the smile
- ρ (rho): Affects the asymmetry of the smile
- α (alpha): Influences the at-the-money volatility level
- v (nu): Impacts the curvature of the smile

### OpenBB Integration
[OpenBB](https://openbb.co/) is an open-source financial market data and analytics platform. In this project, we use OpenBB to:
- Fetch real-time options chain data for SPY (S&P 500 ETF)
- Extract implied volatilities and option prices
- Access historical price data for underlying analysis

## Features

1. **Market Data Retrieval**
   - Fetches options chain data for SPY
   - Extracts calls and puts data
   - Calculates mid prices and implied volatilities

2. **SABR Model Implementation**
   - Uses the Hagan 2002 lognormal SABR approximation
   - Calibrates SABR parameters to market data
   - Generates theoretical volatility curves

3. **Visualization**
   - Plots market implied volatility smile
   - Compares market vs. SABR model fits
   - Visual analysis of parameter sensitivity

## Dependencies

- pandas: Data manipulation and analysis
- numpy: Numerical computations
- matplotlib: Plotting and visualization
- pysabr: SABR model implementation
- openbb: Market data access
- yfinance: Additional market data provider

## Usage

The main script `py_sabr.py` performs the following operations:
1. Fetches current market data for SPY options
2. Filters options by expiration date
3. Calculates implied volatilities and mid prices
4. Fits the SABR model to market data
5. Generates comparison plots of market vs. model volatilities

## References

1. Hagan, P. S., Kumar, D., Lesniewski, A. S., & Woodward, D. E. (2002). Managing smile risk. Wilmott Magazine, 84-108.
2. OpenBB Documentation: [https://docs.openbb.co/](https://docs.openbb.co/)
3. SABR Model Documentation: [PySABR](https://github.com/ynouri/pysabr)
