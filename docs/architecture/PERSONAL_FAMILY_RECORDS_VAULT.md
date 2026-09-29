# Personal & Family Records Vault — Architecture

## Ownership

The Personal & Family Records Vault is a KOVA World/module, not a third platform or repository.

- **kovaos-site** owns the authenticated mobile/desktop user experience at `/vault`.
- **Kova-ai-SYSTEM** owns the future indexing, OCR/extraction, authorization contracts, form-preparation orchestration, connector policy and audit semantics.
- **Google Drive** remains the canonical store for user-owned source files.
- The KOVA database may hold only the minimum non-secret metadata required for indexing, per-person grants, audit events and workflow state. It must not become a duplicate document archive.

## Safety invariants

1. Never create public or anyone-with-link URLs for Vault records.
2. Never store passwords, PINs, one-time codes, recovery codes, wallet seed phrases/private keys, full bank logins, CVVs, or full card numbers.
3. General indexes must not contain full SSNs, full financial identifiers, unmasked child identifiers, or detailed medical values.
4. Sensitive values are retrieved only for an authorized task and shown to the user before use.
5. Authorization is per person/source. Access to one family member's records does not imply access to another family member's account.
6. Original files/images are preserved. OCR and extracted fields are derived metadata with confidence and provenance.
7. Moves and renames require explicit user confirmation.
8. Form answers require source, source date, verification state and confidence. Missing/conflicting/stale/uncertain fields remain warnings; never guess.
9. Sensitive forms are never submitted without a separate final approval.
10. Audit events record the action and source/workflow IDs, not the sensitive answer values.

## Recommended metadata contract

A record index entry should include:

- record ID (KOVA internal)
- source provider and provider file ID
- private source URL/reference
- person/grant scope
- topic and document type
- record/provider date and indexed-at/last-checked date
- provider/company and life event
- currentness: current / old / incomplete / needs-review
- verification: verified-record / user-reported / derived
- extraction/OCR confidence
- non-sensitive tags and searchable approved text
- sensitivity classification
- checksum/version reference when available

## Form-preparation contract

Each suggested field answer must carry:

- requested field name
- suggested value (masked when appropriate)
- source record ID
- source date
- confidence
- state: ready / missing / conflict / stale / uncertain
- human edit/approval status

The draft generator may produce a filled draft or answer sheet only after field review. Submission is a distinct action and must fail closed without explicit approval.

## Live-enablement gates

The redacted prototype in `kovaos-site` must remain in sample mode until all of these are verified:

- server-side Drive adapter points to the canonical private packet without public-link creation;
- deployment secrets contain the canonical folder/index IDs instead of browser hard-coding;
- per-person authorization is enforced;
- OCR/extraction strips or masks prohibited index values;
- audit persistence is tested;
- PDF/DOCX parser is tested against redacted fixtures;
- upload staging uses Intake & Review and requires confirmation before move/rename;
- security tests verify anonymous access and cross-person access are denied.

Canonical machine-readable enforcement lives at `config/vault_live_enablement.v1.json`,
referenced by `kova_repos_config.json` under `vault_live_enablement_policy`. The
validator (`python3 scripts/validate_config.py`) rejects any live cutover enabled
in this Git-tracked policy. Its status and evidence fields are planning records,
not authorization or runtime proof. Live family data remains off until a separate
server-side mechanism verifies the authenticated owner's specific approval,
per-person access, deployment configuration, and independently observed runtime
gates. A self-declared file edit cannot turn those checks on.

## Connected-source rule

Only a source with a verified connected adapter may be queried. Unavailable sources are reported as unavailable and handled through an explicit user export/import workflow. No connector status is inferred from old documentation alone.
