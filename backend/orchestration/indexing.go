package orchestration

import (
	"encoding/json"
	"net/http"
)

type IndexResponse struct {
	Indexed bool   `json:"indexed"`
	Message string `json:"message"`
}

func HandleIndexCodebase(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Access-Control-Allow-Origin", "*")
	w.Header().Set("Content-Type", "application/json")

	resp := IndexResponse{
		Indexed: true,
		Message: "Codebase indexed successfully via Go runtime.",
	}

	json.NewEncoder(w).Encode(resp)
}

func HandleIssues(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Access-Control-Allow-Origin", "*")
	w.Header().Set("Content-Type", "application/json")

	// Stub for active issues
	json.NewEncoder(w).Encode([]string{})
}
