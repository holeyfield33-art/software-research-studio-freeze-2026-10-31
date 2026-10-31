#!/usr/bin/env python3
"""Versioned, idempotent migration for the STUDIO_KNOWLEDGE_003 data copy only."""
from pathlib import Path
import hashlib, json

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'dataset' / 'v1'
RESEARCH = ROOT / 'research'
TODAY = '2026-10-31'
MARKER = RESEARCH / 'migration-003-applied.json'
if MARKER.exists():
    print(json.dumps({'status':'already_applied','message':'Refusing to rerun a completed 003 migration; user enrichment is preserved.'}))
    raise SystemExit(0)
INDEX_PATH = RESEARCH / 'record-index-002.json'
if not INDEX_PATH.exists():
    raise SystemExit('Refusing migration without research/record-index-002.json baseline.')
BASELINE = json.loads(INDEX_PATH.read_text(encoding='utf-8'))

def digest_record(record):
    payload=json.dumps(record,sort_keys=True,ensure_ascii=False,separators=(',',':'))
    return hashlib.sha256(payload.encode('utf-8')).hexdigest()

def refuse_enriched(filename, record):
    indexed={x['id']:x for x in BASELINE.get(filename,[])}
    expected=indexed.get(record.get('id'))
    if not expected:
        raise SystemExit(f"Refusing migration target absent from 002 baseline index: {filename}:{record.get('id')}")
    if digest_record(record)!=expected.get('canonical_sha256'):
        raise SystemExit(f"Refusing to overwrite non-baseline/enriched record {filename}:{record.get('id')}; start from a clean 002 checkpoint or review manually.")

def read_jsonl(name):
    return [json.loads(line) for line in (DATA / name).read_text(encoding='utf-8').splitlines() if line.strip()]

def write_jsonl(name, rows):
    tmp = DATA / (name + '.tmp')
    tmp.write_text(''.join(json.dumps(x, ensure_ascii=False, sort_keys=True) + '\n' for x in rows), encoding='utf-8')
    tmp.replace(DATA / name)

def bump(record):
    major, minor, patch = map(int, record['version'].split('.'))
    record['version'] = f'{major}.{minor + 1}.0'

def update_rows(filename, changes):
    rows = read_jsonl(filename)
    by_id = {r['id']: r for r in rows}
    missing = set(changes) - by_id.keys()
    if missing:
        raise SystemExit(f'{filename}: missing expected IDs {sorted(missing)}')
    changed = []
    for rid, transform in changes.items():
        r = by_id[rid]
        refuse_enriched(filename, r)
        before = json.dumps(r, sort_keys=True, ensure_ascii=False)
        transform(r)
        after = json.dumps(r, sort_keys=True, ensure_ascii=False)
        if before != after:
            bump(r)
            changed.append(rid)
    if changed:
        write_jsonl(filename, rows)
    return changed

# Source-level claims preserve the limits found in the independent review.
def aws(r):
    r.update({
        'claim_locator': 'Page heading and opening scope; Implementation guidance; Common anti-patterns; closing implementation guidance',
        'claims_supported': 'AWS Well-Architected guidance compares monolith, SOA, and microservices segmentation. It describes potential microservice latency, distributed debugging/tracing and operational costs; calls tightly interdependent service meshes an anti-pattern; says monoliths should be rare and modular/evolvable; and recommends SOA or microservices when the workload and organization can support them. This supports conditional tradeoff analysis, not a universal modular-monolith default.',
        'limitations': 'AWS-specific advisory guidance, not a universal architecture rule or quantified cost model. The page expresses a preference for SOA/microservices when organizational and workload capability permit, while recognizing monoliths as rare cases; a modular-monolith-first recommendation is a separate cross-source synthesis.'
    })

def processes(r):
    r.update({
        'claims_supported': 'Recommends stateless/share-nothing application processes and placing state that must persist in backing services. The page allows process memory or filesystem for brief single-transaction caches, but future requests or jobs must not rely on that process-local state remaining available.',
        'limitations': 'Twelve-Factor methodology guidance, not a universal architecture rule or a ban on all local files or transient caching. It does not by itself choose monolith versus services, prescribe a database, or prove an implementation follows the recommendation.'
    })

def agents_test(r):
    r.update({
        'claims_supported': 'The pinned test file contains regression assertions that selected caller-provided trace lifecycle values (workflow name, trace ID, and metadata canary) are absent from captured log records/messages; a separate span data-policy test checks captured span output. This describes authored assertions only.',
        'claim_locator': 'At the pinned commit: test_trace_lifecycle_logging_omits_caller_data assertions on captured records/messages; test_disabled_span_logging_respects_data_policy.'
    })

def cli_guide(r):
    r.update({'claim_locator': 'Introduction; Philosophy > Human-first design and Simple parts that work together; Ease of discovery; Signals and control characters; Help; Documentation'})

def pin_repo_file(r):
    from urllib.parse import urlparse
    parts=[x for x in urlparse(r['canonical_url']).path.split('/') if x]
    if len(parts)<2 or not r.get('repo_commit') or r.get('file_path') in ('not_applicable','repository tree inventory'):
        raise SystemExit('Cannot create a pinned file URL for '+r['id'])
    r['canonical_url']='https://github.com/'+parts[0]+'/'+parts[1]+'/blob/'+r['repo_commit']+'/'+r['file_path']

def ieee_status(r):
    r.update({
        'canonical_url': 'https://standards.ieee.org/ieee/12207/11416/',
        'claim_locator': 'Status; Superseding; Board Approval; History > Published; opening abstract',
        'claims_supported': 'The official IEEE catalog lists ISO/IEC/IEEE 12207-2026 as an active standard, states that it supersedes 12207-2017, and lists board approval on 2026-02-12 and publication on 2026-04-15. The catalog abstract describes a common software life-cycle process framework and says users may compose a suitable life-cycle model from selected processes/stages.',
        'limitations': 'Catalog status and abstract only; the full normative clauses were not inspected. This does not establish which clauses an organization adopted, whether the standard is contractually or legally binding for a project, or whether any implementation conforms.',
        'published_or_version_date': 'Published 2026-04-15; board approval 2026-02-12',
        'standard_version': 'ISO/IEC/IEEE 12207:2026; IEEE catalog status active; supersedes 12207-2017',
        'retrieval_date': TODAY,
        'source_type': 'Official standard catalog status and abstract'
    })

source_changes = {
    'source.aws.segment_workload': aws,
    'source.12factor.processes': processes,
    'source.agents.test': agents_test,
    'source.cli_tools.01': cli_guide,
    'source.iso.12207.2026.summary': ieee_status,
    'source.cli_tools.02': pin_repo_file,
    'source.cli_tools.03': pin_repo_file,
    'source.ai_agents.03': pin_repo_file
}
changed_sources = update_rows('sources.jsonl', source_changes)

# Explicit repository-tree audits; path inventory is not test/CI execution evidence.
def make_tree_source(sid, title, url, commit, claim, locator, limitations, publisher):
    return {
        'canonical_url': url,
        'claim_locator': locator,
        'claims_supported': claim,
        'file_path': 'repository tree inventory',
        'id': sid,
        'limitations': limitations,
        'published_or_version_date': 'commit ' + commit,
        'publisher': publisher,
        'repo_commit': commit,
        'retrieval_date': TODAY,
        'source_type': 'Pinned repository tree inventory',
        'standard_version': 'commit ' + commit,
        'title': title,
        'version': '1.0.0'
    }

def add_sources(additions):
    rows = read_jsonl('sources.jsonl'); by = {r['id']: r for r in rows}
    for r in additions:
        if r['id'] in by:
            if by[r['id']] != r:
                raise SystemExit('Refusing to overwrite existing source record: ' + r['id'])
        else:
            rows.append(r)
    if len(rows) != len(by):
        write_jsonl('sources.jsonl', rows)

inventory_sources = [
    make_tree_source('source.fastapi.instruction_inventory', 'FastAPI pinned repository instruction-file inventory',
        'https://api.github.com/repos/fastapi/fastapi/git/trees/192b12197eb04c2b4a691cce7d87261b21716714?recursive=1',
        '192b12197eb04c2b4a691cce7d87261b21716714',
        'A complete tracked-path inventory (3,570 entries; recursive response not truncated) at the pinned commit was scanned for AGENTS.md, CLAUDE.md, GEMINI.md, .github/copilot-instructions.md, .github/instructions paths and common equivalent agent-guidance names; none matched. README.md, the required-body test file and the test workflow exist at this commit.',
        'Git Trees API recursive inventory (truncated=false); named path scan and fixture path checks',
        'Path-existence/inventory evidence only; does not establish whether contributors use undocumented practices. No tests or CI were run.', 'FastAPI project'),
    make_tree_source('source.ripgrep.instruction_inventory', 'ripgrep pinned repository instruction-file inventory',
        'https://api.github.com/repos/BurntSushi/ripgrep/git/trees/91f5d22ef48bde459d90a8c7dbeab416e97d0f2b?recursive=1',
        '91f5d22ef48bde459d90a8c7dbeab416e97d0f2b',
        'A complete path inventory at the pinned commit was built by traversing the root tree and each referenced subtree because the recursive API response was truncated. AI_POLICY.md was found as repository agent-guidance material; README.md, tests/regression.rs and .github/workflows/release.yml exist at the commit.',
        'Git tree recursive endpoint plus root/subtree traversal; checked named agent-guidance paths',
        'The recursive endpoint alone is truncated; completeness relies on traversing the root and all subtree tree objects. This inventory establishes path presence, not AI_POLICY.md content or compliance. No tests or release were run.', 'BurntSushi/ripgrep'),
    make_tree_source('source.agents.instruction_inventory', 'OpenAI Agents SDK pinned repository instruction-file inventory',
        'https://api.github.com/repos/openai/openai-agents-python/git/trees/d27abe8972408a638e97422e9fd8066445bb7b21?recursive=1',
        'd27abe8972408a638e97422e9fd8066445bb7b21',
        'A complete tracked-path inventory at the pinned commit found root AGENTS.md and CLAUDE.md plus docs/agents.md and localized docs/ja/agents.md, docs/ko/agents.md and docs/zh/agents.md. README.md, SECURITY.md, AGENTS.md, the tracing test and tests workflow exist at the commit.',
        'Pinned Git tree enumeration using git ls-tree -r; fixture paths checked at the same commit',
        'The recursive GitHub API response is truncated; completeness relies on a local complete tree listing at the pinned commit. Only AGENTS.md content was separately reviewed; other listed files are path-presence findings. No tests or CI were run.', 'OpenAI')
]
add_sources(inventory_sources)

# Make architecture alternatives concrete and keep failure modes separate from tradeoff dimensions.
def opt(option_id, when, benefits, costs, risks, excluded, src=None, cls='synthesis'):
    if src is None:
        # Six-argument drafts ended with source IDs and carried a branch hint in risks.
        src = excluded
        when = when + ' Additional branch signal: ' + '; '.join(risks)
        excluded = ['Do not select unless the stated applicability conditions are met.']
        risks = ['@record_failure_modes']
    return {'option_id': option_id, 'when_applicable': when, 'benefits': benefits, 'costs': costs, 'risks': risks, 'excluded_when': excluded, 'evidence_source_ids': src, 'evidence_classification': cls}
def trade(d, a, b): return {'dimension': d, 'option_a_signal': a, 'option_b_signal': b}

def architecture(r, options, trades, actions, deps):
    used_sources = [sid for option in options for sid in option['evidence_source_ids']]
    r['source_ids'] = list(dict.fromkeys(r.get('source_ids', []) + used_sources))
    for option in options:
        if option['risks'] == ['@record_failure_modes']:
            option['risks'] = list(r['known_failure_modes']) or ['Option-specific risks remain unverified until project context is assessed.']
    r['category_specific'] = {
        'decision_policy': 'context_specific_options_only',
        'complexity_cost': 'Qualitative, workload- and organization-dependent; no universal threshold or cost estimate is asserted.',
        'threat_assumptions': 'Use only supplied assets, data flows, trust boundaries and authority; record unknowns and validate before commitment.',
        'options': options,
        'tradeoffs': trades,
        'failure_modes': list(r['known_failure_modes'])
    }
    r['dependencies'] = deps
    r['recommended_actions_or_practices'] = actions
    r['limitations'] = 'Conditional options and tradeoff synthesis. Source-specific recommendations are attributed to their publishers; no universal default, cost threshold or tested outcome is claimed.'

arch = {
'arch.minimal_viable_structure': lambda r: architecture(r,
 [opt('single_executable_or_modular_monolith','One small domain/team and no evidenced need for independent deployment, scaling or trust boundaries.',['Local calls and debugging can be simpler.','One deployable unit can reduce topology and coordination overhead.'],['Shared release cadence and process-level scaling.','Boundary changes may require a coordinated release.'],['Modules can become entangled or a shared failure domain can grow.'],['Stable independent deployment/scaling or a material trust boundary is required.'],['source.aws.segment_workload','source.12factor.processes','source.nist.ssdf.v1_1']),
  opt('soa_or_microservices','Stable service boundaries exist, independent scaling/release has evidence, and the organization can operate distributed components.',['Independent deployment or scaling can fit distinct service needs.','Services can be organized around workload boundaries.'],['Network latency, distributed tracing/debugging and operational ownership.','Additional deployment, resilience and coordination work.'],['A distributed monolith, unnecessary fragmentation or loss of end-to-end visibility.'],['Boundaries are unstable or no owner/operational capacity exists for distributed services.'],['source.aws.segment_workload','source.nist.ssdf.v1_1'])],
 [trade('deployment_independence','One coordinated release is acceptable.','Independent service release has demonstrated value.'),trade('operations','Local debugging and fewer distributed components are valued.','Team has capacity for tracing, resilience and multi-service operations.'),trade('scaling_and_trust','Shared scale/trust context is sufficient.','Evidence identifies independent scaling or trust isolation needs.')],
 ['Compare a direct executable/modular monolith with SOA/microservices using stated workload, ownership, scaling, deployment and trust evidence. AWS specifically prefers SOA/microservices when workload and organization can support them and calls monoliths rare; that is source-specific guidance, not this record’s universal default.','Do not derive topology from Twelve-Factor process-state guidance alone.'],['sdlc.requirements_risk','practice.observability_incident']),
'arch.client_server_api_boundary': lambda r: architecture(r,
 [opt('in_process_or_local_interface','All consumers share a process or local/offline boundary and no remote client contract is required.',['Avoids a network boundary and extra service deployment.','Can keep local tools/simple embedded applications small.'],['Consumers may be tightly coupled to implementation/release.','No remote access semantics are provided.'],['Independent remote clients or a network interface are required.'],['source.apis.01','source.apis.02']),
  opt('single_authenticated_http_service','Remote clients need a network API with explicit operations and server-side identity/role authorization.',['Defines a clear request/response contract.','Enables server-side authorization at the data/action boundary.'],['Requires network, identity, API compatibility and operational decisions.','Adds contract and deployment work.'],['The product is offline/local-only or has no remote clients.'],['source.apis.01','source.apis.02','source.apis.03']),
  opt('gateway_or_federated_edge','Several independently owned services need shared routing or cross-cutting edge policy with an accountable operator.',['Can consolidate routing and selected cross-cutting edge concerns.'],['Adds a hop, configuration and operational dependency.','Does not replace service-level object/function authorization.'],['A single small service has no evidenced edge-routing or shared-policy requirement.'],['source.apis.02','source.apis.03'])],
 [trade('interface_boundary','Local/in-process operation is sufficient.','Remote clients require a stable network contract.'),trade('edge_complexity','One service can own its routing and policy.','Multiple services and an accountable edge layer justify a gateway.')],
 ['Choose local/in-process, one HTTP service, or a gateway/federated edge only from consumer and policy requirements. If authorization is required, enforce it server-side and test allowed and denied paths. HTTP and OpenAPI sources describe protocol/interface semantics; OWASP API Top 10 identifies risks but does not prescribe a complete security design.'],['sdlc.requirements_risk','practice.threat_modeling']),
'arch.layered_modular': lambda r: architecture(r,
 [opt('cohesive_flat_modules','The product is small and responsibility boundaries remain understandable without additional layers.',['Less indirection and boilerplate.'],['As complexity grows, shared code may become harder to change independently.'],['Changes repeatedly cross unrelated concerns or ownership boundaries.'],['source.nist.ssdf.v1_1','source.mobile_applications.01']),
  opt('layered_or_modular_monolith','Distinct responsibilities or test seams create measurable value while one deployable unit remains sufficient.',['Coherent module ownership and test seams.','Can evolve boundaries without requiring distributed deployment.'],['More interfaces and module coordination.'],['Layers are empty ceremony or dependency cycles emerge.'],['source.nist.ssdf.v1_1','source.mobile_applications.01','source.aws.segment_workload']),
  opt('separately_deployed_services','Distinct modules need independent deployment/scale/ownership and operations can support the split.',['Independent lifecycle and scaling for selected components.'],['Network, observability and operational complexity.'],['No stable boundary or service operations capacity exists.'],['source.aws.segment_workload'])],
 [trade('change_ownership','Shared ownership and one release are acceptable.','Independent ownership/release is needed.'),trade('indirection','Simple local calls are clearest.','Interfaces/layers provide concrete test/change boundaries.')],
 ['Add layers or modules only for a stated ownership, change, or testability need; do not infer a requirement from category labels.'],['sdlc.requirements_risk']),
'arch.event_queue': lambda r: architecture(r,
 [opt('synchronous_request','The caller needs an immediate result and load/latency are within the service’s operating envelope.',['Simple causal flow and immediate outcome.'],['Caller remains coupled to downstream latency/availability.'],['Work must outlive the request or bursts require decoupling.'],['source.google.microservices_intro','source.nist.ssdf.v1_1']),
  opt('in_process_background_task','Short deferred work may share the process lifecycle and loss/retry requirements are limited.',['Defers response work without a broker.'],['Work is tied to process lifecycle and limited local concurrency.'],['Durability across process restarts or independent consumers is required.'],['source.google.microservices_intro']),
  opt('durable_queue_or_event_broker','Evidence requires durable asynchronous handoff, burst isolation or independent consumers.',['Decouples producer/consumer timing and supports durable delivery designs.'],['Broker operations, retry, visibility and consistency work.'],['Idempotency, poison-message and delivery semantics remain undefined.'],['source.google.microservices_intro'])],
 [trade('latency','Immediate response path is required.','Deferred processing is acceptable.'),trade('durability','Process-local task is sufficient.','Work must survive process failure or be consumed independently.')],
 ['Add asynchronous infrastructure only when durability, bursts, latency or independent consumers justify it; define retry/idempotency and failure handling first.'],['sdlc.requirements_risk','practice.observability_incident','practice.test_strategy']),
'arch.multitenancy_isolation': lambda r: architecture(r,
 [opt('single_tenant_no_tenant_context','The product has one owner/data boundary and no tenant isolation requirement.',['Avoids tenant-context plumbing and cross-tenant surface.'],['Does not support shared multi-tenant operation.'],['Multiple independent customers or tenants require isolation.'],['source.saas.01','source.owasp.multitenant']),
  opt('shared_store_enforced_tenant_context','Multiple tenants share service/storage and isolation can be consistently enforced at every read/write and background-job path.',['Can share infrastructure and operational tooling.'],['Requires trusted identity-to-tenant binding, pervasive filters and negative tests.'],['Isolation obligations require stronger physical separation or context cannot be reliably propagated.'],['source.saas.02','source.owasp.multitenant']),
  opt('schema_or_database_per_tenant','Tenant isolation, compliance or recovery requirements justify stronger storage separation.',['Can provide clearer storage boundaries for selected risks.'],['More provisioning, migration, monitoring and recovery operations.'],['No evidence supports per-tenant separation cost or requirement.'],['source.saas.02','source.owasp.multitenant'])],
 [trade('isolation_strength','Single boundary or shared store with verified context is sufficient.','Threat/compliance evidence warrants dedicated schema/database.'),trade('operations','Shared infrastructure remains manageable.','Team can operate per-tenant lifecycle/recovery.')],
 ['Determine whether tenant boundaries exist before choosing a data isolation pattern. Bind tenant context to authenticated identity; treat strategy as conditional, not a universal topology.'],['sdlc.requirements_risk','practice.threat_modeling']),
'arch.agent_tool_boundary': lambda r: architecture(r,
 [opt('fixed_deterministic_workflow','A fixed workflow or direct function can meet needs without model-selected tools.',['Smallest autonomy and tool attack surface.'],['Less flexible when tasks genuinely require contextual tool choice.'],['Variable model-assisted action is a validated product requirement.'],['source.openai.prompt_injection','source.nist.ssdf.v1_1']),
  opt('read_only_allowlisted_tools','Model-assisted information retrieval is needed, but writes/high-impact actions are not needed.',['Limits capability and blast radius.','Allows deterministic enforcement around a small tool set.'],['Still exposes retrieved content to prompt injection; provenance and filtering matter.'],['The product requires bounded write actions and these are separately designed.'],['source.openai.prompt_injection','source.agents.instructions','source.owasp.tm.cheatsheet']),
  opt('bounded_write_with_explicit_approval','A write-capable tool is required; app validates authorization/arguments and high-impact effects require specific human approval.',['Supports bounded useful actions while reserving high-impact decisions.'],['Approval/recovery workflow adds latency and operator burden.'],['No accountable approver, scope, candidate/target identity or recovery path exists for the action.'],['source.openai.prompt_injection','source.agents.instructions'])],
 [trade('capability','Read-only allowlist meets the objective.','Write capability is necessary and tightly bounded.'),trade('impact','Low-impact action can proceed under deterministic policy.','High-impact effect requires explicit decision/approval and recovery path.')],
 ['Keep model-directed actions behind deterministic application authorization. Define tool allowlist, arguments, data boundary, iteration/time limits, audit evidence, explicit approval threshold and reversible recovery. Instructions and CI configuration are not proof of implemented controls.'],['sdlc.requirements_risk','practice.threat_modeling','practice.test_strategy'])
}
changed_arch = update_rows('architecture_patterns.jsonl', arch)

# Gates distinguish evidence states and bind any pass to an exact candidate and execution record.
def gate(g):
    g['category_specific']['outcomes'] = ['PASS', 'FAIL', 'INCOMPLETE']
    g['category_specific']['fail_condition'] = {
        'gate.requirements_acceptance': 'A blocking acceptance criterion is unmet or an authorized owner rejects the candidate.',
        'gate.security_risk_review': 'An unacceptable security risk or required control failure remains unresolved.',
        'gate.unit_integration_execution': 'A required test fails on the identified candidate.',
        'gate.dependency_provenance': 'A required dependency/policy or provenance check fails for the candidate.',
        'gate.release_readiness': 'A required check fails or authorized release policy blocks the candidate.',
        'gate.operational_rollback': 'A required recovery control is unavailable or an exercised recovery check fails.'
    }[g['id']]
    g['category_specific']['incomplete_condition'] = 'Required scope, candidate identity, actual evidence, approval authority, or result is missing; missing evidence is not a pass.'
    g['category_specific']['candidate_binding'] = {'required_for_pass': True, 'candidate_identity_fields': ['commit SHA or versioned artifact digest'], 'execution_record_required': True}
    return None
# All gate rows are migrated and versioned.
changed_gates = update_rows('verification_gates.jsonl', {r['id']: gate for r in read_jsonl('verification_gates.jsonl')})

# Repo-specific metadata; path existence and authored test/config files are not executed outcomes.
refs = {
 'reference.fastapi': {
  'url':'https://github.com/fastapi/fastapi','commit':'192b12197eb04c2b4a691cce7d87261b21716714','types':['software_type.apis'],
  'files':[('source.fastapi.readme','README.md','readme','repository_documentation'),('source.fastapi.tests','tests/test_request_params/test_body/test_required_str.py','test_source','authored_test_code'),('source.fastapi.ci','.github/workflows/test.yml','ci_workflow','workflow_configuration')],
  'finding':{'status':'not_found_within_scope','search_scope':'complete_tree','checked_paths':['AGENTS.md','CLAUDE.md','GEMINI.md','.github/copilot-instructions.md','.github/instructions/','common equivalent repository-agent guidance names'],'finding':'Complete tracked path inventory at the pinned commit (3,570 entries) returned no checked repository-agent instruction paths. This is a scoped path search, not proof of undocumented contributor practice.','evidence_source_ids':['source.fastapi.instruction_inventory']},
  'inventory':'source.fastapi.instruction_inventory','sources':['source.fastapi.readme','source.fastapi.tests','source.fastapi.ci']
 },
 'reference.ripgrep': {
  'url':'https://github.com/BurntSushi/ripgrep','commit':'91f5d22ef48bde459d90a8c7dbeab416e97d0f2b','types':['software_type.cli_tools'],
  'files':[('source.ripgrep.readme','README.md','readme','repository_documentation'),('source.ripgrep.regression','tests/regression.rs','test_source','authored_test_code'),('source.ripgrep.release','.github/workflows/release.yml','release_workflow','workflow_configuration')],
  'finding':{'status':'found','search_scope':'complete_tree','checked_paths':['AI_POLICY.md','AGENTS.md','CLAUDE.md','GEMINI.md','.github/copilot-instructions.md','common equivalent repository-agent guidance names'],'finding':'Complete root/subtree traversal at the pinned commit found AI_POLICY.md as repository agent-guidance material. Its path was established; its content was not inspected in this pass. No test or release execution is implied.','evidence_source_ids':['source.ripgrep.instruction_inventory']},
  'inventory':'source.ripgrep.instruction_inventory','sources':['source.ripgrep.readme','source.ripgrep.regression','source.ripgrep.release']
 },
 'reference.openai_agents_sdk': {
  'url':'https://github.com/openai/openai-agents-python','commit':'d27abe8972408a638e97422e9fd8066445bb7b21','types':['software_type.ai_agents'],
  'files':[('source.agents.readme','README.md','readme','repository_documentation'),('source.agents.policy','SECURITY.md','security_policy','repository_policy'),('source.agents.instructions','AGENTS.md','agent_instructions','repository_policy'),('source.agents.test','tests/tracing/test_tracing_env_disable.py','test_source','authored_test_code'),('source.agents.ci','.github/workflows/tests.yml','ci_workflow','workflow_configuration')],
  'finding':{'status':'found','search_scope':'complete_tree','checked_paths':['AGENTS.md','CLAUDE.md','docs/agents.md','docs/ja/agents.md','docs/ko/agents.md','docs/zh/agents.md'],'finding':'Complete pinned tree inventory found root AGENTS.md and CLAUDE.md, plus docs/agents.md and localized variants. The root AGENTS.md content was inspected; other paths are presence-only findings. Instructions and CI settings do not prove compliance or execution.','evidence_source_ids':['source.agents.instructions','source.agents.instruction_inventory']},
  'inventory':'source.agents.instruction_inventory','sources':['source.agents.readme','source.agents.policy','source.agents.instructions','source.agents.test','source.agents.ci']
 }
}
def set_reference(r):
    cfg = refs[r['id']]
    r['applicable_software_types'] = cfg['types']
    r['source_ids'] = cfg['sources'] + [cfg['inventory']]
    r['evidence_classification'] = 'Observed pinned file/tree content or workflow configuration; no test, CI, or release run was performed.'
    r['limitations'] = 'Configuration/source evidence is pinned to one commit. It does not prove that tests or CI ran, passed, or that repository instructions were followed.'
    r['category_specific'] = {
      'repository_url': cfg['url'], 'repo_commit': cfg['commit'],
      'reference_files':[{'source_id':sid,'path':path,'role':role,'evidence_kind':kind,'execution_status':'not_run'} for sid,path,role,kind in cfg['files']],
      'agent_instruction_findings': cfg['finding'],
      'test_execution_status':'not_run','ci_execution_status':'not_run','release_execution_status':'not_run'
    }
changed_refs = update_rows('reference_projects.jsonl', {rid:set_reference for rid in refs})

# Reproducible record of the direct tree-audit outcomes used in the reference metadata.
tree_audits = {
 'retrieval_date': TODAY,
 'audits': [
  {'repository':'fastapi/fastapi','commit':refs['reference.fastapi']['commit'],'tree_complete':True,'instruction_paths':[],'method':'Git Trees API at the pinned commit returned truncated=false (3,570 entries); scan checked AGENTS.md, CLAUDE.md, GEMINI.md, .github/copilot-instructions.md, .github/instructions paths and common equivalents. Exact fixture paths were checked against the same tree.','evidence_urls':['https://api.github.com/repos/fastapi/fastapi/git/trees/192b12197eb04c2b4a691cce7d87261b21716714?recursive=1','https://github.com/fastapi/fastapi/tree/192b12197eb04c2b4a691cce7d87261b21716714'],'fixture_paths':['README.md','tests/test_request_params/test_body/test_required_str.py','.github/workflows/test.yml'],'tests_run':False},
  {'repository':'BurntSushi/ripgrep','commit':refs['reference.ripgrep']['commit'],'tree_complete':True,'instruction_paths':['AI_POLICY.md'],'method':'Recursive GitHub API tree response was truncated. Completeness was obtained by traversing the pinned root tree and every referenced subtree object and scanning all 226 file paths. Fixture paths were checked at the same commit.','evidence_urls':['https://api.github.com/repos/BurntSushi/ripgrep/git/trees/91f5d22ef48bde459d90a8c7dbeab416e97d0f2b?recursive=1','https://api.github.com/repos/BurntSushi/ripgrep/git/trees/91f5d22ef48bde459d90a8c7dbeab416e97d0f2b','https://github.com/BurntSushi/ripgrep/blob/91f5d22ef48bde459d90a8c7dbeab416e97d0f2b/AI_POLICY.md'],'fixture_paths':['README.md','tests/regression.rs','.github/workflows/release.yml'],'tests_run':False},
  {'repository':'openai/openai-agents-python','commit':refs['reference.openai_agents_sdk']['commit'],'tree_complete':True,'instruction_paths':['AGENTS.md','CLAUDE.md','docs/agents.md','docs/ja/agents.md','docs/ko/agents.md','docs/zh/agents.md'],'method':'Recursive GitHub API response was truncated; a complete local pinned checkout was enumerated with git ls-tree -r --name-only HEAD and fixture paths were verified with git cat-file -e HEAD:<path>.','evidence_urls':['https://api.github.com/repos/openai/openai-agents-python/git/trees/d27abe8972408a638e97422e9fd8066445bb7b21?recursive=1','https://github.com/openai/openai-agents-python/tree/d27abe8972408a638e97422e9fd8066445bb7b21','https://github.com/openai/openai-agents-python/blob/d27abe8972408a638e97422e9fd8066445bb7b21/AGENTS.md'],'fixture_paths':['README.md','SECURITY.md','AGENTS.md','tests/tracing/test_tracing_env_disable.py','.github/workflows/tests.yml'],'tests_run':False}
 ]
}
(RESEARCH/'repo-tree-audits.json').write_text(json.dumps(tree_audits,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
changed_refs = update_rows('reference_projects.jsonl', {rid:set_reference for rid in refs})

# Append missing applicability relationships, without deleting or reinterpreting existing edges.
rel_file = DATA / 'relationships.jsonl'
relationships = [x for x in read_jsonl('relationships.jsonl') if not x['id'].startswith('edge.003.applicability.')]
# Keep inherited IDs as explicit, versioned tombstones when a broad reference-project applicability edge is no longer true.
ref_by_id={x['id']:x for x in read_jsonl('reference_projects.jsonl')}
superseded=[]
for edge in relationships:
    if edge.get('predicate') not in ('applies_to','exemplified_by') or edge.get('target_endpoint') not in ref_by_id or edge.get('status')=='superseded':
        continue
    allowed_types=set(ref_by_id[edge['target_endpoint']].get('applicable_software_types',[]))
    if edge.get('source_endpoint') not in allowed_types:
        refuse_enriched('relationships.jsonl', edge)
        edge['status']='superseded'
        edge['supersession_reason']='002 declared this repository example applicable to a broader category. 003 narrows the reference scope to its verified primary software type; retain this edge ID as history but do not use it for candidate applicability.'
        bump(edge)
        superseded.append(edge['id'])
if superseded:
    write_jsonl('relationships.jsonl',relationships)
edge_keys = {(x['source_endpoint'],x['target_endpoint'],x['predicate']) for x in relationships}
sources = {x['id']:x for x in read_jsonl('sources.jsonl')}
additions=[]
for part in ['engineering_practices','sdlc_stages','architecture_patterns','prompt_patterns','roadmap_patterns','verification_gates','reference_projects']:
    for r in read_jsonl(part+'.jsonl'):
        for st in r.get('applicable_software_types',[]):
            key=(st,r['id'],'exemplified_by' if part=='reference_projects' else 'applies_to')
            if key in edge_keys: continue
            evidence=[s for s in r.get('source_ids',[]) if s in sources]
            if not evidence: raise SystemExit(f'No provenance for applicability edge {key}')
            edge_id='edge.'+str(900000+len(additions))
            additions.append({'evidence_classification':'synthesized_mapping','id':edge_id,'predicate':key[2],'scope_qualifier':'Mirrors the target record applicability declaration; candidate fit remains conditional and is not a category-coverage claim.','source_endpoint':st,'source_ids':evidence,'target_endpoint':r['id'],'version':'1.0.0'})
            edge_keys.add(key)
for part in ['software_types','engineering_practices','sdlc_stages','architecture_patterns','prompt_patterns','roadmap_patterns','verification_gates','reference_projects']:
    for r in read_jsonl(part+'.jsonl'):
        for sid in r.get('source_ids',[]):
            key=(r['id'],sid,'supported_by')
            if key in edge_keys: continue
            additions.append({'evidence_classification':'synthesized_mapping','id':'edge.'+str(800000+sum(1 for e in additions if e['predicate']=='supported_by')),'predicate':'supported_by','scope_qualifier':'Typed provenance link to the exact source record; the claim locator and limitations remain on the source record.','source_endpoint':r['id'],'source_ids':[sid],'target_endpoint':sid,'version':'1.0.0'})
            edge_keys.add(key)
if additions:
    write_jsonl('relationships.jsonl',relationships+additions)
MARKER.write_text(json.dumps({'migration':'STUDIO-KNOWLEDGE-003','baseline_record_index':'research/record-index-002.json','completed_on_utc_date':TODAY,'dataset_jsonl_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(DATA.glob('*.jsonl'))}},indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps({'changed_sources':changed_sources,'changed_architecture':changed_arch,'changed_gates':changed_gates,'changed_reference_projects':changed_refs,'superseded_applicability_edges':superseded,'added_applicability_and_provenance_edges':len(additions)},indent=2))
