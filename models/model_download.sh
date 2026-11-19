#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 2 ]]; then
    echo "Usage: $0 <huggingface-repo> <model-file.gguf>"
    echo
    echo "Example:"
    echo "  $0 unsloth/Qwen3-14B-GGUF Qwen3-14B-Q3_K_M.gguf"
    exit 1
fi

REPO="$1"
MODEL="$2"

if [[ "$MODEL" != *.gguf ]]; then
    echo "Error: model must be a .gguf file"
    exit 1
fi

MODEL_NAME="${REPO##*/}"
DEST="$( dirname "${BASH_SOURCE[0]}" )/models/gguf/${MODEL_NAME}"

if ! command -v hf >/dev/null 2>&1; then
    echo "Error: Hugging Face CLI not found."
    echo "Install with: pip install -U huggingface_hub"
    exit 1
fi

mkdir -p "$DEST"

echo "Repository: $REPO"
echo "Model:      $MODEL"
echo "Destination: $DEST"
echo

hf download "$REPO" "$MODEL" \
    --local-dir "$DEST"

echo
echo "Download completed:"
echo "$DEST/$MODEL"

