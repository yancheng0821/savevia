#!/bin/bash

# ============================================
# 关闭RDS SSH隧道
# SaveVia Production Database
# ============================================

LOCAL_PORT=3308

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  关闭SaveVia RDS SSH隧道${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# 查找占用端口的进程
if lsof -Pi :$LOCAL_PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    PID=$(lsof -Pi :$LOCAL_PORT -sTCP:LISTEN -t)
    echo -e "${YELLOW}找到SSH隧道进程 PID: $PID${NC}"
    kill $PID
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ SSH隧道已关闭${NC}"
    else
        echo -e "${RED}✗ 关闭失败，请手动执行: kill $PID${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}未检测到运行中的SSH隧道（端口 $LOCAL_PORT）${NC}"
fi
