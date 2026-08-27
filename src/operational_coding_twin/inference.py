from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import torch

from operational_coding_twin.frozen_resources import (
    FrozenResources,
)


# ============================================================
# RESULT TYPES
# ============================================================

@dataclass(frozen=True)
class RankedPrediction:
    """
    One ranked ICD-10 category prediction.
    """

    rank: int
    category: str
    probability: float


@dataclass(frozen=True)
class PredictionResult:
    """
    Complete inference result returned by the frozen classifier.
    """

    recommendation: str
    predicted_class_id: int

    calibrated_confidence: float
    raw_confidence: float

    top3: list[RankedPrediction]

    temperature: float
    input_tokens: int
    truncated: bool
    source_mode: str


# ============================================================
# FROZEN INFERENCE SERVICE
# ============================================================

class FrozenInferenceService:
    """
    Read-only inference service for the frozen Phase 7
    seed-42 BioClinicalBERT classifier.

    This class:

        - does NOT train
        - does NOT update model weights
        - does NOT recalibrate
        - does NOT select thresholds
        - does NOT automatically accept predictions
        - does NOT access Phase 9 test artefacts
    """

    def __init__(
        self,
        resources: FrozenResources,
        max_length: int = 320,
    ) -> None:

        self.resources = resources

        self.model = resources.model
        self.tokenizer = resources.tokenizer

        self.label2id = resources.label2id
        self.id2label = resources.id2label

        self.temperature = float(
            resources.temperature
        )

        self.device = resources.device

        self.max_length = int(
            max_length
        )

        # ----------------------------------------------------
        # Frozen-model safety checks
        # ----------------------------------------------------

        if self.max_length != 320:
            raise RuntimeError(
                "The frozen BioClinicalBERT inference "
                "contract requires max_length=320."
            )

        if len(
            self.label2id
        ) != 50:
            raise RuntimeError(
                "Frozen inference requires "
                "exactly 50 ICD-10 categories."
            )

        if self.temperature <= 0:
            raise RuntimeError(
                "Calibration temperature must "
                "be greater than zero."
            )

        self.model.to(
            self.device
        )

        self.model.eval()


    # ========================================================
    # INPUT VALIDATION
    # ========================================================

    def validate_text(
        self,
        clinical_text: str,
    ) -> str:
        """
        Validate a synthetic demonstration clinical note.

        This is a lightweight operational validation step,
        not clinical validation.
        """

        if clinical_text is None:
            raise ValueError(
                "clinical_text cannot be None."
            )

        clinical_text = str(
            clinical_text
        ).strip()

        if not clinical_text:
            raise ValueError(
                "clinical_text cannot be empty."
            )

        if len(
            clinical_text
        ) < 30:
            raise ValueError(
                "Clinical text is too short for "
                "the demonstration workflow."
            )

        if len(
            clinical_text
        ) > 50_000:
            raise ValueError(
                "Clinical text exceeds the "
                "prototype input-size limit."
            )

        return clinical_text


    # ========================================================
    # TOKENISATION
    # ========================================================

    def _tokenize(
        self,
        clinical_text: str,
    ) -> tuple[
        dict[str, torch.Tensor],
        int,
        bool,
    ]:
        """
        Apply the frozen tokenizer contract.

        Returns:
            encoded tensors
            original token count
            whether truncation occurred
        """

        # ----------------------------------------------------
        # Count tokens BEFORE truncation.
        # ----------------------------------------------------

        untruncated = self.tokenizer(
            clinical_text,
            truncation=False,
            add_special_tokens=True,
        )

        original_token_count = len(
            untruncated[
                "input_ids"
            ]
        )

        truncated = (
            original_token_count
            > self.max_length
        )

        # ----------------------------------------------------
        # Actual model input
        # ----------------------------------------------------

        encoded = self.tokenizer(
            clinical_text,

            truncation=True,
            max_length=self.max_length,

            padding=False,

            return_tensors="pt",
        )

        encoded = {
            key: value.to(
                self.device
            )

            for key, value
            in encoded.items()
        }

        return (
            encoded,
            original_token_count,
            truncated,
        )


    # ========================================================
    # FRESH SYNTHETIC-CASE INFERENCE
    # ========================================================

    def predict(
        self,
        clinical_text: str,
    ) -> PredictionResult:
        """
        Run fresh inference on a synthetic demonstration note
        using the frozen BioClinicalBERT checkpoint.

        Calibration is applied using the frozen Phase 8B
        scalar temperature.
        """

        clinical_text = (
            self.validate_text(
                clinical_text
            )
        )

        (
            encoded,
            original_token_count,
            truncated,
        ) = self._tokenize(
            clinical_text
        )

        self.model.eval()

        # ----------------------------------------------------
        # Frozen forward pass
        # ----------------------------------------------------

        with torch.inference_mode():

            outputs = self.model(
                **encoded
            )

            logits = outputs.logits[
                0
            ]

        # ----------------------------------------------------
        # Verify model output
        # ----------------------------------------------------

        if logits.ndim != 1:
            raise RuntimeError(
                "Expected one-dimensional "
                "classification logits."
            )

        if logits.shape[
            0
        ] != 50:
            raise RuntimeError(
                "Frozen model must return "
                "exactly 50 logits."
            )

        if not torch.isfinite(
            logits
        ).all():
            raise RuntimeError(
                "Model produced non-finite logits."
            )

        # ----------------------------------------------------
        # RAW probabilities
        #
        # These are retained only for diagnostic comparison.
        # The UI should display calibrated confidence.
        # ----------------------------------------------------

        raw_probabilities = torch.softmax(
            logits,
            dim=-1,
        )

        # ----------------------------------------------------
        # FROZEN Phase 8B temperature scaling
        #
        # p = softmax(logits / T)
        # ----------------------------------------------------

        calibrated_logits = (
            logits
            / self.temperature
        )

        calibrated_probabilities = (
            torch.softmax(
                calibrated_logits,
                dim=-1,
            )
        )

        # ----------------------------------------------------
        # Convert to CPU NumPy
        # ----------------------------------------------------

        raw_probabilities_np = (
            raw_probabilities
            .detach()
            .cpu()
            .numpy()
            .astype(
                np.float64
            )
        )

        probabilities_np = (
            calibrated_probabilities
            .detach()
            .cpu()
            .numpy()
            .astype(
                np.float64
            )
        )

        # ----------------------------------------------------
        # Probability validation
        # ----------------------------------------------------

        if not np.isfinite(
            probabilities_np
        ).all():
            raise RuntimeError(
                "Calibrated probabilities "
                "contain non-finite values."
            )

        if not np.isclose(
            probabilities_np.sum(),
            1.0,
            atol=1e-8,
        ):
            raise RuntimeError(
                "Calibrated probabilities "
                "do not sum to one."
            )

        # ----------------------------------------------------
        # Rank predictions
        # ----------------------------------------------------

        ranked_ids = np.argsort(
            probabilities_np
        )[::-1]

        top3_ids = ranked_ids[
            :3
        ]

        top3 = [
            RankedPrediction(
                rank=rank,

                category=self.id2label[
                    int(
                        class_id
                    )
                ],

                probability=float(
                    probabilities_np[
                        int(
                            class_id
                        )
                    ]
                ),
            )

            for rank, class_id
            in enumerate(
                top3_ids,
                start=1,
            )
        ]

        predicted_class_id = int(
            top3_ids[
                0
            ]
        )

        recommendation = (
            self.id2label[
                predicted_class_id
            ]
        )

        calibrated_confidence = float(
            probabilities_np[
                predicted_class_id
            ]
        )

        raw_confidence = float(
            raw_probabilities_np[
                predicted_class_id
            ]
        )

        return PredictionResult(
            recommendation=recommendation,

            predicted_class_id=(
                predicted_class_id
            ),

            calibrated_confidence=(
                calibrated_confidence
            ),

            raw_confidence=(
                raw_confidence
            ),

            top3=top3,

            temperature=(
                self.temperature
            ),

            input_tokens=(
                original_token_count
            ),

            truncated=truncated,

            source_mode=(
                "fresh_frozen_inference"
            ),
        )


    # ========================================================
    # FROZEN VALIDATION REPLAY
    # ========================================================

    def replay(
        self,
        validation_row: int,
    ) -> PredictionResult:
        """
        Return an already-frozen Phase 8B validation prediction.

        This does NOT run the model again.

        It is used by the reproducibility/replay mode of the
        hybrid Streamlit application.
        """

        validation_row = int(
            validation_row
        )

        if (
            validation_row < 0
            or
            validation_row >= 375
        ):
            raise ValueError(
                "validation_row must be "
                "between 0 and 374."
            )

        # ----------------------------------------------------
        # Only allow rows from the deterministic n=100 sample.
        # ----------------------------------------------------

        permitted_rows = set(
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
            not in permitted_rows
        ):
            raise ValueError(
                "Requested validation row is not "
                "part of the frozen deterministic "
                "Phase 8B n=100 replay sample."
            )

        probabilities = np.asarray(
            self.resources
            .replay_probabilities[
                validation_row
            ],
            dtype=np.float64,
        )

        if probabilities.shape != (
            50,
        ):
            raise RuntimeError(
                "Replay probability vector "
                "must contain 50 categories."
            )

        if not np.isclose(
            probabilities.sum(),
            1.0,
            atol=1e-8,
        ):
            raise RuntimeError(
                "Replay probability vector "
                "does not sum to one."
            )

        ranked_ids = np.argsort(
            probabilities
        )[::-1]

        top3_ids = ranked_ids[
            :3
        ]

        top3 = [
            RankedPrediction(
                rank=rank,

                category=self.id2label[
                    int(
                        class_id
                    )
                ],

                probability=float(
                    probabilities[
                        int(
                            class_id
                        )
                    ]
                ),
            )

            for rank, class_id
            in enumerate(
                top3_ids,
                start=1,
            )
        ]

        predicted_class_id = int(
            top3_ids[
                0
            ]
        )

        return PredictionResult(
            recommendation=(
                self.id2label[
                    predicted_class_id
                ]
            ),

            predicted_class_id=(
                predicted_class_id
            ),

            calibrated_confidence=float(
                probabilities[
                    predicted_class_id
                ]
            ),

            # Raw probability is deliberately unavailable
            # from the calibrated replay matrix.
            raw_confidence=float(
                "nan"
            ),

            top3=top3,

            temperature=(
                self.temperature
            ),

            input_tokens=0,

            truncated=False,

            source_mode=(
                "frozen_validation_replay"
            ),
        )