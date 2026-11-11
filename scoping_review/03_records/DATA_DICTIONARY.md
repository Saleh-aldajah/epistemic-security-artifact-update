# Data dictionary for the full private PRISMA validation release

The master ledger contains every identified database record and the retained abstract text. Key fields:

- `executed_query_id`: exact database/query export identifier linked to the search ledger.
- `prisma_stage`: identification/deduplication or title/abstract screening.
- `deduplication_status`: `unique` or `duplicate`.
- `duplicate_of_record_id`: canonical retained record for every duplicate.
- `duplicate_resolution_method`: original public mapping or transparent repair source.
- `canonical_final_decision`: final decision assigned to the retained canonical record.
- `final_record_disposition`: `include_core`, `include_background`, `exclude`, or `duplicate_removed_before_screening`.
- `decision_comment`: screening rationale for unique records; duplicate mapping explanation for duplicates.
- `full_text_status`: the completed evidence map used title/abstract records; full-text eligibility was not a stage.
- `released_*_sha256`: value in the earlier rights-cleared public ledger.
- `recomputed_*_sha256`: value calculated from the retained source-text snapshot under the published normalization specification.
- `*_hash_match`: alignment result between those two values.

The 552-row full charting file contains the eight evidence-map dimensions and both transparent computational coder outputs. These are computational reproducibility measures, not human inter-rater judgments.
