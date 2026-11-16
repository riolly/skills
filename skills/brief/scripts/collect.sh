#!/usr/bin/env bash
# Collect the state of every active project for the brief skill.
# Read-only on GitHub. Locally it runs `git fetch` and nothing else that writes.
# Usage: collect.sh [project]   a name or alias from projects.yaml; omit it for every project
# Env:   BRIEF_REGISTRY  repo that holds projects.yaml and the needs-you issues (riolly/dotfiles)
#        BRIEF_REF       branch to read projects.yaml from (main)
#        BRIEF_ROOTS     space-separated folders that hold checkouts ($HOME/codes)
set -uo pipefail

registry=${BRIEF_REGISTRY:-riolly/dotfiles}
ref=${BRIEF_REF:-main}
roots=${BRIEF_ROOTS:-$HOME/codes}
want=$(printf '%s' "${1:-}" | tr '[:upper:]' '[:lower:]')
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

if ! gh api "repos/$registry/contents/projects.yaml?ref=$ref" -H 'Accept: application/vnd.github.raw' >"$tmp/projects.yaml" 2>"$tmp/err"; then
  echo "error: cannot read projects.yaml from $registry@$ref: $(cat "$tmp/err")"
  exit 1
fi

# projects.yaml is flat: "- name:" starts a project and "key: value" lines follow it.
# Emit one |-separated line per project: name, aliases, repo, target, other keys as key=value.
awk '
  function flush() { if (name != "") print name "|" aliases "|" repo "|" target "|" links }
  /^[[:space:]]*#/ { next }
  /^[[:space:]]*- name:/ { flush(); sub(/^[[:space:]]*- name:[[:space:]]*/, ""); name=$0; aliases=""; repo=""; target=""; links=""; next }
  name != "" && /^[[:space:]]+[a-z_]+:/ {
    key=$1; sub(/:$/, "", key); val=$0; sub(/^[[:space:]]*[a-z_]+:[[:space:]]*/, "", val)
    if (key == "aliases") { gsub(/[][]/, "", val); aliases=val }
    else if (key == "repo") repo=val
    else if (key == "target") target=val
    else links=links (links == "" ? "" : " ") key "=" val
  }
  END { flush() }
' "$tmp/projects.yaml" >"$tmp/projects.txt"

if [ -n "$want" ]; then
  awk -F'|' -v w="$want" '{
    hit=(tolower($1) == w); n=split(tolower($2), a, /,[[:space:]]*/)
    for (i=1; i<=n; i++) if (a[i] == w) hit=1
    if (hit) print
  }' "$tmp/projects.txt" >"$tmp/match.txt"
  if [ "$(wc -l <"$tmp/match.txt" | tr -d ' ')" != 1 ]; then
    echo "no single project matches \"$1\". Projects and aliases:"
    awk -F'|' '{print "- " $1 (length($2) ? " (" $2 ")" : "")}' "$tmp/projects.txt"
    exit 2
  fi
  mv "$tmp/match.txt" "$tmp/projects.txt"
fi

# Map each checkout under the roots to its GitHub repo, once.
for root in $roots; do
  for d in "$root"/*/; do
    [ -d "$d/.git" ] || continue  # a clone, not a linked worktree; worktrees are listed below
    url=$(git -C "$d" remote get-url origin 2>/dev/null) || continue
    slug=$(printf '%s' "$url" | sed -E 's#^[a-z+]+://[^/]+/##; s#^[^@/]+@[^:]+:##; s#\.git$##')
    printf '%s\t%s\n' "$slug" "${d%/}"
  done
done >"$tmp/checkouts.tsv"

# jq helpers for PRs: check buckets, and the unchecked boxes under Before merge and After merge.
pr_jq='
  def bucket: (.conclusion // .state // "") as $c |
    if (["SUCCESS", "NEUTRAL", "SKIPPED"] | index($c)) then "pass"
    elif (.status // "COMPLETED") != "COMPLETED" or $c == "PENDING" or $c == "EXPECTED" or $c == "" then "pending"
    else "fail" end;
  def summary: if length == 0 then "none" else (group_by(bucket) | map("\(length) \(.[0] | bucket)") | join(", ")) end;
  def named($b): map(select(bucket == $b) | (.name // .context)) | join(", ");
  def steps: (. // "") | split("\n") | reduce .[] as $l ({sec: null, out: []};
    if ($l | test("^\\s*(#+\\s*|\\*\\*)?(before|after) merge:?(\\*\\*)?:?\\s*$"; "i")) then .sec = ($l | ascii_downcase | capture("(?<s>before|after) merge").s)
    elif ($l | test("^\\s*#")) then .sec = null
    elif .sec != null and ($l | test("^\\s*[-*] \\[ \\]")) then .out += ["\(.sec) merge: \($l | sub("^\\s*[-*] \\[ \\]\\s*"; ""))"]
    else . end) | .out;
  if length == 0 then "prs: none open" else .[] | .statusCheckRollup as $rollup |
    "pr #\(.number) \(.title)\n  \(.url)\n  \(.headRefName) -> \(.baseRefName), \(if .isDraft then "draft" else "not draft" end), \(.mergeable | ascii_downcase), checks: \(.statusCheckRollup | summary)"
    + (["fail", "pending"] | map(. as $b | ($rollup | named($b)) as $n | select($n != "") | " (\($b): \($n))") | join(""))
    + ", review: \(if (.reviewDecision // "") == "" then "none" else (.reviewDecision | ascii_downcase) end), open \((now - (.createdAt | fromdateiso8601)) / 86400 | floor) days, updated \(.updatedAt[0:10])"
    + (.body | steps | map("\n  [ ] " + .) | join(""))
  end'

project() {
  local name=$1 repo=$2 target=$3 links=$4
  local default phase found=0 slug dir b n wt
  default=$(gh api "repos/$repo" --jq .default_branch 2>&1) || { echo "## $name ($repo)"; echo "error: $default"; return; }
  echo "## $name ($repo) default=$default target=$target"
  [ -n "$links" ] && echo "links: $links"

  phase=$(gh api "repos/$repo/contents/CLAUDE.md?ref=$target" -H 'Accept: application/vnd.github.raw' 2>/dev/null | grep -m1 -E '^[*_]*Phase:')
  echo "phase: ${phase:-MISSING, no Phase: line in CLAUDE.md on $target}"

  if [ "$target" != "$default" ]; then
    if ! gh api "repos/$repo/branches/$target" --silent 2>/dev/null; then
      echo "target: MISSING, $target is not a branch on GitHub"
    else
      gh api "repos/$repo/compare/$default...$target?per_page=1" --jq '
        if .ahead_by == 0 then "target: 0 commits ahead of '"$default"', nothing to release"
        else (.commits[0].commit.committer.date) as $d | ((now - ($d | fromdateiso8601)) / 86400) as $age |
          "target: \(.ahead_by) commits ahead of '"$default"', \(.behind_by) behind, oldest unreleased commit \($d[0:10]), \($age | floor) day\(if ($age | floor) == 1 then "" else "s" end) old\(if $age > 3 then ", STALE: over 3 days" else "" end)"
        end' 2>&1 || echo "target: compare failed"
    fi
  fi

  gh pr list -R "$repo" --state open --limit 50 \
    --json number,title,url,headRefName,baseRefName,isDraft,mergeable,reviewDecision,createdAt,updatedAt,statusCheckRollup,body \
    --jq "$pr_jq" 2>&1

  if [ -n "$want" ]; then
    gh pr list -R "$repo" --state merged --limit 5 --json number,title,baseRefName,mergedAt \
      --jq '.[] | "merged #\(.number) into \(.baseRefName) on \(.mergedAt[0:10]): \(.title)"' 2>&1
  fi

  while IFS=$'\t' read -r slug dir; do
    [ "$slug" = "$repo" ] || continue
    found=1
    echo "checkout: $dir"
    git -C "$dir" fetch --quiet --prune origin 2>/dev/null || echo "  fetch failed, so the counts below may be stale"
    # Commits on a local branch that no remote branch holds. A branch whose PR merged is
    # skipped, because a squash merge leaves its commits on no remote branch.
    for b in $(git -C "$dir" for-each-ref --format='%(refname:short)' refs/heads); do
      n=$(git -C "$dir" rev-list --count "$b" --not --remotes 2>/dev/null)
      [ "${n:-0}" -gt 0 ] || continue
      [ -n "$(gh pr list -R "$repo" --state merged --head "$b" --limit 1 --json number --jq '.[].number' 2>/dev/null)" ] && continue
      echo "  unpushed: $b has $n commits on no remote branch"
    done
    git -C "$dir" worktree list --porcelain | awk '/^worktree /{w=substr($0,10)} /^branch /{print w "\t" substr($0,19)} /^detached/{print w "\tdetached HEAD"}' |
      while IFS=$'\t' read -r wt b; do
        n=$(git -C "$wt" rev-list --count "HEAD..@{u}" 2>/dev/null) && [ "$n" -gt 0 ] && echo "  behind: $b is $n commits behind its remote, in $wt"
        n=$(git -C "$wt" status --porcelain 2>/dev/null | wc -l | tr -d ' ')
        [ "$n" -gt 0 ] && echo "  uncommitted: $n files in $wt ($b)"
      done
  done <"$tmp/checkouts.tsv"
  [ "$found" = 1 ] || echo "checkout: none on this machine under $roots"
}

count=0
while IFS='|' read -r name aliases repo target links; do
  count=$((count + 1))
  project "$name" "$repo" "$target" "$links" >"$tmp/p$count" 2>&1 &
done <"$tmp/projects.txt"

# With a project named, keep only the issues titled "<project>: ...", in any case.
prefix=""
[ -n "$want" ] && prefix="$(cut -d'|' -f1 "$tmp/projects.txt" | tr '[:upper:]' '[:lower:]'):"
gh issue list -R "$registry" --label needs-you --state open --limit 100 \
  --json number,title,url,createdAt,updatedAt,body \
  --jq 'sort_by(.number) | .[] | select(.title | ascii_downcase | startswith("'"${prefix//\"/}"'")) | "### #\(.number) \(.title)\n\(.url), waiting \((now - (.createdAt | fromdateiso8601)) / 86400 | floor) days, updated \(.updatedAt[0:10])\n\(.body)\n"' >"$tmp/issues" 2>&1 &
wait

echo "machine: $(hostname -s)"
echo "registry: $registry"
echo
for i in $(seq 1 "$count"); do cat "$tmp/p$i"; echo; done
echo "# needs-you issues in $registry"
cat "$tmp/issues"

# The state of every PR an issue links to, so a step that is done can be closed with proof.
{ grep -oE 'https://github\.com/[^/ )]+/[^/ )]+/pull/[0-9]+' "$tmp/issues" || true; } | sort -u | while read -r u; do
  gh pr view "$u" --json state,mergedAt --jq "\"linked $u: \(.state | ascii_downcase)\(if .mergedAt then \" \(.mergedAt[0:10])\" else \"\" end)\"" || echo "linked $u: unreadable"
done
exit 0
