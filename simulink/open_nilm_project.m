%% Runner script to open the NILM Energy Meter simulation in Simulink
% Project: Himshikhar 2026 Energy Portal - ESP32 NILM Energy Meter & Load Simulator
% Author:  Manit Sharma (Roll No: 36)

clear; clc;
modelName = 'NILM_Himshikhar_Portal';

fprintf('Opening %s in Simulink...\n', modelName);
open_system(modelName);
fprintf('Model opened successfully!\n');
fprintf('👉 Click the green "Run" button to start real-time telemetry.\n');
fprintf('👉 Double-click any "Switch" (Heater, Motor, Microwave) to toggle appliances live!\n');
fprintf('👉 Double-click "Live_Vector_Oscilloscope" to see the live voltage-current waveforms and phase shift.\n');
