def evolve_threat_model(score):
    if score > 0.8:
        return "CRITICAL ATTACK"
    elif score > 0.5:
        return "SUSPICIOUS"
    else:
        return "NORMAL"