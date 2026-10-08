# Submission credential and path scan

Scan date: 2026-10-08. Scope: all 152 files under `submission/`, including packaged Harbor trajectories, configuration, logs, task files, and the XML members of the author-side XLSX workbook. The scan compared file contents with the private API key without printing it, searched common credential-token patterns, enumerated URL hostnames, and checked Unix and Windows host paths, private IPv4 ranges, loopback, and internal hostnames.

Correction: the initial path scanner checked Windows user-directory paths but missed other drive-letter paths. A later workbook inspection found three local drive-letter paths in Excel metadata/text. They were removed from the distributed workbook. The 0.02 s history and all 86 graded cycle-summary rows were verified unchanged after sanitization. The expanded final path scan has zero host-path findings.

| Check | Result |
| --- | --- |
| Exact private API key | 0 matches |
| Common API key / bearer token patterns | 0 matches |
| Host home paths and Windows drive-letter paths | 0 matches after sanitization |
| Host workspace and Harbor installation paths | 0 matches |
| Private IP, loopback, and internal hostnames | 0 matches |
| URL hosts | Only public providers and documentation: `api.moonshot.cn`, `api.deepseek.com`, `github.com`, `lims.ac.uk`, and document/schema sites |

Three matches for an `asciinema` install-id path occur in the run-04 agent recording, pane, and JSON trajectory. This is a path *inside the agent container*, not a host path or credential value. Three other temporary paths are container-local scratch files. The provider URLs are direct public API endpoints, not internal relay addresses.

This scan covers the package as it existed on the scan date. Newly added trajectories or configuration files require another scan before delivery.
