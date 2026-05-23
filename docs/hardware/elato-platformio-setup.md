# Elato Hardware Setup for MatriBlood Q

This is the Phase 2 hardware checklist for connecting the Elato ESP32 voice device to the MatriBlood Q demo.

## Goal

Voice report should flow like this:

```text
Elato ESP32 -> Elato Deno WebSocket server -> Supabase transcript/message -> MatriBlood Q dashboard -> Python/Qiskit optimizer
```

## Required Local Services

- Remote Supabase project configured in `.env.local`
- Elato Deno WebSocket server running locally
- Python API running locally on `http://localhost:8000`
- Next.js dashboard running locally on `http://localhost:3000`
- ESP32 and laptop on the same Wi-Fi network

## Firmware Configuration

Follow the Elato PlatformIO guide, then open the Elato firmware project:

```text
firmware-arduino/src/Config.cpp
```

Set the WebSocket and backend server values to your laptop LAN IP, not `localhost`.

Example:

```cpp
const char* ws_server = "ws://192.168.1.20:8000/ws";
const char* backend_server = "http://192.168.1.20:3000";
```

Replace `192.168.1.20` with your actual laptop IP.

On macOS, get it with:

```bash
ipconfig getifaddr en0
```

## Verification Checklist

- [ ] ESP32 builds successfully in PlatformIO.
- [ ] ESP32 uploads successfully.
- [ ] Elato Deno WebSocket server is reachable from another device on the same Wi-Fi.
- [ ] Speaking into the device creates or updates a transcript/message in Supabase.
- [ ] The MatriBlood Q dashboard can display or manually paste that transcript.
- [ ] The transcript can be parsed into an emergency case.
- [ ] The case can run through greedy baseline and Qiskit optimizer.

## Fallback During Demo

If hardware is unstable:

1. Paste the transcript into the dashboard manually.
2. Click **Parse**.
3. Click **Optimize**.
4. Use the spoken-response preview as the action plan.

This preserves the full core story:

```text
voice-style request -> structured case -> Qiskit procurement plan -> operator action
```

