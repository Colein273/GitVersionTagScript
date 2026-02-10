package main

import (
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
)

// ================================
// 构建策略开关
// 0 = 保留 version.c / version.h
// 1 = 生成 lib 后删除
// ================================
const CLEAN_VERSION_SRC = 0

// ================================
// Keil 安装路径
// ================================
const KEIL_PATH = `E:\Keil`

func run(cmd string, args ...string) error {
	// fmt.Printf("[CMD] %s %v\n", cmd, args)
	c := exec.Command(cmd, args...)
	c.Stdout = os.Stdout
	c.Stderr = os.Stderr
	return c.Run()
}

func mustExist(path string, name string) {
	if _, err := os.Stat(path); err != nil {
		fmt.Printf("[ERROR] %s not found: %s\n", name, path)
		os.Exit(1)
	}
}

func main() {
	fmt.Println("[INFO] Build GD32 FMC + Version static library (ARMCC5)")

	// ================================
	// 当前 exe / go 文件所在目录（Version）
	// ================================
	exePath, err := os.Executable()
	if err != nil {
		panic(err)
	}
	scriptDir := filepath.Dir(exePath)

	// ================================
	// 工程根目录
	// ================================
	projectRoot := filepath.Clean(filepath.Join(scriptDir, ".."))

	// ================================
	// 工具链
	// ================================
	armcc := filepath.Join(KEIL_PATH, "ARM", "ARMCC", "bin", "armcc.exe")
	armar := filepath.Join(KEIL_PATH, "ARM", "ARMCC", "bin", "armar.exe")

	mustExist(armcc, "armcc")
	mustExist(armar, "armar")

	// ================================
	// 路径
	// ================================
	objDir := filepath.Join(projectRoot, "output")
	libPath := filepath.Join(scriptDir, "version.lib")

	os.MkdirAll(objDir, 0755)

	// 清理旧文件
	os.Remove(libPath)
	filepath.Walk(objDir, func(p string, info os.FileInfo, err error) error {
		if filepath.Ext(p) == ".o" {
			os.Remove(p)
		}
		return nil
	})

	// ================================
	// 编译参数（ARMCC5 对齐 Keil）
	// ================================
	cflags := []string{
		"--c99",
		"--cpu", "Cortex-M4.fp",
		"-O0",
		"--apcs=interwork",
		"--split_sections",
		"-DGD32F450",
		"-I", filepath.Join(projectRoot, "gd32Lib", "Include"),
		"-I", scriptDir,
		"-c",
	}

	// ================================
	// 编译 gd32f4xx_fmc.c
	// ================================
	fmt.Println("[CC] gd32f4xx_fmc.c")
	err = run(
		armcc,
		append(cflags,
			filepath.Join(projectRoot, "gd32Lib", "Source", "gd32f4xx_fmc.c"),
			"-o", filepath.Join(objDir, "gd32f4xx_fmc.o"),
		)...,
	)
	if err != nil {
		fmt.Println("[ERROR] Compile failed")
		os.Exit(1)
	}

	// ================================
	// 编译 version.c
	// ================================
	fmt.Println("[CC] version.c")
	err = run(
		armcc,
		append(cflags,
			filepath.Join(scriptDir, "version.c"),
			"-o", filepath.Join(objDir, "version.o"),
		)...,
	)
	if err != nil {
		fmt.Println("[ERROR] Compile failed")
		os.Exit(1)
	}

	// ================================
	// 打包静态库
	// ================================
	fmt.Println("[AR] version.lib")
	err = run(
		armar,
		"--create",
		libPath,
		filepath.Join(objDir, "gd32f4xx_fmc.o"),
		filepath.Join(objDir, "version.o"),
	)
	if err != nil {
		fmt.Println("[ERROR] Archive failed")
		os.Exit(1)
	}

	// ================================
	// 可选：删除 version 源文件
	// ================================
	if CLEAN_VERSION_SRC == 1 {
		fmt.Println("[INFO] Cleaning version source files")
		os.Remove(filepath.Join(scriptDir, "version.c"))
		os.Remove(filepath.Join(scriptDir, "version.h"))
	}

	fmt.Println("[SUCCESS] Build finished:", libPath)
}
