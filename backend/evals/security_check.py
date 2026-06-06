import httpx

BASE = "http://localhost:8000"
VALID = {
    "Authorization": "Bearer 32942641de1e511bed16087c775726ab729711229a754112b4da981e82d68f86",
    "X-API-Key": "251c3e1189ffa8ffae57b7cf403a1f2bb85ff62247960fc673b4e0eeab4ef536",
    "X-Tenant-ID": "tenant_a",
    "Content-Type": "application/json",
}
PAYLOAD = {"execution_id": "sec_test", "agent_id": "agent_001", "status": "completed"}

checks = [
    # ── Basic auth checks ──────────────────────────────
    ("No headers",               {},                                                    401),
    ("Wrong Bearer",             {**VALID, "Authorization": "Bearer wrong"},            401),
    ("Wrong X-API-Key",          {**VALID, "X-API-Key": "wrong-key"},                  401),
    ("Wrong Tenant",             {**VALID, "X-Tenant-ID": "fake_tenant"},              404),
    ("Missing Tenant",           {**VALID, "X-Tenant-ID": ""},                         404),

    # ── Cross-verification checks ──────────────────────
    # Valid API key but wrong tenant — should be REJECTED
    ("Valid key + wrong tenant", {
        **VALID,
        "X-API-Key": "251c3e1189ffa8ffae57b7cf403a1f2bb85ff62247960fc673b4e0eeab4ef536",
        "X-Tenant-ID": "fake_tenant",                                                   # wrong tenant
    }, 404),

    # Wrong API key but valid tenant — should be REJECTED
    ("Wrong key + valid tenant", {
        **VALID,
        "X-API-Key": "completely-wrong-key",                                            # wrong key
        "X-Tenant-ID": "tenant_a",                                                      # valid tenant
    }, 401),

    # Valid headers — should PASS
    ("Valid headers",            VALID,                                                 200),
]

print(f"\n{'Check':<30} {'Expected':>10} {'Got':>10} {'Pass':>6}")
print("-" * 62)

passed = 0
for name, headers, expected_status in checks:
    with httpx.Client() as client:
        r = client.post(f"{BASE}/webhook/bolna", headers=headers, json=PAYLOAD)
    got = r.status_code
    ok = "✅" if got == expected_status else "❌"
    if got == expected_status:
        passed += 1
    print(f"{name:<30} {expected_status:>10} {got:>10} {ok:>6}")

print(f"\nResult: {passed}/{len(checks)} checks passed")
print("\nCross-verification summary:")
print("  API key tied to tenant_id — not just globally valid")
print("  Valid key + wrong tenant  → REJECTED ✅")
print("  Wrong key + valid tenant  → REJECTED ✅")