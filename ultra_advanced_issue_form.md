// abstract upgrade representation

+ attention.num_heads = 32 → 48
+ rotary_embedding.fraction = 0.5 → 0.75
+ loss_fn = CrossEntropy → SymmetricInfoNCE
+ optim = AdamW → SophiaG (second‑order)
- dropout.rate = 0.1
+ activation = GELU → KANLayer (Kolmogorov‑Arnold)
+ memory_bank.size = 2048 → dynamic (up to 64K)
+ world_model = False → True (latent rollout)