#!/usr/bin/env bash

SCRIPT_CURRENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

JAR_FILE="${SCRIPT_CURRENT_DIR}/track/jar/track-code-and-upload.jar"
PARAM_CONFIG_FILE="${SCRIPT_CURRENT_DIR}/config/credentials.config"
PARAM_STORE_DIR="${SCRIPT_CURRENT_DIR}/track/localstore"
PARAM_SOURCECODE_DIR="${SCRIPT_CURRENT_DIR}"

JAVA_BIN=""
EXTRA_ARGS=""

# Detect if we are inside a Docker container by checking /.dockerenv
if [ -f "/.dockerenv" ]; then
  JAVA_BIN="java" # Use the Java runtime available in the container
  EXTRA_ARGS="--listening-host 0.0.0.0"
  echo "Running inside Docker, using system Java runtime"
else
  JAVA_BIN="${SCRIPT_CURRENT_DIR}/track/jdk/bin/java" # Use the bundled JDK
  EXTRA_ARGS="" # Default: no extra args
  echo "Running on host, using bundled JDK"
fi

# For MacOS newer than 11.0.0 - allow the terminal to run the Java runtime
xattr -rd com.apple.quarantine "${SCRIPT_CURRENT_DIR}" >/dev/null 2>&1 || true

set -ex
exec "$JAVA_BIN"                    \
  -Dlogback.enableJansi="true"      \
  -jar "$JAR_FILE"                  \
  "track-and-upload"                \
  "--config" "${PARAM_CONFIG_FILE}" \
  "--store" "${PARAM_STORE_DIR}"    \
  "--sourcecode" "${PARAM_SOURCECODE_DIR}" \
  $EXTRA_ARGS "$@"
