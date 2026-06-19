"""Final DHMS binding checkpoint before engine execution."""

from typing import Mapping, Any


class BindingViolation(ValueError):
    """Raised when DHMS binding validation must block execution."""


class ExecutionGate:
    """Final deterministic gate for a proposed DHMS run."""

    REQUIRED_CONTRACT_VERSION = "DHMS Contract Layer v1"

    def validate(
        self,
        *,
        regimes: Mapping[str, Mapping[str, Any]],
        perturbation: Mapping[str, Any],
        metrics: Mapping[str, Any],
        contract_version: Any,
    ) -> None:
        if contract_version != self.REQUIRED_CONTRACT_VERSION:
            raise BindingViolation("run must bind to DHMS Contract Layer v1 exactly.")

        self._validate_regime_consistency(regimes)
        self._validate_perturbation_status(perturbation)
        self._validate_metric_status(metrics)

    def _validate_regime_consistency(self, regimes: Mapping[str, Mapping[str, Any]]) -> None:
        required = {"DHMS-A", "DHMS-B", "DHMS-C"}
        if set(regimes.keys()) != required:
            raise BindingViolation("execution blocked: regime set is incomplete or contains extra regimes.")

        a = regimes["DHMS-A"]
        for name in ("DHMS-B", "DHMS-C"):
            regime = regimes[name]
            for field in (
                "input_condition",
                "task_framing",
                "evaluation_criterion",
                "observational_procedure",
                "metric_profile",
            ):
                if a.get(field) != regime.get(field):
                    raise BindingViolation(f"execution blocked: {field} differs across regimes.")

    def _validate_perturbation_status(self, perturbation: Mapping[str, Any]) -> None:
        if perturbation.get("scope") != "memory_condition":
            raise BindingViolation("execution blocked: perturbation is not memory-confined.")
        if perturbation.get("target") != "memory_condition":
            raise BindingViolation("execution blocked: perturbation target is not memory-confined.")
        if perturbation.get("alters_input") is True:
            raise BindingViolation("execution blocked: perturbation alters input.")
        if perturbation.get("alters_task") is True:
            raise BindingViolation("execution blocked: perturbation alters task framing.")
        if perturbation.get("alters_metrics") is True:
            raise BindingViolation("execution blocked: perturbation alters metric semantics.")

    def _validate_metric_status(self, metrics: Mapping[str, Any]) -> None:
        if metrics.get("interpretation_only") is not True:
            raise BindingViolation("execution blocked: metrics are not interpretation-only.")
        if metrics.get("can_modify_behavior") is not False:
            raise BindingViolation("execution blocked: metrics can modify behavior.")
        if metrics.get("implementation_agnostic") is not True:
            raise BindingViolation("execution blocked: metrics are not implementation-agnostic.")

