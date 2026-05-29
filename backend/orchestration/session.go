package orchestration

import (
	"encoding/json"
	"net/http"
)

type SessionStatus struct {
	Status  string `json:"status"`
	Session string `json:"session"`
}

func HandleCheckSession(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Access-Control-Allow-Origin", "*")
	w.Header().Set("Content-Type", "application/json")

	status := SessionStatus{
		Status:  "active",
		Session: "autonomous-parity-v2",
	}

	json.NewEncoder(w).Encode(status)
}
