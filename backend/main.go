package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os/exec"
	"strings"
	"backend/orchestration"
)

type SubmoduleStatus struct {
	Path   string `json:"path"`
	Status string `json:"status"`
}

func handleSystemStatus(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Access-Control-Allow-Origin", "*")
	w.Header().Set("Content-Type", "application/json")

	statuses := []SubmoduleStatus{}

	out, err := exec.Command("git", "submodule", "status", "--recursive").Output()
	if err != nil {
		json.NewEncoder(w).Encode(statuses)
		return
	}

	lines := strings.Split(strings.TrimSpace(string(out)), "\n")
	for _, line := range lines {
		if line == "" {
			continue
		}
		parts := strings.Fields(line)
		if len(parts) >= 2 {
			statusChar := parts[0][0:1]
			status := "synced"
			if statusChar == "-" {
				status = "uninitialized"
			} else if statusChar == "+" {
				status = "out-of-sync"
			} else if statusChar == "U" {
				status = "merge-conflict"
			}

			statuses = append(statuses, SubmoduleStatus{
				Path:   parts[1],
				Status: status,
			})
		}
	}
	json.NewEncoder(w).Encode(statuses)
}

func main() {
	// Start the Shadow Pilot Diff Monitor
	orchestration.StartDiffMonitor()

	http.HandleFunc("/api/system/status", handleSystemStatus)
	http.HandleFunc("/api/check-session", orchestration.HandleCheckSession)
	http.HandleFunc("/api/issues", orchestration.HandleIssues)
	http.HandleFunc("/api/index-codebase", orchestration.HandleIndexCodebase)
	http.HandleFunc("/api/health", func(w http.ResponseWriter, r *http.Request) {
		fmt.Fprintf(w, "OK")
	})

	fmt.Println("Server starting on :8080...")
	log.Fatal(http.ListenAndServe(":8080", nil))
}
