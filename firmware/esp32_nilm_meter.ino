/*
 * =====================================================================================
 * Project: Himshikhar 2026 Energy Portal - ESP32 NILM Energy Meter Firmware
 * Author:  Manit Sharma (Roll No: 36) | Graphic Era Deemed to be University, Dehradun
 * Hardware Target: ESP32-WROOM-32 DevKit
 * Sensors: ZMPT101B Active AC Voltage Transformer (Pin 34)
 *          SCT-013 Current Transformer Clamp with Midpoint Voltage Divider (Pin 35)
 * Status:  Production C++ Firmware with Dynamic DC Bias Tracking & Edge NILM Classifier
 * =====================================================================================
 *
 * ARCHITECTURAL HIGHLIGHTS:
 * 1. Dynamic DC Midpoint Auto-Calibration & Tracking:
 *    Solves the ~3.5A phantom current bug caused by static 1760-count ADC offset drift.
 *    Initializes resting DC bias during boot and dynamically tracks baseline drift using
 *    an integer-cycle window mean (5 full cycles at 50 Hz = 100ms lock window).
 * 2. 100ms Temporal Waveform Lock:
 *    Synchronous discrete integration over exactly 5 AC cycles (50 Hz mains).
 * 3. Discrete Integration:
 *    True RMS calculation for Voltage and Current, Real Power (instantaneous V * I product),
 *    Apparent Power (V_rms * I_rms), Power Factor (cos theta), and Phase Angle (theta).
 * 4. Edge NILM Appliance Disaggregation:
 *    On-chip heuristic classifier detecting pure resistive (Heater), inductive (Motor),
 *    and complex reactive (Microwave) appliance signatures.
 * 5. Wi-Fi SoftAP Provisioning & Preferences:
 *    Fallback to 'Himshikhar_Config' AP if credentials missing or connection fails.
 * 6. Responsive Dark-Mode Telemetry Portal (Chart.js) + JSON REST API (/api/data).
 * =====================================================================================
 */

#include <WiFi.h>
#include <WebServer.h>
#include <Preferences.h>
#include <math.h>

// -------------------------------------------------------------------------------------
// Pin Definitions
// -------------------------------------------------------------------------------------
const int VOLTAGE_PIN = 34; // ZMPT101B analog output (ADC1_CH6)
const int CURRENT_PIN = 35; // SCT-013 biased analog output (ADC1_CH7)
const int LED_PIN     = 2;  // Onboard status LED

// -------------------------------------------------------------------------------------
// Calibration Constants
// -------------------------------------------------------------------------------------
// VOLTAGE_CAL: Derived from ZMPT101B multi-turn trimpot divider gain to map 230V RMS mains.
// CURRENT_CAL: Derived from SCT-013 (100A/50mA) with burden resistor (100.0 A per Volt RMS).
const float VOLTAGE_CAL = 883.58f;
const float CURRENT_CAL = 100.00f;

// -------------------------------------------------------------------------------------
// Dynamic DC Bias Midpoint Tracking
// -------------------------------------------------------------------------------------
// Initial baseline fallback (nominal ~1.65V on 3.3V reference = ~1760 to ~2048 counts)
float voltage_offset = 1760.0f;
float current_offset = 1760.0f;
bool calibration_locked = false;

// -------------------------------------------------------------------------------------
// Global Electrical Telemetry Variables
// -------------------------------------------------------------------------------------
float V_rms            = 0.0f;
float I_rms            = 0.0f;
float real_power       = 0.0f;
float apparent_power   = 0.0f;
float power_factor     = 1.0f;
float phase_difference = 0.0f;
bool  ct_reversed      = false;
String appliance_name  = "Standby / Idle";
int appliance_code     = 0;

// Web Server & Storage
WebServer server(80);
Preferences preferences;

// Runtime Flags & Timers
bool apMode = false;
unsigned long previousLedMillis    = 0;
unsigned long previousSerialMillis = 0;
int ledState = LOW;

// -------------------------------------------------------------------------------------
// Edge NILM Appliance Disaggregation Classifier
// -------------------------------------------------------------------------------------
void classifyAppliance() {
  float active_p = fabsf(real_power);
  if (I_rms < 0.40f || active_p < 30.0f) {
    appliance_code = 0;
    appliance_name = "Standby / Idle";
  } else if (active_p >= 850.0f && active_p <= 1150.0f && power_factor >= 0.96f) {
    appliance_code = 1;
    appliance_name = "Appliance 1: Water Heater (1000W, PF 1.00)";
  } else if (active_p >= 250.0f && active_p <= 450.0f && power_factor >= 0.65f && power_factor <= 0.78f) {
    appliance_code = 2;
    appliance_name = "Appliance 2: Refrigerator Motor (350W, PF 0.72 lag)";
  } else if (active_p >= 700.0f && active_p <= 950.0f && power_factor >= 0.82f && power_factor <= 0.92f) {
    appliance_code = 3;
    appliance_name = "Appliance 3: Microwave Oven (800W, PF 0.88 lag)";
  } else if (active_p > 1150.0f) {
    appliance_code = 4;
    appliance_name = "Combined Multi-Appliance Load";
  } else {
    appliance_code = 5;
    appliance_name = "Active Unclassified Load";
  }
}

// -------------------------------------------------------------------------------------
// Auto-Calibration Routine for DC Bias Midpoint (Integer-Cycle Synchronous)
// -------------------------------------------------------------------------------------
void autoCalibrateMidpoints() {
  Serial.println("[Calibration] Auto-tuning DC bias midpoints (10 integer cycles / 200ms lock)...");
  uint64_t sum_v_cal = 0;
  uint64_t sum_i_cal = 0;
  uint32_t cal_samples = 0;

  unsigned long start_cal = micros();
  // 200ms lock: exactly 10 full cycles at 50 Hz (200,000 microseconds)
  // Guarantees any AC voltage/current component integrates to exactly zero (sin(20*pi) = 0)
  while (micros() - start_cal < 200000) {
    sum_v_cal += analogRead(VOLTAGE_PIN);
    sum_i_cal += analogRead(CURRENT_PIN);
    cal_samples++;
    delayMicroseconds(40); // Controlled rate ~15 kHz to prevent bus contention
  }

  if (cal_samples > 0) {
    voltage_offset = (float)sum_v_cal / (float)cal_samples;
    current_offset = (float)sum_i_cal / (float)cal_samples;
    calibration_locked = true;
  }

  Serial.printf("[Calibration] Locked (%u samples)! V_offset = %6.2f counts | I_offset = %6.2f counts\n",
                cal_samples, voltage_offset, current_offset);
}

// -------------------------------------------------------------------------------------
// Signal Capture & Discrete RMS / Power Integration (100ms Temporal Lock)
// -------------------------------------------------------------------------------------
void captureAndCalculate() {
  double   sum_V_squared   = 0.0;
  double   sum_I_squared   = 0.0;
  double   sum_inst_power  = 0.0;
  uint64_t sum_raw_V       = 0;
  uint64_t sum_raw_I       = 0;
  int sample_count         = 0;

  unsigned long start_time = micros();

  // 100ms temporal lock: exactly 5 full cycles at 50 Hz (100,000 microseconds)
  while (micros() - start_time < 100000) {
    int sample_V = analogRead(VOLTAGE_PIN);
    int sample_I = analogRead(CURRENT_PIN);

    sum_raw_V += sample_V;
    sum_raw_I += sample_I;

    double inst_V = (double)sample_V - (double)voltage_offset;
    double inst_I = (double)sample_I - (double)current_offset;

    sum_V_squared  += inst_V * inst_V;
    sum_I_squared  += inst_I * inst_I;
    sum_inst_power += inst_V * inst_I;
    sample_count++;
  }

  if (sample_count == 0) return;

  // ---------------------------------------------------------------------------------
  // Dynamic Midpoint Tracking (EMA)
  // Because 100ms contains exactly 5 full AC cycles, the AC component integrates to 0.
  // The algebraic mean over the window is the exact hardware DC operating bias.
  // We apply an exponential filter (alpha = 0.05) to track thermal and rail drift.
  // ---------------------------------------------------------------------------------
  float window_mean_V = (float)sum_raw_V / (float)sample_count;
  float window_mean_I = (float)sum_raw_I / (float)sample_count;
  voltage_offset = (voltage_offset * 0.95f) + (window_mean_V * 0.05f);
  current_offset = (current_offset * 0.95f) + (window_mean_I * 0.05f);

  // ---------------------------------------------------------------------------------
  // Discrete RMS Integration (Double-Precision Accumulation)
  // ---------------------------------------------------------------------------------
  V_rms = (float)(sqrt(sum_V_squared / (double)sample_count) * (3.3 / 4095.0) * (double)VOLTAGE_CAL);
  I_rms = (float)(sqrt(sum_I_squared / (double)sample_count) * (3.3 / 4095.0) * (double)CURRENT_CAL);

  // Hardware Noise Gates (eliminate residual ADC thermal noise floor)
  if (I_rms < 0.25f) {
    I_rms = 0.0f;
  }
  if (V_rms < 12.0f) {
    V_rms = 0.0f;
  }

  // ---------------------------------------------------------------------------------
  // Power & Phase Angle Calculations
  // ---------------------------------------------------------------------------------
  real_power = (float)((sum_inst_power / (double)sample_count) *
                       (3.3 / 4095.0) * (3.3 / 4095.0) *
                       (double)VOLTAGE_CAL * (double)CURRENT_CAL);

  apparent_power = V_rms * I_rms;

  // Detect and handle reverse CT clamp installation orientation
  ct_reversed = (real_power < -15.0f && apparent_power > 25.0f);
  float active_p_mag = fabsf(real_power);

  if (I_rms == 0.0f || V_rms == 0.0f) {
    real_power       = 0.0f;
    apparent_power   = 0.0f;
    power_factor     = 1.0f;
    phase_difference = 0.0f;
  } else if (apparent_power > 5.0f) {
    power_factor = active_p_mag / apparent_power;
    if (power_factor > 1.0f) power_factor = 1.0f;
    if (power_factor < 0.0f) power_factor = 0.0f;
    phase_difference = acos(power_factor) * (180.0f / (float)M_PI);
  } else {
    power_factor     = 1.0f;
    phase_difference = 0.0f;
  }

  // Run NILM Disaggregation
  classifyAppliance();
}

// -------------------------------------------------------------------------------------
// Web Portal: Telemetry Dashboard (Chart.js)
// -------------------------------------------------------------------------------------
void handleTelemetryRoot() {
  String html = "<!DOCTYPE html><html><head><meta charset='UTF-8'><meta name='viewport' content='width=device-width, initial-scale=1'>";
  html += "<title>Himshikhar 2026 Energy Portal</title>";
  html += "<script src='https://cdn.jsdelivr.net/npm/chart.js'></script>";
  html += "<style>";
  html += "body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; margin: 0; padding: 24px; background: #0d1117; color: #c9d1d9; }";
  html += ".header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #30363d; padding-bottom: 16px; margin-bottom: 24px; }";
  html += "h1 { margin: 0; color: #58a6ff; font-size: 26px; }";
  html += ".badge { background: #238636; color: #fff; padding: 4px 12px; border-radius: 12px; font-size: 13px; font-weight: 600; }";
  html += ".grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 16px; margin-bottom: 24px; }";
  html += ".card { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 18px; box-shadow: 0 4px 12px rgba(0,0,0,0.3); }";
  html += ".card h3 { margin: 0 0 8px 0; font-size: 13px; text-transform: uppercase; letter-spacing: 0.08em; color: #8b949e; }";
  html += ".value { font-size: 28px; font-weight: 700; color: #58a6ff; }";
  html += ".unit { font-size: 16px; color: #8b949e; font-weight: normal; margin-left: 4px; }";
  html += ".appliance-card { background: #1f242c; border-left: 4px solid #f778ba; }";
  html += ".chart-card { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 20px; }";
  html += ".footer { margin-top: 24px; font-size: 12px; color: #8b949e; text-align: center; }";
  html += "</style></head><body>";

  html += "<div class='header'>";
  html += "  <div><h1>Himshikhar 2026 Energy Portal</h1><small>ESP32 Edge NILM Disaggregation | Graphic Era University</small></div>";
  html += "  <div class='badge'>LIVE 50Hz TELEMETRY</div>";
  html += "</div>";

  html += "<div class='grid'>";
  html += "  <div class='card'><h3>Voltage Node</h3><div class='value' id='val-v'>" + String(V_rms, 1) + "<span class='unit'>V RMS</span></div></div>";
  html += "  <div class='card'><h3>Current Node</h3><div class='value' id='val-i' style='color:#f778ba;'>" + String(I_rms, 2) + "<span class='unit'>A RMS</span></div></div>";
  html += "  <div class='card'><h3>Real Power (P)</h3><div class='value' id='val-p' style='color:#7ee787;'>" + String(real_power, 1) + "<span class='unit'>W</span></div></div>";
  html += "  <div class='card'><h3>Apparent Power (S)</h3><div class='value' id='val-s' style='color:#d2a8ff;'>" + String(apparent_power, 1) + "<span class='unit'>VA</span></div></div>";
  html += "  <div class='card'><h3>Power Factor (PF)</h3><div class='value' id='val-pf' style='color:#ffa657;'>" + String(power_factor, 2) + "</div></div>";
  html += "  <div class='card'><h3>Phase Angle (&theta;)</h3><div class='value' id='val-deg' style='color:#ff7b72;'>" + String(phase_difference, 1) + "<span class='unit'>&deg;</span></div></div>";
  html += "</div>";

  html += "<div class='grid'>";
  html += "  <div class='card appliance-card' style='grid-column: 1 / -1;'>";
  html += "    <h3>Active NILM Classification</h3>";
  html += "    <div class='value' id='val-app' style='font-size:20px; color:#58a6ff;'>" + appliance_name + "</div>";
  html += "    <small id='val-dc' style='color:#8b949e;'>Dynamic Midpoint Offsets: V_DC = " + String(voltage_offset, 1) + " | I_DC = " + String(current_offset, 1) + " counts (Phantom Amps Resolved)</small>";
  html += "  </div>";
  html += "</div>";

  html += "<div class='chart-card'>";
  html += "  <h3>Live Vector Telemetry Visualizer</h3>";
  html += "  <canvas id='telemetryChart' height='100'></canvas>";
  html += "</div>";

  html += "<div class='footer'>Author: Manit Sharma | GitHub: @manttii | B.Tech ECE 3rd Sem</div>";

  html += "<script>";
  html += "let chart = null;";
  html += "try {";
  html += "  const ctx = document.getElementById('telemetryChart').getContext('2d');";
  html += "  chart = new Chart(ctx, {";
  html += "    type: 'bar',";
  html += "    data: {";
  html += "      labels: ['Voltage (V)', 'Current (A * 20)', 'Real Power (W / 10)', 'Apparent Power (VA / 10)', 'Phase Angle (deg)'],";
  html += "      datasets: [{";
  html += "        label: 'Edge Metrics',";
  html += "        data: [" + String(V_rms, 1) + ", " + String(I_rms * 20.0f, 1) + ", " + String(real_power / 10.0f, 1) + ", " + String(apparent_power / 10.0f, 1) + ", " + String(phase_difference, 1) + "],";
  html += "        backgroundColor: ['#58a6ff', '#f778ba', '#7ee787', '#d2a8ff', '#ff7b72'],";
  html += "        borderRadius: 6";
  html += "      }]";
  html += "    },";
  html += "    options: { responsive: true, animation: false, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, grid: { color: '#30363d' } }, x: { grid: { display: false } } } }";
  html += "  });";
  html += "} catch (e) { console.warn('Chart.js offline or loading deferred', e); }";
  html += "async function updateTelemetry() {";
  html += "  try {";
  html += "    const res = await fetch('/api/data');";
  html += "    if (!res.ok) return;";
  html += "    const d = await res.json();";
  html += "    document.getElementById('val-v').innerHTML = d.voltage_rms.toFixed(1) + \"<span class='unit'>V RMS</span>\";";
  html += "    document.getElementById('val-i').innerHTML = d.current_rms.toFixed(2) + \"<span class='unit'>A RMS</span>\";";
  html += "    document.getElementById('val-p').innerHTML = d.real_power.toFixed(1) + \"<span class='unit'>W</span>\";";
  html += "    document.getElementById('val-s').innerHTML = d.apparent_power.toFixed(1) + \"<span class='unit'>VA</span>\";";
  html += "    document.getElementById('val-pf').innerText = d.power_factor.toFixed(2);";
  html += "    document.getElementById('val-deg').innerHTML = d.phase_angle.toFixed(1) + \"<span class='unit'>&deg;</span>\";";
  html += "    document.getElementById('val-app').innerText = d.appliance_name;";
  html += "    document.getElementById('val-dc').innerText = 'Dynamic Midpoint Offsets: V_DC = ' + d.dc_offset_voltage.toFixed(1) + ' | I_DC = ' + d.dc_offset_current.toFixed(1) + ' counts' + (d.ct_reversed ? ' | [CT Polarity Auto-Corrected]' : ' (Phantom Amps Resolved)');";
  html += "    if (chart) {";
  html += "      chart.data.datasets[0].data = [d.voltage_rms, d.current_rms * 20.0, d.real_power / 10.0, d.apparent_power / 10.0, d.phase_angle];";
  html += "      chart.update('none');";
  html += "    }";
  html += "  } catch (e) { console.error('Telemetry fetch error', e); }";
  html += "}";
  html += "setInterval(updateTelemetry, 1500);";
  html += "</script>";

  html += "</body></html>";
  server.send(200, "text/html", html);
}

// -------------------------------------------------------------------------------------
// Web API: JSON Telemetry Endpoint (/api/data)
// -------------------------------------------------------------------------------------
void handleApiData() {
  server.sendHeader("Access-Control-Allow-Origin", "*");
  String json = "{";
  json += "\"voltage_rms\":" + String(V_rms, 2) + ",";
  json += "\"current_rms\":" + String(I_rms, 2) + ",";
  json += "\"real_power\":" + String(real_power, 2) + ",";
  json += "\"apparent_power\":" + String(apparent_power, 2) + ",";
  json += "\"power_factor\":" + String(power_factor, 2) + ",";
  json += "\"phase_angle\":" + String(phase_difference, 2) + ",";
  json += "\"appliance_code\":" + String(appliance_code) + ",";
  json += "\"appliance_name\":\"" + appliance_name + "\",";
  json += "\"dc_offset_voltage\":" + String(voltage_offset, 2) + ",";
  json += "\"dc_offset_current\":" + String(current_offset, 2) + ",";
  json += "\"ct_reversed\":" + String(ct_reversed ? "true" : "false");
  json += "}";
  server.send(200, "application/json", json);
}

// -------------------------------------------------------------------------------------
// Web Portal: Wi-Fi Provisioning Setup Mode
// -------------------------------------------------------------------------------------
void handleConfigRoot() {
  int n = WiFi.scanNetworks();

  String html = "<!DOCTYPE html><html><head><meta name='viewport' content='width=device-width, initial-scale=1'>";
  html += "<style>body{font-family:sans-serif;margin:30px;background:#121212;color:#ffffff;}";
  html += ".card{background:#1e1e1e;padding:24px;border-radius:8px;max-width:400px;margin:auto;box-shadow:0 4px 16px rgba(0,0,0,0.4);}";
  html += "input, select{width:100%;padding:12px;margin:10px 0;box-sizing:border-box;border-radius:4px;border:1px solid #333;background:#2a2a2a;color:#fff;}";
  html += "button{width:100%;padding:14px;background:#58a6ff;color:#121212;font-weight:bold;border:none;border-radius:4px;cursor:pointer;}";
  html += "button:hover{background:#79b8ff;}</style></head><body>";

  html += "<div class='card'><h2>Himshikhar Wi-Fi Setup</h2><p style='color:#8b949e;font-size:14px;'>Configure local network credentials for ESP32 telemetry.</p>";
  html += "<form action='/save' method='POST'>";
  html += "<label>Select Network:</label><select name='ssid'>";

  if (n == 0) {
    html += "<option value=''>No networks detected</option>";
  } else {
    for (int i = 0; i < n; ++i) {
      html += "<option value='" + WiFi.SSID(i) + "'>" + WiFi.SSID(i) + " (" + String(WiFi.RSSI(i)) + " dBm)</option>";
    }
  }

  html += "</select>";
  html += "<label>Password:</label><input type='password' name='pass' placeholder='Wi-Fi Password'>";
  html += "<button type='submit'>Save Credentials & Connect</button>";
  html += "</form></div></body></html>";

  server.send(200, "text/html", html);
}

void handleConfigSave() {
  if (server.hasArg("ssid") && server.hasArg("pass")) {
    String newSSID = server.arg("ssid");
    String newPass = server.arg("pass");

    preferences.putString("ssid", newSSID);
    preferences.putString("pass", newPass);

    String html = "<!DOCTYPE html><html><head><meta name='viewport' content='width=device-width, initial-scale=1'>";
    html += "<style>body{font-family:sans-serif;background:#121212;color:#58a6ff;text-align:center;margin-top:60px;}</style></head><body>";
    html += "<h2>Credentials Saved!</h2><p>ESP32 is restarting and associating with <b>" + newSSID + "</b>.</p>";
    html += "<p>Reconnect your device to your local Wi-Fi router to view the portal.</p></body></html>";

    server.send(200, "text/html", html);
    delay(2000);
    ESP.restart();
  } else {
    server.send(400, "text/plain", "Missing SSID or Password");
  }
}

// -------------------------------------------------------------------------------------
// Setup Routine
// -------------------------------------------------------------------------------------
void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);
  pinMode(VOLTAGE_PIN, INPUT);
  pinMode(CURRENT_PIN, INPUT);
  delay(1000);

  Serial.println("\n=======================================================");
  Serial.println("  HIMSHIKHAR 2026 ENERGY PORTAL - ESP32 NILM METER");
  Serial.println("  Author: Manit Sharma | Graphic Era Deemed University");
  Serial.println("=======================================================");

  // Perform dynamic DC baseline midpoint calibration at startup
  autoCalibrateMidpoints();

  // Load Wi-Fi credentials from NVS (Preferences)
  preferences.begin("wifi-kv", false);
  String savedSSID = preferences.getString("ssid", "");
  String savedPass = preferences.getString("pass", "");

  if (savedSSID != "") {
    Serial.print("[System] Found stored credentials. Linking to: ");
    Serial.println(savedSSID);

    WiFi.mode(WIFI_STA);
    WiFi.begin(savedSSID.c_str(), savedPass.c_str());

    int check = 0;
    while (WiFi.status() != WL_CONNECTED && check < 20) {
      digitalWrite(LED_PIN, !digitalRead(LED_PIN));
      delay(500);
      Serial.print(".");
      check++;
    }
  }

  if (WiFi.status() == WL_CONNECTED) {
    apMode = false;
    digitalWrite(LED_PIN, HIGH);

    Serial.println("\n[Success] Connected to Local Wi-Fi!");
    Serial.print("[Network] Web Portal IP: http://");
    Serial.println(WiFi.localIP());

    server.on("/", handleTelemetryRoot);
    server.on("/api/data", handleApiData);
    server.begin();
  } else {
    apMode = true;
    Serial.println("\n[System] Stored network unavailable. Initiating SoftAP Config Portal...");

    WiFi.mode(WIFI_AP);
    WiFi.softAP("Himshikhar_Config");

    Serial.println("\n--- ACTION REQUIRED ---");
    Serial.println("1. Connect your smartphone/PC Wi-Fi to SSID: 'Himshikhar_Config' (Open)");
    Serial.print("2. Open browser and navigate to: http://");
    Serial.println(WiFi.softAPIP());
    Serial.println("------------------------\n");

    server.on("/", handleConfigRoot);
    server.on("/save", HTTP_POST, handleConfigSave);
    server.begin();
  }
}

// -------------------------------------------------------------------------------------
// Main Execution Loop
// -------------------------------------------------------------------------------------
void loop() {
  unsigned long currentMillis = millis();

  // Status LED control
  if (apMode) {
    if (currentMillis - previousLedMillis >= 150) {
      previousLedMillis = currentMillis;
      ledState = !ledState;
      digitalWrite(LED_PIN, ledState);
    }
  } else {
    digitalWrite(LED_PIN, HIGH);
  }

  // Active Telemetry Capture
  if (!apMode) {
    captureAndCalculate();

    // Stream formatted telemetry to Serial Monitor every 1500ms
    if (currentMillis - previousSerialMillis >= 1500) {
      previousSerialMillis = currentMillis;
      Serial.printf("[Sensors] Volts: %5.2f V | Amps: %5.2f A | P.Factor: %4.2f | Angle: %5.1f° | P: %6.1f W | %s\n",
                    V_rms, I_rms, power_factor, phase_difference, real_power, appliance_name.c_str());
    }
  }

  server.handleClient();

  if (!apMode) {
    delay(10);
  }
}
