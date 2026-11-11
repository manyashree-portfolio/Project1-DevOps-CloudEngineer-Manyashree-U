<!-- The brief asks for 5 reflection questions of 200-400 words each but does not list them, so these five were chosen to cover the project. Edit each answer so it matches your own experience before submitting. -->
# Reflections

**Author:** Manyashree U

## 1. What was the hardest trade-off between speed and compliance, and how did you resolve it?
The brief asks for commit-to-production under two hours and an elite lead time under one hour, while also requiring SAST, DAST, dependency scanning, SBOM generation, signing and policy gates before any release. Added together, my standard pipeline came to about 1 hour 46 minutes: inside the two-hour target, but not inside the one-hour figure. I did not want to hide this by shrinking the gates.

My resolution was to separate the two goals. The standard path keeps every gate in full. A second "fast lane" is available only to pre-approved, low-risk change categories, runs independent stages in parallel, and reaches an estimated 56 minutes. The fast lane skips no mandatory gate; it only skips the manual approval wait and the long soak for changes that were pre-approved in advance by the change board.

I also found that the one-hour figure itself is out of date. Recent DORA reports describe the top band as lead time under one day. I kept the brief's number as the design target, explained the difference in the observability document, and did not claim a measurement I do not have. The lesson I take from this is that a trade-off is easier to defend when each side is stated with its real numbers, and when the numbers are labelled as estimates.

## 2. Which parts of your design are verified, and which are not?
I tried to keep a clear line between what was run and what was only written. The canary analysis script was run on synthetic data and returned "promote" for the healthy sample and "rollback" for the faulty one. YAML and JSON files parse, the Helm chart renders with test values, and the Terraform is correctly formatted.

Other parts have not been run against a real system. The Rego policies and their tests need OPA, and the winget install did not work on my Windows machine, so OPA has to be downloaded manually; the test results should be saved to the evidence folder once they have been run. The Prometheus alert rules were not checked with promtool. The emergency rollback script was syntax-checked only. The Terraform was never planned, because that needs cloud credentials. The Grafana dashboards use metric names that will not exist until exporters are built, so they are mockups.

I wrote these limits into the README and the self-assessment because a reviewer who finds an unlabelled gap will trust the rest of the work less. Keeping this list honest also helped my own planning, because it shows exactly where the remaining risk sits. If I had another week, the first things I would do are run the policies in a Kyverno test cluster, run the rollback script in a kind cluster, and plan the Terraform against a sandbox account.

## 3. What did the Friday 5 PM simulation teach you about your own design?
Before the exercise I believed the design was strong because it has automatic rollback. The simulation confirmed that part: with the Category A rules, rollback begins at T+0 and restores traffic in under a minute, so the human steps are triage, communication and verification instead of firefighting.

What it exposed was weaker. The hotfix skipped staging, and nothing at deploy time asked for proof that staging had passed. My documents said hotfixes are "expedited but not bypassed", but that was a convention, not a control. The release also landed inside the UPI evening peak on a Friday, and the deployment window was enforced for GitOps syncs but not for every possible path.

The third alert, the payment-gateway timeouts, taught me the most. It would have been easy to blame the gateway. The playbook's scenario for that case says to check whether our release changed the gateway call before assuming a vendor outage, and watching the timeouts fall after rollback is what pointed back at our change. I turned these findings into five concrete gaps and six post-mortem actions, including a signed promotion-evidence check at admission. They are proposals, not implemented controls, and I have said so in the documents. The broader point is that automation limits damage, while prevention needs controls that cannot be skipped by someone in a hurry on a Friday evening.

## 4. How did you use AI assistance, and how did you check its output?
I used an AI assistant to draft documents, configuration and scripts, and I treated every output as a draft to be tested or checked. Several things only worked because of checking. At one point some generated files failed to write because of a shell quirk with brace-expanded folder names, and the assistant had to clean up and rewrite them. It also said plainly that it had written the Rego policies without being able to run them, which is exactly why those policies need a real test run before anyone relies on them.

The brief itself contains deliberate errors, so I could not simply trust its numbers either. Checking the PCI-DSS requirement numbers, the Cloudflare outage details, and the gh-ost tool against primary sources turned up the three errors recorded in ERRATA.md. A useful habit that came out of this was asking of every claim: where does this come from, and was it run?

I also learned where AI help is weakest for this kind of work. It is good at producing consistent structure quickly, but it cannot confirm that a regulation section number is current, that an alert rule fires correctly in a real cluster, or that a rollback script works on a real network. Those checks remain my job, and the self-assessment lists them.

## 5. What would you change if this went to production?
First, I would test before polishing. The gaps most likely to cause real harm are untested ones: the admission policies, the rollback script, and the alert rules. Each needs a test cluster and a recorded result, and a team that has rehearsed the runbook with a real on-call engineer at 3 AM, not just written it.

Second, I would close the open gaps named in the traceability matrix: a pipeline for security and WAF-style configuration changes, the autoscaling trigger on p99 latency, the rule requiring a performance test within 48 hours before a high-traffic window, and a per-pod image-hash check with a kill-switch, which is the control Knight Capital lacked.

Third, I would replace estimates with measurements. The 1 hour 46 minute and 56 minute figures, the rollback timing, and the DORA targets should come from real pipeline runs, and the dashboards should read real metrics.

Fourth, I would keep the repository small and consistent as it grows, with the link checker and validation script running automatically on every pull request so the documents cannot drift apart. Finally, I would hand the regulatory parts to the people who own them. The RBI and CERT-In reporting deadlines and the exact Master Direction section numbers should be confirmed by Compliance, and the exception and audit-record formats should be reviewed by the external auditor's expectations before anyone relies on them.
