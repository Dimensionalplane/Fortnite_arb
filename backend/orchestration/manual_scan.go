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

	// Resolve absolute path to scanner.py
	cwd, _ := os.Getwd()
	scannerPath := filepath.Join(filepath.Dir(cwd), "src/scanner.py")
	if _, err := os.Stat(scannerPath); os.IsNotExist(err) {
		scannerPath = "src/scanner.py"
	}

	// Trigger scan asynchronously
	go func() {
		fmt.Printf("[SCAN] Manual scan triggered via API for %s...\n", scannerPath)
		cmd := exec.Command("python3", scannerPath)
		// Set PYTHONPATH so absolute imports work
		cmd.Env = append(os.Environ(), "PYTHONPATH=" + filepath.Dir(filepath.Dir(scannerPath)))
		out, err := cmd.CombinedOutput()
		if err != nil {
			fmt.Printf("[SCAN] Manual scan failed: %v\nOutput: %s\n", err, string(out))
		} else {
			fmt.Println("[SCAN] Manual scan completed successfully.")
		}
	}()

	resp := ScanResponse{
		Message: "Manual market scan initiated in the background.",
		Success: true,
	}
	json.NewEncoder(w).Encode(resp)
}
