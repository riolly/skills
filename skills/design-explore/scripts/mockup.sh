#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Generate one mockup image from a prompt file, with optional reference images.

Usage: mockup.sh --prompt <file> --out <file> [--ref <image>]... [options]

  --prompt <file>   Text of the prompt.
  --out <file>      Where to write the image. The extension picks the format: .webp, .png or .jpg.
  --ref <image>     A reference image the prompt refers to by position. Repeat for more, in order.
  --size <WxH>      Default 1536x1024 (desktop). Use 1024x1536 for a phone screen.
                    Both sides are multiples of 16, and neither is longer than 3840.
  --quality <q>     low, medium (default), high, xhigh or max. Each step up costs more.
  --model <id>      Default gpt-image-2.6-flare, or $DESIGN_EXPLORE_MODEL.

The OpenAI API key comes from $OPENAI_API_KEY, or from the file
~/.config/design-explore/openai-key. $OPENAI_BASE_URL overrides the API address.
EOF
}

die() { printf 'mockup.sh: %s\n' "$1" >&2; exit "${2:-1}"; }

prompt_file="" out="" size="1536x1024" quality="medium"
model="${DESIGN_EXPLORE_MODEL:-gpt-image-2.6-flare}"
refs=()

while [ $# -gt 0 ]; do
  case "$1" in
    -h|--help) usage; exit 0 ;;
    --prompt|--out|--ref|--size|--quality|--model)
      [ $# -ge 2 ] || die "$1 needs a value" 2
      case "$1" in
        --prompt) prompt_file="$2" ;;
        --out) out="$2" ;;
        --ref) refs+=("$2") ;;
        --size) size="$2" ;;
        --quality) quality="$2" ;;
        --model) model="$2" ;;
      esac
      shift 2 ;;
    *) die "unknown option $1 (see --help)" 2 ;;
  esac
done

[ -n "$prompt_file" ] && [ -n "$out" ] || { usage >&2; exit 2; }
[ -s "$prompt_file" ] || die "the prompt file $prompt_file is missing or empty" 2

case "$out" in
  *.webp) format=webp ;;
  *.png) format=png ;;
  *.jpg|*.jpeg) format=jpeg ;;
  *) die "--out must end in .webp, .png or .jpg" 2 ;;
esac

for ref in ${refs[@]+"${refs[@]}"}; do
  [ -f "$ref" ] || die "the reference image $ref does not exist" 2
  case "$ref" in *'"'*|*\\*) die "rename $ref: a reference path can't hold a quote or a backslash" 2 ;; esac
done

key="${OPENAI_API_KEY:-}"
key_file="${XDG_CONFIG_HOME:-$HOME/.config}/design-explore/openai-key"
if [ -z "$key" ] && [ -r "$key_file" ]; then key="$(tr -d '[:space:]' <"$key_file")"; fi
[ -n "$key" ] || die "no OpenAI API key. Set OPENAI_API_KEY, or save the key in $key_file" 3

command -v jq >/dev/null || die "jq is not installed" 2

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
base="${OPENAI_BASE_URL:-https://api.openai.com/v1}"

if [ "${#refs[@]}" -eq 0 ]; then
  jq -n --rawfile prompt "$prompt_file" --arg model "$model" --arg size "$size" \
    --arg quality "$quality" --arg format "$format" \
    '{model: $model, prompt: $prompt, size: $size, quality: $quality, output_format: $format}' >"$work/body.json"
  request=("$base/images/generations" -H "Content-Type: application/json" --data-binary "@$work/body.json")
else
  request=("$base/images/edits" --form-string "model=$model" --form-string "prompt=$(cat "$prompt_file")"
    --form-string "size=$size" --form-string "quality=$quality" --form-string "output_format=$format")
  for ref in "${refs[@]}"; do request+=(-F "image[]=@\"$ref\""); done
fi

status="$(printf 'header = "Authorization: Bearer %s"\n' "$key" |
  curl --config - -sS --max-time 600 -o "$work/response.json" -w '%{http_code}' "${request[@]}")" ||
  die "the request to $base failed"

if [ "$status" != 200 ]; then
  message="$(jq -r '.error.message // empty' "$work/response.json" 2>/dev/null || true)"
  die "the API answered $status: ${message:-$(head -c 300 "$work/response.json")}"
fi

mkdir -p "$(dirname "$out")"
jq -er '.data[0].b64_json' "$work/response.json" | base64 --decode >"$work/image" ||
  die "the API answered 200 without an image"
mv "$work/image" "$out"

printf 'wrote %s (%s, %s, %s quality, %s reference images)\n' "$out" "$model" "$size" "$quality" "${#refs[@]}"
jq -r '.usage // empty | "tokens: \(.total_tokens // "?") total, \(.output_tokens // "?") output"' "$work/response.json"
