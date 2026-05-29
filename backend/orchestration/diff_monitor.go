package orchestration

import (
	"fmt"
	"os/exec"
	"time"
)

func StartDiffMonitor() {
	ticker := time.NewTicker(30 * time.Second)
	go func() {
		for range ticker.C {
			out, err := exec.Command("git", "diff").Output()
			if err == nil && len(out) > 0 {
				fmt.Printf("[SHADOW PILOT] Diff detected at %s\n", time.Now().Format(time.RFC3339))
				// LLM evaluation logic would go here
			}
		}
	}()
}
