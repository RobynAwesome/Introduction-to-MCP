# Priority Security Investigation: IONOS Web Deployment Architecture

**Document ID:** SEC-IONOS-DEPLOY-2026-1022  
**Auditor / Lead:** Lead Dev AG (AntiGravity)  
**Authority:** Founder / RTC  
**Scope:** Forensic analysis of `.github/workflows/deploy-web.yml` and IONOS production deployment pipeline.  
**Severity:** HIGH / PRIORITY DEFENSE  
**Policy Standard:** No production credential changes, merges, or deployments during review.

---

## 1. Executive Summary

A forensic review of `.github/workflows/deploy-web.yml` identified three critical security deficiencies that compromise production infrastructure sovereignty and confidentiality:

1. **Certificate Verification Disabled (`set ssl:verify-certificate no`):** Completely bypasses TLS X.509 certificate validation, enabling Man-in-the-Middle (MitM) credential interception and payload tampering.
2. **Cleartext Downgrade Permitted (`set ftp:ssl-allow yes`):** Allows fallback to unencrypted FTP if AUTH TLS is stripped or negotiation fails. TLS is opportunistic rather than mandatory.
3. **Non-Master Production Deployment Triggers:** Pushes to feature/student branches (`codex/kc-sovereign-gui-full-dev` and `jiro/stap-session4`) automatically trigger production deployments to `https://kopanolabs.com`.
4. **Destructive Mirroring Risk (`mirror --reverse --delete`):** Recursively deletes any remote files not present in the local commit, risking deletion of server-side security controls (`.htaccess`, `.user.ini`, PHP handler overrides).

---

## 2. Technical Vulnerability Details

### Finding A: Disabled TLS Certificate Verification (MitM Risk)
```bash
# deploy-web.yml line 115
set ssl:verify-certificate no;
```
- **Mechanism:** Instructs `lftp` to ignore certificate hostname mismatches, self-signed certificates, and expired/untrusted certificate authorities.
- **Impact:** An attacker on the transit network (ISP level, compromised intermediate router, or DNS spoofing) can present an arbitrary certificate. The FTP client transmits `IONOS_FTP_USER` and `IONOS_FTP_PASS` to the attacker, who can then impersonate the server and serve weaponized HTML/JavaScript from `kopanolabs.com`.

### Finding B: Opportunistic TLS with Plaintext Fallback
```bash
# deploy-web.yml line 114
set ftp:ssl-allow yes;
```
- **Mechanism:** `ssl-allow yes` makes encryption optional. If an adversary injects a TCP reset or strips `AUTH TLS` from the FTP greeting banner, `lftp` downgrades to cleartext FTP.
- **Impact:** Credentials and web assets travel unencrypted over public transit.
- **Remediation:** Enforce TLS strictly using:
  ```bash
  set ftp:ssl-force yes;
  set ftp:ssl-protect-data yes;
  set ssl:verify-certificate yes;
  ```

### Finding C: Branch Exposure Violation (Student/Dev Pushes to Production)
```yaml
# deploy-web.yml lines 18-23
on:
  push:
    branches: [master, codex/kc-sovereign-gui-full-dev, jiro/stap-session4]
    paths:
      - "public/**"
      - "kopano-labs-web/**"
```
- **Mechanism:** Non-master branches (`codex/kc-sovereign-gui-full-dev` and `jiro/stap-session4`) trigger automated deployment to production environment `kopanolabs-production`.
- **Doctrine Violation:** Black Mask Commandment 04 (*Student proposes; Teacher validates; never skip teacher_review*) and Commandment 10 (*Main Brain roadmap gate satisfied before production graduation*). A student drill or local dev experiment pushing a file to `public/` deploys directly to the public live site.
- **Remediation:** Scope automated push triggers strictly to `master` (or require explicit manual `workflow_dispatch` with founder approval).

### Finding D: Destructive Synchronization Risk (`--delete`)
```bash
# deploy-web.yml line 119
mirror --reverse --delete --verbose \
  --exclude='.git/' \
```
- **Mechanism:** `--delete` purges remote files absent from local `public/`.
- **Impact:** If the IONOS web space contains remote server configuration files (such as `.htaccess` restricting directory indexing, `.user.ini` disabling PHP execution, or provider SSL challenge directories), `--delete` wipes them out, leaving the server in an unhardened default state.
- **Remediation:** Exclude server configuration files from deletion:
  ```bash
  --exclude='.git/' \
  --exclude='^(\.htaccess|\.user\.ini|php\.ini|\.well-known/)' \
  ```

---

## 3. Proposed Hardened Configuration

```yaml
# Proposed Hardened lftp Script Block for deploy-web.yml
- name: Upload public/ → IONOS (Hardened TLS & Scope)
  env:
    FTP_HOST: ${{ secrets.IONOS_FTP_HOST }}
    FTP_USER: ${{ secrets.IONOS_FTP_USER }}
    FTP_PASS: ${{ secrets.IONOS_FTP_PASS }}
  run: |
    lftp -c "
      set ftp:ssl-force yes;
      set ftp:ssl-protect-data yes;
      set ssl:verify-certificate yes;
      set ssl:ca-file /etc/ssl/certs/ca-certificates.crt;
      set net:timeout 30;
      set net:max-retries 3;
      open -u '$FTP_USER','$FTP_PASS' '$FTP_HOST';
      mirror --reverse --verbose \
        --delete \
        --exclude='.git/' \
        --exclude='\.htaccess' \
        --exclude='\.user\.ini' \
        --exclude='php\.ini' \
        --exclude='\.well-known/' \
        public/ /
    "
```

---

## 4. Connection Test & Safe Rollback Plan

### Safe Pre-Flight Connection Test (Non-Destructive)
Before updating production workflows, execute an isolated, non-mutating pre-flight probe from a dedicated test workflow or runner:
```bash
# Read-only verification (no mirror, no writes, no deletes)
lftp -c "
  set ftp:ssl-force yes;
  set ftp:ssl-protect-data yes;
  set ssl:verify-certificate yes;
  set ssl:ca-file /etc/ssl/certs/ca-certificates.crt;
  open -u '$FTP_USER','$FTP_PASS' '$FTP_HOST';
  ls -la /;
"
```
*If certificate validation fails due to an IONOS shared cluster certificate hostname (e.g. `*.kundenserver.de`), record the exact certificate subject and SAN before configuring any host-specific trust pin.*

### Rollback Plan
1. If hardened TLS handshake fails, do NOT revert to `ssl:verify-certificate no`.
2. Disable automated push deployments to IONOS immediately.
3. Fall back to manual atomic deployment via SFTP / SSH key where available, or acquire IONOS cluster CA pinning parameters.

---

## 5. Operational Status

- **Production Credentials:** Untouched (`IONOS_FTP_*` secrets not modified or extracted).
- **Deployment Action:** No deployments triggered.
- **Approval Requirement:** Hardening patch requires explicit Founder / RTC review before committing to master workflow.

`[LEAD_DEV_AG | IONOS_DEPLOY_SECURITY | AUDIT_COMPLETE | HARDENING_PROPOSED | NO_PRODUCTION_CHANGES]`
