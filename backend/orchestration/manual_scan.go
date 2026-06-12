package orchestration

import (
	"encoding/json"
	"fmt"
	"net/http"
	"os/exec"
	"path/filepath"
	"os"
)

type ScanResponse struct {
	Message string `json:"message"`
	Success bool   `json:"success"`
}

func HandleManualScan(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Access-Control-Allow-Origin", "*")
	w.Header().Set("Content-Type", "application/json")

	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	cwd, _ := os.Getwd()
	// Go up one from 'backend' to get root
	rootDir := filepath.Dir(cwd)
	enginePath := filepath.Join(rootDir, "src/trading/engine.py")

	go func() {
		fmt.Printf("[TRADING] Manual cycle triggered via API for %s...\n", enginePath)
		cmd := exec.Command("python3", enginePath)
		// Root is PYTHONPATH
		cmd.Env = append(os.Environ(), "PYTHONPATH=" + rootDir)
		out, err := cmd.CombinedOutput()
		if err != nil {
			fmt.Printf("[TRADING] Cycle failed: %v\nOutput: %s\n", err, string(out))
		} else {
			fmt.Println("[TRADING] Cycle completed successfully.")
		}
	}()

	resp := ScanResponse{
		Message: "Trading cycle initiated in the background.",
		Success: true,
	}
	json.NewEncoder(w).Encode(resp)
}
