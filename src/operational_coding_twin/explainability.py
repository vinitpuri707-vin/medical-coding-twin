from __future__ import annotations

import json
import math

from dataclasses import dataclass
from typing import Any

import numpy as np
import torch

from captum.attr import LayerIntegratedGradients

from operational_coding_twin.config import (
    EXPLANATION_WARNING,
)

from operational_coding_twin.frozen_resources import (
    FrozenResources,
)

from operational_coding_twin.inference import (
    PredictionResult,
)


# ============================================================
# RESULT TYPES
# ============================================================

@dataclass(frozen=True)
class TokenAttribution:
    """
    Attribution assigned to one input token.
    """

    position: int
    token: str
    raw_score: float
    normalized_score: float


@dataclass(frozen=True)
class ExplanationResult:
    """
    Explainability result for one ICD recommendation.
    """

    category: str

    method: str
    steps: int
    baseline: str

    evidence: list[TokenAttribution]
    all_token_attributions: list[TokenAttribution]

    convergence_delta: float | None

    source_mode: str

    warning: str


# ============================================================
# EXPLAINABILITY SERVICE
# ============================================================

class FrozenExplainabilityService:
    """
    Layer Integrated Gradients explainability for the frozen
    Phase 7 seed-42 BioClinicalBERT classifier.

    Fresh synthetic cases:
        calculate a new LIG explanation.

    Validation replay cases:
        load the saved Phase 8B explanation.

    This service does NOT:
        - train
        - alter model weights
        - recalibrate
        - access the test partition
        - treat attribution as causal clinical evidence
    """

    def __init__(
        self,
        resources: FrozenResources,
        *,
        max_length: int = 320,
        n_steps: int = 50,
        top_k: int = 12,
    ) -> None:

        self.resources = resources

        self.model = resources.model
        self.tokenizer = resources.tokenizer
        self.device = resources.device

        self.max_length = int(
            max_length
        )

        self.n_steps = int(
            n_steps
        )

        self.top_k = int(
            top_k
        )

        # ----------------------------------------------------
        # Frozen protocol checks
        # ----------------------------------------------------

        if self.max_length != 320:
            raise RuntimeError(
                "Frozen explainability contract "
                "requires max_length=320."
            )

        if self.n_steps != 50:
            raise RuntimeError(
                "Frozen LIG contract requires "
                "exactly 50 integration steps."
            )

        if self.top_k <= 0:
            raise ValueError(
                "top_k must be greater than zero."
            )

        if not hasattr(
            self.model,
            "bert",
        ):
            raise RuntimeError(
                "Expected a BERT-based classification model."
            )

        if not hasattr(
            self.model.bert,
            "embeddings",
        ):
            raise RuntimeError(
                "Unable to locate BERT embedding layer."
            )

        if (
            self.tokenizer.pad_token_id
            is None
        ):
            raise RuntimeError(
                "Tokenizer must define a PAD token."
            )

        self.model.to(
            self.device
        )

        self.model.eval()

        # ----------------------------------------------------
        # Captum Layer Integrated Gradients
        # ----------------------------------------------------

        self.lig = LayerIntegratedGradients(
            self._forward,
            self.model.bert.embeddings,
        )


    # ========================================================
    # MODEL FORWARD FUNCTION USED BY CAPTUM
    # ========================================================

    def _forward(
        self,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor,
        token_type_ids: torch.Tensor | None = None,
    ) -> torch.Tensor:
        """
        Forward function exposed to Captum.

        Returns all 50 logits.
        """

        kwargs: dict[str, torch.Tensor] = {
            "input_ids":
                input_ids,

            "attention_mask":
                attention_mask,
        }

        if token_type_ids is not None:

            kwargs[
                "token_type_ids"
            ] = token_type_ids

        outputs = self.model(
            **kwargs
        )

        return outputs.logits


    # ========================================================
    # TOKENISE EXACTLY AS FROZEN INFERENCE CONTRACT
    # ========================================================

    def _tokenize(
        self,
        clinical_text: str,
    ) -> dict[str, torch.Tensor]:

        if clinical_text is None:
            raise ValueError(
                "clinical_text cannot be None."
            )

        clinical_text = str(
            clinical_text
        ).strip()

        if len(
            clinical_text
        ) < 30:
            raise ValueError(
                "Clinical text is too short."
            )

        encoded = self.tokenizer(
            clinical_text,

            truncation=True,
            max_length=self.max_length,

            padding=False,

            return_tensors="pt",
        )

        return {
            key:
                tensor.to(
                    self.device
                )

            for key, tensor
            in encoded.items()
        }


    # ========================================================
    # BUILD PAD-CONTENT BASELINE
    # ========================================================

    def _build_baseline(
        self,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor,
    ) -> tuple[
        torch.Tensor,
        np.ndarray,
    ]:
        """
        Build the frozen PAD-content baseline.

        [CLS] and [SEP] remain unchanged.

        Ordinary content tokens are replaced with [PAD].

        The attention mask remains the same so that the
        attribution represents replacement of content-token
        embeddings rather than shortening the sequence.
        """

        baseline_ids = (
            input_ids
            .detach()
            .clone()
        )

        token_ids = (
            input_ids[
                0
            ]
            .detach()
            .cpu()
            .tolist()
        )

        special_mask = (
            self.tokenizer
            .get_special_tokens_mask(
                token_ids,
                already_has_special_tokens=True,
            )
        )

        attention = (
            attention_mask[
                0
            ]
            .detach()
            .cpu()
            .numpy()
            .astype(
                bool
            )
        )

        special_mask_np = np.asarray(
            special_mask,
            dtype=bool,
        )

        # True for actual clinical content tokens.
        content_mask = (
            attention
            &
            ~special_mask_np
        )

        content_positions = np.where(
            content_mask
        )[0]

        if len(
            content_positions
        ) == 0:

            raise RuntimeError(
                "No explainable content tokens "
                "were found."
            )

        baseline_ids[
            0,
            torch.as_tensor(
                content_positions,
                device=self.device,
                dtype=torch.long,
            ),
        ] = int(
            self.tokenizer.pad_token_id
        )

        return (
            baseline_ids,
            content_mask,
        )


    # ========================================================
    # FRESH LIG EXPLANATION
    # ========================================================

    def explain(
        self,
        clinical_text: str,
        prediction: PredictionResult,
    ) -> ExplanationResult:
        """
        Calculate a fresh LIG explanation for a synthetic
        demonstration case.

        Attribution target = predicted ICD category.
        """

        if (
            prediction.source_mode
            != "fresh_frozen_inference"
        ):

            raise ValueError(
                "Fresh LIG explanation requires a "
                "fresh_frozen_inference prediction."
            )

        predicted_class_id = int(
            prediction.predicted_class_id
        )

        if (
            predicted_class_id < 0
            or predicted_class_id >= 50
        ):

            raise RuntimeError(
                "Predicted class ID is outside "
                "the frozen 50-category space."
            )

        expected_category = (
            self.resources.id2label[
                predicted_class_id
            ]
        )

        if (
            expected_category
            != prediction.recommendation
        ):

            raise RuntimeError(
                "Prediction category and frozen "
                "label mapping are inconsistent."
            )

        encoded = self._tokenize(
            clinical_text
        )

        input_ids = encoded[
            "input_ids"
        ]

        attention_mask = encoded[
            "attention_mask"
        ]

        token_type_ids = encoded.get(
            "token_type_ids"
        )

        (
            baseline_ids,
            content_mask,
        ) = self._build_baseline(
            input_ids,
            attention_mask,
        )

        self.model.eval()

        self.model.zero_grad(
            set_to_none=True
        )

        # ----------------------------------------------------
        # IMPORTANT:
        #
        # Do NOT use torch.inference_mode() here.
        # Integrated Gradients requires gradients.
        # ----------------------------------------------------

        if token_type_ids is not None:

            additional_forward_args = (
                attention_mask,
                token_type_ids,
            )

        else:

            additional_forward_args = (
                attention_mask,
            )

        attributions, delta = (
            self.lig.attribute(
                inputs=input_ids,

                baselines=baseline_ids,

                additional_forward_args=(
                    additional_forward_args
                ),

                target=predicted_class_id,

                n_steps=self.n_steps,

                internal_batch_size=5,

                return_convergence_delta=True,
            )
        )

        # ----------------------------------------------------
        # Collapse embedding dimensions to token attribution.
        # ----------------------------------------------------

        token_scores = (
            attributions
            .sum(
                dim=-1
            )[
                0
            ]
            .detach()
            .cpu()
            .numpy()
            .astype(
                np.float64
            )
        )

        token_ids = (
            input_ids[
                0
            ]
            .detach()
            .cpu()
            .tolist()
        )

        tokens = (
            self.tokenizer
            .convert_ids_to_tokens(
                token_ids
            )
        )

        # ----------------------------------------------------
        # Normalisation:
        #
        # score / sum(abs(content scores))
        #
        # This preserves attribution direction:
        # positive = supports predicted class
        # negative = opposes predicted class
        # ----------------------------------------------------

        content_scores = (
            token_scores[
                content_mask
            ]
        )

        denominator = float(
            np.abs(
                content_scores
            ).sum()
        )

        if (
            not np.isfinite(
                denominator
            )
            or denominator <= 0.0
        ):

            denominator = 1.0

        all_attributions: list[
            TokenAttribution
        ] = []

        for position in np.where(
            content_mask
        )[0]:

            raw_score = float(
                token_scores[
                    position
                ]
            )

            normalized_score = (
                raw_score
                / denominator
            )

            all_attributions.append(
                TokenAttribution(
                    position=int(
                        position
                    ),

                    token=str(
                        tokens[
                            position
                        ]
                    ),

                    raw_score=raw_score,

                    normalized_score=float(
                        normalized_score
                    ),
                )
            )

        # ----------------------------------------------------
        # Supporting evidence = positive attribution only.
        # ----------------------------------------------------

        positive = [
            item

            for item
            in all_attributions

            if (
                item.raw_score > 0
                and
                math.isfinite(
                    item.raw_score
                )
            )
        ]

        evidence = sorted(
            positive,

            key=lambda item:
                item.raw_score,

            reverse=True,
        )[
            :self.top_k
        ]

        # ----------------------------------------------------
        # Captum convergence delta
        # ----------------------------------------------------

        convergence_delta: (
            float | None
        )

        try:

            convergence_delta = float(
                delta
                .detach()
                .cpu()
                .reshape(
                    -1
                )[
                    0
                ]
                .item()
            )

        except Exception:

            convergence_delta = None

        return ExplanationResult(
            category=(
                prediction.recommendation
            ),

            method=(
                "Layer Integrated Gradients"
            ),

            steps=(
                self.n_steps
            ),

            baseline=(
                "PAD-content baseline; "
                "special tokens preserved"
            ),

            evidence=evidence,

            all_token_attributions=(
                all_attributions
            ),

            convergence_delta=(
                convergence_delta
            ),

            source_mode=(
                "fresh_lig"
            ),

            warning=(
                EXPLANATION_WARNING
            ),
        )


    # ========================================================
    # FROZEN VALIDATION REPLAY EXPLANATION
    # ========================================================

    def replay(
        self,
        validation_row: int,
    ) -> ExplanationResult:
        """
        Load a saved Phase 8B LIG explanation.

        No new attribution calculation occurs.
        """

        validation_row = int(
            validation_row
        )

        sample_rows = set(
            self.resources
            .replay_sample[
                "validation_row"
            ]
            .astype(
                int
            )
            .tolist()
        )

        if (
            validation_row
            not in sample_rows
        ):

            raise ValueError(
                "Validation row is not part of "
                "the deterministic Phase 8B "
                "n=100 XAI sample."
            )

        rows = (
            self.resources
            .replay_explanations[
                self.resources
                .replay_explanations[
                    "validation_row"
                ]
                .astype(
                    int
                )
                == validation_row
            ]
        )

        if len(
            rows
        ) != 1:

            raise RuntimeError(
                "Expected exactly one frozen "
                "LIG explanation for validation "
                f"row {validation_row}."
            )

        row = rows.iloc[
            0
        ]

        if int(
            row[
                "lig_steps"
            ]
        ) != 50:

            raise RuntimeError(
                "Frozen replay explanation "
                "does not use 50 LIG steps."
            )

        predicted_category = str(
            row[
                "predicted_category"
            ]
        )

        raw_support = json.loads(
            row[
                "top_support_tokens"
            ]
        )

        if not isinstance(
            raw_support,
            list,
        ):

            raise RuntimeError(
                "Frozen top_support_tokens "
                "must contain a JSON list."
            )

        evidence: list[
            TokenAttribution
        ] = []

        for index, item in enumerate(
            raw_support
        ):

            # ------------------------------------------------
            # Historical files may use slightly different
            # field names. Normalise them here.
            # ------------------------------------------------

            if isinstance(
                item,
                dict,
            ):

                token = (
                    item.get(
                        "token"
                    )
                    or item.get(
                        "text"
                    )
                    or item.get(
                        "word"
                    )
                    or ""
                )

                raw_score = self._first_number(
                    item,
                    (
                        "raw_score",
                        "attribution",
                        "score",
                        "importance",
                    ),
                    default=0.0,
                )

                normalized_score = (
                    self._first_number(
                        item,
                        (
                            "normalized_score",
                            "normalised_score",
                            "normalized_attribution",
                            "normalised_attribution",
                        ),
                        default=raw_score,
                    )
                )

                position = int(
                    item.get(
                        "position",
                        index,
                    )
                )

            else:

                token = str(
                    item
                )

                raw_score = 0.0

                normalized_score = 0.0

                position = index

            evidence.append(
                TokenAttribution(
                    position=position,

                    token=str(
                        token
                    ),

                    raw_score=float(
                        raw_score
                    ),

                    normalized_score=float(
                        normalized_score
                    ),
                )
            )

        return ExplanationResult(
            category=(
                predicted_category
            ),

            method=(
                "Layer Integrated Gradients "
                "(frozen Phase 8B replay)"
            ),

            steps=50,

            baseline=(
                "PAD-content baseline; "
                "special tokens preserved"
            ),

            evidence=evidence,

            # Full token table remains in the Phase 8B
            # research archive; the working application uses
            # the frozen case-level support-token summary.
            all_token_attributions=[],

            convergence_delta=None,

            source_mode=(
                "frozen_validation_replay"
            ),

            warning=(
                EXPLANATION_WARNING
            ),
        )


    # ========================================================
    # REPLAY FIELD HELPER
    # ========================================================

    @staticmethod
    def _first_number(
        data: dict[str, Any],
        keys: tuple[str, ...],
        *,
        default: float,
    ) -> float:

        for key in keys:

            if key not in data:
                continue

            value = data[
                key
            ]

            try:

                number = float(
                    value
                )

            except (
                TypeError,
                ValueError,
            ):

                continue

            if math.isfinite(
                number
            ):

                return number

        return float(
            default
        )