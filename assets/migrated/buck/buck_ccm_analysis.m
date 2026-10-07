% Buck converter teaching example: ideal CCM, resistive load.
% Dr. Fulong Li -- first draft, September 2026.
% Requires MATLAB and Control System Toolbox.
% Numerical model independently checked; native MATLAB execution pending.
clear; clc;
Vg = 24; V = 12; Pout = 30; fs = 100e3;
L = 150e-6; C = 100e-6; R = V^2/Pout;
D = V/Vg; I = V/R;   % in a buck the inductor carries the load current
s = tf('s');
Delta = L*C*s^2 + (L/R)*s + 1;
Gvd = Vg/Delta;        % duty-to-output: constant numerator, no RHP zero
Gvg = D/Delta;         % line-to-output
Zo  = L*s/Delta;       % vo_hat = -Zo * extra_load_current_hat
f0 = 1/sqrt(L*C)/(2*pi);
Q  = R*sqrt(C/L);
fprintf('D=%.3f, I=%.3f A, f0=%.3f Hz, Q=%.3f\n',D,I,f0,Q);
fprintf('DC duty-to-output gain = %.3f V/duty\n',dcgain(Gvd));
fprintf('Resonant peak |Gvd(f0)| = %.1f (%.1f dB)\n', Vg*Q, 20*log10(Vg*Q));
figure; bode(Gvd); grid on; title('Ideal CCM duty-to-output plant (no RHP zero)');
% Small perturbations start from the physical equilibrium I, V.
deltaD = 0.005;
t = linspace(0,0.02,20001);
figure; step(deltaD*Gvd,t); grid on;
title('Output voltage perturbation for a +0.005 duty step (V)');
fprintf('Linear final delta V = %.6f V; exact = %.6f V\n', ...
    deltaD*dcgain(Gvd),(D+deltaD)*Vg-V);
% Intentionally slow voltage-mode baseline. Output reconstructed in volts;
% controller output in duty units: H = 1 and GPWM = 1. A pure PI must stay
% well below f0 because the lightly damped LC peak here is about 39 dB.
Kp = 8e-3; Ki = 8;
Gc = Kp+Ki/s;
T = Gc*Gvd;
disp('All nominal continuous-time loop margins:'); disp(allmargin(T));
CL = feedback(T,1);
disp('Nominal closed-loop poles:'); disp(pole(CL));
assert(isstable(CL),'Nominal continuous-time loop is unstable');
figure; margin(T); grid on;
title('Nominal PI loop: inspect allmargin for every crossing');
figure; step(0.1*CL,linspace(0,0.1,10001)); grid on;
title('Output perturbation for a 0.1 V reference step');
% A small added current sink in parallel with R, not a large resistor change.
Gload = minreal(-Zo/(1+T));
figure; step(0.05*Gload,linspace(0,0.1,10001)); grid on;
title('Output perturbation for a +0.05 A load-current step');
% Nominal sampled illustration: ZOH duty hold plus one full update delay.
% Actual ADC/PWM scheduling may differ; no saturation/anti-windup here.
Ta = 1/fs;
Gcd = c2d(Gc,Ta,'tustin');
Gpd = c2d(Gvd,Ta,'zoh');
z = tf('z',Ta);
Td = Gcd*Gpd/z;
disp('Sampled loop margins (assumed one-period update delay):');
disp(allmargin(Td));
disp('Sampled closed-loop stable:'); disp(isstable(feedback(Td,1)));
% Because there is no RHP zero, a Type III design can place crossover above
% f0 for far higher bandwidth. This script does not model DCM, startup,
% device losses, protection or physical ripple.
