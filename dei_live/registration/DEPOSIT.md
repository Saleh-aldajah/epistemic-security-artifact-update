# Deposit and timestamp procedure (PENDING #9 — do this BEFORE the first paid episode)

What is deposited: this `registration/` folder (policy.json, held_out_cases.json, development_cases.json,
probe_cases.json, strata.json, design.md, MANIFEST.sha256) together with the code the manifest hashes (dei_live/, probes/,
run_campaign.py, analyze.py, tests, power/registration validators, make_registration.py). The manifest is the object that is timestamped; everything
else is verified against it.

1. Verify the manifest locally (from the dei_live/ root):
       sha256sum -c registration/MANIFEST.sha256
   Every line must say OK. If any file changed since generation, re-run `python3 -I make_registration.py` first.
   Then run `python3 power_verify.py --out validation/power.json` and
   `python3 validate_registration.py --out validation/registration_audit.json`; both must pass before upload.

2. Build the deposit archive:
       tar --sort=name --mtime='2026-11-01 00:00Z' --owner=0 --group=0 --numeric-owner \
           -czf registration_deposit_v2.tar.gz registration dei_live probes run_campaign.py analyze.py \
           test_dei_live.py test_probes.py test_analyze.py power_verify.py validate_registration.py \
           make_registration.py README.md validation
       sha256sum registration_deposit_v2.tar.gz   # record this digest in the paper's deposit sentence

3. Public deposit (either; both is fine):
   - Zenodo: new upload, type "Dataset"/"Software", title "Epistemic Security — registered design and held-out cases
     (S&P 2028 campaign), deposit v2", upload registration_deposit_v2.tar.gz, reserve the DOI, publish.
     Anonymity: deposit under an institution-neutral account or use Zenodo's restricted/embargoed access with the DOI
     visible; the paper cites the DOI and the manifest hash, not the depositor.
   - OSF: new project → Registrations → "Open-Ended Registration"; attach the archive; register. OSF issues a
     registration timestamp of its own.

4. Independent timestamp (OpenTimestamps; free, Bitcoin-anchored):
       pip install opentimestamps-client
       ots stamp registration/MANIFEST.sha256          # creates registration/MANIFEST.sha256.ots
       # ~1–6 h later, once anchored:
       ots upgrade registration/MANIFEST.sha256.ots
       ots verify  registration/MANIFEST.sha256.ots    # prints the Bitcoin block height/time
   Keep the .ots file with the deposit (add it to the Zenodo record as a second file; it does not change the manifest).

5. Record in the paper (replaces PENDING "deposit record" in §6.1): DOI, archive SHA-256, manifest SHA-256
   (first line of `sha256sum registration/MANIFEST.sha256`), OpenTimestamps block time.

6. Only after steps 1–4: run the campaign (`run_campaign.py --cases registration/held_out_cases.json ...`,
   `run_campaign.py --probes ...`). Any later change to policy, cases, or arms is a new deposit (v3) and is reported
   as a deviation.

Keys are read from the environment only (FRONTIER_API_KEY / FRONTIER_BASE_URL / FRONTIER_MODEL, OW_BASE_URL / OW_MODEL /
OW_API_KEY); nothing in the deposit contains a credential — `grep -rEa --exclude-dir=__pycache__ "(\bsk-[A-Za-z0-9_-]{16,}|\bAIza[0-9A-Za-z_-]{30,})" .`
from the dei_live root must return nothing.
