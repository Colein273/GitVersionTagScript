package main

import (
	"bufio"
	"bytes"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"time"
)

/* ======================== 工具函数 ======================== */

func runGit(args ...string) string {
	cmd := exec.Command("git", args...)
	var out bytes.Buffer
	cmd.Stdout = &out
	cmd.Stderr = nil
	if err := cmd.Run(); err != nil {
		return ""
	}
	return strings.TrimSpace(out.String())
}

func readKeyValueFile(path string) map[string]string {
	m := make(map[string]string)

	file, err := os.Open(path)
	if err != nil {
		return m
	}
	defer file.Close()

	scanner := bufio.NewScanner(file)
	for scanner.Scan() {
		line := strings.TrimSpace(scanner.Text())
		if line == "" || strings.HasPrefix(line, "#") {
			continue
		}
		parts := strings.SplitN(line, "=", 2)
		if len(parts) == 2 {
			m[parts[0]] = parts[1]
		}
	}
	return m
}

func boolToInt(b bool) int {
	if b {
		return 1
	}
	return 0
}

/* ======================== 主程序 ======================== */

func main() {

	/* ---------- 定位自身目录 ---------- */
	exePath, _ := os.Executable()
	scriptDir := filepath.Dir(exePath)

	/* ---------- 工程固有信息 ---------- */
	projectName := "GD32-Communication-Module"
	buildType := "CommModuleForGD32.uvprojx"
	productName := "CommModuleForGD32"
	mcuType := "GD32F450"
	platform := "Keil5"

	/* ---------- Git 信息 ---------- */
	gitTag := runGit("tag", "--list", "v*", "--sort=-v:refname")
	if gitTag == "" {
		gitTag = "v0.0.0"
	} else {
		gitTag = strings.Split(gitTag, "\n")[0]
	}

	gitHash := runGit("rev-parse", "--short", "HEAD")
	if gitHash == "" {
		gitHash = "nogit"
	}

	dirty := runGit("status", "--porcelain") != ""

	/* ---------- 解析 vX.Y.Z ---------- */
	tagClean := strings.TrimPrefix(gitTag, "v")
	parts := strings.Split(tagClean, ".")
	major, minor, patch := 0, 0, 0

	if len(parts) > 0 {
		fmt.Sscanf(parts[0], "%d", &major)
	}
	if len(parts) > 1 {
		fmt.Sscanf(parts[1], "%d", &minor)
	}
	if len(parts) > 2 {
		fmt.Sscanf(parts[2], "%d", &patch)
	}

	// vX.Y.Z -> 0xXXYYZZ00
	gitTagHex := (major << 24) | (minor << 16) | (patch << 8)

	/* ---------- version_base.txt ---------- */
	baseFile := filepath.Join(scriptDir, "version_base.txt")
	baseKV := readKeyValueFile(baseFile)

	buildRealtime := baseKV["BUILD_REALTIME"]
	buildRealnum := baseKV["BUILD_REALNUM"]

	// 工程兜底，保证可编译、可运行
	if buildRealtime == "" {
		buildRealtime = "UNKNOWN"
	}
	if buildRealnum == "" {
		buildRealnum = "0"
	}

	/* ---------- 构建时间 / 主机 ---------- */
	buildTime := time.Now().Format("2006-01-02 15:04:05")
	buildHost, _ := os.Hostname()
	buildUser := os.Getenv("USERNAME")

	/* ---------- 设备白名单 ---------- */
	allowHosts := map[string]bool{
		"LAPTOP-Q2N29D5I": true,
		"BuildServer":    true,
		"YCY-Laptop":     true,
	}
	allowPrint := allowHosts[buildHost]

	/* ======================== 输出 version.h ======================== */

	versionH := filepath.Join(scriptDir, "version.h")
	fh, err := os.Create(versionH)
	if err != nil {
		fmt.Println("ERROR: cannot create version.h")
		os.Exit(1)
	}
	defer fh.Close()

	fmt.Fprintln(fh, "#ifndef __VERSION_H__")
	fmt.Fprintln(fh, "#define __VERSION_H__")
	fmt.Fprintln(fh)
	fmt.Fprintln(fh, "extern void Write_Version_Info(void);")
	fmt.Fprintln(fh)
	fmt.Fprintln(fh, "#endif")

	/* ======================== 输出 version.c ======================== */

	versionC := filepath.Join(scriptDir, "version.c")
	fc, err := os.Create(versionC)
	if err != nil {
		fmt.Println("ERROR: cannot create version.c")
		os.Exit(1)
	}
	defer fc.Close()

	fmt.Fprintln(fc, "#include \"version.h\"")
	fmt.Fprintln(fc, "#include \"gd32f4xx_fmc.h\"")
	fmt.Fprintln(fc)

	fmt.Fprintf(fc, "#define FW_GIT_HASH      \"%s\"\n", gitHash)
	fmt.Fprintf(fc, "#define FW_GIT_TAG       \"%s\"\n", gitTag)
	fmt.Fprintf(fc, "#define FW_GIT_TAG_HEX   0x%08X\n", gitTagHex)
	fmt.Fprintf(fc, "#define FW_DIRTY_FLAG    %d\n", boolToInt(dirty))
	fmt.Fprintf(fc, "#define FW_ALLOW_FLAG    %d\n", boolToInt(allowPrint))
	fmt.Fprintln(fc)

	fmt.Fprintf(fc, "#define FW_BD_REALTIME  \"%s\"\n", buildRealtime)
	fmt.Fprintf(fc, "#define FW_BD_REALNUM   \"%s\"\n", buildRealnum)
	fmt.Fprintf(fc, "#define FW_BUILD_TIME  \"%s\"\n", buildTime)
	fmt.Fprintf(fc, "#define FW_BUILD_HOST  \"%s\"\n", buildHost)
	fmt.Fprintf(fc, "#define FW_BUILD_USER  \"%s\"\n", buildUser)
	fmt.Fprintln(fc)

	fmt.Fprintf(fc, "#define MAJOR_VERSION   %d\n", major)
	fmt.Fprintf(fc, "#define MINOR_VERSION   %d\n", minor)
	fmt.Fprintf(fc, "#define PATCH_VERSION   %d\n", patch)
	fmt.Fprintf(fc, "#define VERSION_NUM     ((%d<<24)|(%d<<16)|(%d<<8))\n", major, minor, patch)
	fmt.Fprintln(fc)

	fmt.Fprintf(fc, "#define FW_PROJECT_NAME \"%s\"\n", projectName)
	fmt.Fprintf(fc, "#define FW_BUILD_TYPE   \"%s\"\n", buildType)
	fmt.Fprintf(fc, "#define FW_PRODUCT_NAME \"%s\"\n", productName)
	fmt.Fprintf(fc, "#define FW_MCU_TYPE     \"%s\"\n", mcuType)
	fmt.Fprintf(fc, "#define FW_PLATFORM     \"%s\"\n", platform)
	fmt.Fprintln(fc)

	fmt.Fprintln(fc, "#define VERSION_FLASH_BASE ((uint32_t)0x08020000)")
	fmt.Fprintln(fc)

	fmt.Fprintln(fc, "void Write_Version_Info(void)")
	fmt.Fprintln(fc, "{")
	fmt.Fprintln(fc, "    fmc_unlock();")
	fmt.Fprintln(fc, "    fmc_sector_erase(CTL_SECTOR_NUMBER_5);")
	fmt.Fprintln(fc, "    fmc_byte_program(VERSION_FLASH_BASE + 0x00, FW_ALLOW_FLAG);")
	fmt.Fprintln(fc, "    fmc_lock();")
	fmt.Fprintln(fc, "}")
}
