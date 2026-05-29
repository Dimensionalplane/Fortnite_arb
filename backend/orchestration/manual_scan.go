package orchestration

import (
	"encoding/json"
	"fmt"
	"net/http"
	"os/exec"
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

	// Trigger scan asynchronously
	go func() {
		fmt.Println("[SCAN] Manual scan triggered via API...")
		cmd := exec.Command("python3", "src/scanner.py")
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
