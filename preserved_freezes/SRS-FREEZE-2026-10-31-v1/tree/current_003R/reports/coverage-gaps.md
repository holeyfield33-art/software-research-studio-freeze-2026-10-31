# Coverage gaps

This is a deliberately bounded research checkpoint, not a market-readiness assessment.

## Not calibrated in 003

- `software_type.data_pipelines` — **NOT_CALIBRATED**. The type’s overview record and general cross-cutting records may exist, but no dedicated golden fixture validates category-specific selection, exclusion, evidence locators, or gate behavior.
- `software_type.developer_tools` — **NOT_CALIBRATED**. The type’s overview record and general cross-cutting records may exist, but no dedicated golden fixture validates category-specific selection, exclusion, evidence locators, or gate behavior.
- `software_type.libraries` — **NOT_CALIBRATED**. The type’s overview record and general cross-cutting records may exist, but no dedicated golden fixture validates category-specific selection, exclusion, evidence locators, or gate behavior.
- `software_type.mobile_applications` — **NOT_CALIBRATED**. The type’s overview record and general cross-cutting records may exist, but no dedicated golden fixture validates category-specific selection, exclusion, evidence locators, or gate behavior.
- `software_type.saas` — **NOT_CALIBRATED**. The type’s overview record and general cross-cutting records may exist, but no dedicated golden fixture validates category-specific selection, exclusion, evidence locators, or gate behavior.
- `software_type.security_products` — **NOT_CALIBRATED**. The type’s overview record and general cross-cutting records may exist, but no dedicated golden fixture validates category-specific selection, exclusion, evidence locators, or gate behavior.
- `software_type.web_applications` — **NOT_CALIBRATED**. The type’s overview record and general cross-cutting records may exist, but no dedicated golden fixture validates category-specific selection, exclusion, evidence locators, or gate behavior.

## Narrowly demonstrated only

- `software_type.ai_agents`: one external/untrusted-content agent with read and bounded-write tools, side effects, no standing high-impact approval, and missing candidate/run/recovery evidence.
- `software_type.apis`: one authenticated, role-authorized, persisted-record, single-service API; tenanting, queueing, gateway, billing, microservices, and Kubernetes are not presumed.
- `software_type.cli_tools`: one offline local-file processor, no account/network/shared-state boundary, and no authorized destructive writes; packaging and local recovery are conditional.

These examples do not establish complete category coverage. Before any broader claim, add category-specific evidence and a separate worked fixture. No additional category content was expanded merely to improve counts.
