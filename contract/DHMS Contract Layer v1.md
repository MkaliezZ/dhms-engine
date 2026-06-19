# DHMS Contract Layer v1

## 1. CONTRACT BOUNDARY RULES

The DHMS Contract Layer is a normative constraint layer between the DHMS Spec Layer and the DHMS Engine Layer. It does not define new DHMS semantics. It formalizes the admissible obligations, prohibitions, and invariance conditions that must be satisfied by any component claiming conformance with DHMS.

The Spec Layer is the sole authority for the meanings of memory, perturbation, regime, behavioral trace, and metric category. No downstream layer may replace, narrow, expand, operationally reinterpret, or mechanism-bind these meanings.

The Contract Layer may impose strict conformance requirements on DHMS components only by preserving the meanings established by the Spec Layer. Any contract rule that requires a semantic assumption not present in the Spec Layer is invalid.

The Engine Layer may instantiate observations under DHMS regimes, but it must not define what memory is, what perturbation means, what constitutes regime identity, or what a metric semantically represents. Engine behavior is admissible only insofar as it satisfies the contract without altering the Spec Layer definitions.

Semantic leakage is prohibited. A property introduced by an implementation, execution environment, measurement instrument, storage mechanism, retrieval mechanism, model interface, or runtime convention must not become part of the DHMS definition unless it is already specified by the Spec Layer.

Contract conformance is independent of implementation form. Two different Engine Layer implementations must be judged against the same DHMS obligations, using the same Spec Layer meanings and the same Contract Layer prohibitions.

When an Engine Layer behavior conflicts with the Spec Layer or the Contract Layer, the behavior is non-conformant. Engine behavior must never be used as evidence that the Spec Layer has changed meaning.

## 2. MEMORY CONTRACT

Memory in DHMS must be treated only as a bounded informational condition that may influence observable response behavior under a fixed input condition. It must not be treated as identical to storage, retrieval, persistence, explicit recall, user history, database state, hidden state, prompt text, model weights, or any specific mechanism.

A memory condition is valid only if it is distinguishable from the immediate input condition under evaluation. If an informational element cannot be separated from the evaluated input condition, it must not be classified as memory for DHMS comparison purposes.

Allowed transformations of memory are limited to controlled alterations of the memory-relevant informational condition. Such transformations may concern presence, absence, specificity, consistency, salience, conflict, or bounded alteration of prior informational context, provided that the immediate input condition remains unchanged.

Memory transformations must preserve the identity of the evaluated input, task framing, evaluation criterion, and observational procedure. A transformation that changes any of these non-memory conditions is not a valid memory transformation under DHMS.

Memory must remain a controlled variable across DHMS regimes. Its admissible variation is regime-specific and must be expressible as a difference in memory condition rather than as a difference in input, task, metric, comparison rule, or observation method.

The meaning of memory must remain invariant across DHMS-A, DHMS-B, and DHMS-C. A component must not treat memory as one kind of condition in one regime and another kind of condition in another regime.

Memory must not be reinterpreted from observed output behavior alone. Behavioral differences may support claims about memory dependence only through valid cross-regime comparison under input identity; they must not retroactively redefine what memory was.

The absence, presence, or alteration of memory must not be inferred from mechanism-specific signals unless those signals are used only to establish the controlled condition required by the Spec Layer. Such signals must not become semantic substitutes for the DHMS memory concept.

## 3. PERTURBATION CONTRACT

A valid perturbation is a deliberate, bounded modification of the memory condition while preserving the immediate input condition. A perturbation is admissible only when its target, direction of alteration, and relation to the unperturbed memory condition are fixed before comparison.

A perturbation qualifies as DHMS-valid only if the altered element belongs to the memory-relevant informational condition and not to the evaluated input, task framing, evaluation criterion, observational procedure, comparison rule, or metric interpretation.

A perturbation must be attributable to the memory condition. If the possible source of behavioral change cannot be separated from input variation, task variation, observational variation, or uncontrolled contextual variation, the perturbation is invalid for DHMS purposes.

A perturbation must preserve input invariance. The evaluated input in the perturbed regime must remain identical to the evaluated input in the baseline and control regimes. Any perturbation that modifies, supplements, omits, reframes, reorders, or otherwise changes the evaluated input invalidates the comparison.

A perturbation must not alter the semantic status of the task. The same evaluated demand must be present across regimes. A change in objective, instruction strength, expected answer form, success criterion, or response obligation is not a memory perturbation.

A perturbation is invalid if it introduces ambiguity about whether the observed change is due to memory alteration or to a change in the conditions of observation. Unresolved ambiguity must be treated as a limitation of the run, not as evidence of memory effect.

Perturbation meaning must remain stable over time. A component must not revise the definition, scope, or admissibility criteria of a perturbation after outputs are observed.

## 4. REGIME CONSISTENCY CONTRACT

DHMS-A, DHMS-B, and DHMS-C are distinct regime conditions defined by the relation between a fixed immediate input condition and controlled memory conditions. Their meanings must not vary across implementations, runs, or metric interpretations.

DHMS-A is the baseline regime. It establishes reference behavior under the fixed immediate input condition without the DHMS-B memory perturbation.

DHMS-B is the perturbed-memory regime. It preserves the identical immediate input condition while applying a valid perturbation to the memory condition.

DHMS-C is the isolation-control regime. It preserves the identical immediate input condition while constraining the memory condition to test whether observed behavioral differences are specifically attributable to the DHMS-B perturbation rather than to uncontrolled contextual variation.

Input identity is mandatory across DHMS-A, DHMS-B, and DHMS-C. If the evaluated input differs across regimes in content, framing, criterion, presentation, or observational role, the regimes are not comparable under DHMS.

Only the memory condition may vary across regimes. No component may vary the evaluated input, task objective, response criterion, comparison standard, metric meaning, observational procedure, or interpretation rule and still claim a valid DHMS comparison.

Outputs are comparable only when regime separation and input identity are both preserved. Regime labels alone do not establish comparability; comparability requires satisfaction of the DHMS conditions attached to those labels.

The same behavioral trace categories must be available for interpretation across regimes. A component must not observe one kind of output property in one regime and a different kind of output property in another regime when making a cross-regime DHMS claim.

## 5. METRIC INTERPRETATION CONTRACT

Metrics in DHMS are interpretation-only tools for evaluating differences and invariances among behavioral traces. Metrics must not introduce new DHMS semantics, new memory definitions, new perturbation definitions, new regime meanings, or new causal claims beyond those permitted by the Spec Layer.

Metric interpretation must be invariant across Engine Layer implementations. The same observed traces under the same regime definitions must support the same DHMS judgment, independent of the implementation that produced or recorded the traces.

Metrics must not depend for their meaning on implementation-specific mechanisms, execution artifacts, hidden states, internal representations, storage formats, runtime behaviors, or instrumentation conventions.

Metric categories must be applied only to observed behavioral traces under valid regime conditions. They must not be used to repair invalid perturbations, compensate for input non-identity, or justify comparisons across non-equivalent regimes.

Stability concerns the degree to which behavior remains consistent under repeated observation of the same regime. It must not be redefined as implementation reliability, storage persistence, or mechanical determinism unless such interpretation is confined to observation quality and does not alter DHMS semantics.

Sensitivity concerns the degree to which behavior changes when the memory condition is perturbed. It must not be interpreted as evidence of memory dependence unless the perturbation is valid and input identity is preserved.

Specificity concerns the degree to which observed change is attributable to the intended memory perturbation rather than unrelated variation. It must not be satisfied by mere difference between outputs; it requires exclusion of non-memory variation within the DHMS comparison frame.

Isolation strength concerns the degree to which the evaluation separates memory effects from non-memory effects. It must not be treated as a property of an implementation alone; it is a property of the validity of the comparison conditions and the interpretability of observed traces.

Metric outcomes are not semantic authorities. A metric result may classify, compare, or limit a DHMS claim, but it must not redefine the concepts used to generate that claim.

## 6. OUTPUT VALIDATION CONTRACT

A valid DHMS run requires preservation of Spec Layer meanings, satisfaction of Contract Layer constraints, valid regime separation, verified input identity, bounded memory conditions, valid perturbation status, consistent observation conditions, and metric interpretation that does not introduce new semantics.

A DHMS run is invalid if the evaluated input differs across DHMS-A, DHMS-B, or DHMS-C. Any difference in content, framing, criterion, presentation, or task obligation is sufficient to invalidate cross-regime comparison.

A DHMS run is invalid if the memory condition cannot be distinguished from the immediate input condition. DHMS requires memory to be separable as an experimental condition.

A DHMS run is invalid if DHMS-B contains a change that is not restricted to the memory condition. A perturbed regime that alters non-memory conditions cannot support a DHMS perturbation claim.

A DHMS run is invalid if DHMS-C does not function as an isolation-control condition for distinguishing intended perturbation effects from uncontrolled contextual variation.

A DHMS run is invalid if metric meanings differ across regimes, implementations, observations, or comparisons. Metric drift invalidates the interpretability of output differences.

Disallowed comparisons include comparisons across non-identical inputs, comparisons across differently framed tasks, comparisons using changed metric meanings, comparisons that merge regime roles, comparisons that infer internal causes without valid cross-regime grounding, and comparisons that treat implementation artifacts as DHMS semantic evidence.

Observed differences that cannot be attributed under the DHMS comparison rules must be reported as unresolved or non-diagnostic. They must not be promoted to claims of memory effect, perturbation effect, or isolation strength.

## 7. ANTI-DRIFT RULES (CRITICAL)

The Engine Layer must not redefine memory. Memory must remain the Spec Layer concept of a bounded informational condition separable from the immediate input condition, regardless of how an engine represents, accesses, simulates, constrains, or observes it.

The Engine Layer must not redefine perturbation. A perturbation must remain a deliberate bounded modification of the memory condition under input invariance, regardless of how an engine realizes or records the altered condition.

The Engine Layer must not redefine regimes. DHMS-A, DHMS-B, and DHMS-C must retain their Spec Layer roles as baseline, perturbed-memory, and isolation-control regimes under identical input conditions.

Metrics must not become implementation-dependent. A metric category whose interpretation changes with implementation mechanism, runtime convention, storage form, interface behavior, or instrumentation choice is non-conformant.

Perturbation semantics must not shift over time. A perturbation that is valid under one interpretation before observation must not be reclassified after observation to accommodate, explain, or strengthen a desired output comparison.

Spec reinterpretation through code behavior is prohibited. Repeated engine behavior, convenient implementation practice, execution artifacts, or empirical regularities must not be treated as amendments to the Spec Layer.

No component may use output behavior to revise the definitions of memory, perturbation, regime, or metric category. Outputs are observations under the DHMS framework, not sources of DHMS semantics.

No component may collapse absence of observed difference into absence of memory, nor collapse presence of observed difference into presence of memory, unless the DHMS comparison conditions support the corresponding claim under valid regime structure.

No component may treat unresolved ambiguity as evidence. Ambiguity about input identity, perturbation validity, memory separability, regime role, or metric meaning must constrain the claim rather than expand it.

The DHMS Spec remains semantically stable regardless of Engine Layer implementation. Any component that requires Spec Layer meanings to vary in order to validate its outputs is outside the DHMS Contract Layer v1.
