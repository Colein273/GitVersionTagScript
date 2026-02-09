#!/bin/bash
set -e

# ===============================
# 配置（路径一定要相对仓库根）
# ===============================
VERSION_FILE="Version/version_base.txt"
TAG_PREFIX="v"

# ===============================
# 1. 基本环境校验
# ===============================
if ! command -v git >/dev/null 2>&1; then
    echo "[post-commit] ERROR: git not found"
    exit 1
fi

if [ ! -f "$VERSION_FILE" ]; then
    echo "[post-commit] ERROR: $VERSION_FILE not found"
    exit 1
fi

# ===============================
# 2. 读取版本号
# ===============================
# shellcheck disable=SC1090
source "$VERSION_FILE"

if [ -z "$MAJOR" ] || [ -z "$MINOR" ] || [ -z "$PATCH" ] || [ -z "$BUILD" ]; then
    echo "[post-commit] ERROR: version_base.txt format error"
    exit 1
fi

# ===============================
# 3. BUILD 自增（仅记录，不提交）
# ===============================
BUILD=$((BUILD + 1))
BUILD_REALTIME=$(date "+%Y%m%d%H%M%S")

TAG_NAME="${TAG_PREFIX}${MAJOR}.${MINOR}.${PATCH}"
TAG_NAME_BUILD="${TAG_NAME}.${BUILD}"

# ===============================
# 4. 防止重复 tag
# ===============================
if git rev-parse "$TAG_NAME_BUILD" >/dev/null 2>&1; then
    echo "[post-commit] ERROR: tag $TAG_NAME_BUILD already exists"
    exit 1
fi

# ===============================
# 5. 更新版本文件（不 commit）
# ===============================
cat > "$VERSION_FILE" <<EOF
MAJOR=${MAJOR}
MINOR=${MINOR}
PATCH=${PATCH}
BUILD=${BUILD}
BUILD_REALTIME=${BUILD_REALTIME}
BUILD_REALNUM=${TAG_NAME_BUILD}
EOF

# 加入暂存区，等待**下次提交**
git add "$VERSION_FILE"

# ===============================
# 6. 创建 tag（基于刚刚的 commit）
# ===============================
git tag -a "$TAG_NAME_BUILD" -m "Release ${TAG_NAME_BUILD}"

echo "[post-commit] ✔ Tag created: $TAG_NAME_BUILD"
echo "[post-commit] ℹ version_base.txt updated and staged for next commit"
