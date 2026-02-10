#!/bin/bash
set -e

# ===============================
# 配置
# ===============================
VERSION_FILE="version_base.txt"
TAG_PREFIX="v"
REMOTE_NAME="origin"

# ===============================
# 1. 基本环境校验
# ===============================
if ! command -v git >/dev/null 2>&1; then
    echo "ERROR: git not found"
    exit 1
fi

if [ ! -f "$VERSION_FILE" ]; then
    echo "ERROR: $VERSION_FILE not found"
    exit 1
fi

# ===============================
# 2. 读取版本号
# ===============================
source "$VERSION_FILE"


if [ -z "$MAJOR" ] || [ -z "$MINOR" ] || [ -z "$PATCH" ] || [ -z "$BUILD" ]; then
    echo "ERROR: version_base.txt format error"
    exit 1
fi

# BUILD 自增
BUILD=$((BUILD + 1))

TAG_NAME="${TAG_PREFIX}${MAJOR}.${MINOR}.${PATCH}"
TAG_NAME_BUILD="${TAG_NAME}.${BUILD}"
BUILD_REALTIME=$(date "+%Y%m%d%H%M%S")
# ===============================
# 3. 防止重复 tag
# ===============================
if git rev-parse "$TAG_NAME_BUILD" >/dev/null 2>&1; then
    echo "ERROR: tag $TAG_NAME_BUILD already exists"
    exit 1
fi

# ===============================
# 4. 更新版本文件
# ===============================
cat > "$VERSION_FILE" <<EOF
MAJOR=${MAJOR}
MINOR=${MINOR}
PATCH=${PATCH}
BUILD=${BUILD}
BUILD_REALTIME=${BUILD_REALTIME}
BUILD_REALNUM=${TAG_NAME_BUILD}
EOF

git commit -am "chore(version): bump to ${TAG_NAME_BUILD}"
# ===============================
# 5. 创建 annotated tag
# ===============================
git tag -a "$TAG_NAME" -m "Release ${TAG_NAME}"

echo "✔ Version tag created: $TAG_NAME"