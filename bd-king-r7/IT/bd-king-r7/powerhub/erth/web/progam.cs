using System;
using System.Collections.Generic;

class Program
{
    static Dictionary<string, int> intState = new();
    static Dictionary<string, string> strState = new();
    static Random rng = new();

    static void Main()
    {
        InitState();

        IncrementCycle();
        EmotionEngine();
        ForceFieldEngine();
        PowerEngine();
        DriftEngine();
        StabilityEngine();
        VairajEngine();
        FusionEngine();

        PrintProfile();
    }

    // ---------------- INIT ----------------
    static void InitState()
    {
        strState["emotion"] = "CALM";
        intState["emotion_intensity"] = 50;
        strState["power_mode"] = "SUPERSONIC";
        intState["power_drift"] = 0;
        intState["power_stability"] = 100;
        strState["force_field"] = "FOUNDATION";
        strState["vairaj_directive"] = "PRESERVE";
        intState["vairaj_shadow_level"] = 0;
        strState["vairaj_hint"] = "HOLD";
        intState["vairaj_trust"] = 50;
        intState["cycles"] = 0;
    }

    static string S(string key) => strState[key];
    static int I(string key) => intState[key];
    static void SetS(string key, string value) => strState[key] = value;
    static void SetI(string key, int value) => intState[key] = value;

    // ---------------- CYCLE ----------------
    static void IncrementCycle()
    {
        SetI("cycles", I("cycles") + 1);
    }

    // ---------------- EMOTION ----------------
    static void EmotionEngine()
    {
        int intensity = I("emotion_intensity");
        intensity += rng.Next(-7, 8);
        intensity = Math.Clamp(intensity, 10, 100);

        string emo =
            intensity > 80 ? "ASCENDING" :
            intensity > 60 ? "FOCUSED" :
            intensity > 40 ? "CALM" :
            "BURNING";

        SetS("emotion", emo);
        SetI("emotion_intensity", intensity);
    }

    // ---------------- FORCE FIELD ----------------
    static void ForceFieldEngine()
    {
        string emo = S("emotion");
        string ff =
            emo == "ASCENDING" ? "DOMINION" :
            emo == "BURNING" ? "IGNITION" :
            emo == "FOCUSED" || emo == "CALM" ? "FOUNDATION" :
            "RESONANCE";

        SetS("force_field", ff);
    }

    // ---------------- POWER ----------------
    static void PowerEngine()
    {
        string emo = S("emotion");
        string mode =
            emo == "CALM" ? "SUPERSONIC" :
            emo == "FOCUSED" ? "HYPERSONIC" :
            emo == "ASCENDING" ? "ULTRA" :
            "ASCEND";

        SetS("power_mode", mode);
    }

    // ---------------- DRIFT ----------------
    static void DriftEngine()
    {
        int drift = I("power_drift");
        drift += rng.Next(0, 5);
        drift = Math.Clamp(drift, 0, 50);
        SetI("power_drift", drift);
    }

    // ---------------- STABILITY ----------------
    static void StabilityEngine()
    {
        int drift = I("power_drift");
        int stab = I("power_stability");

        stab -= drift / 5;
        stab = Math.Clamp(stab, 0, 100);

        SetI("power_stability", stab);
    }

    // ---------------- VAIRAJ ----------------
    static void VairajEngine()
    {
        int drift = I("power_drift");
        int stab = I("power_stability");
        int trust = I("vairaj_trust");

        string directive =
            stab < 30 ? "STABILIZE" :
            drift > 30 ? "CONTAIN" :
            "ASCEND";

        SetS("vairaj_directive", directive);

        int shadow = drift + (100 - stab) / 2;
        shadow = Math.Clamp(shadow, 0, 100);
        SetI("vairaj_shadow_level", shadow);

        string hint =
            shadow > 70 ? "GROUND" :
            shadow > 40 ? "LIMIT" :
            "ALLOW";

        SetS("vairaj_hint", hint);

        trust += stab / 20 - shadow / 20;
        trust = Math.Clamp(trust, 0, 100);
        SetI("vairaj_trust", trust);
    }

    // ---------------- FUSION ----------------
    static void FusionEngine()
    {
        string mode = S("power_mode");
        int basePower =
            mode == "SUPERSONIC" ? 1500 :
            mode == "HYPERSONIC" ? 3000 :
            mode == "ULTRA" ? 6000 :
            12000;

        int drift = I("power_drift");
        int stab = I("power_stability");

        int fusion = 100 + drift - (100 - stab) / 2;
        fusion = Math.Clamp(fusion, 50, 200);

        int output = basePower * fusion / 100;
        SetI("power_output", output);
    }

    // ---------------- PROFILE ----------------
    static void PrintProfile()
    {
        Console.WriteLine("============== BD-KING-R7 (.NET) ==============");
        Console.WriteLine($" Emotion      : {S("emotion")} ({I("emotion_intensity")})");
        Console.WriteLine($" Power Mode   : {S("power_mode")}");
        Console.WriteLine($" Drift        : {I("power_drift")}");
        Console.WriteLine($" Stability    : {I("power_stability")}%");
        Console.WriteLine($" Force Field  : {S("force_field")}");
        Console.WriteLine($" Vairaj Dir   : {S("vairaj_directive")}");
        Console.WriteLine($" Vairaj Hint  : {S("vairaj_hint")}");
        Console.WriteLine($" Vairaj Shadow: {I("vairaj_shadow_level")}");
        Console.WriteLine($" Vairaj Trust : {I("vairaj_trust")}");
        Console.WriteLine($" Power Output : {I("power_output")} W");
        Console.WriteLine($" Cycles       : {I("cycles")}");
        Console.WriteLine("===============================================");
    }
}
