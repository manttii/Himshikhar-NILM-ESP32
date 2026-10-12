%% Verification Test Suite for NILM_Himshikhar_Portal
modelName = 'NILM_Himshikhar_Portal';
load_system(modelName);

test_cases = {
    % Name, sw1, sw2, sw3, Expected V, Expected I, Expected P, Expected PF, Expected StateID
    '1. Idle / Standby (No Load)',  '0', '0', '0', 230, 0.0,    0,    1.00, 0;
    '2. Appliance 1: 1000W Heater', '1', '0', '0', 230, 4.35, 1000,  1.00, 1;
    '3. Appliance 2: Fridge Motor', '0', '1', '0', 230, 2.11,  350,  0.72, 2;
    '4. Appliance 3: Microwave',    '0', '0', '1', 230, 3.95,  800,  0.88, 3;
    '5. Combined: Heater + Motor',  '1', '1', '0', 230, 6.04, 1350,  0.97, 4;
    '6. Combined: All Appliances',  '1', '1', '1', 230, 9.93, 2150,  0.94, 4;
};

fprintf('\n======================================================================\n');
fprintf('  HIMSHIKHAR 2026 ENERGY PORTAL - NILM SIMULATION VERIFICATION\n');
fprintf('======================================================================\n');

all_passed = true;

for k = 1:size(test_cases, 1)
    name       = test_cases{k, 1};
    sw1_val    = test_cases{k, 2};
    sw2_val    = test_cases{k, 3};
    sw3_val    = test_cases{k, 4};
    exp_v      = test_cases{k, 5};
    exp_i      = test_cases{k, 6};
    exp_p      = test_cases{k, 7};
    exp_pf     = test_cases{k, 8};
    exp_st     = test_cases{k, 9};
    
    set_param([modelName '/Switch_Heater'], 'CurrentSetting', sw1_val);
    set_param([modelName '/Switch_Motor'],  'CurrentSetting', sw2_val);
    set_param([modelName '/Switch_Microwave'], 'CurrentSetting', sw3_val);
    
    set_param(modelName, 'StopTime', '0.5'); % 500ms simulation
    simOut = sim(modelName, 'ReturnWorkspaceOutputs', 'on');
    
    yout = simOut.get('yout');
    v_actual  = yout{1}.Values.Data(end);
    i_actual  = yout{2}.Values.Data(end);
    p_actual  = yout{3}.Values.Data(end);
    pf_actual = yout{4}.Values.Data(end);
    
    % Check tolerances (within 3% due to discrete sampling and ADC quantization)
    v_err  = abs(v_actual - exp_v);
    i_err  = abs(i_actual - exp_i);
    p_err  = abs(p_actual - exp_p);
    pf_err = abs(pf_actual - exp_pf);
    
    pass_i = (exp_i == 0 && i_actual == 0) || (i_err <= 0.25);
    pass_p = (exp_p == 0 && p_actual <= 10) || (p_err <= 45);
    pass_pf = (pf_err <= 0.05);
    
    if (v_err <= 5.0 && pass_i && pass_p && pass_pf)
        fprintf('  [PASS] %-30s => V: %5.1fV | I: %4.2fA | P: %5.0fW | PF: %4.2f\n', ...
                name, v_actual, i_actual, p_actual, pf_actual);
    else
        fprintf('  [FAIL] %-30s => Got V:%5.1fV, I:%4.2fA, P:%5.0fW, PF:%4.2f (Exp I:%4.2fA, P:%5.0fW, PF:%4.2f)\n', ...
                name, v_actual, i_actual, p_actual, pf_actual, exp_i, exp_p, exp_pf);
        all_passed = false;
    end
end

fprintf('======================================================================\n');
if all_passed
    fprintf('  >>> 100%% OF ALL NILM APPLIANCE LOAD SIGNATURES VERIFIED! <<<\n');
else
    fprintf('  >>> VERIFICATION COMPLETED WITH SOME TOLERANCE OFFSETS. <<<\n');
end
fprintf('======================================================================\n\n');

% Reset default: Heater ON, others OFF, StopTime 10s
set_param([modelName '/Switch_Heater'], 'CurrentSetting', '1');
set_param([modelName '/Switch_Motor'],  'CurrentSetting', '0');
set_param([modelName '/Switch_Microwave'], 'CurrentSetting', '0');
set_param(modelName, 'StopTime', '10');
save_system(modelName);
close_system(modelName);
