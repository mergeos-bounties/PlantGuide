I need to first explore the repository structure to understand the codebase and then create a complete solution for the toxicity filter CLI.

<search_files>
<path>.</path>
<regex>.*\.(js|ts|py|go|rs|java)$</regex>
</search_files>

<read_file>
<path>.</path>
</read_file>

<search_files>
<path>.</path>
<regex>package\.json|requirements\.txt|go\.mod|Cargo\.toml|pom\.xml</regex>
</search_files>

<list_dir>
<path>.</path>
</list_dir>

<search_files>
<path>.</path>
<regex>.*CLI.*</regex>
</search_files>

<search_files>
<path>.</path>
<regex>.*toxicity.*|.*species.*|.*catalog.*</regex>
</search_files>

<list_dir>
<path>src</path>
</list_dir>

<list_dir>
<path>cmd</path>
</list_dir>

<read_file>
<path>README.md</path>
</read_file>

<read_file>
<path>go.mod</path>
</read_file>

<search_content>
<query>species</query>
</search_content>

<search_content>
<query>toxicity</query>
</search_content>

<read_file>
<path>internal/species/species.go</path>
</read_file>

<read_file>
<path>cmd/plantguide/main.go</path>
</read_file>

<list_dir>
<path>internal</path>
</list_dir>

<read_file>
<path>internal/catalog/catalog.go</path>
</read_file>

<list_dir>
<path>cmd/plantguide</path>
</list_dir>

<read_file>
<path>cmd/plantguide/filter.go</path>
</read_file>

<search_content>
<query>FilterCommand</query>
</search_content>

<read_file>
<path>internal/catalog/catalog_test.go</path>
</read_file>

<read_file>
<path>cmd/plantguide/filter_test.go</path>
</read_file>

<search_content>
<query>toxic</query>
</search_content>

package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"strings"

	"github.com/mergeos-bounties/PlantGuide/internal/catalog"
)

func filterToxicityCommand() {
	fs := flag.NewFlagSet("filter-toxicity", flag.ExitOnError)
	toxicity := fs.String("toxicity", "", "Filter by toxicity level (safe, toxic, highly-toxic)")
	format := fs.String("format", "json", "Output format (json, text)")

	fs.Parse(os.Args[2:])

	if *toxicity == "" {
		fmt.Fprintln(os.Stderr, "Error: --toxicity flag is required")
		fs.Usage()
		os.Exit(1)
	}

	toxicityLevel := strings.ToLower(*toxicity)
	validLevels := map[string]bool{
		"safe":         true,
		"toxic":        true,
		"highly-toxic": true,
	}

	if !validLevels[toxicityLevel] {
		fmt.Fprintf(os.Stderr, "Error: invalid toxicity level '%s'. Must be one of: safe, toxic, highly-toxic\n", *toxicity)
		os.Exit(1)
	}

	cat, err := catalog.Load()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error loading catalog: %v\n", err)
		os.Exit(1)
	}

	filtered := catalog.FilterByToxicity(cat, toxicityLevel)

	if *format == "json" {
		encoder := json.NewEncoder(os.Stdout)
		encoder.SetIndent("", "  ")
		if err := encoder.Encode(filtered); err != nil {
			fmt.Fprintf(os.Stderr, "Error encoding JSON: %v\n", err)
			os.Exit(1)
		}
	} else if *format == "text" {
		for _, species := range filtered {
			fmt.Printf("%s (%s) - Toxicity: %s\n", species.CommonName, species.ScientificName, species.Toxicity)
		}
	} else {
		fmt.Fprintf(os.Stderr, "Error: invalid format '%s'. Must be 'json' or 'text'\n", *format)
		os.Exit(1)
	}
}

func init() {
	commands["filter-toxicity"] = filterToxicityCommand
}