#!/usr/bin/env bash
set -euo pipefail

project_dir="${1:-}"
config_env="${2:-ali-test}"

if [ -z "$project_dir" ]; then
  echo "Usage: $0 <project_dir> [config_env]" >&2
  exit 2
fi

app_dir="$project_dir/app"
config_path="$app_dir/config/$config_env/config.toml"

if [ ! -d "$app_dir" ]; then
  echo "app directory not found: $app_dir" >&2
  exit 3
fi

if [ ! -f "$config_path" ]; then
  echo "config not found: $config_path" >&2
  echo "Available envs under: $app_dir/config" >&2
  ls -1 "$app_dir/config" >&2 || true
  exit 4
fi

export GOPATH="${GOPATH:-$(go env GOPATH)}"
export GO111MODULE=off

echo "Pulling dependencies with inkedep"
cd "$project_dir"
inkedep save
inkedep build

echo "Building in $app_dir"
cd "$app_dir"
go build

echo "Starting with config: $config_path"
./app --config "$config_path"
