<div align="center">
  <h1 align="center">PID Heater</h1>
  <div align="center">
  <a href="https://pid-dumb.streamlit.app">pid-dumb.streamlit.app</a>
  </div>

🔧 A small project where we can see a difference in conserving energy and maintaining a particular temperature on a heater using a PID Device rather than using the conventional switch-on/off method.
</div>

## Features

- **Customise Multiple Features:** From your room size, wall thickness, to the type of wall present in your home, for the perfect simulations which match real-time properties 
- **Custom Tuning:** Tune the PID from the Advanced Tuning Sidebar to get better (or maybe worse) results.
- **Analytics:** You will be able to check the % Energy Saved, amount saved per month and also the time taken for the PID Simulated Heater to attain comfort temperature!

## Demo

![GIF](https://github.com/hrudaych1099/PID-Heater/blob/main/PID-videoeditedbetter%20(1).gif)

## Physics Behind Model

The simulation models a standard room using 4th Order Runge-Kutta (RK4) over discrete time steps ($dt$).
 - Using a physics-based Python simulation, we modelled a thermal system with Newton’s Law of Cooling. The results demonstrate that while traditional thermostats suffer from "comfort drift" and overshoot, a tuned PID controller maintains target temperature with zero steady-state error. Furthermore, when normalized for comfort (minimum service level), the PID controller achieved upto 25% reduction in energy consumption compared to the hysteresis-based approach.

## Governing Equations
 - Heat Loss: Modeled via Newton's Law of Cooling:
$$Q_{loss} = \frac{T_{room} - T_{ambient}}{R_{thermal}}$$
Where $R_{thermal}$ is calculated based on wall thickness and material properties (e.g., Burnt Clay Bricks, $R \approx 0.5$).
 - Thermal Inertia:
$$T_{new} = T_{old} + \frac{Q_{net}}{C_{heat}} \cdot dt$$
Where $C_{heat}$ (Heat Capacity or Thermal Mass) is derived from air density ($\rho = 1.225 kg/m^3$) and specific heat capacity ($c_p = 1005 J/kg\cdot K$).
 - PID Controller: Calculates power output continuously:
$$P(t) = K_p e(t) + K_i \int e(t) dt + K_d \frac{de(t)}{dt}$$

## Conclusion 
 - The simulation proves that the inefficiency of mechanical thermostats comes not from the hardware, but from the human compensation required to deal with inaccuracy. By using PID control, we eliminate the need for the "safety buffer," allowing the system to run at the true desired temperature. This results in significant cost savings without sacrificing comfort.

## Future Scope 
 - Hardware Implementation: Deploying this code on an Arduino/ESP32 with a solid-state relay.

 - Weather Compensation: Adding a "Feed-Forward" term to the PID loop based on outdoor weather forecasts.
