#!/bin/sh
set -eu

source_dir="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)/skills/android-optimizer"
target="$HOME/.claude/skills/android-optimizer"

if [ -e "$target" ]; then
  echo "Ja existe uma instalacao em $target. Remova essa pasta para reinstalar."
  exit 1
fi

mkdir -p "$(dirname -- "$target")"
cp -R "$source_dir" "$target"
rm -rf "$target/evals"
echo "Skill instalada em $target. Reinicie o Claude Code."
