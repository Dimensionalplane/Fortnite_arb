package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/exec"
	"strings"
	"path/filepath"
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

func handleArbitrageHistory(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Access-Control-Allow-Origin", "*")
	w.Header().Set("Content-Type", "application/json")

	cwd, _ := os.Getwd()
	historyPath := filepath.Join(filepath.Dir(cwd), "data/scan_history.json")
	if _, err := os.Stat(historyPath); os.IsNotExist(err) {
		historyPath = "data/scan_history.json"
	}

	data, err := os.ReadFile(historyPath)
	if err != nil {
		w.Write([]byte("[]"))
		return
	}
	w.Write(data)
}

func handleConfig(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Access-Control-Allow-Origin", "*")
	w.Header().Set("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
	w.Header().Set("Access-Control-Allow-Headers", "Content-Type")
	w.Header().Set("Content-Type", "application/json")

	if r.Method == http.MethodOptions {
		return
	}

	cwd, _ := os.Getwd()
	configPath := filepath.Join(filepath.Dir(cwd), "config/items.json")
	if _, err := os.Stat(configPath); os.IsNotExist(err) {
		configPath = "config/items.json"
	}

	if r.Method == http.MethodGet {
		data, err := os.ReadFile(configPath)
		if err != nil {
			fmt.Printf("Error reading config at %s: %v\n", configPath, err)
			http.Error(w, "Failed to read config", http.StatusInternalServerError)
			return
		}
		w.Write(data)
	} else if r.Method == http.MethodPost {
		var config interface{}
		if err := json.NewDecoder(r.Body).Decode(&config); err != nil {
			http.Error(w, "Invalid JSON", http.StatusBadRequest)
			return
		}
		data, _ := json.MarshalIndent(config, "", "    ")
		if err := os.WriteFile(configPath, data, 0644); err != nil {
			http.Error(w, "Failed to save config", http.StatusInternalServerError)
			return
		}
		json.NewEncoder(w).Encode(map[string]bool{"success": true})
	}
}

func main() {
	orchestration.StartDiffMonitor()

	http.HandleFunc("/api/system/status", handleSystemStatus)
	http.HandleFunc("/api/arbitrage/history", handleArbitrageHistory)
	http.HandleFunc("/api/arbitrage/scan", orchestration.HandleManualScan)
	http.HandleFunc("/api/config", handleConfig)
	http.HandleFunc("/api/check-session", orchestration.HandleCheckSession)
	http.HandleFunc("/api/issues", orchestration.HandleIssues)
	http.HandleFunc("/api/index-codebase", orchestration.HandleIndexCodebase)
	http.HandleFunc("/api/health", func(w http.ResponseWriter, r *http.Request) {
		fmt.Fprintf(w, "OK")
	})

	fmt.Println("Server starting on :8080...")
	log.Fatal(http.ListenAndServe(":8080", nil))
}
