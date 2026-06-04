using System;
using System.IO;
using System.Collections.Generic;

class BDKingR7
{
    static string StateFile = "state.db";

    static Dictionary<string, string> state = new();

    static void Main()
    {
        LoadState();

        IncrementCycle();
        EmotionEngine();
        ForceFieldEngine();
        PowerEngine();
        DriftEngine();
        StabilityEngine();
        VairajEngine();
        FusionEngine();

        SaveState();
        PrintProfile();
    }

    // ---------------------------------------------------------
    // STATE MANAGEMENT
    // ---------------------------------------------------------
    static void LoadState()
    {
        if (!File.Exists(StateFile))
        {
            File.WriteAllLines(StateFile, new[]
            {
                "emotion=CALM",
                "emotion_intensity=50",
                "power_mode=SUPERSONIC",
                "power_drift=0",
                "power_stability=100",
                "force_field=FOUNDATION",
                "vairaj_directive=PRESERVE",
                "vairaj_shadow_level=0",
                "vairaj_hint=HOLD",
                "vairaj_trust=50",
                "cycles=0"
            });
        }

        foreach (var line in File.ReadAllLines(StateFile))
        {
            var parts = line.Split('=');
            if (parts.Length == 2)
                state[parts[0]] = parts[1];
        }
    }

    static void SaveState()
    {
        List<string> lines = new();
        foreach (var kv in state)
            lines.Add($"{kv.Key}={kv.Value}");
        File.WriteAllLines(StateFile, lines);
    }

    static string Get(string key) => state[key];
    static int GetInt(string key) => int.Parse(state[key]);
    static void Set(string key, object value) => state[key] = value.ToString();

    // ---------------------------------------------------------
    // CYCLE COUNTER
    // ---------------------------------------------------------
    static void IncrementCycle()
    {
        int c = GetInt("cycles");
        Set("cycles", c + 1);
    }

    // ---------------------------------------------------------
    // EMOTION ENGINE
    // ---------------------------------------------------------
    static void EmotionEngine()
    {
        int intensity = GetInt("emotion_intensity");
        intensity += new Random().Next(-7, 8);

        intensity = Math.Clamp(intensity, 10, 100);

        string emo =
            intensity > 80 ? "ASCENDING" :
            intensity > 60 ? "FOCUSED" :
            intensity > 40 ? "CALM" :
            "BURNING";

        Set("emotion", emo);
        Set("emotion_intensity", intensity);
    }

    // ---------------------------------------------------------
    // FORCE FIELD ENGINE
    // ---------------------------------------------------------
    static void ForceFieldEngine()
    {
        string emo = Get("emotion");
        string ff =
            emo == "ASCENDING" ? "DOMINION" :
            emo == "BURNING" ? "IGNITION" :
            emo == "FOCUSED" || emo == "CALM" ? "FOUNDATION" :
            "RESONANCE";

        Set("force_field", ff);
    }

    // ---------------------------------------------------------
    // POWER ENGINE
    // ---------------------------------------------------------
    static void PowerEngine()
    {
        string emo = Get("emotion");
        string mode =
            emo == "CALM" ? "SUPERSONIC" :
            emo == "FOCUSED" ? "HYPERSONIC" :
            emo == "ASCENDING" ? "ULTRA" :
            "ASCEND";

        Set("power_mode", mode);
    }

    // ---------------------------------------------------------
    // DRIFT ENGINE
    // ---------------------------------------------------------
    static void DriftEngine()
    {
        int drift = GetInt("power_drift");
        drift += new Random().Next(0, 5);
        drift = Math.Clamp(drift, 0, 50);
        Set("power_drift", drift);
    }

    // ---------------------------------------------------------
    // STABILITY ENGINE
    // ---------------------------------------------------------
    static void StabilityEngine()
    {
        int drift = GetInt("power_drift");
        int stab = GetInt("power_stability");

        stab -= drift / 5;
        stab = Math.Clamp(stab, 0, 100);

        Set("power_stability", stab);
    }

    // ---------------------------------------------------------
    // VAIRAJ ENGINE
    // ---------------------------------------------------------
    static void VairajEngine()
    {
        int drift = GetInt("power_drift");
        int stab = GetInt("power_stability");
        int trust = GetInt("vairaj_trust");

        string directive =
            stab < 30 ? "STABILIZE" :
            drift > 30 ? "CONTAIN" :
            "ASCEND";

        Set("vairaj_directive", directive);

        int shadow = drift + (100 - stab) / 2;
        shadow = Math.Clamp(shadow, 0, 100);
        Set("vairaj_shadow_level", shadow);

        string hint =
            shadow > 70 ? "GROUND" :
            shadow > 40 ? "LIMIT" :
            "ALLOW";

        Set("vairaj_hint", hint);

        trust += stab / 20 - shadow / 20;
        trust = Math.Clamp(trust, 0, 100);
        Set("vairaj_trust", trust);
    }

    // ---------------------------------------------------------
    // FUSION ENGINE
    // ---------------------------------------------------------
    static void FusionEngine()
    {
        string mode = Get("power_mode");
        int basePower =
            mode == "SUPERSONIC" ? 1500 :
            mode == "HYPERSONIC" ? 3000 :
            mode == "ULTRA" ? 6000 :
            12000;

        int drift = GetInt("power_drift");
        int stab = GetInt("power_stability");

        int fusion = 100 + drift - (100 - stab) / 2;
        fusion = Math.Clamp(fusion, 50, 200);

        int output = basePower * fusion / 100;
        Set("power_output", output);
    }

    // ---------------------------------------------------------
    // PROFILE OUTPUT
    // ---------------------------------------------------------
    static void PrintProfile()
    {
        Console.WriteLine("============== BD-KING-R7 (.NET VERSION) ==============");
        Console.WriteLine($" Emotion      : {Get("emotion")} ({Get("emotion_intensity")})");
        Console.WriteLine($" Power Mode   : {Get("power_mode")}");
        Console.WriteLine($" Drift        : {Get("power_drift")}");
        Console.WriteLine($" Stability    : {Get("power_stability")}%");
        Console.WriteLine($" Force Field  : {Get("force_field")}");
        Console.WriteLine($" Vairaj Dir   : {Get("vairaj_directive")}");
        Console.WriteLine($" Vairaj Hint  : {Get("vairaj_hint")}");
        Console.WriteLine($" Vairaj Shadow: {Get("vairaj_shadow_level")}");
        Console.WriteLine($" Vairaj Trust : {Get("vairaj_trust")}");
        Console.WriteLine($" Power Output : {Get("power_output")} W");
        Console.WriteLine($" Cycles       : {Get("cycles")}");
        Console.WriteLine("========================================================");
    }
}
