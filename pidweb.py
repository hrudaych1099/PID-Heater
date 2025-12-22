import streamlit as st
import matplotlib.pyplot as plt
class PIDController:
    def __init__(self, Kp, Ki, Kd, dt):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.dt = dt
        self.integral_sum = 0.0
        self.last_error = 0.0

    def update(self, target, current_temp):
        error = target - current_temp
        P_term = self.Kp * error
        self.integral_sum += error * self.dt
        
        # Anti-windup
        limit = 2000.0 / self.Ki if self.Ki != 0 else 0
        if self.integral_sum > limit: self.integral_sum = limit
        if self.integral_sum < -limit: self.integral_sum = -limit
        I_term = self.Ki * self.integral_sum

        derivative = (error - self.last_error) / self.dt
        D_term = self.Kd * derivative
        self.last_error = error
        
        output = P_term + I_term + D_term
        return output
def settlingtime(time_history,temp_history, target, tolerance=0.5):
    if abs(temp_history[-1]- target) > tolerance:
        return None
    settling_index = len(temp_history) - 1
    for i in range(len(temp_history) - 1, -1, -1):
        if abs(temp_history[i] - target) > tolerance:
            settling_index = i + 1
            break
    return time_history[settling_index]
def get_rate_of_change(T, power, T_ambient, R_insul, C_heat):
    loss = (T - T_ambient) / R_insul
    dT_dt = (power - loss) / C_heat
    return dT_dt
    
#web interface
st.set_page_config(page_title="Smart Heater Simulator", layout="wide", page_icon="🔧")
st.title("PID vs. Thermostat - By Hruday")
st.markdown("""
**Engineering Project** | **Simulating Thermal Dynamics & Control Systems**
""")
st.markdown("""
**→ Configure Simulation Parameters in the Sidebar 🔧**
""")
st.markdown("""
→ This app simulates the energy efficiency difference between a standard On/Off Hater uhm-uhm (Heater) 
and a Smart PID Control Algorithm.
""")
st.markdown("""
P.S:- We shall use a basic 2kw Heater for this project, so don't input huge volumes required to heat an entire house :)
""")

#sidebar
with st.sidebar:
    st.header("⚙️ Simulation Parameters")
    
    st.subheader("Room Physics")
    #Users can pick room size
    room_type = st.selectbox("Room Size", ["Small Bedroom", "Large Hall", "Custom"], help="Choose Custom for accurate readings")
    if room_type == "Small Bedroom":
        C_heat = 40000.0
    elif room_type == "Large Hall":
        C_heat = 100000.0
    else:
        Volume = st.number_input("Volume of Room (m³)", 0, 1000, 10)
        mass = Volume*1.225
        C_heat = mass*1005
    st.markdown(f"**Thermal Mass (C):** `{C_heat:,.0f} J/K`", help="Energy required to raise room temp by 1°C")
    Thickness = st.number_input("Thickness of Wall (cm)", 0.0, 1000.0, 20.0, help="Assuming Uniform Thickness across the Room")
    walltype = st.selectbox("Wall Type", ["Burnt Clay Bricks", "Cement Bricks", "Custom"], help ="Choose Burnt Clay if it's those classic red bricks which were used :)")
    if walltype == "Burnt Clay Bricks":
        R_thermal = 0.5
    elif walltype == "Cement Bricks":
        R_thermal = 0.08
    else:
        R_thermal = st.number_input("Thermal Resistance/cm",0.0,10.0,0.1)

    R_insul = R_thermal*Thickness
    st.markdown(f"**Thermal Resistance(R):** `{R_insul:.2f} K/W`")
    T_ambient = st.number_input("Outside Temperature (°C)", -10.0, 20.0, 10.0)
    hours = st.number_input("Hours Run on Heater",0.0,24.0,6.0)
    time = st.slider("Time Steps (dt) seconds", 0.5,10.0,5.0, help="Lower Time Steps = Higher Simulation Times")
    cost_per_kwh = st.number_input("Electricity Cost (₹/kWh)", 0.0, 100.0, 10.0)
    st.write("---")
    st.subheader("Thermostat Settings")
    target_pid = st.slider("Your Desired Temperature °C", 18.0, 30.0, 25.0) 
    
    # set thermostat higher
    target_dumb = st.slider("Thermostat Setting °C", 18.0, 32.0, 28.0, help="Set higher to compensate for swings")
    st.write("---")
    st.subheader("PID Tuning (Advanced)")
    Kp = st.number_input("Kp (Proportional)", 80.0, 1000.0, 100.0)
    Ki = st.number_input("Ki (Integral)", 0.0001, 0.01, 0.001, format="%.4f")
    Kd = st.number_input("Kd (Derivative)", 10000.0, 50000.0, 35000.0)

#simulation
if st.button("🚀 Run Simulation", type="primary"):
    
    # Constants
    dt = time
    sim_hours = hours
    steps = int(3600 * sim_hours / dt)
    max_power = 2000.0
    hysteresis = 1.5


    #Initialization
    pid = PIDController(Kp, Ki, Kd, dt)
    T_pid, T_dumb = T_ambient, T_ambient
    energy_pid, energy_dumb = 0.0, 0.0
    dumb_on = False
    
    #store data in lists
    history_time = []
    history_pid = []
    history_dumb = []

    #progress
    progress_bar = st.progress(0)
    for i in range(steps):
        p_pid = pid.update(target_pid, T_pid)
        p_pid = max(0, min(max_power, p_pid))
        #rk4 physics
        k1 = get_rate_of_change(T_pid, p_pid, T_ambient, R_insul, C_heat)
        k2 = get_rate_of_change(T_pid + 0.5*dt*k1, p_pid, T_ambient, R_insul, C_heat)
        k3 = get_rate_of_change(T_pid + 0.5*dt*k2, p_pid, T_ambient, R_insul, C_heat)
        k4 = get_rate_of_change(T_pid + dt*k3, p_pid, T_ambient, R_insul, C_heat)
        T_pid += (dt / 6.0) * (k1 + 2*k2 + 2*k3 + k4)
        energy_pid += p_pid * dt
        if T_dumb < (target_dumb - hysteresis):
            dumb_on = True
        elif T_dumb > (target_dumb + hysteresis):
            dumb_on = False
        
        p_dumb = max_power if dumb_on else 0.0
        k1 = get_rate_of_change(T_dumb, p_dumb, T_ambient, R_insul, C_heat)
        k2 = get_rate_of_change(T_dumb + 0.5*dt*k1, p_dumb, T_ambient, R_insul, C_heat)
        k3 = get_rate_of_change(T_dumb + 0.5*dt*k2, p_dumb, T_ambient, R_insul, C_heat)
        k4 = get_rate_of_change(T_dumb + dt*k3, p_dumb, T_ambient, R_insul, C_heat)
        T_dumb += (dt / 6.0) * (k1 + 2*k2 + 2*k3 + k4)
        energy_dumb += p_dumb * dt
        
        #storing data
        if i % 60 == 0: # Save every minute
            history_time.append(i/60)
            history_pid.append(T_pid)
            history_dumb.append(T_dumb)
        
        if i % (steps // 10) == 0:
            progress_bar.progress(i / steps)
            
    progress_bar.progress(100)
    settling_time = settlingtime(history_time, history_pid, target_pid, tolerance=0.5)

    #results
    kwh_pid = energy_pid / 3600000
    kwh_dumb = energy_dumb / 3600000
    savings = ((kwh_dumb - kwh_pid) / kwh_dumb) * 100

    #metrics

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Free-Use Heater Usage", f"{kwh_dumb:.2f} kWh")
    col2.metric("Smart PID Usage", f"{kwh_pid:.2f} kWh")
    if savings > 0:
        col3.metric("Energy Savings", f"{savings:.1f} %", delta=f"{savings:.1f} %", delta_color="normal") 
    else:
        col3.metric("Energy Savings", f"{savings:.1f} %", delta=f"{savings:.1f} %", delta_color="off") 
    if settling_time:
        col4.metric("Settling Time", f"{settling_time:.0f} mins", help="Time to stabilize within 0.1°C of Target Temperature")
    else:
        col4.metric("Settling Time", "Not Settled", help="System never stabilized within tolerance")
    #plot
    fig, ax = plt.subplots(figsize=(10, 5))
    fig.patch.set_alpha(0.0)
    ax.patch.set_alpha(0.0)
    ax.spines['bottom'].set_color('#403f3f')
    ax.spines['top'].set_color('#403f3f') 
    ax.spines['right'].set_color('#403f3f')
    ax.spines['left'].set_color('#403f3f')
    ax.tick_params(axis='x', colors='#403f3f')
    ax.tick_params(axis='y', colors='#403f3f')
    ax.yaxis.label.set_color('#403f3f')
    ax.xaxis.label.set_color('#403f3f')
    ax.title.set_color('#403f3f')

    ax.plot(history_time, history_dumb, 'r--', label=f'Normal Thermostat (Set {target_dumb}°C)', alpha=0.7) # Increased alpha for visibility
    ax.plot(history_time, history_pid, 'c-', label=f'Smart PID (Set {target_pid}°C)', linewidth=2) # Cyan is better than Blue on dark backgrounds
    ax.axhline(y=target_pid, color='g', linestyle=':', label='Comfort Zone')
    ax.set_xlabel('Time (Minutes)')
    ax.set_ylabel('Temperature (°C)')
    ax.legend(facecolor='#b9b9b9', labelcolor='white')
    ax.grid(True, alpha=0.3)
    money_saved = (kwh_dumb - kwh_pid) * cost_per_kwh * (30 * 24 / sim_hours) #for 1 month
    
    st.pyplot(fig)
    
    
    if savings > 0:
        st.success(f"✅ Success! The PID controller maintained comfort while using **{savings:.1f}% less energy**.")
    else:
        st.warning("⚠️ The PID used more energy. This usually happens if the Dumb thermostat target is set too low (causing discomfort).")
    if money_saved > 0:

        st.info(f"💰 At this rate, you would save ₹**{money_saved:.2f} per month**.")











